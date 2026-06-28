# ═══════════════════════════════════════════════════════════
# PART 2: DATABASE, AI ENGINE, EXCHANGE, TECHNICAL ANALYSIS
# ═══════════════════════════════════════════════════════════

# IMPORTS FOR PART 2
import os
import json
import time
import hmac
import hashlib
import asyncio
import logging
import traceback
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple
from collections import OrderedDict, deque

import aiosqlite
import aiohttp
import numpy as np
from groq import Groq, RateLimitError as GroqRateLimitError
from groq import APIStatusError as GroqAPIError, APIConnectionError as GroqConnectionError

# Import shared components from part1
from part1 import *

logger = logging.getLogger("OstadBot")

# ════════════════════════════════════════
# SECTION 10: DATABASE ENGINE (FULL)
# ════════════════════════════════════════

class DatabaseEngine:
    """
    High-performance async SQLite database manager.
    Implements WAL mode, connection pooling, and comprehensive schema.
    """
    
    SCHEMA_VERSION = 8
    
    FULL_SCHEMA = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        full_name TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        language TEXT DEFAULT 'fa',
        plan TEXT DEFAULT 'free',
        plan_until REAL DEFAULT 0,
        welcome_bonus INTEGER DEFAULT 0,
        risk_level TEXT DEFAULT 'medium',
        total_paid REAL DEFAULT 0,
        total_earnings REAL DEFAULT 0,
        referral_code TEXT DEFAULT '',
        referred_by INTEGER DEFAULT 0,
        total_referrals INTEGER DEFAULT 0,
        referral_earnings REAL DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0,
        notifications_enabled INTEGER DEFAULT 1,
        created_at REAL DEFAULT (strftime('%s', 'now')),
        last_active REAL DEFAULT (strftime('%s', 'now')),
        metadata TEXT DEFAULT '{}'
    );
    
    CREATE TABLE IF NOT EXISTS user_state (
        user_id INTEGER PRIMARY KEY,
        daily_ai_count INTEGER DEFAULT 0,
        total_ai_count INTEGER DEFAULT 0,
        daily_signal_count INTEGER DEFAULT 0,
        total_signal_count INTEGER DEFAULT 0,
        last_ai_at REAL DEFAULT 0,
        last_signal_at REAL DEFAULT 0,
        last_reset_day TEXT DEFAULT '',
        last_active_at REAL DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS watchlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        note TEXT DEFAULT '',
        target_price REAL DEFAULT 0,
        added_at REAL DEFAULT (strftime('%s', 'now')),
        UNIQUE(user_id, symbol)
    );
    
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        target_price REAL NOT NULL,
        alert_type TEXT DEFAULT 'above',
        note TEXT DEFAULT '',
        active INTEGER DEFAULT 1,
        triggered INTEGER DEFAULT 0,
        triggered_at REAL DEFAULT 0,
        notification_sent INTEGER DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        direction TEXT NOT NULL,
        entry_price REAL NOT NULL,
        stop_loss REAL NOT NULL,
        take_profit1 REAL,
        take_profit2 REAL,
        take_profit3 REAL,
        confidence REAL DEFAULT 0.5,
        timeframe TEXT DEFAULT '4h',
        analysis_type TEXT DEFAULT 'ai',
        status TEXT DEFAULT 'active',
        result TEXT DEFAULT '',
        profit_percent REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now')),
        closed_at REAL DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT DEFAULT 'card',
        status TEXT DEFAULT 'pending',
        receipt_file_id TEXT DEFAULT '',
        receipt_message_id INTEGER DEFAULT 0,
        admin_note TEXT DEFAULT '',
        transaction_id TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now')),
        processed_at REAL DEFAULT 0,
        processed_by INTEGER DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS ai_conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        context TEXT DEFAULT '',
        tokens_used INTEGER DEFAULT 0,
        model TEXT DEFAULT 'llama-3.3-70b',
        response_time REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        referred_id INTEGER NOT NULL,
        status TEXT DEFAULT 'active',
        earnings REAL DEFAULT 0,
        level INTEGER DEFAULT 1,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        wallet_address TEXT DEFAULT '',
        wallet_type TEXT DEFAULT 'USDT_TRC20',
        status TEXT DEFAULT 'pending',
        admin_note TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now')),
        processed_at REAL DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT DEFAULT '',
        updated_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type TEXT NOT NULL,
        task_data TEXT DEFAULT '{}',
        status TEXT DEFAULT 'pending',
        scheduled_at REAL DEFAULT 0,
        executed_at REAL DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 0,
        action TEXT NOT NULL,
        level TEXT DEFAULT 'INFO',
        details TEXT DEFAULT '',
        ip_address TEXT DEFAULT '',
        user_agent TEXT DEFAULT '',
        created_at REAL DEFAULT (strftime('%s', 'now'))
    );
    
    CREATE TABLE IF NOT EXISTS broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_text TEXT NOT NULL,
        target_plan TEXT DEFAULT 'all',
        status TEXT DEFAULT 'pending',
        sent_count INTEGER DEFAULT 0,
        total_count INTEGER DEFAULT 0,
        created_by INTEGER DEFAULT 0,
        created_at REAL DEFAULT (strftime('%s', 'now')),
        sent_at REAL DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS market_data_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        data_type TEXT NOT NULL,
        data_json TEXT NOT NULL,
        cached_at REAL DEFAULT (strftime('%s', 'now')),
        expires_at REAL DEFAULT 0
    );
    
    CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan);
    CREATE INDEX IF NOT EXISTS idx_users_referrer ON users(referred_by);
    CREATE INDEX IF NOT EXISTS idx_users_active ON users(last_active);
    CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(user_id, active);
    CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol, active);
    CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
    CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
    CREATE INDEX IF NOT EXISTS idx_signals_created ON signals(created_at);
    CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
    CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
    CREATE INDEX IF NOT EXISTS idx_payments_created ON payments(created_at);
    CREATE INDEX IF NOT EXISTS idx_logs_action ON logs(action);
    CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id);
    CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at);
    CREATE INDEX IF NOT EXISTS idx_ai_conv_user ON ai_conversations(user_id);
    CREATE INDEX IF NOT EXISTS idx_ai_conv_created ON ai_conversations(created_at);
    CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlists(user_id);
    CREATE INDEX IF NOT EXISTS idx_withdrawals_status ON withdrawals(status);
    CREATE INDEX IF NOT EXISTS idx_withdrawals_user ON withdrawals(user_id);
    CREATE INDEX IF NOT EXISTS idx_market_cache ON market_data_cache(symbol, data_type);
    """
    
def __init__(self, db_path: str = "ostadbot.db"):
    self.db_path = db_path          # ۸ فاصله
    self._write_lock = asyncio.Lock()  # ۸ فاصله
    self._connection_pool: List = []   # ۸ فاصله
    self._max_connections = 10          # ۸ فاصله
    self._query_count = 0               # ۸ فاصله
    self._error_count = 0               # ۸ فاصله

async def initialize(self) -> bool:
    """Initialize database with full schema and optimizations"""
    try:
        async with self._write_lock:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("PRAGMA journal_mode=WAL")
                await conn.execute("PRAGMA synchronous=NORMAL")
                await conn.execute("PRAGMA cache_size=-16000")
                await conn.execute("PRAGMA foreign_keys=ON")
                await conn.execute("PRAGMA busy_timeout=5000")
                await conn.execute("PRAGMA temp_store=MEMORY")
                await conn.execute("PRAGMA mmap_size=268435456")
                await conn.execute("PRAGMA page_size=4096")
                
                await conn.executescript(self.FULL_SCHEMA)
                
                await conn.commit()
        
        logger.info(f"Database initialized (v{self.SCHEMA_VERSION}): {self.db_path}")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

async def execute(self, query: str, params: tuple = ()) -> int:
    """Execute SQL and return lastrowid"""
    self._query_count += 1
    try:
        async with self._write_lock:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute(query, params)
                await conn.commit()
                return cursor.lastrowid
    except Exception as e:
        self._error_count += 1
        logger.error(f"SQL execute error: {e}\nQuery: {query[:200]}")
        raise
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute multiple SQL statements"""
        self._query_count += len(params_list)
        try:
            async with self._write_lock:
                async with aiosqlite.connect(self.db_path) as conn:
                    await conn.executemany(query, params_list)
                    await conn.commit()
                    return len(params_list)
        except Exception as e:
            self._error_count += 1
            logger.error(f"SQL executemany error: {e}")
            raise
    
    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row as dictionary"""
        self._query_count += 1
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(query, params) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            self._error_count += 1
            logger.error(f"SQL fetchone error: {e}")
            return None
    
    async def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows as list of dictionaries"""
        self._query_count += 1
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self._error_count += 1
            logger.error(f"SQL fetchall error: {e}")
            return []
    
    async def fetchval(self, query: str, params: tuple = (), default: Any = None) -> Any:
        """Fetch a single value"""
        row = await self.fetchone(query, params)
        return list(row.values())[0] if row else default
    
    async def count(self, table: str, where: str = "1=1", params: tuple = ()) -> int:
        """Count rows in a table"""
        return await self.fetchval(f"SELECT COUNT(*) FROM {table} WHERE {where}", params, 0)
    
    async def exists(self, table: str, where: str = "1=1", params: tuple = ()) -> bool:
        """Check if any rows exist"""
        return await self.count(table, where, params) > 0
    
    # ════════════════════════════════════════
    # USER OPERATIONS
    # ════════════════════════════════════════
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get complete user data"""
        return await self.fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))
    
    async def upsert_user(self, user_id: int, username: str = "", full_name: str = "") -> None:
        """Create or update user"""
        now = time.time()
        await self.execute("""
            INSERT INTO users(user_id, username, full_name, last_active)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(NULLIF(?, ''), users.username),
                full_name = COALESCE(NULLIF(?, ''), users.full_name),
                last_active = ?
        """, (user_id, username, full_name, now, username, full_name, now))
        await self.execute(
            "INSERT OR IGNORE INTO user_state(user_id, last_reset_day) VALUES(?, date('now'))",
            (user_id,)
        )
    
    async def get_user_plan(self, user_id: int) -> str:
        """Get effective user plan"""
        user = await self.get_user(user_id)
        if not user:
            return PlanType.FREE.value
        if user.get('is_banned'):
            return "banned"
        if user['plan'] in (PlanType.VIP.value, PlanType.PRO.value, PlanType.ELITE.value):
            if user.get('plan_until') and time.time() < user['plan_until']:
                return user['plan']
        return PlanType.FREE.value
    
    async def is_premium(self, user_id: int) -> bool:
        """Check if user has premium access"""
        plan = await self.get_user_plan(user_id)
        return plan not in (PlanType.FREE.value, "banned")
    
    async def set_user_plan(self, user_id: int, plan: str, days: int = 30) -> None:
        """Set user subscription plan"""
        plan_until = time.time() + (days * 86400)
        await self.execute(
            "UPDATE users SET plan = ?, plan_until = ? WHERE user_id = ?",
            (plan, plan_until, user_id)
        )
        await self.log(user_id, "plan_changed", f"Plan: {plan}, Days: {days}")
    
    async def get_ai_limit(self, user_id: int) -> int:
        """Get user's daily AI limit"""
        plan = await self.get_user_plan(user_id)
        plan_config = PLANS.get(plan, PLANS[PlanType.FREE.value])
        return plan_config.get("ai_daily_limit", FREE_DAILY_AI)
    
    async def get_ai_usage(self, user_id: int) -> int:
        """Get today's AI usage count"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        state = await self.fetchone("SELECT * FROM user_state WHERE user_id = ?", (user_id,))
        
        if not state:
            await self.execute(
                "INSERT OR IGNORE INTO user_state(user_id, last_reset_day) VALUES(?, ?)",
                (user_id, today)
            )
            return 0
        
        if state.get('last_reset_day') != today:
            await self.execute(
                "UPDATE user_state SET daily_ai_count = 0, last_reset_day = ? WHERE user_id = ?",
                (today, user_id)
            )
            return 0
        
        return state.get('daily_ai_count', 0)
    
    async def increment_ai_usage(self, user_id: int) -> int:
        """Increment AI usage counter"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        await self.execute("""
            UPDATE user_state SET
                daily_ai_count = daily_ai_count + 1,
                total_ai_count = total_ai_count + 1,
                last_ai_at = ?,
                last_reset_day = ?
            WHERE user_id = ?
        """, (time.time(), today, user_id))
        return await self.fetchval(
            "SELECT daily_ai_count FROM user_state WHERE user_id = ?",
            (user_id,), 0
        )
    
    async def can_use_ai(self, user_id: int) -> Tuple[bool, int, int]:
        """Check if user can use AI. Returns (can_use, used, limit)"""
        used = await self.get_ai_usage(user_id)
        limit = await self.get_ai_limit(user_id)
        return (used < limit, used, limit)
    
    # ════════════════════════════════════════
    # PAYMENT OPERATIONS
    # ════════════════════════════════════════
    
    async def create_payment(self, user_id: int, plan: str, amount: float, method: str = "card") -> int:
        """Create a new payment record"""
        return await self.execute(
            "INSERT INTO payments(user_id, plan, amount, payment_method) VALUES(?, ?, ?, ?)",
            (user_id, plan, amount, method)
        )
    
    async def approve_payment(self, payment_id: int, admin_id: int) -> bool:
        """Approve payment and activate user's plan"""
        payment = await self.fetchone(
            "SELECT * FROM payments WHERE id = ? AND status = 'pending'", (payment_id,)
        )
        if not payment:
            return False
        
        plan_config = PLANS.get(payment['plan'], PLANS[PlanType.VIP.value])
        days = plan_config.get('days', 30)
        
        await self.set_user_plan(payment['user_id'], payment['plan'], days)
        await self.execute(
            "UPDATE payments SET status = 'approved', processed_at = ?, processed_by = ? WHERE id = ?",
            (time.time(), admin_id, payment_id)
        )
        
        user = await self.get_user(payment['user_id'])
        if user and user.get('referred_by') and user['referred_by'] != 0:
            commission = payment['amount'] * (REFERRAL_COMMISSION_PERCENT / 100)
            await self.execute(
                "UPDATE users SET referral_earnings = referral_earnings + ?, total_earnings = total_earnings + ? WHERE user_id = ?",
                (commission, commission, user['referred_by'])
            )
            await self.execute(
                "UPDATE referrals SET earnings = earnings + ? WHERE referrer_id = ? AND referred_id = ?",
                (commission, user['referred_by'], payment['user_id'])
            )
        
        await self.log(payment['user_id'], "payment_approved", f"Payment ID: {payment_id}")
        return True
    
    async def reject_payment(self, payment_id: int, admin_id: int, reason: str = "") -> bool:
        """Reject a payment"""
        await self.execute(
            "UPDATE payments SET status = 'rejected', processed_at = ?, processed_by = ?, admin_note = ? WHERE id = ?",
            (time.time(), admin_id, reason, payment_id)
        )
        return True
    
    # ════════════════════════════════════════
