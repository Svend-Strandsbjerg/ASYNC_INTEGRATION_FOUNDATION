# Retry and Dead-Letter Semantics

## Retry waiting

On failure, items first enter `FAILED`.

If retry is allowed and attempts remain:

- transition to `RETRY_WAITING`
- set `next_retry_at`

A retry preparation step promotes `RETRY_WAITING -> READY` when retry conditions are met.

## Dead letter

If retry is not allowed or attempts are exhausted:

- transition `FAILED -> DEAD_LETTER`

`DEAD_LETTER` is terminal for automatic processing:

- no auto-dispatch
- no auto-retry
- item remains inspectable and associated with the queue

Future manual replay/recovery flows can be added explicitly without changing this baseline behavior.
