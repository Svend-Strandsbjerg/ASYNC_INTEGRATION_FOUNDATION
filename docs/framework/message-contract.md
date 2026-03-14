# Message Contract Model

## Purpose

Queue items carry a **generic integration message contract** that is target-neutral.

## Queue item payload contract

Each `QueueItem` supports:

- `payload`: message/command body
- `payload_type`: logical contract name (for example `timesheet.entry`)
- `payload_version`: version marker for contract evolution

These fields stay generic in core domain models. Adapter-specific request mapping happens outside the queue model.

## Routing and adapter metadata

Each `QueueItem` can carry routing hints:

- `adapter_key`
- `target_system`
- `operation`

These values are optional and generic. They inform adapter selection and mapping without embedding target-specific schemas in the core model.

## Traceability and idempotency

Queue items support:

- `correlation_id`
- `causation_id`
- `request_id`
- `idempotency_key`

These are metadata concerns and remain separate from technical keys (`queue_id`, `item_id`) and business references (`business_key`, `external_reference`).
