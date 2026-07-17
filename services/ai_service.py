from ollama import chat

import time

from services.logger import logger

from services.context import build_context

SYSTEM_PROMPT = """
You are Harmonix.

You are an operating system.

You have access to:

• Tasks
• Notes
• Projects

When answering,
use the provided context.

Never invent information that is not in the context.
"""


async def ask(prompt: str) -> str:
    
    start = time.time()

    context = build_context()
    
    print("=" * 50)
    print(context)
    print("=" * 50)

    response = chat(
        model="llama3.2:3b",      # Change if you're using another model
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT + "\n\n" + context
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
        🤖 AI Request

        **Model**
        llama3.2:3b

        **Time**
        {elapsed:.2f}s

        **Prompt**
        ```text
        {prompt[:300]}

        **Response**
        {len(response.message.content)} characters
        
        **Context**
        ```text
        Context:
        {len(context)} characters
        """
    )

    return response.message.content