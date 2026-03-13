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
- `paused`: convenience flag derived from state
- `items`: queue item collection

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

### DispatchResult

Normalized result from a transport adapter.

Fields:

- `success`: boolean
- `retryable`: whether retry is allowed
- `external_reference`: optional target reference
- `error_message`: optional failure details

## Design choices

- Core model does not encode SAP-specific or domain-specific payload structure.
- State is explicit and inspectable at both queue and item level.
- Retry metadata is stored on items for clear auditability.
