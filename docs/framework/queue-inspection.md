# Queue Inspection Model

## Purpose

The framework now includes additive, lightweight inspection capabilities so consuming applications can discover and inspect queues without coupling to internal mutation logic.

## Queue scoping metadata

`Queue` supports optional application-level scope metadata:

- `session_id`
- `user_id`
- `context_type`
- `context_id`
- `metadata` (opaque key/value payload)

This metadata is used only for queue identification and lookup. It does not change dispatch eligibility, retry behavior, or lifecycle transitions.

## Scoped queue resolution

`QueueRepository` now supports:

- `get_queue(queue_id)`
- `get_queue_by_scope(session_id, context_type, context_id)`
- `list_queues_by_session(session_id)`
- `list_queues_by_context(session_id, context_type)`

The in-memory implementation supports all lookups directly.

## Queue resolution helper

`QueueResolver` provides framework-level `get_or_create_queue(...)` support:

- resolve an existing queue by `(session_id, context_type, context_id)`
- create a queue when no existing scoped queue is found

Additional helper operations:

- `add_item(queue_id, item)`
- `pause_queue(queue_id)`
- `resume_queue(queue_id)`

These helpers are additive and keep lifecycle/dispatch semantics unchanged.

## Queue snapshot read model

`build_queue_snapshot(queue)` converts a domain queue into a stable, read-friendly model.

Queue snapshot fields include:

- identifiers and scope metadata
- queue state and dispatch mode
- `is_paused`
- item counters (`total_items`, `waiting_items`, `ready_items`, `sending_items`, `sent_items`, `failed_items`)
- item snapshots with attempt/error/timestamp details
- `last_updated_at`

## Lightweight queue activity log

`QueueActivityLog` and `InMemoryQueueActivityLog` provide append-only, inspectable queue activity events.

Events include:

- `queue_created`
- `queue_paused`
- `queue_resumed`
- `item_added`
- `dispatch_started`
- `item_sent`
- `dispatch_completed`
- `dispatch_failed`

Query support:

- `list_for_queue(queue_id)`
- `list_for_session(session_id)`

The activity log is observational only and does not drive queue behavior.
