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


async def ask(prompt: str) -> str:
    
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

    elapsed = time.perf_counter() - start

    await logger.ai(
        f"""
        **Model**
        llama3.2:3b

        **Time**
        {elapsed:.2f}s

        **Prompt**
        ```text
        {prompt[:300]}

        Response
        {len(response.message.content)} characters
        """
    )

    return response.message.content