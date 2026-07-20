#Based on intent from the router, 
#dispatches the message to the appropriate service for processing.

from services.router import classify, Intent
from services import task_service, note_service, ai_service
from services.logger import logger

async def dispatch(message: str):

    print(f"Dispatching message: {message}")

    intent = await classify(message)

    print(f"Identified intent: {intent}")

    await logger.info(
        f"""
📨 Dispatch

**Message**
{message}

**Intent**
{intent.name}
"""
    )

    try:

        match intent:

            case Intent.TASK_CREATE:
                await task_service.create_task(message)
                result = "✅ Task created."

            case Intent.TASK_QUERY:
                tasks = await task_service.get_tasks()

                if not tasks:
                    result = "🎉 No tasks."
                else:
                    msg = "# 📋 Tasks\n\n"

                    for task in tasks:
                        msg += f"`#{task[0]}` • {task[1]}\n"

                    result = msg

            case Intent.NOTE_CREATE:
                await note_service.create_note(message)
                result = "📝 Note saved."

            case Intent.NOTE_QUERY:
                notes = await note_service.get_notes()

                if not notes:
                    result = "📝 No notes."

                else:
                    msg = "# 📝 Notes\n\n"

                    for note in notes:
                        msg += f"`#{note[0]}` • {note[1]}\n"

                    result = msg

            case Intent.CHAT:
                result = await ai_service.ask(message)

            case _:
                result = "I couldn't determine your intent."

        await logger.info(
            f"""
✅ Dispatch Complete

**Intent**
{intent.name}

**Response**
{result[:300]}
"""
        )

        return result

    except Exception as e:

        await logger.error(
            f"""
            ❌ Dispatch Error

            **Message**
            {message}

            **Intent**
            {intent.name if intent else "Unknown"}

            ```text
            {e}
            ```
            """
        )