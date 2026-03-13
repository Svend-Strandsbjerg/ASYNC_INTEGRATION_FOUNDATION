# Example: Swimlane Immediate Dispatch

## Scenario

A card move in a swimlane board should dispatch immediately to an outbound integration endpoint.

## Reference flow

1. Create queue configured for immediate dispatch.
2. Append item as `READY`.
3. Trigger single-item dispatch through dispatcher.
4. Track success/failure status per item.
5. Retry retryable failures if needed.

## Why this matters

This validates immediate dispatch behavior while preserving reusable queue and adapter abstractions.
