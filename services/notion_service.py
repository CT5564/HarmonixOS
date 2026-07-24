# Notion Service
#
# Handles searching and reading Notion pages,
# databases, database entries, and nested blocks.

from services.notion_client import notion


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_rich_text(
    rich_text: list
) -> str:

    if not rich_text:
        return ""

    return "".join(
        item.get(
            "plain_text",
            ""
        )
        for item in rich_text
    )


# ============================================================
# PAGE TITLE
# ============================================================

def extract_page_title(
    page: dict
) -> str:

    properties = page.get(
        "properties",
        {}
    )

    for prop in properties.values():

        if prop.get(
            "type"
        ) == "title":

            return extract_rich_text(
                prop.get(
                    "title",
                    []
                )
            )

    return "Untitled"


# ============================================================
# BLOCK TEXT
# ============================================================

def extract_block_text(
    block: dict
) -> str:

    block_type = block.get(
        "type"
    )

    if not block_type:
        return ""


    data = block.get(
        block_type,
        {}
    )


    # ========================================================
    # RICH TEXT BLOCKS
    # ========================================================

    if "rich_text" in data:

        return extract_rich_text(
            data.get(
                "rich_text",
                []
            )
        )


    # ========================================================
    # CHILD PAGE
    # ========================================================

    if block_type == "child_page":

        return (
            data.get(
                "title"
            )
            or "Untitled Page"
        )


    # ========================================================
    # CHILD DATABASE
    # ========================================================

    if block_type == "child_database":

        return (
            data.get(
                "title"
            )
            or "Untitled Database"
        )


    return ""


# ============================================================
# RECURSIVE BLOCK READER
# ============================================================

async def get_block_children(
    block_id: str,
    depth: int = 0,
    max_depth: int = 10
) -> str:

    if depth > max_depth:

        return ""


    response = notion.blocks.children.list(
        block_id=block_id
    )


    blocks = response.get(
        "results",
        []
    )


    content = []


    for block in blocks:

        text = extract_block_text(
            block
        )


        if text:

            indent = "  " * depth

            content.append(
                f"{indent}{text}"
            )


        # ====================================================
        # RECURSIVE CHILD BLOCKS
        # ====================================================

        if block.get(
            "has_children",
            False
        ):

            children = (
                await get_block_children(
                    block["id"],
                    depth=depth + 1,
                    max_depth=max_depth
                )
            )


            if children:

                content.append(
                    children
                )


    return "\n".join(
        content
    )


# ============================================================
# PAGE CONTENT
# ============================================================

async def get_page_content(
    page_id: str
) -> str:

    return await get_block_children(
        page_id
    )


# ============================================================
# SEARCH PAGES
# ============================================================

async def search_pages(
    keyword: str
):

    response = notion.search(
        query=keyword
    )


    results = []


    for item in response.get(
        "results",
        []
    ):

        object_type = item.get(
            "object"
        )


        # Only pages for now

        if object_type != "page":

            continue


        title = extract_page_title(
            item
        )


        results.append(
            {
                "id": item["id"],
                "title": title,
                "type": "page"
            }
        )


    return results


# ============================================================
# SEARCH DATABASES
# ============================================================

async def search_databases(
    keyword: str
):

    response = notion.search(
        query=keyword,
        filter={
            "property": "object",
            "value": "database"
        }
    )

    results = []

    for item in response.get(
        "results",
        []
    ):

        title = extract_database_title(
            item
        )

        results.append(
            {
                "id": item["id"],
                "title": title,
                "type": "database"
            }
        )

    return results


# ============================================================
# QUERY DATABASE
# ============================================================

async def query_database(
    database_id: str
):

    response = notion.databases.query(
        database_id=database_id
    )


    return response.get(
        "results",
        []
    )


# ============================================================
# DATABASE PROPERTY EXTRACTION
# ============================================================

def extract_database_properties(
    page: dict
) -> str:

    properties = []


    for name, prop in page.get(
        "properties",
        {}
    ).items():

        prop_type = prop.get(
            "type"
        )


        if not prop_type:

            continue


        value = prop.get(
            prop_type
        )


        if not value:

            continue


        # ====================================================
        # TITLE
        # ====================================================

        if prop_type == "title":

            text = extract_rich_text(
                value
            )


        # ====================================================
        # RICH TEXT
        # ====================================================

        elif prop_type == "rich_text":

            text = extract_rich_text(
                value
            )


        # ====================================================
        # SELECT
        # ====================================================

        elif prop_type == "select":

            text = (
                value.get(
                    "name",
                    ""
                )
                if value
                else ""
            )


        # ====================================================
        # STATUS
        # ====================================================

        elif prop_type == "status":

            text = (
                value.get(
                    "name",
                    ""
                )
                if value
                else ""
            )


        # ====================================================
        # MULTI SELECT
        # ====================================================

        elif prop_type == "multi_select":

            text = ", ".join(
                item.get(
                    "name",
                    ""
                )
                for item in value
            )


        # ====================================================
        # DATE
        # ====================================================

        elif prop_type == "date":

            if value:

                text = (
                    value.get(
                        "start",
                        ""
                    )
                )

            else:

                text = ""


        # ====================================================
        # NUMBER
        # ====================================================

        elif prop_type == "number":

            text = str(
                value
            )


        # ====================================================
        # CHECKBOX
        # ====================================================

        elif prop_type == "checkbox":

            text = (
                "Yes"
                if value
                else "No"
            )


        # ====================================================
        # URL
        # ====================================================

        elif prop_type == "url":

            text = (
                value
                or ""
            )


        # ====================================================
        # EMAIL
        # ====================================================

        elif prop_type == "email":

            text = (
                value
                or ""
            )


        # ====================================================
        # PHONE
        # ====================================================

        elif prop_type == "phone_number":

            text = (
                value
                or ""
            )


        else:

            text = str(
                value
            )


        if text:

            properties.append(
                f"{name}: {text}"
            )


    return "\n".join(
        properties
    )


# ============================================================
# DATABASE CONTENT
# ============================================================

async def get_database_content(
    database_id: str
):

    entries = await query_database(
        database_id
    )


    content = []


    for entry in entries:

        title = extract_page_title(
            entry
        )


        properties = (
            extract_database_properties(
                entry
            )
        )


        page_content = (
            await get_page_content(
                entry["id"]
            )
        )


        entry_text = (
            f"Entry: {title}\n"
        )


        if properties:

            entry_text += (
                f"Properties:\n"
                f"{properties}\n"
            )


        if page_content:

            entry_text += (
                f"Content:\n"
                f"{page_content}\n"
            )


        content.append(
            entry_text
        )


    return "\n\n".join(
        content
    )

def extract_database_title(
    database: dict
) -> str:

    title = database.get(
        "title",
        []
    )

    return extract_rich_text(
        title
    ) or "Untitled Database"