from __future__ import annotations

from async_integration_foundation.contracts.persistence import QueueRepository
from async_integration_foundation.domain.models import Queue


class InMemoryQueueRepository(QueueRepository):
    def __init__(self) -> None:
        self._queues: dict[str, Queue] = {}

    def create_queue(self, queue: Queue) -> Queue:
        self._queues[queue.id] = queue
        return queue

    def get_queue(self, queue_id: str) -> Queue | None:
        return self._queues.get(queue_id)

    def save_queue(self, queue: Queue) -> Queue:
        self._queues[queue.id] = queue
        return queue

    def list_queues(self) -> list[Queue]:
        return list(self._queues.values())
