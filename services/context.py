import services.database as db

def build_task_context():
    ...

def build_note_context():
    ...


def build_context() -> str:
    """
    Builds the current context for the AI.
    """

    tasks = db.get_tasks()[:10]
    notes = db.get_notes()[:20]

    context = "# CURRENT CONTEXT\n\n"

    # Tasks
    context += "## Active Tasks\n"

    if tasks:
        for task in tasks:
            context += f"- {task[1]}\n"
    else:
        context += "- None\n"

    context += "\n"

    # Notes
    context += "## Notes\n"

    if notes:
        for note in notes[:10]:   # only the 10 most recent
            context += f"- {note[1]}\n"
    else:
        context += "- None\n"

    return context