# Context Service. Builds the current context for the AI.
import services.database as db
from services.memory import retrieve


def build_task_context():
    ...

def build_note_context():
    ...


def build_context(prompt: str):
    memory = retrieve(prompt)

    tasks = memory["tasks"]
    notes = memory["notes"]

    context = []

    # Tasks
    if tasks:

        context.append("## Relevant Tasks\n")

        for task in tasks:
            context.append(
                f"- {task[1]}"
            )

    # Notes
    if notes:

        context.append("\n## Relevant Notes\n")

        for note in notes:
            context.append(
                f"- {note[1]}"
            )

    if not context:
        return "No relevant memories."

    return "\n".join(context)