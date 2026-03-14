# State Model

## Queue states

- `OPEN`: queue accepts new items.
- `PAUSED`: queue is blocked from dispatch.
- `READY`: queue is committed and dispatchable.
- `DISPATCHING`: queue is actively dispatching.
- `COMPLETED`: all items sent.
- `FAILED`: queue-level unsuccessful state.
- `PARTIAL_FAILED`: mixed item outcomes.
- `CANCELLED`: intentionally terminated.

## Queue item states

- `NEW`: created.
- `STAGED`: staged for manual commit.
- `READY`: eligible for dispatch.
- `SENDING`: in-flight.
- `SENT`: successful.
- `FAILED`: terminal failure.
- `RETRY_WAITING`: retryable failure.
- `CANCELLED`: cancelled.

## Additional state context

Queue and item state snapshots now include technical ids (`queue_id`, `item_id`), queue linkage (`queue_id` on item), and `sequence_number` for deterministic ordering.
