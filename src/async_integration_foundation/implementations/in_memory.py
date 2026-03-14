from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from async_integration_foundation.contracts.activity import QueueActivityLog
from async_integration_foundation.contracts.persistence import QueueRepository
from async_integration_foundation.domain.models import Queue, QueueActivityEvent, QueueActivityType


class InMemoryQueueRepository(QueueRepository):
    def __init__(self) -> None:
        self._queues: dict[str, Queue] = {}

    def create_queue(self, queue: Queue) -> Queue:
        self._queues[queue.id] = queue
        return queue

    def get_queue(self, queue_id: str) -> Queue | None:
        return self._queues.get(queue_id)

    def get_queue_by_scope(self, session_id: str, context_type: str, context_id: str) -> Queue | None:
        for queue in self._queues.values():
            if (
                queue.session_id == session_id
                and queue.context_type == context_type
                and queue.context_id == context_id
            ):
                return queue
        return None

    def save_queue(self, queue: Queue) -> Queue:
        queue.updated_at = datetime.now(timezone.utc)
        self._queues[queue.id] = queue
        return queue

    def list_queues(self) -> list[Queue]:
        return list(self._queues.values())

    def list_queues_by_session(self, session_id: str) -> list[Queue]:
        return [queue for queue in self._queues.values() if queue.session_id == session_id]

    def list_queues_by_context(self, session_id: str, context_type: str) -> list[Queue]:
        return [
            queue
            for queue in self._queues.values()
            if queue.session_id == session_id and queue.context_type == context_type
        ]


class InMemoryQueueActivityLog(QueueActivityLog):
    def __init__(self) -> None:
        self._events: list[QueueActivityEvent] = []

    def record(
        self,
        queue_id: str,
        event_type: QueueActivityType,
        session_id: str | None = None,
        item_id: str | None = None,
        detail: str | None = None,
    ) -> QueueActivityEvent:
        event = QueueActivityEvent(
            event_id=str(uuid4()),
            queue_id=queue_id,
            event_type=event_type,
            occurred_at=datetime.now(timezone.utc),
            session_id=session_id,
            item_id=item_id,
            detail=detail,
        )
        self._events.append(event)
        return event

    def list_for_queue(self, queue_id: str) -> list[QueueActivityEvent]:
        return [event for event in self._events if event.queue_id == queue_id]

    def list_for_session(self, session_id: str) -> list[QueueActivityEvent]:
        return [event for event in self._events if event.session_id == session_id]
