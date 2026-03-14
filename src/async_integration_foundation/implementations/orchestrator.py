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

        queue.state = QueueState.DISPATCHING
        self._record_activity(queue, QueueActivityType.DISPATCH_STARTED)
        for item in queue.items:
            if self._is_item_dispatchable(item):
                self._dispatch_item(queue, item)

        queue.state = self._aggregate_queue_state(queue)
        self._record_dispatch_outcome(queue)
        return self.repository.save_queue(queue)

    def dispatch_item(self, queue_id: str, item_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        if queue.state == QueueState.PAUSED:
            return queue

        item = next((i for i in queue.items if i.id == item_id), None)
        if item is None:
            raise ValueError(f"Queue item not found: {item_id}")

        if not self._is_item_dispatchable(item):
            return queue

        queue.state = QueueState.DISPATCHING
        self._record_activity(queue, QueueActivityType.DISPATCH_STARTED, item_id=item.id)

        self._dispatch_item(queue, item)
        queue.state = self._aggregate_queue_state(queue)
        self._record_dispatch_outcome(queue)
        return self.repository.save_queue(queue)

    def retry_failed_items(self, queue_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        for item in queue.items:
            if item.state in {QueueItemState.RETRY_WAITING, QueueItemState.FAILED} and self.retry_policy.can_retry(item):
                item.state = QueueItemState.READY
        return self.dispatch_queue(queue_id)

    def _dispatch_item(self, queue: Queue, item: QueueItem) -> None:
        item.state = QueueItemState.SENDING
        item.attempt_count += 1
        item.last_attempt_at = datetime.now(timezone.utc)
        item.mapped_payload = self.mapper.map_payload(item.payload)
        result = self.transport.send(item.mapped_payload)

        if result.success:
            item.state = QueueItemState.SENT
            item.last_error = None
            self._record_activity(queue, QueueActivityType.ITEM_SENT, item_id=item.id)
            return

        item.last_error = result.error_message
        if result.retryable and self.retry_policy.can_retry(item):
            item.state = QueueItemState.RETRY_WAITING
            return

        item.state = QueueItemState.FAILED

    def _aggregate_queue_state(self, queue: Queue) -> QueueState:
        item_states = {item.state for item in queue.items}
        if not item_states:
            return QueueState.OPEN
        if item_states == {QueueItemState.SENT}:
            return QueueState.COMPLETED
        if item_states.issubset({QueueItemState.FAILED, QueueItemState.RETRY_WAITING}):
            return QueueState.FAILED
        if QueueItemState.FAILED in item_states or QueueItemState.RETRY_WAITING in item_states:
            return QueueState.PARTIAL_FAILED
        if QueueItemState.SENDING in item_states:
            return QueueState.DISPATCHING
        return QueueState.READY

    def _require_queue(self, queue_id: str) -> Queue:
        queue = self.repository.get_queue(queue_id)
        if queue is None:
            raise ValueError(f"Queue not found: {queue_id}")
        return queue

    def _is_item_dispatchable(self, item: QueueItem) -> bool:
        return item.state in {
            QueueItemState.READY,
            QueueItemState.STAGED,
            QueueItemState.RETRY_WAITING,
            QueueItemState.NEW,
        }

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
        if queue.state == QueueState.COMPLETED:
            self._record_activity(queue, QueueActivityType.DISPATCH_COMPLETED)
        elif queue.state in {QueueState.PARTIAL_FAILED, QueueState.FAILED}:
            self._record_activity(queue, QueueActivityType.DISPATCH_FAILED)
