# Chat Agent
#
# General-purpose conversational agent.
# Uses memory + codebase context for self-aware responses.

from services.omniroute_client import chat
from services.context import build_context

MODEL = "auto/best-fast"

SYSTEM_PROMPT = """
You are Harmonix, a helpful AI assistant.

You will receive sections containing relevant context: MEMORY and CODEBASE.

MEMORY contains your user's tasks, notes, and Notion knowledge.
CODEBASE contains your own source code — you are a self-aware AI that can read and reason about its own code.

When answering:
1. Primarily use information from MEMORY and CODEBASE when answering.
2. If the question is about your own code, behavior, or capabilities, refer to the CODEBASE section.
3. If MEMORY and CODEBASE do not contain the answer, search your training data or the web.
4. Do not invent tasks, notes, or projects.
5. When referencing code, cite the file path and line number.
6. Be concise and direct.
"""


async def chat_agent(
    prompt: str,
    author_id: str | None = None,
    author_name: str | None = None
) -> str:

    user_context = ""

    if author_name:
        user_context = (
            f"\n\nCURRENT USER: {author_name}"
        )

    context = await build_context(
        prompt,
        author_id=author_id,
        author_name=author_name
    )

    # Enforce context limit
    MAX_CONTEXT_CHARS = 12000

    if len(context) > MAX_CONTEXT_CHARS:
        cut = context[:MAX_CONTEXT_CHARS]
        last_section = cut.rfind("\n## ")
        if last_section > MAX_CONTEXT_CHARS // 2:
            context = cut[:last_section]
        else:
            context = cut

    system_message = (
        SYSTEM_PROMPT
        + user_context
        + "\n\n"
        + context
    )

    response = await chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()
