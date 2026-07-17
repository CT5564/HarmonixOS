#Based on intent from the router, 
#dispatches the message to the appropriate service for processing.


from services.router import classify, Intent
from services import task_service, note_service, ai_service


async def dispatch(message: str):

    intent = await classify(message)

    match intent:

        case Intent.TASK_CREATE:
            await task_service.create_task(message)
            return "✅ Task created."

        case Intent.TASK_QUERY:
            tasks = await task_service.get_tasks()
            return tasks

        case Intent.NOTE_CREATE:
            await note_service.create_note(message)
            return "📝 Note saved."

        case Intent.NOTE_QUERY:
            notes = await note_service.get_notes()
            return notes

        case Intent.CHAT:
            return await ai_service.ask(message)

        case _:
            return "I couldn't determine your intent."