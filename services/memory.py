import services.task_service as task_service

def build_context(query: str) -> str:

    tasks = task_service.search_for_tasks(query)

    context = []

    if tasks:

        context.append("Relevant Tasks:")

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
"""
            )

    return "\n".join(context)