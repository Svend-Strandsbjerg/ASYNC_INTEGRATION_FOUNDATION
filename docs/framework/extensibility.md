# Extensibility Model

## Core extension points

The framework exposes contracts that isolate orchestration from infrastructure and business mapping logic.

- `QueueRepository`: persistence abstraction for queue and item state.
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
