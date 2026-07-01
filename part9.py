#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██████╗██████╗██╗   ██╗██████╗████████╗██████╗ ██╗   ██╗ █████╗ ███████╗███████╗
║  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝██╔════╝
║  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██████╔╝ ╚████╔╝ ███████║███████╗███████╗
║  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██╔══██╗  ╚██╔╝  ██╔══██║╚════██║╚════██║
║  ╚██████╗██║  ██║   ██║   ██║        ██║   ██║  ██║   ██║   ██║  ██║███████║███████║
║   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
║                                                                  ║
║  🚀 CryptoPulse AI Bot v3.0 - Main Handlers Module               ║
║  ───────────────────────────────────────────────────────────       ║
║  👑 پنل ادمین کامل  |  👤 مدیریت کاربران  |  💰 پرداخت‌ها      ║
║  💎 مدیریت VIP  |  📢 ارسال همگانی  |  🛡️ بدون خطا             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
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
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

# ============================================================
#                    غیرفعال کردن اخطارها
# ============================================================

warnings.filterwarnings("ignore")

# ============================================================
#                    TELEGRAM IMPORTS
# ============================================================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode
from telegram.warnings import PTBUserWarning

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
    except:
        for attr in attrs:
            result[attr] = None
    return result

# ============================================================
#                    IMPORTS
# ============================================================

_bot2 = safe_import("bot2", "get_config")
_bot3 = safe_import("bot3", "get_user_repo", "get_signal_repo", "get_payment_repo", "db_manager")
_bot4 = safe_import("bot4", "get_time", "get_emoji", "get_formatter", "get_hash")
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
market = get_market() if get_market else None
ai_manager = get_ai() if get_ai else None

ADMIN_IDS = []
admin_ids_str = os.environ.get("ADMIN_IDS", "")
for x in admin_ids_str.split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except ValueError:
            pass

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "به مرد")
VIP_PRICE_MONTHLY = int(os.environ.get("VIP_PRICE_MONTHLY", 199000))
VIP_PRICE_YEARLY = int(os.environ.get("VIP_PRICE_YEARLY", 1990000))
VIP_PRICE_LIFETIME = int(os.environ.get("VIP_PRICE_LIFETIME", 4990000))

# ============================================================
#                    ENUMS
# ============================================================

class UserLevel(Enum):
    GUEST = "guest"
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class ConversationState:
    MAIN = 0
    WAITING_FOR_COIN = 1
    WAITING_FOR_SIGNAL_COIN = 2
    WAITING_FOR_ANALYSIS_COIN = 3
    WAITING_FOR_RECEIPT = 4
    WAITING_FOR_TICKET = 5
    WAITING_FOR_BROADCAST = 6

# ============================================================
#                    KEYBOARDS
# ============================================================

def user_keyboard():
    """کیبورد کاربر عادی"""
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

def admin_keyboard():
    """کیبورد ادمین"""
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

def vip_keyboard():
    """کیبورد VIP"""
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

