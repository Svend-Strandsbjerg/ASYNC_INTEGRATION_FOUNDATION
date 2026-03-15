from __future__ import annotations

from typing import Any, NewType
from uuid import uuid4

from .domain.models import QueueItem, QueueOperation, QueueScheduling

QueueId = NewType("QueueId", str)
QueueItemId = NewType("QueueItemId", str)


def create_queue_id() -> QueueId:
    return QueueId(str(uuid4()))


def create_queue_item_id() -> QueueItemId:
    return QueueItemId(str(uuid4()))


def build_queue_item(
    *,
    queue_id: QueueId,
    item_id: QueueItemId,
    block_id: str,
    operation: QueueOperation,
    day: str,
    start_time: str,
    end_time: str,
    interval: str | None = None,
    payload: Any = None,
    metadata: dict[str, Any] | None = None,
) -> QueueItem:
    resolved_interval = interval or f"{start_time} - {end_time}"
    resolved_metadata = dict(metadata or {})
    resolved_metadata.setdefault("block_id", block_id)

    return QueueItem(
        item_id=str(item_id),
        queue_id=str(queue_id),
        operation=operation,
        scheduling=QueueScheduling(
            day_key=day,
            start_time=start_time,
            end_time=end_time,
            interval=resolved_interval,
        ),
        payload={} if payload is None else payload,
        metadata=resolved_metadata,
    )
