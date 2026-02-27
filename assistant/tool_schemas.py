SYSTEM_PROMPT = """
You are an Azure enterprise assistant.

Rules:
1) For any actionable user intent (book flight, weather lookup, CRM retrieval, real-time action), use tools.
2) Do not fabricate action results.
3) After tool calls are completed, return only strict JSON.
4) Final JSON must use this schema:
{
  "response_type": "action_result" | "message",
  "request_id": "string",
  "actions": [
    {
      "tool": "string",
      "status": "success" | "failed",
      "data": {"any": "json"},
      "timestamp_utc": "iso8601"
    }
  ],
  "message": "string optional"
}
5) Do not include markdown fences.
""".strip()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_flight",
            "description": "Book a flight for a traveler.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "departure_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "traveler_name": {"type": "string"},
                },
                "required": ["origin", "destination", "departure_date", "traveler_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_weather",
            "description": "Get weather for a city and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["city", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_crm_record",
            "description": "Fetch CRM customer account details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_realtime_action",
            "description": "Execute a real-time operation in an external system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_name": {"type": "string"},
                    "payload": {"type": "object"},
                },
                "required": ["action_name", "payload"],
            },
        },
    },
]
