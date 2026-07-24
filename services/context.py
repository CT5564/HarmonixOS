# Context Service.
# Builds AI-readable context from Harmonix's memory.

from services.memory import retrieve_memory

async def build_context(
    prompt: str,
    author_name: str | None = None
):

    memory = await retrieve_memory(
        prompt,
        author_name=author_name
    )

    tasks = memory["tasks"]
    notes = memory["notes"]
    notion_pages = memory["notion_pages"]

    context = []

    # Tasks
    if tasks:

        context.append(
            "## Relevant Tasks\n"
        )

        for task in tasks:

            context.append(
                f"- {task[1]}"
            )

    # Notes
    if notes:

        context.append(
            "\n## Relevant Notes\n"
        )

        for note in notes:

            context.append(
                f"- {note[1]}"
            )
    # Notion Pages

    if notion_pages:

        context.append(
            "\n## Relevant Notion Knowledge\n"
        )


        for page in notion_pages:

            context.append(
                f"""
    ### {page['title']}
    Type: {page['type']}

    {page['content']}
    """
            )

    if not context:
        return "No relevant memories."

    return "\n".join(context)