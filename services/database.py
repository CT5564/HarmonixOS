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
        # MIGRATIONS — add columns if missing
        # ============================================================

        cursor.execute(
            "PRAGMA table_info(tasks)"
        )
        cols = {
            row[1]
            for row in cursor.fetchall()
        }

        if "updated_at" not in cols:
            cursor.execute(
                "ALTER TABLE tasks "
                "ADD COLUMN updated_at "
                "TIMESTAMP"
            )

        if "type" not in cols:
            cursor.execute(
                "ALTER TABLE tasks "
                "ADD COLUMN type TEXT"
            )

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
                type,
                notion_page_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                getattr(task, "type", None),
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


def get_task_by_id(
    task_id: int
):
    """Get a single task by its local ID."""

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                author_id,
                title,
                description,
                status,
                priority,
                due_date,
                due_time,
                project,
                tags,
                type,
                notion_page_id
            FROM tasks
            WHERE id = ?
            """,
            (task_id,)
        )

        return cursor.fetchone()


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
                completed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
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
            SET title = ?,
                updated_at = CURRENT_TIMESTAMP
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
    author_id: str | None,
    keyword: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        if author_id:
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
        else:
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
                    (
                        title LIKE ?
                        OR description LIKE ?
                        OR project LIKE ?
                    )
                LIMIT 5
                """,
                (
                    f"%{keyword}%",
                    f"%{keyword}%",
                    f"%{keyword}%"
                )
            )

        return cursor.fetchall()


def get_today_tasks(
    author_id: str | None,
    today: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        if author_id:
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
        else:
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
                    due_date = ?
                    AND status != 'completed'
                ORDER BY
                    due_time IS NULL,
                    due_time,
                    created_at
                """,
                (today,)
            )

        return cursor.fetchall()


def get_overdue_tasks(
    author_id: str | None,
    today: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        if author_id:
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
        else:
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
                    due_date < ?
                    AND status != 'completed'
                ORDER BY
                    due_date,
                    due_time
                """,
                (today,)
            )

        return cursor.fetchall()


def get_upcoming_tasks(
    author_id: str | None,
    today: str,
    end_date: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        if author_id:
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
                    AND due_date > ?
                    AND due_date <= ?
                    AND status != 'completed'
                ORDER BY
                    due_date,
                    due_time IS NULL,
                    due_time,
                    created_at
                """,
                (
                    author_id,
                    today,
                    end_date
                )
            )
        else:
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
                    due_date > ?
                    AND due_date <= ?
                    AND status != 'completed'
                ORDER BY
                    due_date,
                    due_time IS NULL,
                    due_time,
                    created_at
                """,
                (
                    today,
                    end_date
                )
            )

        return cursor.fetchall()


# ============================================================
# NOTION SYNC
# ============================================================

def upsert_task_from_notion(
    data: dict
) -> int | None:
    """Insert or update a task by notion_page_id.
    Returns the local task id."""

    with get_connection() as conn:

        cursor = conn.cursor()

        notion_page_id = data.get("notion_page_id")

        if not notion_page_id:
            return None

        cursor.execute(
            """
            SELECT id FROM tasks
            WHERE notion_page_id = ?
            """,
            (notion_page_id,)
        )

        existing = cursor.fetchone()

        tags_json = json.dumps(
            data.get("tags", [])
        )

        if existing:

            cursor.execute(
                """
                UPDATE tasks
                SET
                    title = ?,
                    description = ?,
                    status = ?,
                    priority = ?,
                    due_date = ?,
                    due_time = ?,
                    project = ?,
                    tags = ?,
                    type = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    last_synced = CURRENT_TIMESTAMP
                WHERE
                    notion_page_id = ?
                """,
                (
                    data.get("title", ""),
                    data.get("description"),
                    data.get("status", "todo"),
                    data.get("priority"),
                    data.get("due_date"),
                    data.get("due_time"),
                    data.get("project"),
                    tags_json,
                    data.get("type"),
                    notion_page_id
                )
            )

            conn.commit()
            return existing[0]

        else:

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
                    type,
                    notion_page_id,
                    sync_status,
                    last_synced
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, 'synced',
                    CURRENT_TIMESTAMP
                )
                """,
                (
                    data.get(
                        "author_id",
                        "0"
                    ),
                    data.get("title", ""),
                    data.get("description"),
                    data.get("status", "todo"),
                    data.get("priority"),
                    data.get("due_date"),
                    data.get("due_time"),
                    data.get("project"),
                    tags_json,
                    data.get("type"),
                    notion_page_id
                )
            )

            conn.commit()
            return cursor.lastrowid


def get_task_by_notion_id(
    notion_page_id: str
):
    """Get a local task by its Notion page ID."""

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                author_id,
                title,
                description,
                status,
                priority,
                due_date,
                due_time,
                project,
                tags,
                type,
                notion_page_id,
                updated_at,
                last_synced
            FROM tasks
            WHERE notion_page_id = ?
            """,
            (notion_page_id,)
        )

        return cursor.fetchone()


def mark_task_synced(
    task_id: int
):
    """Mark a task as synced with Notion."""

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET
                last_synced = CURRENT_TIMESTAMP,
                sync_status = 'synced'
            WHERE id = ?
            """,
            (task_id,)
        )

        conn.commit()


def get_unsynced_tasks():
    """Get tasks that need syncing to Notion.
    Either no notion_page_id (new) or
    last_synced < updated_at (modified)."""

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                author_id,
                title,
                description,
                status,
                priority,
                due_date,
                due_time,
                project,
                tags,
                type,
                notion_page_id,
                updated_at,
                last_synced
            FROM tasks
            WHERE
                status != 'deleted'
                AND (
                    notion_page_id IS NULL
                    OR last_synced IS NULL
                    OR updated_at > last_synced
                )
            """
        )

        return cursor.fetchall()


def set_notion_page_id(
    task_id: int,
    notion_page_id: str
):
    """Store the Notion page ID for a local task."""

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET
                notion_page_id = ?,
                last_synced = CURRENT_TIMESTAMP,
                sync_status = 'synced'
            WHERE id = ?
            """,
            (
                notion_page_id,
                task_id
            )
        )

        conn.commit()


def soft_delete_task_by_notion_id(
    notion_page_id: str
):
    """Mark a local task as deleted when
    Notion page is trashed."""

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET
                status = 'deleted',
                updated_at = CURRENT_TIMESTAMP,
                last_synced = CURRENT_TIMESTAMP
            WHERE notion_page_id = ?
            """,
            (notion_page_id,)
        )

        conn.commit()


def restore_task_by_notion_id(
    notion_page_id: str
):
    """Restore a locally deleted task when
    Notion page is restored."""

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET
                status = 'todo',
                updated_at = CURRENT_TIMESTAMP,
                last_synced = CURRENT_TIMESTAMP
            WHERE
                notion_page_id = ?
                AND status = 'deleted'
            """,
            (notion_page_id,)
        )

        conn.commit()


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


def update_note(
    note_id: int,
    content: str
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE notes
            SET content = ?
            WHERE id = ?
            """,
            (
                content,
                note_id
            )
        )

        conn.commit()


def search_notes(
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

