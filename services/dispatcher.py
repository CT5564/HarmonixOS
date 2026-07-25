#Based on intent from the router, 
#dispatches the message to the appropriate service for processing.

from services.router import classify, Intent
from services import task_service, note_service, ai_service
from services.logger import logger
from services.entity_extractor import extract_task

async def dispatch(
    message: str,
    author_id: str = None,
    author_name: str = None
):
    
    print(f"Dispatching message: {message}")
    print(f"Author ID: {author_id}")
    print(f"Author Name: {author_name}")

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
                entity = await extract_task(message, author_id)
                await task_service.create_task(entity)
                return f"✅ Task created: **{entity.title}**"

            case Intent.TASK_QUERY:
                tasks = await task_service.get_all_tasks(author_id)

                if not tasks:
                    result = "🎉 No tasks."
                else:
                    msg = "# 📋 Tasks\n\n"

                    for task in tasks:
                        msg += f"`#{task[0]}` • {task[1]}\n"

                    result = msg

            case Intent.NOTE_CREATE:
                await note_service.create_note(
                    message,
                    author_id,
                    author_name
)
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
                print(
                    f"[Dispatcher] Author: {author_name}"
                )
                return await ai_service.ask(
                    message,
                    author_id=author_id,
                    author_name=author_name
                )
                

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