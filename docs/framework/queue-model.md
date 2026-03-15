# Queue Model

## Queue

Queue fields include:

- `id`, `name`, `dispatch_mode`, `state`
- `items`
- `session_id`, `user_id`, `context_type`, `context_id`
- `metadata`
- `pre_pause_state` (supports pause/resume semantics)
- `created_at`, `updated_at`

## QueueItem

Queue item fields include:

- `id`, `queue_id`
- `payload`, `mapped_payload`
- `state`
- `sequence_number` (deterministic dispatch ordering)
- `attempt_count`, `max_attempts`
- `next_retry_at`, `retry_policy_key`
- `last_error`, `created_at`, `last_attempt_at`

## QueueSnapshot

Queue snapshots expose queue/item lifecycle visibility with explicit counters:

- `new_items`
- `ready_items`
- `dispatching_items`
- `sent_items`
- `failed_items`
- `retry_waiting_items`
- `dead_letter_items`
- `has_retry_waiting_items`
- `has_dead_letter_items`

This read model is intended for inspection/monitoring use cases.

## Runtime builder contract

For runtime integrations (such as planning POCs), use:

- `create_queue_id` / `createQueueId`
- `create_queue_item_id` / `createQueueItemId`
- `build_queue_item` / `buildQueueItem`

`build_queue_item` stores scheduling metadata in a canonical structure:

- `scheduling.day_key`
- `scheduling.start_time`
- `scheduling.end_time`
- `scheduling.interval`

Supported queue operations: `create | update | delete`.
