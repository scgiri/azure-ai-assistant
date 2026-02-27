from __future__ import annotations

from typing import Any, Callable

from tools.crm_service import retrieve_crm_record
from tools.flight_service import book_flight
from tools.realtime_service import execute_realtime_action
from tools.weather_service import check_weather


ToolFunction = Callable[..., dict[str, Any]]


TOOL_REGISTRY: dict[str, ToolFunction] = {
    "book_flight": book_flight,
    "check_weather": check_weather,
    "retrieve_crm_record": retrieve_crm_record,
    "execute_realtime_action": execute_realtime_action,
}
