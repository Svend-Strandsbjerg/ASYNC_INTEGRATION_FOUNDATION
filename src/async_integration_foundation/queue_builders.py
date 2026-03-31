from __future__ import annotations

from typing import Any, NewType
from uuid import uuid4

from .domain.models import QueueItem, QueueOperation

QueueId = NewType("QueueId", str)
QueueItemId = NewType("QueueItemId", str)


def create_queue_id() -> QueueId:
    return QueueId(str(uuid4()))


def create_queue_item_id() -> QueueItemId:
    return QueueItemId(str(uuid4()))


def build_queue_item(
    *,
    queue_id: QueueId,
    item_id: QueueItemId | None = None,
    payload: Any = None,
    operation: QueueOperation | None = None,
    item_type: str | None = None,
    payload_type: str | None = None,
    payload_version: str | None = None,
    adapter_key: str | None = None,
    target_system: str | None = None,
    idempotency_key: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> QueueItem:
    return QueueItem(
        item_id=str(item_id) if item_id is not None else str(create_queue_item_id()),
        queue_id=str(queue_id),
        item_type=item_type,
        operation=operation,
        payload_type=payload_type,
        payload_version=payload_version,
        adapter_key=adapter_key,
        target_system=target_system,
        idempotency_key=idempotency_key,
        payload={} if payload is None else payload,
        metadata=dict(metadata or {}),
    )
