# AI Service
#
# Thin wrapper around the chat agent.
# The dispatcher calls this for CHAT intent.

from agents.chat import chat_agent
from services.log import get_log
from services.logger import logger

log = get_log(__name__)


async def ask(
    prompt: str,
    author_id: str | None = None,
    author_name: str | None = None
) -> str:

    log.info(
        f"Chat request from "
        f"{author_name or 'Unknown'}"
    )

    await logger.ai(
        f"""
🚀 **AI Request**

**User**
{author_name or "Unknown"}

**Agent**
chat

**Prompt Length**
{len(prompt):,} characters

**Status**
⏳ Processing
"""
    )

    try:

        answer = await chat_agent(
            prompt,
            author_id=author_id,
            author_name=author_name
        )

    except Exception as e:

        log.error(
            f"{type(e).__name__}: {e}"
        )

        await logger.error(
            f"""
❌ **AI Error**

**User**
{author_name or "Unknown"}

**Agent**
chat

**Error**
```text
{type(e).__name__}: {e}
```

**Status**
🔴 Failed
"""
        )

        raise

    await logger.ai(
        f"""
✅ **AI Completed**

**User**
{author_name or "Unknown"}

**Agent**
chat

**Response Length**
{len(answer):,} characters

**Status**
✅ Done
"""
    )

    return answer
