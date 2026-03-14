# ASYNC_INTEGRATION_FOUNDATION

`ASYNC_INTEGRATION_FOUNDATION` is a reusable technical foundation for building **asynchronous integration and queue-driven workflows** with strong engineering governance.

It is intentionally business-neutral and transport-neutral. The repository provides architecture, contracts, reference implementations, and process standards for safely developing async integration capabilities with human + AI collaboration.

## Repository goals

This foundation is designed to support future use cases without coupling core logic to a single domain:

- Manual staging + commit flows (for example, timesheet commit)
- Immediate dispatch flows (for example, live swimlane updates)
- Batch and single-item dispatch
- Ordered dispatch
- Retry-aware delivery with status visibility
- SAP and non-SAP outbound targets through pluggable adapters

## Engineering and governance model

This repository preserves the `REPO_FOUNDATION` discipline:

- Branch-based development with PR-first delivery
- Human review before merge to `main`
- CI validation and repository hygiene checks
- Documentation-driven change management
- Explicit AI agent operating rules in `AGENTS.md`

## Framework scope (current phase)

The current implementation focuses on **foundation shaping and reference behavior**:

- Queue and queue-item domain/state models
- Dispatch lifecycle and interface contracts
- In-memory persistence implementation
- Scoped queue lookup and queue resolution helper APIs
- Queue snapshot read model and lightweight activity logging
- Mock transport adapter and dispatcher/orchestrator
- Reference examples for timesheet commit and swimlane immediate dispatch
- Tests for key state transitions and retry behavior

A full production-grade runtime engine is intentionally out of scope for this first delivery.

## Repository map

- `ARCHITECTURE.md`: target framework architecture and phased implementation strategy.
- `AGENTS.md`: AI contributor operating rules.
- `CONTRIBUTING.md`: contribution workflow for humans and AI agents.
- `docs/framework/`: queue model, state model, lifecycle, extensibility, and inspection docs.
- `docs/examples/`: example flow documentation.
- `src/async_integration_foundation/`: framework contracts and reference implementation.
- `tests/`: test coverage for foundation behavior.

## Quick start (local)

```bash
python -m pytest
```

## Non-goals

This repository does **not** currently attempt to:

- Replace enterprise message brokers
- Deliver production infrastructure/runtime hardening in one step
- Encode business-specific policies directly in core modules

Instead, it establishes a clear, extensible baseline that future iterations can evolve safely.
