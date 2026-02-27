# Architecture

This project uses Azure OpenAI function-calling as the orchestration layer between user intent and business tools.

## Mermaid diagram

```mermaid
flowchart LR
    U[User / Backend Caller] --> F[FastAPI /assist endpoint]
    U --> M[main.py CLI]
    F --> C[config.settings load env or args]
    M --> C
    C --> O[assistant.orchestrator]
    O --> AOAI[Azure OpenAI Chat Completion]
    AOAI -->|Tool call request| TR[assistant.tool_registry]
    TR --> F[tools.flight_service]
    TR --> W[tools.weather_service]
    TR --> CRM[tools.crm_service]
    TR --> RT[tools.realtime_service]
    F --> O
    W --> O
    CRM --> O
    RT --> O
    O --> J[Strict Structured JSON Output]
    J --> U
```

## Flow summary

1. Request enters via `main.py`.
    - or via FastAPI `POST /assist`.
2. Settings are loaded from args or environment.
3. Orchestrator sends prompt + tool definitions to Azure OpenAI.
4. Model selects tool(s).
5. Python executes selected tool(s).
6. Results are fed back to model context.
7. Final response is emitted as strict JSON for backend systems.
