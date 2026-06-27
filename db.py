import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import aiosqlite
from config import DATABASE_URL

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    language TEXT DEFAULT 'fa',
    risk_level TEXT DEFAULT 'medium',
    plan TEXT DEFAULT 'free',
    plan_until INTEGER DEFAULT 0,
    created_at INTEGER
);
CREATE TABLE IF NOT EXISTS user_state (
    user_id INTEGER PRIMARY KEY,
    last_ai_at INTEGER DEFAULT 0,
    daily_ai_count INTEGER DEFAULT 0,
    last_reset_day TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS watchlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    symbol TEXT,
    target_price REAL DEFAULT 0,
    created_at INTEGER
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    plan TEXT,
    amount REAL,
    status TEXT,
    reference TEXT,
    created_at INTEGER
);
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    data TEXT,
    created_at INTEGER
);
"""

def tehran_now():
    return datetime.now(ZoneInfo("Asia/Tehran"))

async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as conn:
        await conn.executescript(CREATE_TABLES)
        await conn.commit()

async def q(sql, params=(), one=False, all_=False):
    async with aiosqlite.connect(DATABASE_URL) as conn:
        cur = await conn.execute(sql, params)
        if one:
            return await cur.fetchone()
        if all_:
            return await cur.fetchall()
        await conn.commit()

async def upsert_user(user_id, username, full_name):
    await q(
        "INSERT INTO users(user_id, username, full_name, created_at) VALUES(?,?,?,?) "
        "ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name",
        (user_id, username, full_name, int(time.time()))
    )
    await q(
        "INSERT OR IGNORE INTO user_state(user_id, last_ai_at, daily_ai_count, last_reset_day) VALUES(?,?,?,?)",
        (user_id, 0, 0, tehran_now().date().isoformat())
    )

async def get_user(user_id):
    return await q("SELECT * FROM users WHERE user_id=?", (user_id,), one=True)

async def set_plan(user_id, plan="vip", days=30, reference="manual"):
    until = int((tehran_now() + timedelta(days=days)).timestamp())
    await q("UPDATE users SET plan=?, plan_until=? WHERE user_id=?", (plan, until, user_id))
    await q(
        "INSERT INTO payments(user_id, plan, amount, status, reference, created_at) VALUES(?,?,?,?,?,?)",
        (user_id, plan, 199000, "paid", reference, int(time.time()))
    )

async def is_premium(user_row):
    return bool(user_row and user_row[5] in ("vip", "pro", "elite") and int(time.time()) < int(user_row[6] or 0))
