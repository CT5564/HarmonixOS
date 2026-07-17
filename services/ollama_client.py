#Ollama Client Service
#Ollama settings are defined here (?)

import requests
import asyncio
import time
import json

def ollama_online():
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=2
        )

        response.raise_for_status()

        return True
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        return False
    

OLLAMA_URL = "http://localhost:11434/api/chat"


async def chat(model: str, messages: list) -> dict:
    """
    Send a chat request to Ollama.
    Returns the full JSON response.
    """
    print("✅ Ollama online" if ollama_online() else "❌ Ollama offline")
    def request():
            
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "messages": messages,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()

    start = time.perf_counter()

    data = await asyncio.to_thread(request)

    elapsed = time.perf_counter() - start

    data["python_duration"] = elapsed

    print(json.dumps(data, indent=4))

    return data

    