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
    assert all(item.state.value == "SENT" for item in resolved.items)


def test_swimlane_immediate_dispatch_success() -> None:
    repo, dispatcher = _build_dispatcher(MockTransportAdapter())
    queue = build_swimlane_immediate_queue()
    repo.create_queue(queue)

    resolved = dispatcher.dispatch_item(queue.id, "card-1")

    assert resolved.state == QueueState.COMPLETED
    assert resolved.items[0].state.value == "SENT"


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
    assert all(item.state == QueueItemState.STAGED for item in persisted.items)
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
    queue.items[1].state = QueueItemState.CANCELLED
    repo.create_queue(queue)

    resolved = dispatcher.dispatch_item(queue.id, "ts-1")

    sent = next(item for item in resolved.items if item.id == "ts-1")
    untouched = next(item for item in resolved.items if item.id == "ts-2")
    assert sent.state == QueueItemState.SENT
    assert sent.attempt_count == 1
    assert untouched.state == QueueItemState.CANCELLED
    assert untouched.attempt_count == 0
    assert transport.sent_payloads == [{"id": "ts-1", "hours": 8}]


def test_retry_waiting_then_fail_when_attempt_budget_exhausted() -> None:
    transport = MockTransportAdapter(fail_payload_keys={"ts-1"}, retryable=True)
    repo, dispatcher = _build_dispatcher(transport)
    queue = build_timesheet_commit_queue()
    repo.create_queue(queue)

    first = dispatcher.dispatch_queue(queue.id)
    ts1 = [item for item in first.items if item.id == "ts-1"][0]
    assert ts1.state.value == "RETRY_WAITING"
    assert first.state == QueueState.PARTIAL_FAILED

    second = dispatcher.retry_failed_items(queue.id)
    ts1_second = [item for item in second.items if item.id == "ts-1"][0]
    assert ts1_second.state.value == "RETRY_WAITING"

    third = dispatcher.retry_failed_items(queue.id)
    ts1_third = [item for item in third.items if item.id == "ts-1"][0]
    assert ts1_third.state.value == "FAILED"
    assert third.state == QueueState.PARTIAL_FAILED
