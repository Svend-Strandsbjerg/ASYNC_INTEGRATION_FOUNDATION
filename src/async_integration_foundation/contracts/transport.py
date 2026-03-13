from __future__ import annotations

from abc import ABC, abstractmethod

from async_integration_foundation.domain.models import DispatchResult


class TransportAdapter(ABC):
    @abstractmethod
    def send(self, payload: dict) -> DispatchResult:
        raise NotImplementedError
