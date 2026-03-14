from __future__ import annotations

from abc import ABC, abstractmethod

from async_integration_foundation.domain.models import QueueActivityEvent, QueueActivityType


class QueueActivityLog(ABC):
    @abstractmethod
    def record(
        self,
        queue_id: str,
        event_type: QueueActivityType,
        session_id: str | None = None,
        item_id: str | None = None,
        detail: str | None = None,
    ) -> QueueActivityEvent:
        raise NotImplementedError

    @abstractmethod
    def list_for_queue(self, queue_id: str) -> list[QueueActivityEvent]:
        raise NotImplementedError

    @abstractmethod
    def list_for_session(self, session_id: str) -> list[QueueActivityEvent]:
        raise NotImplementedError
