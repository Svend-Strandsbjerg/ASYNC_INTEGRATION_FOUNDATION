# Queue Model

## Overview

The queue model defines enterprise-oriented queue/message entities for generic async integration.

## Queue

`Queue` is the lifecycle container.

Primary technical identity:

- `queue_id` (stable unique technical identifier)

Key fields:

- `queue_type`
- `queue_state`
- `dispatch_mode`
- `session_id`, `user_id`
- `context_type`, `context_id`
- `correlation_id`
- `business_key`, `external_reference`
- `created_at`, `updated_at`, `created_by`
- `metadata`
- `is_paused` (derived from state)

## QueueItem

`QueueItem` is a dispatchable unit linked to a queue.

Primary technical identity:

- `item_id` (stable unique technical identifier)

Explicit queue linkage:

- `queue_id` (required relationship to parent queue)

Key fields:

- `item_type`, `item_state`
- `sequence_number` (deterministic ordering)
- `payload`, `payload_type`, `payload_version`
- `adapter_key`, `target_system`, `operation`
- `correlation_id`, `causation_id`, `request_id`
- `business_key`, `external_reference`
- `idempotency_key`
- `attempt_count`, `last_attempt_at`, `last_error`
- `created_at`, `updated_at`
- `metadata`

## Separation of concerns

- `queue_id` / `item_id`: technical identity
- `business_key` / `external_reference`: domain references
- `correlation_id` (and related ids): traceability
- `idempotency_key`: replay/retry safety
- `payload*`: generic message contract
- adapter fields: routing/mapping hints
