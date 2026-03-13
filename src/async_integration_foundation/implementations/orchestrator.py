from __future__ import annotations

from async_integration_foundation.contracts.dispatcher import Dispatcher
from async_integration_foundation.contracts.mapper import PayloadMapper
from async_integration_foundation.contracts.persistence import QueueRepository
from async_integration_foundation.contracts.policy import RetryPolicy
from async_integration_foundation.contracts.transport import TransportAdapter
from async_integration_foundation.domain.models import Queue, QueueItem, QueueItemState, QueueState


class MockDispatcher(Dispatcher):
    def __init__(
        self,
        repository: QueueRepository,
        transport: TransportAdapter,
        mapper: PayloadMapper,
        retry_policy: RetryPolicy,
    ) -> None:
        self.repository = repository
        self.transport = transport
        self.mapper = mapper
        self.retry_policy = retry_policy

    def dispatch_queue(self, queue_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        if queue.state == QueueState.PAUSED:
            return queue

        queue.state = QueueState.DISPATCHING
        for item in queue.items:
            if self._is_item_dispatchable(item):
                self._dispatch_item(queue, item)

        queue.state = self._aggregate_queue_state(queue)
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

        self._dispatch_item(queue, item)
        queue.state = self._aggregate_queue_state(queue)
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
        item.mapped_payload = self.mapper.map_payload(item.payload)
        result = self.transport.send(item.mapped_payload)

        if result.success:
            item.state = QueueItemState.SENT
            item.last_error = None
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
