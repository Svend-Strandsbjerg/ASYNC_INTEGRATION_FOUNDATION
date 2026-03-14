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
from async_integration_foundation.domain.state_machine import transition_queue_state


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
        correlation_id: str | None = None,
        business_key: str | None = None,
        external_reference: str | None = None,
    ) -> Queue:
        existing = self.repository.get_queue_by_scope(
            session_id=session_id,
            context_type=context_type,
            context_id=context_id,
        )
        if existing is not None:
            return existing

        queue = Queue(
            queue_type=context_type,
            dispatch_mode=dispatch_mode,
            session_id=session_id,
            user_id=user_id,
            context_type=context_type,
            context_id=context_id,
            correlation_id=correlation_id,
            business_key=business_key,
            external_reference=external_reference,
            created_by=user_id,
            metadata=dict(metadata or {}),
        )
        created = self.repository.create_queue(queue)
        self._record(created, QueueActivityType.QUEUE_CREATED)
        return created

    def add_item(self, queue_id: str, item: QueueItem) -> Queue:
        queue = self._require_queue(queue_id)
        if item.sequence_number == 0:
            item.sequence_number = _next_sequence_number(queue.items)
        queue.items.append(item)
        saved = self.repository.save_queue(queue)
        self._record(saved, QueueActivityType.ITEM_ADDED, item_id=item.item_id)
        return saved

    def pause_queue(self, queue_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        queue.pre_pause_state = queue.state
        transition_queue_state(queue, QueueState.PAUSED)
        saved = self.repository.save_queue(queue)
        self._record(saved, QueueActivityType.QUEUE_PAUSED)
        return saved

    def resume_queue(self, queue_id: str) -> Queue:
        queue = self._require_queue(queue_id)
        resume_state = queue.pre_pause_state if queue.pre_pause_state != QueueState.PAUSED else QueueState.OPEN
        transition_queue_state(queue, resume_state)
        saved = self.repository.save_queue(queue)
        self._record(saved, QueueActivityType.QUEUE_RESUMED)
        return saved

    def _record(self, queue: Queue, event_type: QueueActivityType, item_id: str | None = None) -> None:
        if self.activity_log is None:
            return
        self.activity_log.record(
            queue_id=queue.queue_id,
            session_id=queue.session_id,
            event_type=event_type,
            item_id=item_id,
        )

    def _require_queue(self, queue_id: str) -> Queue:
        queue = self.repository.get_queue(queue_id)
        if queue is None:
            raise ValueError(f"Queue not found: {queue_id}")
        return queue

    def _next_sequence_number(self, queue: Queue) -> int:
        if not queue.items:
            return 1
        return max((item.sequence_number or 0) for item in queue.items) + 1


def build_queue_snapshot(queue: Queue) -> QueueSnapshot:
    return QueueSnapshot(
        queue_id=queue.queue_id,
        queue_type=queue.queue_type,
        session_id=queue.session_id,
        user_id=queue.user_id,
        context_type=queue.context_type,
        context_id=queue.context_id,
        correlation_id=queue.correlation_id,
        business_key=queue.business_key,
        external_reference=queue.external_reference,
        queue_state=queue.state.value,
        dispatch_mode=queue.dispatch_mode.value,
        is_paused=queue.is_paused,
        total_items=len(queue.items),
        new_items=_count_items(queue.items, {QueueItemState.NEW}),
        ready_items=_count_items(queue.items, {QueueItemState.READY}),
        dispatching_items=_count_items(queue.items, {QueueItemState.DISPATCHING}),
        sent_items=_count_items(queue.items, {QueueItemState.SENT}),
        failed_items=_count_items(queue.items, {QueueItemState.FAILED}),
        retry_waiting_items=_count_items(queue.items, {QueueItemState.RETRY_WAITING}),
        dead_letter_items=_count_items(queue.items, {QueueItemState.DEAD_LETTER}),
        has_retry_waiting_items=_count_items(queue.items, {QueueItemState.RETRY_WAITING}) > 0,
        has_dead_letter_items=_count_items(queue.items, {QueueItemState.DEAD_LETTER}) > 0,
        items=[
            QueueItemSnapshot(
                item_id=item.item_id,
                queue_id=item.queue_id,
                sequence_number=item.sequence_number,
                item_type=item.item_type,
                payload_type=item.payload_type,
                payload_version=item.payload_version,
                adapter_key=item.adapter_key,
                target_system=item.target_system,
                operation=item.operation,
                correlation_id=item.correlation_id,
                business_key=item.business_key,
                external_reference=item.external_reference,
                idempotency_key=item.idempotency_key,
                display_name=item.payload.get("id", item.item_id),
                state=item.state.value,
                attempt_count=item.attempt_count,
                created_at=item.created_at,
                last_attempt_at=item.last_attempt_at,
                next_retry_at=item.next_retry_at,
                last_error=item.last_error,
                metadata=dict(item.metadata),
            )
            for item in sorted(queue.items, key=lambda item: item.sequence_number or 0)
        ],
        metadata=dict(queue.metadata),
        last_updated_at=queue.updated_at,
    )


def _count_items(items: list[QueueItem], states: set[QueueItemState]) -> int:
    return len([item for item in items if item.state in states])


def _next_sequence_number(items: list[QueueItem]) -> int:
    if not items:
        return 1
    return max(item.sequence_number for item in items) + 1
