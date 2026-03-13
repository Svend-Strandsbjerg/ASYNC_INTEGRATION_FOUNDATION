from __future__ import annotations

from async_integration_foundation.domain.models import DispatchMode, Queue, QueueItem, QueueItemState


def build_swimlane_immediate_queue(queue_id: str = "swimlane-q") -> Queue:
    queue = Queue(id=queue_id, name="swimlane-live-update", dispatch_mode=DispatchMode.IMMEDIATE)
    queue.items.append(
        QueueItem(
            id="card-1",
            queue_id=queue.id,
            payload={"id": "card-1", "from": "todo", "to": "in-progress"},
            state=QueueItemState.READY,
        )
    )
    return queue
