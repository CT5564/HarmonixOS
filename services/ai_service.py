# AI Service. Handles all interactions with the AI model.

from services.ollama_client import chat
from services.context import build_context
from services.logger import logger

MODEL = "auto/best-fast"

SYSTEM_PROMPT = """
You are Harmonix.

You will receive a MEMORY section.

Primarily use information from MEMORY when answering.

If MEMORY does not contain the answer, search for the answer in your training data or the web.

Do not invent tasks, notes, or projects.
"""
async def ask(prompt: str,
    author_name: str | None = None):
    current_user_context = ""

    if author_name:

        current_user_context = (
            f"\n\nCURRENT USER:\n"
            f"The person currently speaking to you is "
            f"{author_name}."
        )
    context = await build_context(
        prompt,
        author_name=author_name
    )
    print(
        f"[DEBUG] Context type: {type(context)}"
    )

    print(
        f"[DEBUG] Context value: {context!r}"
    )
    print("Context Built.")
    print(context)
    try:
        print("Sending to AI...")
        response = await chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        SYSTEM_PROMPT
                        +"\n\n"
                        + current_user_context
                        + "\n\n"
                        + "MEMORY:\n"
                        + context
                    )
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

    usage = response.get(
        "usage",
        {}
    )

    await logger.ai(
        f"""
    🤖 AI Request

    **Model**
    {response.get('model', 'Unknown')}

    **Context**
    {len(context)} chars

    **Prompt Tokens**
    {usage.get('prompt_tokens', 'Unknown')}

    **Generated Tokens**
    {usage.get('completion_tokens', 'Unknown')}

    **Total Tokens**
    {usage.get('total_tokens', 'Unknown')}

    **Response**
    {len(response['choices'][0]['message']['content'])} chars
    """
    )
    
    return response[
        "choices"
    ][0][
        "message"
    ][
        "content"
    ]