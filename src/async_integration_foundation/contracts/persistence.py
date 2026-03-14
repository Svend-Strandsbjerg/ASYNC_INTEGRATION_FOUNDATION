from __future__ import annotations

from abc import ABC, abstractmethod

from async_integration_foundation.domain.models import Queue


class QueueRepository(ABC):
    @abstractmethod
    def create_queue(self, queue: Queue) -> Queue:
        raise NotImplementedError

    @abstractmethod
    def get_queue(self, queue_id: str) -> Queue | None:
        raise NotImplementedError

    @abstractmethod
    def get_queue_by_scope(self, session_id: str, context_type: str, context_id: str) -> Queue | None:
        raise NotImplementedError

    @abstractmethod
    def save_queue(self, queue: Queue) -> Queue:
        raise NotImplementedError

    @abstractmethod
    def list_queues(self) -> list[Queue]:
        raise NotImplementedError

    @abstractmethod
    def list_queues_by_session(self, session_id: str) -> list[Queue]:
        raise NotImplementedError

    @abstractmethod
    def list_queues_by_context(self, session_id: str, context_type: str) -> list[Queue]:
        raise NotImplementedError
