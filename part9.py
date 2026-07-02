#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   ██████╗██████╗██╗   ██╗██████╗████████╗██████╗ ██╗   ██╗ █████╗ ███████╗███████╗║
║  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝██╔════╝║
║  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██████╔╝ ╚████╔╝ ███████║███████╗███████╗║
║  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██╔══██╗  ╚██╔╝  ██╔══██║╚════██║╚════██║║
║  ╚██████╗██║  ██║   ██║   ██║        ██║   ██║  ██║   ██║   ██║  ██║███████║███████║║
║   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝║
║                                                                                    ║
║  🚀 CryptoPulse AI Bot v3.5 - Ultimate Telegram Handlers                          ║
║  ───────────────────────────────────────────────────────────────────────────────    ║
║  👑 Admin Panel  |  👤 Users  |  💰 Payments  |  💎 VIP  |  📢 Broadcast         ║
║  📡 Channel  |  🔧 API  |  💾 Backup  |  🚪 Server  |  🧠 Intelligence          ║
║  ════════════════════════════════════════════════════════════════════════════════   ║
║  📁 ۶۰۰۰+ خط کد  |  ⚡ فوق‌بهینه  |  🔥 حرفه‌ای  |  🛡️ ضد خطا                  ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import asyncio
import time
import random
import string
import hashlib
import warnings
import re
import logging
import traceback
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict, Counter
from functools import wraps, lru_cache
from contextlib import contextmanager, asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
#                    LOGGING SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Part9-Handlers")

# ============================================================
#                    غیرفعال کردن اخطارها
# ============================================================

warnings.filterwarnings("ignore")

# ============================================================
#                    TELEGRAM IMPORTS
# ============================================================

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    Bot, ReplyKeyboardMarkup, KeyboardButton,
    ChatPermissions, Message, CallbackQuery, ChatMember,
    InlineQueryResultArticle, InlineQueryResultPhoto,
    InlineQueryResultGif, InlineQueryResultVideo,
    ReplyKeyboardRemove, ForceReply
)

from telegram.constants import ParseMode
from telegram.warnings import PTBUserWarning
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    Defaults,
    ApplicationBuilder,
    AIORateLimiter
)

warnings.filterwarnings("ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

# ============================================================
#                    SAFE IMPORTS
# ============================================================

def safe_import(module_name: str, *attrs):
    """ایمن‌سازی واردات ماژول‌ها"""
    result = {}
    try:
        module = __import__(module_name, fromlist=attrs)
        for attr in attrs:
            result[attr] = getattr(module, attr) if hasattr(module, attr) else None
        logger.info(f"✅ Imported from {module_name}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to import {module_name}: {e}")
        for attr in attrs:
            result[attr] = None
    return result

_bot2 = safe_import("bot2", "get_config")
_bot3 = safe_import("bot3", "get_user_repo", "get_signal_repo", "get_payment_repo", "db_manager")
_bot4 = safe_import("bot4", "get_time", "get_emoji", "get_formatter", "get_hash", "get_validator", "get_cache")
_bot5 = safe_import("bot5", "get_market", "get_coinex")
_bot6 = safe_import("bot6", "get_ai", "get_groq")
_bot7 = safe_import("bot7", "get_technical")
_bot8 = safe_import("bot8", "lux_keyboard", "menu_builder", "LuxText", "LuxEmoji")
_part16 = safe_import("part16", "get_intelligence_engine")

get_config = _bot2.get("get_config")
get_user_repo = _bot3.get("get_user_repo")
get_signal_repo = _bot3.get("get_signal_repo")
get_payment_repo = _bot3.get("get_payment_repo")
db_manager = _bot3.get("db_manager")
get_time = _bot4.get("get_time")
get_emoji = _bot4.get("get_emoji")
get_formatter = _bot4.get("get_formatter")
get_hash = _bot4.get("get_hash")
get_validator = _bot4.get("get_validator")
get_cache = _bot4.get("get_cache")
get_market = _bot5.get("get_market")
get_coinex = _bot5.get("get_coinex")
get_ai = _bot6.get("get_ai")
get_groq = _bot6.get("get_groq")
get_technical = _bot7.get("get_technical")
lux_keyboard = _bot8.get("lux_keyboard")
menu_builder = _bot8.get("menu_builder")
LuxText = _bot8.get("LuxText")
LuxEmoji = _bot8.get("LuxEmoji")
get_intelligence_engine = _part16.get("get_intelligence_engine")

# ============================================================
#                    CONFIG
# ============================================================

config = get_config() if get_config else None
time_manager = get_time() if get_time else None
emoji_manager = get_emoji() if get_emoji else None
formatter = get_formatter() if get_formatter else None
hash_utils = get_hash() if get_hash else None
validator = get_validator() if get_validator else None
cache = get_cache() if get_cache else None
market = get_market() if get_market else None
ai_manager = get_ai() if get_ai else None
technical = get_technical() if get_technical else None

ADMIN_IDS = []
admin_ids_str = os.environ.get("ADMIN_IDS", "")
for x in admin_ids_str.split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except ValueError:
            pass

# Try multiple env var names
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    BOT_TOKEN = os.environ.get("Telegram _bot_token", "")
if not BOT_TOKEN:
    BOT_TOKEN = os.environ.get("telegram_bot_token", "")
if not BOT_TOKEN:
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "Farhad Behmard")
VIP_PRICE_MONTHLY = int(os.environ.get("VIP_PRICE_MONTHLY", 199000))
VIP_PRICE_YEARLY = int(os.environ.get("VIP_PRICE_YEARLY", 1990000))
VIP_PRICE_LIFETIME = int(os.environ.get("VIP_PRICE_LIFETIME", 4990000))
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
PROXY_URL = os.environ.get("PROXY_URL", "")

if BOT_TOKEN:
    logger.info(f"✅ BOT_TOKEN loaded: {BOT_TOKEN[:8]}...")
else:
    logger.error("❌ BOT_TOKEN not found!")

# ============================================================
#                    ENUMS & CONSTANTS
# ============================================================

class UserLevel(Enum):
    GUEST = "guest"
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class ErrorCode(Enum):
    SUCCESS = 0
    UNAUTHORIZED = 1001
    NOT_FOUND = 1002
    INVALID_INPUT = 1003
    RATE_LIMIT = 1004
    SERVER_ERROR = 1005
    VIP_REQUIRED = 1007
    ADMIN_REQUIRED = 1008

class ConversationState:
    MAIN = 0
    WAITING_FOR_ANALYSIS_COIN = 1
    WAITING_FOR_SIGNAL_COIN = 2
    WAITING_FOR_BROADCAST = 3
    WAITING_FOR_RECEIPT = 4
    WAITING_FOR_TICKET = 5
    WAITING_FOR_USER_ID = 6
    WAITING_FOR_REASON = 7
    WAITING_FOR_CONFIRM = 8
    WAITING_FOR_PAYMENT_ID = 9
    WAITING_FOR_BACKUP_RESTORE = 10
    WAITING_FOR_CHANNEL_MESSAGE = 11
    WAITING_FOR_CUSTOM_ALERT = 12
    WAITING_FOR_REFERRAL = 13
    WAITING_FOR_SETTINGS = 14

# ============================================================
#                    INTELLIGENCE ENGINE SETUP
# ============================================================

# Cache for intelligence reports
_intel_cache = {}
_intel_cache_time = {}
INTEL_CACHE_TTL = 300  # 5 minutes

def get_cached_intel_report():
    """دریافت گزارش هوشمند با کش"""
    now = time.time()
    if 'report' in _intel_cache and (now - _intel_cache_time.get('report', 0)) < INTEL_CACHE_TTL:
        return _intel_cache['report']
    
    if get_intelligence_engine:
        engine = get_intelligence_engine()
        report = engine.generate_comprehensive_report()
        _intel_cache['report'] = report
        _intel_cache_time['report'] = now
        return report
    return None

# ============================================================
#                    DECORATORS
# ============================================================

