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


class QueueActivityType(str, Enum):
    QUEUE_CREATED = "queue_created"
    QUEUE_PAUSED = "queue_paused"
    QUEUE_RESUMED = "queue_resumed"
    ITEM_ADDED = "item_added"
    DISPATCH_STARTED = "dispatch_started"
    ITEM_SENT = "item_sent"
    DISPATCH_COMPLETED = "dispatch_completed"
    DISPATCH_FAILED = "dispatch_failed"


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
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_attempt_at: datetime | None = None


@dataclass
class Queue:
    id: str
    name: str
    dispatch_mode: DispatchMode = DispatchMode.MANUAL_COMMIT
    state: QueueState = QueueState.OPEN
    items: list[QueueItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str | None = None
    user_id: str | None = None
    context_type: str | None = None
    context_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_paused(self) -> bool:
        return self.state == QueueState.PAUSED


@dataclass
class DispatchResult:
    success: bool
    retryable: bool = False
    external_reference: str | None = None
    error_message: str | None = None


@dataclass
class QueueItemSnapshot:
    item_id: str
    display_name: str
    state: str
    attempt_count: int
    created_at: datetime
    last_attempt_at: datetime | None
    last_error: str | None


@dataclass
class QueueSnapshot:
    queue_id: str
    session_id: str | None
    user_id: str | None
    context_type: str | None
    context_id: str | None
    queue_state: str
    dispatch_mode: str
    is_paused: bool
    total_items: int
    waiting_items: int
    ready_items: int
    sending_items: int
    sent_items: int
    failed_items: int
    items: list[QueueItemSnapshot]
    last_updated_at: datetime


@dataclass
class QueueActivityEvent:
    event_id: str
    queue_id: str
    event_type: QueueActivityType
    occurred_at: datetime
    session_id: str | None = None
    item_id: str | None = None
    detail: str | None = None
