# ASYNC_INTEGRATION_FOUNDATION Architecture

## Principles

- Framework-level and business-neutral
- Explicit state machines at queue and item levels
- Centralized transition validation and dispatchability logic
- Deterministic dispatch ordering
- Retry/dead-letter readiness without transport lock-in

## Core lifecycle

1. Queue starts in `OPEN`.
2. Items are created as `NEW` and promoted to `READY` when dispatchable.
3. Queue may move to `PAUSED`; dispatch is blocked while paused.
4. Dispatch transitions queue to `DISPATCHING` and items `READY -> DISPATCHING`.
5. Successful send: `DISPATCHING -> SENT`.
6. Failed send: `DISPATCHING -> FAILED`, then either:
   - `FAILED -> RETRY_WAITING` (with `next_retry_at`), or
   - `FAILED -> DEAD_LETTER`.
7. Retry preparation promotes `RETRY_WAITING -> READY` when due.
8. Queue resolves to `COMPLETED` when no active work remains; otherwise `OPEN`.

## Module layout

```text
src/async_integration_foundation/
  domain/
    models.py
    state_machine.py
  contracts/
  implementations/
  examples/
```

## Validation and safety

- Invalid queue/item transitions raise errors.
- Dispatch eligibility is defined once and reused by queue/item/retry paths.
- Snapshot read models provide state-distribution visibility for operations.
