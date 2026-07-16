from ollama import chat

import time

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
elapsed = time.time() - start

def ask(prompt: str) -> str:
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
    )

    return response.message.content

async def log_startup() -> None:
    await logger.ai(
    f"🔵 AI\n"
    f"Prompt took {elapsed:.2f}s"
)