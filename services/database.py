#Database Service. Handles all database operations for the bot.

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

        #Task Service Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        #Note Service Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)



def add_task(task: Task) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
        """
        INSERT INTO tasks(
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
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
    

def get_tasks() -> list:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                title,
                priority,
                due_date,
                due_time,
                project
            FROM tasks
            WHERE status = 'todo'
            ORDER BY created_at
        """)

        return cursor.fetchall()

def complete_task(task_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE tasks
        SET
            status = 'completed',
            completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (task_id,))
        

def delete_task(task_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )


def update_task(task_id, title):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tasks
            SET title = ?
            WHERE id = ?
        """, (title, task_id))



def search_tasks(keyword: str):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
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
                title LIKE ?
                OR description LIKE ?
                OR project LIKE ?
            LIMIT 5
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ))

        return cursor.fetchall()
    


#Notes
def add_note(content: str):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO notes(content) VALUES(?)",
            (content,)
        )

def get_notes():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, content
            FROM notes
            ORDER BY created_at DESC
        """)

        return cursor.fetchall()
    
def delete_note(note_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,)
        )

async def search_notes(keyword: str):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, content
            FROM notes
            WHERE content LIKE ?
            ORDER BY created_at DESC
        """, (f"%{keyword}%",))

        return cursor.fetchall()