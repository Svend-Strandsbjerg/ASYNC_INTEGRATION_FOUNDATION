from datetime import datetime, timedelta, timezone

from async_integration_foundation.contracts.mapper import IdentityPayloadMapper
from async_integration_foundation.contracts.policy import MaxAttemptsRetryPolicy
from async_integration_foundation.domain.models import QueueItemState, QueueState
from async_integration_foundation.examples.swimlane import build_swimlane_immediate_queue
from async_integration_foundation.examples.timesheet import build_timesheet_commit_queue
from async_integration_foundation.implementations.in_memory import InMemoryQueueRepository
from async_integration_foundation.implementations.mock_transport import MockTransportAdapter
from async_integration_foundation.implementations.orchestrator import MockDispatcher


def _build_dispatcher(transport: MockTransportAdapter) -> tuple[InMemoryQueueRepository, MockDispatcher]:
    repo = InMemoryQueueRepository()
    dispatcher = MockDispatcher(
        repository=repo,
        transport=transport,
        mapper=IdentityPayloadMapper(),
        retry_policy=MaxAttemptsRetryPolicy(),
    )
    return repo, dispatcher


def test_timesheet_commit_dispatch_success() -> None:
    repo, dispatcher = _build_dispatcher(MockTransportAdapter())
    queue = build_timesheet_commit_queue()
    repo.create_queue(queue)

    resolved = dispatcher.dispatch_queue(queue.id)

    assert resolved.state == QueueState.COMPLETED
    assert all(item.state == QueueItemState.SENT for item in resolved.items)


def test_swimlane_immediate_dispatch_success() -> None:
    repo, dispatcher = _build_dispatcher(MockTransportAdapter())
    queue = build_swimlane_immediate_queue()
    repo.create_queue(queue)

    resolved = dispatcher.dispatch_item(queue.id, "card-1")

    assert resolved.state == QueueState.COMPLETED
    assert resolved.items[0].state == QueueItemState.SENT


def test_dispatch_item_unknown_id_does_not_mutate_queue_state_or_dispatch() -> None:
    transport = MockTransportAdapter()
    repo, dispatcher = _build_dispatcher(transport)
    queue = build_timesheet_commit_queue()
    repo.create_queue(queue)

    original_state = queue.state

    try:
        dispatcher.dispatch_item(queue.id, "missing-item")
        assert False, "Expected ValueError for unknown queue item"
    except ValueError as error:
        assert "Queue item not found" in str(error)

    persisted = repo.get_queue(queue.id)
    assert persisted is not None
    assert persisted.state == original_state
    assert all(item.attempt_count == 0 for item in persisted.items)
    assert all(item.state == QueueItemState.READY for item in persisted.items)
    assert transport.sent_payloads == []


def test_dispatch_item_sent_item_is_rejected_without_mutation() -> None:
    transport = MockTransportAdapter()
    repo, dispatcher = _build_dispatcher(transport)
    queue = build_swimlane_immediate_queue()
    queue.items[0].state = QueueItemState.SENT
    queue.state = QueueState.COMPLETED
    repo.create_queue(queue)

    resolved = dispatcher.dispatch_item(queue.id, "card-1")

    assert resolved.state == QueueState.COMPLETED
    assert resolved.items[0].state == QueueItemState.SENT
    assert resolved.items[0].attempt_count == 0
    assert transport.sent_payloads == []


def test_dispatch_item_only_target_dispatchable_item_is_mutated() -> None:
    transport = MockTransportAdapter()
    repo, dispatcher = _build_dispatcher(transport)
    queue = build_timesheet_commit_queue()
    queue.items[1].state = QueueItemState.DEAD_LETTER
    repo.create_queue(queue)

    resolved = dispatcher.dispatch_item(queue.id, "ts-1")

    sent = next(item for item in resolved.items if item.id == "ts-1")
    untouched = next(item for item in resolved.items if item.id == "ts-2")
    assert sent.state == QueueItemState.SENT
    assert sent.attempt_count == 1
    assert untouched.state == QueueItemState.DEAD_LETTER
    assert untouched.attempt_count == 0
    assert transport.sent_payloads == [{"id": "ts-1", "hours": 8}]


def test_retry_waiting_then_dead_letter_when_attempt_budget_exhausted() -> None:
    transport = MockTransportAdapter(fail_payload_keys={"ts-1"}, retryable=True)
    repo, dispatcher = _build_dispatcher(transport)
    queue = build_timesheet_commit_queue()
    queue.items[0].max_attempts = 2
    repo.create_queue(queue)

    first = dispatcher.dispatch_queue(queue.id)
    ts1 = [item for item in first.items if item.id == "ts-1"][0]
    assert ts1.state == QueueItemState.RETRY_WAITING
    assert ts1.next_retry_at is not None
    assert first.state == QueueState.OPEN

    second = dispatcher.retry_failed_items(queue.id)
    ts1_second = [item for item in second.items if item.id == "ts-1"][0]
    assert ts1_second.state == QueueItemState.DEAD_LETTER


def test_retry_waiting_is_not_dispatchable_directly() -> None:
    transport = MockTransportAdapter()
    repo, dispatcher = _build_dispatcher(transport)
    queue = build_swimlane_immediate_queue()
    queue.items[0].state = QueueItemState.RETRY_WAITING
    queue.items[0].next_retry_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    repo.create_queue(queue)

    resolved = dispatcher.dispatch_queue(queue.id)

    assert resolved.items[0].state == QueueItemState.RETRY_WAITING
    assert transport.sent_payloads == []


def test_only_ready_items_are_dispatched_in_sequence_number_order() -> None:
    transport = MockTransportAdapter()
    repo, dispatcher = _build_dispatcher(transport)
    queue = build_timesheet_commit_queue()
    queue.items[0].sequence_number = 10
    queue.items[1].sequence_number = 2
    queue.items[0].state = QueueItemState.READY
    queue.items[1].state = QueueItemState.NEW
    repo.create_queue(queue)

    dispatcher.dispatch_queue(queue.id)

    assert transport.sent_payloads == [{"id": "ts-1", "hours": 8}]


def test_non_dispatchable_states_cannot_dispatch() -> None:
    transport = MockTransportAdapter()
    repo, dispatcher = _build_dispatcher(transport)
    queue = build_swimlane_immediate_queue()
    repo.create_queue(queue)

    for state in [QueueItemState.NEW, QueueItemState.SENT, QueueItemState.DEAD_LETTER, QueueItemState.RETRY_WAITING]:
        queue.items[0].state = state
        queue.items[0].attempt_count = 0
        transport.sent_payloads.clear()
        resolved = dispatcher.dispatch_item(queue.id, "card-1")
        assert resolved.items[0].state == state
        assert resolved.items[0].attempt_count == 0
        assert transport.sent_payloads == []
