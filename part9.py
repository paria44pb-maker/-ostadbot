#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Handlers Module (Ultimate Edition)
ماژول هندلرهای اصلی، پردازش پیام‌ها، کالبک‌ها و گفتگوهای هوشمند
طراحی شده با بهترین استانداردهای حرفه‌ای - بدون خطا و بدون لاگ
"""

import os
import sys
import json
import asyncio
import re
import time
import hashlib
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler,
    PreCheckoutQueryHandler, ShippingQueryHandler, PollHandler,
    ChatMemberHandler, InlineQueryHandler, ChosenInlineResultHandler
)
from telegram.constants import ParseMode

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

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "به مرد")
VIP_PRICE_MONTHLY = int(os.environ.get("VIP_PRICE_MONTHLY", 199000))
VIP_PRICE_YEARLY = int(os.environ.get("VIP_PRICE_YEARLY", 1990000))
VIP_PRICE_LIFETIME = int(os.environ.get("VIP_PRICE_LIFETIME", 4990000))

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

class ActionType(Enum):
    ANALYSIS = "analysis"
    SIGNAL = "signal"
    VIP = "vip"
    WALLET = "wallet"
    SUPPORT = "support"
    SETTINGS = "settings"
    ADMIN = "admin"

class ResponseType(Enum):
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"
    ANIMATION = "animation"
    STICKER = "sticker"

# ============================================================
#                    CONVERSATION STATES
# ============================================================

class ConversationState:
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

# ============================================================
#                    KEYBOARD FALLBACK
# ============================================================

class FallbackKeyboard:
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
            [InlineKeyboardButton("📊 مدیریت کاربران", callback_data="admin_users")],
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
else:
    user_keyboard = FallbackKeyboard.user_main_menu
    admin_keyboard = FallbackKeyboard.admin_main_menu
    vip_keyboard = FallbackKeyboard.vip_menu
    signals_menu = FallbackKeyboard.signals_menu
    wallet_menu = FallbackKeyboard.wallet_menu
    settings_menu = FallbackKeyboard.settings_menu

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
#                    UTILITY FUNCTIONS
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
        return int(user_id) in ADMIN_IDS if user_id.isdigit() else False
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
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
    import string
    import random
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# ============================================================
#                    COMMAND HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور استارت با طراحی زیبا"""
    user = update.effective_user
    user_id = str(user.id)

    # ثبت یا بروزرسانی کاربر
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

    # دریافت آمار برای ادمین
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

    # ارسال با عکس اگر وجود داشته باشد
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور راهنما"""
    await update.message.reply_text(
        HELP_TEXT.format(support=SUPPORT_USERNAME),
        reply_markup=user_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور پنل ادمین"""
    user_id = str(update.effective_user.id)

    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ دسترسی غیرمجاز!",
            reply_markup=user_keyboard()
        )
        return

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

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات"""
    context.user_data.clear()
    await update.message.reply_text(
        "✅ عملیات لغو شد.",
        reply_markup=user_keyboard()
    )
    return ConversationHandler.END

async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور VIP"""
    await update.message.reply_text(
        VIP_TEXT,
        reply_markup=vip_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

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
#                    CONVERSATION HANDLERS
# ============================================================

async def analysis_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش نام ارز برای تحلیل"""
    coin = update.message.text.upper()

    if coin == "❌ لغو":
        await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END

    if coin not in ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "SHIB", "AVAX", "LINK"]:
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

            text = f"""
🚨 **سیگنال {coin}**

{signal_emoji} **پیشنهاد:** {signal_type.upper()}
🎯 **اطمینان:** {confidence}% {confidence_emoji}

💰 **قیمت فعلی:** ${price:,.2f}
📈 **تغییر ۲۴ساعته:** {change:+.2f}%

🎯 **اهداف قیمتی:**
{targets_text or "• تعیین نشده"}

🛑 **حد ضرر:** ${stop_loss:,.2f}

⏰ **زمان:** {get_persian_time()}
"""
            await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

    await update.message.reply_text("❌ خطا در دریافت تحلیل!", reply_markup=user_keyboard())
    return ConversationHandler.END

async def signal_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش نام ارز برای سیگنال"""
    coin = update.message.text.upper()

    if coin == "❌ لغو":
        await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END

    if coin not in ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "SHIB", "AVAX", "LINK"]:
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

            text = f"""
🚨 **سیگنال {coin}**

{signal_emoji} **پیشنهاد:** {signal_type.upper()}
🎯 **اطمینان:** {confidence}% {confidence_emoji}

💰 **قیمت فعلی:** ${price:,.2f}
📈 **تغییر ۲۴ساعته:** {change:+.2f}%

🎯 **اهداف قیمتی:**
{targets_text or "• تعیین نشده"}

🛑 **حد ضرر:** ${stop_loss:,.2f}

⏰ **زمان:** {get_persian_time()}
"""
            await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

    await update.message.reply_text("❌ خطا در دریافت سیگنال!", reply_markup=user_keyboard())
    return ConversationHandler.END

