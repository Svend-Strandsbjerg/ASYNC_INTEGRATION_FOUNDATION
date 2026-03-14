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
            QueueItem(
                item_id="ts-1",
                queue_id=queue.queue_id,
                sequence_number=1,
                payload={"id": "ts-1", "hours": 8},
                payload_type="timesheet.entry",
                payload_version="1.0",
                adapter_key="rest_api",
                target_system="timesheet_backend",
                operation="CREATE",
                item_state=QueueItemState.STAGED,
            ),
            QueueItem(
                item_id="ts-2",
                queue_id=queue.queue_id,
                sequence_number=2,
                payload={"id": "ts-2", "hours": 7.5},
                payload_type="timesheet.entry",
                payload_version="1.0",
                adapter_key="rest_api",
                target_system="timesheet_backend",
                operation="CREATE",
                item_state=QueueItemState.STAGED,
            ),
        ]
    )
    queue.state = QueueState.READY
    return queue
