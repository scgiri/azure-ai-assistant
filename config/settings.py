from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class AzureOpenAISettings:
    endpoint: str
    api_key: str
    deployment: str
    api_version: str = "2024-02-01"


def load_settings(
    *,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    deployment: Optional[str] = None,
    api_version: Optional[str] = None,
) -> AzureOpenAISettings:
    load_dotenv()

    resolved_endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "")
    resolved_api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY", "")
    resolved_deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    resolved_api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

    missing = []
    if not resolved_endpoint:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not resolved_api_key:
        missing.append("AZURE_OPENAI_API_KEY")
    if not resolved_deployment:
        missing.append("AZURE_OPENAI_DEPLOYMENT")

    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Missing required configuration values: {joined}")

    return AzureOpenAISettings(
        endpoint=resolved_endpoint,
        api_key=resolved_api_key,
        deployment=resolved_deployment,
        api_version=resolved_api_version,
    )
