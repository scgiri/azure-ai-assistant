from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path


CITIES = [
    "Hyderabad",
    "Singapore",
    "Seattle",
    "San Francisco",
    "London",
    "Dubai",
    "Bengaluru",
    "Sydney",
]

AIRLINES = ["Azure Air", "Contoso Sky", "Fabrikam Jet", "Northwind Air"]
CUSTOMER_NAMES = [
    "Contoso Holdings",
    "Fabrikam Retail",
    "Northwind Logistics",
    "Adventure Works",
    "Tailspin Toys",
    "Litware Solutions",
]
REGIONS = ["APAC", "NA", "EMEA", "LATAM"]
TIERS = ["silver", "gold", "platinum"]
ACTION_TEMPLATES = [
    ("send_alert", "Azure Event Grid"),
    ("create_incident", "Azure Monitor"),
    ("update_inventory", "Azure Service Bus"),
    ("sync_customer", "Azure Functions"),
]


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _route_code(origin: str, destination: str) -> str:
    return f"{origin[:3].upper()}-{destination[:3].upper()}"


def generate_flights(size: int) -> list[dict]:
    records: list[dict] = []
    for _ in range(size):
        origin, destination = random.sample(CITIES, 2)
        departure_hour = random.randint(0, 23)
        departure_minute = random.choice([0, 10, 15, 20, 30, 40, 45, 50])
        duration_hours = random.randint(1, 11)
        duration_minutes = random.choice([0, 10, 15, 20, 30, 40, 45, 50])

        arrival_hour = (departure_hour + duration_hours) % 24
        arrival_minute = (departure_minute + duration_minutes) % 60

        records.append(
            {
                "route": _route_code(origin, destination),
                "airline": random.choice(AIRLINES),
                "flight_number": f"AZ{random.randint(100, 999)}",
                "departure_time": f"{departure_hour:02d}:{departure_minute:02d}",
                "arrival_time": f"{arrival_hour:02d}:{arrival_minute:02d}",
                "duration": f"{duration_hours}h {duration_minutes}m",
                "price_usd": random.randint(120, 980),
            }
        )

    return records


def generate_weather(size: int) -> list[dict]:
    today = date.today()
    summaries = ["Sunny", "Partly cloudy", "Light rain", "Thunderstorms", "Overcast"]

    records: list[dict] = []
    for _ in range(size):
        day_offset = random.randint(0, 30)
        weather_date = today + timedelta(days=day_offset)
        records.append(
            {
                "city": random.choice(CITIES),
                "date": weather_date.isoformat(),
                "summary": random.choice(summaries),
                "temperature_c": random.randint(8, 39),
                "wind_kph": random.randint(4, 38),
                "humidity": random.randint(22, 92),
            }
        )

    return records


def generate_crm_records(size: int) -> list[dict]:
    records: list[dict] = []
    for index in range(1, size + 1):
        records.append(
            {
                "customer_id": f"CUST-{1000 + index}",
                "name": random.choice(CUSTOMER_NAMES),
                "tier": random.choice(TIERS),
                "region": random.choice(REGIONS),
                "last_contact": (date.today() - timedelta(days=random.randint(1, 60))).isoformat(),
                "open_opportunities": random.randint(0, 9),
                "account_manager": random.choice(
                    [
                        "Riya Sharma",
                        "Daniel Reed",
                        "Ananya Patel",
                        "Priya Nair",
                        "Jacob Thomas",
                    ]
                ),
            }
        )

    return records


def generate_realtime_actions(size: int) -> list[dict]:
    records: list[dict] = []
    for _ in range(size):
        action_name, target_system = random.choice(ACTION_TEMPLATES)
        records.append(
            {
                "action_name": action_name,
                "default_status": "executed",
                "target_system": target_system,
                "expected_latency_ms": random.randint(80, 420),
            }
        )

    return records


def write_json(path: Path, payload: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate dummy data for Azure Action Assistant")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic output")
    parser.add_argument("--flights", type=int, default=30, help="Number of flight records")
    parser.add_argument("--weather", type=int, default=30, help="Number of weather records")
    parser.add_argument("--crm", type=int, default=20, help="Number of CRM records")
    parser.add_argument("--realtime", type=int, default=20, help="Number of real-time action templates")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)

    data_dir = _project_root() / "data"

    flights = generate_flights(args.flights)
    weather = generate_weather(args.weather)
    crm_records = generate_crm_records(args.crm)
    realtime_actions = generate_realtime_actions(args.realtime)

    write_json(data_dir / "flights.json", flights)
    write_json(data_dir / "weather.json", weather)
    write_json(data_dir / "crm_records.json", crm_records)
    write_json(data_dir / "realtime_actions.json", realtime_actions)

    print("Dummy data generated successfully.")
    print(f"flights.json: {len(flights)}")
    print(f"weather.json: {len(weather)}")
    print(f"crm_records.json: {len(crm_records)}")
    print(f"realtime_actions.json: {len(realtime_actions)}")


if __name__ == "__main__":
    main()
