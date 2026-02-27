# Azure Action Assistant (Python)

An Azure-centric AI assistant that uses **Azure OpenAI function calling (tools)** to:
- Book flights
- Check weather
- Retrieve CRM data
- Execute real-time actions

It returns **structured JSON** for backend systems and avoids free-form action responses.

## Best approach for your scenario

For your multiple business actions + strict JSON requirement, the best option is:

**B. Use Azure OpenAI function calling (tools) capability.**

Why:
- It gives the model a controlled way to call specific backend actions.
- You validate/execute each action in code.
- You can enforce deterministic JSON output contracts.

## Project structure

```text
azure-ai-assistant/
├─ assistant/
│  ├─ __init__.py
│  ├─ client.py
│  ├─ models.py
│  ├─ orchestrator.py
│  ├─ tool_registry.py
│  └─ tool_schemas.py
├─ config/
│  ├─ __init__.py
│  └─ settings.py
├─ tools/
│  ├─ __init__.py
│  ├─ crm_service.py
│  ├─ flight_service.py
│  ├─ realtime_service.py
│  └─ weather_service.py
├─ docs/
│  ├─ ARCHITECTURE.md
│  └─ LEARNING_GUIDE.md
├─ .env.example
├─ main.py
└─ requirements.txt
```

## Prerequisites

- Python 3.10+
- Azure OpenAI resource
- A deployed chat model in Azure OpenAI (example: `gpt-4o`)

## Setup

1) Create virtual environment and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION` (default `2024-02-01`)

## Run

### Option A: Use `.env`

```powershell
python main.py --prompt "Book a flight from Hyderabad to Singapore on 2026-03-12 for Ravi Kumar"
```

### Option B: Pass endpoint/key/deployment directly (as requested)

```powershell
python main.py \
  --prompt "Check weather in Seattle on 2026-03-01" \
  --endpoint "https://<your-resource>.openai.azure.com/" \
  --api-key "<your-api-key>" \
  --deployment "gpt-4o"
```

## Run as API (FastAPI)

Start server:

```powershell
uvicorn api:app --reload
```

Call API:

```powershell
curl -X POST "http://127.0.0.1:8000/assist" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Retrieve CRM data for customer CUST-1001"
  }'
```

Open interactive docs:
- http://127.0.0.1:8000/docs

## Run with Docker (production-style)

Build image:

```powershell
docker build -t azure-action-assistant:latest .
```

Run container:

```powershell
docker run --rm -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com/" \
  -e AZURE_OPENAI_API_KEY="<your-api-key>" \
  -e AZURE_OPENAI_DEPLOYMENT="gpt-4o" \
  -e AZURE_OPENAI_API_VERSION="2024-02-01" \
  azure-action-assistant:latest
```

Then open:
- http://127.0.0.1:8000/docs

## GitHub Actions CI

This repo includes workflow: `.github/workflows/ci.yml`.

It runs on pushes and pull requests and performs:
- dependency installation
- Python syntax validation
- import smoke tests
- dummy data generation smoke test

## GitHub Actions CD (Azure Container Apps)

This repo includes CD workflow: `.github/workflows/cd-aca.yml`.

It deploys your app to Azure Container Apps by:
- logging into Azure with OIDC (`azure/login`)
- building container image from `Dockerfile`
- pushing image to Azure Container Registry
- deploying latest image to your Azure Container App

Required GitHub Secrets:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `ACR_LOGIN_SERVER`
- `ACR_USERNAME`
- `ACR_PASSWORD`
- `RESOURCE_GROUP`
- `CONTAINER_APP_NAME`
- `CONTAINERAPPS_ENVIRONMENT`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

Full setup guide:
- `docs/DEPLOY_AZURE_CONTAINER_APPS.md`

## Example output (structured JSON)

```json
{
  "response_type": "action_result",
  "request_id": "9d5f8d7e-78f7-45ba-9be1-c88c9f8bf6a9",
  "actions": [
    {
      "tool": "check_weather",
      "status": "success",
      "data": {
        "city": "Seattle",
        "date": "2026-03-01",
        "summary": "Partly cloudy",
        "temperature_c": 24,
        "wind_kph": 13,
        "provider": "Azure-Weather-Mock"
      },
      "timestamp_utc": "2026-02-26T10:21:55.123456+00:00"
    }
  ]
}
```

## Included dummy data (for learning/demo)

The project includes JSON datasets in `data/` used by tools:

- `data/flights.json` routes: `HYD-SIN`, `SEA-SFO`, `LHR-DXB`
- `data/weather.json` examples: Seattle (`2026-03-01`), Singapore (`2026-03-12`), Hyderabad (`2026-03-12`)
- `data/crm_records.json` customer IDs: `CUST-1001`, `CUST-1002`, `CUST-1003`
- `data/realtime_actions.json` actions: `send_alert`, `create_incident`, `update_inventory`

Try prompts like:
- "Retrieve CRM data for customer CUST-1002"
- "Book a flight from Hyderabad to Singapore on 2026-03-12 for Ravi Kumar"
- "Execute realtime action send_alert with payload severity high and service payments"

### Regenerate larger dummy datasets

You can regenerate all dummy files using:

```powershell
python scripts/generate_dummy_data.py
```

Custom sizes:

```powershell
python scripts/generate_dummy_data.py --flights 100 --weather 120 --crm 80 --realtime 60 --seed 7
```

## Important notes

- Tool implementations are mocked for learning; replace with real APIs/services.
- Do not commit `.env` or secrets.
- Keep strict JSON contract for backend reliability.

## Learning docs

- Beginner walkthrough: `docs/LEARNING_GUIDE.md`
- Architecture and diagram: `docs/ARCHITECTURE.md`
- Deployment guide: `docs/DEPLOY_AZURE_CONTAINER_APPS.md`

