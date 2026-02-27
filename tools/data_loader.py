from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_data(file_name: str) -> list[dict[str, Any]]:
    project_root = Path(__file__).resolve().parent.parent
    data_file = project_root / "data" / file_name
    if not data_file.exists():
        return []

    with data_file.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if isinstance(payload, list):
        return payload
    return []
