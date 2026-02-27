# Beginner Learning Guide: Azure Action Assistant

This guide explains how the project works end-to-end in simple steps.

## 1) Why function calling?

If you only prompt for JSON, the model can still drift. Function calling gives you:
- Controlled action list (book flight, weather, CRM, real-time)
- Structured inputs (JSON schema for every tool)
- Safer execution path (your Python code runs the action)

## 2) Key files and what they do

- `main.py`  
  Entry point. Reads prompt + credentials, runs assistant, prints JSON.

- `config/settings.py`  
  Loads Azure endpoint/key/deployment from params or `.env`.

- `assistant/tool_schemas.py`  
  Defines system rules + tool schema metadata sent to model.

- `assistant/orchestrator.py`  
  Core loop:
  1. Send user request to model
  2. Model requests tool call
  3. Python executes tool
  4. Tool result goes back to model
  5. Final JSON response returned

- `assistant/tool_registry.py`  
  Maps tool names to Python functions.

- `tools/*.py`  
  Business actions (currently mock implementations).

## 3) Request lifecycle

1. User sends: "Book flight ..."
2. Model decides to call `book_flight`
3. Python executes `tools/flight_service.py`
4. Tool output is captured as structured data
5. Assistant returns final JSON payload with action status

## 4) How to replace mocks with real services

Example upgrades:
- `book_flight` → call your travel API
- `check_weather` → call weather provider API
- `retrieve_crm_record` → call Dynamics/Salesforce/internal CRM
- `execute_realtime_action` → call your workflow/event platform

Keep each function returning JSON-serializable dictionaries.

## 5) Security basics

- Store secrets in `.env` / Key Vault (recommended in production).
- Never hardcode API keys.
- Validate tool arguments before calling external systems.

## 6) Suggested next learning steps

1. Add argument validation with Pydantic
2. Use included FastAPI endpoint (`api.py`) for backend integration
3. Add unit tests for each tool
4. Add real service adapters behind interfaces

## 7) API mode (already included)

- Start server: `uvicorn api:app --reload`
- Health check: `GET /health`
- Main action endpoint: `POST /assist`

Minimal request body:

```json
{
  "prompt": "Book a flight from Hyderabad to Singapore on 2026-03-12 for Ravi Kumar"
}
```

You can also pass `endpoint`, `api_key`, `deployment`, and `api_version` per request.
