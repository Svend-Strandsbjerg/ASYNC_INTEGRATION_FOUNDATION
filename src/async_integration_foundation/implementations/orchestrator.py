from __future__ import annotations

from datetime import datetime, timezone

from async_integration_foundation.contracts.activity import QueueActivityLog
from async_integration_foundation.contracts.dispatcher import Dispatcher
from async_integration_foundation.contracts.mapper import PayloadMapper
from async_integration_foundation.contracts.persistence import QueueRepository
from async_integration_foundation.contracts.policy import RetryPolicy
from async_integration_foundation.contracts.transport import TransportAdapter
from async_integration_foundation.domain.models import (
    Queue,
    QueueActivityType,
    QueueItem,
    QueueItemState,
    QueueState,
)
from async_integration_foundation.domain.state_machine import (
    derive_queue_post_dispatch_state,
    is_item_dispatchable,
    is_retry_due,
    transition_item_state,
    transition_queue_state,
)


class MockDispatcher(Dispatcher):
    def __init__(
        self,
        repository: QueueRepository,
        transport: TransportAdapter,
        mapper: PayloadMapper,
        retry_policy: RetryPolicy,
        activity_log: QueueActivityLog | None = None,
    ) -> None:
        self.repository = repository
        self.transport = transport
        self.mapper = mapper
        self.retry_policy = retry_policy
        self.activity_log = activity_log

    def dispatch_queue(self, queue_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        if queue.state == QueueState.PAUSED:
            return queue

        transition_queue_state(queue, QueueState.DISPATCHING)
        self._record_activity(queue, QueueActivityType.DISPATCH_STARTED)
        for item in sorted(queue.items, key=lambda candidate: (candidate.sequence_number, candidate.id)):
            if is_item_dispatchable(item):
                self._dispatch_item(queue, item)

        transition_queue_state(queue, derive_queue_post_dispatch_state(queue))
        self._record_dispatch_outcome(queue)
        return self.repository.save_queue(queue)

    def dispatch_item(self, queue_id: str, item_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        if queue.state == QueueState.PAUSED:
            return queue

        item = next((i for i in queue.items if i.id == item_id), None)
        if item is None:
            raise ValueError(f"Queue item not found: {item_id}")

        if not is_item_dispatchable(item):
            return queue

        transition_queue_state(queue, QueueState.DISPATCHING)
        self._record_activity(queue, QueueActivityType.DISPATCH_STARTED, item_id=item.id)

        self._dispatch_item(queue, item)
        transition_queue_state(queue, derive_queue_post_dispatch_state(queue))
        self._record_dispatch_outcome(queue)
        return self.repository.save_queue(queue)

    def retry_failed_items(self, queue_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        now = datetime.now(timezone.utc)
        for item in queue.items:
            if item.state == QueueItemState.FAILED and self.retry_policy.can_retry(item):
                transition_item_state(item, QueueItemState.RETRY_WAITING)
                if item.next_retry_at is None:
                    item.next_retry_at = now
            if is_retry_due(item, now=now):
                transition_item_state(item, QueueItemState.READY)
                item.next_retry_at = None
        return self.dispatch_queue(queue_id)

    def _dispatch_item(self, queue: Queue, item: QueueItem) -> None:
        transition_item_state(item, QueueItemState.DISPATCHING)
        item.attempt_count += 1
        item.last_attempt_at = datetime.now(timezone.utc)
        item.mapped_payload = self.mapper.map_payload(item.payload)
        result = self.transport.send(item.mapped_payload)

        if result.success:
            transition_item_state(item, QueueItemState.SENT)
            item.last_error = None
            item.next_retry_at = None
            self._record_activity(queue, QueueActivityType.ITEM_SENT, item_id=item.id)
            return

        item.last_error = result.error_message
        transition_item_state(item, QueueItemState.FAILED)
        if result.retryable and self.retry_policy.can_retry(item):
            transition_item_state(item, QueueItemState.RETRY_WAITING)
            item.next_retry_at = datetime.now(timezone.utc)
            return

        transition_item_state(item, QueueItemState.DEAD_LETTER)

    def _require_queue(self, queue_id: str) -> Queue:
        queue = self.repository.get_queue(queue_id)
        if queue is None:
            raise ValueError(f"Queue not found: {queue_id}")
        return queue

    def _record_activity(self, queue: Queue, event_type: QueueActivityType, item_id: str | None = None) -> None:
        if self.activity_log is None:
            return
        self.activity_log.record(
            queue_id=queue.id,
            session_id=queue.session_id,
            event_type=event_type,
            item_id=item_id,
        )

    def _record_dispatch_outcome(self, queue: Queue) -> None:
        has_failure_outcome = any(
            item.state in {QueueItemState.FAILED, QueueItemState.RETRY_WAITING, QueueItemState.DEAD_LETTER}
            for item in queue.items
        )
        if has_failure_outcome:
            self._record_activity(queue, QueueActivityType.DISPATCH_FAILED)
        elif queue.state == QueueState.COMPLETED:
            self._record_activity(queue, QueueActivityType.DISPATCH_COMPLETED)
