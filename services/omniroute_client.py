# AI Client
# Sends AI requests through OmniRoute.

import os
import asyncio
import time

import requests

from dotenv import load_dotenv

load_dotenv()

OMNIROUTE_URL = os.getenv(
    "OMNIROUTE_URL",
    "http://localhost:20128/v1/chat/completions"
)

OMNIROUTE_API_KEY = os.getenv(
    "OMNIROUTE_API_KEY"
)


async def chat(
    model: str,
    messages: list,
    tools: list | None = None
) -> dict:

    def request():

        start_time = time.perf_counter()

        headers = {
            "Content-Type": "application/json"
        }

        if OMNIROUTE_API_KEY:
            headers["Authorization"] = (
                f"Bearer {OMNIROUTE_API_KEY}"
            )

        body = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        if tools:
            body["tools"] = tools

        response = requests.post(
            OMNIROUTE_URL,
            headers=headers,
            json=body,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        elapsed = time.perf_counter() - start_time

        return data, elapsed

    data, elapsed = await asyncio.to_thread(
        request
    )

    choice = data["choices"][0]

    message = choice.get("message", {})

    content = message.get("content") or ""

    tool_calls = message.get("tool_calls")

    return {
        "model": data.get(
            "model",
            model
        ),

        "message": {
            "role": "assistant",
            "content": content,
            **(
                {"tool_calls": tool_calls}
                if tool_calls
                else {}
            ),
        },

        "finish_reason": choice.get(
            "finish_reason", "stop"
        ),

        "python_duration": elapsed,

        "total_duration": 0,
        "load_duration": 0,
        "prompt_eval_duration": 0,
        "eval_duration": 0,

        "prompt_eval_count": data.get(
            "usage", {}
        ).get("prompt_tokens", 0),

        "eval_count": data.get(
            "usage", {}
        ).get("completion_tokens", 0),
    }
