# Sync Service
#
# Handles bidirectional sync between local
# SQLite tasks and the Notion "Stuff" database.
#
# Notion → Local: via webhook_server.py (real-time)
# Local → Notion: via push_to_notion() (on task mutation)

import asyncio

from services.notion_client import notion
from services.notion_service import (
    extract_rich_text,
    query_database,
)
import services.database as db
from services.log import get_log

from config import (
    NOTION_TASKS_DB_ID,
    NOTION_PROJECTS_DB_ID,
)

log = get_log(__name__)


# ============================================================
# COURSE NAME CACHE
# ============================================================

_course_cache: dict[str, str] = {}


async def resolve_course_name(
    course_page_id: str
) -> str:
    """Resolve a Course relation page ID to its
    project name. Cached in memory."""

    if course_page_id in _course_cache:
        return _course_cache[course_page_id]

    try:

        page = await asyncio.to_thread(
            notion.request,
            f"pages/{course_page_id}",
            "GET"
        )

        for prop in page.get(
            "properties", {}
        ).values():

            if prop.get("type") == "title":

                name = extract_rich_text(
                    prop.get("title", [])
                )

                if name:
                    _course_cache[
                        course_page_id
                    ] = name
                    return name

    except Exception as e:

        log.error(
            f"Failed to resolve course "
            f"{course_page_id}: {e}"
        )

    return ""


async def build_course_cache():
    """Pre-cache all course ID → name mappings
    from the Projects database."""

    global _course_cache

    try:

        entries = await query_database(
            NOTION_PROJECTS_DB_ID
        )

        for entry in entries:

            page_id = entry["id"]

            for prop in entry.get(
                "properties", {}
            ).values():

                if prop.get("type") == "title":

                    name = extract_rich_text(
                        prop.get("title", [])
                    )

                    if name:
                        _course_cache[
                            page_id
                        ] = name

        log.info(
            f"Cached "
            f"{len(_course_cache)} course names."
        )

    except Exception as e:

        log.error(
            f"Failed to build course "
            f"cache: {e}"
        )


async def find_course_id_by_name(
    name: str
) -> str | None:
    """Find a course page ID by its project name.
    Used when pushing tasks to Notion."""

    for pid, pname in _course_cache.items():

        if pname.lower() == name.lower():
            return pid

    return None


# ============================================================
# NOTION → LOCAL CONVERSION
# ============================================================

async def notion_to_local(
    entry: dict
) -> dict:
    """Convert a Notion page dict to a local
    task dict suitable for upsert_task_from_notion."""

    props = entry.get("properties", {})

    # Title
    title = ""
    title_prop = props.get(
        "Assignment Name", {}
    )
    if title_prop.get("type") == "title":
        title = extract_rich_text(
            title_prop.get("title", [])
        )

    # Status
    status = "todo"
    status_prop = props.get("Status", {})
    if status_prop.get("type") == "status":
        s = status_prop.get("status") or {}
        notion_status = s.get("name", "")
        if notion_status == "Done":
            status = "completed"
        else:
            status = "todo"

    # Priority
    priority = None
    prio_prop = props.get("Priority", {})
    if prio_prop.get("type") == "select":
        s = prio_prop.get("select") or {}
        p = s.get("name", "")
        if p:
            priority = p.lower()

    # Due date
    due_date = None
    due_prop = props.get("Due / When", {})
    if due_prop.get("type") == "date":
        d = due_prop.get("date") or {}
        due_date = d.get("start")

    # Type → tags
    tags = []
    type_prop = props.get("Type", {})
    if type_prop.get("type") == "select":
        s = type_prop.get("select") or {}
        t = s.get("name", "")
        if t:
            tags = [t]

    # Course → project
    project = None
    course_prop = props.get("Course", {})
    if course_prop.get("type") == "relation":
        relations = course_prop.get(
            "relation", []
        )
        if relations:
            course_id = relations[0].get("id")
            if course_id:
                project = (
                    await resolve_course_name(
                        course_id
                    )
                )

    return {
        "notion_page_id": entry["id"],
        "title": title or "Untitled",
        "description": None,
        "status": status,
        "priority": priority,
        "due_date": due_date,
        "due_time": None,
        "project": project,
        "tags": tags,
        "type": tags[0] if tags else None,
    }


# ============================================================
# LOCAL → NOTION CONVERSION
# ============================================================

def local_to_notion_props(
    task_data: dict
) -> dict:
    """Convert local task data to Notion page
    properties for create/update."""

    props = {}

    # Title
    props["Assignment Name"] = {
        "title": [
            {
                "text": {
                    "content": task_data.get(
                        "title", "Untitled"
                    )
                }
            }
        ]
    }

    # Status
    local_status = task_data.get(
        "status", "todo"
    )
    notion_status = (
        "Done"
        if local_status == "completed"
        else "Not Started"
    )
    props["Status"] = {
        "status": {"name": notion_status}
    }

    # Priority
    priority = task_data.get("priority")
    if priority:
        props["Priority"] = {
            "select": {
                "name": priority.capitalize()
            }
        }

    # Due date
    due_date = task_data.get("due_date")
    if due_date:
        props["Due / When"] = {
            "date": {"start": due_date}
        }

    # Type
    task_type = task_data.get("type")
    if not task_type:
        tags = task_data.get("tags", [])
        if tags:
            task_type = tags[0]
    if task_type:
        props["Type"] = {
            "select": {"name": task_type}
        }

    return props


