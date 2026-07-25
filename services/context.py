# Context Service.
# Builds AI-readable context from Harmonix's memory.

from services.memory import retrieve_memory
from services.logger import logger


async def build_context(
    prompt: str,
    author_id: str | None = None,
    author_name: str | None = None
) -> str:

    print("[Context] Retrieving memory...")

    memory = await retrieve_memory(
        prompt,
        author_id=author_id,
        author_name=author_name
    )

    print("[Context] Memory retrieved.")

    tasks = memory.get("tasks", [])
    notes = memory.get("notes", [])
    notion_pages = memory.get("notion_pages", [])

    context = []

    # ============================================================
    # TASKS
    # ============================================================

    if tasks:

        context.append(
            "## Relevant Tasks"
        )

        for task in tasks:

            context.append(
                f"- {task[1]}"
            )

    # ============================================================
    # NOTES
    # ============================================================

    if notes:

        context.append(
            "\n## Relevant Notes"
        )

        for note in notes:

            context.append(
                f"- {note[1]}"
            )

    # ============================================================
    # NOTION KNOWLEDGE
    # ============================================================

    if notion_pages:

        context.append(
            "\n## Relevant Notion Knowledge"
        )

        for page in notion_pages:

            context.append(
                f"""
### {page['title']}
Type: {page['type']}

{page['content']}
"""
            )

    # ============================================================
    # FINAL CONTEXT
    # ============================================================

    if not context:

        final_context = "No relevant memories."

    else:

        final_context = "\n".join(context)

    print(
        f"[Context] Built successfully: "
        f"{len(final_context):,} characters"
    )

    await logger.ai(
        f"""
🧠 **Memory Context Built**

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

**Status**
✅ Ready for AI
"""
    )

    return final_context