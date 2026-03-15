from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
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
    DISPATCHING = "DISPATCHING"
    COMPLETED = "COMPLETED"


class QueueItemState(str, Enum):
    NEW = "NEW"
    READY = "READY"
    DISPATCHING = "DISPATCHING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRY_WAITING = "RETRY_WAITING"
    DEAD_LETTER = "DEAD_LETTER"


QueueOperation = Literal["create", "update", "delete"]


@dataclass(frozen=True)
class QueueScheduling:
    day_key: str
    start_time: str
    end_time: str
    interval: str


class QueueActivityType(str, Enum):
    QUEUE_CREATED = "queue_created"
    QUEUE_PAUSED = "queue_paused"
    QUEUE_RESUMED = "queue_resumed"
    ITEM_ADDED = "item_added"
    DISPATCH_STARTED = "dispatch_started"
    ITEM_SENT = "item_sent"
    DISPATCH_COMPLETED = "dispatch_completed"
    DISPATCH_FAILED = "dispatch_failed"


@dataclass(init=False)
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
    retry_policy_key: str | None = None
    next_retry_at: datetime | None = None
    last_error: str | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    last_attempt_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    scheduling: QueueScheduling | None = None

    def __init__(
        self,
        item_id: str | None = None,
        queue_id: str = "",
        item_type: str | None = None,
        item_state: QueueItemState = QueueItemState.NEW,
        sequence_number: int | None = None,
        payload: dict[str, Any] | None = None,
        payload_type: str | None = None,
        payload_version: str | None = None,
        adapter_key: str | None = None,
        target_system: str | None = None,
        operation: str | None = None,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        request_id: str | None = None,
        business_key: str | None = None,
        external_reference: str | None = None,
        idempotency_key: str | None = None,
        mapped_payload: dict[str, Any] | None = None,
        attempt_count: int = 0,
        max_attempts: int = 3,
        retry_policy_key: str | None = None,
        next_retry_at: datetime | None = None,
        last_error: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        last_attempt_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        scheduling: QueueScheduling | None = None,
        id: str | None = None,
        state: QueueItemState | None = None,
    ) -> None:
        self.item_id = item_id or id or _new_id()
        self.queue_id = queue_id
        self.item_type = item_type
        self.item_state = state or item_state
        self.sequence_number = sequence_number
        self.payload = dict(payload or {})
        self.payload_type = payload_type
        self.payload_version = payload_version
        self.adapter_key = adapter_key
        self.target_system = target_system
        self.operation = operation
        self.correlation_id = correlation_id
        self.causation_id = causation_id
        self.request_id = request_id
        self.business_key = business_key
        self.external_reference = external_reference
        self.idempotency_key = idempotency_key
        self.mapped_payload = dict(mapped_payload) if mapped_payload is not None else None
        self.attempt_count = attempt_count
        self.max_attempts = max_attempts
        self.retry_policy_key = retry_policy_key
        self.next_retry_at = next_retry_at
        self.last_error = last_error
        self.created_at = created_at or _utcnow()
        self.updated_at = updated_at or _utcnow()
        self.last_attempt_at = last_attempt_at
        self.metadata = dict(metadata or {})
        self.scheduling = scheduling

    @property
    def id(self) -> str:
        return self.item_id

    @property
    def state(self) -> QueueItemState:
        return self.item_state

    @state.setter
    def state(self, value: QueueItemState) -> None:
        self.item_state = value


@dataclass(init=False)
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
    pre_pause_state: QueueState = QueueState.OPEN

    def __init__(
        self,
        queue_id: str | None = None,
        queue_type: str = "default",
        queue_state: QueueState = QueueState.OPEN,
        dispatch_mode: DispatchMode = DispatchMode.MANUAL_COMMIT,
        items: list[QueueItem] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        context_type: str | None = None,
        context_id: str | None = None,
        correlation_id: str | None = None,
        business_key: str | None = None,
        external_reference: str | None = None,
        created_by: str | None = None,
        metadata: dict[str, Any] | None = None,
        pre_pause_state: QueueState = QueueState.OPEN,
        id: str | None = None,
        name: str | None = None,
        state: QueueState | None = None,
        status: QueueState | None = None,
    ) -> None:
        self.queue_id = queue_id or id or _new_id()
        self.queue_type = name or queue_type
        self.queue_state = status or state or queue_state
        self.dispatch_mode = dispatch_mode
        self.items = list(items or [])
        self.created_at = created_at or _utcnow()
        self.updated_at = updated_at or _utcnow()
        self.session_id = session_id
        self.user_id = user_id
        self.context_type = context_type
        self.context_id = context_id
        self.correlation_id = correlation_id
        self.business_key = business_key
        self.external_reference = external_reference
        self.created_by = created_by
        self.metadata = dict(metadata or {})
        self.pre_pause_state = pre_pause_state

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
    def status(self) -> QueueState:
        return self.queue_state

    @status.setter
    def status(self, value: QueueState) -> None:
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
    next_retry_at: datetime | None
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
    new_items: int
    ready_items: int
    dispatching_items: int
    sent_items: int
    failed_items: int
    retry_waiting_items: int
    dead_letter_items: int
    has_retry_waiting_items: bool
    has_dead_letter_items: bool
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
