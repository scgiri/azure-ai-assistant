from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from assistant.client import create_azure_openai_client
from assistant.orchestrator import AzureToolCallingAssistant
from config.settings import load_settings


class AssistRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    request_id: str | None = None
    endpoint: str | None = None
    api_key: str | None = None
    deployment: str | None = None
    api_version: str | None = None


class AssistResponse(BaseModel):
    response_type: str
    request_id: str
    actions: list[dict[str, Any]] | None = None
    message: str | None = None


app = FastAPI(title="Azure Action Assistant API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/assist", response_model=AssistResponse)
def assist(request: AssistRequest) -> dict[str, Any]:
    try:
        settings = load_settings(
            endpoint=request.endpoint,
            api_key=request.api_key,
            deployment=request.deployment,
            api_version=request.api_version,
        )
        client = create_azure_openai_client(settings)
        assistant = AzureToolCallingAssistant(client=client, deployment=settings.deployment)
        result = assistant.handle_request(user_input=request.prompt, request_id=request.request_id)
        return result
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Assistant execution failed: {ex}") from ex
