from __future__ import annotations

import argparse
import json

from assistant.client import create_azure_openai_client
from assistant.orchestrator import AzureToolCallingAssistant
from config.settings import load_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Azure AI Assistant with function calling")
    parser.add_argument("--prompt", required=True, help="User request for the assistant")
    parser.add_argument("--endpoint", help="Azure OpenAI endpoint")
    parser.add_argument("--api-key", help="Azure OpenAI API key")
    parser.add_argument("--deployment", help="Azure OpenAI deployment name (example: gpt-4o)")
    parser.add_argument("--api-version", default=None, help="Azure OpenAI API version")
    parser.add_argument("--request-id", default=None, help="Optional custom request ID")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings(
        endpoint=args.endpoint,
        api_key=args.api_key,
        deployment=args.deployment,
        api_version=args.api_version,
    )

    client = create_azure_openai_client(settings)
    assistant = AzureToolCallingAssistant(client=client, deployment=settings.deployment)

    result = assistant.handle_request(user_input=args.prompt, request_id=args.request_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
