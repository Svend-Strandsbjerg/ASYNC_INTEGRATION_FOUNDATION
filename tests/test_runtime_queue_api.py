from async_integration_foundation import (
    Queue,
    QueueStatus,
    buildQueueItem,
    build_queue_item,
    createQueueId,
    createQueueItemId,
    create_queue_id,
    create_queue_item_id,
)


def test_runtime_queue_ids_are_unique() -> None:
    queue_a = create_queue_id()
    queue_b = createQueueId()
    item_a = create_queue_item_id()
    item_b = createQueueItemId()

    assert isinstance(queue_a, str)
    assert isinstance(item_a, str)
    assert queue_a != queue_b
    assert item_a != item_b


def test_build_queue_item_contains_canonical_fields() -> None:
    queue_id = create_queue_id()
    item_id = create_queue_item_id()

    item = build_queue_item(
        queue_id=queue_id,
        item_id=item_id,
        block_id="block-1",
        operation="update",
        day="Wednesday",
        start_time="08:30",
        end_time="09:30",
        payload={"hours": 1},
        metadata={"source": "poc"},
    )

    assert item.id == item_id
    assert item.queue_id == queue_id
    assert item.operation == "update"
    assert item.scheduling.day_key == "Wednesday"
    assert item.scheduling.interval == "08:30 - 09:30"
    assert item.payload == {"hours": 1}
    assert item.metadata["source"] == "poc"
    assert item.metadata["block_id"] == "block-1"


def test_camel_case_builder_alias_and_queue_contract() -> None:
    queue_id = createQueueId()
    item_id = createQueueItemId()

    item = buildQueueItem(
        queue_id=queue_id,
        item_id=item_id,
        block_id="block-2",
        operation="create",
        day="Monday",
        start_time="13:00",
        end_time="14:30",
        interval="13:00 - 14:30",
        payload={"id": "block-2"},
    )

    queue = Queue(id=queue_id, status=QueueStatus.PAUSED, items=[item])

    assert queue.status == QueueStatus.PAUSED
    assert queue.items[0].operation == "create"
