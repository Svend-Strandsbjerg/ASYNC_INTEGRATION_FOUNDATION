# State Model

## Queue states

The framework models queue-level orchestration state explicitly.

- `OPEN`: queue accepts new items.
- `PAUSED`: queue is temporarily blocked from dispatch.
- `READY`: queue is committed and ready for dispatch.
- `DISPATCHING`: queue is actively dispatching items.
- `COMPLETED`: all items dispatched successfully.
- `FAILED`: all items failed or queue-level failure.
- `PARTIAL_FAILED`: mixed success/failure result.
- `CANCELLED`: queue terminated intentionally.

## Queue item states

Each item has independent dispatch state.

- `NEW`: item created but not staged.
- `STAGED`: item staged for manual commit flow.
- `READY`: item eligible for dispatch.
- `SENDING`: item currently being sent.
- `SENT`: item successfully sent.
- `FAILED`: item failed with no retry path.
- `RETRY_WAITING`: item failed but retry remains possible.
- `CANCELLED`: item cancelled.

## Transition constraints

- Paused queues must not transition to `DISPATCHING` until unpaused.
- Items in `SENT` are immutable for dispatch operations.
- Retry transitions from `FAILED` require explicit reset logic.
- Queue terminal states (`COMPLETED`, `FAILED`, `CANCELLED`) are inspectable and should not silently reopen.
