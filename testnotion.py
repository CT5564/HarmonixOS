from services.notion_service import (
    get_database_content
)

import asyncio


async def main():

    database_id = (
        "20798e48-9e2b-80d4-87df-db961c0249df"
    )

    print(
        "🔎 Querying database..."
    )

    content = await get_database_content(
        database_id
    )

    print(
        "\n========== DATABASE CONTENT ==========\n"
    )

    print(
        content
    )

    print(
        "\n======================================"
    )


asyncio.run(main())