# Extensibility Model

## Core extension points

- `QueueRepository`: persistence abstraction for queue/item state and lookup.
- `QueueActivityLog`: queue/session activity stream abstraction.
- `Dispatcher`: dispatch orchestration boundary.
- `TransportAdapter`: outbound integration boundary.
- `PayloadMapper`: transforms generic payload contracts.
- `RetryPolicy` / `DispatchPolicy`: pluggable behavior controls.

## Generic payload + adapter mapping

Core queue items store generic payload contracts (`payload`, `payload_type`, `payload_version`).

Adapters and payload mappers transform those generic contracts into target-specific requests. This keeps framework domain models business-neutral and target-neutral.

## Metadata extensibility

Both `Queue` and `QueueItem` support optional opaque `metadata` fields.

Implementations should preserve metadata safely and avoid aliasing when creating objects from caller-provided dictionaries.
