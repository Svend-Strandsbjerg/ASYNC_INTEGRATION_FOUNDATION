from __future__ import annotations

from async_integration_foundation.contracts.activity import QueueActivityLog
from async_integration_foundation.contracts.persistence import QueueRepository
from async_integration_foundation.domain.models import (
    DispatchMode,
    Queue,
    QueueActivityType,
    QueueItem,
    QueueItemSnapshot,
    QueueItemState,
    QueueSnapshot,
    QueueState,
)


class QueueResolver:
    def __init__(self, repository: QueueRepository, activity_log: QueueActivityLog | None = None) -> None:
        self.repository = repository
        self.activity_log = activity_log

    def get_or_create_queue(
        self,
        session_id: str,
        context_type: str,
        context_id: str,
        dispatch_mode: DispatchMode,
        user_id: str | None = None,
        metadata: dict | None = None,
    ) -> Queue:
        existing = self.repository.get_queue_by_scope(
            session_id=session_id,
            context_type=context_type,
            context_id=context_id,
        )
        if existing is not None:
            return existing

        queue = Queue(
            id=f"{session_id}:{context_type}:{context_id}",
            name=f"{context_type}-{context_id}",
            dispatch_mode=dispatch_mode,
            session_id=session_id,
            user_id=user_id,
            context_type=context_type,
            context_id=context_id,
            metadata=metadata or {},
        )
        created = self.repository.create_queue(queue)
        self._record(created, QueueActivityType.QUEUE_CREATED)
        return created

    def add_item(self, queue_id: str, item: QueueItem) -> Queue:
        queue = self._require_queue(queue_id)
        queue.items.append(item)
        saved = self.repository.save_queue(queue)
        self._record(saved, QueueActivityType.ITEM_ADDED, item_id=item.id)
        return saved

    def pause_queue(self, queue_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        queue.state = QueueState.PAUSED
        saved = self.repository.save_queue(queue)
        self._record(saved, QueueActivityType.QUEUE_PAUSED)
        return saved

    def resume_queue(self, queue_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        queue.state = QueueState.OPEN
        saved = self.repository.save_queue(queue)
        self._record(saved, QueueActivityType.QUEUE_RESUMED)
        return saved

    def _record(self, queue: Queue, event_type: QueueActivityType, item_id: str | None = None) -> None:
        if self.activity_log is None:
            return
        self.activity_log.record(
            queue_id=queue.id,
            session_id=queue.session_id,
            event_type=event_type,
            item_id=item_id,
        )

    def _require_queue(self, queue_id: str) -> Queue:
        queue = self.repository.get_queue(queue_id)
        if queue is None:
            raise ValueError(f"Queue not found: {queue_id}")
        return queue


def build_queue_snapshot(queue: Queue) -> QueueSnapshot:
    return QueueSnapshot(
        queue_id=queue.id,
        session_id=queue.session_id,
        user_id=queue.user_id,
        context_type=queue.context_type,
        context_id=queue.context_id,
        queue_state=queue.state.value,
        dispatch_mode=queue.dispatch_mode.value,
        is_paused=queue.is_paused,
        total_items=len(queue.items),
        waiting_items=_count_items(queue.items, {QueueItemState.NEW, QueueItemState.STAGED}),
        ready_items=_count_items(queue.items, {QueueItemState.READY, QueueItemState.RETRY_WAITING}),
        sending_items=_count_items(queue.items, {QueueItemState.SENDING}),
        sent_items=_count_items(queue.items, {QueueItemState.SENT}),
        failed_items=_count_items(queue.items, {QueueItemState.FAILED}),
        items=[
            QueueItemSnapshot(
                item_id=item.id,
                display_name=item.payload.get("id", item.id),
                state=item.state.value,
                attempt_count=item.attempt_count,
                created_at=item.created_at,
                last_attempt_at=item.last_attempt_at,
                last_error=item.last_error,
            )
            for item in queue.items
        ],
        last_updated_at=queue.updated_at,
    )


def _count_items(items: list[QueueItem], states: set[QueueItemState]) -> int:
    return len([item for item in items if item.state in states])
