# ASYNC_INTEGRATION_FOUNDATION

`ASYNC_INTEGRATION_FOUNDATION` is a reusable technical foundation for building **asynchronous integration and queue-driven workflows**.

It is intentionally business-neutral and transport-neutral.

## What is included

- Queue lifecycle and dispatch orchestration
- Enterprise-style queue and queue-item identifiers
- Queue/item linkage and ordering metadata
- Traceability, business reference, and idempotency fields
- Generic payload contracts and adapter routing metadata
- In-memory repository + snapshot read model
- Reference dispatcher, mock transport, and tests

## Enterprise queue/message model highlights

- Stable technical IDs: `queue_id`, `item_id`
- Explicit item linkage: `queue_id` on every item
- Ordering: `sequence_number`
- Traceability: `correlation_id`, `causation_id`, `request_id`
- Business references: `business_key`, `external_reference`
- Idempotency: `idempotency_key`
- Generic payload contract: `payload`, `payload_type`, `payload_version`
- Routing hints: `adapter_key`, `target_system`, `operation`
- Optional extensible metadata on both queue and queue item

## Documentation

- `ARCHITECTURE.md`
- `docs/framework/queue-model.md`
- `docs/framework/state-model.md`
- `docs/framework/extensibility.md`
- `docs/framework/message-contract.md`

## Quick start

```bash
python -m pytest
```
