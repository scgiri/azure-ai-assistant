# Azure Action Assistant (Python)

An Azure-centric AI assistant that uses **Azure OpenAI function calling (tools)** to:
- Book flights
- Check weather
- Retrieve CRM data
- Execute real-time actions

It returns **structured JSON** for backend systems and avoids free-form action responses.

## Why function calling?

For multiple business actions + strict JSON output, the best approach is **Azure OpenAI function calling (tools)**:
- The model calls specific backend actions in a controlled way
- You validate and execute each action in code
- You enforce deterministic JSON output contracts

## Project structure

```text
azure-ai-assistant/
├─ .github/workflows/
│  ├─ ci.yml              # CI: lint, test, build & push to ACR
│  └─ cd-aca.yml           # CD: deploy to Azure Container Apps
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
├─ data/
│  ├─ crm_records.json
│  ├─ flights.json
│  ├─ realtime_actions.json
│  └─ weather.json
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ DEPLOY_AZURE_CONTAINER_APPS.md
│  └─ LEARNING_GUIDE.md
├─ scripts/
│  └─ generate_dummy_data.py
├─ tools/
│  ├─ __init__.py
│  ├─ crm_service.py
│  ├─ data_loader.py
│  ├─ flight_service.py
│  ├─ realtime_service.py
│  └─ weather_service.py
├─ .env.example
├─ api.py
├─ Dockerfile
├─ main.py
└─ requirements.txt
```

## Prerequisites

- Python 3.10+
- Azure OpenAI resource with a deployed chat model (e.g. `gpt-4o`)
- (Optional) Docker, Azure CLI, Azure Container Registry for containerised deployment

## Setup

1) Create virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

2) Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set:
- `AZURE_OPENAI_ENDPOINT` — your Azure OpenAI resource URL
- `AZURE_OPENAI_API_KEY` — API key from the Azure portal
- `AZURE_OPENAI_DEPLOYMENT` — model deployment name (e.g. `gpt-4o`)
- `AZURE_OPENAI_API_VERSION` — API version (e.g. `2025-01-01-preview`)

## Run

### CLI (using `.env`)

```bash
python main.py --prompt "Book a flight from Hyderabad to Singapore on 2026-03-12 for Ravi Kumar"
```

### CLI (inline overrides)

```bash
python main.py \
  --prompt "Check weather in Seattle on 2026-03-01" \
  --endpoint "https://<your-resource>.openai.azure.com/" \
  --api-key "<your-api-key>" \
  --deployment "gpt-4o"
```

## Run as API (FastAPI)

Start server:

```bash
uvicorn api:app --reload
```

Call API:

```bash
curl -X POST "http://127.0.0.1:8000/assist" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Retrieve CRM data for customer CUST-1001"}'
```

Interactive docs: http://127.0.0.1:8000/docs

## Run with Docker

Build and run:

```bash
docker build -t azure-action-assistant:latest .

docker run --rm -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com/" \
  -e AZURE_OPENAI_API_KEY="<your-api-key>" \
  -e AZURE_OPENAI_DEPLOYMENT="gpt-4o" \
  -e AZURE_OPENAI_API_VERSION="2025-01-01-preview" \
  azure-action-assistant:latest
```

Then open: http://127.0.0.1:8000/docs

### Push to Azure Container Registry

```bash
az acr login --name aiassistantacr
ACR_SERVER=$(az acr show --name aiassistantacr --query loginServer -o tsv)

docker tag azure-action-assistant:latest $ACR_SERVER/azure-action-assistant:v1
docker push $ACR_SERVER/azure-action-assistant:v1
```

## CI/CD

### GitHub Actions CI (`.github/workflows/ci.yml`)

Runs on every push and pull request:
1. **build-and-validate** — installs dependencies, validates Python syntax, runs import smoke tests and dummy data generation
2. **push-to-acr** — (main branch only) authenticates to Azure via OIDC, builds the Docker image, and pushes it to Azure Container Registry with both a commit-SHA tag and `latest`

Required GitHub secrets for ACR push:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

### GitHub Actions CD (`.github/workflows/cd-aca.yml`)

Deploys to Azure Container Apps on pushes to `main` (or manual dispatch):
- Builds and pushes the container image to ACR
- Deploys the latest image to your Container App with environment variables injected

Required GitHub secrets:
- `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`
- `ACR_LOGIN_SERVER`, `ACR_USERNAME`, `ACR_PASSWORD`
- `RESOURCE_GROUP`, `CONTAINER_APP_NAME`, `CONTAINERAPPS_ENVIRONMENT`
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`

Full setup guide: `docs/DEPLOY_AZURE_CONTAINER_APPS.md`

## Example output (structured JSON)

```json
{
  "response_type": "action_result",
  "request_id": "da0b57d8-8599-448e-b964-9ce4d300613f",
  "actions": [
    {
      "tool": "book_flight",
      "status": "success",
      "data": {
        "booking_id": "FL-32D5AA4C",
        "origin": "Hyderabad",
        "destination": "Singapore",
        "departure_date": "2026-03-12",
        "traveler_name": "Ravi Kumar",
        "status": "confirmed",
        "provider": "Azure-Travel-Mock",
        "flight": {
          "route": "HYD-SIN",
          "airline": "Azure Air",
          "flight_number": "AZ101",
          "departure_time": "09:15",
          "arrival_time": "15:35",
          "duration": "6h 20m",
          "price_usd": 420
        }
      },
      "timestamp_utc": "2026-03-01T18:42:18.074160+00:00"
    }
  ],
  "message": "Your flight has been successfully booked."
}
```

## Included dummy data (for learning/demo)

JSON datasets in `data/` used by the mock tools:

| File | Examples |
|------|----------|
| `flights.json` | Routes: `HYD-SIN`, `SEA-SFO`, `LHR-DXB` |
| `weather.json` | Cities: Seattle, Singapore, Hyderabad |
| `crm_records.json` | IDs: `CUST-1001`, `CUST-1002`, `CUST-1003` |
| `realtime_actions.json` | Actions: `send_alert`, `create_incident`, `update_inventory` |

Try prompts like:
- `"Retrieve CRM data for customer CUST-1002"`
- `"Book a flight from Hyderabad to Singapore on 2026-03-12 for Ravi Kumar"`
- `"Execute realtime action send_alert with payload severity high and service payments"`

### Regenerate dummy datasets

```bash
python scripts/generate_dummy_data.py                          # defaults
python scripts/generate_dummy_data.py --flights 100 --weather 120 --crm 80 --realtime 60 --seed 7
```

## Important notes

- Tool implementations are mocked for learning; replace with real APIs/services in production.
- Do not commit `.env` or secrets.
- Keep strict JSON contract for backend reliability.

## Learning docs

- Beginner walkthrough: `docs/LEARNING_GUIDE.md`
- Architecture and diagram: `docs/ARCHITECTURE.md`
- Deployment guide: `docs/DEPLOY_AZURE_CONTAINER_APPS.md`

