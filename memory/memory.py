import sqlite3
import os

DB_FOLDER = "database"
DB_NAME = "database/memory.db"


def init_db():

    # ساخت خودکار پوشه database
    os.makedirs(DB_FOLDER, exist_ok=True)

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        content TEXT
    )
    """)

    conn.commit()

    conn.close()


def save_message(user_id, role, content):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO messages (
        user_id,
        role,
        content
    )
    VALUES (?, ?, ?)
    """, (user_id, role, content))

    conn.commit()

    conn.close()


def load_messages(user_id, limit=10):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, content
    FROM messages
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()

    conn.close()

    rows.reverse()

    messages = []

    for role, content in rows:

        messages.append({
            "role": role,
            "content": content
        })

    return messages
