# Dispatch Lifecycle

## End-to-end flow

1. Queue is resolved/created in `OPEN`.
2. Items are added in `NEW` or directly in `READY`.
3. Optional pause/resume controls queue dispatch eligibility.
4. Queue dispatch transitions queue to `DISPATCHING`.
5. Eligible items (`READY` only) are selected in `sequence_number` order.
6. Item transitions: `READY -> DISPATCHING -> SENT|FAILED`.
7. Failed items transition to `RETRY_WAITING` or `DEAD_LETTER`.
8. Retry preparation promotes due retry items back to `READY`.
9. Queue resolves to `OPEN` (active work remains) or `COMPLETED` (no active work).

## Guarantees

- Non-dispatchable states are ignored.
- Queue `PAUSED` blocks dispatch.
- Retry-waiting items are never dispatched directly.
- Dead-letter items are terminal for automatic dispatch.
