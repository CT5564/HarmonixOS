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
    messages: list
) -> dict:

    def request():

        start_time = time.perf_counter()

        headers = {
            "Content-Type": "application/json"
        }

        # Only add API key if one is configured.
        if OMNIROUTE_API_KEY:
            headers["Authorization"] = (
                f"Bearer {OMNIROUTE_API_KEY}"
            )

        response = requests.post(
            OMNIROUTE_URL,
            headers=headers,
            json={
                "model": model,
                "messages": messages,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        elapsed = time.perf_counter() - start_time

        return data, elapsed

    data, elapsed = await asyncio.to_thread(
        request
    )

    # OmniRoute uses OpenAI-compatible responses.

    content = (
        data["choices"][0]
        ["message"]
        ["content"]
    )

    return {
        "model": data.get(
            "model",
            model
        ),

        "message": {
            "role": "assistant",
            "content": content
        },

        # OmniRoute timing
        "python_duration": elapsed,

        # These existed in the old Ollama response.
        # Keep them so the rest of Harmonix
        # doesn't break.

        "total_duration": 0,
        "load_duration": 0,
        "prompt_eval_duration": 0,
        "eval_duration": 0,

        "prompt_eval_count": data.get(
            "usage",
            {}
        ).get(
            "prompt_tokens",
            0
        ),

        "eval_count": data.get(
            "usage",
            {}
        ).get(
            "completion_tokens",
            0
        )
    }