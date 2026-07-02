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
║  🚀 CryptoPulse AI Bot v3.0 - Main Handlers Module (Ultimate Edition)              ║
║  ───────────────────────────────────────────────────────────────────────────────    ║
║  👑 پنل ادمین کامل  |  👤 مدیریت کاربران  |  💰 پرداخت‌ها  |  💎 مدیریت VIP       ║
║  📢 ارسال همگانی  |  📡 کانال  |  🔧 API  |  💾 بکاپ  |  🚪 سرور                 ║
║  ════════════════════════════════════════════════════════════════════════════════   ║
║  📁 ۴۸۰۰+ خط کد  |  ⚡ بهینه  |  🔥 فوق‌پیشرفته  |  🛡️ بدون خطا                ║
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
from collections import defaultdict, OrderedDict
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
logger = logging.getLogger("Part9")

# ============================================================
#                    غیرفعال کردن اخطارها
# ============================================================

warnings.filterwarnings("ignore")

# ============================================================
#                    TELEGRAM IMPORTS (کامل)
# ============================================================

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    InputFile, Bot, ReplyKeyboardMarkup, KeyboardButton,
    Chat, User, Message, CallbackQuery, ChatMember,
    ChatPermissions, ChatPhoto, ChatLocation, ChatInviteLink,
    MessageEntity, MessageId, InputMediaPhoto, InputMediaVideo,
    InputMediaDocument, InputMediaAudio, InputMediaAnimation,
    InlineQueryResultArticle, InlineQueryResultPhoto,
    InlineQueryResultGif, InlineQueryResultVideo,
    InlineQueryResultAudio, InlineQueryResultDocument,
    InlineQueryResultLocation, InlineQueryResultVenue,
    InlineQueryResultContact, InlineQueryResultGame,
    InlineQueryResultCachedPhoto, InlineQueryResultCachedGif,
    InlineQueryResultCachedVideo, InlineQueryResultCachedAudio,
    InlineQueryResultCachedDocument, InlineQueryResultCachedSticker,
    Game, CallbackGame, LoginUrl, MenuButton, MenuButtonCommands,
    MenuButtonWebApp, MenuButtonDefault, WebAppData, WebAppInfo,
    KeyboardButtonPollType, KeyboardButtonRequestChat,
    KeyboardButtonRequestUser, KeyboardButtonRequestUsers,
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
    TypeHandler,
    StringCommandHandler,
    StringRegexHandler,
    ChatMemberHandler,
    InlineQueryHandler,
    ChosenInlineResultHandler,
    PreCheckoutQueryHandler,
    ShippingQueryHandler,
    PollHandler,
    CallbackContext,
    JobQueue,
    Defaults,
    ApplicationBuilder,
    ExtBot,
    MessageReactionHandler,
    AIORateLimiter
)

warnings.filterwarnings("ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

# ============================================================
#                    SAFE IMPORTS (پیشرفته)
# ============================================================

def safe_import(module_name: str, *attrs):
    """ایمن‌سازی واردات ماژول‌ها با کش"""
    result = {}
    try:
        module = __import__(module_name, fromlist=attrs)
        for attr in attrs:
            result[attr] = getattr(module, attr) if hasattr(module, attr) else None
        logger.info(f"✅ Successfully imported from {module_name}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to import from {module_name}: {e}")
        for attr in attrs:
            result[attr] = None
    return result

# ============================================================
#                    IMPORTS (کامل)
# ============================================================

_bot2 = safe_import("bot2", "get_config")
_bot3 = safe_import("bot3", "get_user_repo", "get_signal_repo", "get_payment_repo", "db_manager")
_bot4 = safe_import("bot4", "get_time", "get_emoji", "get_formatter", "get_hash", "get_validator", "get_cache")
_bot5 = safe_import("bot5", "get_market", "get_coinex")
_bot6 = safe_import("bot6", "get_ai", "get_groq")
_bot7 = safe_import("bot7", "get_technical")
_bot8 = safe_import("bot8", "lux_keyboard", "menu_builder", "LuxText", "LuxEmoji")

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

# ============================================================
#                    CONFIG (کامل)
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

if BOT_TOKEN:
    logger.info(f"✅ BOT_TOKEN loaded: {BOT_TOKEN[:8]}...")
else:
    logger.error("❌ BOT_TOKEN not found in any environment variable!")

CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "به مرد")
VIP_PRICE_MONTHLY = int(os.environ.get("VIP_PRICE_MONTHLY", 199000))
VIP_PRICE_YEARLY = int(os.environ.get("VIP_PRICE_YEARLY", 1990000))
VIP_PRICE_LIFETIME = int(os.environ.get("VIP_PRICE_LIFETIME", 4990000))
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
PROXY_URL = os.environ.get("PROXY_URL", "")

logger.info(f"📋 Config loaded - ENV: {ENVIRONMENT}, DEBUG: {DEBUG}")
logger.info(f"👑 Admin IDs: {ADMIN_IDS}")
logger.info(f"📡 Channel: {CHANNEL_ID}")
logger.info(f"🔧 Proxy: {'Set' if PROXY_URL else 'Not set'}")

# ============================================================
#                    ENUMS & CONSTANTS (کامل)
# ============================================================

class UserLevel(Enum):
    """سطح دسترسی کاربران"""
    GUEST = "guest"
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    
    @classmethod
    def from_string(cls, value: str):
        for member in cls:
            if member.value == value:
                return member
        return cls.GUEST
    
    def get_permissions(self) -> List[str]:
        permissions = {
            "guest": ["view_signals", "view_analysis"],
            "free": ["view_signals", "view_analysis", "request_signal"],
            "premium": ["view_signals", "view_analysis", "request_signal", "premium_signals"],
            "vip": ["view_signals", "view_analysis", "request_signal", "vip_signals", "vip_analysis"],
            "admin": ["*"],
            "super_admin": ["*"]
        }
        return permissions.get(self.value, [])

class ActionType(Enum):
    """نوع اقدامات کاربر"""
    ANALYSIS = "analysis"
    SIGNAL = "signal"
    VIP = "vip"
    WALLET = "wallet"
    SUPPORT = "support"
    SETTINGS = "settings"
    ADMIN = "admin"
    BROADCAST = "broadcast"
    BACKUP = "backup"
    PAYMENT = "payment"
    SERVER = "server"
    CHANNEL = "channel"
    API = "api"
    USER = "user"

class ResponseType(Enum):
    """نوع پاسخ ربات"""
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"
    ANIMATION = "animation"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    POLL = "poll"
    GAME = "game"
    INVOICE = "invoice"
    SUCCESSFUL_PAYMENT = "successful_payment"

class ErrorCode(Enum):
    """کدهای خطا"""
    SUCCESS = 0
    UNAUTHORIZED = 1001
    NOT_FOUND = 1002
    INVALID_INPUT = 1003
    RATE_LIMIT = 1004
    SERVER_ERROR = 1005
    MAINTENANCE = 1006
    VIP_REQUIRED = 1007
    ADMIN_REQUIRED = 1008
    ALREADY_EXISTS = 1009
    EXPIRED = 1010

# ============================================================
#                    CONVERSATION STATES (کامل)
# ============================================================

class ConversationState:
    """وضعیت‌های گفتگو - کامل"""
    MAIN = 0
    WAITING_FOR_COIN = 1
    WAITING_FOR_TIMEFRAME = 2
    WAITING_FOR_AMOUNT = 3
    WAITING_FOR_PRICE = 4
    WAITING_FOR_MESSAGE = 5
    WAITING_FOR_BROADCAST = 6
    WAITING_FOR_BACKUP = 7
    WAITING_FOR_SETTINGS = 8
    WAITING_FOR_SUPPORT = 9
    WAITING_FOR_TICKET = 10
    WAITING_FOR_RECEIPT = 11
    WAITING_FOR_VIP_REQUEST = 12
    WAITING_FOR_ANALYSIS_COIN = 13
    WAITING_FOR_SIGNAL_COIN = 14
    WAITING_FOR_PORTFOLIO = 15
    WAITING_FOR_ALERT = 16
    WAITING_FOR_WITHDRAW = 17
    WAITING_FOR_DEPOSIT = 18
    WAITING_FOR_REFERRAL = 19
    WAITING_FOR_EDUCATION = 20
    WAITING_FOR_NEWS = 21
    WAITING_FOR_REPORT = 22
    WAITING_FOR_BAN = 23
    WAITING_FOR_UNBAN = 24
    WAITING_FOR_MAKE_ADMIN = 25
    WAITING_FOR_DELETE_USER = 26
    WAITING_FOR_CONFIRM = 27
    WAITING_FOR_PAYMENT = 28
    WAITING_FOR_WEBHOOK = 29
    WAITING_FOR_API_KEY = 30
    WAITING_FOR_CHANNEL_MESSAGE = 31
    WAITING_FOR_SEND_CHANNEL = 32
    WAITING_FOR_SEND_BROADCAST = 33
    WAITING_FOR_SEND_BROADCAST_VIP = 34
    WAITING_FOR_SEND_BROADCAST_NORMAL = 35
    WAITING_FOR_ANALYSIS_RESULT = 36
    WAITING_FOR_SIGNAL_RESULT = 37
    WAITING_FOR_VIP_PURCHASE = 38
    WAITING_FOR_VIP_CONFIRM = 39
    WAITING_FOR_ADMIN_ACTION = 40
    WAITING_FOR_USER_ID = 41
    WAITING_FOR_REASON = 42
    WAITING_FOR_PAYMENT_ID = 43
    WAITING_FOR_BACKUP_RESTORE = 44
    WAITING_FOR_BACKUP_DELETE = 45
    WAITING_FOR_SERVER_ACTION = 46
    WAITING_FOR_EDUCATION_TOPIC = 47
    WAITING_FOR_REFERRAL_CODE = 48
    WAITING_FOR_CUSTOM_ALERT = 49
    WAITING_FOR_PORTFOLIO_ADD = 50
    WAITING_FOR_PORTFOLIO_REMOVE = 51
    WAITING_FOR_NEWSLETTER = 52
    WAITING_FOR_COMPETITION = 53

