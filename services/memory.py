import services.database as db


def retrieve(query: str):

    return {
        "tasks": db.search_tasks(query),
        "notes": db.search_notes(query)
    }