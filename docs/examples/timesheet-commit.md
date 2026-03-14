# Example: Timesheet Commit Flow

## Scenario

Timesheet entries are prepared and committed in a controlled batch.

## Reference flow

1. Create queue (`OPEN`).
2. Add entries (`NEW` or `READY`).
3. Promote staged entries (`NEW -> READY`) when commit occurs.
4. Optional pause/resume for operator control.
5. Dispatch queue; items move through `READY -> DISPATCHING -> SENT|FAILED`.
6. Route failed items to `RETRY_WAITING` or `DEAD_LETTER`.
7. Inspect queue snapshot counters and retry/dead-letter status.
