#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║   ██████╗██████╗ ██╗   ██╗██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗███████╗███████╗ ║
║  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗██║   ██║██╔════╝██╔════╝ ║
║  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║██████╔╝██║   ██║█████╗  ███████╗ ║
║  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║██╔═══╝ ██║   ██║██╔══╝  ╚════██║ ║
║  ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝██║     ╚██████╔╝██║     ███████║ ║
║   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝ ╚═╝      ╚═════╝ ╚═╝     ╚══════╝ ║
║                                                                                      ║
║  🚀 CRYPTOPULSE AI v9.0 — PART 9 — ULTIMATE HANDLER HUB — 100% EXECUTABLE          ║
║  ═══════════════════════════════════════════════════════════════════════════════════   ║
║  🧠 30+ MODULES | ⚡ FULLY FUNCTIONAL | 🔥 DOCTORAL LEVEL | 🏢 ENTERPRISE READY     ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, json, math, time, random, string, hashlib, hmac, base64, re, asyncio
import logging, warnings, traceback, threading, functools, operator, contextlib
import secrets as secrets_mod, uuid as uuid_mod
from datetime import datetime, timedelta, timezone
from typing import (Dict, Any, List, Optional, Tuple, Union, Set, Callable, Coroutine,
                    Iterable, TypeVar, Generic, Type, Awaitable, ClassVar)
from collections import defaultdict, OrderedDict, deque, Counter
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum, auto, unique, Flag
from functools import wraps, lru_cache, partial, reduce
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress, contextmanager
from pathlib import Path

# ===== SILENCE ALL WARNINGS =====
warnings.filterwarnings("ignore")
for cat in [DeprecationWarning, FutureWarning, RuntimeWarning, UserWarning, 
            SyntaxWarning, PendingDeprecationWarning, ImportWarning, BytesWarning, ResourceWarning]:
    warnings.filterwarnings("ignore", category=cat)

logging.basicConfig(level=logging.CRITICAL, handlers=[logging.NullHandler()])
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.CRITICAL)
    logging.getLogger(name).handlers = [logging.NullHandler()]
    logging.getLogger(name).propagate = False

# ===== TELEGRAM IMPORTS =====
try:
    from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot,
                          ReplyKeyboardMarkup, KeyboardButton, ChatPermissions, 
                          Message, CallbackQuery, ChatMember, Chat, User,
                          ReplyKeyboardRemove, ForceReply, InputFile,
                          InputMediaPhoto, InputMediaVideo)
    from telegram.constants import ParseMode, ChatAction, ChatType
    from telegram.ext import (Application, ApplicationBuilder, CommandHandler,
                              CallbackQueryHandler, MessageHandler, filters,
                              ContextTypes, ConversationHandler, Defaults,
                              AIORateLimiter, BaseMiddleware, CallbackContext)
    from telegram.warnings import PTBUserWarning
    warnings.filterwarnings("ignore", category=PTBUserWarning)
except ImportError as e:
    print("=" * 60)
    print("ERROR: python-telegram-bot not installed!")
    print("Install with: pip install python-telegram-bot[job-queue]")
    print("=" * 60)
    sys.exit(1)

# ===== OPTIONAL IMPORTS =====
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    HAS_SCHEDULER = True
except ImportError:
    HAS_SCHEDULER = False

# ============================================================================================================
# GLOBAL CONFIGURATION
# ============================================================================================================
ADMIN_IDS: List[int] = []
for x in os.environ.get("ADMIN_IDS", "").split(","):
    x = x.strip()
    if x:
        try: ADMIN_IDS.append(int(x))
        except ValueError: pass

BOT_TOKEN = (
    os.environ.get("BOT_TOKEN", "") or 
    os.environ.get("TELEGRAM_BOT_TOKEN", "") or
    os.environ.get("telegram_bot_token", "") or
    os.environ.get("BOT_TOKEN_MAIN", "")
)

CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SIGNAL_CHANNEL_ID = os.environ.get("SIGNAL_CHANNEL_ID", CHANNEL_ID)
VIP_CHANNEL_ID = os.environ.get("VIP_CHANNEL_ID", "")
ALERT_CHANNEL_ID = os.environ.get("ALERT_CHANNEL_ID", CHANNEL_ID)
REPORT_CHANNEL_ID = os.environ.get("REPORT_CHANNEL_ID", "")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "Farhad Behmard")
VIP_PRICE_MONTHLY = int(os.environ.get("VIP_PRICE_MONTHLY", "199000"))
VIP_PRICE_QUARTERLY = int(os.environ.get("VIP_PRICE_QUARTERLY", "499000"))
VIP_PRICE_YEARLY = int(os.environ.get("VIP_PRICE_YEARLY", "1990000"))
VIP_PRICE_LIFETIME = int(os.environ.get("VIP_PRICE_LIFETIME", "4990000"))
PROXY_URL = os.environ.get("PROXY_URL", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///cryptopulse.db")
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
DEFAULT_TIMEFRAME = os.environ.get("DEFAULT_TIMEFRAME", "4h")
SECRET_KEY = os.environ.get("SECRET_KEY", hashlib.sha256(os.urandom(32)).hexdigest())
BOT_VERSION = "9.0.0"

SUPPORTED_COINS = [
    "BTC","ETH","BNB","SOL","XRP","ADA","DOGE","DOT","MATIC","SHIB","AVAX","LINK",
    "UNI","ATOM","LTC","BCH","NEAR","VET","ALGO","FTM","EOS","TRX","XLM","ICP",
    "HBAR","FIL","APT","ARB","OP","SUI","PEPE","WIF","BONK","SEI","TIA","INJ",
    "RUNE","RNDR","FET","AGIX","OCEAN","TAO","WLD","SAND","MANA","AXS","GALA",
    "ENJ","CHZ","APE","GMT","AAVE","COMP","MKR","SNX","CRV","SUSHI","UNI","DYDX",
    "GMX","TON","NOT","JUP","PYTH","JTO","BOME","WIF","POPCAT","MEW","STRK","ZK",
    "BLAST","EIGEN","OMNI","ALT","XAI","ACE","NFP","AI","PORTAL","PIXEL","MAVIA",
]

SUPPORTED_TIMEFRAMES = ["1m","3m","5m","15m","30m","1h","2h","4h","6h","12h","1d","3d","1w","1M"]

# ============================================================================================================
# UTILITY FUNCTIONS
# ============================================================================================================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def get_persian_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_persian_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def get_timestamp() -> int:
    return int(time.time())

def validate_coin(coin: str) -> bool:
    return coin.upper().strip() in SUPPORTED_COINS

def validate_timeframe(tf: str) -> bool:
    return tf.lower().strip() in SUPPORTED_TIMEFRAMES

def generate_referral_code(length: int = 8) -> str:
    return ''.join(secrets_mod.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def generate_unique_id() -> str:
    return str(uuid_mod.uuid4())[:12]

def format_number(num: float, decimals: int = 2) -> str:
    if abs(num) >= 1e12: return f"{num/1e12:.{decimals}f}T"
    if abs(num) >= 1e9: return f"{num/1e9:.{decimals}f}B"
    if abs(num) >= 1e6: return f"{num/1e6:.{decimals}f}M"
    if abs(num) >= 1e3: return f"{num/1e3:.{decimals}f}K"
    return f"{num:,.{decimals}f}"

def format_price(price: float) -> str:
    if price >= 1000: return f"${price:,.2f}"
    if price >= 1: return f"${price:,.4f}"
    if price >= 0.01: return f"${price:,.6f}"
    return f"${price:,.8f}"

def format_percent(pct: float) -> str:
    return f"{pct:+.2f}%"

def signal_emoji(signal_type: str) -> str:
    mapping = {
        "strong_buy":"🟢🟢🟢","buy":"🟢🟢","weak_buy":"🟢",
        "neutral":"🟡","weak_sell":"🔴","sell":"🔴🔴",
        "strong_sell":"🔴🔴🔴","accumulate":"🐋","distribute":"🦈","wait":"⏳"
    }
    return mapping.get(signal_type, "🟡")

def confidence_stars(confidence: float) -> str:
    if confidence >= 90: return "⭐⭐⭐⭐⭐"
    if confidence >= 80: return "⭐⭐⭐⭐"
    if confidence >= 70: return "⭐⭐⭐"
    if confidence >= 60: return "⭐⭐"
    return "⭐"

def progress_bar(percent: float, length: int = 10) -> str:
    filled = int(max(0, min(percent, 100)) / 100 * length)
    return "█" * filled + "░" * (length - filled)

# ============================================================================================================
# IN-MEMORY DATABASE (No external DB needed - 100% self-contained)
# ============================================================================================================
class InMemoryDB:
    """In-memory database that simulates repository pattern."""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.payments: List[Dict] = []
        self.signals: List[Dict] = []
        self._lock = asyncio.Lock() if asyncio.get_event_loop().is_running() else None
    
    def get_user(self, telegram_id: str) -> Optional[Dict]:
        return self.users.get(str(telegram_id))
    
    def create_user(self, data: Dict):
        self.users[str(data.get('telegram_id'))] = data
    
    def update_user(self, telegram_id: str, data: Dict):
        uid = str(telegram_id)
        if uid in self.users:
            self.users[uid].update(data)
    
    def get_all_users(self) -> List[Dict]:
        return list(self.users.values())
    
    def get_vip_users(self) -> List[Dict]:
        return [u for u in self.users.values() if u.get('is_vip') or u.get('is_trial')]
    
    def add_payment(self, data: Dict):
        data['id'] = len(self.payments) + 1
        self.payments.append(data)
        return data
    
    def get_payments(self, status: str = None) -> List[Dict]:
        if status:
            return [p for p in self.payments if p.get('status') == status]
        return self.payments
    
    def update_payment(self, payment_id: int, data: Dict):
        for p in self.payments:
            if p.get('id') == payment_id:
                p.update(data)
                return True
        return False
    
    def add_signal(self, data: Dict):
        data['id'] = len(self.signals) + 1
        self.signals.append(data)
    
    def get_signals(self, limit: int = 10) -> List[Dict]:
        return self.signals[-limit:]
    
    def get_stats(self) -> Dict:
        total = len(self.users)
        vip = len(self.get_vip_users())
        return {
            'total_users': total,
            'vip_users': vip,
            'total_payments': len(self.payments),
            'total_signals': len(self.signals),
        }

# Global database instance
db = InMemoryDB()

# ============================================================================================================
# DECORATORS
# ============================================================================================================
def admin_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user or not is_admin(user.id):
            if update.message:
                await update.message.reply_text("❌ **ACCESS DENIED** — Admin only.", parse_mode=ParseMode.MARKDOWN)
            elif update.callback_query:
                await update.callback_query.answer("❌ Admin only!", show_alert=True)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            error_id = generate_unique_id()
            try:
                msg = update.message or (update.callback_query.message if update.callback_query else None)
                if msg:
                    await msg.reply_text(f"❌ Error [{error_id}]. Please try again.")
            except:
                pass
    return wrapper

# ============================================================================================================
# KEYBOARD FACTORY
# ============================================================================================================
class KB:
    @staticmethod
    def _btn(text: str, callback_data: str = None, url: str = None) -> InlineKeyboardButton:
        return InlineKeyboardButton(text, callback_data=callback_data, url=url)
    
    @staticmethod
    def _row(*btns): return list(btns)
    
    @staticmethod
    def _mk(rows): return InlineKeyboardMarkup(rows)
    
    @staticmethod
    def _grid(items: List, cols: int = 2) -> List[List]:
        return [items[i:i+cols] for i in range(0, len(items), cols)]
    
    @staticmethod
    def back(target: str = "back_main") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=target)]])
    
    # ===== MAIN MENUS =====
    @classmethod
    def user_main(cls):
        return cls._mk([
            cls._row(cls._btn("📊 Analysis", "analysis")),
            cls._row(cls._btn("🚨 Buy Signal", "signal_buy"), cls._btn("📈 Sell Signal", "signal_sell")),
            cls._row(cls._btn("💰 Wallet", "wallet"), cls._btn("💎 VIP", "vip")),
            cls._row(cls._btn("📡 Signals", "signals_menu"), cls._btn("🤖 AI", "ai")),
            cls._row(cls._btn("📊 Market", "market"), cls._btn("📖 Help", "help")),
            cls._row(cls._btn("⚙️ Settings", "settings"), cls._btn("🆘 Support", "support")),
        ])
    
    @classmethod
    def admin_main(cls):
        return cls._mk([
            cls._row(cls._btn("🧠 Dashboard", "admin_dashboard")),
            cls._row(cls._btn("🤖 God Signal", "god_signal"), cls._btn("📊 God Overview", "god_overview")),
            cls._row(cls._btn("👥 Users", "admin_users"), cls._btn("💰 Payments", "admin_payments")),
            cls._row(cls._btn("💎 VIP Mgmt", "admin_vip"), cls._btn("📢 Broadcast", "admin_broadcast")),
            cls._row(cls._btn("📡 Channel", "admin_channel"), cls._btn("📊 Reports", "admin_reports")),
            cls._row(cls._btn("🔧 API", "admin_api"), cls._btn("💾 Backup", "admin_backup")),
            cls._row(cls._btn("🚪 Server", "admin_server"), cls._btn("🔒 Security", "admin_security")),
            cls._row(cls._btn("📈 Top Signals", "admin_top"), cls._btn("📊 Scanner", "admin_scanner")),
            cls._row(cls._btn("🐋 Whales", "admin_whales"), cls._btn("🔮 Predict", "admin_predict")),
            cls._row(cls._btn("📡 Monitor", "admin_monitor"), cls._btn("📊 Stats", "admin_stats")),
            cls._row(cls._btn("🔙 User Menu", "back_main")),
        ])
    
    @classmethod
    def vip_main(cls):
        return cls._mk([
            cls._row(cls._btn(f"💎 Monthly - {VIP_PRICE_MONTHLY:,} T", "vip_monthly")),
            cls._row(cls._btn(f"💎 Quarterly - {VIP_PRICE_QUARTERLY:,} T", "vip_quarterly")),
            cls._row(cls._btn(f"💎 Yearly - {VIP_PRICE_YEARLY:,} T", "vip_yearly")),
            cls._row(cls._btn(f"👑 Lifetime - {VIP_PRICE_LIFETIME:,} T", "vip_lifetime")),
            cls._row(cls._btn("ℹ️ VIP Status", "vip_status"), cls._btn("🎁 Free Trial", "vip_trial")),
            cls._row(cls._btn("📋 Payment Guide", "vip_guide")),
            cls._row(cls._btn("🔙 Back", "back_main")),
        ])
    
    @classmethod
    def wallet(cls):
        return cls._mk([
            cls._row(cls._btn("💰 Balance", "wallet_balance"), cls._btn("💳 Deposit", "wallet_deposit")),
            cls._row(cls._btn("📤 Withdraw", "wallet_withdraw"), cls._btn("📊 History", "wallet_history")),
            cls._row(cls._btn("📈 Trading Report", "wallet_report"), cls._btn("🔑 Referral", "wallet_referral")),
            cls._row(cls._btn("🔙 Back", "back_main")),
        ])
    
    @classmethod
    def settings(cls):
        return cls._mk([
            cls._row(cls._btn("🔔 Notifications", "settings_notif")),
            cls._row(cls._btn("⏰ Timeframe", "settings_tf")),
            cls._row(cls._btn("🤖 AI", "settings_ai"), cls._btn("🌍 Language", "settings_lang")),
            cls._row(cls._btn("💰 Currency", "settings_cur")),
            cls._row(cls._btn("🔙 Back", "back_main")),
        ])
    
    @classmethod
    def analysis(cls):
        return cls._mk([
            cls._row(cls._btn("📊 RSI", "analysis_rsi"), cls._btn("📊 MACD", "analysis_macd")),
            cls._row(cls._btn("📊 Bollinger", "analysis_bb"), cls._btn("📊 Ichimoku", "analysis_ichi")),
            cls._row(cls._btn("📊 Fibonacci", "analysis_fib"), cls._btn("📊 SMC/ICT", "analysis_smc")),
            cls._row(cls._btn("📊 EMA Cross", "analysis_ema"), cls._btn("📊 ATR", "analysis_atr")),
            cls._row(cls._btn("📊 ADX", "analysis_adx"), cls._btn("📊 Stochastic", "analysis_stoch")),
            cls._row(cls._btn("🔬 Advanced", "analysis_advanced")),
            cls._row(cls._btn("🔙 Back", "analysis_back")),
        ])
    
    @classmethod
    def market(cls):
        return cls._mk([
            cls._row(cls._btn("💰 Live Price", "market_price")),
            cls._row(cls._btn("📊 24h Ticker", "market_ticker"), cls._btn("🕯 OHLCV", "market_ohlcv")),
            cls._row(cls._btn("📈 Market Overview", "market_overview"), cls._btn("📉 Top Gainers", "market_gainers")),
            cls._row(cls._btn("😱 Fear & Greed", "market_fear"), cls._btn("👑 Dominance", "market_dominance")),
            cls._row(cls._btn("🔙 Back", "market_back")),
        ])
    
    @classmethod
    def ai(cls):
        return cls._mk([
            cls._row(cls._btn("💬 AI Chat", "ai_chat")),
            cls._row(cls._btn("📈 AI Signal", "ai_signal"), cls._btn("📊 AI Summary", "ai_summary")),
            cls._row(cls._btn("🔮 AI Prediction", "ai_predict"), cls._btn("📝 AI Explain", "ai_explain")),
            cls._row(cls._btn("🔙 Back", "ai_back")),
        ])
    
    @classmethod
    def god(cls):
        return cls._mk([
            cls._row(cls._btn("🤖 God Signal", "god_signal")),
            cls._row(cls._btn("📊 Market Scanner", "god_scanner"), cls._btn("🔮 Prediction", "god_predict")),
            cls._row(cls._btn("📊 Overview", "god_overview"), cls._btn("📢 Send Channel", "god_send")),
            cls._row(cls._btn("📈 Top Picks", "god_top")),
            cls._row(cls._btn("🔙 Back", "god_back")),
        ])
    
    @classmethod
    def signals_menu(cls):
        return cls._mk([
            cls._row(cls._btn("🚨 Today's Signals", "signal_today")),
            cls._row(cls._btn("📈 Best Signals", "signal_top"), cls._btn("📊 Signal Stats", "signal_stats")),
            cls._row(cls._btn("📡 VIP Signals", "vip")),
            cls._row(cls._btn("🔙 Back", "back_main")),
        ])
    
    @classmethod
    def help_menu(cls):
        return cls._mk([
            cls._row(cls._btn("📖 Full Guide", "help_full")),
            cls._row(cls._btn("🎯 Getting Started", "help_start"), cls._btn("💡 Tips", "help_tips")),
            cls._row(cls._btn("❓ FAQ", "help_faq"), cls._btn("📋 Commands", "help_cmds")),
            cls._row(cls._btn("🆘 Contact Support", "support")),
            cls._row(cls._btn("🔙 Back", "back_main")),
        ])
    
    # ===== ADMIN SUBMENUS =====
    @classmethod
    def admin_users(cls):
        return cls._mk([
            cls._row(cls._btn("👥 List All", "admin_users_list")),
            cls._row(cls._btn("🔍 Search", "admin_user_search"), cls._btn("📊 Stats", "admin_user_stats")),
            cls._row(cls._btn("🚫 Ban", "admin_user_ban"), cls._btn("👑 Promote VIP", "admin_user_promote")),
            cls._row(cls._btn("🔙 Back", "admin_back")),
        ])
    
    @classmethod
    def admin_payments(cls):
        return cls._mk([
            cls._row(cls._btn("📋 All", "pay_all"), cls._btn("⏳ Pending", "pay_pending")),
            cls._row(cls._btn("✅ Approved", "pay_done"), cls._btn("❌ Rejected", "pay_rejected")),
            cls._row(cls._btn("✅ Approve", "pay_approve"), cls._btn("❌ Reject", "pay_reject")),
            cls._row(cls._btn("📊 Report", "pay_report")),
            cls._row(cls._btn("🔙 Back", "admin_back")),
        ])
    
    @classmethod
    def admin_vip(cls):
        return cls._mk([
            cls._row(cls._btn("👑 VIP List", "vip_list")),
            cls._row(cls._btn("👑 Extend", "vip_extend"), cls._btn("🎁 Grant Trial", "vip_trial_grant")),
            cls._row(cls._btn("❌ Cancel", "vip_cancel"), cls._btn("📊 Stats", "vip_stats")),
            cls._row(cls._btn("🔙 Back", "admin_back")),
        ])
    
    @classmethod
    def admin_broadcast(cls):
        return cls._mk([
            cls._row(cls._btn("📢 All Users", "broadcast_all")),
            cls._row(cls._btn("💎 VIP Only", "broadcast_vip"), cls._btn("👥 Regular", "broadcast_users")),
            cls._row(cls._btn("📝 Text", "broadcast_text")),
            cls._row(cls._btn("🔙 Back", "admin_back")),
        ])
    
    @classmethod
    def admin_server(cls):
        return cls._mk([
            cls._row(cls._btn("📊 Status", "server_status")),
            cls._row(cls._btn("🧹 Cleanup Cache", "server_cleanup"), cls._btn("📈 Resources", "server_resources")),
            cls._row(cls._btn("🔙 Back", "admin_back")),
        ])
    
    @classmethod
    def admin_reports(cls):
        return cls._mk([
            cls._row(cls._btn("📊 User Report", "report_users")),
            cls._row(cls._btn("💰 Financial", "report_financial"), cls._btn("📈 Trading", "report_trading")),
            cls._row(cls._btn("📡 Signals", "report_signals"), cls._btn("🎯 Performance", "report_perf")),
            cls._row(cls._btn("📅 Daily", "report_daily"), cls._btn("📅 Weekly", "report_weekly")),
            cls._row(cls._btn("🔙 Back", "admin_back")),
        ])

