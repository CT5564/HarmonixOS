import services.database as db

from services.logger import logger


async def create_note(    
    content: str,
    author_id: str,
    author_name: str):

    
        return db.create_note(
            content=content,
            author_id=author_id,
            author_name=author_name
        )
        await logger.note(
            f"Created note\n\n{content}"
        )

async def get_notes():

    return db.get_notes()

async def delete_note_by_id(note_id: int):

    db.delete_note(note_id)

    await logger.note(
        f"Deleted note #{note_id}"
    )

async def search_for_notes(
    keyword: str
):

    return await db.search_notes(
        keyword
    )