#Based on intent from the router, 
#dispatches the message to the appropriate service for processing.


from services.router import classify, Intent
from services import task_service, note_service, ai_service
from services.entity_extractor import extract_task

async def dispatch(message: str):

    intent = await classify(message)
    print(f"Dispatching message: {message}")
    print(f"Identified intent: {intent}")
    match intent:

        case Intent.TASK_CREATE:

            task = await extract_task(message)
            await task_service.create_task(task)
            return f"✅ Saved **{task.title}**"
            

        case Intent.TASK_QUERY:
            tasks = await task_service.get_all_tasks()
            if not tasks:
                return "🎉 No tasks."

            msg = "# 📋 Tasks\n\n"

            for task in tasks:
                msg += f"`#{task[0]}` • {task[1]}\n"

            print(intent)
            return msg

        case Intent.NOTE_CREATE:
            await note_service.create_note(message)
            print(intent)
            return "📝 Note saved."

        case Intent.NOTE_QUERY:
            notes = await note_service.get_notes()
            print(intent)
            return notes

        case Intent.CHAT:
            print(intent)
            return await ai_service.ask(message)

        case _:
            return "I couldn't determine your intent."
        
    