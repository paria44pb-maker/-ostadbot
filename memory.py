import sqlite3

conn = sqlite3.connect("memory.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    favorite_coin TEXT,
    level TEXT
)
""")

conn.commit()


def save_user(user_id, coin="BTC", level="beginner"):

    cursor.execute("""
    INSERT OR REPLACE INTO users
    VALUES (?, ?, ?)
    """, (user_id, coin, level))

    conn.commit()


def get_user(user_id):

    cursor.execute("""
    SELECT * FROM users
    WHERE user_id=?
    """, (user_id,))

    return cursor.fetchone()
