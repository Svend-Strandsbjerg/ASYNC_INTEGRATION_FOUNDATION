from __future__ import annotations

from async_integration_foundation.contracts.transport import TransportAdapter
from async_integration_foundation.domain.models import DispatchResult


class MockTransportAdapter(TransportAdapter):
    def __init__(self, fail_payload_keys: set[str] | None = None, retryable: bool = True) -> None:
        self.fail_payload_keys = fail_payload_keys or set()
        self.retryable = retryable
        self.sent_payloads: list[dict] = []

    def send(self, payload: dict) -> DispatchResult:
        self.sent_payloads.append(payload)
        key = str(payload.get("id", ""))
        if key in self.fail_payload_keys:
            return DispatchResult(
                success=False,
                retryable=self.retryable,
                error_message=f"Mock failure for payload id '{key}'",
            )
        return DispatchResult(success=True, external_reference=f"mock-ref-{key or 'ok'}")
