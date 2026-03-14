# ASYNC_INTEGRATION_FOUNDATION

`ASYNC_INTEGRATION_FOUNDATION` is a reusable technical foundation for building asynchronous integration and queue-driven workflows with explicit lifecycle control.

## What this framework provides

- Generic queue + queue item domain model
- Explicit queue state machine: `OPEN`, `PAUSED`, `DISPATCHING`, `COMPLETED`
- Explicit queue item state machine: `NEW`, `READY`, `DISPATCHING`, `SENT`, `FAILED`, `RETRY_WAITING`, `DEAD_LETTER`
- Centralized dispatchability rules (`READY` only)
- Deterministic queue dispatch ordering by `sequence_number`
- Retry metadata support (`next_retry_at`, `max_attempts`, optional `retry_policy_key`)
- Dead-letter terminal semantics
- In-memory reference repository/dispatcher/transport implementations
- Queue snapshot read model and activity log hooks

## Quick start

```bash
python -m pytest
```

## Docs

- `ARCHITECTURE.md`
- `docs/framework/state-model.md`
- `docs/framework/queue-model.md`
- `docs/framework/dispatch-lifecycle.md`
- `docs/framework/retry-and-dead-letter.md`
