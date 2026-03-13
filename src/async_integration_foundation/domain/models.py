from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class DispatchMode(str, Enum):
    MANUAL_COMMIT = "MANUAL_COMMIT"
    IMMEDIATE = "IMMEDIATE"
    BATCH = "BATCH"
    SINGLE_ITEM = "SINGLE_ITEM"
    ORDERED = "ORDERED"


class QueueState(str, Enum):
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    READY = "READY"
    DISPATCHING = "DISPATCHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL_FAILED = "PARTIAL_FAILED"
    CANCELLED = "CANCELLED"


class QueueItemState(str, Enum):
    NEW = "NEW"
    STAGED = "STAGED"
    READY = "READY"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRY_WAITING = "RETRY_WAITING"
    CANCELLED = "CANCELLED"


@dataclass
class QueueItem:
    id: str
    queue_id: str
    payload: dict[str, Any]
    mapped_payload: dict[str, Any] | None = None
    state: QueueItemState = QueueItemState.NEW
    attempt_count: int = 0
    max_attempts: int = 3
    last_error: str | None = None


@dataclass
class Queue:
    id: str
    name: str
    dispatch_mode: DispatchMode = DispatchMode.MANUAL_COMMIT
    state: QueueState = QueueState.OPEN
    items: list[QueueItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DispatchResult:
    success: bool
    retryable: bool = False
    external_reference: str | None = None
    error_message: str | None = None
