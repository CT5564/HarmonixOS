# AI Service. Handles all interactions with the AI model.

from services.ollama_client import chat
from services.context import build_context
from services.logger import logger

MODEL = "llama3.2:3b"

SYSTEM_PROMPT = """
You are Harmonix.

You are an operating system.

You have access to:

• Tasks
• Notes
• Projects

Use the provided context.

Never invent information not found in the context.
"""

async def ask(prompt: str):

    context = build_context()

    try:
        response = await chat(
            model=MODEL,
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

    except Exception as e:
        await logger.error(
            f"❌ AI Error\n\n```text\n{e}\n```"
        )
        raise

    await logger.ai(
    f"""
    🤖 AI Request

    **Model**
    {response['model']}

    **Python**
    {response['python_duration']:.2f}s

    **Inference**
    {response['total_duration']/1e9:.2f}s

    **Load**
    {response['load_duration']/1e9:.2f}s

    **Prompt Eval**
    {response['prompt_eval_duration']/1e9:.2f}s

    **Generation**
    {response['eval_duration']/1e9:.2f}s

    **Prompt Tokens**
    {response['prompt_eval_count']}

    **Generated Tokens**
    {response['eval_count']}

    **Context**
    {len(context)} chars

    **Response**
    {len(response['message']['content'])} chars
    """
    )

    return response["message"]["content"]