from __future__ import annotations

from abc import ABC, abstractmethod

from async_integration_foundation.domain.models import QueueItem


class RetryPolicy(ABC):
    @abstractmethod
    def can_retry(self, item: QueueItem) -> bool:
        raise NotImplementedError


class MaxAttemptsRetryPolicy(RetryPolicy):
    def can_retry(self, item: QueueItem) -> bool:
        return item.attempt_count < item.max_attempts