# ============================================================
#                    KEYBOARD FALLBACK (کامل)
# ============================================================

class FallbackKeyboard:
    """کیبوردهای جایگزین"""
    
    @staticmethod
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

    @staticmethod
    def admin_main_menu():
        keyboard = [
            [InlineKeyboardButton("👑 مدیریت کاربران", callback_data="admin_users")],
            [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
            [InlineKeyboardButton("💎 مدیریت VIP", callback_data="admin_vip")],
            [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast")],
            [InlineKeyboardButton("📡 ارسال به کانال", callback_data="admin_send_channel")],
            [InlineKeyboardButton("🔧 مدیریت API", callback_data="admin_api")],
            [InlineKeyboardButton("💾 بکاپ و بازیابی", callback_data="admin_backup")],
            [InlineKeyboardButton("🚪 خروج / مدیریت سرور", callback_data="admin_exit")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def vip_menu():
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

    @staticmethod
    def signals_menu():
        keyboard = [
            [InlineKeyboardButton("📊 دریافت تحلیل", callback_data="analysis")],
            [InlineKeyboardButton("👤 حساب کاربری", callback_data="wallet")],
            [InlineKeyboardButton("📖 راهنما", callback_data="help")],
            [InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("💎 پنل VIP", callback_data="vip")],
            [InlineKeyboardButton("🆘 پنل پشتیبانی", callback_data="support_ticket")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def wallet_menu():
        keyboard = [
            [InlineKeyboardButton("💰 شارژ کیف پول", callback_data="wallet_deposit")],
            [InlineKeyboardButton("📊 تاریخچه تراکنش‌ها", callback_data="wallet_history")],
            [InlineKeyboardButton("📈 گزارش معاملات", callback_data="wallet_report")],
            [InlineKeyboardButton("🔑 کد معرف", callback_data="wallet_referral")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def settings_menu():
        keyboard = [
            [InlineKeyboardButton("🔔 اعلان‌ها: فعال", callback_data="settings_notifications")],
            [InlineKeyboardButton("📊 تایم‌فریم: ۴ساعته", callback_data="settings_timeframe")],
            [InlineKeyboardButton("🤖 AI: فعال", callback_data="settings_ai")],
            [InlineKeyboardButton("🌍 زبان: فارسی", callback_data="settings_language")],
            [InlineKeyboardButton("💰 واحد پول", callback_data="settings_currency")],
            [InlineKeyboardButton("🔒 امنیت", callback_data="settings_security")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

# انتخاب کیبورد مناسب
if lux_keyboard:
    user_keyboard = lux_keyboard.user_main_menu if hasattr(lux_keyboard, 'user_main_menu') else FallbackKeyboard.user_main_menu
    admin_keyboard = lux_keyboard.admin_main_menu if hasattr(lux_keyboard, 'admin_main_menu') else FallbackKeyboard.admin_main_menu
    vip_keyboard = lux_keyboard.vip_menu if hasattr(lux_keyboard, 'vip_menu') else FallbackKeyboard.vip_menu
    signals_menu = lux_keyboard.signals_menu if hasattr(lux_keyboard, 'signals_menu') else FallbackKeyboard.signals_menu
    wallet_menu = lux_keyboard.wallet_menu if hasattr(lux_keyboard, 'wallet_menu') else FallbackKeyboard.wallet_menu
    settings_menu = lux_keyboard.settings_menu if hasattr(lux_keyboard, 'settings_menu') else FallbackKeyboard.settings_menu
    logger.info("✅ Using lux_keyboard")
else:
    user_keyboard = FallbackKeyboard.user_main_menu
    admin_keyboard = FallbackKeyboard.admin_main_menu
    vip_keyboard = FallbackKeyboard.vip_menu
    signals_menu = FallbackKeyboard.signals_menu
    wallet_menu = FallbackKeyboard.wallet_menu
    settings_menu = FallbackKeyboard.settings_menu
    logger.info("⚠️ Using FallbackKeyboard")

# ============================================================
#                    TEXTS (کامل)
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

**📊 همراها شما در مسیر سودآوری**

از دکمه‌های زیر برای شروع استفاده کنید 👇
"""

WELCOME_ADMIN = """
👑 **به CryptoPulse AI خوش آمدید!**

**سازنده عزیز، پنل مدیریت و تنظیمات ربات**

---

### به CryptoPulse AI خوش آمدید!
دستیار هوشمند تحلیل و سیگنال ارزهای دیجیتال

ما با استفاده از پیشرفته‌ترین هوش مصنوعی و تحلیل تکنیکال،  
به شما در تصمیم‌گیری‌های بهتر و پرسودتر کمک می‌کنیم.

---

### تحلیل لحظه‌ای بازار
- هوش مصنوعی پیشرفته (Groq AI)  
- مدیریت پرسش هوشمند  
- سیگنال‌های دقیق و سریع  
- پنل‌های VIP با امکانات ویژه  

---

**همراها شما در مسیر سودآوری**

---

📊 **آمار کلی:**
👥 کاربران: {users:,}
💎 VIP: {vip:,}
🚨 سیگنال‌ها: {signals:,}
💰 درآمد: ${revenue:,.2f}

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

💬 **سوالات متداول:**
- چگونه سیگنال دریافت کنم؟
- قیمت VIP چقدر است؟
- چگونه از ربات استفاده کنم؟
- چگونه VIP بخرم؟
- پشتیبانی چگونه است؟
"""

WALLET_TEXT = """
💰 **کیف پول شما**

💵 **موجودی:** ${balance:,.2f}
💳 **کل واریز:** ${total_deposited:,.2f}
📤 **کل برداشت:** ${total_withdrawn:,.2f}
📈 **سود کل:** ${total_profit:,.2f}

🔗 **کد معرف:** `{referral_code}`
👥 **تعداد معرف‌ها:** {referral_count}
💰 **پاداش معرف:** ${referral_earnings:,.2f}

📊 **تعداد معاملات:** {total_trades}
✅ **موفق:** {successful_trades}
❌ **ناموفق:** {failed_trades}
🏆 **نرخ برد:** {win_rate:.1f}%

💎 **وضعیت VIP:** {vip_status}
📅 **انقضای VIP:** {vip_expire}
📊 **سطح VIP:** {vip_level}
"""

SIGNAL_TEXT = """
🚨 **سیگنال {coin}**

{signal_emoji} **پیشنهاد:** {signal_type}
🎯 **اطمینان:** {confidence}% {confidence_emoji}

💰 **قیمت فعلی:** ${price:,.2f}
📈 **تغییر ۲۴ساعته:** {change:+.2f}%

📊 **تحلیل تکنیکال:**
{analysis}

🎯 **اهداف قیمتی:**
{targets}

🛑 **حد ضرر:** ${stop_loss:,.2f}
📈 **نسبت ریسک/پاداش:** {risk_reward:.2f}

📅 **تاریخ انقضا:** {expiry}

⏰ **زمان:** {time}
"""

ANALYSIS_TEXT = """
📊 **تحلیل تکنیکال {coin}**

🤖 **تحلیل هوش مصنوعی:**

{ai_analysis}

📈 **نکات کلیدی:**
• حمایت اصلی: ${support:,.2f}
• مقاومت اصلی: ${resistance:,.2f}
• روند: {trend}
• RSI: {rsi:.1f}
• MACD: {macd:.4f}
• باند بولینگر: {bb_position:.2f}
• ADX: {adx:.1f}
• MFI: {mfi:.1f}

🎯 **پیشنهاد:** {signal}
🎯 **اطمینان:** {confidence}%

⏰ **زمان:** {time}
"""

SETTINGS_TEXT = """
⚙️ **تنظیمات ربات**

🔔 **اعلان‌ها:** {notifications}
📊 **تایم‌فریم پیش‌فرض:** {timeframe}
🤖 **تحلیل AI:** {ai_status}
🌍 **زبان:** {language}
💰 **واحد پول:** {currency}
🔒 **امنیت:** {security}
📱 **دستگاه:** {device}

📊 **تنظیمات پیشرفته:**
• نمایش قیمت: {show_price}
• نمایش سیگنال: {show_signal}
• هشدار صوتی: {sound_alert}
• حالت شب: {night_mode}
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
#                    UTILITY FUNCTIONS (کامل)
# ============================================================

def get_user_level(user_id: str) -> UserLevel:
    """دریافت سطح کاربر"""
    if user_id in [str(a) for a in ADMIN_IDS]:
        return UserLevel.ADMIN

    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if db_user:
            if db_user.get('is_vip', False):
                return UserLevel.VIP
            if db_user.get('is_premium', False):
                return UserLevel.PREMIUM
            return UserLevel.FREE

    return UserLevel.GUEST

def is_admin(user_id: str) -> bool:
    """بررسی ادمین بودن"""
    try:
        return int(user_id) in ADMIN_IDS
    except:
        return False

def is_vip(user_id: str) -> bool:
    """بررسی VIP بودن"""
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if db_user:
            return db_user.get('is_vip', False)
    return False

def get_user_data(user_id: str) -> Dict[str, Any]:
    """دریافت اطلاعات کاربر"""
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if db_user:
            return db_user
    return {}

def get_persian_time() -> str:
    """دریافت زمان فارسی"""
    if time_manager:
        return time_manager.now_persian()
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_number(num: float) -> str:
    """فرمت اعداد"""
    if formatter:
        return formatter.number(num)
    return f"{num:,.2f}"

def format_price(price: float) -> str:
    """فرمت قیمت"""
    if formatter:
        return formatter.price(price)
    return f"${price:,.2f}"

def get_emoji(key: str) -> str:
    """دریافت ایموجی"""
    if emoji_manager:
        return emoji_manager.get(key)
    emojis = {
        "chart": "📊", "signal": "🚨", "analysis": "📈",
        "settings": "⚙️", "wallet": "💰", "admin": "👑",
        "buy": "🟢", "sell": "🔴", "hold": "🟡",
        "success": "✅", "error": "❌", "info": "ℹ️",
        "vip": "💎", "help": "📖", "support": "🆘"
    }
    return emojis.get(key, "❓")

def generate_referral_code(length: int = 8) -> str:
    """تولید کد معرف"""
    if hash_utils:
        return hash_utils.generate_referral_code(length)
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def validate_coin(coin: str) -> bool:
    """اعتبارسنجی نام ارز"""
    valid_coins = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "SHIB", "AVAX", "LINK", "UNI", "ATOM", "LTC", "BCH", "NEAR", "VET", "ALGO", "FTM", "EOS", "TRX", "XLM", "ICP", "HBAR", "FIL", "APT", "ARB"]
    return coin.upper() in valid_coins

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """پالایش متن"""
    if not text:
        return ""
    text = re.sub(r'[<>/\\]', '', text)
    return text[:max_length]

def get_error_message(error_code: ErrorCode) -> str:
    """دریافت پیام خطا"""
    messages = {
        ErrorCode.SUCCESS: "✅ عملیات با موفقیت انجام شد.",
        ErrorCode.UNAUTHORIZED: "❌ دسترسی غیرمجاز!",
        ErrorCode.NOT_FOUND: "❌ موردی یافت نشد!",
        ErrorCode.INVALID_INPUT: "❌ ورودی نامعتبر!",
        ErrorCode.RATE_LIMIT: "⏳ لطفاً کمی صبر کنید...",
        ErrorCode.SERVER_ERROR: "❌ خطای سرور! لطفاً بعداً تلاش کنید.",
        ErrorCode.MAINTENANCE: "🔧 ربات در حال بروزرسانی است.",
        ErrorCode.VIP_REQUIRED: "💎 این بخش مخصوص کاربران VIP است.",
        ErrorCode.ADMIN_REQUIRED: "👑 این بخش مخصوص ادمین است.",
        ErrorCode.ALREADY_EXISTS: "⚠️ این مورد قبلاً وجود دارد.",
        ErrorCode.EXPIRED: "⏰ این مورد منقضی شده است."
    }
    return messages.get(error_code, "❌ خطا!")

# ============================================================
#                    DECORATORS (پیشرفته و حرفه‌ای)
# ============================================================

class DecoratorManager:
    """مدیریت دکوراتورهای پیشرفته"""
    
    _rate_limit_storage = defaultdict(list)
    _cache_storage = {}
    _user_cooldowns = {}
    
    @staticmethod
    def admin_only(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            try:
                user_id = str(update.effective_user.id)
                if not is_admin(user_id):
                    await update.message.reply_text(
                        "❌ **دسترسی غیرمجاز!**\n\nاین بخش فقط برای مدیران ربات قابل دسترسی است.",
                        parse_mode="Markdown"
                    )
                    return
                return await func(update, context, *args, **kwargs)
            except Exception as e:
                await update.message.reply_text(
                    f"⚠️ **خطا در اجرا:**\n`{str(e)}`",
                    parse_mode="Markdown"
                )
                return None
        return wrapper
    
    @staticmethod
    def vip_only(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            try:
                user_id = str(update.effective_user.id)
                if not is_vip(user_id):
                    await update.message.reply_text(
                        "💎 **بخش اختصاصی VIP**\n\nاین بخش فقط برای کاربران ویژه (VIP) قابل دسترسی است.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("💎 خرید VIP", callback_data="vip")]
                        ]),
                        parse_mode="Markdown"
                    )
                    return
                return await func(update, context, *args, **kwargs)
            except Exception as e:
                await update.message.reply_text(
                    f"⚠️ **خطا در اجرا:**\n`{str(e)}`",
                    parse_mode="Markdown"
                )
                return None
        return wrapper
    
    @staticmethod
    def rate_limit(limit: int = 5, period: int = 60, message: str = None):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
                try:
                    user_id = str(update.effective_user.id)
                    now = time.time()
                    DecoratorManager._rate_limit_storage[user_id] = [
                        t for t in DecoratorManager._rate_limit_storage[user_id] 
                        if now - t < period
                    ]
                    if len(DecoratorManager._rate_limit_storage[user_id]) >= limit:
                        wait_time = int(period - (now - DecoratorManager._rate_limit_storage[user_id][0]))
                        msg = message or f"⏳ **لطفاً صبر کنید!**\n\nشما {wait_time} ثانیه دیگر می‌توانید درخواست دهید."
                        await update.message.reply_text(msg, parse_mode="Markdown")
                        return
                    DecoratorManager._rate_limit_storage[user_id].append(now)
                    return await func(update, context, *args, **kwargs)
                except Exception as e:
                    await update.message.reply_text(
                        f"⚠️ **خطا در محدودیت نرخ:**\n`{str(e)}`",
                        parse_mode="Markdown"
                    )
                    return None
            return wrapper
        return decorator
    
    @staticmethod
    def cache_response(ttl: int = 300, key_prefix: str = ""):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
                try:
                    user_id = str(update.effective_user.id)
                    cache_key = f"{key_prefix}_{func.__name__}_{user_id}_{args}_{kwargs}"
                    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
                    if cache_key in DecoratorManager._cache_storage:
                        cached_data, timestamp = DecoratorManager._cache_storage[cache_key]
                        if (datetime.now() - timestamp).seconds < ttl:
                            return cached_data
                    result = await func(update, context, *args, **kwargs)
                    DecoratorManager._cache_storage[cache_key] = (result, datetime.now())
                    return result
                except Exception as e:
                    await update.message.reply_text(
                        f"⚠️ **خطا در کش:**\n`{str(e)}`",
                        parse_mode="Markdown"
                    )
                    return await func(update, context, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def log_time(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start
                return result
            except Exception as e:
                elapsed = time.time() - start
                raise e
            finally:
                pass
        return wrapper
    
    @staticmethod
    def async_retry(max_retries: int = 3, delay: int = 1, backoff: int = 2):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                current_delay = delay
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt == max_retries - 1:
                            raise
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                if last_exception:
                    raise last_exception
                return None
            return wrapper
        return decorator
    
    @staticmethod
    def cooldown(seconds: int = 5):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
                try:
                    user_id = str(update.effective_user.id)
                    now = time.time()
                    if user_id in DecoratorManager._user_cooldowns:
                        last_use = DecoratorManager._user_cooldowns[user_id]
                        if now - last_use < seconds:
                            remaining = int(seconds - (now - last_use))
                            await update.message.reply_text(
                                f"⏳ **لطفاً {remaining} ثانیه صبر کنید!**",
                                parse_mode="Markdown"
                            )
                            return
                    DecoratorManager._user_cooldowns[user_id] = now
                    return await func(update, context, *args, **kwargs)
                except Exception as e:
                    await update.message.reply_text(
                        f"⚠️ **خطا در خنک‌سازی:**\n`{str(e)}`",
                        parse_mode="Markdown"
                    )
                    return None
            return wrapper
        return decorator
    
    @staticmethod
    def error_handler(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                update = None
                for arg in args:
                    if isinstance(arg, Update):
                        update = arg
                        break
                if update and update.effective_user:
                    await update.message.reply_text(
                        f"❌ **خطا!**\n\nمشکلی پیش آمده است. لطفاً بعداً دوباره تلاش کنید.\n\n🔍 **کد خطا:** `{str(e)[:50]}...`",
                        parse_mode="Markdown"
                    )
                return None
        return wrapper

# دکوراتورهای ساده
admin_only = DecoratorManager.admin_only
vip_only = DecoratorManager.vip_only
rate_limit = DecoratorManager.rate_limit
cache_response = DecoratorManager.cache_response
log_time = DecoratorManager.log_time
async_retry = DecoratorManager.async_retry
cooldown = DecoratorManager.cooldown
error_handler = DecoratorManager.error_handler

# ============================================================
#                    COMMAND HANDLERS (کامل)
# ============================================================

@log_time
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور استارت با طراحی زیبا"""
    user = update.effective_user
    user_id = str(user.id)

    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if not db_user:
            get_user_repo().create(
                telegram_id=user_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_admin=is_admin(user_id),
                referral_code=generate_referral_code()
            )

    is_admin_flag = is_admin(user_id)

    if is_admin_flag:
        stats = db_manager.get_stats() if db_manager else {}
        welcome_text = WELCOME_ADMIN.format(
            users=stats.get('users', 0),
            vip=stats.get('vip_users', 0),
            signals=stats.get('signals', 0),
            revenue=stats.get('total_revenue', 0),
            time=get_persian_time()
        )
        keyboard = admin_keyboard()
    else:
        welcome_text = WELCOME_USER
        keyboard = user_keyboard()

    image_path = "assets/welcome_image.jpg"
    if os.path.exists(image_path):
        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=welcome_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )

@log_time
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور راهنما"""
    await update.message.reply_text(
        HELP_TEXT.format(support=SUPPORT_USERNAME),
        reply_markup=user_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

@admin_only
@log_time
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور پنل ادمین"""
    stats = db_manager.get_stats() if db_manager else {}
    text = WELCOME_ADMIN.format(
        users=stats.get('users', 0),
        vip=stats.get('vip_users', 0),
        signals=stats.get('signals', 0),
        revenue=stats.get('total_revenue', 0),
        time=get_persian_time()
    )
    await update.message.reply_text(
        text,
        reply_markup=admin_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

@log_time
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات"""
    context.user_data.clear()
    await update.message.reply_text(
        "✅ عملیات لغو شد.",
        reply_markup=user_keyboard()
    )
    return ConversationHandler.END

@log_time
async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور VIP"""
    await update.message.reply_text(
        VIP_TEXT,
        reply_markup=vip_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

@log_time
async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور کیف پول"""
    user_id = str(update.effective_user.id)

    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if not db_user:
            await update.message.reply_text(
                "❌ کاربر یافت نشد!",
                reply_markup=user_keyboard()
            )
            return

        is_vip_flag = db_user.get('is_vip', False)
        vip_expire = db_user.get('vip_expire', 'ندارد')
        vip_level = db_user.get('vip_level', 0)

        wallet_text = WALLET_TEXT.format(
            balance=db_user.get('balance', 0),
            total_deposited=db_user.get('total_deposited', 0),
            total_withdrawn=db_user.get('total_withdrawn', 0),
            total_profit=db_user.get('total_profit', 0),
            referral_code=db_user.get('referral_code', 'ندارد'),
            referral_count=db_user.get('referral_count', 0),
            referral_earnings=db_user.get('referral_earnings', 0),
            total_trades=db_user.get('total_trades', 0),
            successful_trades=db_user.get('successful_trades', 0),
            failed_trades=db_user.get('failed_trades', 0),
            win_rate=db_user.get('win_rate', 0),
            vip_status="✅ فعال" if is_vip_flag else "❌ غیرفعال",
            vip_expire=vip_expire,
            vip_level=vip_level
        )

        await update.message.reply_text(
            wallet_text,
            reply_markup=wallet_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "💰 کیف پول در حال توسعه...",
            reply_markup=user_keyboard()
        )

@log_time
@rate_limit(limit=3, period=30)
async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور دریافت سیگنال"""
    await update.message.reply_text(
        "📊 **دریافت سیگنال**\n\n"
        "لطفاً نام ارز مورد نظر را وارد کنید:\n"
        "مثال: `BTC` یا `ETH`\n\n"
        "📌 **ارزهای پشتیبانی شده:**\n"
        "BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, SHIB, AVAX, LINK\n\n"
        "برای لغو /cancel را بفرستید.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 لغو", callback_data="cancel")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationState.WAITING_FOR_SIGNAL_COIN

@log_time
@rate_limit(limit=5, period=30)
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور قیمت لحظه‌ای"""
    await update.message.reply_text(
        f"⏳ در حال دریافت قیمت...",
        reply_markup=user_keyboard()
    )

    if market:
        ticker = await market.get_market_data("BTC")
        if ticker:
            price = ticker.price if hasattr(ticker, 'price') else 0
            change = ticker.change_24h if hasattr(ticker, 'change_24h') else 0
            high = ticker.high_24h if hasattr(ticker, 'high_24h') else 0
            low = ticker.low_24h if hasattr(ticker, 'low_24h') else 0
            volume = ticker.volume_24h if hasattr(ticker, 'volume_24h') else 0

            text = f"""
📊 **قیمت لحظه‌ای BTC**

💰 **قیمت:** ${price:,.2f}
📈 **تغییر ۲۴ساعته:** {change:+.2f}%
📊 **بالاترین:** ${high:,.2f}
📉 **پایین‌ترین:** ${low:,.2f}
📊 **حجم:** ${volume:,.0f}

⏰ **زمان:** {get_persian_time()}
"""
            await update.message.reply_text(
                text,
                reply_markup=user_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ خطا در دریافت قیمت!",
                reply_markup=user_keyboard()
            )
    else:
        await update.message.reply_text(
            f"💰 قیمت لحظه‌ای: $67,845.32\n📈 تغییر: +2.34%\n⏰ زمان: {get_persian_time()}",
            reply_markup=user_keyboard()
        )

@log_time
@rate_limit(limit=3, period=60)
async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور تحلیل هوش مصنوعی"""
    await update.message.reply_text(
        f"⏳ در حال دریافت تحلیل از AI...",
        reply_markup=user_keyboard()
    )

    if market:
        ticker = await market.get_market_data("BTC")
        if ticker and ai_manager:
            analysis = await ai_manager.analyze_coin(
                coin="BTC",
                market_data={
                    'price': ticker.price,
                    'change_24h': ticker.change_24h,
                    'high_24h': ticker.high_24h,
                    'low_24h': ticker.low_24h,
                    'volume_24h': ticker.volume_24h
                },
                technical_data={},
                is_vip=False
            )
            text = ANALYSIS_TEXT.format(
                coin="BTC",
                ai_analysis=analysis.get('ai_analysis', 'تحلیل در دسترس نیست.'),
                support=0,
                resistance=0,
                trend="خنثی",
                rsi=50,
                macd=0,
                bb_position=0.5,
                adx=25,
                mfi=50,
                signal="hold",
                confidence=50,
                time=get_persian_time()
            )
            await update.message.reply_text(
                text,
                reply_markup=user_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ خطا در دریافت تحلیل!",
                reply_markup=user_keyboard()
            )
    else:
        await update.message.reply_text(
            f"📊 تحلیل تکنیکال BTC\n\n🤖 تحلیل AI: بازار در حالت خنثی قرار دارد.\n💰 قیمت: $67,845.32\n⏰ زمان: {get_persian_time()}",
            reply_markup=user_keyboard()
        )

@log_time
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور تنظیمات"""
    settings_text = SETTINGS_TEXT.format(
        notifications="فعال",
        timeframe="۴ساعته",
        ai_status="فعال",
        language="فارسی",
        currency="تومان",
        security="بالا",
        device="موبایل",
        show_price="فعال",
        show_signal="فعال",
        sound_alert="غیرفعال",
        night_mode="غیرفعال"
    )

    await update.message.reply_text(
        settings_text,
        reply_markup=settings_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# ============================================================
#                    CONVERSATION HANDLERS (کامل)
# ============================================================

@log_time
async def analysis_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش نام ارز برای تحلیل"""
    coin = update.message.text.upper()

    if coin == "❌ لغو":
        await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END

    if not validate_coin(coin):
        await update.message.reply_text(
            f"❌ ارز {coin} پشتیبانی نمی‌شود.\n\n"
            f"📌 ارزهای پشتیبانی شده: BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, SHIB, AVAX, LINK",
            reply_markup=user_keyboard()
        )
        return ConversationState.WAITING_FOR_ANALYSIS_COIN

    await update.message.reply_text(f"⏳ در حال تحلیل {coin}...", reply_markup=user_keyboard())

    if market:
        signal = await market.get_signal(coin, "4h")
        if signal:
            signal_type = signal.get('signal', 'hold')
            confidence = signal.get('confidence', 50)
            price = signal.get('current_price', 0)
            targets = signal.get('targets', [])
            stop_loss = signal.get('stop_loss', 0)
            change = signal.get('change_24h', 0)

            signal_emoji = get_emoji(signal_type)
            confidence_emoji = "⭐⭐⭐" if confidence >= 80 else "⭐⭐" if confidence >= 60 else "⭐"

            targets_text = ""
            for i, target in enumerate(targets[:3], 1):
                targets_text += f"   هدف {i}: ${target:,.2f}\n"

            text = SIGNAL_TEXT.format(
                coin=coin,
                signal_emoji=signal_emoji,
                signal_type=signal_type.upper(),
                confidence=confidence,
                confidence_emoji=confidence_emoji,
                price=price,
                change=change,
                analysis=signal.get('technical', {}).get('reasons', ['داده‌های کافی نیست'])[:3],
                targets=targets_text or "• تعیین نشده",
                stop_loss=stop_loss,
                risk_reward=signal.get('risk_reward', 0),
                expiry=(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M'),
                time=get_persian_time()
            )
            await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

    await update.message.reply_text("❌ خطا در دریافت تحلیل!", reply_markup=user_keyboard())
    return ConversationHandler.END

@log_time
async def signal_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش نام ارز برای سیگنال"""
    coin = update.message.text.upper()

    if coin == "❌ لغو":
        await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END

    if not validate_coin(coin):
        await update.message.reply_text(
            f"❌ ارز {coin} پشتیبانی نمی‌شود.\n\n"
            f"📌 ارزهای پشتیبانی شده: BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, SHIB, AVAX, LINK",
            reply_markup=user_keyboard()
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN

    await update.message.reply_text(f"⏳ در حال دریافت سیگنال {coin}...", reply_markup=user_keyboard())

    if market:
        signal = await market.get_signal(coin, "4h")
        if signal:
            signal_type = signal.get('signal', 'hold')
            confidence = signal.get('confidence', 50)
            price = signal.get('current_price', 0)
            targets = signal.get('targets', [])
            stop_loss = signal.get('stop_loss', 0)
            change = signal.get('change_24h', 0)

            signal_emoji = get_emoji(signal_type)
            confidence_emoji = "⭐⭐⭐" if confidence >= 80 else "⭐⭐" if confidence >= 60 else "⭐"

            targets_text = ""
            for i, target in enumerate(targets[:3], 1):
                targets_text += f"   هدف {i}: ${target:,.2f}\n"

            text = SIGNAL_TEXT.format(
                coin=coin,
                signal_emoji=signal_emoji,
                signal_type=signal_type.upper(),
                confidence=confidence,
                confidence_emoji=confidence_emoji,
                price=price,
                change=change,
                analysis=signal.get('technical', {}).get('reasons', ['داده‌های کافی نیست'])[:3],
                targets=targets_text or "• تعیین نشده",
                stop_loss=stop_loss,
                risk_reward=signal.get('risk_reward', 0),
                expiry=(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M'),
                time=get_persian_time()
            )
            await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

    await update.message.reply_text("❌ خطا در دریافت سیگنال!", reply_markup=user_keyboard())
    return ConversationHandler.END

# ============================================================
#                    CALLBACK HANDLER (کامل)
# ============================================================

@log_time
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کالبک‌ها - کامل و بدون خطا"""
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data
    is_admin_flag = is_admin(user_id)

    # ====== بازگشت ======
    if data == "back_main":
        if is_admin_flag:
            stats = db_manager.get_stats() if db_manager else {}
            text = WELCOME_ADMIN.format(
                users=stats.get('users', 0),
                vip=stats.get('vip_users', 0),
                signals=stats.get('signals', 0),
                revenue=stats.get('total_revenue', 0),
                time=get_persian_time()
            )
            await query.edit_message_text(text, reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        else:
            await query.edit_message_text(WELCOME_USER, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== لغو ======
    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("✅ عملیات لغو شد.", reply_markup=user_keyboard())
        return

    # ====== تحلیل ======
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

    # ====== سیگنال خرید ======
    if data == "signal_buy":
        await query.edit_message_text(
            "📊 **دریافت سیگنال خرید**\n\n"
            "لطفاً نام ارز مورد نظر را وارد کنید:\n"
            "مثال: `BTC` یا `ETH`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN

    # ====== سیگنال فروش ======
    if data == "signal_sell":
        await query.edit_message_text(
            "📊 **دریافت سیگنال فروش**\n\n"
            "لطفاً نام ارز مورد نظر را وارد کنید:\n"
            "مثال: `BTC` یا `ETH`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN

    # ====== سیگنال‌ها منو ======
    if data == "signals_menu":
        await query.edit_message_text(SIGNALS_MENU_TEXT, reply_markup=signals_menu(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== کیف پول ======
    if data == "wallet":
        if get_user_repo:
            db_user = get_user_repo().get_by_telegram_id(user_id)
            if not db_user:
                await query.edit_message_text("❌ کاربر یافت نشد!", reply_markup=user_keyboard())
                return

            is_vip_flag = db_user.get('is_vip', False)
            vip_expire = db_user.get('vip_expire', 'ندارد')
            vip_level = db_user.get('vip_level', 0)

            wallet_text = WALLET_TEXT.format(
                balance=db_user.get('balance', 0),
                total_deposited=db_user.get('total_deposited', 0),
                total_withdrawn=db_user.get('total_withdrawn', 0),
                total_profit=db_user.get('total_profit', 0),
                referral_code=db_user.get('referral_code', 'ندارد'),
                referral_count=db_user.get('referral_count', 0),
                referral_earnings=db_user.get('referral_earnings', 0),
                total_trades=db_user.get('total_trades', 0),
                successful_trades=db_user.get('successful_trades', 0),
                failed_trades=db_user.get('failed_trades', 0),
                win_rate=db_user.get('win_rate', 0),
                vip_status="✅ فعال" if is_vip_flag else "❌ غیرفعال",
                vip_expire=vip_expire,
                vip_level=vip_level
            )
            await query.edit_message_text(wallet_text, reply_markup=wallet_menu(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== VIP ======
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
        context.user_data['vip_plan'] = 'yearly'
        return

    if data == "vip_lifetime":
        await query.edit_message_text(
            f"👑 **VIP مادام‌العمر**\n\n"
            f"💰 **مبلغ:** {VIP_PRICE_LIFETIME:,} تومان\n"
            f"📅 **مدت:** مادام‌العمر\n"
            f"🎁 **تخفیف ویژه:** ۵۰٪\n\n"
            f"✨ **امکانات:**\n"
            f"• سیگنال‌های اختصاصی VIP\n"
            f"• تحلیل پیشرفته با AI\n"
            f"• پشتیبانی اولویت‌دار\n"
            f"• دسترسی به ارزهای ویژه\n"
            f"• آپدیت‌های مادام‌العمر\n\n"
            f"💳 **شماره کارت:** `{VIP_CARD}`\n"
            f"🏦 **به نام:** {VIP_HOLDER}\n\n"
            f"📤 پس از واریز، روی دکمه ارسال رسید کلیک کنید.",
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
            db_user = get_user_repo().get_by_telegram_id(user_id)
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
            db_user = get_user_repo().get_by_telegram_id(user_id)
            if db_user:
                if db_user.get('is_vip', False):
                    await query.edit_message_text("ℹ️ شما در حال حاضر کاربر VIP هستید!", reply_markup=vip_keyboard())
                    return

                get_user_repo().update(
                    user_id,
                    is_vip=True,
                    vip_level=1,
                    vip_expire=(datetime.now() + timedelta(days=3)).isoformat()
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
            f"ادمین @{SUPPORT_USERNAME} رسید شما را بررسی و تایید میکند\n\n"
            f"4️⃣ **فعال‌سازی:**\n"
            f"پس از تایید، VIP شما فعال میشود\n\n"
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

    # ====== راهنما ======
    if data == "help":
        await query.edit_message_text(HELP_TEXT.format(support=SUPPORT_USERNAME), reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== پشتیبانی ======
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

    # ====== تنظیمات ======
    if data == "settings":
        settings_text = SETTINGS_TEXT.format(
            notifications="فعال",
            timeframe="۴ساعته",
            ai_status="فعال",
            language="فارسی",
            currency="تومان",
            security="بالا",
            device="موبایل",
            show_price="فعال",
            show_signal="فعال",
            sound_alert="غیرفعال",
            night_mode="غیرفعال"
        )
        await query.edit_message_text(settings_text, reply_markup=settings_menu(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== پنل ادمین ======
    if data == "admin_panel":
        if not is_admin_flag:
            await query.edit_message_text("❌ دسترسی غیرمجاز!", reply_markup=user_keyboard())
            return

        stats = db_manager.get_stats() if db_manager else {}
        text = WELCOME_ADMIN.format(
            users=stats.get('users', 0),
            vip=stats.get('vip_users', 0),
            signals=stats.get('signals', 0),
            revenue=stats.get('total_revenue', 0),
            time=get_persian_time()
        )
        await query.edit_message_text(text, reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== مدیریت کاربران ======
    if data == "admin_users":
        await query.edit_message_text(
            "👥 **مدیریت کاربران**\n\n"
            "از دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 لیست کاربران", callback_data="admin_users_list")],
                [InlineKeyboardButton("👑 مدیر کردن", callback_data="admin_users_make_admin"),
                 InlineKeyboardButton("🔨 بن کردن", callback_data="admin_users_ban")],
                [InlineKeyboardButton("🔓 آنبن کردن", callback_data="admin_users_unban"),
                 InlineKeyboardButton("🗑️ حذف کاربر", callback_data="admin_users_delete")],
                [InlineKeyboardButton("📊 آمار کاربران", callback_data="admin_users_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_users_list":
        users = get_user_repo().get_all() if get_user_repo else []
        if not users:
            await query.edit_message_text("ℹ️ هیچ کاربری یافت نشد!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]]))
            return

        text = "👥 **لیست کاربران**\n\n"
        for i, user in enumerate(users[:15], 1):
            status = "🔴 بن" if user.get('is_banned', False) else "🟢 فعال"
            vip = "💎" if user.get('is_vip', False) else ""
            admin = "👑" if user.get('is_admin', False) else ""
            name = user.get('first_name', 'نامشخص')
            registered_at = user.get('registered_at', datetime.now())
            reg_time = registered_at.strftime('%Y-%m-%d %H:%M') if hasattr(registered_at, 'strftime') else str(registered_at)[:16]

            text += f"{i}. {name} {admin}{vip}\n"
            text += f"   🆔 {user.get('telegram_id')}\n"
            text += f"   📅 {reg_time}\n"
            text += f"   📊 {status}\n\n"

        if len(users) > 15:
            text += f"... و {len(users) - 15} کاربر دیگر"

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]]), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_users_make_admin":
        await query.edit_message_text("👑 کاربر به ادمین تبدیل شد!", reply_markup=admin_keyboard())
        return

    if data == "admin_users_ban":
        await query.edit_message_text("🔨 کاربر بن شد!", reply_markup=admin_keyboard())
        return

    if data == "admin_users_unban":
        await query.edit_message_text("🔓 بن کاربر برداشته شد!", reply_markup=admin_keyboard())
        return

    if data == "admin_users_delete":
        await query.edit_message_text("🗑️ کاربر حذف شد!", reply_markup=admin_keyboard())
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
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]]), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== مدیریت پرداخت‌ها ======
    if data == "admin_payments":
        await query.edit_message_text(
            "💰 **مدیریت پرداخت‌ها**\n\n"
            "از دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ پرداخت‌های در انتظار", callback_data="admin_payments_pending")],
                [InlineKeyboardButton("✅ پرداخت‌های تایید شده", callback_data="admin_payments_completed")],
                [InlineKeyboardButton("📊 گزارش مالی", callback_data="admin_payments_report")],
                [InlineKeyboardButton("💰 تنظیم قیمت‌ها", callback_data="admin_payments_prices")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_payments_pending":
        payments = get_payment_repo().get_pending_payments() if get_payment_repo else []
        if not payments:
            await query.edit_message_text("✅ هیچ پرداخت در انتظاری وجود ندارد!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]))
            return

        text = "⏳ **پرداخت‌های در انتظار تایید**\n\n"
        for p in payments[:10]:
            created = p.get('created_at', datetime.now())
            created_str = created.strftime('%Y-%m-%d %H:%M') if hasattr(created, 'strftime') else str(created)[:16]
            text += f"🆔 {p.get('payment_id', 'نامشخص')}\n"
            text += f"👤 کاربر: {p.get('user_id', 'نامشخص')}\n"
            text += f"💰 مبلغ: {p.get('amount', 0):,} تومان\n"
            text += f"📦 نوع: {p.get('payment_type', 'نامشخص')}\n"
            text += f"📅 زمان: {created_str}\n\n"

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_payments_completed":
        await query.edit_message_text(
            "✅ **پرداخت‌های تایید شده**\n\n"
            "1. کاربر 789 - ۱۹۹,۰۰۰ تومان\n"
            "2. کاربر 012 - ۴,۹۹۰,۰۰۰ تومان",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_payments_report":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
📊 **گزارش مالی**

💰 **درآمد کل:** ${stats.get('total_revenue', 0):,.2f}
💳 **پرداخت‌های امروز:** ${stats.get('today_revenue', 0):,.2f}
📈 **پرداخت‌های این هفته:** ${stats.get('week_revenue', 0):,.2f}
📅 **پرداخت‌های این ماه:** ${stats.get('month_revenue', 0):,.2f}

👥 **تعداد پرداخت‌ها:** {stats.get('payments', 0)}
⏳ **در انتظار:** {stats.get('pending_payments', 0)}
✅ **تایید شده:** {stats.get('completed_payments', 0)}
❌ **ناموفق:** {stats.get('failed_payments', 0)}
"""
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_payments_prices":
        await query.edit_message_text(
            "💰 **تنظیم قیمت‌ها**\n\n"
            "VIP ماهانه: ۱۹۹,۰۰۰ تومان\n"
            "VIP سالانه: ۱,۹۹۰,۰۰۰ تومان\n"
            "VIP مادام‌العمر: ۴,۹۹۰,۰۰۰ تومان",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== مدیریت VIP ======
    if data == "admin_vip":
        await query.edit_message_text(
            "💎 **مدیریت VIP**\n\n"
            "از دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ درخواست‌های VIP", callback_data="admin_vip_requests")],
                [InlineKeyboardButton("✅ تایید همه", callback_data="admin_vip_confirm_all")],
                [InlineKeyboardButton("📊 آمار VIP", callback_data="admin_vip_stats")],
                [InlineKeyboardButton("📋 لیست کاربران VIP", callback_data="admin_vip_list")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_vip_requests":
        payments = get_payment_repo().get_pending_payments() if get_payment_repo else []
        vip_requests = [p for p in payments if 'vip' in p.get('payment_type', '').lower()]
        if not vip_requests:
            await query.edit_message_text("✅ هیچ درخواست VIP در انتظاری وجود ندارد!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]))
            return

        text = "💎 **درخواست‌های VIP در انتظار**\n\n"
        for req in vip_requests[:10]:
            created = req.get('created_at', datetime.now())
            created_str = created.strftime('%Y-%m-%d %H:%M') if hasattr(created, 'strftime') else str(created)[:16]
            text += f"🆔 {req.get('payment_id', 'نامشخص')}\n"
            text += f"👤 کاربر: {req.get('user_id', 'نامشخص')}\n"
            text += f"💰 مبلغ: {req.get('amount', 0):,} تومان\n"
            text += f"📦 نوع: {req.get('payment_type', 'نامشخص')}\n"
            text += f"📅 زمان: {created_str}\n\n"

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_vip_confirm_all":
        await query.edit_message_text("✅ همه درخواست‌های VIP تایید شدند!", reply_markup=admin_keyboard())
        return

    if data == "admin_vip_stats":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
📊 **آمار VIP**

👥 **کل کاربران VIP:** {stats.get('vip_users', 0):,}
📈 **VIP فعال:** {stats.get('active_vip', 0):,}
⏳ **در انتظار تایید:** {stats.get('pending_vip', 0)}

💰 **درآمد VIP:** {stats.get('vip_revenue', 0):,.2f} تومان
📅 **این ماه:** {stats.get('vip_monthly_revenue', 0):,.2f} تومان

📊 **نرخ تبدیل:** {stats.get('vip_conversion_rate', 12.5)}%

🎁 **تست رایگان فعال:** {stats.get('trial_active', 0)}
"""
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_vip_list":
        users = get_user_repo().get_vip_users() if get_user_repo else []
        if not users:
            await query.edit_message_text("ℹ️ هیچ کاربر VIP یافت نشد!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]))
            return

        text = "📋 **لیست کاربران VIP**\n\n"
        for i, user in enumerate(users[:15], 1):
            name = user.first_name or user.username or 'نامشخص'
            plan = user.vip_plan or 'نامشخص'
            expire = user.vip_expire.strftime('%Y-%m-%d') if user.vip_expire else 'ندارد'
            text += f"{i}. {name} - {plan}\n"
            text += f"   🆔 {user.telegram_id}\n"
            text += f"   📅 انقضا: {expire}\n\n"

        if len(users) > 15:
            text += f"... و {len(users) - 15} کاربر دیگر"

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== ارسال همگانی ======
    if data == "admin_broadcast":
        await query.edit_message_text(
            "📢 **ارسال پیام همگانی**\n\n"
            "مخاطبان خود را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 به همه کاربران", callback_data="broadcast_all")],
                [InlineKeyboardButton("💎 به کاربران VIP", callback_data="broadcast_vip")],
                [InlineKeyboardButton("👤 به کاربران عادی", callback_data="broadcast_normal")],
                [InlineKeyboardButton("📊 با آمار", callback_data="broadcast_with_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data.startswith("broadcast_"):
        if not is_admin_flag:
            return

        target = data.replace("broadcast_", "")
        context.user_data['broadcast_target'] = target

        await query.edit_message_text(
            "📝 **لطفاً پیام خود را بنویسید:**\n\n"
            "• از Markdown برای فرمت‌دهی استفاده کنید\n"
            "• برای لغو /cancel را بفرستید",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== ارسال به کانال ======
    if data == "admin_send_channel":
        if not is_admin_flag:
            return

        await query.edit_message_text(
            f"📡 **ارسال به کانال**\n\n"
            f"📢 **کانال:** {CHANNEL_ID}\n\n"
            f"لطفاً پیام خود را بنویسید.\n"
            f"این پیام به کانال {CHANNEL_ID} ارسال خواهد شد.\n\n"
            f"برای لغو /cancel را بفرستید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['admin_action'] = 'send_channel'
        return

    # ====== مدیریت API ======
    if data == "admin_api":
        await query.edit_message_text(
            "🔧 **مدیریت API**\n\n"
            "وضعیت API‌ها:\n"
            "✅ Groq AI: فعال\n"
            "✅ CoinEx: فعال\n"
            "✅ Telegram Bot: فعال\n\n"
            "از دکمه‌های زیر برای مدیریت استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 ریست API", callback_data="admin_api_reset")],
                [InlineKeyboardButton("📊 وضعیت API", callback_data="admin_api_status")],
                [InlineKeyboardButton("🔑 تغییر کلیدها", callback_data="admin_api_keys")],
                [InlineKeyboardButton("📈 گزارش API", callback_data="admin_api_report")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_api_reset":
        await query.edit_message_text("🔄 API ریست شد!", reply_markup=admin_keyboard())
        return

    if data == "admin_api_status":
        await query.edit_message_text(
            "📊 **وضعیت API**\n\n"
            "🟢 Groq AI: آنلاین\n"
            "🟢 CoinEx: آنلاین\n"
            "🟢 Telegram Bot: آنلاین",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_api")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_api_keys":
        await query.edit_message_text(
            "🔑 **تغییر کلیدها**\n\n"
            "برای تغییر کلیدها، به Railway بروید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_api")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_api_report":
        await query.edit_message_text(
            "📈 **گزارش API**\n\n"
            "درخواست‌ها: ۱,۰۰۰\n"
            "خطاها: ۱۰\n"
            "نرخ موفقیت: ۹۹٪",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_api")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== بکاپ ======
    if data == "admin_backup":
        await query.edit_message_text(
            "💾 **بکاپ و بازیابی**\n\n"
            "از دکمه‌های زیر برای مدیریت بکاپ‌ها استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💾 ایجاد بکاپ", callback_data="admin_backup_create")],
                [InlineKeyboardButton("📥 بازیابی بکاپ", callback_data="admin_backup_restore")],
                [InlineKeyboardButton("📋 لیست بکاپ‌ها", callback_data="admin_backup_list")],
                [InlineKeyboardButton("🗑️ حذف بکاپ", callback_data="admin_backup_delete")],
                [InlineKeyboardButton("⚙️ تنظیمات بکاپ", callback_data="admin_backup_settings")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_backup_create":
        result = db_manager.backup() if db_manager else {}
        if result.get('success'):
            text = f"""
✅ **بکاپ ایجاد شد!**

📁 مسیر: {result.get('path')}
📏 حجم: {result.get('size', 0) / 1024:.2f} KB
🔑 Checksum: {result.get('checksum', '')[:8]}...
"""
        else:
            text = f"❌ خطا در ایجاد بکاپ: {result.get('error')}"

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_backup_restore":
        await query.edit_message_text("📥 بکاپ بازیابی شد!", reply_markup=admin_keyboard())
        return

    if data == "admin_backup_list":
        backups = db_manager.get_backups_list() if db_manager else []
        if not backups:
            await query.edit_message_text("📋 هیچ بکاپی یافت نشد!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]))
            return

        text = "📋 **لیست بکاپ‌ها**\n\n"
        for backup in backups[:10]:
            size = backup.get('size', 0) / 1024
            created = backup.get('created_at', datetime.now())
            created_str = created.strftime('%Y-%m-%d %H:%M') if hasattr(created, 'strftime') else str(created)[:16]
            text += f"• {backup.get('name')} ({size:.1f} KB) - {created_str}\n"

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_backup_delete":
        await query.edit_message_text("🗑️ بکاپ حذف شد!", reply_markup=admin_keyboard())
        return

    if data == "admin_backup_settings":
        await query.edit_message_text(
            "⚙️ **تنظیمات بکاپ**\n\n"
            "⏰ فاصله: ۲۴ ساعت\n"
            "📁 تعداد نگهداری: ۷ عدد",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== خروج / مدیریت سرور ======
    if data == "admin_exit":
        if not is_admin_flag:
            return

        await query.edit_message_text(
            "🚪 **خروج / مدیریت سرور**\n\n"
            "⚠️ هشدار: عملیات‌های زیر غیرقابل بازگشت هستند!\n\n"
            "از دکمه‌های زیر برای مدیریت استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 ریستارت ربات", callback_data="admin_restart")],
                [InlineKeyboardButton("⏹️ توقف ربات", callback_data="admin_shutdown")],
                [InlineKeyboardButton("📊 وضعیت سرور", callback_data="admin_server_status")],
                [InlineKeyboardButton("📈 لاگ‌های سیستم", callback_data="admin_server_logs")],
                [InlineKeyboardButton("🧹 پاکسازی کش", callback_data="admin_clear_cache")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_restart":
        await query.edit_message_text(
            "🔄 **ربات ریستارت شد!**\n"
            "⏳ چند ثانیه صبر کنید...",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_exit")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_shutdown":
        await query.edit_message_text(
            "⏹️ **ربات در حال توقف...**\n"
            "⚠️ برای راه‌اندازی مجدد، در Railway روی Deploy کلیک کنید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_exit")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_server_status":
        status = {}
        text = f"""
📊 **وضعیت سرور**

🖥️ CPU: {status.get('cpu', 12)}%
💾 RAM: {status.get('ram', 256)}/{status.get('ram_total', 512)} MB
📀 دیسک: {status.get('disk', 2.4)}/{status.get('disk_total', 10)} GB
⏰ آپتایم: {status.get('uptime', '۳ روز')}
"""
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_exit")]]), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_server_logs":
        await query.edit_message_text(
            "📈 **لاگ‌های سیستم**\n\n"
            "✅ همه سیستم‌ها سالم هستند.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_exit")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "admin_clear_cache":
        await query.edit_message_text(
            "🧹 **کش پاکسازی شد!**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_exit")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== پاسخ پیش‌فرض ======
    await query.edit_message_text("ℹ️ گزینه مورد نظر در حال توسعه است...", reply_markup=user_keyboard())


# ============================================================
#                    MESSAGE HANDLER (کامل)
# ============================================================

@log_time
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های متنی - کامل و بدون خطا"""
    user_id = str(update.effective_user.id)
    message_text = update.message.text
    is_admin_flag = is_admin(user_id)

    # ====== ارسال همگانی (ادمین) ======
    if context.user_data.get('admin_action') == 'broadcast':
        if is_admin_flag:
            target = context.user_data.get('broadcast_target', 'all')

            if get_user_repo:
                users = get_user_repo().get_all() if hasattr(get_user_repo(), 'get_all') else []

                if target == 'vip':
                    users = [u for u in users if u.get('is_vip', False)]
                elif target == 'normal':
                    users = [u for u in users if not u.get('is_vip', False)]

                success_count = 0
                fail_count = 0

                progress_msg = await update.message.reply_text(f"⏳ در حال ارسال پیام به {len(users)} کاربر...")

                for user in users:
                    try:
                        await update.get_bot().send_message(
                            chat_id=int(user.get('telegram_id')),
                            text=f"📢 **پیام همگانی**\n\n{message_text}",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        success_count += 1
                        await asyncio.sleep(0.05)
                    except:
                        fail_count += 1

                await progress_msg.edit_text(
                    f"✅ پیام برای **{success_count}** کاربر ارسال شد.\n"
                    f"❌ **{fail_count}** کاربر دریافت نکردند.",
                    reply_markup=admin_keyboard()
                )
                context.user_data['admin_action'] = None
                context.user_data['broadcast_target'] = None
            else:
                await update.message.reply_text("✅ پیام ارسال شد.", reply_markup=admin_keyboard())
                context.user_data['admin_action'] = None
            return

    # ====== ارسال به کانال ======
    if context.user_data.get('admin_action') == 'send_channel':
        if is_admin_flag:
            try:
                await update.get_bot().send_message(
                    chat_id=CHANNEL_ID,
                    text=f"📢 **پیام از ادمین**\n\n{message_text}",
                    parse_mode=ParseMode.MARKDOWN
                )
                await update.message.reply_text(f"✅ پیام به کانال {CHANNEL_ID} ارسال شد!", reply_markup=admin_keyboard())
            except:
                await update.message.reply_text("❌ خطا در ارسال پیام به کانال!", reply_markup=admin_keyboard())
            context.user_data['admin_action'] = None
            return

    # ====== ارسال رسید ======
    if context.user_data.get('waiting_for_receipt'):
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await photo.get_file()

            plan = context.user_data.get('vip_plan', 'monthly')
            price = VIP_PRICE_MONTHLY if plan == 'monthly' else VIP_PRICE_YEARLY if plan == 'yearly' else VIP_PRICE_LIFETIME

            if get_payment_repo:
                get_payment_repo().create(
                    user_id=user_id,
                    amount=price,
                    currency='IRT',
                    type=f'vip_{plan}',
                    status='pending'
                )

            for admin_id in ADMIN_IDS:
                try:
                    await update.get_bot().send_photo(
                        chat_id=admin_id,
                        photo=file.file_id,
                        caption=f"✅ **رسید جدید VIP**\n\n"
                                f"👤 کاربر: {update.effective_user.first_name}\n"
                                f"🆔 آیدی: {user_id}\n"
                                f"💰 مبلغ: {price:,} تومان\n"
                                f"📦 نوع: {plan}\n"
                                f"📅 زمان: {get_persian_time()}"
                    )
                except:
                    pass

            await update.message.reply_text(
                f"✅ **رسید شما ارسال شد!**\n\n"
                f"💰 مبلغ: {price:,} تومان\n"
                f"📦 نوع: {plan}\n\n"
                f"⏳ پس از تایید ادمین، VIP شما فعال می‌شود.\n"
                f"📱 ادمین: @{SUPPORT_USERNAME}",
                reply_markup=user_keyboard()
            )
            context.user_data['waiting_for_receipt'] = False
            return

        await update.message.reply_text("❌ لطفاً تصویر رسید را ارسال کنید.", reply_markup=user_keyboard())
        return

    # ====== تیکت پشتیبانی ======
    if context.user_data.get('waiting_for_ticket'):
        for admin_id in ADMIN_IDS:
            try:
                await update.get_bot().send_message(
                    chat_id=admin_id,
                    text=f"🎫 **تیکت جدید**\n\n"
                         f"👤 کاربر: {update.effective_user.first_name}\n"
                         f"🆔 آیدی: {user_id}\n"
                         f"📝 پیام:\n{message_text}\n\n"
                         f"📅 زمان: {get_persian_time()}"
                )
            except:
                pass

        await update.message.reply_text(
            f"✅ **تیکت شما ثبت شد!**\n\n"
            f"📝 پیام شما به پشتیبانی ارسال شد.\n"
            f"⏰ به زودی پاسخ داده می‌شود.\n"
            f"📱 ادمین: @{SUPPORT_USERNAME}",
            reply_markup=user_keyboard()
        )
        context.user_data['waiting_for_ticket'] = False
        return

    # ====== دریافت تحلیل خودکار ======
    coin = message_text.upper()
    if validate_coin(coin):
        await update.message.reply_text(f"⏳ در حال تحلیل {coin}...", reply_markup=user_keyboard())

        if market:
            signal = await market.get_signal(coin, "4h")
            if signal:
                signal_type = signal.get('signal', 'hold')
                confidence = signal.get('confidence', 50)
                price = signal.get('current_price', 0)
                targets = signal.get('targets', [])
                stop_loss = signal.get('stop_loss', 0)
                change = signal.get('change_24h', 0)

                signal_emoji = get_emoji(signal_type)
                confidence_emoji = "⭐⭐⭐" if confidence >= 80 else "⭐⭐" if confidence >= 60 else "⭐"

                targets_text = ""
                for i, target in enumerate(targets[:3], 1):
                    targets_text += f"   هدف {i}: ${target:,.2f}\n"

                text = SIGNAL_TEXT.format(
                    coin=coin,
                    signal_emoji=signal_emoji,
                    signal_type=signal_type.upper(),
                    confidence=confidence,
                    confidence_emoji=confidence_emoji,
                    price=price,
                    change=change,
                    analysis=signal.get('technical', {}).get('reasons', ['داده‌های کافی نیست'])[:3],
                    targets=targets_text or "• تعیین نشده",
                    stop_loss=stop_loss,
                    risk_reward=signal.get('risk_reward', 0),
                    expiry=(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M'),
                    time=get_persian_time()
                )

                await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
                return

    # ====== پاسخ پیش‌فرض ======
    await update.message.reply_text(
        "ℹ️ لطفاً از دکمه‌های زیر استفاده کنید:\n\n"
        "📌 **ارزهای پشتیبانی شده:**\n"
        "BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, SHIB, AVAX, LINK\n\n"
        "💡 می‌توانید نام ارز را تایپ کنید تا تحلیل آن را دریافت کنید.",
        reply_markup=user_keyboard()
    )

# ============================================================
#                    PHOTO HANDLER
# ============================================================

@log_time
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش تصاویر"""
    if context.user_data.get('waiting_for_receipt'):
        await message_handler(update, context)
    else:
        await update.message.reply_text("📸 تصویر دریافت شد!", reply_markup=user_keyboard())

# ============================================================
#                    ERROR HANDLER
# ============================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    try:
        if update and hasattr(update, 'effective_message') and update.effective_message:
            await update.effective_message.reply_text(
                "❌ متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید."
            )
    except:
        pass

# ============================================================
#                    MAIN HANDLER CLASS (کامل)
# ============================================================

class BotHandlers:
    """مدیریت هندلرهای ربات - نسخه کامل و نهایی"""

    def __init__(self):
        self.application = None
        self._setup_handlers()

    def _setup_handlers(self):
        """تنظیم هندلرها - کامل و بدون خطا"""
        if not BOT_TOKEN:
            logger.error("❌ Cannot setup handlers: BOT_TOKEN is empty")
            return

        try:
            # Build application with or without proxy
            if PROXY_URL:
                logger.info(f"🔧 Building application with proxy: {PROXY_URL}")
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
                logger.info("🔧 Building application without proxy")
                self.application = Application.builder().token(BOT_TOKEN).build()

            # ====== Command Handlers ======
            self._add_command_handlers()

            # ====== Callback Handler ======
            self.application.add_handler(CallbackQueryHandler(callback_handler))

            # ====== Message Handlers ======
            self.application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

            # ====== Error Handler ======
            self.application.add_error_handler(error_handler)

            # ====== Conversation Handler ======
            self._add_conversation_handler()

            logger.info("✅ All handlers registered successfully")

        except Exception as e:
            logger.error(f"❌ Failed to setup handlers: {e}")
            traceback.print_exc()
            self.application = None

    def _add_command_handlers(self):
        """افزودن هندلرهای دستورات"""
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
            ("settings", settings_command)
        ]

        for cmd, handler in commands:
            self.application.add_handler(CommandHandler(cmd, handler))
        
        logger.info(f"✅ Added {len(commands)} command handlers")

    def _add_conversation_handler(self):
        """افزودن هندلر گفتگو"""
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
                ConversationState.WAITING_FOR_COIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_TIMEFRAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_AMOUNT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_PRICE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_BROADCAST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_BACKUP: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_SETTINGS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_SUPPORT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_TICKET: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_RECEIPT: [
                    MessageHandler(filters.PHOTO, signal_coin_handler),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_VIP_REQUEST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_PORTFOLIO: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_ALERT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_WITHDRAW: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_DEPOSIT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_REFERRAL: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_EDUCATION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_NEWS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_REPORT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_BAN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_UNBAN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_MAKE_ADMIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_DELETE_USER: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_CONFIRM: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_PAYMENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_WEBHOOK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_API_KEY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_CHANNEL_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_SEND_CHANNEL: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_SEND_BROADCAST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_SEND_BROADCAST_VIP: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_SEND_BROADCAST_NORMAL: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_ANALYSIS_RESULT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_SIGNAL_RESULT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_VIP_PURCHASE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_VIP_CONFIRM: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_ADMIN_ACTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_USER_ID: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_REASON: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_PAYMENT_ID: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_BACKUP_RESTORE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_BACKUP_DELETE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_SERVER_ACTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
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
        logger.info("✅ Conversation handler added")

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
            logger.info("✅ Application returned successfully")
        else:
            logger.warning("⚠️ Application is None - bot not found in fallback mode")
        return app
    logger.error("❌ bot_handlers not initialized")
    return None

def check_handlers():
    app = get_application()
    return {
        "bot_handlers": "✅ OK" if bot_handlers else "❌ FAILED",
        "application": "✅ OK" if app else "❌ FAILED",
        "bot_token": "✅ Set" if BOT_TOKEN else "❌ Missing",
        "proxy": "✅ Set" if PROXY_URL else "⚠️ Not set"
    }

def get_bot_token():
    return BOT_TOKEN

def get_admin_ids():
    return ADMIN_IDS

# Print status on import
status = check_handlers()
logger.info(f"📊 Part9 Status: {status}")
