from __future__ import annotations

import uuid

from tools.data_loader import load_json_data


def book_flight(origin: str, destination: str, departure_date: str, traveler_name: str) -> dict:
    route_key = f"{origin[:3].upper()}-{destination[:3].upper()}"
    flight_records = load_json_data("flights.json")
    selected_flight = next((record for record in flight_records if record.get("route") == route_key), None)

    return {
        "booking_id": f"FL-{uuid.uuid4().hex[:8].upper()}",
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "traveler_name": traveler_name,
        "status": "confirmed",
        "provider": "Azure-Travel-Mock",
        "flight": selected_flight
        or {
            "route": route_key,
            "airline": "Azure Air",
            "flight_number": "AZ000",
            "departure_time": "10:00",
            "arrival_time": "12:30",
            "duration": "2h 30m",
            "price_usd": 199,
        },
    }
