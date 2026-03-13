from __future__ import annotations

from abc import ABC, abstractmethod

from async_integration_foundation.domain.models import Queue


class Dispatcher(ABC):
    @abstractmethod
    def dispatch_queue(self, queue_id: str) -> Queue:
        raise NotImplementedError

    @abstractmethod
    def dispatch_item(self, queue_id: str, item_id: str) -> Queue:
        raise NotImplementedError

    @abstractmethod
    def retry_failed_items(self, queue_id: str) -> Queue:
        raise NotImplementedError
