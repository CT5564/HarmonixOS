import asyncio

from services.notion_service import (
    get_page_content
)


PAGE_ID = "20698e489e2b809dbc08f4633b69e718"


async def main():

    try:

        content = await get_page_content(
            PAGE_ID
        )

        print(
            "✅ Page content:\n"
        )

        print(content)


    except Exception as e:

        print(
            "❌ Failed to retrieve page"
        )

        print(e)


asyncio.run(
    main()
)