"""Public runtime API for ASYNC_INTEGRATION_FOUNDATION."""

from .domain.models import Queue, QueueItem, QueueOperation, QueueState
from .queue_builders import (
    QueueId,
    QueueItemId,
    build_queue_item,
    create_queue_id,
    create_queue_item_id,
)

QueueStatus = QueueState

# CamelCase aliases for cross-runtime adapter parity.
createQueueId = create_queue_id
createQueueItemId = create_queue_item_id
buildQueueItem = build_queue_item

__all__ = [
    "Queue",
    "QueueId",
    "QueueItem",
    "QueueItemId",
    "QueueOperation",
    "QueueState",
    "QueueStatus",
    "build_queue_item",
    "buildQueueItem",
    "create_queue_id",
    "createQueueId",
    "create_queue_item_id",
    "createQueueItemId",
]
