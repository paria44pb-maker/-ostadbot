import sqlite3

def setup_db():

    conn = sqlite3.connect("memory.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        signal TEXT,
        time TEXT
    )
    """)

    conn.commit()

    conn.close()
