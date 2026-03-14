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

    assert first.id == second.id
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
    queue = resolver.get_or_create_queue("s-1", "workflow", "4711", DispatchMode.MANUAL_COMMIT, user_id="user-7")

    resolver.add_item(
        queue.id,
        QueueItem(
            id="item-1",
            queue_id=queue.id,
            payload={"id": "item-1", "label": "Approve"},
            state=QueueItemState.NEW,
        ),
    )
    saved = repo.get_queue(queue.id)
    assert saved is not None

    saved.items.append(QueueItem(id="item-2", queue_id=queue.id, payload={"id": "item-2"}, state=QueueItemState.RETRY_WAITING))
    saved.items.append(QueueItem(id="item-3", queue_id=queue.id, payload={"id": "item-3"}, state=QueueItemState.DEAD_LETTER))

    snapshot = build_queue_snapshot(saved)

    assert snapshot.queue_id == queue.id
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
    assert snapshot.items[0].display_name == "item-1"


def test_pause_blocks_dispatch_but_add_item_is_allowed() -> None:
    repo = InMemoryQueueRepository()
    resolver = QueueResolver(repository=repo)
    queue = resolver.get_or_create_queue("s-1", "workflow", "4711", DispatchMode.IMMEDIATE)
    resolver.add_item(queue.id, QueueItem(id="item-1", queue_id=queue.id, payload={"id": "item-1"}, state=QueueItemState.READY))

    paused = resolver.pause_queue(queue.id)
    assert paused.state == QueueState.PAUSED

    resolver.add_item(queue.id, QueueItem(id="item-2", queue_id=queue.id, payload={"id": "item-2"}, state=QueueItemState.NEW))

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
        queue.id,
        QueueItem(id="item-1", queue_id=queue.id, payload={"id": "item-1"}, state=QueueItemState.READY),
    )

    dispatcher = MockDispatcher(
        repository=repo,
        transport=MockTransportAdapter(),
        mapper=IdentityPayloadMapper(),
        retry_policy=MaxAttemptsRetryPolicy(),
        activity_log=activity,
    )
    dispatcher.dispatch_queue(queue.id)

    event_types = [event.event_type.value for event in activity.list_for_queue(queue.id)]
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
        queue.id,
        QueueItem(id="bad", queue_id=queue.id, payload={"id": "bad"}, state=QueueItemState.READY),
    )

    dispatcher = MockDispatcher(
        repository=repo,
        transport=MockTransportAdapter(fail_payload_keys={"bad"}, retryable=False),
        mapper=IdentityPayloadMapper(),
        retry_policy=MaxAttemptsRetryPolicy(),
        activity_log=activity,
    )
    resolved = dispatcher.dispatch_queue(queue.id)

    assert resolved.state == QueueState.COMPLETED
    assert resolved.items[0].state == QueueItemState.DEAD_LETTER
    event_types = [event.event_type.value for event in activity.list_for_session("s-1")]
    assert "dispatch_failed" in event_types
