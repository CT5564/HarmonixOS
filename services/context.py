# Context Service.
# Builds AI-readable context from Harmonix's memory and codebase.
# Uses smart budgeting so context fits within the AI's token limit.

import asyncio

from services.memory import retrieve_memory
from services.codebase_service import search_and_read
from services.logger import logger
from services.log import get_log

log = get_log(__name__)


# Budget allocation for each context section
MEMORY_MAX_CHARS = 6000
NOTION_MAX_CHARS = 3000
CODEBASE_MAX_CHARS = 4000


def _truncate(text: str, max_chars: int) -> str:
    """Truncate text at a section boundary when possible."""

    if len(text) <= max_chars:
        return text

    # Try to cut at a section header (## )
    cut = text[:max_chars]
    last_section = cut.rfind("\n## ")

    if last_section > max_chars // 2:
        return cut[:last_section]

    # Fall back to hard truncate
    return cut


async def build_context(
    prompt: str,
    author_id: str | None = None,
    author_name: str | None = None
) -> str:

    log.info("Retrieving memory and codebase...")

    # Run memory and codebase retrieval concurrently
    memory_task = asyncio.create_task(
        retrieve_memory(
            prompt,
            author_id=author_id,
            author_name=author_name
        )
    )
    codebase_task = asyncio.create_task(
        search_and_read(prompt)
    )

    memory, codebase = await asyncio.gather(
        memory_task,
        codebase_task
    )

    log.info("Memory and codebase retrieved.")

    tasks = memory.get("tasks", [])
    notes = memory.get("notes", [])
    notion_pages = memory.get("notion_pages", [])

    context = []

    # ============================================================
    # TASKS (highest priority)
    # ============================================================

    if tasks:

        context.append("## Relevant Tasks")

        for task in tasks:
            context.append(f"- {task[1]}")

    # ============================================================
    # NOTES (high priority)
    # ============================================================

    if notes:

        context.append("\n## Relevant Notes")

        for note in notes:
            context.append(f"- {note[1]}")

    # ============================================================
    # NOTION KNOWLEDGE (lower priority, often large)
    # ============================================================

    if notion_pages:

        notion_parts = ["\n## Relevant Notion Knowledge"]

        for page in notion_pages:

            # Truncate individual page content
            content = page.get("content", "")
            if len(content) > 1500:
                content = content[:1500] + "\n..."

            notion_parts.append(
                f"### {page['title']}\n"
                f"Type: {page['type']}\n\n"
                f"{content}"
            )

        notion_block = "\n".join(notion_parts)

        # Apply budget
        notion_block = _truncate(
            notion_block,
            NOTION_MAX_CHARS
        )

        context.append(notion_block)

    # ============================================================
    # CODEBASE (always relevant for self-awareness)
    # ============================================================

    if codebase:

        codebase = _truncate(
            codebase,
            CODEBASE_MAX_CHARS
        )

        context.append(
            f"\n## Harmonix Source Code\n\n{codebase}"
        )

    # ============================================================
    # FINAL CONTEXT (with budget enforcement)
    # ============================================================

    if not context:

        final_context = "No relevant memories."

    else:

        final_context = "\n".join(context)

        # Apply total memory budget
        # (tasks + notes + notion should fit in MEMORY_MAX)
        # Codebase already self-limited
        total_budget = MEMORY_MAX_CHARS + CODEBASE_MAX_CHARS

        if len(final_context) > total_budget:
            final_context = _truncate(
                final_context,
                total_budget
            )

    log.info(
        f"Built successfully: "
        f"{len(final_context):,} characters"
    )

    await logger.ai(
        f"""
🧠 **Context Built**

**User**
{author_name or "Unknown"}

**Context Length**
{len(final_context):,} characters

**Tasks Found**
{len(tasks)}

**Notes Found**
{len(notes)}

**Notion Sources Found**
{len(notion_pages)}

**Codebase Included**
{"Yes" if codebase else "No"}

**Status**
✅ Ready for AI
"""
    )

    return final_context
