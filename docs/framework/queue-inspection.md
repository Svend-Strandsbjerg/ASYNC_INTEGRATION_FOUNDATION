# Queue Inspection Model

## Purpose

Inspection APIs expose lifecycle status without coupling consumers to mutation logic.

## Queue snapshot fields

`build_queue_snapshot(queue)` includes:

- queue identifiers/scope metadata
- queue state and dispatch mode
- `is_paused`
- state counters:
  - `total_items`
  - `new_items`
  - `ready_items`
  - `dispatching_items`
  - `sent_items`
  - `failed_items`
  - `retry_waiting_items`
  - `dead_letter_items`
- state flags:
  - `has_retry_waiting_items`
  - `has_dead_letter_items`
- per-item snapshots including `next_retry_at`
- `last_updated_at`

## Activity log

`QueueActivityLog` is observational (does not drive behavior) and records key queue lifecycle events for queue/session inspection.
