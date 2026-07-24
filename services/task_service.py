# This file contains the task service for the bot.
# It is responsible for handling all task-related logic and database interactions.
# This file contains the task service for the bot.
# It is responsible for handling all task-related logic and database interactions.
# Everything backend related to tasks should be handled here, while the cogs/tasks.py file should only handle the frontend (discord commands).



from datetime import date

import services.database as db
from models.task import Task
from services.logger import logger

async def create_task(task: Task):
    print("Task Service:", task)
    db.add_task(task)
    
    await logger.task(
        f"Created task\n\n{task.title}"
    )


async def get_all_tasks():
    print("Getting all tasks")
    return db.get_tasks()


async def complete_task_by_id(task_id: int):

    db.complete_task(task_id)

    await logger.task(
        f"Completed task #{task_id}"
    )


async def delete_task_by_id(task_id: int):

    db.delete_task(task_id)

    await logger.task(
        f"Deleted task #{task_id}"
    )


async def edit_task(task_id: int, title: str):

    db.update_task(task_id, title)

    await logger.task(
        f"Edited task #{task_id}"
    )


async def search_for_tasks(keyword: str):

    return db.search_tasks(keyword)

async def get_today_tasks():

    today = date.today().isoformat()

    return db.get_today_tasks(today)

async def get_overdue_tasks():

    today = date.today().isoformat()

    return db.get_overdue_tasks(today)