from __future__ import annotations

import uuid

from tools.data_loader import load_json_data


def execute_realtime_action(action_name: str, payload: dict) -> dict:
    templates = load_json_data("realtime_actions.json")
    match = next(
        (
            record
            for record in templates
            if record.get("action_name", "").lower() == action_name.lower()
        ),
        None,
    )

    return {
        "operation_id": f"OP-{uuid.uuid4().hex[:10].upper()}",
        "action_name": action_name,
        "payload": payload,
        "status": (match or {}).get("default_status", "executed"),
        "target_system": (match or {}).get("target_system", "Azure-Realtime-Mock"),
        "expected_latency_ms": (match or {}).get("expected_latency_ms", 200),
        "executor": "Azure-Realtime-Mock",
    }
