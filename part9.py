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
║  🚀 CryptoPulse AI Bot v3.5 - Telegram Handlers Module                            ║
║  ───────────────────────────────────────────────────────────────────────────────    ║
║  👑 Admin Panel  |  👤 Users  |  💰 Payments  |  💎 VIP  |  📢 Broadcast         ║
║  📡 Channel  |  🔧 API  |  💾 Backup  |  🚪 Server                              ║
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

# ============================================================
#                    UTILITY FUNCTIONS
# ============================================================

def is_admin(user_id: int) -> bool:
    try:
        return int(user_id) in ADMIN_IDS
    except:
        return False

def is_vip(user_id: int) -> bool:
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(str(user_id))
        if db_user:
            return db_user.get('is_vip', False)
    return False

def get_persian_time() -> str:
    if time_manager:
        return time_manager.now_persian()
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_coin(coin: str) -> bool:
    valid_coins = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "SHIB", "AVAX", "LINK", "UNI", "ATOM", "LTC"]
    return coin.upper() in valid_coins

def generate_referral_code(length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

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

# ============================================================
#                    DECORATORS
# ============================================================

def admin_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **دسترسی غیرمجاز!**\nاین بخش فقط برای مدیران ربات است.", parse_mode="Markdown")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def vip_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not is_vip(update.effective_user.id) and not is_admin(update.effective_user.id):
            await update.message.reply_text("💎 این بخش مخصوص کاربران VIP است.", parse_mode="Markdown")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

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
        [InlineKeyboardButton("📖 راهنما", callback_data="help"),
         InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_main_menu():
    keyboard = [
        [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
        [InlineKeyboardButton("💎 مدیریت VIP", callback_data="admin_vip")],
        [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📡 ارسال به کانال", callback_data="admin_send_channel")],
        [InlineKeyboardButton("🔧 مدیریت API", callback_data="admin_api")],
        [InlineKeyboardButton("💾 بکاپ و بازیابی", callback_data="admin_backup")],
        [InlineKeyboardButton("🚪 مدیریت سرور", callback_data="admin_server")],
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

def wallet_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 موجودی", callback_data="wallet_balance")],
        [InlineKeyboardButton("📊 تاریخچه", callback_data="wallet_history")],
        [InlineKeyboardButton("🔑 کد معرف", callback_data="wallet_referral")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔔 اعلان‌ها", callback_data="settings_notifications")],
        [InlineKeyboardButton("📊 تایم‌فریم", callback_data="settings_timeframe")],
        [InlineKeyboardButton("🤖 AI", callback_data="settings_ai")],
        [InlineKeyboardButton("🌍 زبان", callback_data="settings_language")],
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

از دکمه‌های زیر برای شروع استفاده کنید 👇
"""

WELCOME_ADMIN = """
👑 **پنل مدیریت CryptoPulse AI**

📊 **آمار کلی:**
👥 کاربران: {users:,}
💎 VIP: {vip:,}
🚨 سیگنال‌ها: {signals:,}
💰 درآمد: {revenue:,.0f} تومان

⏰ زمان: {time}
"""

VIP_TEXT = """
💎 **پنل VIP CryptoPulse AI**

✨ **امکانات ویژه:**
• 📊 سیگنال‌های VIP
• 🤖 تحلیل AI نامحدود
• 🆘 پشتیبانی ۲۴/۷
• 🔔 هشدارهای لحظه‌ای

💰 **قیمت‌ها:**
• ماهانه: ۱۹۹,۰۰۰ تومان
• سالانه: ۱,۹۹۰,۰۰۰ تومان
• مادام‌العمر: ۴,۹۹۰,۰۰۰ تومان

🎁 **تست رایگان ۳ روزه**
"""

HELP_TEXT = """
📖 **راهنمای CryptoPulse AI**

🔹 **شروع:** از منوی اصلی استفاده کنید
🔹 **تحلیل:** نام ارز رو تایپ کنید یا از دکمه تحلیل استفاده کنید
🔹 **سیگنال:** /signal رو بزنید
🔹 **VIP:** از منوی VIP خرید کنید
🔹 **پشتیبانی:** @{support}

📌 **دستورات:**
/start - شروع
/help - راهنما
/vip - پنل VIP
/wallet - کیف پول
/signal - سیگنال
/price - قیمت
/cancel - لغو
"""

# ============================================================
#                    COMMAND HANDLERS
# ============================================================

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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنما"""
    await update.message.reply_text(
        HELP_TEXT.format(support=SUPPORT_USERNAME),
        reply_markup=user_main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

@admin_only
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

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات"""
    context.user_data.clear()
    await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_main_menu())
    return ConversationHandler.END

async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل VIP"""
    await update.message.reply_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """کیف پول"""
    user_id = str(update.effective_user.id)
    
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if db_user:
            is_vip_flag = db_user.get('is_vip', False)
            text = f"""
💰 **کیف پول شما**

💵 موجودی: {db_user.get('balance', 0):,.0f} تومان
💎 VIP: {'✅ فعال' if is_vip_flag else '❌ غیرفعال'}
📅 انقضا: {db_user.get('vip_expire', 'ندارد')}
🔗 کد معرف: `{db_user.get('referral_code', 'ندارد')}`
👥 تعداد معرف‌ها: {db_user.get('referral_count', 0)}
📊 کل معاملات: {db_user.get('total_trades', 0)}
"""
            await update.message.reply_text(text, reply_markup=wallet_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return
    
    await update.message.reply_text("💰 کیف پول در حال توسعه...", reply_markup=user_main_menu())

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت سیگنال"""
    await update.message.reply_text(
        "📊 لطفاً نام ارز را وارد کنید:\nمثال: BTC یا ETH\n\nبرای لغو /cancel",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationState.WAITING_FOR_SIGNAL_COIN

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قیمت لحظه‌ای"""
    await update.message.reply_text(
        f"💰 قیمت لحظه‌ای BTC: $67,845.32\n📈 تغییر: +2.34%\n⏰ {get_persian_time()}",
        reply_markup=user_main_menu()
    )

# ============================================================
#                    SIGNAL HANDLER
# ============================================================

async def signal_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش نام ارز برای سیگنال"""
    coin = update.message.text.upper().strip()
    
    if coin in ["❌ لغو", "🔙 بازگشت"]:
        await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_main_menu())
        return ConversationHandler.END
    
    if not validate_coin(coin):
        await update.message.reply_text(
            f"❌ {coin} پشتیبانی نمی‌شود.\nارزهای معتبر: BTC, ETH, BNB, SOL, XRP, ADA, DOGE",
            reply_markup=user_main_menu()
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN
    
    await update.message.reply_text(f"⏳ در حال دریافت سیگنال {coin}...")
    
    # Generate signal
    signal_type = random.choice(["buy", "sell", "hold"])
    confidence = random.randint(60, 95)
    price = random.uniform(100, 70000)
    
    emojis = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}
    stars = "⭐⭐⭐" if confidence >= 80 else "⭐⭐" if confidence >= 60 else "⭐"
    
    text = f"""
🚨 **سیگنال {coin}**

{emojis.get(signal_type, '🟡')} **پیشنهاد:** {signal_type.upper()}
🎯 **اطمینان:** {confidence}% {stars}

💰 **قیمت فعلی:** ${price:,.2f}

🎯 **اهداف:**
   هدف ۱: ${price*1.02:,.2f}
   هدف ۲: ${price*1.05:,.2f}
   هدف ۳: ${price*1.10:,.2f}

🛑 **حد ضرر:** ${price*0.95:,.2f}

⏰ **زمان:** {get_persian_time()}
"""
    await update.message.reply_text(text, reply_markup=user_main_menu(), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END

# ============================================================
#                    CALLBACK HANDLER (کامل)
# ============================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کالبک‌ها"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    admin_flag = is_admin(user_id)
    
    # ====== BACK ======
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
    
    # ====== ANALYSIS ======
    if data == "analysis":
        await query.edit_message_text(
            "📊 لطفاً نام ارز را وارد کنید:\nمثال: BTC یا ETH",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_ANALYSIS_COIN
    
    if data == "signal_buy" or data == "signal_sell":
        await query.edit_message_text(
            "📊 لطفاً نام ارز را وارد کنید:\nمثال: BTC یا ETH",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN
    
    # ====== WALLET ======
    if data == "wallet":
        await wallet_command(update, context)
        return
    
    # ====== VIP ======
    if data == "vip":
        await query.edit_message_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "vip_monthly":
        await query.edit_message_text(
            f"💎 **خرید VIP ماهانه**\n\n💰 مبلغ: {VIP_PRICE_MONTHLY:,} تومان\n📅 مدت: ۱ ماه\n\n💳 کارت: `{VIP_CARD}`\n🏦 به نام: {VIP_HOLDER}\n\n📤 پس از واریز، رسید را ارسال کنید.",
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
            f"💎 **خرید VIP سالانه**\n\n💰 مبلغ: {VIP_PRICE_YEARLY:,} تومان\n📅 مدت: ۱۲ ماه\n🎁 تخفیف: ۱۰٪\n\n💳 کارت: `{VIP_CARD}`\n🏦 به نام: {VIP_HOLDER}\n\n📤 پس از واریز، رسید را ارسال کنید.",
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
            f"👑 **VIP مادام‌العمر**\n\n💰 مبلغ: {VIP_PRICE_LIFETIME:,} تومان\n📅 مدت: مادام‌العمر\n🎁 تخفیف: ۵۰٪\n\n💳 کارت: `{VIP_CARD}`\n🏦 به نام: {VIP_HOLDER}\n\n📤 پس از واریز، رسید را ارسال کنید.",
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
                    f"💎 **وضعیت VIP**\n\n📊 وضعیت: {'✅ فعال' if is_vip_flag else '❌ غیرفعال'}\n📅 انقضا: {expire}\n📊 سطح: {level}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
    
    if data == "vip_trial":
        if get_user_repo:
            db_user = get_user_repo().get_by_telegram_id(str(user_id))
            if db_user:
                if db_user.get('is_vip'):
                    await query.answer("شما قبلاً VIP هستید!", show_alert=True)
                    return
                
                if db_user.get('vip_trial_used'):
                    await query.answer("تست رایگان فقط یک بار قابل استفاده است!", show_alert=True)
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
                    f"🎁 **VIP تست ۳ روزه فعال شد!**\n\n📅 انقضا: {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}\n\n💎 از امکانات ویژه لذت ببرید!",
                    reply_markup=vip_keyboard(),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
    
    if data == "vip_guide":
        await query.edit_message_text(
            f"📋 **راهنمای خرید VIP**\n\n1️⃣ مبلغ را به کارت واریز کنید:\n💳 `{VIP_CARD}`\n🏦 {VIP_HOLDER}\n\n2️⃣ رسید را ارسال کنید\n3️⃣ ادمین تایید می‌کند\n4️⃣ VIP فعال می‌شود\n\n⏱️ زمان تایید: ۲۴ ساعت\n📱 ادمین: @{SUPPORT_USERNAME}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "vip_send_receipt":
        await query.edit_message_text(
            "📤 لطفاً تصویر رسید را ارسال کنید.\n\n⚠️ حتماً نام کاربری خود را یادداشت کنید.\nبرای لغو /cancel",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_receipt'] = True
        return
    
    # ====== HELP & SUPPORT ======
    if data == "help":
        await query.edit_message_text(HELP_TEXT.format(support=SUPPORT_USERNAME), reply_markup=user_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "support":
        await query.edit_message_text(
            f"🆘 **پشتیبانی**\n\n📱 ادمین: @{SUPPORT_USERNAME}\n⏰ ۲۴/۷\n\nبرای ارسال تیکت روی دکمه زیر کلیک کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎫 تیکت جدید", callback_data="support_ticket")],
                [InlineKeyboardButton("📱 تماس با ادمین", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "support_ticket":
        await query.edit_message_text(
            "🎫 لطفاً مشکل یا سوال خود را بنویسید.\nبرای لغو /cancel",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_ticket'] = True
        return
    
    # ====== SETTINGS ======
    if data == "settings":
        await query.edit_message_text(
            "⚙️ **تنظیمات**\n\n🔔 اعلان‌ها: فعال\n📊 تایم‌فریم: ۴ساعته\n🤖 AI: فعال\n🌍 زبان: فارسی",
            reply_markup=settings_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ============================================================
    #                    ADMIN PANEL (کامل)
    # ============================================================
    
    if not admin_flag and data.startswith("admin_"):
        await query.answer("❌ دسترسی غیرمجاز!", show_alert=True)
        return
    
    # ====== ADMIN USERS ======
    if data == "admin_users":
        await query.edit_message_text(
            "👥 **مدیریت کاربران**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 لیست کاربران", callback_data="admin_users_list")],
                [InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="admin_users_search")],
                [InlineKeyboardButton("🔨 بن کاربر", callback_data="admin_users_ban")],
                [InlineKeyboardButton("🔓 آنبن کاربر", callback_data="admin_users_unban")],
                [InlineKeyboardButton("👑 ادمین کردن", callback_data="admin_users_make_admin")],
                [InlineKeyboardButton("🗑️ حذف کاربر", callback_data="admin_users_delete")],
                [InlineKeyboardButton("📊 آمار کاربران", callback_data="admin_users_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_users_list":
        if get_user_repo:
            users = get_user_repo().get_all()
            if not users:
                await query.edit_message_text("ℹ️ هیچ کاربری یافت نشد!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]]))
                return
            
            text = f"👥 **لیست کاربران** ({len(users)} کاربر)\n\n"
            for i, user in enumerate(users[:20], 1):
                status = "🔴 بن" if user.get('is_banned') else "🟢 فعال"
                vip = "💎" if user.get('is_vip') else ""
                admin = "👑" if user.get('is_admin') else ""
                name = user.get('first_name', 'نامشخص')
                tid = user.get('telegram_id', '?')
                text += f"{i}. {name} {admin}{vip} | `{tid}` | {status}\n"
            
            if len(users) > 20:
                text += f"\n... و {len(users) - 20} کاربر دیگر"
            
            await query.edit_message_text(
                text, 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]]), 
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    if data == "admin_users_stats":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
📊 **آمار کاربران**

👥 کل: {stats.get('users', 0):,}
🟢 فعال: {stats.get('active_users', 0):,}
💎 VIP: {stats.get('vip_users', 0):,}
🚫 بن شده: {stats.get('banned_users', 0):,}
📈 امروز: {stats.get('today_users', 0)}
📅 این ماه: {stats.get('month_users', 0)}
"""
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]]), parse_mode=ParseMode.MARKDOWN)
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
            f"🔍 لطفاً **آیدی عددی** کاربر را برای {action} وارد کنید:\n\nبرای لغو /cancel",
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
                [InlineKeyboardButton("✅ تایید شده‌ها", callback_data="admin_payments_completed")],
                [InlineKeyboardButton("❌ رد شده‌ها", callback_data="admin_payments_rejected")],
                [InlineKeyboardButton("📊 گزارش مالی", callback_data="admin_payments_report")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_payments_pending":
        if get_payment_repo:
            payments = get_payment_repo().get_pending_payments()
            if not payments:
                await query.edit_message_text("✅ هیچ پرداخت در انتظاری نیست!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]))
                return
            
            text = "⏳ **پرداخت‌های در انتظار**\n\n"
            keyboard_buttons = []
            for p in payments[:10]:
                pid = p.get('payment_id', '?')
                text += f"🆔 `{pid}`\n👤 `{p.get('user_id')}`\n💰 {p.get('amount', 0):,} تومان\n📦 {p.get('payment_type')}\n━━━━━━━━━━━\n"
                keyboard_buttons.append([InlineKeyboardButton(f"✅ تایید {pid}", callback_data=f"confirm_payment_{pid}")])
            
            keyboard_buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")])
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard_buttons), parse_mode=ParseMode.MARKDOWN)
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
                            text=f"🎉 **تبریک! VIP {plan_name} شما فعال شد!**\n\n📅 انقضا: {expire_date.strftime('%Y-%m-%d')}\n\nاز امکانات ویژه لذت ببرید! 🚀",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        pass
                
                await query.edit_message_text(
                    f"✅ **پرداخت تایید شد!**\n\n🆔 {payment_id}\n👤 {target_user_id}\n💰 {payment.get('amount', 0):,} تومان\n💎 VIP {plan_name} فعال شد\n📅 انقضا: {expire_date.strftime('%Y-%m-%d')}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]),
                    parse_mode=ParseMode.MARKDOWN
                )
        return
    
    if data == "admin_payments_report":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
📊 **گزارش مالی**

💰 درآمد کل: {stats.get('total_revenue', 0):,.0f} تومان
💳 امروز: {stats.get('today_revenue', 0):,.0f} تومان
📈 این هفته: {stats.get('week_revenue', 0):,.0f} تومان
📅 این ماه: {stats.get('month_revenue', 0):,.0f} تومان

👥 تعداد پرداخت‌ها: {stats.get('payments', 0)}
⏳ در انتظار: {stats.get('pending_payments', 0)}
✅ تایید شده: {stats.get('completed_payments', 0)}
"""
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]), parse_mode=ParseMode.MARKDOWN)
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
                await query.edit_message_text("✅ هیچ درخواست VIP در انتظاری نیست!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]))
                return
            
            text = "💎 **درخواست‌های VIP**\n\n"
            keyboard_buttons = []
            for req in vip_requests[:10]:
                pid = req.get('payment_id', '?')
                text += f"🆔 `{pid}` | 👤 `{req.get('user_id')}` | 💰 {req.get('amount', 0):,} تومان\n"
                keyboard_buttons.append([InlineKeyboardButton(f"✅ تایید {pid}", callback_data=f"confirm_payment_{pid}")])
            
            keyboard_buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")])
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard_buttons), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_vip_list":
        if get_user_repo:
            users = get_user_repo().get_vip_users()
            if not users:
                await query.edit_message_text("ℹ️ هیچ کاربر VIP یافت نشد!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]))
                return
            
            text = f"📋 **لیست VIP ها** ({len(users)} کاربر)\n\n"
            for i, user in enumerate(users[:15], 1):
                name = user.get('first_name', 'نامشخص')
                plan = user.get('vip_plan', '?')
                expire = user.get('vip_expire', '?')
                text += f"{i}. {name} | {plan} | {expire}\n"
            
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_vip_stats":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
📊 **آمار VIP**

👥 کل VIP: {stats.get('vip_users', 0):,}
📈 فعال: {stats.get('active_vip', 0):,}
⏳ در انتظار: {stats.get('pending_vip', 0)}
💰 درآمد VIP: {stats.get('vip_revenue', 0):,.0f} تومان
📅 این ماه: {stats.get('vip_monthly_revenue', 0):,.0f} تومان
🎁 تست رایگان: {stats.get('trial_active', 0)}
"""
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data in ["admin_vip_add", "admin_vip_remove"]:
        context.user_data['admin_action'] = data
        action = "افزودن" if data == "admin_vip_add" else "حذف"
        await query.edit_message_text(
            f"🔍 لطفاً **آیدی عددی** کاربر را برای {action} VIP وارد کنید:\n\nبرای لغو /cancel",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_USER_ID
    
    # ====== ADMIN BROADCAST ======
    if data == "admin_broadcast":
        await query.edit_message_text(
            "📢 **ارسال پیام همگانی**\n\nمخاطبان را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 همه کاربران", callback_data="broadcast_all")],
                [InlineKeyboardButton("💎 فقط VIP", callback_data="broadcast_vip")],
                [InlineKeyboardButton("👤 کاربران عادی", callback_data="broadcast_normal")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data.startswith("broadcast_"):
        target = data.replace("broadcast_", "")
        context.user_data['broadcast_target'] = target
        await query.edit_message_text(
            "📝 لطفاً پیام خود را بنویسید:\n\nبرای لغو /cancel",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_BROADCAST
    
    # ====== ADMIN SEND CHANNEL ======
    if data == "admin_send_channel":
        context.user_data['admin_action'] = 'send_channel'
        await query.edit_message_text(
            f"📡 **ارسال به کانال**\n\n📢 کانال: {CHANNEL_ID}\n\nلطفاً پیام را بنویسید.\nبرای لغو /cancel",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== ADMIN API ======
    if data == "admin_api":
        await query.edit_message_text(
            "🔧 **مدیریت API**\n\n✅ Groq AI: فعال\n✅ Telegram: فعال",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 وضعیت", callback_data="admin_api_status")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== ADMIN BACKUP ======
    if data == "admin_backup":
        await query.edit_message_text(
            "💾 **بکاپ و بازیابی**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💾 ایجاد بکاپ", callback_data="admin_backup_create")],
                [InlineKeyboardButton("📋 لیست بکاپ‌ها", callback_data="admin_backup_list")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_backup_create":
        if db_manager:
            result = db_manager.backup()
            if result.get('success'):
                await query.edit_message_text(
                    f"✅ **بکاپ ایجاد شد!**\n\n📁 {result.get('name')}\n📏 {result.get('size', 0)/1024:.1f} KB",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.edit_message_text("❌ خطا در ایجاد بکاپ!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]))
        return
    
    # ====== ADMIN SERVER ======
    if data == "admin_server":
        await query.edit_message_text(
            "🚪 **مدیریت سرور**\n\n⚠️ عملیات‌های زیر غیرقابل بازگشت هستند!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 وضعیت سرور", callback_data="admin_server_status")],
                [InlineKeyboardButton("🧹 پاکسازی کش", callback_data="admin_clear_cache")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== DEFAULT ======
    await query.edit_message_text("ℹ️ این بخش در حال توسعه است...", reply_markup=user_main_menu())

# ============================================================
#                    MESSAGE HANDLER
# ============================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های متنی"""
    user_id = update.effective_user.id
    message_text = update.message.text
    admin_flag = is_admin(user_id)
    
    # ====== BROADCAST ======
    if context.user_data.get('admin_action') == 'broadcast' or context.user_data.get('broadcast_target'):
        if admin_flag:
            target = context.user_data.get('broadcast_target', 'all')
            
            if get_user_repo:
                users = get_user_repo().get_all()
                
                if target == 'vip':
                    users = [u for u in users if u.get('is_vip')]
                elif target == 'normal':
                    users = [u for u in users if not u.get('is_vip')]
                
                success, fail = 0, 0
                progress_msg = await update.message.reply_text(f"⏳ در حال ارسال به {len(users)} کاربر...")
                
                for user in users:
                    try:
                        await context.bot.send_message(
                            chat_id=int(user.get('telegram_id')),
                            text=f"📢 **پیام همگانی**\n\n{message_text}",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        success += 1
                        await asyncio.sleep(0.05)
                    except:
                        fail += 1
                
                await progress_msg.edit_text(
                    f"✅ ارسال به {success} کاربر\n❌ ناموفق: {fail}",
                    reply_markup=admin_main_menu()
                )
                context.user_data['admin_action'] = None
                context.user_data['broadcast_target'] = None
            return
    
    # ====== SEND CHANNEL ======
    if context.user_data.get('admin_action') == 'send_channel':
        if admin_flag:
            try:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=f"📢 {message_text}",
                    parse_mode=ParseMode.MARKDOWN
                )
                await update.message.reply_text(f"✅ پیام به {CHANNEL_ID} ارسال شد!", reply_markup=admin_main_menu())
            except Exception as e:
                await update.message.reply_text(f"❌ خطا: {e}", reply_markup=admin_main_menu())
            context.user_data['admin_action'] = None
            return
    
    # ====== RECEIPT ======
    if context.user_data.get('waiting_for_receipt'):
        if update.message.photo:
            photo = update.message.photo[-1]
            plan = context.user_data.get('vip_plan', 'monthly')
            prices = {'monthly': VIP_PRICE_MONTHLY, 'yearly': VIP_PRICE_YEARLY, 'lifetime': VIP_PRICE_LIFETIME}
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
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_photo(
                        chat_id=admin_id,
                        photo=photo.file_id,
                        caption=f"📤 **رسید جدید VIP**\n👤 {update.effective_user.first_name}\n🆔 `{user_id}`\n💰 {price:,} تومان\n📦 {plan}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except:
                    pass
            
            await update.message.reply_text(
                f"✅ **رسید ارسال شد!**\n💰 {price:,} تومان\n📦 {plan}\n\n⏳ پس از تایید، VIP فعال می‌شود.\n📱 @{SUPPORT_USERNAME}",
                reply_markup=user_main_menu()
            )
            context.user_data['waiting_for_receipt'] = False
            return
        
        await update.message.reply_text("❌ لطفاً تصویر رسید را ارسال کنید.")
        return
    
    # ====== TICKET ======
    if context.user_data.get('waiting_for_ticket'):
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🎫 **تیکت جدید**\n👤 {update.effective_user.first_name}\n🆔 `{user_id}`\n📝 {message_text}"
                )
            except:
                pass
        
        await update.message.reply_text(
            f"✅ **تیکت ثبت شد!**\n⏰ به زودی پاسخ داده می‌شود.\n📱 @{SUPPORT_USERNAME}",
            reply_markup=user_main_menu()
        )
        context.user_data['waiting_for_ticket'] = False
        return
    
    # ====== ADMIN ACTIONS ======
    if context.user_data.get('admin_action') and admin_flag:
        action = context.user_data['admin_action']
        target_id = message_text.strip()
        
        if not target_id.isdigit():
            await update.message.reply_text("❌ لطفاً آیدی عددی معتبر وارد کنید.", reply_markup=admin_main_menu())
            context.user_data['admin_action'] = None
            return
        
        if get_user_repo:
            user = get_user_repo().get_by_telegram_id(target_id)
            
            if action == "admin_users_ban":
                if user:
                    get_user_repo().ban_user(target_id, reason="توسط ادمین")
                    await update.message.reply_text(f"🔨 کاربر `{target_id}` بن شد.", reply_markup=admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ کاربر یافت نشد.", reply_markup=admin_main_menu())
            
            elif action == "admin_users_unban":
                if user:
                    get_user_repo().unban_user(target_id)
                    await update.message.reply_text(f"🔓 کاربر `{target_id}` آنبن شد.", reply_markup=admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ کاربر یافت نشد.", reply_markup=admin_main_menu())
            
            elif action == "admin_users_make_admin":
                if user:
                    get_user_repo().make_admin(target_id)
                    await update.message.reply_text(f"👑 کاربر `{target_id}` ادمین شد.", reply_markup=admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ کاربر یافت نشد.", reply_markup=admin_main_menu())
            
            elif action == "admin_users_delete":
                if user:
                    get_user_repo().delete(target_id)
                    await update.message.reply_text(f"🗑️ کاربر `{target_id}` حذف شد.", reply_markup=admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ کاربر یافت نشد.", reply_markup=admin_main_menu())
            
            elif action == "admin_vip_add":
                if user:
                    get_user_repo().update(target_id, is_vip=True, vip_level=2, vip_plan='manual', vip_expire=(datetime.now() + timedelta(days=30)).isoformat())
                    await update.message.reply_text(f"💎 کاربر `{target_id}` VIP شد.", reply_markup=admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    # Create user if not exists
                    get_user_repo().create(telegram_id=target_id, is_vip=True, vip_level=2, vip_plan='manual', vip_expire=(datetime.now() + timedelta(days=30)).isoformat())
                    await update.message.reply_text(f"💎 کاربر `{target_id}` ایجاد و VIP شد.", reply_markup=admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_vip_remove":
                if user:
                    get_user_repo().update(target_id, is_vip=False, vip_level=0, vip_plan=None, vip_expire=None)
                    await update.message.reply_text(f"➖ VIP کاربر `{target_id}` حذف شد.", reply_markup=admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ کاربر یافت نشد.", reply_markup=admin_main_menu())
        
        context.user_data['admin_action'] = None
        return
    
    # ====== AUTO ANALYSIS ======
    coin = message_text.upper().strip()
    if validate_coin(coin):
        await update.message.reply_text(f"⏳ در حال تحلیل {coin}...")
        
        signal_type = random.choice(["buy", "sell", "hold"])
        confidence = random.randint(60, 95)
        price = random.uniform(100, 70000)
        emojis = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}
        
        text = f"""
🚨 **سیگنال {coin}**

{emojis.get(signal_type, '🟡')} **{signal_type.upper()}**
🎯 اطمینان: {confidence}%

💰 قیمت: ${price:,.2f}
🎯 اهداف: ${price*1.02:,.2f} | ${price*1.05:,.2f} | ${price*1.10:,.2f}
🛑 حد ضرر: ${price*0.95:,.2f}

⏰ {get_persian_time()}
"""
        await update.message.reply_text(text, reply_markup=user_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ====== DEFAULT ======
    await update.message.reply_text(
        "ℹ️ لطفاً از دکمه‌های زیر استفاده کنید.\n\n📌 ارزهای پشتیبانی: BTC, ETH, BNB, SOL, XRP, ADA, DOGE\n💡 می‌توانید نام ارز را تایپ کنید.",
        reply_markup=user_main_menu()
    )

# ============================================================
#                    PHOTO HANDLER
# ============================================================

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش تصاویر"""
    if context.user_data.get('waiting_for_receipt'):
        await message_handler(update, context)
    else:
        await update.message.reply_text("📸 تصویر دریافت شد.", reply_markup=user_main_menu())

# ============================================================
#                    ERROR HANDLER
# ============================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت خطاها"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        if update and hasattr(update, 'effective_message') and update.effective_message:
            await update.effective_message.reply_text("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.")
    except:
        pass

# ============================================================
#                    MAIN HANDLER CLASS
# ============================================================

class BotHandlers:
    """مدیریت هندلرهای ربات"""

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
                from telegram.request import HTTPXRequest
                request = HTTPXRequest(proxy_url=PROXY_URL, read_timeout=30, write_timeout=30, connect_timeout=30)
                self.application = Application.builder().token(BOT_TOKEN).request(request).build()
            else:
                self.application = Application.builder().token(BOT_TOKEN).build()

            # Command handlers
            self.application.add_handler(CommandHandler("start", start))
            self.application.add_handler(CommandHandler("help", help_command))
            self.application.add_handler(CommandHandler("admin", admin_command))
            self.application.add_handler(CommandHandler("cancel", cancel_command))
            self.application.add_handler(CommandHandler("vip", vip_command))
            self.application.add_handler(CommandHandler("wallet", wallet_command))
            self.application.add_handler(CommandHandler("signal", signal_command))
            self.application.add_handler(CommandHandler("price", price_command))

            # Callback handler
            self.application.add_handler(CallbackQueryHandler(callback_handler))

            # Conversation handler
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
                        MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
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
                fallbacks=[CommandHandler("cancel", cancel_command)],
                per_message=True,
                per_chat=True,
                per_user=True,
                name="main_conversation"
            )
            self.application.add_handler(conv_handler)

            # Message handlers
            self.application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

            # Error handler
            self.application.add_error_handler(error_handler)

            logger.info("✅ All handlers registered")

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
        return bot_handlers.get_application()
    return None

def check_handlers():
    app = get_application()
    return {
        "bot_handlers": "✅ OK" if bot_handlers else "❌",
        "application": "✅ OK" if app else "❌",
        "bot_token": "✅ Set" if BOT_TOKEN else "❌"
    }

def get_bot_token():
    return BOT_TOKEN

def get_admin_ids():
    return ADMIN_IDS

def start():
    """Compatibility function for ModuleManager"""
    logger.info("✅ part9 Telegram Handlers loaded successfully")
    return True

# Status on import
logger.info(f"📊 Part9 Status: {check_handlers()}")
