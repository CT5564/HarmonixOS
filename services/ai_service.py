from ollama import chat

import time

from services.logger import logger

start = time.time()

SYSTEM_PROMPT = """
You are Harmonix.

You are Jake's AI operating system.

Your job is to:
- help organize work
- answer questions
- help with coding
- help with academics
- help with church production
- help with music
- keep answers concise unless asked otherwise

Never mention being an AI assistant unless directly asked.
"""


def ask(prompt: str) -> str:
    elapsed = time.time() - start
    response = chat(
        model="llama3.2:3b",      # Change if you're using another model
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

    await logger.ai(
        f"🔵 AI\n"
        f"Prompt took {elapsed:.2f}s"

        )
    )

    return response.message.content