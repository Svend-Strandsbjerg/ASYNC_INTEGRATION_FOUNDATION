# Example: Timesheet Staging and Commit

## Scenario

Timesheet entries are staged during user editing and committed in a controlled batch.

## Reference flow

1. Create a queue for a timesheet session.
2. Append entries as `STAGED` items.
3. Pause queue if review/validation is needed.
4. Unpause and commit queue to mark staged items as `READY`.
5. Dispatch queue in batch mode.
6. Inspect item-level status and retry retryable failures.

## Why this matters

This pattern proves staged commit behavior without embedding timesheet business logic into the framework core.
