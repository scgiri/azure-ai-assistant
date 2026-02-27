from __future__ import annotations

import json
import uuid
from typing import Any

from openai import AzureOpenAI

from assistant.models import ActionResult, AssistantResponse
from assistant.tool_registry import TOOL_REGISTRY
from assistant.tool_schemas import SYSTEM_PROMPT, TOOLS


class AzureToolCallingAssistant:
    def __init__(self, client: AzureOpenAI, deployment: str):
        self.client = client
        self.deployment = deployment

    def handle_request(self, user_input: str, request_id: str | None = None) -> dict[str, Any]:
        resolved_request_id = request_id or str(uuid.uuid4())

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"request_id={resolved_request_id}\n{user_input}"},
        ]

        action_results: list[ActionResult] = []

        for _ in range(5):
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0,
                response_format={"type": "json_object"},
            )

            assistant_message = response.choices[0].message
            tool_calls = assistant_message.tool_calls or []

            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [tc.model_dump() for tc in tool_calls],
                }
            )

            if not tool_calls:
                break

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments or "{}")

                tool_handler = TOOL_REGISTRY.get(function_name)
                if not tool_handler:
                    tool_output = {"error": f"Unknown tool: {function_name}"}
                    status = "failed"
                else:
                    try:
                        tool_output = tool_handler(**function_args)
                        status = "success"
                    except Exception as ex:
                        tool_output = {"error": str(ex)}
                        status = "failed"

                action_results.append(ActionResult(tool=function_name, status=status, data=tool_output))

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_output),
                    }
                )

        final_response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            tools=TOOLS,
            temperature=0,
            response_format={"type": "json_object"},
        )

        final_message = final_response.choices[0].message.content or "{}"

        try:
            model_payload = json.loads(final_message)
        except json.JSONDecodeError:
            model_payload = {
                "response_type": "action_result" if action_results else "message",
                "request_id": resolved_request_id,
                "message": "Model returned non-JSON response.",
            }

        if action_results:
            response_model = AssistantResponse(
                response_type="action_result",
                request_id=resolved_request_id,
                actions=action_results,
                message=model_payload.get("message"),
            )
            return response_model.to_dict()

        response_model = AssistantResponse(
            response_type=model_payload.get("response_type", "message"),
            request_id=resolved_request_id,
            message=model_payload.get("message", "No response message."),
        )
        return response_model.to_dict()
