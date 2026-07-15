import sqlite3

conn = sqlite3.connect("data/jake.db")

cursor = conn.cursor()

def add_task(task):

    cursor.execute(
        "INSERT INTO tasks(title) VALUES(?)",
        (task,)
    )

    conn.commit()