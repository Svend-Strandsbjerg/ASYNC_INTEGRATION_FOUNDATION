# Extensibility Model

## Core extension points

- `QueueRepository`: queue persistence and scoped lookup.
- `QueueActivityLog`: inspection-friendly event stream.
- `Dispatcher`: queue/item dispatch orchestration.
- `TransportAdapter`: outbound delivery abstraction.
- `PayloadMapper`: payload transformation boundary.
- `RetryPolicy`: retry eligibility decision.

## State-machine extensibility

State transitions and dispatchability are centralized in the domain state machine helpers.

This allows extensions to stay consistent:

- custom dispatchers can reuse transition validation
- retry coordinators can promote `RETRY_WAITING -> READY` in one place
- future replay tooling can intentionally handle `DEAD_LETTER`

## Retry/dead-letter extension hooks

The model already supports enterprise retry evolution without transport coupling:

- `max_attempts`
- `next_retry_at`
- optional `retry_policy_key`
- terminal `DEAD_LETTER` state

Future schedulers/backoff strategies can be layered on top without changing payload contracts.
