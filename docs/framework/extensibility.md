# Extensibility Model

## Core extension points

The framework exposes contracts that isolate orchestration from infrastructure and business mapping logic.

- `QueueRepository`: persistence abstraction for queue and item state, including scoped queue lookup.
- `QueueActivityLog`: lightweight activity stream abstraction for queue/session event inspection.
- `Dispatcher`: orchestration contract for dispatch operations.
- `TransportAdapter`: outbound transport integration point.
- `PayloadMapper`: payload transformation boundary.
- `RetryPolicy` / `DispatchPolicy`: behavior and control policies.

## Adapter strategy

Transport adapters can target any outbound system:

- REST APIs
- event/message brokers
- SAP and non-SAP systems
- internal service endpoints

The core framework depends only on adapter contracts, not transport-specific implementations.

## Policy strategy

Policies are injectable to keep runtime behavior configurable without changing core orchestration.

Examples:

- max attempts
- retry eligibility
- dispatch ordering
- selective queue routing

## Persistence strategy

The first reference implementation uses in-memory storage.

Future backends (SQL/NoSQL/event store) can implement the same repository contract with no changes to queue/domain semantics.

## Application-facing queue ergonomics

Framework helpers (`QueueResolver`, `build_queue_snapshot`) provide additive capabilities for consuming applications:

- queue get-or-create by `(session_id, context_type, context_id)`
- queue listing by session/context scope
- stable queue snapshot read model for inspection endpoints
- lightweight activity history access without runtime coupling

These capabilities are discoverability/inspection-focused and do not change transport, lifecycle, or dispatch behavior.
