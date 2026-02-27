from __future__ import annotations

from tools.data_loader import load_json_data


def check_weather(city: str, date: str) -> dict:
    weather_records = load_json_data("weather.json")
    match = next(
        (
            record
            for record in weather_records
            if record.get("city", "").lower() == city.lower() and record.get("date") == date
        ),
        None,
    )

    if match:
        return {
            **match,
            "provider": "Azure-Weather-Mock",
        }

    return {
        "city": city,
        "date": date,
        "summary": "Partly cloudy",
        "temperature_c": 24,
        "wind_kph": 13,
        "humidity": 50,
        "provider": "Azure-Weather-Mock",
    }
