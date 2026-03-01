# Architecture

This project uses Azure OpenAI function-calling as the orchestration layer between user intent and business tools.

## Mermaid diagram

```mermaid
flowchart LR
    U[User / Backend Caller] --> API[FastAPI /assist endpoint]
    U --> M[main.py CLI]
    API --> C[config.settings load env or args]
    M --> C
    C --> O[assistant.orchestrator]
    O --> AOAI[Azure OpenAI Chat Completion]
    AOAI -->|Tool call request| TR[assistant.tool_registry]
    TR --> FS[tools.flight_service]
    TR --> WS[tools.weather_service]
    TR --> CRM[tools.crm_service]
    TR --> RT[tools.realtime_service]
    FS --> DL[tools.data_loader]
    WS --> DL
    CRM --> DL
    RT --> DL
    DL --> DATA[(data/*.json)]
    FS --> O
    WS --> O
    CRM --> O
    RT --> O
    O --> J[Strict Structured JSON Output]
    J --> U
```

## Flow summary

1. Request enters via `main.py` (CLI) or FastAPI `POST /assist`.
2. Settings are loaded from args or `.env` environment variables.
3. Orchestrator sends prompt + tool definitions to Azure OpenAI.
4. Model selects tool(s) and returns structured tool-call requests.
5. `tool_registry` dispatches to the appropriate service in `tools/`.
6. Each service uses `data_loader` to read from `data/*.json`.
7. Tool results are fed back to the model context.
8. Final response is emitted as strict JSON for backend systems.

## Deployment

- **Docker image** built from `Dockerfile` (Python 3.12-slim)
- **CI** (`.github/workflows/ci.yml`): validates, builds, and pushes image to Azure Container Registry
- **CD** (`.github/workflows/cd-aca.yml`): deploys to Azure Container Apps
- ACR auth uses OIDC — no registry username/password needed
