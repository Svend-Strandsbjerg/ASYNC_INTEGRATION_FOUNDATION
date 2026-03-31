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
        operation="update",
        payload={"hours": 1},
        metadata={"source": "poc"},
    )

    assert item.id == item_id
    assert item.queue_id == queue_id
    assert item.operation == "update"
    assert item.payload == {"hours": 1}
    assert item.metadata["source"] == "poc"


def test_camel_case_builder_alias_and_queue_contract() -> None:
    queue_id = createQueueId()
    item_id = createQueueItemId()

    item = buildQueueItem(
        queue_id=queue_id,
        item_id=item_id,
        operation="create",
        payload={"task": "approve"},
    )

    queue = Queue(id=queue_id, status=QueueStatus.PAUSED, items=[item])

    assert queue.status == QueueStatus.PAUSED
    assert queue.items[0].operation == "create"


def test_builder_can_generate_item_id_and_accept_explicit_routing_hints() -> None:
    queue_id = create_queue_id()

    item = build_queue_item(
        queue_id=queue_id,
        payload={"nested": {"any": "shape"}},
        adapter_key="adapter-x",
        target_system="system-y",
        payload_type="custom.type",
        idempotency_key="idem-custom",
    )

    assert item.item_id
    assert item.queue_id == queue_id
    assert item.payload == {"nested": {"any": "shape"}}
    assert item.adapter_key == "adapter-x"
    assert item.target_system == "system-y"
    assert item.payload_type == "custom.type"
    assert item.idempotency_key == "idem-custom"
