from __future__ import annotations

from async_integration_foundation.domain.models import DispatchMode, Queue, QueueItem, QueueItemState


def build_swimlane_immediate_queue(queue_id: str = "swimlane-q") -> Queue:
    queue = Queue(
        queue_id=queue_id,
        queue_type="swimlane-live-update",
        dispatch_mode=DispatchMode.IMMEDIATE,
        correlation_id="corr-swimlane-update",
    )
    queue.items.append(
        QueueItem(
            item_id="card-1",
            queue_id=queue.queue_id,
            sequence_number=1,
            payload={"id": "card-1", "from": "todo", "to": "in-progress"},
            payload_type="swimlane.move",
            payload_version="1.0",
            adapter_key="rest_api",
            target_system="workflow_board",
            operation="UPDATE",
            item_state=QueueItemState.READY,
        )
    )
    return queue
