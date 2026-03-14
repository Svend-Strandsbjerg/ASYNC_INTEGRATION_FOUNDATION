# Queue Model

## Overview

The queue model defines the core entities used by the async integration foundation.

## Entities

### Queue

A queue represents a logical dispatch container.

Key fields:

- `id`: queue identifier
- `name`: logical queue name
- `state`: queue lifecycle state
- `dispatch_mode`: manual, immediate, batch, ordered, or single-item mode
- `created_at` / `updated_at`: timestamps
- `items`: queue item collection
- `session_id` / `user_id`: optional application-level scope identifiers
- `context_type` / `context_id`: optional logical context scoping metadata
- `metadata`: opaque application-level metadata
- `is_paused`: convenience property derived from queue state

### QueueItem

A queue item is a single dispatchable work unit.

Key fields:

- `id`: item identifier
- `queue_id`: parent queue
- `payload`: raw business payload
- `mapped_payload`: optional transport-specific payload
- `state`: item lifecycle state
- `attempt_count`: number of send attempts
- `max_attempts`: per-item retry budget
- `last_error`: latest error summary
- `created_at`: item creation timestamp
- `last_attempt_at`: latest dispatch attempt timestamp

### DispatchResult

Normalized result from a transport adapter.

Fields:

- `success`: boolean
- `retryable`: whether retry is allowed
- `external_reference`: optional target reference
- `error_message`: optional failure details

### QueueSnapshot

Read-optimized projection for stable queue inspection.

Fields include:

- queue identifiers and scope metadata
- queue lifecycle/dispatch fields
- item counters by state category
- item snapshots with attempt/error/timestamps
- `last_updated_at`

### QueueActivityEvent

Lightweight queue activity event record for inspection.

Fields include:

- `event_id`
- `queue_id`
- `event_type`
- `occurred_at`
- optional `session_id`, `item_id`, and `detail`

## Design choices

- Core model does not encode SAP-specific or domain-specific payload structure.
- State is explicit and inspectable at both queue and item level.
- Retry metadata is stored on items for clear auditability.
- Scope metadata is opaque application metadata and does not alter dispatch semantics.