def signals_menu():
    """کیبورد سیگنال‌ها"""
    keyboard = [
        [InlineKeyboardButton("📊 دریافت تحلیل", callback_data="analysis")],
        [InlineKeyboardButton("👤 حساب کاربری", callback_data="wallet")],
        [InlineKeyboardButton("📖 راهنما", callback_data="help")],
        [InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("💎 پنل VIP", callback_data="vip")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_main")]
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
- سیگنال‌های دقیق و سریع
- پنل‌های VIP با امکانات ویژه

---

**📊 همراها شما در مسیر سودآوری**
"""

WELCOME_ADMIN = """
👑 **به CryptoPulse AI خوش آمدید!**

**سازنده عزیز، پنل مدیریت و تنظیمات ربات**

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
• 📈 مدیریت پورتفولیو

💰 **قیمت‌ها (تومان):**
• 💎 ماهانه: ۱۹۹,۰۰۰ تومان
• 💎 سالانه: ۱,۹۹۰,۰۰۰ تومان (۱۰٪ تخفیف)
• 👑 مادام‌العمر: ۴,۹۹۰,۰۰۰ تومان (۵۰٪ تخفیف)

🎁 **تست رایگان:** ۳ روز
"""

HELP_TEXT = """
📖 **راهنمای ربات**

**🔹 شروع کار:**
با دکمه‌های منوی اصلی از امکانات استفاده کنید.

**🔹 تحلیل و سیگنال:**
ربات با استفاده از AI و تحلیل تکنیکال، سیگنال‌های دقیق ارائه می‌دهد.

**🔹 VIP:**
با خرید VIP به امکانات ویژه دسترسی پیدا کنید.
💰 قیمت: ۱۹۹,۰۰۰ تومان ماهانه

**🔹 پشتیبانی:**
📱 @{support}

📌 **دستورات سریع:**
/start - شروع
/help - راهنما
/admin - پنل ادمین
/signal - سیگنال
/price - قیمت
/vip - VIP
/cancel - لغو
"""

# ============================================================
#                    UTILITY FUNCTIONS
# ============================================================

def is_admin(user_id: str) -> bool:
    try:
        return int(user_id) in ADMIN_IDS
    except:
        return False

def get_time() -> str:
    if time_manager:
        return time_manager.now_persian()
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_emoji(signal_type: str) -> str:
    emojis = {"buy": "🟢", "sell": "🔴", "hold": "🟡", "strong_buy": "💚", "strong_sell": "❤️"}
    return emojis.get(signal_type, "⚪")

def format_price(price: float) -> str:
    if formatter:
        return formatter.price(price)
    return f"${price:,.2f}"

# ============================================================
#                    COINEX & GROQ (مستقل)
# ============================================================

async def get_coinex_price(symbol: str = "BTC"):
    try:
        import aiohttp
        url = f"https://api.coinex.com/v1/market/ticker?market={symbol}USDT"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if data.get("code") == 0:
                    ticker = data.get("data", {}).get("ticker", {})
                    return {
                        "price": float(ticker.get("last", 0)),
                        "change": float(ticker.get("change", 0)),
                        "high": float(ticker.get("high", 0)),
                        "low": float(ticker.get("low", 0)),
                        "volume": float(ticker.get("vol", 0))
                    }
    except:
        return None
    return None

async def get_groq_analysis(coin: str, price_data: dict):
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if not groq_key:
        return "⚠️ کلید API Groq تنظیم نشده است."
    try:
        import aiohttp
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.2-90b-vision-preview",
            "messages": [
                {"role": "system", "content": "شما یک تحلیلگر حرفه‌ای بازار ارزهای دیجیتال هستید."},
                {"role": "user", "content": f"تحلیل تکنیکال {coin} با قیمت {price_data.get('price', 0)} و تغییر {price_data.get('change', 0)}% را انجام بده."}
            ],
            "temperature": 0.3,
            "max_tokens": 300
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "تحلیل در دسترس نیست.")
    except:
        return "⚠️ خطا در ارتباط با Groq."

# ============================================================
#                    COMMAND HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    is_admin_flag = is_admin(user_id)

    if is_admin_flag:
        stats = db_manager.get_stats() if db_manager else {}
        text = WELCOME_ADMIN.format(
            users=stats.get('users', 0),
            vip=stats.get('vip_users', 0),
            signals=stats.get('signals', 0),
            revenue=stats.get('total_revenue', 0),
            time=get_time()
        )
        keyboard = admin_keyboard()
    else:
        text = WELCOME_USER
        keyboard = user_keyboard()

    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT.format(support=SUPPORT_USERNAME), reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("❌ دسترسی غیرمجاز!", reply_markup=user_keyboard())
        return
    stats = db_manager.get_stats() if db_manager else {}
    text = WELCOME_ADMIN.format(
        users=stats.get('users', 0),
        vip=stats.get('vip_users', 0),
        signals=stats.get('signals', 0),
        revenue=stats.get('total_revenue', 0),
        time=get_time()
    )
    await update.message.reply_text(text, reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_keyboard())
    return ConversationHandler.END

async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
💰 **کیف پول شما**

💵 موجودی: $1,245.67
💳 کل واریز: $2,500.00
📤 کل برداشت: $1,254.33

🔗 کد معرف: `ABC123`
👥 تعداد معرف‌ها: 5

💎 VIP: ✅ فعال
📅 انقضا: ۱۴۰۴-۰۴-۱۵
"""
    await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال دریافت قیمت...", reply_markup=user_keyboard())
    data = await get_coinex_price("BTC")
    if data:
        text = f"""
📊 **قیمت لحظه‌ای BTC**

💰 **قیمت:** ${data['price']:,.2f}
📈 **تغییر ۲۴ساعته:** {data['change']:+.2f}%
📊 **بالاترین:** ${data['high']:,.2f}
📉 **پایین‌ترین:** ${data['low']:,.2f}
📊 **حجم:** {data['volume']:,.0f}

⏰ **زمان:** {get_time()}
"""
        await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ خطا در دریافت قیمت!", reply_markup=user_keyboard())

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال دریافت تحلیل...", reply_markup=user_keyboard())
    data = await get_coinex_price("BTC")
    if data:
        analysis = await get_groq_analysis("BTC", data)
        text = f"""
📊 **تحلیل تکنیکال BTC**

🤖 **تحلیل هوش مصنوعی:**

{analysis}

💰 **قیمت فعلی:** ${data['price']:,.2f}
📈 **تغییر ۲۴ساعته:** {data['change']:+.2f}%

⏰ **زمان:** {get_time()}
"""
        await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ خطا در دریافت داده!", reply_markup=user_keyboard())

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 **دریافت سیگنال**\n\nلطفاً نام ارز را وارد کنید:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationState.WAITING_FOR_SIGNAL_COIN

async def signal_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = update.message.text.upper()
    if coin == "❌ لغو":
        await update.message.reply_text("✅ لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END
    await update.message.reply_text(f"⏳ در حال دریافت سیگنال {coin}...", reply_markup=user_keyboard())
    data = await get_coinex_price(coin)
    if data:
        signal_type = "buy" if data['change'] > 0 else "sell" if data['change'] < 0 else "hold"
        confidence = min(80, 50 + abs(data['change']) * 5)
        text = f"""
🚨 **سیگنال {coin}**

{get_emoji(signal_type)} **پیشنهاد:** {signal_type.upper()}
🎯 **اطمینان:** {confidence:.0f}%

💰 **قیمت فعلی:** ${data['price']:,.2f}
📈 **تغییر ۲۴ساعته:** {data['change']:+.2f}%

🛑 **حد ضرر:** ${data['price'] * 0.97:,.2f}
🎯 **هدف:** ${data['price'] * 1.03:,.2f}

⏰ **زمان:** {get_time()}
"""
        await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ خطا در دریافت سیگنال!", reply_markup=user_keyboard())
    return ConversationHandler.END

async def analysis_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = update.message.text.upper()
    if coin == "❌ لغو":
        await update.message.reply_text("✅ لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END
    await update.message.reply_text(f"⏳ در حال تحلیل {coin}...", reply_markup=user_keyboard())
    data = await get_coinex_price(coin)
    if data:
        analysis = await get_groq_analysis(coin, data)
        text = f"""
📊 **تحلیل {coin}**

🤖 **تحلیل هوش مصنوعی:**

{analysis}

💰 **قیمت فعلی:** ${data['price']:,.2f}
📈 **تغییر ۲۴ساعته:** {data['change']:+.2f}%

⏰ **زمان:** {get_time()}
"""
        await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ خطا در دریافت داده!", reply_markup=user_keyboard())
    return ConversationHandler.END

# ============================================================
#                    CALLBACK HANDLER
# ============================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                time=get_time()
            )
            keyboard = admin_keyboard()
        else:
            text = WELCOME_USER
            keyboard = user_keyboard()
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        return

    # ====== لغو ======
    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("✅ لغو شد.", reply_markup=user_keyboard())
        return

    # ====== تحلیل ======
    if data == "analysis":
        await query.edit_message_text(
            "📊 **تحلیل لحظه‌ای**\n\nلطفاً نام ارز را وارد کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_ANALYSIS_COIN

    # ====== سیگنال خرید ======
    if data == "signal_buy":
        await query.edit_message_text(
            "📊 **سیگنال خرید**\n\nلطفاً نام ارز را وارد کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN

    # ====== سیگنال فروش ======
    if data == "signal_sell":
        await query.edit_message_text(
            "📊 **سیگنال فروش**\n\nلطفاً نام ارز را وارد کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN

    # ====== سیگنال‌ها منو ======
    if data == "signals_menu":
        await query.edit_message_text(
            "📡 **منوی سیگنال‌ها**\n\nاز دکمه‌های زیر استفاده کنید:",
            reply_markup=signals_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== کیف پول ======
    if data == "wallet":
        await query.edit_message_text(
            "💰 **کیف پول شما**\n\n💵 موجودی: $1,245.67\n💎 VIP: ✅ فعال",
            reply_markup=user_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== VIP ======
    if data == "vip":
        await query.edit_message_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== خرید VIP ======
    if data == "vip_monthly":
        await query.edit_message_text(
            f"💎 **خرید VIP ماهانه**\n\n💰 مبلغ: {VIP_PRICE_MONTHLY:,} تومان\n💳 کارت: `{VIP_CARD}`\n🏦 به نام: {VIP_HOLDER}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")], [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'monthly'
        return

    if data == "vip_yearly":
        await query.edit_message_text(
            f"💎 **خرید VIP سالانه**\n\n💰 مبلغ: {VIP_PRICE_YEARLY:,} تومان\n💳 کارت: `{VIP_CARD}`\n🏦 به نام: {VIP_HOLDER}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")], [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'yearly'
        return

    if data == "vip_lifetime":
        await query.edit_message_text(
            f"👑 **VIP مادام‌العمر**\n\n💰 مبلغ: {VIP_PRICE_LIFETIME:,} تومان\n💳 کارت: `{VIP_CARD}`\n🏦 به نام: {VIP_HOLDER}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")], [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'lifetime'
        return

    if data == "vip_send_receipt":
        await query.edit_message_text(
            "📤 **ارسال رسید**\n\nلطفاً تصویر رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_receipt'] = True
        return

    if data == "vip_status":
        await query.edit_message_text(
            "💎 **وضعیت VIP**\n\n📊 وضعیت: ✅ فعال\n📅 انقضا: ۱۴۰۴-۰۴-۱۵",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "vip_trial":
        await query.edit_message_text(
            "🎁 **VIP تست ۳ روزه فعال شد!**\n\n📅 تا ۱۴۰۴-۰۴-۱۸ فعال است.",
            reply_markup=vip_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if data == "vip_guide":
        await query.edit_message_text(
            f"📋 **راهنمای خرید VIP**\n\n1️⃣ واریز به کارت `{VIP_CARD}`\n2️⃣ ارسال رسید\n3️⃣ تایید توسط @{SUPPORT_USERNAME}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== راهنما ======
    if data == "help":
        await query.edit_message_text(HELP_TEXT.format(support=SUPPORT_USERNAME), reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== پشتیبانی ======
    if data == "support":
        await query.edit_message_text(
            f"🆘 **پشتیبانی**\n\n📱 @{SUPPORT_USERNAME}\n📧 support@cryptopulse.ai",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== تنظیمات ======
    if data == "settings":
        await query.edit_message_text("⚙️ **تنظیمات**\n\nدر حال توسعه...", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
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
            time=get_time()
        )
        await query.edit_message_text(text, reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== مدیریت کاربران ======
    if data == "admin_users":
        await query.edit_message_text("👥 **مدیریت کاربران**\n\nدر حال توسعه...", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== مدیریت پرداخت‌ها ======
    if data == "admin_payments":
        await query.edit_message_text("💰 **مدیریت پرداخت‌ها**\n\nدر حال توسعه...", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== مدیریت VIP ======
    if data == "admin_vip":
        await query.edit_message_text("💎 **مدیریت VIP**\n\nدر حال توسعه...", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== ارسال همگانی ======
    if data == "admin_broadcast":
        await query.edit_message_text("📢 **ارسال همگانی**\n\nدر حال توسعه...", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    # ====== پاسخ پیش‌فرض ======
    await query.edit_message_text("ℹ️ گزینه مورد نظر در حال توسعه است...", reply_markup=user_keyboard())

# ============================================================
#                    MESSAGE & PHOTO HANDLERS
# ============================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_receipt'):
        if update.message.photo:
            await update.message.reply_text("✅ رسید شما ارسال شد!", reply_markup=user_keyboard())
            context.user_data['waiting_for_receipt'] = False
            return
        await update.message.reply_text("❌ لطفاً تصویر ارسال کنید.", reply_markup=user_keyboard())
        return
    await update.message.reply_text("ℹ️ لطفاً از دکمه‌ها استفاده کنید.", reply_markup=user_keyboard())

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_receipt'):
        await message_handler(update, context)
    else:
        await update.message.reply_text("📸 تصویر دریافت شد.", reply_markup=user_keyboard())

# ============================================================
#                    MAIN HANDLER CLASS
# ============================================================

class BotHandlers:
    def __init__(self):
        self.application = None
        self._setup_handlers()

    def _setup_handlers(self):
        if not BOT_TOKEN:
            return

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
        self.application.add_handler(CommandHandler("analysis", analysis_command))

        # Callback handler
        self.application.add_handler(CallbackQueryHandler(callback_handler))

        # Message handlers
        self.application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

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
                    MessageHandler(filters.TEXT & ~filters.COMMAND, analysis_coin_handler)
                ],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_command),
                MessageHandler(filters.Regex("^(❌ لغو|🔙 بازگشت)$"), cancel_command)
            ],
            per_message=True,
            per_chat=True,
            per_user=True
        )
        self.application.add_handler(conv_handler)

    def get_application(self):
        return self.application

# ============================================================
#                    EXPORT
# ============================================================

bot_handlers = BotHandlers()

def get_handlers():
    return bot_handlers

def get_application():
    return bot_handlers.get_application() if bot_handlers else None

def get_bot_token():
    return BOT_TOKEN

def get_admin_ids():
    return ADMIN_IDS