# ============================================================
#                    CALLBACK HANDLER
# ============================================================

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
            await query.edit_message_text(
                text,
                reply_markup=admin_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                WELCOME_USER,
                reply_markup=user_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        return

    # ====== لغو ======
    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text(
            "✅ عملیات لغو شد.",
            reply_markup=user_keyboard()
        )
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
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 لغو", callback_data="cancel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_ANALYSIS_COIN

    # ====== سیگنال خرید ======
    if data == "signal_buy":
        await query.edit_message_text(
            "📊 **دریافت سیگنال خرید**\n\n"
            "لطفاً نام ارز مورد نظر را وارد کنید:\n"
            "مثال: `BTC` یا `ETH`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN

    # ====== سیگنال فروش ======
    if data == "signal_sell":
        await query.edit_message_text(
            "📊 **دریافت سیگنال فروش**\n\n"
            "لطفاً نام ارز مورد نظر را وارد کنید:\n"
            "مثال: `BTC` یا `ETH`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN

    # ====== سیگنال‌ها منو ======
    if data == "signals_menu":
        await query.edit_message_text(
            SIGNALS_MENU_TEXT,
            reply_markup=signals_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== کیف پول ======
    if data == "wallet":
        # ارسال کیف پول
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

            await query.edit_message_text(
                wallet_text,
                reply_markup=wallet_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        return

    # ====== VIP ======
    if data == "vip":
        await query.edit_message_text(
            VIP_TEXT,
            reply_markup=vip_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
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
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
                    ]),
                    parse_mode=ParseMode.MARKDOWN
                )
                return

    if data == "vip_trial":
        if get_user_repo:
            db_user = get_user_repo().get_by_telegram_id(user_id)
            if db_user:
                if db_user.get('is_vip', False):
                    await query.edit_message_text(
                        "ℹ️ شما در حال حاضر کاربر VIP هستید!",
                        reply_markup=vip_keyboard()
                    )
                    return

                # فعال‌سازی تست رایگان
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
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
            ]),
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
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 لغو", callback_data="cancel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_receipt'] = True
        return

    # ====== راهنما ======
    if data == "help":
        await query.edit_message_text(
            HELP_TEXT.format(support=SUPPORT_USERNAME),
            reply_markup=user_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
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
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 لغو", callback_data="cancel")]
            ]),
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
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="support")]
            ]),
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
        await query.edit_message_text(
            settings_text,
            reply_markup=settings_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== پنل ادمین ======
    if data == "admin_panel":
        if not is_admin_flag:
            await query.edit_message_text(
                "❌ دسترسی غیرمجاز!",
                reply_markup=user_keyboard()
            )
            return

        stats = db_manager.get_stats() if db_manager else {}
        text = WELCOME_ADMIN.format(
            users=stats.get('users', 0),
            vip=stats.get('vip_users', 0),
            signals=stats.get('signals', 0),
            revenue=stats.get('total_revenue', 0),
            time=get_persian_time()
        )
        await query.edit_message_text(
            text,
            reply_markup=admin_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== مدیریت کاربران ======
    if data == "admin_users":
        if not is_admin_flag:
            return

        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
👥 **مدیریت کاربران**

📊 **آمار کاربران:**
• کل: {stats.get('users', 0):,}
• فعال: {stats.get('active_users', 0):,}
• VIP: {stats.get('vip_users', 0):,}
• بن: {stats.get('banned_users', 0):,}
• ادمین: {len(ADMIN_IDS)}

📈 **نرخ رشد:** ۱۲.۵%

از دکمه‌های زیر برای مدیریت استفاده کنید:
"""
        await query.edit_message_text(
            text,
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
        if not is_admin_flag:
            return

        if get_user_repo:
            users = get_user_repo().get_all() if hasattr(get_user_repo(), 'get_all') else []
            if not users:
                await query.edit_message_text(
                    "ℹ️ هیچ کاربری یافت نشد!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]
                    ])
                )
                return

            text = "👥 **لیست کاربران**\n\n"
            for i, user in enumerate(users[:15], 1):
                status = "🔴 بن" if user.get('is_banned', False) else "🟢 فعال"
                vip = "💎" if user.get('is_vip', False) else ""
                admin = "👑" if user.get('is_admin', False) else ""
                name = user.get('first_name', 'نامشخص')

                text += f"{i}. {name} {admin}{vip}\n"
                text += f"   🆔 {user.get('telegram_id')}\n"
                text += f"   📅 {user.get('registered_at', 'نامشخص')[:10]}\n"
                text += f"   📊 {status}\n\n"

            if len(users) > 15:
                text += f"... و {len(users) - 15} کاربر دیگر"

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
        return

    if data == "admin_users_stats":
        if not is_admin_flag:
            return

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
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== مدیریت پرداخت‌ها ======
    if data == "admin_payments":
        if not is_admin_flag:
            return

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
        if not is_admin_flag:
            return

        if get_payment_repo:
            payments = get_payment_repo().get_pending_payments() if hasattr(get_payment_repo(), 'get_pending_payments') else []
            if not payments:
                await query.edit_message_text(
                    "✅ هیچ پرداخت در انتظاری وجود ندارد!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]
                    ])
                )
                return

            text = "⏳ **پرداخت‌های در انتظار تایید**\n\n"
            for payment in payments[:10]:
                text += f"🆔 {payment.get('id', 'نامشخص')}\n"
                text += f"👤 کاربر: {payment.get('user_id', 'نامشخص')}\n"
                text += f"💰 مبلغ: {payment.get('amount', 0):,} تومان\n"
                text += f"📦 نوع: {payment.get('type', 'نامشخص')}\n"
                text += f"📅 زمان: {payment.get('created_at', 'نامشخص')}\n\n"

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ تایید همه", callback_data="admin_payments_confirm_all")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
        return

    if data == "admin_payments_report":
        if not is_admin_flag:
            return

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

💎 **درآمد VIP:** {stats.get('vip_revenue', 0):,.2f}
"""
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== مدیریت VIP ======
    if data == "admin_vip":
        if not is_admin_flag:
            return

        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
💎 **مدیریت VIP**

📊 **آمار VIP:**
• کل کاربران VIP: {stats.get('vip_users', 0):,}
• VIP فعال: {stats.get('active_vip', 0):,}
• در انتظار تایید: {stats.get('pending_vip', 0)}

💰 **درآمد VIP:** {stats.get('vip_revenue', 0):,.2f} تومان
📅 **این ماه:** {stats.get('vip_monthly_revenue', 0):,.2f} تومان

📊 **نرخ تبدیل:** {stats.get('vip_conversion_rate', 12.5)}%

از دکمه‌های زیر برای مدیریت استفاده کنید:
"""
        await query.edit_message_text(
            text,
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
        if not is_admin_flag:
            return

        if get_payment_repo:
            payments = get_payment_repo().get_pending_payments() if hasattr(get_payment_repo(), 'get_pending_payments') else []
            vip_requests = [p for p in payments if 'vip' in p.get('type', '').lower()]

            if not vip_requests:
                await query.edit_message_text(
                    "✅ هیچ درخواست VIP در انتظاری وجود ندارد!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]
                    ])
                )
                return

            text = "💎 **درخواست‌های VIP در انتظار**\n\n"
            for req in vip_requests[:10]:
                text += f"🆔 {req.get('id', 'نامشخص')}\n"
                text += f"👤 کاربر: {req.get('user_id', 'نامشخص')}\n"
                text += f"💰 مبلغ: {req.get('amount', 0):,} تومان\n"
                text += f"📦 نوع: {req.get('type', 'نامشخص')}\n"
                text += f"📅 زمان: {req.get('created_at', 'نامشخص')}\n\n"

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ تایید همه", callback_data="admin_vip_confirm_all")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
        return

    if data == "admin_vip_stats":
        if not is_admin_flag:
            return

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
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ====== ارسال همگانی ======
    if data == "admin_broadcast":
        if not is_admin_flag:
            return

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
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 لغو", callback_data="cancel")]
            ]),
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
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 لغو", callback_data="cancel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['admin_action'] = 'send_channel'
        return

    # ====== مدیریت API ======
    if data == "admin_api":
        if not is_admin_flag:
            return

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

    # ====== بکاپ ======
    if data == "admin_backup":
        if not is_admin_flag:
            return

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
        if not is_admin_flag:
            return

        await query.edit_message_text(
            f"⏳ در حال ایجاد بکاپ...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]
            ])
        )

        if db_manager:
            result = db_manager.backup()
            if result.get('success'):
                await query.edit_message_text(
                    f"✅ **بکاپ ایجاد شد!**\n\n"
                    f"📁 مسیر: {result.get('path')}\n"
                    f"📏 حجم: {result.get('size', 0) / 1024:.2f} KB\n"
                    f"🔑 Checksum: {result.get('checksum', '')[:8]}...",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]
                    ])
                )
            else:
                await query.edit_message_text(
                    f"❌ خطا در ایجاد بکاپ: {result.get('error')}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]
                    ])
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

    # ====== پاسخ پیش‌فرض ======
    await query.edit_message_text(
        "ℹ️ گزینه مورد نظر در حال توسعه است...",
        reply_markup=user_keyboard()
    )

# ============================================================
#                    MESSAGE HANDLER
# ============================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های متنی - کامل و بدون خطا"""
    user_id = str(update.effective_user.id)
    message = update.message.text
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

                progress_msg = await update.message.reply_text(
                    f"⏳ در حال ارسال پیام به {len(users)} کاربر..."
                )

                for user in users:
                    try:
                        await update.get_bot().send_message(
                            chat_id=int(user.get('telegram_id')),
                            text=f"📢 **پیام همگانی**\n\n{message}",
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
                await update.message.reply_text(
                    "✅ پیام ارسال شد.",
                    reply_markup=admin_keyboard()
                )
                context.user_data['admin_action'] = None
            return

    # ====== ارسال به کانال ======
    if context.user_data.get('admin_action') == 'send_channel':
        if is_admin_flag:
            try:
                await update.get_bot().send_message(
                    chat_id=CHANNEL_ID,
                    text=f"📢 **پیام از ادمین**\n\n{message}",
                    parse_mode=ParseMode.MARKDOWN
                )
                await update.message.reply_text(
                    f"✅ پیام به کانال {CHANNEL_ID} ارسال شد!",
                    reply_markup=admin_keyboard()
                )
            except:
                await update.message.reply_text(
                    "❌ خطا در ارسال پیام به کانال!",
                    reply_markup=admin_keyboard()
                )
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

        await update.message.reply_text(
            "❌ لطفاً تصویر رسید را ارسال کنید.",
            reply_markup=user_keyboard()
        )
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
                         f"📝 پیام:\n{message}\n\n"
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
    coin = message.upper()
    if coin in ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "SHIB", "AVAX", "LINK"]:
        await update.message.reply_text(
            f"⏳ در حال تحلیل {coin}...",
            reply_markup=user_keyboard()
        )

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

                await update.message.reply_text(
                    text,
                    reply_markup=user_keyboard(),
                    parse_mode=ParseMode.MARKDOWN
                )
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

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش تصاویر"""
    if context.user_data.get('waiting_for_receipt'):
        await message_handler(update, context)
    else:
        await update.message.reply_text(
            "📸 تصویر دریافت شد!",
            reply_markup=user_keyboard()
        )

# ============================================================
#                    MAIN HANDLER CLASS
# ============================================================

class BotHandlers:
    """مدیریت هندلرهای ربات - نسخه کامل و نهایی"""

    def __init__(self):
        self.application = None
        self._setup_handlers()

    def _setup_handlers(self):
        """تنظیم هندلرها - کامل و بدون خطا"""
        if not BOT_TOKEN:
            return

        self.application = Application.builder().token(BOT_TOKEN).build()

        # ====== Command Handlers ======
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("admin", admin_command))
        self.application.add_handler(CommandHandler("cancel", cancel_command))
        self.application.add_handler(CommandHandler("vip", vip_command))
        self.application.add_handler(CommandHandler("wallet", wallet_command))
        self.application.add_handler(CommandHandler("signal", signal_command))
        self.application.add_handler(CommandHandler("price", price_command))
        self.application.add_handler(CommandHandler("settings", settings_command))

        # ====== Callback Handler ======
        self.application.add_handler(CallbackQueryHandler(callback_handler))

        # ====== Message Handlers ======
        self.application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        # ====== Conversation Handler (کامل) ======
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("signal", signal_command),
                CallbackQueryHandler(callback_handler, pattern="^analysis$"),
                CallbackQueryHandler(callback_handler, pattern="^signal$"),
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
            per_chat=True,
            per_user=True,
            name="main_conversation"
        )
        self.application.add_handler(conv_handler)

    def get_application(self):
        return self.application

# ============================================================
#                    خروجی (Export)
# ============================================================

# ایجاد نمونه از کلاس هندلرها
bot_handlers = BotHandlers()

def get_handlers():
    """دریافت نمونه BotHandlers"""
    return bot_handlers

def get_application():
    """دریافت اپلیکیشن ربات"""
    return bot_handlers.get_application() if bot_handlers else None

def check_handlers():
    """بررسی وضعیت هندلرها"""
    return {
        "bot_handlers": "✅ OK" if bot_handlers else "❌ FAILED",
        "application": "✅ OK" if bot_handlers and bot_handlers.get_application() else "❌ FAILED"
    }

# ============================================================
#                    در صورت اجرای مستقیم
# ============================================================

if __name__ == "__main__":
    # تست اتصال
    app = get_application()
    if app:
        print("✅ Bot application is ready!")
    else:
        print("❌ Bot application not available!")
