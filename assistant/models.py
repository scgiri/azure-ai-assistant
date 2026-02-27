from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ActionResult:
    tool: str
    status: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp_utc: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "status": self.status,
            "data": self.data,
            "timestamp_utc": self.timestamp_utc,
        }


@dataclass
class AssistantResponse:
    response_type: str
    request_id: str
    actions: list[ActionResult] = field(default_factory=list)
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "response_type": self.response_type,
            "request_id": self.request_id,
        }
        if self.actions:
            payload["actions"] = [result.to_dict() for result in self.actions]
        if self.message:
            payload["message"] = self.message
        return payload