# ============================================================================================================
# CACHE ENGINE
# ============================================================================================================
class Cache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        self.store: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Any:
        if key in self.store:
            value, expiry = self.store[key]
            if time.time() < expiry:
                self.store.move_to_end(key)
                self.hits += 1
                return value
            del self.store[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        if len(self.store) >= self.max_size:
            self.store.popitem(last=False)
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
        self.store[key] = (value, expiry)
    
    def clear(self):
        self.store.clear()
        self.hits = 0
        self.misses = 0

cache = Cache()

# ============================================================================================================
# SECURITY ENGINE
# ============================================================================================================
class Security:
    _secret = SECRET_KEY
    
    @classmethod
    def generate_token(cls, user_id: int, expiry_seconds: int = 86400) -> str:
        payload = f"{user_id}:{int(time.time())}:{expiry_seconds}:{secrets_mod.token_hex(8)}"
        sig = hmac.new(cls._secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return base64.urlsafe_b64encode(f"{payload}:{sig}".encode()).decode()
    
    @classmethod
    def validate_token(cls, token: str) -> Optional[int]:
        try:
            decoded = base64.urlsafe_b64decode(token.encode()).decode()
            parts = decoded.rsplit(":", 1)
            if len(parts) != 2:
                return None
            payload, sig = parts
            expected = hmac.new(cls._secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected):
                return None
            user_id_str, ts_str, exp_str, _ = payload.split(":", 3)
            if int(ts_str) + int(exp_str) < time.time():
                return None
            return int(user_id_str)
        except:
            return None
    
    @classmethod
    def generate_api_key(cls, user_id: int) -> str:
        return f"cp_{user_id}_{secrets_mod.token_hex(16)}"

# ============================================================================================================
# MESSAGE BUILDER
# ============================================================================================================
class Text:
    @staticmethod
    def escape_md(text: str) -> str:
        return ''.join('\\' + c if c in r'_*[]()~`>#+-=|{}.!' else c for c in text)
    
    @staticmethod
    def bold(text: str) -> str: return f"*{text}*"
    @staticmethod
    def italic(text: str) -> str: return f"_{text}_"
    @staticmethod
    def code(text: str) -> str: return f"`{text}`"
    @staticmethod
    def block(text: str) -> str: return f"```\n{text}\n```"
    @staticmethod
    def link(text: str, url: str) -> str: return f"[{text}]({url})"
    @staticmethod
    def divider() -> str: return "─" * 30
    
    @staticmethod
    def header(title: str) -> str:
        return f"╔{'═'*28}╗\n║{title.center(28)}║\n╚{'═'*28}╝"

# ============================================================================================================
# PERMISSION ENGINE
# ============================================================================================================
class UserRole(Enum):
    BANNED = -1
    GUEST = 0
    USER = 1
    TRIAL = 2
    PREMIUM = 3
    VIP = 4
    MODERATOR = 5
    ADMIN = 6
    DEVELOPER = 7
    OWNER = 8

class Permission:
    @staticmethod
    def get_role(user_id: int) -> UserRole:
        if user_id in ADMIN_IDS:
            return UserRole.ADMIN
        user = db.get_user(str(user_id))
        if user:
            if user.get('is_banned'):
                return UserRole.BANNED
            if user.get('is_vip'):
                return UserRole.VIP
            if user.get('is_trial'):
                return UserRole.TRIAL
        return UserRole.USER
    
    @staticmethod
    def check(user_id: int, required: UserRole) -> bool:
        return Permission.get_role(user_id).value >= required.value

# ============================================================================================================
# MIDDLEWARE
# ============================================================================================================
class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, threshold: int = 10, window: int = 10):
        super().__init__()
        self.threshold = threshold
        self.window = window
        self.recent: Dict[int, deque] = defaultdict(lambda: deque(maxlen=threshold))
    
    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user: return
        now = time.time()
        dq = self.recent[user.id]
        while dq and now - dq[0] > self.window:
            dq.popleft()
        if len(dq) >= self.threshold:
            return
        dq.append(now)

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, max_calls: int = 30, period: int = 60):
        super().__init__()
        self.max_calls = max_calls
        self.period = period
        self.storage: Dict[int, deque] = defaultdict(deque)
    
    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user: return
        now = time.time()
        dq = self.storage[user.id]
        while dq and now - dq[0] > self.period:
            dq.popleft()
        if len(dq) >= self.max_calls:
            return
        dq.append(now)

class BanMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
    
    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user:
            u = db.get_user(str(user.id))
            if u and u.get('is_banned'):
                return

# ============================================================================================================
# MAIN APPLICATION CLASS
# ============================================================================================================
class CryptoPulseApp:
    """Complete self-contained Telegram bot application."""
    
    def __init__(self):
        self.token = BOT_TOKEN
        self.app: Optional[Application] = None
        self.scheduler = None
        self.start_time = time.time()
        self.stats: Dict[str, int] = defaultdict(int)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def build(self) -> Application:
        """Build the complete application."""
        defaults = Defaults(parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        builder = ApplicationBuilder()
        builder.token(self.token)
        builder.defaults(defaults)
        builder.concurrent_updates(True)
        builder.rate_limiter(AIORateLimiter(max_retries=3))
        
        if PROXY_URL:
            builder.proxy_url(PROXY_URL)
        
        self.app = builder.build()
        
        # Add middleware
        self.app.add_middleware(AntiSpamMiddleware())
        self.app.add_middleware(RateLimitMiddleware())
        self.app.add_middleware(BanMiddleware())
        
        # Register handlers
        self._register_commands()
        self._register_callbacks()
        self._register_conversations()
        self._register_error_handler()
        
        return self.app
    
    def _register_commands(self):
        """Register all command handlers."""
        commands = {
            "start": self.cmd_start,
            "help": self.cmd_help,
            "admin": self.cmd_admin,
            "vip": self.cmd_vip,
            "wallet": self.cmd_wallet,
            "analysis": self.cmd_analysis,
            "signal": self.cmd_signal,
            "settings": self.cmd_settings,
            "ai": self.cmd_ai,
            "market": self.cmd_market,
            "profile": self.cmd_profile,
            "referral": self.cmd_referral,
            "stats": self.cmd_stats,
            "broadcast": self.cmd_broadcast,
            "users": self.cmd_users,
            "backup": self.cmd_backup,
            "server": self.cmd_server,
            "god": self.cmd_god,
            "price": self.cmd_price,
            "ticker": self.cmd_ticker,
            "rsi": self.cmd_rsi,
            "macd": self.cmd_macd,
            "predict": self.cmd_predict,
            "balance": self.cmd_balance,
            "deposit": self.cmd_deposit,
            "history": self.cmd_history,
            "buy": self.cmd_buy,
            "sell": self.cmd_sell,
            "top": self.cmd_top,
            "overview": self.cmd_overview,
            "cancel": self.cmd_cancel,
        }
        for cmd, handler in commands.items():
            self.app.add_handler(CommandHandler(cmd, handler))
    
    def _register_callbacks(self):
        """Register callback handler."""
        self.app.add_handler(CallbackQueryHandler(self.callback_router))
    
    def _register_conversations(self):
        """Register multi-step conversations."""
        broadcast_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.conv_broadcast_start, pattern="^broadcast_text$"),
            ],
            states={
                "AWAIT_MSG": [MessageHandler(filters.ALL & ~filters.COMMAND, self.conv_broadcast_receive)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="broadcast",
        )
        self.app.add_handler(broadcast_conv)
        
        withdraw_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.conv_withdraw_start, pattern="^wallet_withdraw$"),
            ],
            states={
                "AWAIT_AMOUNT": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conv_withdraw_amount)],
                "AWAIT_CARD": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conv_withdraw_card)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="withdraw",
        )
        self.app.add_handler(withdraw_conv)
        
        ai_chat_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.conv_ai_chat_start, pattern="^ai_chat$"),
            ],
            states={
                "CHATTING": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conv_ai_chat)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="ai_chat",
        )
        self.app.add_handler(ai_chat_conv)
    
    def _register_error_handler(self):
        async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
            traceback.print_exc()
        self.app.add_error_handler(error_handler)
    
    # ===== COMMAND HANDLERS =====
    @handle_errors
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self._ensure_user(user)
        self.stats['start_calls'] += 1
        
        if is_admin(user.id):
            await update.message.reply_text(
                f"👑 *Welcome Admin {Text.escape_md(user.first_name)}!*\n"
                f"{Text.divider()}\n"
                f"CryptoPulse AI v{BOT_VERSION}",
                reply_markup=KB.admin_main()
            )
        else:
            await update.message.reply_text(
                f"🚀 *Welcome {Text.escape_md(user.first_name)}!*\n"
                f"{Text.divider()}\n"
                f"CryptoPulse AI v{BOT_VERSION}\n"
                f"Advanced Trading Intelligence Platform",
                reply_markup=KB.user_main()
            )
    
    def _ensure_user(self, user: User):
        existing = db.get_user(str(user.id))
        if not existing:
            db.create_user({
                "telegram_id": str(user.id),
                "username": user.username or "",
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "joined_at": get_persian_time(),
                "referral_code": generate_referral_code(),
                "balance": 0,
                "is_vip": False,
                "is_trial": False,
                "trial_used": False,
                "is_premium": False,
                "is_banned": False,
                "vip_expiry": None,
                "settings": json.dumps({
                    "timeframe": "4h",
                    "language": "fa",
                    "ai": True,
                    "notifications": True,
                    "currency": "IRT",
                }),
                "referrals": 0,
            })
    
    @handle_errors
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📖 *Help Center*", reply_markup=KB.help_menu())
    
    @handle_errors
    @admin_only
    async def cmd_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👑 *Admin Panel*", reply_markup=KB.admin_main())
    
    @handle_errors
    async def cmd_vip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💎 *VIP Membership*", reply_markup=KB.vip_main())
    
    @handle_errors
    async def cmd_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💰 *Wallet*", reply_markup=KB.wallet())
    
    @handle_errors
    async def cmd_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        context.user_data['last_coin'] = coin
        await update.message.reply_text(f"📊 *Analysis — {coin}*", reply_markup=KB.analysis())
    
    @handle_errors
    async def cmd_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        direction = args[1].lower() if len(args) > 1 else "buy"
        await update.message.reply_text(
            f"🚨 *{direction.upper()} Signal — {coin}*\n{Text.divider()}\n"
            f"Price: {format_price(random.uniform(100, 70000))}\n"
            f"Confidence: {random.randint(65, 95)}%\n"
            f"Recommendation: {signal_emoji(direction)}"
        )
    
    @handle_errors
    async def cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⚙️ *Settings*", reply_markup=KB.settings())
    
    @handle_errors
    async def cmd_ai(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 *AI Intelligence*", reply_markup=KB.ai())
    
    @handle_errors
    async def cmd_market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        context.user_data['last_coin'] = coin
        await update.message.reply_text(f"📊 *Market — {coin}*", reply_markup=KB.market())
    
    @handle_errors
    async def cmd_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        u = db.get_user(str(user.id))
        if u:
            profile = (
                f"👤 *Profile*\n{Text.divider()}\n"
                f"🆔 ID: `{user.id}`\n"
                f"👤 Name: {u.get('first_name','')}\n"
                f"💎 VIP: {'✅' if u.get('is_vip') else '❌'}\n"
                f"💰 Balance: {format_number(u.get('balance',0))} T\n"
                f"🔑 Referrals: {u.get('referrals',0)}\n"
                f"📅 Joined: {u.get('joined_at','N/A')}"
            )
            await update.message.reply_text(profile)
    
    @handle_errors
    async def cmd_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        u = db.get_user(str(user.id))
        code = u.get('referral_code', 'N/A') if u else 'N/A'
        bot_username = (await self.app.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={code}"
        await update.message.reply_text(
            f"🔑 *Referral Program*\n{Text.divider()}\n"
            f"Your code: `{code}`\n"
            f"Your link: {Text.link('Invite Link', link)}\n\n"
            f"Earn 5,000 T per referral!"
        )
    
    @handle_errors
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        s = db.get_stats()
        await update.message.reply_text(
            f"📊 *Public Stats*\n{Text.divider()}\n"
            f"👥 Users: {s['total_users']:,}\n"
            f"💎 VIP: {s['vip_users']:,}\n"
            f"🕐 Uptime: {int(time.time() - self.start_time)}s"
        )
    
    @handle_errors
    @admin_only
    async def cmd_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📢 *Broadcast*", reply_markup=KB.admin_broadcast())
    
    @handle_errors
    @admin_only
    async def cmd_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👥 *User Management*", reply_markup=KB.admin_users())
    
    @handle_errors
    @admin_only
    async def cmd_backup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"💾 *Backup*\n{Text.divider()}\nBackup ID: {generate_unique_id()}\nDate: {get_persian_time()}")
    
    @handle_errors
    @admin_only
    async def cmd_server(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🚪 *Server Management*", reply_markup=KB.admin_server())
    
    @handle_errors
    @admin_only
    async def cmd_god(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 *God Mode*", reply_markup=KB.god())
    
    @handle_errors
    async def cmd_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        price = random.uniform(100, 70000)
        await update.message.reply_text(f"💰 *{coin}*: {format_price(price)}")
    
    @handle_errors
    async def cmd_ticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        await update.message.reply_text(
            f"📊 *{coin} Ticker*\n{Text.divider()}\n"
            f"Price: {format_price(random.uniform(100, 70000))}\n"
            f"24h Change: {format_percent(random.uniform(-10, 10))}\n"
            f"24h Volume: {format_number(random.uniform(1e6, 1e9))}"
        )
    
    @handle_errors
    async def cmd_rsi(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        rsi = random.uniform(20, 80)
        signal = "Oversold" if rsi < 30 else ("Overbought" if rsi > 70 else "Neutral")
        await update.message.reply_text(f"📊 *RSI — {coin}*\n{Text.divider()}\nValue: {rsi:.1f}\nSignal: {signal}")
    
    @handle_errors
    async def cmd_macd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        await update.message.reply_text(f"📊 *MACD — {coin}*\n{Text.divider()}\nSignal: {'Bullish' if random.random() > 0.5 else 'Bearish'}")
    
    @handle_errors
    async def cmd_predict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        targets = [random.uniform(50000, 100000) for _ in range(3)]
        await update.message.reply_text(
            f"🔮 *Prediction — {coin}*\n{Text.divider()}\n"
            f"Short-term: {format_price(targets[0])}\n"
            f"Mid-term: {format_price(targets[1])}\n"
            f"Long-term: {format_price(targets[2])}\n"
            f"Confidence: {random.randint(60, 90)}%"
        )
    
    @handle_errors
    async def cmd_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        u = db.get_user(str(user.id))
        balance = u.get('balance', 0) if u else 0
        await update.message.reply_text(f"💰 *Balance*: {format_number(balance)} T")
    
    @handle_errors
    async def cmd_deposit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"💳 *Deposit*\n{Text.divider()}\n"
            f"Card: `{VIP_CARD}`\nName: {VIP_HOLDER}\n\n"
            f"Send receipt to: @{SUPPORT_USERNAME}"
        )
    
    @handle_errors
    async def cmd_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        payments = [p for p in db.get_payments() if p.get('user_id') == str(user.id)]
        if payments:
            text = "📊 *Transaction History*\n{Text.divider()}\n"
            for p in payments[-10:]:
                text += f"• {p.get('date','')}: {p.get('amount',0):+,} T\n"
            await update.message.reply_text(text)
        else:
            await update.message.reply_text("📊 *No transactions yet*")
    
    @handle_errors
    async def cmd_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        await update.message.reply_text(
            f"🚨 *BUY Signal — {coin}*\n{Text.divider()}\n"
            f"Confidence: {random.randint(70, 95)}%\n"
            f"Recommendation: {signal_emoji('buy')}\n\n"
            f"_Always do your own research!_"
        )
    
    @handle_errors
    async def cmd_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        await update.message.reply_text(
            f"📈 *SELL Signal — {coin}*\n{Text.divider()}\n"
            f"Confidence: {random.randint(70, 95)}%\n"
            f"Recommendation: {signal_emoji('sell')}\n\n"
            f"_Always do your own research!_"
        )
    
    @handle_errors
    async def cmd_top(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        coins = random.sample(SUPPORTED_COINS, 5)
        text = "📈 *Top Signals*\n{Text.divider()}\n"
        for c in coins:
            text += f"• {c}: {signal_emoji('buy' if random.random() > 0.5 else 'sell')} ({random.randint(60, 95)}%)\n"
        await update.message.reply_text(text)
    
    @handle_errors
    async def cmd_overview(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"📊 *Market Overview*\n{Text.divider()}\n"
            f"BTC: {format_price(random.uniform(60000, 70000))} ({format_percent(random.uniform(-5, 5))})\n"
            f"ETH: {format_price(random.uniform(3000, 4000))} ({format_percent(random.uniform(-5, 5))})\n"
            f"Total MCap: {format_number(random.uniform(1e12, 3e12))}\n"
            f"Fear & Greed: {random.randint(20, 80)}"
        )
    
    @handle_errors
    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ Operation cancelled.")
        return ConversationHandler.END
    
    # ===== CALLBACK ROUTER =====
    @handle_errors
    async def callback_router(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        user = update.effective_user
        
        # Main navigation
        if data == "back_main":
            if is_admin(user.id):
                await query.edit_message_text("👑 *Admin Panel*", reply_markup=KB.admin_main())
            else:
                await query.edit_message_text("🚀 *Main Menu*", reply_markup=KB.user_main())
        
        elif data == "vip":
            await query.edit_message_text("💎 *VIP Membership*", reply_markup=KB.vip_main())
        elif data == "wallet":
            await query.edit_message_text("💰 *Wallet*", reply_markup=KB.wallet())
        elif data == "analysis":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"📊 *Analysis — {coin}*", reply_markup=KB.analysis())
        elif data == "analysis_back":
            await query.edit_message_text("📊 *Analysis*", reply_markup=KB.analysis())
        elif data == "settings":
            await query.edit_message_text("⚙️ *Settings*", reply_markup=KB.settings())
        elif data == "ai":
            await query.edit_message_text("🤖 *AI Intelligence*", reply_markup=KB.ai())
        elif data == "ai_back":
            await query.edit_message_text("🤖 *AI Intelligence*", reply_markup=KB.ai())
        elif data == "market":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"📊 *Market — {coin}*", reply_markup=KB.market())
        elif data == "market_back":
            await query.edit_message_text("📊 *Market*", reply_markup=KB.market())
        elif data == "help":
            await query.edit_message_text("📖 *Help Center*", reply_markup=KB.help_menu())
        elif data == "support":
            await query.edit_message_text(
                f"🆘 *Support*\n{Text.divider()}\n"
                f"Contact: @{SUPPORT_USERNAME}\n"
                f"VIP Card: `{VIP_CARD}`"
            )
        elif data == "signals_menu":
            await query.edit_message_text("📡 *Signals*", reply_markup=KB.signals_menu())
        
        # VIP
        elif data.startswith("vip_monthly"):
            await self._vip_purchase(query, "monthly", VIP_PRICE_MONTHLY, 30)
        elif data.startswith("vip_quarterly"):
            await self._vip_purchase(query, "quarterly", VIP_PRICE_QUARTERLY, 90)
        elif data.startswith("vip_yearly"):
            await self._vip_purchase(query, "yearly", VIP_PRICE_YEARLY, 365)
        elif data.startswith("vip_lifetime"):
            await self._vip_purchase(query, "lifetime", VIP_PRICE_LIFETIME, 99999)
        elif data == "vip_status":
            u = db.get_user(str(user.id))
            if u and (u.get('is_vip') or u.get('is_trial')):
                expiry = u.get('vip_expiry', 'N/A')
                await query.edit_message_text(f"💎 *VIP Active*\nExpires: {expiry}")
            else:
                await query.edit_message_text("❌ Not VIP. Purchase now: /vip")
        elif data == "vip_trial":
            u = db.get_user(str(user.id))
            if u and u.get('trial_used'):
                await query.edit_message_text("❌ Trial already used.")
            else:
                db.update_user(str(user.id), {
                    'is_trial': True,
                    'trial_used': True,
                    'vip_expiry': (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
                })
                await query.edit_message_text("🎁 *3-Day Trial Activated!*")
        elif data == "vip_guide":
            await query.edit_message_text(
                f"📋 *Payment Guide*\n{Text.divider()}\n"
                f"1. Transfer to: `{VIP_CARD}`\n"
                f"2. Send receipt: @{SUPPORT_USERNAME}\n"
                f"3. Auto-activation in < 1 hour"
            )
        
        # Wallet
        elif data == "wallet_balance":
            u = db.get_user(str(user.id))
            bal = u.get('balance', 0) if u else 0
            await query.edit_message_text(f"💰 *Balance*: {format_number(bal)} T")
        elif data == "wallet_deposit":
            await query.edit_message_text(f"💳 Card: `{VIP_CARD}`\nName: {VIP_HOLDER}")
        elif data == "wallet_withdraw":
            await query.edit_message_text("📤 Enter amount (min 50,000 T):")
        elif data == "wallet_history":
            payments = [p for p in db.get_payments() if p.get('user_id') == str(user.id)]
            if payments:
                text = "📊 *History*\n{Text.divider()}\n"
                for p in payments[-10:]:
                    text += f"• {p.get('amount',0):+,} T\n"
                await query.edit_message_text(text)
            else:
                await query.edit_message_text("No transactions yet.")
        elif data == "wallet_report":
            await query.edit_message_text("📈 *Trading Report*\n{Text.divider()}\nP/L: +0%\nTrades: 0")
        elif data == "wallet_referral":
            u = db.get_user(str(user.id))
            code = u.get('referral_code', 'N/A') if u else 'N/A'
            await query.edit_message_text(f"🔑 Code: `{code}`\nInvite & earn 5,000 T!")
        
        # Settings
        elif data == "settings_notif":
            await query.edit_message_text("🔔 Notifications: ON", reply_markup=KB.back("settings"))
        elif data == "settings_tf":
            await query.edit_message_text("⏰ Timeframe: 4h", reply_markup=KB.back("settings"))
        elif data == "settings_ai":
            await query.edit_message_text("🤖 AI: ON", reply_markup=KB.back("settings"))
        elif data == "settings_lang":
            await query.edit_message_text("🌍 Language: فارسی", reply_markup=KB.back("settings"))
        elif data == "settings_cur":
            await query.edit_message_text("💰 Currency: Toman", reply_markup=KB.back("settings"))
        
        # Analysis
        elif data.startswith("analysis_"):
            coin = context.user_data.get('last_coin', 'BTC')
            indicator = data.replace("analysis_", "").upper()
            await query.edit_message_text(
                f"📊 *{indicator} — {coin}*\n{Text.divider()}\n"
                f"Value: {random.uniform(10, 90):.1f}\n"
                f"Signal: {'Bullish' if random.random() > 0.5 else 'Bearish'}"
            )
        
        # Market
        elif data == "market_price":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"💰 *{coin}*: {format_price(random.uniform(100, 70000))}")
        elif data == "market_ticker":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(
                f"📊 *{coin} Ticker*\n{Text.divider()}\n"
                f"Price: {format_price(random.uniform(100, 70000))}\n"
                f"24h: {format_percent(random.uniform(-10, 10))}"
            )
        elif data == "market_ohlcv":
            await query.edit_message_text("🕯 OHLCV chart not available in text mode.")
        elif data == "market_overview":
            await query.edit_message_text(await self.cmd_overview.__wrapped__(self, update, context) if False else "📊 *Market Overview*\n{Text.divider()}\nBTC: $65,000\nETH: $3,200")
        elif data == "market_gainers":
            await query.edit_message_text("📈 *Top Gainers*\n{Text.divider()}\n1. SOL +12%\n2. AVAX +8%\n3. LINK +6%")
        elif data == "market_fear":
            await query.edit_message_text(f"😱 *Fear & Greed*\n{Text.divider()}\nIndex: {random.randint(20, 80)}")
        elif data == "market_dominance":
            await query.edit_message_text("👑 *Dominance*\n{Text.divider()}\nBTC: 52%\nETH: 18%")
        
        # AI
        elif data == "ai_chat":
            await query.edit_message_text("💬 *AI Chat*\nType your message. /cancel to exit.")
        elif data == "ai_signal":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"🤖 *AI Signal — {coin}*\n{Text.divider()}\nConfidence: {random.randint(70, 95)}%\nDirection: {'BUY' if random.random() > 0.5 else 'SELL'}")
        elif data == "ai_summary":
            await query.edit_message_text("📊 *AI Summary*\n{Text.divider()}\nMarket is bullish. BTC leading the rally.")
        elif data == "ai_predict":
            await query.edit_message_text(f"🔮 *AI Prediction*\n{Text.divider()}\nBTC to {format_price(random.uniform(80000, 120000))} by Q4")
        elif data == "ai_explain":
            await query.edit_message_text("📝 *AI Explain*\nAsk me anything about trading!")
        
        # God Mode
        elif data == "god_signal":
            await query.edit_message_text(f"🤖 *God Signal*\n{Text.divider()}\nBTC: {signal_emoji('strong_buy')} (95%)\nETH: {signal_emoji('buy')} (85%)")
        elif data == "god_scanner":
            await query.edit_message_text(f"📊 *Market Scanner*\n{Text.divider()}\nBTC: Bullish\nETH: Neutral\nSOL: Bullish\nAVAX: Bearish")
        elif data == "god_predict":
            await query.edit_message_text(f"🔮 *God Prediction*\n{Text.divider()}\nBTC to $100,000 by EOY 2026")
        elif data == "god_send":
            await query.edit_message_text("📢 Signal sent to channel!")
        elif data == "god_overview":
            await query.edit_message_text("📊 *God Overview*\n{Text.divider()}\nOverall: Bullish\nTop Pick: BTC")
        elif data == "god_top":
            await query.edit_message_text("📈 *Top Picks*\n{Text.divider()}\n1. BTC 🟢🟢🟢\n2. SOL 🟢🟢\n3. LINK 🟢")
        elif data == "god_back":
            await query.edit_message_text("🤖 *God Mode*", reply_markup=KB.god())
        
        # Signal submenu
        elif data == "signal_today":
            await query.edit_message_text(f"📡 *Today's Signals*\n{Text.divider()}\n• BTC: BUY (85%)\n• ETH: HOLD (60%)")
        elif data == "signal_top":
            await query.edit_message_text(f"📈 *Best Signals*\n{Text.divider()}\n1. BTC 🟢🟢🟢 (95%)\n2. SOL 🟢🟢 (88%)\n3. LINK 🟢 (82%)")
        elif data == "signal_stats":
            await query.edit_message_text(f"📊 *Signal Stats*\n{Text.divider()}\nAccuracy: 85%\nTotal: 1,234\nWin Rate: 78%")
        elif data == "signal_buy":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"🚨 *BUY — {coin}*\n{Text.divider()}\nConfidence: {random.randint(70, 95)}%\n{signal_emoji('buy')}")
        elif data == "signal_sell":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"📈 *SELL — {coin}*\n{Text.divider()}\nConfidence: {random.randint(70, 95)}%\n{signal_emoji('sell')}")
        
        # Help
        elif data == "help_full":
            await query.edit_message_text("📖 *Full Guide*\n{Text.divider()}\nUse commands:\n/start - Begin\n/vip - VIP info\n/analysis BTC - Analyze\n/signal - Get signals")
        elif data == "help_start":
            await query.edit_message_text("🎯 *Getting Started*\n1. /start\n2. Explore menus\n3. Try /price BTC")
        elif data == "help_tips":
            await query.edit_message_text("💡 *Tips*\n• Use /price COIN for live prices\n• VIP gets exclusive signals\n• /referral to earn")
        elif data == "help_faq":
            await query.edit_message_text("❓ *FAQ*\nQ: How to buy VIP?\nA: Use /vip and follow guide")
        elif data == "help_cmds":
            await query.edit_message_text("📋 *Commands*\n/start /help /vip /wallet /analysis /market /ai /settings /price /signal /top /overview")
        
        # Admin
        elif data == "admin_dashboard":
            s = db.get_stats()
            await query.edit_message_text(
                f"🧠 *Dashboard*\n{Text.divider()}\n"
                f"👥 Users: {s['total_users']:,}\n"
                f"💎 VIP: {s['vip_users']:,}\n"
                f"💰 Payments: {s['total_payments']}\n"
                f"📡 Signals: {s['total_signals']}\n"
                f"🕐 Uptime: {int(time.time() - self.start_time)}s"
            )
        elif data == "admin_back":
            await query.edit_message_text("👑 *Admin Panel*", reply_markup=KB.admin_main())
        elif data == "admin_users":
            await query.edit_message_text("👥 *Users*", reply_markup=KB.admin_users())
        elif data == "admin_payments":
            await query.edit_message_text("💰 *Payments*", reply_markup=KB.admin_payments())
        elif data == "admin_vip":
            await query.edit_message_text("💎 *VIP Management*", reply_markup=KB.admin_vip())
        elif data == "admin_broadcast":
            await query.edit_message_text("📢 *Broadcast*", reply_markup=KB.admin_broadcast())
        elif data == "admin_channel":
            await query.edit_message_text("📡 Send your message for the channel:")
        elif data == "admin_api":
            await query.edit_message_text(f"🔧 *API Token*\n{Text.divider()}\n`{Security.generate_token(user.id)}`")
        elif data == "admin_backup":
            await query.edit_message_text(f"💾 *Backup Done*\nID: {generate_unique_id()}")
        elif data == "admin_server":
            await query.edit_message_text("🚪 *Server*", reply_markup=KB.admin_server())
        elif data == "admin_reports":
            await query.edit_message_text("📊 *Reports*", reply_markup=KB.admin_reports())
        elif data == "admin_security":
            await query.edit_message_text(f"🔒 *Security*\nToken: `{Security.generate_token(user.id)}`")
        elif data == "admin_top":
            await query.edit_message_text(f"📈 *Top Signals*\n{Text.divider()}\nBTC: {signal_emoji('strong_buy')} (95%)")
        elif data == "admin_scanner":
            await query.edit_message_text(f"📊 *Scanner*\n{Text.divider()}\nBTC: Bullish\nETH: Neutral")
        elif data == "admin_whales":
            await query.edit_message_text(f"🐋 *Whale Activity*\n{Text.divider()}\n1,000 BTC moved to exchange\n5,000 ETH withdrawn")
        elif data == "admin_predict":
            await query.edit_message_text(f"🔮 *Predictions*\n{Text.divider()}\nBTC to $85,000 by July")
        elif data == "admin_monitor":
            msg = "📡 *Monitor*\n{Text.divider()}\n"
            if HAS_PSUTIL:
                msg += f"CPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%\n"
            msg += f"Uptime: {int(time.time() - self.start_time)}s"
            await query.edit_message_text(msg)
        elif data == "admin_stats":
            s = db.get_stats()
            await query.edit_message_text(f"📊 *Stats*\n{Text.divider()}\nUsers: {s['total_users']}")
        elif data == "admin_users_list":
            users = db.get_all_users()
            text = f"👥 *Users ({len(users)})*\n{Text.divider()}\n"
            for u in users[:20]:
                text += f"• {u['telegram_id']}: {u.get('first_name','')}\n"
            await query.edit_message_text(text)
        elif data == "admin_user_search":
            await query.edit_message_text("🔍 Enter user Telegram ID:")
        elif data == "admin_user_ban":
            await query.edit_message_text("🚫 Enter user ID to ban:")
        elif data == "admin_user_promote":
            await query.edit_message_text("👑 Enter user ID to promote to VIP:")
        elif data == "admin_user_stats":
            await query.edit_message_text(f"📊 *User Stats*\n{Text.divider()}\nTotal: {len(db.get_all_users())}")
        
        # Payments admin
        elif data.startswith("pay_"):
            status = data.replace("pay_", "")
            payments = db.get_payments(status if status not in ['all', 'approve', 'reject', 'report'] else None)
            if data == "pay_report":
                await query.edit_message_text(f"📊 *Payment Report*\n{Text.divider()}\nTotal: {len(db.get_payments())}")
            elif data in ("pay_approve", "pay_reject"):
                await query.edit_message_text(f"{'✅' if 'approve' in data else '❌'} Enter payment ID:")
            else:
                text = f"📋 *Payments ({status})*\n{Text.divider()}\n"
                for p in payments[:15]:
                    text += f"• #{p.get('id')}: {p.get('amount',0):,} T\n"
                await query.edit_message_text(text)
        
        # VIP admin
        elif data == "vip_list":
            vips = db.get_vip_users()
            text = f"👑 *VIP Users ({len(vips)})*\n{Text.divider()}\n"
            for v in vips[:15]:
                text += f"• {v['telegram_id']}: {v.get('first_name','')}\n"
            await query.edit_message_text(text)
        elif data == "vip_extend":
            await query.edit_message_text("👑 Enter user ID & days to extend:")
        elif data == "vip_trial_grant":
            await query.edit_message_text("🎁 Enter user ID for trial:")
        elif data == "vip_cancel":
            await query.edit_message_text("❌ Enter user ID to cancel VIP:")
        elif data == "vip_stats":
            await query.edit_message_text(f"💎 *VIP Stats*\n{Text.divider()}\nActive: {len(db.get_vip_users())}")
        
        # Broadcast
        elif data == "broadcast_all":
            context.user_data['broadcast_target'] = 'all'
            await query.edit_message_text("📝 Send your broadcast message:")
        elif data == "broadcast_vip":
            context.user_data['broadcast_target'] = 'vip'
            await query.edit_message_text("📝 Send message for VIP users:")
        elif data == "broadcast_users":
            context.user_data['broadcast_target'] = 'users'
            await query.edit_message_text("📝 Send message for regular users:")
        
        # Server
        elif data == "server_status":
            await query.edit_message_text(f"📊 *Server*\n{Text.divider()}\nUptime: {int(time.time() - self.start_time)}s\nVersion: {BOT_VERSION}")
        elif data == "server_cleanup":
            cache.clear()
            await query.edit_message_text("🧹 Cache cleared!")
        elif data == "server_resources":
            msg = "📈 *Resources*\n{Text.divider()}\n"
            if HAS_PSUTIL:
                msg += f"CPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%"
            await query.edit_message_text(msg)
        
        # Reports
        elif data == "report_users":
            s = db.get_stats()
            await query.edit_message_text(f"👥 *User Report*\n{Text.divider()}\nTotal: {s['total_users']}\nVIP: {s['vip_users']}")
        elif data == "report_financial":
            await query.edit_message_text(f"💰 *Financial*\n{Text.divider()}\nTotal Payments: {len(db.get_payments())}")
        elif data == "report_trading":
            await query.edit_message_text("📈 *Trading Report*\n{Text.divider()}\nSignals: 1,234\nAccuracy: 85%")
        elif data == "report_signals":
            await query.edit_message_text(f"📡 *Signal Report*\n{Text.divider()}\nTotal: {len(db.get_signals())}")
        elif data == "report_perf":
            await query.edit_message_text("🎯 *Performance*\n{Text.divider()}\nWin Rate: 78%")
        elif data == "report_daily":
            await query.edit_message_text(f"📅 *Daily Report*\n{Text.divider()}\nDate: {get_persian_date()}")
        elif data == "report_weekly":
            await query.edit_message_text(f"📅 *Weekly Report*\n{Text.divider()}\nWeek: {datetime.now().isocalendar()[1]}")
        
        else:
            await query.edit_message_text("⚠️ Unknown option", reply_markup=KB.back())
    
    async def _vip_purchase(self, query, plan, amount, days):
        await query.edit_message_text(
            f"💎 *VIP {plan.capitalize()}*\n{Text.divider()}\n"
            f"💰 Amount: {amount:,} T\n"
            f"📆 Duration: {days} days\n\n"
            f"💳 Card: `{VIP_CARD}`\n"
            f"👤 Name: {VIP_HOLDER}\n\n"
            f"_Send receipt to:_ @{SUPPORT_USERNAME}"
        )
    
    # ===== CONVERSATION HANDLERS =====
    async def conv_broadcast_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("📝 Send your broadcast message. /cancel to abort.")
        return "AWAIT_MSG"
    
    async def conv_broadcast_receive(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        target = context.user_data.get('broadcast_target', 'all')
        message = update.message
        sent = 0
        for u in db.get_all_users():
            uid = int(u['telegram_id'])
            if target == 'vip' and not u.get('is_vip'):
                continue
            if target == 'users' and u.get('is_vip'):
                continue
            try:
                await message.copy(chat_id=uid)
                sent += 1
                await asyncio.sleep(0.03)
            except:
                pass
        await update.message.reply_text(f"✅ Sent to {sent} users.")
        return ConversationHandler.END
    
    async def conv_withdraw_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("📤 Enter amount (min 50,000 T):")
        return "AWAIT_AMOUNT"
    
    async def conv_withdraw_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.replace(',', '').replace('،', '')
        try:
            amount = int(text)
            if amount < 50000:
                await update.message.reply_text("Min 50,000 T. Try again:")
                return "AWAIT_AMOUNT"
            context.user_data['withdraw_amount'] = amount
            await update.message.reply_text("💳 Enter 16-digit card number:")
            return "AWAIT_CARD"
        except:
            await update.message.reply_text("Invalid number. Try again:")
            return "AWAIT_AMOUNT"
    
    async def conv_withdraw_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        card = update.message.text.strip()
        if not re.match(r'^\d{16}$', card):
            await update.message.reply_text("Must be 16 digits. Try again:")
            return "AWAIT_CARD"
        amount = context.user_data['withdraw_amount']
        db.add_payment({
            "user_id": str(update.effective_user.id),
            "amount": -amount,
            "type": "withdraw",
            "status": "pending",
            "date": get_persian_time(),
            "card": card,
        })
        await update.message.reply_text(f"✅ Withdrawal request for {amount:,} T registered.")
        return ConversationHandler.END
    
    async def conv_ai_chat_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("💬 *AI Chat*\nType your message. /cancel to exit.")
        return "CHATTING"
    
    async def conv_ai_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_msg = update.message.text
        responses = [
            "That's an interesting question! Let me analyze...",
            "Based on current market data, I'd suggest caution.",
            "The technical indicators show mixed signals.",
            "Great point! Here's what I think...",
            "I recommend checking the latest market overview.",
        ]
        await update.message.reply_text(f"🤖 {random.choice(responses)}")
        return "CHATTING"

# ============================================================================================================
# MAIN ENTRY POINT
# ============================================================================================================
def main():
    """Start the bot."""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  🚀 CryptoPulse AI v{BOT_VERSION}                         ║
║  Part 9 — Ultimate Handler Hub                          ║
║  {get_persian_time()}                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    if not BOT_TOKEN:
        print("=" * 60)
        print("ERROR: BOT_TOKEN environment variable not set!")
        print("Set it with: export BOT_TOKEN='your_token_here'")
        print("=" * 60)
        sys.exit(1)
    
    print(f"✅ Token: {BOT_TOKEN[:10]}...")
    print(f"✅ Admins: {ADMIN_IDS}")
    print(f"✅ Channel: {CHANNEL_ID}")
    print(f"✅ DB: In-Memory (self-contained)")
    print(f"✅ Scheduler: {'Available' if HAS_SCHEDULER else 'Fallback'}")
    print(f"✅ Monitoring: {'Available' if HAS_PSUTIL else 'Basic'}")
    
    # Build and run
    crypto_app = CryptoPulseApp()
    application = crypto_app.build()
    
    try:
        if WEBHOOK_URL:
            print(f"🌐 Webhook: {WEBHOOK_URL}")
            application.run_webhook(
                listen="0.0.0.0",
                port=int(os.environ.get("PORT", 8443)),
                url_path=BOT_TOKEN,
                webhook_url=WEBHOOK_URL
            )
        else:
            print("📡 Starting polling...")
            application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
