# Task Service
#
# Responsible for task-related business logic
# and communication with the database layer.
#
# Discord/frontend logic should remain in cogs/tasks.py.
# User identity is represented by Discord user_id.

from datetime import date

import services.database as db
from models.task import Task
from services.log import get_log
from services.logger import logger

log = get_log(__name__)


# ============================================================
# CREATE TASK
# ============================================================

async def create_task(
    task: Task
):

    log.info(
        f"Task Service: {task}"
    )

    db.add_task(
        task
    )

    await logger.task(
        f"Created task\n\n"
        f"User: {task.author_id}\n"
        f"Task: {task.title}"
    )


# ============================================================
# GET ALL TASKS
# ============================================================

async def get_all_tasks(
    author_id: str
):

    log.info(
        f"Getting all tasks for user "
        f"{author_id}"
    )

    return db.get_tasks(
        author_id
    )


# ============================================================
# COMPLETE TASK
# ============================================================

async def complete_task_by_id(
    task_id: int,
    author_id: str
):

    db.complete_task(
        task_id,
        author_id
    )

    await logger.task(
        f"Completed task #{task_id}\n\n"
        f"User: {author_id}"
    )


# ============================================================
# DELETE TASK
# ============================================================

async def delete_task_by_id(
    task_id: int,
    author_id: str
):

    db.delete_task(
        task_id,
        author_id
    )

    await logger.task(
        f"Deleted task #{task_id}\n\n"
        f"User: {author_id}"
    )


# ============================================================
# EDIT TASK
# ============================================================

async def edit_task(
    task_id: int,
    author_id: str,
    title: str
):

    db.update_task(
        task_id,
        author_id,
        title
    )

    await logger.task(
        f"Edited task #{task_id}\n\n"
        f"User: {author_id}"
    )


# ============================================================
# SEARCH TASKS
# ============================================================

async def search_for_tasks(
    author_id: str,
    keyword: str
):

    return db.search_tasks(
        author_id,
        keyword
    )


# ============================================================
# TODAY'S TASKS
# ============================================================

async def get_today_tasks(
    author_id: str
):

    today = date.today().isoformat()

    return db.get_today_tasks(
        author_id,
        today
    )


# ============================================================
# OVERDUE TASKS
# ============================================================

async def get_overdue_tasks(
    author_id: str
):

    today = date.today().isoformat()

    return db.get_overdue_tasks(
        author_id,
        today
    )


# ============================================================
# UPCOMING TASKS (next 2 weeks)
# ============================================================

async def get_upcoming_tasks(
    author_id: str
):

    today = date.today().isoformat()
    end = (
        date.today()
        + __import__('datetime').timedelta(days=14)
    ).isoformat()

    return db.get_upcoming_tasks(
        author_id,
        today,
        end
    )