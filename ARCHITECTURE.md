# ASYNC_INTEGRATION_FOUNDATION Architecture

## Purpose

This document defines the target architecture of the async integration foundation and the phased strategy for implementing runtime behavior safely.

## Architecture principles

- Framework first, use case second
- Explicit state and transitions
- Pluggable transports and policies
- Business-neutral core orchestration
- Observability-ready status tracking
- Incremental delivery with test-backed changes

## High-level module structure

```text
src/async_integration_foundation/
  domain/
    models.py          # Queue/QueueItem entities and states
  contracts/
    persistence.py     # Queue persistence contract
    dispatcher.py      # Dispatch/orchestrator contract
    transport.py       # Outbound transport adapter contract
    mapper.py          # Payload mapping contract
    policy.py          # Retry and dispatch policy contracts
  implementations/
    in_memory.py       # In-memory queue repository
    mock_transport.py  # Mock outbound adapter
    orchestrator.py    # Reference dispatcher/orchestrator
  examples/
    timesheet.py       # Reference staged commit flow
    swimlane.py        # Reference immediate dispatch flow
```

## Core domain model

The framework separates queue-level and item-level state to support staged commit, immediate dispatch, and partial failure visibility.

- Queue: lifecycle container for dispatch operations.
- QueueItem: unit of work sent through adapters.
- DispatchResult: normalized success/failure output from transport layer.

Detailed definitions live in:

- `docs/framework/queue-model.md`
- `docs/framework/state-model.md`
- `docs/framework/dispatch-lifecycle.md`

## Dispatch lifecycle (target flow)

1. Queue is created (`OPEN`).
2. Items are appended (`NEW`/`STAGED`).
3. Queue may be paused (`PAUSED`) and resumed (`OPEN`).
4. Queue is committed (`READY`) for batch dispatch, or item-level dispatch is triggered immediately.
5. Dispatcher transitions queue to `DISPATCHING` and item(s) to `SENDING`.
6. Transport adapter returns success/failure.
7. Retryable failures become `RETRY_WAITING`; non-retryable failures become `FAILED`.
8. Queue resolves to `COMPLETED`, `PARTIAL_FAILED`, or `FAILED` based on aggregate item status.

## Phase-based implementation strategy

### Phase 1: Foundation shaping

- Repository identity and architecture docs updated for async integration scope.
- Module boundaries and contracts documented.

### Phase 2: Model and contracts

- Queue/item state model implemented.
- Persistence, dispatch, adapter, mapper, and policy interfaces established.

### Phase 3: Reference implementation

- In-memory persistence.
- Mock transport adapter.
- Mock/reference orchestrator.
- Example flows and tests.

### Phase 4: Production runtime evolution

Future iterations can add:

- advanced pause/unpause semantics,
- ordered dispatch guarantees,
- richer retry backoff,
- telemetry hooks,
- persistence backends,
- operational controls.

## Governance and workflow architecture

The repository keeps the template governance model:

- branch-based workflow,
- PR-first change management,
- CI checks,
- documented standards and process,
- human-reviewed merges.

These controls ensure framework evolution remains safe, auditable, and maintainable.