# ============================================================
# PUSH LOCAL → NOTION
# ============================================================

async def push_to_notion(
    task_data: dict
):
    """Push a local task to Notion.
    Creates a new page if no notion_page_id,
    otherwise updates the existing page."""

    notion_page_id = task_data.get(
        "notion_page_id"
    )

    props = local_to_notion_props(task_data)

    try:

        if notion_page_id:

            await asyncio.to_thread(
                notion.request,
                f"pages/{notion_page_id}",
                "PATCH",
                body={
                    "properties": props
                }
            )

            log.info(
                f"Updated Notion page "
                f"{notion_page_id}"
            )

        else:

            # Resolve course → relation ID
            project = task_data.get("project")
            if project:
                course_id = (
                    await find_course_id_by_name(
                        project
                    )
                )
                if course_id:
                    props["Course"] = {
                        "relation": [
                            {"id": course_id}
                        ]
                    }

            response = await asyncio.to_thread(
                notion.request,
                "pages",
                "POST",
                body={
                    "parent": {
                        "database_id":
                            NOTION_TASKS_DB_ID
                    },
                    "properties": props,
                }
            )

            new_page_id = response["id"]

            task_id = task_data.get("id")
            if task_id:
                db.set_notion_page_id(
                    task_id, new_page_id
                )

            log.info(
                f"Created Notion page "
                f"{new_page_id}"
            )

            return new_page_id

    except Exception as e:

        log.error(
            f"Failed to push to Notion: "
            f"{e}"
        )

    return None


# ============================================================
# DELETE IN NOTION
# ============================================================

async def delete_in_notion(
    task_data: dict
):
    """Move a Notion page to trash."""

    notion_page_id = task_data.get(
        "notion_page_id"
    )

    if not notion_page_id:
        return

    try:

        await asyncio.to_thread(
            notion.request,
            f"pages/{notion_page_id}",
            "PATCH",
            body={"in_trash": True}
        )

        log.info(
            f"Trashed Notion page "
            f"{notion_page_id}"
        )

    except Exception as e:

        log.error(
            f"Failed to trash Notion "
            f"page: {e}"
        )


# ============================================================
# RESTORE IN NOTION
# ============================================================

async def restore_in_notion(
    task_data: dict
):
    """Restore a trashed Notion page."""

    notion_page_id = task_data.get(
        "notion_page_id"
    )

    if not notion_page_id:
        return

    try:

        await asyncio.to_thread(
            notion.request,
            f"pages/{notion_page_id}",
            "PATCH",
            body={"in_trash": False}
        )

        log.info(
            f"Restored Notion page "
            f"{notion_page_id}"
        )

    except Exception as e:

        log.error(
            f"Failed to restore Notion "
            f"page: {e}"
        )


# ============================================================
# UPSERT FROM NOTION (called by webhook handler)
# ============================================================

async def upsert_from_notion(
    page_id: str
):
    """Fetch a full page from Notion and
    upsert it into the local database."""

    try:

        entry = await asyncio.to_thread(
            notion.request,
            f"pages/{page_id}",
            "GET"
        )

        task_data = await notion_to_local(
            entry
        )

        local_id = db.upsert_task_from_notion(
            task_data
        )

        log.info(
            f"Upserted Notion page "
            f"{page_id} → local task "
            f"{local_id}"
        )

        return local_id

    except Exception as e:

        log.error(
            f"Failed to upsert from "
            f"Notion: {e}"
        )

    return None


# ============================================================
# INITIAL SYNC (on startup)
# ============================================================

async def initial_sync():
    """Pull all Notion tasks into local DB
    on startup. Notion is source of truth."""

    log.info("Starting initial sync...")

    await build_course_cache()

    try:

        entries = await query_database(
            NOTION_TASKS_DB_ID
        )

        log.info(
            f"Found {len(entries)} "
            f"entries in Notion."
        )

        for entry in entries:

            task_data = await notion_to_local(
                entry
            )

            db.upsert_task_from_notion(
                task_data
            )

        log.info(
            f"Initial sync complete. "
            f"Synced {len(entries)} tasks."
        )

    except Exception as e:

        log.error(
            f"Initial sync failed: {e}"
        )


# ============================================================
# PUSH UNSYNCED (periodic safety net)
# ============================================================

async def push_unsynced():
    """Push any locally modified tasks that
    haven't been synced to Notion yet."""

    unsynced = db.get_unsynced_tasks()

    if not unsynced:
        return

    log.info(
        f"Pushing {len(unsynced)} "
        f"unsynced tasks..."
    )

    for row in unsynced:

        task_data = {
            "id": row[0],
            "author_id": row[1],
            "title": row[2],
            "description": row[3],
            "status": row[4],
            "priority": row[5],
            "due_date": row[6],
            "due_time": row[7],
            "project": row[8],
            "tags": (
                __import__("json").loads(row[9])
                if row[9]
                else []
            ),
            "type": row[10],
            "notion_page_id": row[11],
        }

        await push_to_notion(task_data)
