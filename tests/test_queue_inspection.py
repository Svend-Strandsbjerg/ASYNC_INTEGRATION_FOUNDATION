from async_integration_foundation.contracts.mapper import IdentityPayloadMapper
from async_integration_foundation.contracts.policy import MaxAttemptsRetryPolicy
from async_integration_foundation.domain.models import DispatchMode, QueueItem, QueueItemState, QueueState
from async_integration_foundation.implementations.in_memory import InMemoryQueueActivityLog, InMemoryQueueRepository
from async_integration_foundation.implementations.mock_transport import MockTransportAdapter
from async_integration_foundation.implementations.orchestrator import MockDispatcher
from async_integration_foundation.implementations.queue_services import QueueResolver, build_queue_snapshot


def test_get_or_create_queue_by_scope_returns_existing_queue() -> None:
    repo = InMemoryQueueRepository()
    resolver = QueueResolver(repository=repo)

    first = resolver.get_or_create_queue(
        session_id="session-1",
        context_type="timesheet_day",
        context_id="2026-03-13",
        dispatch_mode=DispatchMode.MANUAL_COMMIT,
        user_id="u-1",
    )
    second = resolver.get_or_create_queue(
        session_id="session-1",
        context_type="timesheet_day",
        context_id="2026-03-13",
        dispatch_mode=DispatchMode.IMMEDIATE,
    )

    assert first.queue_id == second.queue_id
    assert repo.get_queue_by_scope("session-1", "timesheet_day", "2026-03-13") is not None


def test_list_queues_by_session_and_context() -> None:
    repo = InMemoryQueueRepository()
    resolver = QueueResolver(repository=repo)

    resolver.get_or_create_queue("s-1", "workflow", "a", DispatchMode.MANUAL_COMMIT)
    resolver.get_or_create_queue("s-1", "workflow", "b", DispatchMode.MANUAL_COMMIT)
    resolver.get_or_create_queue("s-1", "timesheet_day", "c", DispatchMode.MANUAL_COMMIT)
    resolver.get_or_create_queue("s-2", "workflow", "d", DispatchMode.MANUAL_COMMIT)

    assert len(repo.list_queues_by_session("s-1")) == 3
    assert len(repo.list_queues_by_context("s-1", "workflow")) == 2


def test_queue_snapshot_contains_read_model_fields() -> None:
    repo = InMemoryQueueRepository()
    resolver = QueueResolver(repository=repo)
    queue = resolver.get_or_create_queue(
        "s-1",
        "workflow",
        "4711",
        DispatchMode.MANUAL_COMMIT,
        user_id="user-7",
        correlation_id="corr-4711",
        business_key="work-order-4711",
        external_reference="ext-4711",
    )

    resolver.add_item(
        queue.queue_id,
        QueueItem(
            item_id="item-1",
            queue_id=queue.queue_id,
            payload={"label": "Approve"},
            state=QueueItemState.NEW,
        ),
    )
    saved = repo.get_queue(queue.queue_id)
    assert saved is not None

    saved.items.append(QueueItem(id="item-2", queue_id=queue.id, payload={"status": "waiting"}, state=QueueItemState.RETRY_WAITING))
    saved.items.append(QueueItem(id="item-3", queue_id=queue.id, payload={"status": "dead"}, state=QueueItemState.DEAD_LETTER))

    snapshot = build_queue_snapshot(saved)

    assert snapshot.queue_id == queue.queue_id
    assert snapshot.queue_type == "workflow"
    assert snapshot.session_id == "s-1"
    assert snapshot.user_id == "user-7"
    assert snapshot.context_type == "workflow"
    assert snapshot.context_id == "4711"
    assert snapshot.total_items == 3
    assert snapshot.new_items == 1
    assert snapshot.retry_waiting_items == 1
    assert snapshot.dead_letter_items == 1
    assert snapshot.has_retry_waiting_items is True
    assert snapshot.has_dead_letter_items is True
    assert snapshot.items[0].item_id == "item-1"
    assert snapshot.items[0].queue_id == queue.queue_id
    assert snapshot.items[0].sequence_number == 1
    assert snapshot.items[0].payload_type is None
    assert snapshot.items[0].adapter_key is None
    assert snapshot.items[0].target_system is None
    assert snapshot.items[0].operation is None
    assert snapshot.items[0].idempotency_key is None
    assert snapshot.items[0].display_name == "item-1"


def test_pause_blocks_dispatch_but_add_item_is_allowed() -> None:
    repo = InMemoryQueueRepository()
    resolver = QueueResolver(repository=repo)
    queue = resolver.get_or_create_queue("s-1", "workflow", "4711", DispatchMode.IMMEDIATE)
    resolver.add_item(queue.id, QueueItem(id="item-1", queue_id=queue.id, payload={"value": "item-1"}, state=QueueItemState.READY))

    paused = resolver.pause_queue(queue.id)
    assert paused.state == QueueState.PAUSED

    resolver.add_item(queue.id, QueueItem(id="item-2", queue_id=queue.id, payload={"value": "item-2"}, state=QueueItemState.NEW))

    dispatcher = MockDispatcher(
        repository=repo,
        transport=MockTransportAdapter(),
        mapper=IdentityPayloadMapper(),
        retry_policy=MaxAttemptsRetryPolicy(),
    )

    resolved = dispatcher.dispatch_queue(queue.id)
    assert resolved.state == QueueState.PAUSED
    assert resolved.items[0].state == QueueItemState.READY


