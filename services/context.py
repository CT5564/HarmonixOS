# Context Service.
# Builds AI-readable context from Harmonix's memory.

from services.memory import retrieve_memory


async def build_context(prompt: str) -> str:

    # Retrieve relevant memories
    memory = await retrieve_memory(
        prompt
    )

    tasks = memory.get(
        "tasks",
        []
    )

    notes = memory.get(
        "notes",
        []
    )

    context = []


    # ============================================================
    # RELEVANT TASKS
    # ============================================================

    if tasks:

        context.append(
            "## Relevant Tasks"
        )

        for task in tasks:

            context.append(
                f"""
Title: {task[1]}
Description: {task[2]}
Priority: {task[3]}
Due Date: {task[4]}
Due Time: {task[5]}
Project: {task[6]}
Tags: {task[7]}
""".strip()
            )


    # ============================================================
    # RELEVANT NOTES
    # ============================================================

    if notes:

        context.append(
            "## Relevant Notes"
        )

        for note in notes:

            context.append(
                f"""
Note ID: {note[0]}
Content: {note[1]}
""".strip()
            )


    # ============================================================
    # NO MEMORY
    # ============================================================

    if not context:

        return "No relevant memories."


    return "\n\n".join(
        context
    )