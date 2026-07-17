import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "harmonix.db"

DB_PATH.parent.mkdir(exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
        """)



def add_task(title: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO tasks(title) VALUES(?)",
            (title,)
        )


def get_tasks() -> list:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title
            FROM tasks
            WHERE completed = 0
            ORDER BY created_at
        """)

        return cursor.fetchall()

def complete_task(task_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tasks
            SET completed = 1,
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



def search_tasks(keyword):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title
            FROM tasks
            WHERE title LIKE ?
            ORDER BY created_at
        """, (f"%{keyword}%",))

        return cursor.fetchall()