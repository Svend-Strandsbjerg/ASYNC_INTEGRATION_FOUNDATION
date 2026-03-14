# ASYNC_INTEGRATION_FOUNDATION Architecture

## Purpose

This document defines the target architecture of the async integration foundation.

## Architecture principles

- Framework-first and business-neutral core
- Explicit queue/item state and lifecycle
- Stable technical identifiers and clear entity linkage
- Generic payload contract with adapter-driven mapping
- Pluggable persistence, transport, and policy boundaries
- Incremental, test-backed delivery

## Module structure

```text
src/async_integration_foundation/
  domain/models.py
  contracts/
    persistence.py
    activity.py
    dispatcher.py
    transport.py
    mapper.py
    policy.py
  implementations/
    in_memory.py
    queue_services.py
    orchestrator.py
    mock_transport.py
  examples/
    timesheet.py
    swimlane.py
```

## Core model shape

### Queue

Technical identity and queue metadata:

- `queue_id` (technical key)
- `queue_type`, `queue_state`, `dispatch_mode`
- scope: `session_id`, `user_id`, `context_type`, `context_id`
- traceability/reference: `correlation_id`, `business_key`, `external_reference`
- timestamps and metadata

### QueueItem

Dispatch unit with explicit queue linkage:

- `item_id` (technical key)
- `queue_id` (parent queue reference)
- `sequence_number` for deterministic order
- payload contract: `payload`, `payload_type`, `payload_version`
- routing metadata: `adapter_key`, `target_system`, `operation`
- traceability/reference/idempotency metadata
- retry and attempt tracking fields

## Mapping architecture

Queue items store **generic** payload contracts.

Target-specific request structures are built through `PayloadMapper` + `TransportAdapter` implementations. The domain model intentionally avoids SAP/ServiceNow specific schemas.
