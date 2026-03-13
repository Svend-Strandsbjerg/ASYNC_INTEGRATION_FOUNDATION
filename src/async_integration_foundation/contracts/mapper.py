from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PayloadMapper(ABC):
    @abstractmethod
    def map_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class IdentityPayloadMapper(PayloadMapper):
    def map_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload
