# Database Service
# Handles all database operations for the bot.

import sqlite3
import json
from pathlib import Path

from models.task import Task


DB_PATH = Path("data") / "harmonix.db"

DB_PATH.parent.mkdir(exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():

    with get_connection() as conn:

        cursor = conn.cursor()

        # ============================================================
        # TASK SERVICE TABLE
        # ============================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo',
            priority TEXT,
            due_date TEXT,
            due_time TEXT,
            project TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            notion_page_id TEXT,
            sync_status TEXT DEFAULT 'pending',
            last_synced TIMESTAMP
        )
        """)
        cursor.execute("""
        
        """)


        # ============================================================
        # NOTE SERVICE TABLE
        # ============================================================

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            author_id TEXT,
            author_name TEXT
        )
        """)

        conn.commit()


# ============================================================
# TASKS
# ============================================================

def add_task(task: Task) -> None:

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tasks(
                author_id,
                title,
                description,
                status,
                priority,
                due_date,
                due_time,
                project,
                tags,
                notion_page_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.author_id,
                task.title,
                task.description,
                "todo",
                task.priority,
                task.due_date,
                task.due_time,
                task.project,
                json.dumps(task.tags or []),
                None
            )
        )

        conn.commit()


def get_tasks(author_id: str) -> list:

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                priority,
                due_date,
                due_time,
                project
            FROM tasks
            WHERE
                author_id = ?
                AND status = 'todo'
            ORDER BY created_at
            """,
            (author_id,)
        )

        return cursor.fetchall()


def complete_task(
    task_id: int,
    author_id: str
) -> None:

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET
                status = 'completed',
                completed_at = CURRENT_TIMESTAMP
            WHERE
                id = ?
                AND author_id = ?
            """,
            (
                task_id,
                author_id
            )
        )

        conn.commit()


def delete_task(
    task_id: int,
    author_id: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM tasks
            WHERE
                id = ?
                AND author_id = ?
            """,
            (
                task_id,
                author_id
            )
        )

        conn.commit()


def update_task(
    task_id: int,
    author_id: str,
    title: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET title = ?
            WHERE
                id = ?
                AND author_id = ?
            """,
            (
                title,
                task_id,
                author_id
            )
        )

        conn.commit()


def search_tasks(
    author_id: str,
    keyword: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                priority,
                due_date,
                due_time,
                project,
                tags
            FROM tasks
            WHERE
                author_id = ?
                AND (
                    title LIKE ?
                    OR description LIKE ?
                    OR project LIKE ?
                )
            LIMIT 5
            """,
            (
                author_id,
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%"
            )
        )

        return cursor.fetchall()


def get_today_tasks(
    author_id: str,
    today: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                priority,
                due_date,
                due_time,
                project,
                tags,
                status
            FROM tasks
            WHERE
                author_id = ?
                AND due_date = ?
                AND status != 'completed'
            ORDER BY
                due_time IS NULL,
                due_time,
                created_at
            """,
            (
                author_id,
                today
            )
        )

        return cursor.fetchall()


def get_overdue_tasks(
    author_id: str,
    today: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                priority,
                due_date,
                due_time,
                project,
                tags,
                status
            FROM tasks
            WHERE
                author_id = ?
                AND due_date < ?
                AND status != 'completed'
            ORDER BY
                due_date,
                due_time
            """,
            (
                author_id,
                today
            )
        )

        return cursor.fetchall()


# ============================================================
# NOTES
# ============================================================

def add_note(
    content: str,
    author_id: str,
    author_name: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO notes (
                content,
                author_id,
                author_name
            )
            VALUES (?, ?, ?)
            """,
            (
                content,
                author_id,
                author_name
            )
        )

        conn.commit()


def get_notes():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                content
            FROM notes
            ORDER BY created_at DESC
            """
        )

        return cursor.fetchall()


def delete_note(
    note_id: int
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,)
        )

        conn.commit()


async def search_notes(
    keyword: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                content,
                author_id,
                author_name,
                created_at
            FROM notes
            WHERE
                content LIKE ?
                OR author_name LIKE ?
            ORDER BY created_at DESC
            """,
            (
                f"%{keyword}%",
                f"%{keyword}%"
            )
        )

        return cursor.fetchall()

