from __future__ import annotations

from async_integration_foundation.domain.models import DispatchMode, Queue, QueueItem, QueueItemState, QueueState


def build_timesheet_commit_queue(queue_id: str = "timesheet-q") -> Queue:
    queue = Queue(
        queue_id=queue_id,
        queue_type="timesheet-commit",
        dispatch_mode=DispatchMode.MANUAL_COMMIT,
        correlation_id="corr-timesheet-commit",
    )
    queue.items.extend(
        [
            QueueItem(id="ts-1", queue_id=queue.id, payload={"id": "ts-1", "hours": 8}, state=QueueItemState.READY),
            QueueItem(id="ts-2", queue_id=queue.id, payload={"id": "ts-2", "hours": 7.5}, state=QueueItemState.READY),
        ]
    )
    queue.state = QueueState.OPEN
    return queue
