from services.notion_client import notion


async def search_pages(query: str):

    response = notion.search(
        query=query
    )

    results = []

    for result in response.get(
        "results",
        []
    ):

        page_id = result["id"]

        properties = result.get(
            "properties",
            {}
        )

        title = "Untitled"

        for prop in properties.values():

            if prop["type"] == "title":

                title_parts = prop.get(
                    "title",
                    []
                )

                if title_parts:

                    title = "".join(
                        part["plain_text"]
                        for part in title_parts
                    )

                break

        results.append(
            {
                "id": page_id,
                "title": title
            }
        )

    return results


async def get_page_content(page_id: str):

    response = notion.blocks.children.list(
        block_id=page_id
    )

    blocks = response.get(
        "results",
        []
    )

    content = []

    for block in blocks:

        block_type = block.get(
            "type"
        )

        block_data = block.get(
            block_type,
            {}
        )

        rich_text = block_data.get(
            "rich_text",
            []
        )

        if not rich_text:
            continue

        text = "".join(
            item.get(
                "plain_text",
                ""
            )
            for item in rich_text
        )

        if text:

            content.append(
                text
            )

    return "\n".join(
        content
    )