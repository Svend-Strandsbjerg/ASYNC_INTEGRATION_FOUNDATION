# State Model

## Queue states

The queue lifecycle is intentionally explicit and constrained.

- `OPEN`: queue can accept items and can dispatch eligible items.
- `PAUSED`: queue can still accept items but dispatch is blocked.
- `DISPATCHING`: queue is currently dispatching one or more items.
- `COMPLETED`: queue has no active work left.

Allowed queue transitions:

- `OPEN -> PAUSED`
- `PAUSED -> OPEN` (or back to the pre-pause active state)
- `OPEN -> DISPATCHING`
- `DISPATCHING -> OPEN`
- `OPEN -> COMPLETED`
- `PAUSED -> COMPLETED`

## Queue item states

Each queue item has its own lifecycle.

- `NEW`: item exists but is not dispatchable.
- `READY`: item is dispatchable.
- `DISPATCHING`: item is currently being sent.
- `SENT`: terminal success state.
- `FAILED`: failed attempt captured before retry/dead-letter routing.
- `RETRY_WAITING`: waiting for retry eligibility (`next_retry_at`).
- `DEAD_LETTER`: terminal failure state (no automatic retry).

Allowed item transitions:

- `NEW -> READY`
- `READY -> DISPATCHING`
- `DISPATCHING -> SENT`
- `DISPATCHING -> FAILED`
- `FAILED -> RETRY_WAITING`
- `RETRY_WAITING -> READY`
- `FAILED -> DEAD_LETTER`

Invalid transitions are rejected by the shared state machine helpers.

## Dispatchability rules

Dispatchability is centralized and deterministic:

- dispatchable: `READY`
- non-dispatchable: `NEW`, `DISPATCHING`, `SENT`, `FAILED`, `RETRY_WAITING`, `DEAD_LETTER`

Queue dispatch selects eligible items in ascending `sequence_number` order.
