import sqlite3
import json
import time

DB_NAME = "memory.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# =========================
# TABLES
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
user_message TEXT,
bot_message TEXT,
timestamp INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS long_memory (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
key TEXT,
value TEXT,
importance INTEGER,
timestamp INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_profile (
user_id INTEGER PRIMARY KEY,
name TEXT,
language TEXT,
preferences TEXT,
last_seen INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory_summary (
user_id INTEGER PRIMARY KEY,
summary TEXT,
updated_at INTEGER
)
""")

conn.commit()

# =========================
# SHORT TERM MEMORY
# =========================

def save_chat(user_id, user_message, bot_message):

    cursor.execute(
        """
        INSERT INTO chat_history
        (user_id, user_message, bot_message, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, user_message, bot_message, int(time.time()))
    )

    conn.commit()


def get_recent_chats(user_id, limit=12):

    cursor.execute(
        """
        SELECT user_message, bot_message
        FROM chat_history
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit)
    )

    rows = cursor.fetchall()

    rows.reverse()

    history = []

    for u, b in rows:
        history.append({"role": "user", "content": u})
        history.append({"role": "assistant", "content": b})

    return history


# =========================
# LONG TERM MEMORY
# =========================

def save_long_memory(user_id, key, value, importance=5):

    cursor.execute(
        """
        INSERT INTO long_memory
        (user_id, key, value, importance, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, key, value, importance, int(time.time()))
    )

    conn.commit()


def get_long_memory(user_id):

    cursor.execute(
        """
        SELECT key, value
        FROM long_memory
        WHERE user_id=?
        ORDER BY importance DESC
        LIMIT 20
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    memory = {}

    for k, v in rows:
        memory[k] = v

    return memory


# =========================
# USER PROFILE
# =========================

def update_user_profile(user_id, name=None, language=None, preferences=None):

    cursor.execute(
        """
        INSERT OR REPLACE INTO user_profile
        (user_id, name, language, preferences, last_seen)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            name,
            language,
            json.dumps(preferences) if preferences else None,
            int(time.time())
        )
    )

    conn.commit()


def get_user_profile(user_id):

    cursor.execute(
        """
        SELECT name, language, preferences
        FROM user_profile
        WHERE user_id=?
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    if not row:
        return {}

    name, language, preferences = row

    return {
        "name": name,
        "language": language,
        "preferences": json.loads(preferences) if preferences else {}
    }


# =========================
# MEMORY SUMMARY
# =========================

def save_summary(user_id, summary):

    cursor.execute(
        """
        INSERT OR REPLACE INTO memory_summary
        (user_id, summary, updated_at)
        VALUES (?, ?, ?)
        """,
        (user_id, summary, int(time.time()))
    )

    conn.commit()


def get_summary(user_id):

    cursor.execute(
        """
        SELECT summary
        FROM memory_summary
        WHERE user_id=?
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    return ""


# =========================
# MEMORY CLEANUP
# =========================

def cleanup_old_chats(days=30):

    limit_time = int(time.time()) - days * 86400

    cursor.execute(
        """
        DELETE FROM chat_history
        WHERE timestamp < ?
        """,
        (limit_time,)
    )

    conn.commit()


# =========================
# CONTEXT BUILDER
# =========================

def build_context(user_id):

    history = get_recent_chats(user_id)

    summary = get_summary(user_id)

    long_memory = get_long_memory(user_id)

    context = []

    if summary:
        context.append({
            "role": "system",
            "content": f"Conversation summary: {summary}"
        })

    if long_memory:
        mem_text = "\n".join(
            [f"{k}: {v}" for k, v in long_memory.items()]
        )

        context.append({
            "role": "system",
            "content": f"User information:\n{mem_text}"
        })

    context.extend(history)

    return context
