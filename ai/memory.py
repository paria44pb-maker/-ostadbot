import sqlite3

DB_PATH = "database/memory.db"


def init_db():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        memory TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_memory(user_id, memory):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO users (user_id, memory)
    VALUES (?, ?)
    """, (user_id, memory))

    conn.commit()
    conn.close()


def get_memory(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT memory FROM users
    WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return ""
