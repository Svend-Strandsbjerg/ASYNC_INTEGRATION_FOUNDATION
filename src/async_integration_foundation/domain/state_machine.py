from __future__ import annotations

from datetime import datetime, timezone

from async_integration_foundation.domain.models import Queue, QueueItem, QueueItemState, QueueState

ITEM_TRANSITIONS: dict[QueueItemState, set[QueueItemState]] = {
    QueueItemState.NEW: {QueueItemState.READY},
    QueueItemState.READY: {QueueItemState.DISPATCHING},
    QueueItemState.DISPATCHING: {QueueItemState.SENT, QueueItemState.FAILED},
    QueueItemState.FAILED: {QueueItemState.RETRY_WAITING, QueueItemState.DEAD_LETTER},
    QueueItemState.RETRY_WAITING: {QueueItemState.READY},
    QueueItemState.SENT: set(),
    QueueItemState.DEAD_LETTER: set(),
}

QUEUE_TRANSITIONS: dict[QueueState, set[QueueState]] = {
    QueueState.OPEN: {QueueState.PAUSED, QueueState.DISPATCHING, QueueState.COMPLETED},
    QueueState.PAUSED: {QueueState.OPEN, QueueState.DISPATCHING, QueueState.COMPLETED},
    QueueState.DISPATCHING: {QueueState.OPEN, QueueState.COMPLETED, QueueState.PAUSED},
    QueueState.COMPLETED: {QueueState.OPEN, QueueState.PAUSED},
}


DISPATCHABLE_ITEM_STATES = {QueueItemState.READY}


ACTIVE_ITEM_STATES = {
    QueueItemState.NEW,
    QueueItemState.READY,
    QueueItemState.DISPATCHING,
    QueueItemState.FAILED,
    QueueItemState.RETRY_WAITING,
}


def transition_item_state(item: QueueItem, to_state: QueueItemState) -> None:
    if item.state == to_state:
        return
    allowed = ITEM_TRANSITIONS[item.state]
    if to_state not in allowed:
        raise ValueError(f"Invalid queue item transition: {item.state.value} -> {to_state.value}")
    item.state = to_state


def transition_queue_state(queue: Queue, to_state: QueueState) -> None:
    if queue.state == to_state:
        return
    allowed = QUEUE_TRANSITIONS[queue.state]
    if to_state not in allowed:
        raise ValueError(f"Invalid queue transition: {queue.state.value} -> {to_state.value}")
    queue.state = to_state


def is_item_dispatchable(item: QueueItem) -> bool:
    return item.state in DISPATCHABLE_ITEM_STATES


def is_retry_due(item: QueueItem, now: datetime | None = None) -> bool:
    if item.state != QueueItemState.RETRY_WAITING:
        return False
    if item.next_retry_at is None:
        return True
    at = now or datetime.now(timezone.utc)
    return item.next_retry_at <= at


def derive_queue_post_dispatch_state(queue: Queue) -> QueueState:
    if any(item.state in ACTIVE_ITEM_STATES for item in queue.items):
        return QueueState.OPEN
    return QueueState.COMPLETED