def test_activity_log_records_queue_actions_and_dispatch_events() -> None:
    repo = InMemoryQueueRepository()
    activity = InMemoryQueueActivityLog()
    resolver = QueueResolver(repository=repo, activity_log=activity)

    queue = resolver.get_or_create_queue("s-1", "workflow", "4711", DispatchMode.IMMEDIATE)
    resolver.add_item(
        queue.queue_id,
        QueueItem(item_id="item-1", queue_id=queue.queue_id, payload={"item_ref": "item-1"}, item_state=QueueItemState.READY),
    )

    dispatcher = MockDispatcher(
        repository=repo,
        transport=MockTransportAdapter(),
        mapper=IdentityPayloadMapper(),
        retry_policy=MaxAttemptsRetryPolicy(),
        activity_log=activity,
    )
    dispatcher.dispatch_queue(queue.queue_id)

    event_types = [event.event_type.value for event in activity.list_for_queue(queue.queue_id)]
    assert "queue_created" in event_types
    assert "item_added" in event_types
    assert "dispatch_started" in event_types
    assert "item_sent" in event_types
    assert "dispatch_completed" in event_types


def test_activity_log_records_dispatch_failure() -> None:
    repo = InMemoryQueueRepository()
    activity = InMemoryQueueActivityLog()
    resolver = QueueResolver(repository=repo, activity_log=activity)

    queue = resolver.get_or_create_queue("s-1", "workflow", "f-1", DispatchMode.IMMEDIATE)
    resolver.add_item(
        queue.queue_id,
        QueueItem(item_id="bad", queue_id=queue.queue_id, payload={"item_ref": "bad"}, item_state=QueueItemState.READY),
    )

    dispatcher = MockDispatcher(
        repository=repo,
        transport=MockTransportAdapter(fail_payload_keys={'{"item_ref": "bad"}'}, retryable=False),
        mapper=IdentityPayloadMapper(),
        retry_policy=MaxAttemptsRetryPolicy(),
        activity_log=activity,
    )
    resolved = dispatcher.dispatch_queue(queue.queue_id)

    assert resolved.state == QueueState.COMPLETED
    assert resolved.items[0].state == QueueItemState.DEAD_LETTER
    event_types = [event.event_type.value for event in activity.list_for_session("s-1")]
    assert "dispatch_failed" in event_types


def test_queue_and_item_identifiers_are_unique_and_stable() -> None:
    first_queue = QueueResolver(repository=InMemoryQueueRepository()).get_or_create_queue(
        "s-1", "workflow", "id-a", DispatchMode.MANUAL_COMMIT
    )
    second_queue = QueueResolver(repository=InMemoryQueueRepository()).get_or_create_queue(
        "s-2", "workflow", "id-b", DispatchMode.MANUAL_COMMIT
    )

    first_item = QueueItem(queue_id=first_queue.queue_id)
    second_item = QueueItem(queue_id=first_queue.queue_id)

    assert first_queue.queue_id != second_queue.queue_id
    assert first_item.item_id != second_item.item_id
    assert first_item.item_id == first_item.id


def test_add_item_assigns_sequence_and_metadata_is_isolated() -> None:
    repo = InMemoryQueueRepository()
    resolver = QueueResolver(repository=repo)

    shared_metadata = {"origin": "ui"}
    queue = resolver.get_or_create_queue(
        "s-1",
        "workflow",
        "meta-1",
        DispatchMode.MANUAL_COMMIT,
        metadata=shared_metadata,
    )

    item_metadata = {"k": "v"}
    first = QueueItem(item_id="1", payload={"value": "1"}, metadata=item_metadata)
    second = QueueItem(item_id="2", payload={"value": "2"}, metadata={"k": "v2"})

    resolver.add_item(queue.queue_id, first)
    resolver.add_item(queue.queue_id, second)

    shared_metadata["origin"] = "mutated"
    item_metadata["k"] = "mutated"

    saved = repo.get_queue(queue.queue_id)
    assert saved is not None
    assert saved.metadata["origin"] == "ui"
    assert saved.items[0].sequence_number == 1
    assert saved.items[1].sequence_number == 2
    assert saved.items[0].metadata["k"] == "v"


def test_add_item_rejects_explicit_queue_mismatch() -> None:
    repo = InMemoryQueueRepository()
    resolver = QueueResolver(repository=repo)
    queue = resolver.get_or_create_queue("s-1", "workflow", "ctx", DispatchMode.MANUAL_COMMIT)

    try:
        resolver.add_item(queue.queue_id, QueueItem(item_id="x", queue_id="another-queue", payload={}))
        assert False, "Expected queue mismatch ValueError"
    except ValueError as error:
        assert "queue_id mismatch" in str(error)