# WATCHLIST OPERATIONS
# ════════════════════════════════════════

async def add_to_watchlist(self, user_id: int, symbol: str, note: str = "") -> bool:
    """Add symbol to user's watchlist"""
    max_items = 999 if await self.is_premium(user_id) else 5
    current = await self.count("watchlists", "user_id = ?", (user_id,))
    if current >= max_items:
        return False
    await self.execute(
        "INSERT OR IGNORE INTO watchlists(user_id, symbol, note) VALUES(?, ?, ?)",
        (user_id, symbol.upper(), note)
    )
    return True

async def remove_from_watchlist(self, user_id: int, symbol: str) -> bool:
    """Remove symbol from watchlist"""
    await self.execute(
        "DELETE FROM watchlists WHERE user_id = ? AND symbol = ?",
        (user_id, symbol.upper())
    )
    return True

async def get_watchlist(self, user_id: int) -> List[Dict]:
    """Get user's watchlist"""
    return await self.fetchall(
        "SELECT * FROM watchlists WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,)
    )
    
    # ════════════════════════════════════════
    # ALERT OPERATIONS
    # ════════════════════════════════════════
    
    async def create_alert(self, user_id: int, symbol: str, target_price: float, alert_type: str = "above") -> int:
        """Create a price alert"""
        return await self.execute(
            "INSERT INTO alerts(user_id, symbol, target_price, alert_type) VALUES(?, ?, ?, ?)",
            (user_id, symbol.upper(), target_price, alert_type)
        )
    
    async def get_active_alerts(self, user_id: int = None) -> List[Dict]:
        """Get active (untriggered) alerts"""
        if user_id:
            return await self.fetchall(
                "SELECT * FROM alerts WHERE user_id = ? AND active = 1 AND triggered = 0 ORDER BY created_at DESC",
                (user_id,)
            )
        return await self.fetchall(
            "SELECT * FROM alerts WHERE active = 1 AND triggered = 0"
        )
    
    async def trigger_alert(self, alert_id: int) -> None:
        """Mark alert as triggered"""
        await self.execute(
            "UPDATE alerts SET triggered = 1, triggered_at = ? WHERE id = ?",
            (time.time(), alert_id)
        )
    
    async def delete_alert(self, alert_id: int, user_id: int) -> bool:
        """Delete an alert"""
        await self.execute(
            "DELETE FROM alerts WHERE id = ? AND user_id = ?",
            (alert_id, user_id)
        )
        return True
    
    # ════════════════════════════════════════
    # SIGNAL OPERATIONS
    # ════════════════════════════════════════
    
    async def save_signal(self, symbol: str, direction: str, entry: float, stop_loss: float,
                         take_profits: List[float], confidence: float, timeframe: str = "4h") -> int:
        """Save a trading signal"""
        tp1 = take_profits[0] if len(take_profits) > 0 else None
        tp2 = take_profits[1] if len(take_profits) > 1 else None
        tp3 = take_profits[2] if len(take_profits) > 2 else None
        
        return await self.execute(
            """INSERT INTO signals(symbol, direction, entry_price, stop_loss, take_profit1, take_profit2, take_profit3, confidence, timeframe)
               VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (symbol, direction, entry, stop_loss, tp1, tp2, tp3, confidence, timeframe)
        )
    
    async def get_active_signals(self, symbol: str = None) -> List[Dict]:
        """Get active signals"""
        if symbol:
            return await self.fetchall(
                "SELECT * FROM signals WHERE status = 'active' AND symbol = ? ORDER BY created_at DESC",
                (symbol.upper(),)
            )
        return await self.fetchall(
            "SELECT * FROM signals WHERE status = 'active' ORDER BY created_at DESC"
        )
    
    async def close_signal(self, signal_id: int, result: str, profit_percent: float = 0) -> None:
        """Close a signal"""
        await self.execute(
            "UPDATE signals SET status = 'closed', result = ?, profit_percent = ?, closed_at = ? WHERE id = ?",
            (result, profit_percent, time.time(), signal_id)
        )
    
    # ════════════════════════════════════════
    # AI CONVERSATION OPERATIONS
    # ════════════════════════════════════════
    
    async def save_ai_conversation(self, user_id: int, question: str, answer: str,
                                  tokens: int = 0, response_time: float = 0) -> int:
        """Save AI conversation"""
        return await self.execute(
            "INSERT INTO ai_conversations(user_id, question, answer, tokens_used, response_time) VALUES(?, ?, ?, ?, ?)",
            (user_id, question[:500], answer[:2000], tokens, response_time)
        )
    
    async def get_user_ai_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's AI conversation history"""
        return await self.fetchall(
            "SELECT * FROM ai_conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
    
    # ════════════════════════════════════════
    # LOGGING
    # ════════════════════════════════════════
    
    async def log(self, user_id: int, action: str, details: str = "", level: str = "INFO") -> None:
        """Write to system log"""
        await self.execute(
            "INSERT INTO logs(user_id, action, level, details) VALUES(?, ?, ?, ?)",
            (user_id, action, level, details)
        )
    
        # ════════════════════════════════════════
    # ALERT OPERATIONS
    # ════════════════════════════════════════
    
    async def create_alert(self, user_id: int, symbol: str, target_price: float, alert_type: str = "above") -> int:
        """Create a price alert"""
        return await self.execute(
            "INSERT INTO alerts(user_id, symbol, target_price, alert_type) VALUES(?, ?, ?, ?)",
            (user_id, symbol.upper(), target_price, alert_type)
        )
    
    async def get_active_alerts(self, user_id: int = None) -> List[Dict]:
        """Get active (untriggered) alerts"""
        if user_id:
            return await self.fetchall(
                "SELECT * FROM alerts WHERE user_id = ? AND active = 1 AND triggered = 0 ORDER BY created_at DESC",
                (user_id,)
            )
        return await self.fetchall(
            "SELECT * FROM alerts WHERE active = 1 AND triggered = 0"
        )
    
    async def trigger_alert(self, alert_id: int) -> None:
        """Mark alert as triggered"""
        await self.execute(
            "UPDATE alerts SET triggered = 1, triggered_at = ? WHERE id = ?",
            (time.time(), alert_id)
        )
    
    async def delete_alert(self, alert_id: int, user_id: int) -> bool:
        """Delete an alert"""
        await self.execute(
            "DELETE FROM alerts WHERE id = ? AND user_id = ?",
            (alert_id, user_id)
        )
        return True
    
    # ════════════════════════════════════════
    # STATISTICS
    # ════════════════════════════════════════
    
    async def get_full_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        total_users = await self.count("users")
        premium_users = await self.count("users", "plan != 'free' AND plan_until > ?", (time.time(),))
        active_today = await self.count("users", "date(last_active, 'unixepoch') = date('now')")
        total_revenue = await self.fetchval(
            "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'approved'", default=0
        )
        pending_payments = await self.count("payments", "status = 'pending'")
        total_ai_queries = await self.fetchval(
            "SELECT COALESCE(SUM(total_ai_count), 0) FROM user_state", default=0
        )
        total_signals = await self.count("signals")
        active_signals = await self.count("signals", "status = 'active'")
        total_alerts = await self.count("alerts")
        active_alerts = await self.count("alerts", "active = 1 AND triggered = 0")
        
        return {
            "total_users": total_users,
            "premium_users": premium_users,
            "active_today": active_today,
            "total_revenue": total_revenue,
            "pending_payments": pending_payments,
            "total_ai_queries": total_ai_queries,
            "total_signals": total_signals,
            "active_signals": active_signals,
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "conversion_rate": round((premium_users / total_users * 100), 2) if total_users > 0 else 0,
            "timestamp": TT.format(TT.now(), "full"),
            "version": APP_VERSION
        }
    
    async def cleanup_old_logs(self, days: int = 30) -> int:
        """Delete logs older than specified days"""
        cutoff = time.time() - (days * 86400)
        await self.execute("DELETE FROM logs WHERE created_at < ?", (cutoff,))
        return await self.count("logs")
    
    async def cleanup_old_cache(self, hours: int = 24) -> int:
        async def cleanup_old_cache(self, hours: int = 24) -> int:
        """Delete expired market data cache"""
        cutoff = time.time() - (hours * 3600)
        await self.execute("DELETE FROM market_data_cache WHERE cached_at < ?", (cutoff,))
        return await self.count("market_data_cache")

# Initialize database
db = DatabaseEngine(DATABASE_PATH)

# ════════════════════════════════════════
# SECTION 11: GROQ AI ENGINE (ADVANCED)
# ════════════════════════════════════════

class GroqAIEngine:
    """
    Advanced Groq AI integration with:
    - Rate limiting & exponential backoff
    - Response caching with LRU eviction
    - Multiple system prompt templates
    - Token tracking and statistics
    - Comprehensive error recovery
    """
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or GROQ_API_KEY
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        
        self._request_times: deque = deque(maxlen=100)
        self._daily_tokens = 0
        self._daily_reset = ""
        self._response_cache: OrderedDict = OrderedDict()
        self._cache_max_size = 200
        self._total_requests = 0
        self._total_errors = 0
        
        self._system_prompts = self._build_system_prompts()
    
    def _build_system_prompts(self) -> Dict[str, str]:
        """Build comprehensive system prompts for different analysis types"""
        return {
            "default": """شما یک دستیار حرفه‌ای تحلیل بازار کریپتو به زبان فارسی هستید.

قوانین پاسخگویی:
۱. همیشه به فارسی روان و حرفه‌ای پاسخ بدهید
۲. از شکلک‌های مناسب استفاده کنید
۳. تحلیل دقیق، عملی و بدون حاشیه بدهید
۴. حد ضرر و حد سود را مشخص کنید
۵. ریسک‌ها را شفاف بیان کنید
۶. هرگز وعده سود قطعی ندهید
۷. همیشه یادآوری کنید که این تحلیل شخصی است
۸. از اعداد و ارقام دقیق استفاده کنید
۹. روند کلی بازار را در نظر بگیرید
۱۰. به اخبار و رویدادهای مهم اشاره کنید""",
            
            "technical": """شما یک تحلیلگر تکنیکال حرفه‌ای بازار کریپتو هستید.

تحلیل شما باید شامل:
۱. وضعیت RSI و تفسیر
۲. وضعیت MACD و سیگنال‌ها
۳. سطوح حمایت و مقاومت کلیدی
۴. سطوح فیبوناچی مهم
۵. الگوهای کندل استیک
۶. روند کلی بازار
۷. تحلیل حجم معاملات
۸. پیش‌بینی حرکت بعدی قیمت""",
            
            "signal": """شما یک سیگنال‌دهنده حرفه‌ای کریپتو هستید.

سیگنال باید شامل:
۱. جهت معامله (LONG/SHORT)
۲. قیمت ورود دقیق
۳. حد ضرر
۴. اهداف قیمتی (حداقل ۳ سطح)
۵. میزان اطمینان (درصد)
۶. نسبت ریسک به ریوارد
۷. تایم‌فریم پیشنهادی
۸. دلیل صدور سیگنال""",
            
            "risk": """شما یک مدیر ریسک حرفه‌ای هستید.

تحلیل ریسک باید شامل:
۱. میزان ریسک معامله
۲. حداکثر سرمایه پیشنهادی
۳. نسبت ریسک به ریوارد
۴. احتمال موفقیت
۵. عوامل تاثیرگذار
۶. توصیه‌های مدیریت سرمایه""",
        }
    
    def _get_cache_key(self, prompt: str, system_type: str) -> str:
        """Generate MD5 cache key"""
        content = f"{system_type}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_rate_limit(self) -> bool:
        """Check if within rate limits"""
        now = time.time()
        while self._request_times and now - self._request_times[0] >= 60:
            self._request_times.popleft()
        
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if today != self._daily_reset:
            self._daily_tokens = 0
            self._daily_reset = today
        
        return len(self._request_times) < GROQ_RPM_LIMIT and self._daily_tokens < GROQ_TPM_LIMIT
    
    async def ask(self, prompt: str, context: str = "", system_type: str = "default",
                 temperature: float = 0.3, max_tokens: int = 1024,
                 use_cache: bool = True) -> str:
        """Main AI query method with full error handling"""
        
        if not self.client:
            return f"{E.CROSS} کلید API هوش مصنوعی تنظیم نشده است."
        
        cache_key = self._get_cache_key(prompt, system_type)
        if use_cache and cache_key in self._response_cache:
            return self._response_cache[cache_key]
        
        if not self._check_rate_limit():
            await asyncio.sleep(2)
        
        system_prompt = self._system_prompts.get(system_type, self._system_prompts["default"])
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "system", "content": f"اطلاعات بازار:\n{context}"})
        messages.append({"role": "user", "content": prompt})
        
        self._total_requests += 1
        start_time = time.time()
        
        for attempt in range(3):
            try:
                loop = asyncio.get_running_loop()
                
                def sync_call():
                    return self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=0.9,
                    )
                
                response = await loop.run_in_executor(None, sync_call)
                
                self._request_times.append(time.time())
                if response.usage:
                    self._daily_tokens += response.usage.total_tokens
                
                answer = response.choices[0].message.content.strip()
                
                if use_cache:
                    if len(self._response_cache) >= self._cache_max_size:
                        self._response_cache.popitem(last=False)
                    self._response_cache[cache_key] = answer
                
                return answer
                
            except GroqRateLimitError:
                if attempt < 2:
                    await asyncio.sleep((attempt + 1) * 3)
                    continue
                return f"{E.WARNING} سیستم مشغول است. لطفاً چند ثانیه دیگر تلاش کنید."
                
            except (GroqAPIError, GroqConnectionError) as e:
                self._total_errors += 1
                if attempt < 2:
                    await asyncio.sleep(2)
                    continue
                logger.error(f"Groq API error: {e}")
                return f"{E.CROSS} خطا در ارتباط با سرور هوش مصنوعی."
                
            except Exception as e:
                self._total_errors += 1
                logger.error(f"Unexpected Groq error: {e}")
                return f"{E.CROSS} خطای غیرمنتظره."
        
        return f"{E.CROSS} پاسخی دریافت نشد."
    
    async def analyze_technically(self, symbol: str, market_data: str = "") -> str:
        """Get technical analysis for a symbol"""
        prompt = f"تحلیل تکنیکال کامل برای {symbol} با ذکر اندیکاتورها ارائه دهید."
        return await self.ask(prompt, market_data, "technical")
    
    async def generate_signal(self, symbol: str, market_data: str = "") -> str:
        """Generate trading signal"""
        prompt = f"سیگنال معاملاتی دقیق برای {symbol} صادر کنید."
        return await self.ask(prompt, market_data, "signal")
    
    async def assess_risk(self, trade_details: str) -> str:
        """Assess trade risk"""
        return await self.ask(trade_details, "", "risk")
    
    def clear_cache(self) -> None:
        """Clear the response cache"""
        self._response_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get AI engine statistics"""
        return {
            "provider": "Groq",
            "model": "llama-3.3-70b-versatile",
            "requests_minute": len(self._request_times),
            "tokens_today": self._daily_tokens,
            "cache_size": len(self._response_cache),
            "total_requests": self._total_requests,
            "total_errors": self._total_errors,
            "status": "active" if self.client else "inactive"
        }

# Initialize AI engine
ai = GroqAIEngine()

# ════════════════════════════════════════
# SECTION 12: COINEX EXCHANGE CLIENT
# ════════════════════════════════════════

class CoinExExchangeClient:
    """Advanced CoinEx exchange API client with caching"""
    
    BASE_URL = "https://api.coinex.com/v2"
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.api_key = api_key or cfg.get_str("COINEX_KEY")
        self.api_secret = api_secret or cfg.get_str("COINEX_SECRET")
        self._session: Optional[aiohttp.ClientSession] = None
        self._request_count: int = 0
        self._error_count: int = 0
        self._last_request_time: float = 0
        self._rate_limit_interval: float = 0.1
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl: int = 30
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            headers = {
                "User-Agent": f"OstadBot/{APP_VERSION}",
                "Accept": "application/json",
            }
            self._session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self._session
    
    async def _rate_limit(self):
        """Apply rate limiting"""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._rate_limit_interval:
            await asyncio.sleep(self._rate_limit_interval - elapsed)
        self._last_request_time = time.time()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make API request with caching"""
        await self._rate_limit()
        
        cache_key = f"{endpoint}:{json.dumps(params or {})}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached['time'] < self._cache_ttl:
                return cached['data']
        
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(2):
            try:
                session = await self._get_session()
                async with session.get(url, params=params) as response:
                    self._request_count += 1
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0:
                            self._cache[cache_key] = {'data': data, 'time': time.time()}
                            return data
                        return {"code": -1, "message": data.get("message", "Error")}
                    
                    if attempt < 1:
                        await asyncio.sleep(0.5)
                        continue
                    return {"code": -1, "message": f"HTTP {response.status}"}
                    
            except asyncio.TimeoutError:
                self._error_count += 1
                if attempt < 1:
                    continue
                return {"code": -1, "message": "Timeout"}
            except Exception as e:
                self._error_count += 1
                logger.error(f"CoinEx error: {e}")
                return {"code": -1, "message": str(e)}
        
        return {"code": -1, "message": "Max retries"}
    
    async def get_ticker(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Get ticker data"""
        result = await self._make_request("/spot/ticker", {"market": symbol.upper()})
        return result.get("data", {}) if result.get("code") == 0 else {}
    
    async def get_klines(self, symbol: str = "BTCUSDT", period: str = "1hour", limit: int = 100) -> List[Dict]:
        """Get kline/candlestick data"""
        result = await self._make_request("/spot/kline", {
            "market": symbol.upper(), "period": period, "limit": str(limit)
        })
        return result.get("data", []) if result.get("code") == 0 else []
    
    async def get_multiple_tickers(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get tickers for multiple symbols"""
        tasks = [self.get_ticker(sym) for sym in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        tickers = {}
        for sym, result in zip(symbols, results):
            if isinstance(result, dict) and result:
                tickers[sym] = result
        return tickers
    
    async def get_price(self, symbol: str) -> float:
        """Get current price"""
        ticker = await self.get_ticker(symbol)
        try:
            return float(ticker.get("last", 0))
        except:
            return 0.0
    
    async def get_24h_change(self, symbol: str) -> float:
        """Get 24h change percentage"""
        ticker = await self.get_ticker(symbol)
        try:
            return float(ticker.get("change_percentage", 0))
        except:
            return 0.0
    
    async def close(self) -> None:
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def get_stats(self) -> Dict:
        """Get client statistics"""
        return {
            "requests": self._request_count,
            "errors": self._error_count,
            "cache_size": len(self._cache),
            "active": self._session is not None and not self._session.closed
        }

# Initialize exchange
exchange = CoinExExchangeClient()

# ════════════════════════════════════════
# SECTION 13: TECHNICAL ANALYSIS ENGINE
# ════════════════════════════════════════

class TechnicalAnalysisEngine:
    """Comprehensive technical analysis calculator"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if NUMPY_AVAILABLE and prices and len(prices) >= period + 1:
            deltas = np.diff(prices)
            gains = np.maximum(deltas, 0)
            losses = np.maximum(-deltas, 0)
            avg_gain = np.mean(gains[:period])
            avg_loss = np.mean(losses[:period])
            if avg_loss == 0:
                return 100.0
            for i in range(period, len(deltas)):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss > 0 else 0
            return float(np.clip(100 - 100 / (1 + rs), 0, 100))
        return 50.0
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """Calculate MACD"""
        if not prices or len(prices) < slow + signal:
            return (0.0, 0.0, 0.0)
        
        def ema(data: List[float], period: int) -> float:
            if len(data) < period:
                return sum(data) / len(data) if data else 0
            multiplier = 2 / (period + 1)
            ema_val = sum(data[:period]) / period
            for price in data[period:]:
                ema_val = (price - ema_val) * multiplier + ema_val
            return ema_val
        
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        macd_line = ema_fast - ema_slow
        
        macd_values = []
        for i in range(slow - 1, len(prices)):
            fast_val = ema(prices[:i+1], fast)
            slow_val = ema(prices[:i+1], slow)
            macd_values.append(fast_val - slow_val)
        
        signal_line = ema(macd_values, signal) if len(macd_values) >= signal else macd_line * 0.9
        histogram = macd_line - signal_line
        
        return (float(macd_line), float(signal_line), float(histogram))
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        if NUMPY_AVAILABLE and prices and len(prices) >= period:
            recent = np.array(prices[-period:])
            middle = float(np.mean(recent))
            std = float(np.std(recent))
            return (middle + std * std_dev, middle, middle - std * std_dev)
        return (0.0, 0.0, 0.0)
    
    @staticmethod
    def calculate_moving_averages(prices: List[float]) -> Dict[str, float]:
        """Calculate various moving averages"""
        if not prices:
            return {}
        
        def sma(data: List[float], period: int) -> float:
            if len(data) < period:
                return sum(data) / len(data) if data else 0
            return sum(data[-period:]) / period
        
        return {
            "MA5": sma(prices, 5), "MA10": sma(prices, 10),
            "MA20": sma(prices, 20), "MA50": sma(prices, 50),
            "MA100": sma(prices, 100), "MA200": sma(prices, 200),
        }
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], window: int = 20) -> Tuple[float, float]:
        """Calculate support and resistance"""
        if not prices or len(prices) < window:
            return (min(prices) if prices else 0, max(prices) if prices else 0)
        recent = prices[-window:]
        return (float(min(recent)), float(max(recent)))
    
    @staticmethod
    def calculate_fibonacci(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci levels"""
        diff = high - low
        levels = {
            "0%": 0, "23.6%": 0.236, "38.2%": 0.382,
            "50%": 0.5, "61.8%": 0.618, "78.6%": 0.786,
            "100%": 1.0, "127.2%": 1.272, "161.8%": 1.618,
        }
        if diff > 0:
            return {name: low + (diff * ratio) for name, ratio in levels.items()}
        return {name: high - (abs(diff) * ratio) for name, ratio in levels.items()}
    
    @staticmethod
    def detect_trend(prices: List[float], short: int = 10, long: int = 30) -> str:
        """Detect market trend"""
        if NUMPY_AVAILABLE and prices and len(prices) >= long:
            short_ma = np.mean(prices[-short:])
            long_ma = np.mean(prices[-long:])
            diff = ((short_ma - long_ma) / long_ma) * 100
            if diff > 3: return "صعودی قوی 🟢🟢"
            if diff > 1: return "صعودی 🟢"
            if diff > -1: return "خنثی ⚪"
            if diff > -3: return "نزولی 🔴"
            return "نزولی قوی 🔴🔴"
        return "خنثی ⚪"
    
    @staticmethod
    def analyze_volume(volumes: List[float], prices: List[float]) -> Dict[str, Any]:
        """Analyze trading volume"""
        if not volumes or len(volumes) < 20:
            return {"avg": 0, "ratio": 1, "trend": "نرمال", "signal": "خنثی"}
        
        if NUMPY_AVAILABLE:
            avg = float(np.mean(volumes[-20:]))
            current = volumes[-1]
            ratio = current / avg if avg > 0 else 1
            
            if ratio > 2:
                signal = "خرید قوی 🔥🔥🔥" if prices and prices[-1] > prices[-2] else "فروش قوی 🔥🔥🔥"
                trend = "حجم بسیار بالا"
            elif ratio > 1.5:
                signal, trend = "فعال 🔥", "حجم بالا"
            elif ratio < 0.5:
                signal, trend = "نوسان کم 💤", "حجم پایین"
            else:
                signal, trend = "خنثی 📊", "حجم نرمال"
            
            return {"avg": avg, "ratio": round(ratio, 2), "trend": trend, "signal": signal}
        
        return {"avg": 0, "ratio": 1, "trend": "نرمال", "signal": "خنثی"}
    
    @staticmethod
    def market_structure(highs: List[float], lows: List[float]) -> Dict[str, str]:
        """Analyze market structure"""
        if len(highs) < 4 or len(lows) < 4:
            return {"structure": "نامشخص", "bias": "خنثی"}
        
        lh, ph = highs[-1], highs[-3]
        ll, pl = lows[-1], lows[-3]
        
        if lh > ph and ll > pl:
            return {"structure": "HH + HL", "bias": "صعودی 🟢"}
        elif lh < ph and ll < pl:
            return {"structure": "LH + LL", "bias": "نزولی 🔴"}
        elif lh > ph and ll < pl:
            return {"structure": "HH + LL", "bias": "احتمال شکست ⚡"}
        return {"structure": "مختلط", "bias": "خنثی ⚪"}

# Initialize analyzer
ta = TechnicalAnalysisEngine()

# ════════════════════════════════════════
# END OF PART 2 - CONTINUE TO PART 3
# ════════════════════════════════════════
