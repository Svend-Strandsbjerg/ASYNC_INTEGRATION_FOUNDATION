from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid4())


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
    item_id: str = field(default_factory=_new_id)
    queue_id: str = ""
    item_type: str | None = None
    item_state: QueueItemState = QueueItemState.NEW
    sequence_number: int | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    payload_type: str | None = None
    payload_version: str | None = None
    adapter_key: str | None = None
    target_system: str | None = None
    operation: str | None = None
    correlation_id: str | None = None
    causation_id: str | None = None
    request_id: str | None = None
    business_key: str | None = None
    external_reference: str | None = None
    idempotency_key: str | None = None
    mapped_payload: dict[str, Any] | None = None
    attempt_count: int = 0
    max_attempts: int = 3
    last_error: str | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    last_attempt_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.payload = dict(self.payload)
        self.metadata = dict(self.metadata)

    @property
    def id(self) -> str:
        return self.item_id

    @property
    def state(self) -> QueueItemState:
        return self.item_state

    @state.setter
    def state(self, value: QueueItemState) -> None:
        self.item_state = value


@dataclass
class Queue:
    queue_id: str = field(default_factory=_new_id)
    queue_type: str = "default"
    queue_state: QueueState = QueueState.OPEN
    dispatch_mode: DispatchMode = DispatchMode.MANUAL_COMMIT
    items: list[QueueItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    session_id: str | None = None
    user_id: str | None = None
    context_type: str | None = None
    context_id: str | None = None
    correlation_id: str | None = None
    business_key: str | None = None
    external_reference: str | None = None
    created_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.metadata = dict(self.metadata)

    @property
    def id(self) -> str:
        return self.queue_id

    @property
    def name(self) -> str:
        return self.queue_type

    @property
    def state(self) -> QueueState:
        return self.queue_state

    @state.setter
    def state(self, value: QueueState) -> None:
        self.queue_state = value

    @property
    def is_paused(self) -> bool:
        return self.queue_state == QueueState.PAUSED


@dataclass
class DispatchResult:
    success: bool
    retryable: bool = False
    external_reference: str | None = None
    error_message: str | None = None


@dataclass
class QueueItemSnapshot:
    item_id: str
    queue_id: str
    sequence_number: int | None
    item_type: str | None
    payload_type: str | None
    payload_version: str | None
    adapter_key: str | None
    target_system: str | None
    operation: str | None
    correlation_id: str | None
    business_key: str | None
    external_reference: str | None
    idempotency_key: str | None
    display_name: str
    state: str
    attempt_count: int
    created_at: datetime
    last_attempt_at: datetime | None
    last_error: str | None
    metadata: dict[str, Any]


@dataclass
class QueueSnapshot:
    queue_id: str
    queue_type: str
    session_id: str | None
    user_id: str | None
    context_type: str | None
    context_id: str | None
    correlation_id: str | None
    business_key: str | None
    external_reference: str | None
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
    metadata: dict[str, Any]
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
