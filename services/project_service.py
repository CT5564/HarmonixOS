# services/project_service.py

import services.notion_service as notion_service


async def get_project_names():

    database_id = "12f98e489e2b81adb67ccdc6f51f0989"

    entries = await notion_service.query_database(
        database_id
    )

    project_names = []

    for entry in entries:

        title = notion_service.extract_page_title(
            entry
        )

        if title:
            project_names.append(title)

    return project_names
