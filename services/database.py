import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "harmonix.db"

DB_PATH.parent.mkdir(exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
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

    conn.commit()
    conn.close()


def add_task(title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks(title) VALUES(?)",
        (title,)
    )

    conn.commit()
    conn.close()


def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title
        FROM tasks
        WHERE completed = 0
        ORDER BY created_at
    """)

    tasks = cursor.fetchall()

    conn.close()

    return tasks

def complete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET completed = 1,
            completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()


def update_task(task_id, title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET title = ?
        WHERE id = ?
    """, (title, task_id))

    conn.commit()
    conn.close()


def search_tasks(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title
        FROM tasks
        WHERE title LIKE ?
        ORDER BY created_at
    """, (f"%{keyword}%",))

    tasks = cursor.fetchall()

    conn.close()

    return tasks