# Dispatch Lifecycle

## Lifecycle summary

The dispatch lifecycle separates staging, readiness, sending, and post-send resolution.

1. Create queue in `OPEN`.
2. Append items in `NEW` (or directly `READY` for immediate mode).
3. Stage items (`STAGED`) when using manual commit.
4. Commit queue/items to `READY`.
5. Dispatch transitions queue to `DISPATCHING` and item(s) to `SENDING`.
6. Transport result resolves items to `SENT`, `FAILED`, or `RETRY_WAITING`.
7. Queue aggregate state resolves to `COMPLETED`, `PARTIAL_FAILED`, or `FAILED`.

## Supported dispatch patterns

- Manual commit queue dispatch
- Immediate dispatch on append
- Batch dispatch for all ready items
- Single-item dispatch
- Ordered dispatch (reference ordering by insertion)

## Retry lifecycle

- Retryable failure increments `attempt_count` and moves item to `RETRY_WAITING`.
- Retry operation promotes retry-waiting items back to `READY` when attempts remain.
- Non-retryable failures move item directly to `FAILED`.