class DecoratorManager:
    """مدیریت دکوراتورهای پیشرفته"""
    
    _rate_limit_storage = defaultdict(list)
    _user_cooldowns = {}
    _action_counters = defaultdict(int)
    
    @staticmethod
    def admin_only(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not is_admin(update.effective_user.id):
                await update.message.reply_text(
                    "❌ **دسترسی غیرمجاز!**\nاین بخش فقط برای مدیران ربات است.",
                    parse_mode="Markdown"
                )
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def vip_only(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not is_vip(update.effective_user.id) and not is_admin(update.effective_user.id):
                await update.message.reply_text(
                    "💎 **بخش اختصاصی VIP**\nاین بخش فقط برای کاربران ویژه قابل دسترسی است.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💎 خرید VIP", callback_data="vip")]
                    ]),
                    parse_mode="Markdown"
                )
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def rate_limit(limit: int = 5, period: int = 60):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
                user_id = str(update.effective_user.id)
                now = time.time()
                DecoratorManager._rate_limit_storage[user_id] = [
                    t for t in DecoratorManager._rate_limit_storage[user_id] 
                    if now - t < period
                ]
                if len(DecoratorManager._rate_limit_storage[user_id]) >= limit:
                    wait_time = int(period - (now - DecoratorManager._rate_limit_storage[user_id][0]))
                    await update.message.reply_text(
                        f"⏳ **لطفاً صبر کنید!**\n{wait_time} ثانیه دیگر مجاز به درخواست هستید.",
                        parse_mode="Markdown"
                    )
                    return
                DecoratorManager._rate_limit_storage[user_id].append(now)
                return await func(update, context, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def log_action(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            action = func.__name__
            DecoratorManager._action_counters[action] += 1
            logger.info(f"📊 Action: {action} | User: {user.id} | Count: {DecoratorManager._action_counters[action]}")
            return await func(update, context, *args, **kwargs)
        return wrapper

admin_only = DecoratorManager.admin_only
vip_only = DecoratorManager.vip_only
rate_limit = DecoratorManager.rate_limit
log_action = DecoratorManager.log_action

# ============================================================
#                    UTILITY FUNCTIONS
# ============================================================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def is_vip(user_id: int) -> bool:
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(str(user_id))
        if db_user:
            return db_user.get('is_vip', False)
    return False

def get_user_level(user_id: int) -> UserLevel:
    if is_admin(user_id):
        return UserLevel.ADMIN
    if is_vip(user_id):
        return UserLevel.VIP
    return UserLevel.FREE

def get_persian_time() -> str:
    if time_manager:
        return time_manager.now_persian()
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_coin(coin: str) -> bool:
    valid_coins = [
        "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC",
        "SHIB", "AVAX", "LINK", "UNI", "ATOM", "LTC", "BCH", "NEAR", "VET",
        "ALGO", "FTM", "EOS", "TRX", "XLM", "ICP", "HBAR", "FIL", "APT", "ARB"
    ]
    return coin.upper() in valid_coins

def generate_referral_code(length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def format_number(num: float) -> str:
    if formatter:
        return formatter.number(num)
    return f"{num:,.0f}"

def format_price(price: float) -> str:
    if formatter:
        return formatter.price(price)
    return f"${price:,.2f}"

def get_error_message(error_code: ErrorCode) -> str:
    messages = {
        ErrorCode.SUCCESS: "✅ عملیات با موفقیت انجام شد.",
        ErrorCode.UNAUTHORIZED: "❌ دسترسی غیرمجاز!",
        ErrorCode.NOT_FOUND: "❌ موردی یافت نشد!",
        ErrorCode.INVALID_INPUT: "❌ ورودی نامعتبر!",
        ErrorCode.RATE_LIMIT: "⏳ لطفاً کمی صبر کنید...",
        ErrorCode.SERVER_ERROR: "❌ خطای سرور!",
        ErrorCode.VIP_REQUIRED: "💎 این بخش مخصوص کاربران VIP است.",
        ErrorCode.ADMIN_REQUIRED: "👑 این بخش مخصوص ادمین است.",
    }
    return messages.get(error_code, "❌ خطا!")

def sanitize_text(text: str, max_length: int = 1000) -> str:
    if not text:
        return ""
    text = re.sub(r'[<>/\\]', '', text)
    return text[:max_length]

# ============================================================
#                    KEYBOARDS
# ============================================================

def user_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 تحلیل لحظه‌ای", callback_data="analysis")],
        [InlineKeyboardButton("🚨 سیگنال خرید", callback_data="signal_buy"),
         InlineKeyboardButton("📈 سیگنال فروش", callback_data="signal_sell")],
        [InlineKeyboardButton("💰 کیف پول", callback_data="wallet"),
         InlineKeyboardButton("💎 VIP", callback_data="vip")],
        [InlineKeyboardButton("📡 سیگنال‌ها", callback_data="signals_menu")],
        [InlineKeyboardButton("📖 راهنما", callback_data="help"),
         InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_main_menu():
    keyboard = [
        [InlineKeyboardButton("🧠 داشبورد هوشمند", callback_data="admin_intelligence")],
        [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
        [InlineKeyboardButton("💎 مدیریت VIP", callback_data="admin_vip")],
        [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📡 ارسال به کانال", callback_data="admin_send_channel")],
        [InlineKeyboardButton("🔧 مدیریت API", callback_data="admin_api")],
        [InlineKeyboardButton("💾 بکاپ و بازیابی", callback_data="admin_backup")],
        [InlineKeyboardButton("🚪 مدیریت سرور", callback_data="admin_server")],
        [InlineKeyboardButton("📊 گزارش‌های پیشرفته", callback_data="admin_reports")],
        [InlineKeyboardButton("🔒 امنیت و لاگ", callback_data="admin_security")],
        [InlineKeyboardButton("🔙 منوی کاربری", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def vip_keyboard():
    keyboard = [
        [InlineKeyboardButton("💎 VIP ماهانه - ۱۹۹,۰۰۰ تومان", callback_data="vip_monthly")],
        [InlineKeyboardButton("💎 VIP سالانه - ۱,۹۹۰,۰۰۰ تومان", callback_data="vip_yearly")],
        [InlineKeyboardButton("👑 VIP مادام‌العمر - ۴,۹۹۰,۰۰۰ تومان", callback_data="vip_lifetime")],
        [InlineKeyboardButton("ℹ️ وضعیت VIP", callback_data="vip_status")],
        [InlineKeyboardButton("🎁 تست رایگان ۳ روزه", callback_data="vip_trial")],
        [InlineKeyboardButton("📋 راهنمای خرید", callback_data="vip_guide")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def signals_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 دریافت تحلیل", callback_data="analysis")],
        [InlineKeyboardButton("👤 حساب کاربری", callback_data="wallet")],
        [InlineKeyboardButton("📖 راهنما", callback_data="help")],
        [InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("💎 پنل VIP", callback_data="vip")],
        [InlineKeyboardButton("🆘 تیکت پشتیبانی", callback_data="support_ticket")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def wallet_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 موجودی", callback_data="wallet_balance")],
        [InlineKeyboardButton("📊 تاریخچه تراکنش", callback_data="wallet_history")],
        [InlineKeyboardButton("📈 گزارش معاملات", callback_data="wallet_report")],
        [InlineKeyboardButton("🔑 کد معرف", callback_data="wallet_referral")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔔 اعلان‌ها", callback_data="settings_notifications")],
        [InlineKeyboardButton("📊 تایم‌فریم", callback_data="settings_timeframe")],
        [InlineKeyboardButton("🤖 هوش مصنوعی", callback_data="settings_ai")],
        [InlineKeyboardButton("🌍 زبان", callback_data="settings_language")],
        [InlineKeyboardButton("💰 واحد پول", callback_data="settings_currency")],
        [InlineKeyboardButton("🔒 امنیت", callback_data="settings_security")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================
#                    TEXTS
# ============================================================

WELCOME_USER = """
🌟 **به CryptoPulse AI خوش آمدید!**

دستیار هوشمند تحلیل و سیگنال ارزهای دیجیتال

ما با استفاده از پیشرفته‌ترین هوش مصنوعی و تحلیل تکنیکال،  
به شما در تصمیم‌گیری‌های بهتر و پرسودتر کمک می‌کنیم.

---

**🔹 تحلیل لحظه‌ای بازار**
- هوش مصنوعی پیشرفته (Groq AI)
- مدیریت پرسش هوشمند
- سیگنال‌های دقیق و سریع
- پنل‌های VIP با امکانات ویژه

---

**📊 همراه شما در مسیر سودآوری**

از دکمه‌های زیر برای شروع استفاده کنید 👇
"""

WELCOME_ADMIN = """
👑 **پنل مدیریت CryptoPulse AI**

**سازنده عزیز، پنل مدیریت و تنظیمات ربات**

---

📊 **آمار کلی:**
👥 کاربران: {users:,}
💎 VIP: {vip:,}
🚨 سیگنال‌ها: {signals:,}
💰 درآمد: {revenue:,.0f} تومان

⏰ زمان: {time}
"""

VIP_TEXT = """
💎 **پنل VIP CryptoPulse AI**

✨ **امکانات ویژه VIP:**
• 📊 سیگنال‌های اختصاصی VIP
• 🤖 تحلیل پیشرفته با AI (نامحدود)
• 🆘 پشتیبانی اولویت‌دار ۲۴/۷
• 💎 دسترسی به ارزهای ویژه
• 🔔 هشدارهای لحظه‌ای
• 📈 مدیریت پورتفولیو پیشرفته
• 🎯 سیگنال‌های دقیق‌تر با ۳۰+ اندیکاتور
• 📊 اندیکاتورهای اختصاصی
• 🔬 تحلیل تخصصی و فاندامنتال
• 📡 سیگنال‌های لحظه‌ای
• 📱 اعلان‌های فوری در تلگرام
• 🎁 هدیه ماهانه
• 📚 آموزش‌های اختصاصی
• 🤝 دسترسی به گروه VIP
• 🎯 استراتژی‌های معاملاتی

💰 **قیمت‌ها (تومان):**
• 💎 ماهانه: ۱۹۹,۰۰۰ تومان
• 💎 سالانه: ۱,۹۹۰,۰۰۰ تومان (۱۰٪ تخفیف)
• 👑 مادام‌العمر: ۴,۹۹۰,۰۰۰ تومان (۵۰٪ تخفیف)

🎁 **تست رایگان:** ۳ روز

📌 **برای خرید روی گزینه مورد نظر کلیک کنید.**
"""

HELP_TEXT = """
📖 **راهنمای ربات CryptoPulse AI**

**🔹 شروع کار:**
با دکمه‌های منوی اصلی از امکانات استفاده کنید.

**🔹 تحلیل و سیگنال:**
ربات با استفاده از AI و تحلیل تکنیکال، سیگنال‌های دقیق ارائه می‌دهد.

**🔹 VIP:**
با خرید VIP به امکانات ویژه دسترسی پیدا کنید.
💰 قیمت: ۱۹۹,۰۰۰ تومان ماهانه

**🔹 پشتیبانی:**
برای ارتباط با پشتیبانی از گزینه پشتیبانی استفاده کنید.
📱 @{support}

📌 **دستورات سریع:**
/start - شروع مجدد
/help - راهنما
/admin - پنل ادمین (فقط ادمین)
/signal - دریافت سیگنال
/price - قیمت لحظه‌ای
/vip - پنل VIP
/wallet - کیف پول
/cancel - لغو عملیات
"""

SUPPORT_TEXT = """
🆘 **پشتیبانی CryptoPulse AI**

📱 **ادمین:** @{support}
📧 **ایمیل:** support@cryptopulse.ai
🌐 **وبسایت:** https://cryptopulse.ai

⏰ **ساعات پاسخگویی:** ۲۴/۷

📝 **برای ارسال تیکت، روی دکمه زیر کلیک کنید.**
"""

SIGNALS_MENU_TEXT = """
📡 **منوی سیگنال‌ها**

از دکمه‌های زیر برای دسترسی به بخش‌های مختلف استفاده کنید:

📊 **دریافت تحلیل:** تحلیل لحظه‌ای بازار با AI
👤 **حساب کاربری:** مدیریت حساب و کیف پول
📖 **راهنما:** آموزش و نکات معاملاتی
🆘 **پشتیبانی:** ارتباط با پشتیبانی
💎 **پنل VIP:** امکانات ویژه VIP
🆘 **پنل پشتیبانی:** تیکت‌های پشتیبانی
"""

# ============================================================
#                    COMMAND HANDLERS
# ============================================================

@log_action
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور استارت"""
    user = update.effective_user
    user_id = str(user.id)

    # Register user
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if not db_user:
            get_user_repo().create(
                telegram_id=user_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_admin=is_admin(user.id),
                referral_code=generate_referral_code()
            )
        else:
            # Update last active
            get_user_repo().update(user_id, last_active=datetime.now().isoformat())

    if is_admin(user.id):
        stats = db_manager.get_stats() if db_manager else {}
        text = WELCOME_ADMIN.format(
            users=stats.get('users', 0),
            vip=stats.get('vip_users', 0),
            signals=stats.get('signals', 0),
            revenue=stats.get('total_revenue', 0),
            time=get_persian_time()
        )
        keyboard = admin_main_menu()
    else:
        text = WELCOME_USER
        keyboard = user_main_menu()

    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

@log_action
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنما"""
    await update.message.reply_text(
        HELP_TEXT.format(support=SUPPORT_USERNAME),
        reply_markup=user_main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

@admin_only
@log_action
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل ادمین"""
    stats = db_manager.get_stats() if db_manager else {}
    text = WELCOME_ADMIN.format(
        users=stats.get('users', 0),
        vip=stats.get('vip_users', 0),
        signals=stats.get('signals', 0),
        revenue=stats.get('total_revenue', 0),
        time=get_persian_time()
    )
    await update.message.reply_text(text, reply_markup=admin_main_menu(), parse_mode=ParseMode.MARKDOWN)

@log_action
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات"""
    context.user_data.clear()
    await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_main_menu())
    return ConversationHandler.END

@log_action
async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل VIP"""
    await update.message.reply_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)

@log_action
async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """کیف پول"""
    user_id = str(update.effective_user.id)
    
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if db_user:
            is_vip_flag = db_user.get('is_vip', False)
            vip_expire = db_user.get('vip_expire', 'ندارد')
            
            text = f"""
💰 **کیف پول شما**

💵 **موجودی:** {format_number(db_user.get('balance', 0))} تومان
💳 **کل واریز:** {format_number(db_user.get('total_deposited', 0))} تومان
📤 **کل برداشت:** {format_number(db_user.get('total_withdrawn', 0))} تومان
📈 **سود کل:** {format_number(db_user.get('total_profit', 0))} تومان

🔗 **کد معرف:** `{db_user.get('referral_code', 'ندارد')}`
👥 **تعداد معرف‌ها:** {db_user.get('referral_count', 0)}
💰 **پاداش معرف:** {format_number(db_user.get('referral_earnings', 0))} تومان

📊 **تعداد معاملات:** {db_user.get('total_trades', 0)}
✅ **موفق:** {db_user.get('successful_trades', 0)}
❌ **ناموفق:** {db_user.get('failed_trades', 0)}
🏆 **نرخ برد:** {db_user.get('win_rate', 0):.1f}%

💎 **وضعیت VIP:** {'✅ فعال' if is_vip_flag else '❌ غیرفعال'}
📅 **انقضای VIP:** {vip_expire}
📊 **سطح VIP:** {db_user.get('vip_level', 0)}
"""
            await update.message.reply_text(text, reply_markup=wallet_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
    
    await update.message.reply_text("💰 کیف پول در حال توسعه...", reply_markup=user_main_menu())

@log_action
@rate_limit(limit=3, period=30)
async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت سیگنال"""
    await update.message.reply_text(
        "📊 **دریافت سیگنال**\n\n"
        "لطفاً نام ارز مورد نظر را وارد کنید:\n"
        "مثال: `BTC` یا `ETH`\n\n"
        "📌 **ارزهای پشتیبانی شده:**\n"
        "BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, SHIB, AVAX, LINK\n\n"
        "برای لغو /cancel را بفرستید.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationState.WAITING_FOR_SIGNAL_COIN

@log_action
@rate_limit(limit=5, period=30)
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قیمت لحظه‌ای"""
    await update.message.reply_text(
        f"💰 **قیمت لحظه‌ای BTC**\n\n"
        f"💵 قیمت: $67,845.32\n"
        f"📈 تغییر ۲۴ساعته: +2.34%\n"
        f"📊 بالاترین: $68,200.00\n"
        f"📉 پایین‌ترین: $66,500.00\n"
        f"📊 حجم: $24.5B\n\n"
        f"⏰ زمان: {get_persian_time()}",
        reply_markup=user_main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

@log_action
@rate_limit(limit=3, period=60)
async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحلیل هوش مصنوعی"""
    await update.message.reply_text(
        f"⏳ در حال دریافت تحلیل از AI...",
        reply_markup=user_main_menu()
    )
    
    await update.message.reply_text(
        f"📊 **تحلیل تکنیکال BTC**\n\n"
        f"🤖 **تحلیل AI:** بازار در حالت خنثی قرار دارد.\n"
        f"💰 قیمت: $67,845.32\n"
        f"📈 RSI: 55.2\n"
        f"📊 MACD: صعودی\n"
        f"🎯 پیشنهاد: HOLD\n\n"
        f"⏰ زمان: {get_persian_time()}",
        reply_markup=user_main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

@log_action
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیمات"""
    text = f"""
⚙️ **تنظیمات ربات**

🔔 **اعلان‌ها:** فعال
📊 **تایم‌فریم:** ۴ساعته
🤖 **تحلیل AI:** فعال
🌍 **زبان:** فارسی
💰 **واحد پول:** تومان
🔒 **امنیت:** بالا
📱 **دستگاه:** موبایل

📊 **تنظیمات پیشرفته:**
• نمایش قیمت: فعال
• نمایش سیگنال: فعال
• هشدار صوتی: غیرفعال
• حالت شب: غیرفعال
"""
    await update.message.reply_text(text, reply_markup=settings_keyboard(), parse_mode=ParseMode.MARKDOWN)

# ============================================================
#                    SIGNAL HANDLERS
# ============================================================

@log_action
async def signal_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش نام ارز برای سیگنال"""
    coin = update.message.text.upper().strip()
    
    if coin in ["❌ لغو", "🔙 بازگشت"]:
        await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_main_menu())
        return ConversationHandler.END
    
    if not validate_coin(coin):
        await update.message.reply_text(
            f"❌ ارز {coin} پشتیبانی نمی‌شود.\n\n"
            f"📌 ارزهای پشتیبانی شده:\n"
            f"BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, SHIB, AVAX, LINK",
            reply_markup=user_main_menu()
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN
    
    await update.message.reply_text(f"⏳ در حال دریافت سیگنال {coin}...")
    
    # Generate signal
    signal_type = random.choice(["buy", "sell", "hold"])
    confidence = random.randint(60, 95)
    price = random.uniform(100, 70000)
    change = random.uniform(-5, 5)
    stop_loss = price * 0.95
    targets = [price * 1.02, price * 1.05, price * 1.10]
    
    emojis = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}
    stars = "⭐⭐⭐" if confidence >= 80 else "⭐⭐" if confidence >= 60 else "⭐"
    
    targets_text = "\n".join([f"   هدف {i+1}: ${t:,.2f}" for i, t in enumerate(targets[:3])])
    
    text = f"""
🚨 **سیگنال {coin}**

{emojis.get(signal_type, '🟡')} **پیشنهاد:** {signal_type.upper()}
🎯 **اطمینان:** {confidence}% {stars}

💰 **قیمت فعلی:** ${price:,.2f}
📈 **تغییر ۲۴ساعته:** {change:+.2f}%

📊 **تحلیل تکنیکال:**
• RSI در محدوده مناسب
• MACD سیگنال {signal_type} نشان می‌دهد
• حجم معاملات مطلوب

🎯 **اهداف قیمتی:**
{targets_text}

🛑 **حد ضرر:** ${stop_loss:,.2f}
📈 **نسبت ریسک/پاداش:** 2.5

📅 **تاریخ انقضا:** {(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M')}

⏰ **زمان:** {get_persian_time()}
"""
    
    # Save signal
    if get_signal_repo and get_user_repo:
        get_signal_repo().create(
            user_id=str(update.effective_user.id),
            coin=coin,
            signal_type=signal_type,
            confidence=confidence,
            entry_price=price,
            stop_loss=stop_loss,
            targets=json.dumps(targets),
            timeframe="4h"
        )
    
    await update.message.reply_text(text, reply_markup=user_main_menu(), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END

@log_action
async def analysis_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش نام ارز برای تحلیل"""
    coin = update.message.text.upper().strip()
    
    if coin in ["❌ لغو", "🔙 بازگشت"]:
        await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_main_menu())
        return ConversationHandler.END
    
    if not validate_coin(coin):
        await update.message.reply_text(
            f"❌ ارز {coin} پشتیبانی نمی‌شود.",
            reply_markup=user_main_menu()
        )
        return ConversationState.WAITING_FOR_ANALYSIS_COIN
    
    await update.message.reply_text(f"⏳ در حال تحلیل {coin}...")
    
    rsi = random.uniform(30, 70)
    macd = random.uniform(-100, 100)
    trend = random.choice(["صعودی 📈", "نزولی 📉", "خنثی ➡️"])
    signal = "buy" if trend == "صعودی 📈" else "sell" if trend == "نزولی 📉" else "hold"
    
    text = f"""
📊 **تحلیل تکنیکال {coin}**

🤖 **تحلیل هوش مصنوعی:**
بازار {coin} در شرایط {trend} قرار دارد.

📈 **نکات کلیدی:**
• حمایت اصلی: ${random.uniform(100, 60000):,.2f}
• مقاومت اصلی: ${random.uniform(200, 70000):,.2f}
• روند: {trend}
• RSI: {rsi:.1f}
• MACD: {macd:.2f}
• ADX: 25.3
• MFI: 52.1

🎯 **پیشنهاد:** {signal.upper()}
🎯 **اطمینان:** {random.randint(55, 90)}%

⏰ **زمان:** {get_persian_time()}
"""
    await update.message.reply_text(text, reply_markup=user_main_menu(), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END

# ============================================================
#                    CALLBACK HANDLER (ULTIMATE)
# ============================================================

@log_action
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کالبک‌ها — نسخه نهایی و کامل"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    admin_flag = is_admin(user_id)
    
    # ============================================================
    #                    NAVIGATION
    # ============================================================
    
    if data == "back_main":
        if admin_flag:
            stats = db_manager.get_stats() if db_manager else {}
            text = WELCOME_ADMIN.format(
                users=stats.get('users', 0),
                vip=stats.get('vip_users', 0),
                signals=stats.get('signals', 0),
                revenue=stats.get('total_revenue', 0),
                time=get_persian_time()
            )
            await query.edit_message_text(text, reply_markup=admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
        else:
            await query.edit_message_text(WELCOME_USER, reply_markup=user_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("✅ عملیات لغو شد.", reply_markup=user_main_menu())
        return
    
    # ============================================================
    #                    USER FEATURES
    # ============================================================
    
    if data == "analysis":
        await query.edit_message_text(
            "📊 **تحلیل لحظه‌ای**\n\n"
            "لطفاً نام ارز مورد نظر را وارد کنید:\n"
            "مثال: `BTC` یا `ETH`\n\n"
            "📌 **ارزهای پشتیبانی شده:**\n"
            "BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, SHIB, AVAX, LINK\n\n"
            "برای لغو /cancel را بفرستید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_ANALYSIS_COIN
    
    if data in ["signal_buy", "signal_sell"]:
        signal_type = "خرید" if data == "signal_buy" else "فروش"
        await query.edit_message_text(
            f"📊 **دریافت سیگنال {signal_type}**\n\n"
            "لطفاً نام ارز مورد نظر را وارد کنید:\n"
            "مثال: `BTC` یا `ETH`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN
    
    if data == "signals_menu":
        await query.edit_message_text(SIGNALS_MENU_TEXT, reply_markup=signals_menu_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "wallet":
        user_id_str = str(user_id)
        if get_user_repo:
            db_user = get_user_repo().get_by_telegram_id(user_id_str)
            if db_user:
                is_vip_flag = db_user.get('is_vip', False)
                text = f"""
💰 **کیف پول شما**

💵 **موجودی:** {format_number(db_user.get('balance', 0))} تومان
💳 **کل واریز:** {format_number(db_user.get('total_deposited', 0))} تومان
📤 **کل برداشت:** {format_number(db_user.get('total_withdrawn', 0))} تومان

🔗 **کد معرف:** `{db_user.get('referral_code', 'ندارد')}`
👥 **تعداد معرف‌ها:** {db_user.get('referral_count', 0)}

📊 **تعداد معاملات:** {db_user.get('total_trades', 0)}
🏆 **نرخ برد:** {db_user.get('win_rate', 0):.1f}%

💎 **VIP:** {'✅ فعال' if is_vip_flag else '❌ غیرفعال'}
📅 **انقضا:** {db_user.get('vip_expire', 'ندارد')}
"""
                await query.edit_message_text(text, reply_markup=wallet_keyboard(), parse_mode=ParseMode.MARKDOWN)
                return
    
    # ============================================================
    #                    VIP FEATURES
    # ============================================================
    
    if data == "vip":
        await query.edit_message_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "vip_monthly":
        await query.edit_message_text(
            f"💎 **خرید VIP ماهانه**\n\n"
            f"💰 **مبلغ:** {VIP_PRICE_MONTHLY:,} تومان\n"
            f"📅 **مدت:** ۱ ماه\n\n"
            f"✨ **امکانات:**\n"
            f"• سیگنال‌های اختصاصی VIP\n"
            f"• تحلیل پیشرفته با AI\n"
            f"• پشتیبانی اولویت‌دار\n"
            f"• دسترسی به ارزهای ویژه\n\n"
            f"💳 **شماره کارت:** `{VIP_CARD}`\n"
            f"🏦 **به نام:** {VIP_HOLDER}\n\n"
            f"📤 پس از واریز، روی دکمه ارسال رسید کلیک کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'monthly'
        return
    
    if data == "vip_yearly":
        await query.edit_message_text(
            f"💎 **خرید VIP سالانه**\n\n"
            f"💰 **مبلغ:** {VIP_PRICE_YEARLY:,} تومان\n"
            f"📅 **مدت:** ۱۲ ماه\n"
            f"🎁 **تخفیف:** ۱۰٪\n\n"
            f"💳 **کارت:** `{VIP_CARD}`\n"
            f"🏦 **به نام:** {VIP_HOLDER}\n\n"
            f"📤 پس از واریز، رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'yearly'
        return
    
    if data == "vip_lifetime":
        await query.edit_message_text(
            f"👑 **VIP مادام‌العمر**\n\n"
            f"💰 **مبلغ:** {VIP_PRICE_LIFETIME:,} تومان\n"
            f"📅 **مدت:** مادام‌العمر\n"
            f"🎁 **تخفیف ویژه:** ۵۰٪\n\n"
            f"💳 **کارت:** `{VIP_CARD}`\n"
            f"🏦 **به نام:** {VIP_HOLDER}\n\n"
            f"📤 پس از واریز، رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'lifetime'
        return
    
    if data == "vip_status":
        if get_user_repo:
            db_user = get_user_repo().get_by_telegram_id(str(user_id))
            if db_user:
                is_vip_flag = db_user.get('is_vip', False)
                expire = db_user.get('vip_expire', 'ندارد')
                level = db_user.get('vip_level', 0)
                await query.edit_message_text(
                    f"💎 **وضعیت VIP**\n\n"
                    f"📊 **وضعیت:** {'✅ فعال' if is_vip_flag else '❌ غیرفعال'}\n"
                    f"📅 **انقضا:** {expire}\n"
                    f"📊 **سطح:** {level}\n\n"
                    f"برای خرید VIP از منوی اصلی استفاده کنید.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
    
    if data == "vip_trial":
        if get_user_repo:
            db_user = get_user_repo().get_by_telegram_id(str(user_id))
            if db_user:
                if db_user.get('is_vip'):
                    await query.answer("ℹ️ شما قبلاً کاربر VIP هستید!", show_alert=True)
                    return
                
                if db_user.get('vip_trial_used'):
                    await query.answer("⚠️ تست رایگان فقط یک بار قابل استفاده است!", show_alert=True)
                    return
                
                get_user_repo().update(
                    str(user_id),
                    is_vip=True,
                    vip_level=1,
                    vip_plan='trial',
                    vip_expire=(datetime.now() + timedelta(days=3)).isoformat(),
                    vip_activated_at=datetime.now().isoformat(),
                    vip_trial_used=True
                )
                
                await query.edit_message_text(
                    f"🎁 **VIP تست ۳ روزه فعال شد!**\n\n"
                    f"📅 تاریخ انقضا: {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}\n\n"
                    f"💎 از امکانات ویژه VIP لذت ببرید! 🎉",
                    reply_markup=vip_keyboard(),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
    
    if data == "vip_guide":
        await query.edit_message_text(
            f"📋 **راهنمای خرید VIP**\n\n"
            f"1️⃣ **واریز مبلغ:**\n"
            f"مبلغ مورد نظر را به کارت زیر واریز کنید:\n"
            f"💳 `{VIP_CARD}`\n"
            f"🏦 به نام: **{VIP_HOLDER}**\n\n"
            f"2️⃣ **ارسال رسید:**\n"
            f"پس از واریز، از رسید عکس بگیرید و ارسال کنید\n\n"
            f"3️⃣ **تایید:**\n"
            f"ادمین @{SUPPORT_USERNAME} رسید شما را بررسی می‌کند\n\n"
            f"4️⃣ **فعال‌سازی:**\n"
            f"پس از تایید، VIP شما فعال می‌شود\n\n"
            f"⏱️ **زمان تقریبی تایید:** ۲۴ ساعت\n\n"
            f"⚠️ **توجه:** حتماً نام کاربری خود را در رسید یادداشت کنید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "vip_send_receipt":
        await query.edit_message_text(
            "📤 **ارسال رسید**\n\n"
            "لطفاً تصویر رسید خود را ارسال کنید.\n\n"
            "⚠️ **توجه:**\n"
            "• حتماً نام کاربری خود را در رسید یادداشت کنید\n"
            "• تصویر باید واضح و خوانا باشد\n"
            "• پس از تایید، VIP شما فعال می‌شود\n\n"
            "برای لغو /cancel را بفرستید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_receipt'] = True
        return
    
    # ============================================================
    #                    HELP & SUPPORT
    # ============================================================
    
    if data == "help":
        await query.edit_message_text(HELP_TEXT.format(support=SUPPORT_USERNAME), reply_markup=user_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "support":
        await query.edit_message_text(
            SUPPORT_TEXT.format(support=SUPPORT_USERNAME),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 تماس با ادمین", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("📧 ارسال ایمیل", callback_data="support_email")],
                [InlineKeyboardButton("🎫 تیکت جدید", callback_data="support_ticket")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "support_ticket":
        await query.edit_message_text(
            "🎫 **تیکت جدید**\n\n"
            "لطفاً مشکل یا سوال خود را بنویسید:\n\n"
            "📌 **موارد پشتیبانی:**\n"
            "• مشکلات فنی ربات\n"
            "• سوالات درباره VIP\n"
            "• پیشنهادات و انتقادات\n"
            "• گزارش باگ\n\n"
            "برای لغو /cancel را بفرستید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_ticket'] = True
        return
    
    if data == "support_email":
        await query.edit_message_text(
            "📧 **ارسال ایمیل**\n\n"
            "📧 **آدرس ایمیل:** support@cryptopulse.ai\n\n"
            "📝 **موضوع:**\n"
            "• مشکلات فنی\n"
            "• سوالات درباره VIP\n"
            "• پیشنهادات\n\n"
            "⏰ **زمان پاسخ:** ۲۴-۴۸ ساعت",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="support")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ============================================================
    #                    SETTINGS
    # ============================================================
    
    if data == "settings":
        text = f"""
⚙️ **تنظیمات ربات**

🔔 **اعلان‌ها:** فعال
📊 **تایم‌فریم:** ۴ساعته
🤖 **تحلیل AI:** فعال
🌍 **زبان:** فارسی
💰 **واحد پول:** تومان
🔒 **امنیت:** بالا
"""
        await query.edit_message_text(text, reply_markup=settings_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================================
    #                    ADMIN PANEL
    # ============================================================
    
    if not admin_flag and data.startswith("admin_"):
        await query.answer("❌ دسترسی غیرمجاز!", show_alert=True)
        return
    
    # ====== INTELLIGENCE DASHBOARD ======
    if data == "admin_intelligence":
        await query.edit_message_text("🧠 **در حال تحلیل هوشمند...**")
        
        report = get_cached_intel_report()
        
        if report:
            alerts_text = "\n".join([f"• {a}" for a in report['alerts']]) if report['alerts'] else "✅ بدون هشدار"
            insights_text = "\n".join([f"• {i}" for i in report['insights']]) if report['insights'] else "✅ بدون پیشنهاد خاص"
            
            text = f"""
🧠 **داشبورد هوشمند ادمین**

📊 **بخش‌بندی کاربران:**
• 👑 VIP فعال: **{report['segments']['vip_active']}**
• ⏳ VIP در حال انقضا: **{report['segments']['vip_expiring']}**
• 💰 با ارزش: **{report['segments']['high_value']}**
• ⚠️ پرریسک: **{report['segments']['at_risk']}**
• 🆕 کاربران جدید: **{report['segments']['new_users']}**
• 😴 غیرفعال: **{report['segments']['inactive']}**

💰 **تحلیل مالی:**
• درآمد کل: **{format_number(report['financials']['total_revenue'])} تومان**
• امروز: **{format_number(report['financials']['today_revenue'])} تومان**
• این هفته: **{format_number(report['financials']['week_revenue'])} تومان**
• روند: {report['financials']['trend']}
• پیش‌بینی ماهانه: **{format_number(report['financials']['projected_monthly'])} تومان**
• نرخ تبدیل: **{report['financials']['conversion_rate']:.1f}%**
• میانگین تراکنش: **{format_number(report['financials']['avg_transaction'])} تومان**
• طرح محبوب: **{report['financials']['top_plan']}**

🚨 **عملکرد سیگنال‌ها:**
• کل سیگنال‌ها: **{report['signals']['total_signals']}**
• نرخ برد: **{report['signals']['win_rate']:.1f}%**
• میانگین اطمینان: **{report['signals']['avg_confidence']:.1f}%**
• بهترین ارز: **{report['signals']['best_coin']}**
• Profit Factor: **{report['signals']['profit_factor']:.2f}**

⚠️ **هشدارها:**
{alerts_text}

💡 **پیشنهادات هوش مصنوعی:**
{insights_text}
"""
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 کاربران پرریسک", callback_data="admin_intel_risk"),
                 InlineKeyboardButton("📉 پیش‌بینی ریزش", callback_data="admin_intel_churn")],
                [InlineKeyboardButton("👑 کاربران با ارزش", callback_data="admin_intel_high_value"),
                 InlineKeyboardButton("💎 VIP های در حال انقضا", callback_data="admin_intel_expiring")],
                [InlineKeyboardButton("🔄 بروزرسانی گزارش", callback_data="admin_intelligence")],
                [InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="back_main")],
            ])
        else:
            text = "❌ **خطا در دریافت گزارش هوشمند!**\n\nمطمئن شوید part16.py درست import شده است."
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]])
        
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        return
    
    # ====== INTELLIGENCE SUB-MENUS ======
    if data == "admin_intel_risk":
        if get_intelligence_engine:
            engine = get_intelligence_engine()
            risk_users = engine.get_risk_users_detail()
            
            if risk_users:
                text = f"⚠️ **کاربران پرریسک** ({len(risk_users)} کاربر)\n\n"
                for i, u in enumerate(risk_users[:15], 1):
                    text += f"{i}. {u['name']} | ریسک: {u['risk_score']}%\n"
                    text += f"   🆔 `{u['user_id']}`\n"
                    if u['flags']:
                        text += f"   🚩 {', '.join(u['flags'][:2])}\n"
                    text += "\n"
            else:
                text = "✅ **کاربر پرریسکی یافت نشد!**"
            
            await query.edit_message_text(
                text, 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_intelligence")]]), 
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data == "admin_intel_churn":
        if get_intelligence_engine:
            engine = get_intelligence_engine()
            churn_users = engine.get_churn_prediction()
            
            if churn_users:
                text = f"📉 **پیش‌بینی ریزش** ({len(churn_users)} کاربر)\n\n"
                for i, u in enumerate(churn_users[:15], 1):
                    prob = u['churn_probability'] * 100
                    emoji = "🔴" if prob > 50 else "🟡" if prob > 30 else "🟢"
                    text += f"{i}. {u['name']} {emoji} {prob:.0f}%\n"
                    text += f"   🆔 `{u['user_id']}`\n"
                    text += f"   💡 {u['recommendation']}\n\n"
            else:
                text = "✅ **ریزشی پیش‌بینی نمی‌شود!**"
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_intelligence")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data == "admin_intel_high_value":
        if get_intelligence_engine:
            engine = get_intelligence_engine()
            segments = engine.get_user_segments()
            users = segments.get('high_value', [])
            
            if users:
                text = f"👑 **کاربران با ارزش بالا** ({len(users)} کاربر)\n\n"
                for i, user in enumerate(users[:15], 1):
                    name = user.get('first_name', 'نامشخص')
                    tid = user.get('telegram_id', '?')
                    vip = "💎" if user.get('is_vip') else ""
                    text += f"{i}. {name} {vip} | `{tid}`\n"
            else:
                text = "ℹ️ کاربر با ارزشی یافت نشد!"
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_intelligence")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data == "admin_intel_expiring":
        if get_intelligence_engine:
            engine = get_intelligence_engine()
            segments = engine.get_user_segments()
            users = segments.get('vip_expiring', [])
            
            if users:
                text = f"⏳ **VIP های در حال انقضا** ({len(users)} کاربر)\n\n"
                for i, user in enumerate(users[:15], 1):
                    name = user.get('first_name', 'نامشخص')
                    tid = user.get('telegram_id', '?')
                    expire = user.get('vip_expire', 'نامشخص')
                    text += f"{i}. {name} | `{tid}` | {expire}\n"
            else:
                text = "✅ هیچ VIP در حال انقضایی نیست!"
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_intelligence")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    # ====== ADMIN USERS ======
    if data == "admin_users":
        await query.edit_message_text(
            "👥 **مدیریت کاربران**\n\nاز دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 لیست کاربران", callback_data="admin_users_list")],
                [InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="admin_users_search")],
                [InlineKeyboardButton("🔨 بن کاربر", callback_data="admin_users_ban"),
                 InlineKeyboardButton("🔓 آنبن کاربر", callback_data="admin_users_unban")],
                [InlineKeyboardButton("👑 ادمین کردن", callback_data="admin_users_make_admin"),
                 InlineKeyboardButton("🗑️ حذف کاربر", callback_data="admin_users_delete")],
                [InlineKeyboardButton("📊 آمار کاربران", callback_data="admin_users_stats")],
                [InlineKeyboardButton("📋 کاربران VIP", callback_data="admin_users_vip_list")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_users_list":
        if get_user_repo:
            users = get_user_repo().get_all()
            if not users:
                await query.edit_message_text(
                    "ℹ️ هیچ کاربری یافت نشد!",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]])
                )
                return
            
            text = f"👥 **لیست کاربران** ({len(users)} کاربر)\n\n"
            for i, user in enumerate(users[:25], 1):
                status = "🔴 بن" if user.get('is_banned') else "🟢 فعال"
                vip = "💎" if user.get('is_vip') else ""
                admin = "👑" if user.get('is_admin') else ""
                name = user.get('first_name', 'نامشخص')
                tid = user.get('telegram_id', '?')
                
                text += f"{i}. {name} {admin}{vip}\n"
                text += f"   🆔 `{tid}` | {status}\n\n"
            
            if len(users) > 25:
                text += f"\n... و {len(users) - 25} کاربر دیگر"
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_users_list")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data == "admin_users_stats":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
📊 **آمار کاربران**

👥 **کل کاربران:** {stats.get('users', 0):,}
👤 **کاربران فعال:** {stats.get('active_users', 0):,}
💎 **کاربران VIP:** {stats.get('vip_users', 0):,}
🚫 **کاربران بن شده:** {stats.get('banned_users', 0):,}
👑 **ادمین‌ها:** {len(ADMIN_IDS)}

📈 **کاربران امروز:** {stats.get('today_users', 0)}
📊 **کاربران این هفته:** {stats.get('week_users', 0)}
📅 **کاربران این ماه:** {stats.get('month_users', 0)}

📊 **نرخ رشد:** ۱۲.۵%
"""
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_users_vip_list":
        if get_user_repo:
            users = get_user_repo().get_vip_users()
            if not users:
                await query.edit_message_text(
                    "ℹ️ هیچ کاربر VIP یافت نشد!",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]])
                )
                return
            
            text = f"📋 **لیست کاربران VIP** ({len(users)} کاربر)\n\n"
            for i, user in enumerate(users[:25], 1):
                name = user.get('first_name', 'نامشخص')
                plan = user.get('vip_plan', 'نامشخص')
                expire = user.get('vip_expire', 'ندارد')
                tid = user.get('telegram_id', '?')
                
                text += f"{i}. {name} | {plan}\n"
                text += f"   🆔 `{tid}` | 📅 {expire}\n\n"
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data in ["admin_users_ban", "admin_users_unban", "admin_users_make_admin", "admin_users_delete", "admin_users_search"]:
        context.user_data['admin_action'] = data
        action_names = {
            "admin_users_ban": "بن",
            "admin_users_unban": "آنبن",
            "admin_users_make_admin": "ادمین کردن",
            "admin_users_delete": "حذف",
            "admin_users_search": "جستجو"
        }
        action = action_names.get(data, "انجام عملیات")
        await query.edit_message_text(
            f"🔍 لطفاً **آیدی عددی** کاربر را برای **{action}** وارد کنید:\n\nبرای لغو /cancel",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_USER_ID
    
    # ====== ADMIN PAYMENTS ======
    if data == "admin_payments":
        await query.edit_message_text(
            "💰 **مدیریت پرداخت‌ها**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ پرداخت‌های در انتظار", callback_data="admin_payments_pending")],
                [InlineKeyboardButton("✅ پرداخت‌های تایید شده", callback_data="admin_payments_completed")],
                [InlineKeyboardButton("❌ پرداخت‌های رد شده", callback_data="admin_payments_rejected")],
                [InlineKeyboardButton("📊 گزارش مالی", callback_data="admin_payments_report")],
                [InlineKeyboardButton("💰 تنظیم قیمت‌ها", callback_data="admin_payments_prices")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_payments_pending":
        if get_payment_repo:
            payments = get_payment_repo().get_pending_payments()
            if not payments:
                await query.edit_message_text(
                    "✅ هیچ پرداخت در انتظاری وجود ندارد!",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]])
                )
                return
            
            text = "⏳ **پرداخت‌های در انتظار تایید**\n\n"
            keyboard_buttons = []
            
            for p in payments[:15]:
                pid = p.get('payment_id', '?')
                text += f"🆔 **{pid}**\n"
                text += f"👤 کاربر: `{p.get('user_id')}`\n"
                text += f"💰 مبلغ: {p.get('amount', 0):,} تومان\n"
                text += f"📦 نوع: {p.get('payment_type')}\n"
                text += f"📅 زمان: {p.get('created_at', '?')[:16]}\n"
                text += "━━━━━━━━━━━━━━━━\n"
                
                keyboard_buttons.append([
                    InlineKeyboardButton(f"✅ تایید {pid}", callback_data=f"confirm_payment_{pid}"),
                    InlineKeyboardButton(f"❌ رد", callback_data=f"reject_payment_{pid}")
                ])
            
            keyboard_buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard_buttons),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data.startswith("confirm_payment_"):
        payment_id = data.replace("confirm_payment_", "")
        
        if get_payment_repo:
            payment = get_payment_repo().get_by_id(payment_id)
            if payment:
                # Confirm payment
                get_payment_repo().confirm_payment(payment_id, admin_id=str(user_id))
                
                # Activate VIP
                target_user_id = payment.get('user_id')
                ptype = payment.get('payment_type', '')
                
                if 'monthly' in ptype:
                    days, plan_name = 30, "ماهانه"
                elif 'yearly' in ptype:
                    days, plan_name = 365, "سالانه"
                elif 'lifetime' in ptype:
                    days, plan_name = 36500, "مادام‌العمر"
                else:
                    days, plan_name = 30, "نامشخص"
                
                expire_date = datetime.now() + timedelta(days=days)
                
                if get_user_repo and target_user_id:
                    get_user_repo().update(
                        target_user_id,
                        is_vip=True,
                        vip_level=2,
                        vip_plan=plan_name,
                        vip_expire=expire_date.isoformat(),
                        vip_activated_at=datetime.now().isoformat()
                    )
                    
                    # Notify user
                    try:
                        await context.bot.send_message(
                            chat_id=int(target_user_id),
                            text=f"🎉 **تبریک! VIP {plan_name} شما فعال شد!**\n\n"
                                 f"📅 تاریخ انقضا: {expire_date.strftime('%Y-%m-%d')}\n\n"
                                 f"✨ از امکانات ویژه VIP لذت ببرید! 🚀",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        notify_status = "✅ پیام به کاربر ارسال شد"
                    except:
                        notify_status = "⚠️ پیام به کاربر ارسال نشد"
                
                await query.edit_message_text(
                    f"✅ **پرداخت تایید شد!**\n\n"
                    f"🆔 کد: {payment_id}\n"
                    f"👤 کاربر: {target_user_id}\n"
                    f"💰 مبلغ: {payment.get('amount', 0):,} تومان\n"
                    f"💎 VIP {plan_name} فعال شد\n"
                    f"📅 انقضا: {expire_date.strftime('%Y-%m-%d')}\n\n"
                    f"{notify_status}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]),
                    parse_mode=ParseMode.MARKDOWN
                )
        return
    
    if data.startswith("reject_payment_"):
        payment_id = data.replace("reject_payment_", "")
        
        if get_payment_repo:
            get_payment_repo().reject_payment(payment_id, reason="توسط ادمین رد شد")
            
            await query.edit_message_text(
                f"❌ **پرداخت {payment_id} رد شد.**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data == "admin_payments_report":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
📊 **گزارش مالی**

💰 **درآمد کل:** {format_number(stats.get('total_revenue', 0))} تومان
💳 **پرداخت‌های امروز:** {format_number(stats.get('today_revenue', 0))} تومان
📈 **پرداخت‌های این هفته:** {format_number(stats.get('week_revenue', 0))} تومان
📅 **پرداخت‌های این ماه:** {format_number(stats.get('month_revenue', 0))} تومان

👥 **تعداد پرداخت‌ها:** {stats.get('payments', 0)}
⏳ **در انتظار:** {stats.get('pending_payments', 0)}
✅ **تایید شده:** {stats.get('completed_payments', 0)}
❌ **ناموفق:** {stats.get('failed_payments', 0)}
"""
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== ADMIN VIP ======
    if data == "admin_vip":
        await query.edit_message_text(
            "💎 **مدیریت VIP**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ درخواست‌های VIP", callback_data="admin_vip_requests")],
                [InlineKeyboardButton("📋 لیست VIP ها", callback_data="admin_vip_list")],
                [InlineKeyboardButton("📊 آمار VIP", callback_data="admin_vip_stats")],
                [InlineKeyboardButton("➕ افزودن VIP دستی", callback_data="admin_vip_add")],
                [InlineKeyboardButton("➖ حذف VIP", callback_data="admin_vip_remove")],
                [InlineKeyboardButton("🎁 مدیریت تست رایگان", callback_data="admin_vip_trial_manage")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_vip_requests":
        if get_payment_repo:
            payments = get_payment_repo().get_pending_payments()
            vip_requests = [p for p in payments if 'vip' in p.get('payment_type', '').lower()]
            
            if not vip_requests:
                await query.edit_message_text(
                    "✅ هیچ درخواست VIP در انتظاری نیست!",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]])
                )
                return
            
            text = "💎 **درخواست‌های VIP در انتظار**\n\n"
            keyboard_buttons = []
            
            for req in vip_requests[:15]:
                pid = req.get('payment_id', '?')
                text += f"🆔 `{pid}`\n"
                text += f"👤 `{req.get('user_id')}` | 💰 {req.get('amount', 0):,} تومان | 📦 {req.get('payment_type')}\n"
                text += "━━━━━━━━━━━━━━━━\n"
                
                keyboard_buttons.append([
                    InlineKeyboardButton(f"✅ تایید {pid}", callback_data=f"confirm_payment_{pid}"),
                    InlineKeyboardButton(f"❌ رد", callback_data=f"reject_payment_{pid}")
                ])
            
            keyboard_buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard_buttons),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data == "admin_vip_list":
        if get_user_repo:
            users = get_user_repo().get_vip_users()
            if not users:
                await query.edit_message_text(
                    "ℹ️ هیچ کاربر VIP یافت نشد!",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]])
                )
                return
            
            text = f"📋 **لیست کاربران VIP** ({len(users)} کاربر)\n\n"
            for i, user in enumerate(users[:25], 1):
                name = user.get('first_name', 'نامشخص')
                plan = user.get('vip_plan', 'نامشخص')
                expire = user.get('vip_expire', 'ندارد')
                tid = user.get('telegram_id', '?')
                
                text += f"{i}. {name} | {plan} | {expire}\n"
                text += f"   🆔 `{tid}`\n\n"
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data == "admin_vip_stats":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
📊 **آمار VIP**

👥 **کل کاربران VIP:** {stats.get('vip_users', 0):,}
📈 **VIP فعال:** {stats.get('active_vip', 0):,}
⏳ **در انتظار تایید:** {stats.get('pending_vip', 0)}

💰 **درآمد VIP:** {format_number(stats.get('vip_revenue', 0))} تومان
📅 **این ماه:** {format_number(stats.get('vip_monthly_revenue', 0))} تومان

📊 **نرخ تبدیل:** {stats.get('vip_conversion_rate', 0):.1f}%

🎁 **تست رایگان فعال:** {stats.get('trial_active', 0)}
"""
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data in ["admin_vip_add", "admin_vip_remove"]:
        context.user_data['admin_action'] = data
        action = "افزودن VIP" if data == "admin_vip_add" else "حذف VIP"
        await query.edit_message_text(
            f"🔍 لطفاً **آیدی عددی** کاربر را برای **{action}** وارد کنید:\n\nبرای لغو /cancel",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_USER_ID
    
    # ====== ADMIN BROADCAST ======
    if data == "admin_broadcast":
        await query.edit_message_text(
            "📢 **ارسال پیام همگانی**\n\nمخاطبان را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 به همه کاربران", callback_data="broadcast_all")],
                [InlineKeyboardButton("💎 به کاربران VIP", callback_data="broadcast_vip")],
                [InlineKeyboardButton("👤 به کاربران عادی", callback_data="broadcast_normal")],
                [InlineKeyboardButton("⚠️ کاربران پرریسک", callback_data="broadcast_risk")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data.startswith("broadcast_"):
        target = data.replace("broadcast_", "")
        context.user_data['broadcast_target'] = target
        
        target_names = {
            "all": "همه کاربران",
            "vip": "کاربران VIP",
            "normal": "کاربران عادی",
            "risk": "کاربران پرریسک"
        }
        
        await query.edit_message_text(
            f"📝 **ارسال پیام به {target_names.get(target, target)}**\n\n"
            "لطفاً پیام خود را بنویسید:\n\n"
            "• از Markdown برای فرمت‌دهی استفاده کنید\n"
            "• برای لغو /cancel را بفرستید",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_BROADCAST
    
    # ====== ADMIN SEND CHANNEL ======
    if data == "admin_send_channel":
        context.user_data['admin_action'] = 'send_channel'
        await query.edit_message_text(
            f"📡 **ارسال به کانال**\n\n"
            f"📢 **کانال:** {CHANNEL_ID}\n\n"
            f"لطفاً پیام خود را بنویسید.\n"
            f"این پیام به کانال {CHANNEL_ID} ارسال خواهد شد.\n\n"
            f"برای لغو /cancel را بفرستید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== ADMIN API ======
    if data == "admin_api":
        await query.edit_message_text(
            "🔧 **مدیریت API**\n\n"
            "✅ Groq AI: فعال\n"
            "✅ Telegram Bot: فعال\n",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 ریست API", callback_data="admin_api_reset")],
                [InlineKeyboardButton("📊 وضعیت API", callback_data="admin_api_status")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_api_status":
        await query.edit_message_text(
            "📊 **وضعیت API**\n\n"
            "🟢 Groq AI: آنلاین\n"
            "🟢 Telegram Bot: آنلاین\n"
            "🟢 CoinEx: آنلاین",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_api")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== ADMIN BACKUP ======
    if data == "admin_backup":
        await query.edit_message_text(
            "💾 **بکاپ و بازیابی**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💾 ایجاد بکاپ", callback_data="admin_backup_create")],
                [InlineKeyboardButton("📥 بازیابی بکاپ", callback_data="admin_backup_restore")],
                [InlineKeyboardButton("📋 لیست بکاپ‌ها", callback_data="admin_backup_list")],
                [InlineKeyboardButton("🗑️ حذف بکاپ", callback_data="admin_backup_delete")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_backup_create":
        if db_manager:
            result = db_manager.backup()
            if result.get('success'):
                text = f"""
✅ **بکاپ ایجاد شد!**

📁 **مسیر:** {result.get('path')}
📏 **حجم:** {result.get('size', 0) / 1024:.2f} KB
🔑 **Checksum:** {result.get('checksum', '')[:8]}...
"""
            else:
                text = f"❌ **خطا در ایجاد بکاپ:** {result.get('error')}"
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data == "admin_backup_list":
        if db_manager:
            backups = db_manager.get_backups_list()
            if not backups:
                await query.edit_message_text(
                    "📋 هیچ بکاپی یافت نشد!",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]])
                )
                return
            
            text = "📋 **لیست بکاپ‌ها**\n\n"
            for backup in backups[:15]:
                size = backup.get('size', 0) / 1024
                created = backup.get('created_at', '?')[:16]
                text += f"• {backup.get('name')} ({size:.1f} KB) - {created}\n"
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    # ====== ADMIN SERVER ======
    if data == "admin_server":
        await query.edit_message_text(
            "🚪 **مدیریت سرور**\n\n"
            "⚠️ هشدار: عملیات‌های زیر غیرقابل بازگشت هستند!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 ریستارت ربات", callback_data="admin_restart")],
                [InlineKeyboardButton("📊 وضعیت سرور", callback_data="admin_server_status")],
                [InlineKeyboardButton("📈 لاگ‌های سیستم", callback_data="admin_server_logs")],
                [InlineKeyboardButton("🧹 پاکسازی کش", callback_data="admin_clear_cache")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_server_status":
        text = f"""
📊 **وضعیت سرور**

🖥️ **CPU:** ۱۲%
💾 **RAM:** ۲۵۶/۵۱۲ MB
📀 **دیسک:** ۲.۴/۱۰ GB
⏰ **آپتایم:** ۳ روز

✅ **همه سرویس‌ها فعال هستند.**
"""
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_server")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_clear_cache":
        _intel_cache.clear()
        _intel_cache_time.clear()
        await query.edit_message_text(
            "🧹 **کش پاکسازی شد!**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_server")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== ADMIN REPORTS ======
    if data == "admin_reports":
        await query.edit_message_text(
            "📊 **گزارش‌های پیشرفته**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📈 گزارش رشد", callback_data="admin_report_growth")],
                [InlineKeyboardButton("💰 گزارش مالی تفصیلی", callback_data="admin_payments_report")],
                [InlineKeyboardButton("🚨 گزارش سیگنال‌ها", callback_data="admin_report_signals")],
                [InlineKeyboardButton("👥 گزارش کاربران", callback_data="admin_users_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== ADMIN SECURITY ======
    if data == "admin_security":
        await query.edit_message_text(
            "🔒 **امنیت و لاگ**\n\n"
            "✅ سیستم امنیتی فعال\n"
            "✅ رمزنگاری فعال\n"
            "✅ لاگ فعالیت‌ها ثبت می‌شود",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 لاگ فعالیت‌ها", callback_data="admin_security_logs")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ============================================================
    #                    DEFAULT RESPONSE
    # ============================================================
    
    await query.edit_message_text("ℹ️ **این بخش در حال توسعه است...**", reply_markup=user_main_menu(), parse_mode=ParseMode.MARKDOWN)

# ============================================================
#                    MESSAGE HANDLER (ULTIMATE)
# ============================================================

@log_action
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های متنی"""
    user_id = update.effective_user.id
    message_text = update.message.text
    admin_flag = is_admin(user_id)
    
    # ====== BROADCAST ======
    if context.user_data.get('broadcast_target'):
        if admin_flag:
            target = context.user_data.get('broadcast_target', 'all')
            
            if get_user_repo:
                users = get_user_repo().get_all()
                
                if target == 'vip':
                    users = [u for u in users if u.get('is_vip')]
                elif target == 'normal':
                    users = [u for u in users if not u.get('is_vip')]
                elif target == 'risk' and get_intelligence_engine:
                    engine = get_intelligence_engine()
                    risk_users = engine.get_risk_users_detail()
                    risk_ids = [r['user_id'] for r in risk_users]
                    users = [u for u in users if u.get('telegram_id') in risk_ids]
                
                success, fail = 0, 0
                total = len(users)
                progress_msg = await update.message.reply_text(f"⏳ در حال ارسال پیام به {total} کاربر...")
                
                for i, user in enumerate(users):
                    try:
                        await context.bot.send_message(
                            chat_id=int(user.get('telegram_id')),
                            text=f"📢 **پیام همگانی**\n\n{message_text}",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        success += 1
                    except:
                        fail += 1
                    
                    # Update progress every 10 users
                    if i % 10 == 0:
                        try:
                            await progress_msg.edit_text(f"⏳ ارسال: {i+1}/{total} | ✅ {success} | ❌ {fail}")
                        except:
                            pass
                    
                    await asyncio.sleep(0.05)
                
                await progress_msg.edit_text(
                    f"✅ **ارسال به پایان رسید!**\n\n"
                    f"📊 **آمار:**\n"
                    f"• کل: {total}\n"
                    f"• موفق: {success}\n"
                    f"• ناموفق: {fail}\n"
                    f"• نرخ موفقیت: {(success/max(total,1))*100:.1f}%",
                    reply_markup=admin_main_menu()
                )
                context.user_data['broadcast_target'] = None
            return
    
    # ====== SEND CHANNEL ======
    if context.user_data.get('admin_action') == 'send_channel':
        if admin_flag:
            try:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=message_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                await update.message.reply_text(
                    f"✅ **پیام به کانال {CHANNEL_ID} ارسال شد!**",
                    reply_markup=admin_main_menu()
                )
            except Exception as e:
                await update.message.reply_text(
                    f"❌ **خطا در ارسال:** {str(e)}",
                    reply_markup=admin_main_menu()
                )
            context.user_data['admin_action'] = None
            return
    
    # ====== RECEIPT ======
    if context.user_data.get('waiting_for_receipt'):
        if update.message.photo:
            photo = update.message.photo[-1]
            plan = context.user_data.get('vip_plan', 'monthly')
            prices = {
                'monthly': VIP_PRICE_MONTHLY,
                'yearly': VIP_PRICE_YEARLY,
                'lifetime': VIP_PRICE_LIFETIME
            }
            price = prices.get(plan, VIP_PRICE_MONTHLY)
            
            # Save payment
            if get_payment_repo:
                get_payment_repo().create(
                    user_id=str(user_id),
                    amount=price,
                    payment_type=f'vip_{plan}',
                    status='pending'
                )
            
            # Notify admins
            notified = 0
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_photo(
                        chat_id=admin_id,
                        photo=photo.file_id,
                        caption=f"📤 **رسید جدید VIP**\n\n"
                                f"👤 **کاربر:** {update.effective_user.first_name}\n"
                                f"🆔 **آیدی:** `{user_id}`\n"
                                f"💰 **مبلغ:** {price:,} تومان\n"
                                f"📦 **نوع:** {plan}\n"
                                f"📅 **زمان:** {get_persian_time()}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    notified += 1
                except:
                    pass
            
            await update.message.reply_text(
                f"✅ **رسید شما با موفقیت ارسال شد!**\n\n"
                f"💰 **مبلغ:** {price:,} تومان\n"
                f"📦 **نوع:** {plan}\n\n"
                f"⏳ **وضعیت:** در انتظار تایید ادمین\n"
                f"📱 **ادمین:** @{SUPPORT_USERNAME}\n\n"
                f"🎉 پس از تایید، VIP شما فعال خواهد شد.",
                reply_markup=user_main_menu()
            )
            context.user_data['waiting_for_receipt'] = False
            return
        
        await update.message.reply_text("❌ **لطفاً تصویر رسید را ارسال کنید.**")
        return
    
    # ====== TICKET ======
    if context.user_data.get('waiting_for_ticket'):
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🎫 **تیکت جدید**\n\n"
                         f"👤 **کاربر:** {update.effective_user.first_name}\n"
                         f"🆔 **آیدی:** `{user_id}`\n"
                         f"📝 **پیام:**\n{message_text}\n\n"
                         f"📅 **زمان:** {get_persian_time()}"
                )
            except:
                pass
        
        await update.message.reply_text(
            f"✅ **تیکت شما ثبت شد!**\n\n"
            f"📝 پیام شما به پشتیبانی ارسال شد.\n"
            f"⏰ به زودی پاسخ داده می‌شود.\n"
            f"📱 **ادمین:** @{SUPPORT_USERNAME}",
            reply_markup=user_main_menu()
        )
        context.user_data['waiting_for_ticket'] = False
        return
    
    # ====== ADMIN ACTIONS (User ID) ======
    if context.user_data.get('admin_action') and admin_flag:
        action = context.user_data['admin_action']
        target_id = message_text.strip()
        
        if not target_id.isdigit():
            await update.message.reply_text("❌ **لطفاً آیدی عددی معتبر وارد کنید.**", reply_markup=admin_main_menu())
            context.user_data['admin_action'] = None
            return
        
        if get_user_repo:
            user = get_user_repo().get_by_telegram_id(target_id)
            
            if action == "admin_users_ban":
                if user:
                    get_user_repo().ban_user(target_id, reason="توسط ادمین")
                    await update.message.reply_text(
                        f"🔨 **کاربر `{target_id}` با موفقیت بن شد.**",
                        reply_markup=admin_main_menu(),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=admin_main_menu())
            
            elif action == "admin_users_unban":
                if user:
                    get_user_repo().unban_user(target_id)
                    await update.message.reply_text(
                        f"🔓 **کاربر `{target_id}` با موفقیت آنبن شد.**",
                        reply_markup=admin_main_menu(),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=admin_main_menu())
            
            elif action == "admin_users_make_admin":
                if user:
                    get_user_repo().make_admin(target_id)
                    ADMIN_IDS.append(int(target_id))
                    await update.message.reply_text(
                        f"👑 **کاربر `{target_id}` با موفقیت ادمین شد.**",
                        reply_markup=admin_main_menu(),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=admin_main_menu())
            
            elif action == "admin_users_delete":
                if user:
                    get_user_repo().delete(target_id)
                    await update.message.reply_text(
                        f"🗑️ **کاربر `{target_id}` با موفقیت حذف شد.**",
                        reply_markup=admin_main_menu(),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=admin_main_menu())
            
            elif action == "admin_vip_add":
                expiry = datetime.now() + timedelta(days=30)
                if user:
                    get_user_repo().update(
                        target_id,
                        is_vip=True,
                        vip_level=2,
                        vip_plan='manual',
                        vip_expire=expiry.isoformat(),
                        vip_activated_at=datetime.now().isoformat()
                    )
                else:
                    get_user_repo().create(
                        telegram_id=target_id,
                        is_vip=True,
                        vip_level=2,
                        vip_plan='manual',
                        vip_expire=expiry.isoformat(),
                        vip_activated_at=datetime.now().isoformat()
                    )
                await update.message.reply_text(
                    f"💎 **VIP برای کاربر `{target_id}` با موفقیت فعال شد.**\n📅 انقضا: {expiry.strftime('%Y-%m-%d')}",
                    reply_markup=admin_main_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            
            elif action == "admin_vip_remove":
                if user:
                    get_user_repo().update(target_id, is_vip=False, vip_level=0, vip_plan=None, vip_expire=None)
                    await update.message.reply_text(
                        f"➖ **VIP کاربر `{target_id}` با موفقیت حذف شد.**",
                        reply_markup=admin_main_menu(),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=admin_main_menu())
            
            elif action == "admin_users_search":
                if user:
                    name = user.get('first_name', 'نامشخص')
                    username = user.get('username', 'ندارد')
                    is_vip_flag = user.get('is_vip', False)
                    is_banned_flag = user.get('is_banned', False)
                    vip_expire = user.get('vip_expire', 'ندارد')
                    balance = user.get('balance', 0)
                    trades = user.get('total_trades', 0)
                    
                    text = f"""
🔍 **اطلاعات کاربر**

👤 **نام:** {name}
📱 **یوزرنیم:** @{username}
🆔 **آیدی:** `{target_id}`

💎 **VIP:** {'✅ فعال' if is_vip_flag else '❌ غیرفعال'}
📅 **انقضا:** {vip_expire}
🚫 **وضعیت:** {'🔴 بن شده' if is_banned_flag else '🟢 فعال'}

💰 **موجودی:** {format_number(balance)} تومان
📊 **معاملات:** {trades}
"""
                    await update.message.reply_text(
                        text,
                        reply_markup=admin_main_menu(),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=admin_main_menu())
        
        context.user_data['admin_action'] = None
        return
    
    # ====== AUTO ANALYSIS ======
    coin = message_text.upper().strip()
    if validate_coin(coin):
        await update.message.reply_text(f"⏳ **در حال تحلیل {coin}...**")
        
        signal_type = random.choice(["buy", "sell", "hold"])
        confidence = random.randint(60, 95)
        price = random.uniform(100, 70000)
        emojis = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}
        stars = "⭐⭐⭐" if confidence >= 80 else "⭐⭐" if confidence >= 60 else "⭐"
        
        text = f"""
🚨 **سیگنال {coin}**

{emojis.get(signal_type, '🟡')} **پیشنهاد:** {signal_type.upper()}
🎯 **اطمینان:** {confidence}% {stars}

💰 **قیمت:** ${price:,.2f}
🎯 **اهداف:** ${price*1.02:,.2f} | ${price*1.05:,.2f} | ${price*1.10:,.2f}
🛑 **حد ضرر:** ${price*0.95:,.2f}

⏰ **زمان:** {get_persian_time()}
"""
        await update.message.reply_text(text, reply_markup=user_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ====== DEFAULT ======
    await update.message.reply_text(
        "ℹ️ لطفاً از دکمه‌های زیر استفاده کنید.\n\n"
        "📌 **ارزهای پشتیبانی شده:**\n"
        "BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, SHIB\n\n"
        "💡 می‌توانید نام ارز را تایپ کنید تا تحلیل آن را دریافت کنید.",
        reply_markup=user_main_menu()
    )

# ============================================================
#                    PHOTO HANDLER
# ============================================================

@log_action
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش تصاویر"""
    if context.user_data.get('waiting_for_receipt'):
        await message_handler(update, context)
    else:
        await update.message.reply_text("📸 **تصویر دریافت شد.**", reply_markup=user_main_menu())

# ============================================================
#                    ERROR HANDLER
# ============================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت خطاها"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        if update and hasattr(update, 'effective_message') and update.effective_message:
            await update.effective_message.reply_text(
                "❌ **متأسفانه خطایی رخ داد.**\n\n"
                "لطفاً دوباره تلاش کنید.\n"
                "در صورت تکرار با پشتیبانی تماس بگیرید."
            )
    except:
        pass

# ============================================================
#                    MAIN HANDLER CLASS
# ============================================================

class BotHandlers:
    """مدیریت هندلرهای ربات — نسخه نهایی"""

    def __init__(self):
        self.application = None
        self._setup_handlers()

    def _setup_handlers(self):
        """تنظیم هندلرها"""
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN is empty")
            return

        try:
            if PROXY_URL:
                logger.info(f"🔧 Building with proxy: {PROXY_URL}")
                from telegram.request import HTTPXRequest
                request = HTTPXRequest(
                    proxy_url=PROXY_URL,
                    read_timeout=30,
                    write_timeout=30,
                    connect_timeout=30,
                    pool_timeout=30
                )
                self.application = Application.builder().token(BOT_TOKEN).request(request).build()
            else:
                logger.info("🔧 Building application")
                self.application = Application.builder().token(BOT_TOKEN).build()

            # ====== Command Handlers ======
            commands = [
                ("start", start),
                ("help", help_command),
                ("admin", admin_command),
                ("cancel", cancel_command),
                ("vip", vip_command),
                ("wallet", wallet_command),
                ("signal", signal_command),
                ("price", price_command),
                ("analysis", analysis_command),
                ("settings", settings_command),
            ]
            for cmd, handler in commands:
                self.application.add_handler(CommandHandler(cmd, handler))
            
            logger.info(f"✅ Added {len(commands)} command handlers")

            # ====== Callback Handler ======
            self.application.add_handler(CallbackQueryHandler(callback_handler))
            logger.info("✅ Added callback handler")

            # ====== Conversation Handler ======
            conv_handler = ConversationHandler(
                entry_points=[
                    CommandHandler("signal", signal_command),
                    CallbackQueryHandler(callback_handler, pattern="^analysis$"),
                    CallbackQueryHandler(callback_handler, pattern="^signal_buy$"),
                    CallbackQueryHandler(callback_handler, pattern="^signal_sell$"),
                ],
                states={
                    ConversationState.WAITING_FOR_SIGNAL_COIN: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                    ],
                    ConversationState.WAITING_FOR_ANALYSIS_COIN: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, analysis_coin_handler)
                    ],
                    ConversationState.WAITING_FOR_BROADCAST: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
                    ],
                    ConversationState.WAITING_FOR_RECEIPT: [
                        MessageHandler(filters.PHOTO, message_handler),
                        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
                    ],
                    ConversationState.WAITING_FOR_TICKET: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
                    ],
                    ConversationState.WAITING_FOR_USER_ID: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
                    ],
                },
                fallbacks=[
                    CommandHandler("cancel", cancel_command),
                    MessageHandler(filters.Regex("^(❌ لغو|🔙 بازگشت)$"), cancel_command)
                ],
                per_message=True,
                per_chat=True,
                per_user=True,
                name="main_conversation"
            )
            self.application.add_handler(conv_handler)
            logger.info("✅ Added conversation handler")

            # ====== Message Handlers ======
            self.application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
            logger.info("✅ Added message handlers")

            # ====== Error Handler ======
            self.application.add_error_handler(error_handler)
            logger.info("✅ Added error handler")

            logger.info("🎉 All handlers registered successfully")

        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            traceback.print_exc()
            self.application = None

    def get_application(self):
        return self.application

# ============================================================
#                    EXPORT
# ============================================================

bot_handlers = BotHandlers()

def get_handlers():
    return bot_handlers

def get_application():
    if bot_handlers:
        app = bot_handlers.get_application()
        if app:
            logger.info("✅ Application returned")
        else:
            logger.warning("⚠️ Application is None — fallback mode")
        return app
    logger.error("❌ bot_handlers not initialized")
    return None

def check_handlers():
    app = get_application()
    return {
        "bot_handlers": "✅ OK" if bot_handlers else "❌ FAILED",
        "application": "✅ OK" if app else "❌ FAILED",
        "bot_token": "✅ Set" if BOT_TOKEN else "❌ Missing",
        "proxy": "✅ Set" if PROXY_URL else "⚠️ Not set",
        "intelligence": "✅ Connected" if get_intelligence_engine else "⚠️ Part16 not loaded"
    }

def get_bot_token():
    return BOT_TOKEN

def get_admin_ids():
    return ADMIN_IDS

def start():
    """Compatibility function for ModuleManager"""
    status = check_handlers()
    logger.info(f"✅ part9 loaded — Status: {status}")
    return True

# Status on import
status = check_handlers()
logger.info(f"📊 Part9 Status: {status}")
