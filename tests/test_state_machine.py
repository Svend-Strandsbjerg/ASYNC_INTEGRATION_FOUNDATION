import pytest

from async_integration_foundation.domain.models import Queue, QueueItem, QueueItemState, QueueState
from async_integration_foundation.domain.state_machine import transition_item_state, transition_queue_state


def test_valid_item_transitions() -> None:
    item = QueueItem(id="i1", queue_id="q1", payload={})
    transition_item_state(item, QueueItemState.READY)
    transition_item_state(item, QueueItemState.DISPATCHING)
    transition_item_state(item, QueueItemState.SENT)
    assert item.state == QueueItemState.SENT


def test_retry_and_dead_letter_item_transitions() -> None:
    item = QueueItem(id="i1", queue_id="q1", payload={}, state=QueueItemState.READY)
    transition_item_state(item, QueueItemState.DISPATCHING)
    transition_item_state(item, QueueItemState.FAILED)
    transition_item_state(item, QueueItemState.RETRY_WAITING)
    transition_item_state(item, QueueItemState.READY)
    transition_item_state(item, QueueItemState.DISPATCHING)
    transition_item_state(item, QueueItemState.FAILED)
    transition_item_state(item, QueueItemState.DEAD_LETTER)
    assert item.state == QueueItemState.DEAD_LETTER


def test_invalid_item_transition_is_rejected() -> None:
    item = QueueItem(id="i1", queue_id="q1", payload={})
    with pytest.raises(ValueError):
        transition_item_state(item, QueueItemState.SENT)


def test_queue_transitions() -> None:
    queue = Queue(id="q1", name="q")
    transition_queue_state(queue, QueueState.PAUSED)
    transition_queue_state(queue, QueueState.OPEN)
    transition_queue_state(queue, QueueState.DISPATCHING)
    transition_queue_state(queue, QueueState.OPEN)
    transition_queue_state(queue, QueueState.COMPLETED)
    assert queue.state == QueueState.COMPLETED
