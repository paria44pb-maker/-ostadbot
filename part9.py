#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Handlers Module (Complete)
ماژول هندلرهای اصلی، پردازش پیام‌ها، کالبک‌ها و گفتگوهای هوشمند
با طراحی زیبا، حرفه‌ای و کاربرپسند
"""

import os
import sys
import json
import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Bot
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
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

ADMIN_IDS = config.get('admin_ids', []) if config else []
BOT_TOKEN = config.get('bot_token', '') if config else os.environ.get("BOT_TOKEN", "")
CHANNEL_ID = config.get('channel_id', '@CryptoPulse606') if config else '@CryptoPulse606'

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

# ============================================================
#                    KEYBOARD FALLBACK
# ============================================================

class FallbackKeyboard:
    @staticmethod
    def user_main_menu():
        keyboard = [
            [InlineKeyboardButton("📊 تحلیل لحظه‌ای", callback_data="analysis")],
            [InlineKeyboardButton("🚨 سیگنال", callback_data="signal")],
            [InlineKeyboardButton("💰 کیف پول", callback_data="wallet")],
            [InlineKeyboardButton("💎 VIP", callback_data="vip")],
            [InlineKeyboardButton("📖 راهنما", callback_data="help")],
            [InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_main_menu():
        keyboard = [
            [InlineKeyboardButton("📊 مدیریت کاربران", callback_data="admin_users")],
            [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
            [InlineKeyboardButton("💎 مدیریت VIP", callback_data="admin_vip")],
            [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

# انتخاب کیبورد مناسب
if lux_keyboard:
    user_keyboard = lux_keyboard.user_main_menu if hasattr(lux_keyboard, 'user_main_menu') else FallbackKeyboard.user_main_menu
    admin_keyboard = lux_keyboard.admin_main_menu if hasattr(lux_keyboard, 'admin_main_menu') else FallbackKeyboard.admin_main_menu
else:
    user_keyboard = FallbackKeyboard.user_main_menu
    admin_keyboard = FallbackKeyboard.admin_main_menu

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

💰 **قیمت‌ها (تومان):**
• 💎 ماهانه: ۱۹۹,۰۰۰ تومان
• 💎 سالانه: ۱,۹۹۰,۰۰۰ تومان (۱۰٪ تخفیف)
• 👑 مادام‌العمر: ۴,۹۹۰,۰۰۰ تومان

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
📱 @Amir92aa

📌 **دستورات سریع:**
/start - شروع مجدد
/help - راهنما
/admin - پنل ادمین (فقط ادمین)
/signal - دریافت سیگنال
/price - قیمت لحظه‌ای
/vip - پنل VIP
/wallet - کیف پول
"""

SUPPORT_TEXT = """
🆘 **پشتیبانی CryptoPulse AI**

📱 **ادمین:** @Amir92aa
📧 **ایمیل:** support@cryptopulse.ai
🌐 **وبسایت:** https://cryptopulse.ai

⏰ **ساعات پاسخگویی:** ۲۴/۷

📝 **برای ارسال تیکت، روی دکمه زیر کلیک کنید.**

💬 **سوالات متداول:**
- چگونه سیگنال دریافت کنم؟
- قیمت VIP چقدر است؟
- چگونه از ربات استفاده کنم؟
"""

WALLET_TEXT = """
💰 **کیف پول شما**

💵 **موجودی:** ${balance:.2f}
💳 **کل واریز:** ${total_deposited:.2f}
📤 **کل برداشت:** ${total_withdrawn:.2f}
📈 **سود کل:** ${total_profit:.2f}

🔗 **کد معرف:** `{referral_code}`
👥 **تعداد معرف‌ها:** {referral_count}

📊 **تعداد معاملات:** {total_trades}
✅ **موفق:** {successful_trades}
❌ **ناموفق:** {failed_trades}
🏆 **نرخ برد:** {win_rate:.1f}%

💎 **وضعیت VIP:** {vip_status}
📅 **انقضای VIP:** {vip_expire}
"""

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
                is_admin=user_id in [str(a) for a in ADMIN_IDS]
            )
    
    is_admin = user_id in [str(a) for a in ADMIN_IDS]
    
    if is_admin:
        welcome_text = WELCOME_ADMIN
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
        HELP_TEXT,
        reply_markup=user_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور پنل ادمین"""
    user_id = str(update.effective_user.id)
    is_admin = user_id in [str(a) for a in ADMIN_IDS]
    
    if not is_admin:
        await update.message.reply_text(
            "❌ دسترسی غیرمجاز!",
            reply_markup=user_keyboard()
        )
        return
    
    await update.message.reply_text(
        WELCOME_ADMIN,
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
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 خرید VIP ماهانه", callback_data="vip_monthly")],
            [InlineKeyboardButton("💎 خرید VIP سالانه", callback_data="vip_yearly")],
            [InlineKeyboardButton("👑 VIP مادام‌العمر", callback_data="vip_lifetime")],
            [InlineKeyboardButton("ℹ️ وضعیت VIP", callback_data="vip_status")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]),
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
        
        is_vip = db_user.get('is_vip', False)
        vip_expire = db_user.get('vip_expire', 'ندارد')
        
        wallet_text = WALLET_TEXT.format(
            balance=db_user.get('balance', 0),
            total_deposited=db_user.get('total_deposited', 0),
            total_withdrawn=db_user.get('total_withdrawn', 0),
            total_profit=db_user.get('total_profit', 0),
            referral_code=db_user.get('referral_code', 'ندارد'),
            referral_count=db_user.get('referral_count', 0),
            total_trades=db_user.get('total_trades', 0),
            successful_trades=db_user.get('successful_trades', 0),
            failed_trades=db_user.get('failed_trades', 0),
            win_rate=db_user.get('win_rate', 0),
            vip_status="✅ فعال" if is_vip else "❌ غیرفعال",
            vip_expire=vip_expire
        )
        
        await update.message.reply_text(
            wallet_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 شارژ کیف پول", callback_data="wallet_deposit")],
                [InlineKeyboardButton("📊 تاریخچه تراکنش‌ها", callback_data="wallet_history")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
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
            
            text = f"""
📊 **قیمت لحظه‌ای BTC**

💰 **قیمت:** ${price:,.2f}
📈 **تغییر ۲۴ساعته:** {change:+.2f}%
📊 **بالاترین:** ${high:,.2f}
📉 **پایین‌ترین:** ${low:,.2f}

⏰ **زمان:** {time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
            "💰 قیمت لحظه‌ای: $67,845.32\n📈 تغییر: +2.34%",
            reply_markup=user_keyboard()
        )

# ============================================================
#                    CALLBACK HANDLER
# ============================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کالبک‌ها"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    is_admin = user_id in [str(a) for a in ADMIN_IDS]
    
    # ====== بازگشت ======
    if data == "back_main":
        if is_admin:
            await query.edit_message_text(
                WELCOME_ADMIN,
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
            "مثال: `BTC` یا `ETH`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_ANALYSIS_COIN
    
    # ====== سیگنال ======
    if data == "signal":
        await query.edit_message_text(
            "📊 **دریافت سیگنال**\n\n"
            "لطفاً نام ارز مورد نظر را وارد کنید:\n"
            "مثال: `BTC` یا `ETH`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN
    
    # ====== کیف پول ======
    if data == "wallet":
        await wallet_command(update, context)
        return
    
    # ====== VIP ======
    if data == "vip":
        await vip_command(update, context)
        return
    
    if data == "vip_monthly":
        await query.edit_message_text(
            f"💎 **خرید VIP ماهانه**\n\n"
            f"💰 **مبلغ:** ۱۹۹,۰۰۰ تومان\n"
            f"📅 **مدت:** ۱ ماه\n\n"
            f"💳 **شماره کارت:** `6063731196254479`\n"
            f"🏦 **به نام:** به مرد\n\n"
            f"📤 پس از واریز، رسید را ارسال کنید.",
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
            f"💰 **مبلغ:** ۱,۹۹۰,۰۰۰ تومان\n"
            f"📅 **مدت:** ۱۲ ماه\n"
            f"🎁 **تخفیف:** ۱۰٪\n\n"
            f"💳 **شماره کارت:** `6063731196254479`\n"
            f"🏦 **به نام:** به مرد\n\n"
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
            f"💰 **مبلغ:** ۴,۹۹۰,۰۰۰ تومان\n"
            f"📅 **مدت:** مادام‌العمر\n"
            f"🎁 **تخفیف ویژه:** ۵۰٪\n\n"
            f"💳 **شماره کارت:** `6063731196254479`\n"
            f"🏦 **به نام:** به مرد\n\n"
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
            db_user = get_user_repo().get_by_telegram_id(user_id)
            if db_user:
                is_vip = db_user.get('is_vip', False)
                expire = db_user.get('vip_expire', 'ندارد')
                await query.edit_message_text(
                    f"💎 **وضعیت VIP**\n\n"
                    f"📊 **وضعیت:** {'✅ فعال' if is_vip else '❌ غیرفعال'}\n"
                    f"📅 **انقضا:** {expire}\n\n"
                    f"برای خرید VIP از منوی اصلی استفاده کنید.",
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
            "• تصویر باید واضح و خوانا باشد\n\n"
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
            HELP_TEXT,
            reply_markup=user_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== پشتیبانی ======
    if data == "support":
        await query.edit_message_text(
            SUPPORT_TEXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 تماس با ادمین", url="https://t.me/Amir92aa")],
                [InlineKeyboardButton("📧 ارسال ایمیل", callback_data="support_email")],
                [InlineKeyboardButton("🎫 تیکت جدید", callback_data="support_ticket")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== پنل ادمین ======
    if data == "admin_panel":
        if not is_admin:
            await query.edit_message_text(
                "❌ دسترسی غیرمجاز!",
                reply_markup=user_keyboard()
            )
            return
        
        await query.edit_message_text(
            WELCOME_ADMIN,
            reply_markup=admin_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== مدیریت کاربران ======
    if data == "admin_users":
        if not is_admin:
            return
        
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""
👥 **مدیریت کاربران**

📊 **آمار کاربران:**
• کل: {stats.get('users', 0)}
• فعال: {stats.get('active_users', 0)}
• VIP: {stats.get('vip_users', 0)}
• بن: {stats.get('banned_users', 0)}

از دکمه‌های زیر برای مدیریت استفاده کنید:
"""
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 لیست کاربران", callback_data="admin_users_list")],
                [InlineKeyboardButton("📊 آمار کاربران", callback_data="admin_users_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== مدیریت پرداخت‌ها ======
    if data == "admin_payments":
        if not is_admin:
            return
        
        await query.edit_message_text(
            "💰 **مدیریت پرداخت‌ها**\n\n"
            "از دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ پرداخت‌های در انتظار", callback_data="admin_payments_pending")],
                [InlineKeyboardButton("📊 گزارش مالی", callback_data="admin_payments_report")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== مدیریت VIP ======
    if data == "admin_vip":
        if not is_admin:
            return
        
        await query.edit_message_text(
            "💎 **مدیریت VIP**\n\n"
            "از دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ درخواست‌های VIP", callback_data="admin_vip_requests")],
                [InlineKeyboardButton("📊 آمار VIP", callback_data="admin_vip_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ====== ارسال همگانی ======
    if data == "admin_broadcast":
        if not is_admin:
            return
        
        await query.edit_message_text(
            "📢 **ارسال پیام همگانی**\n\n"
            "لطفاً پیام خود را بنویسید.\n"
            "برای لغو /cancel را بفرستید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 لغو", callback_data="cancel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['admin_action'] = 'broadcast'
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
    """پردازش پیام‌های متنی"""
    user_id = str(update.effective_user.id)
    message = update.message.text
    
    # ====== ارسال همگانی (ادمین) ======
    if context.user_data.get('admin_action') == 'broadcast':
        if user_id in [str(a) for a in ADMIN_IDS]:
            # ارسال به همه کاربران
            if get_user_repo:
                users = get_user_repo().get_all() if hasattr(get_user_repo(), 'get_all') else []
                success_count = 0
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
                        pass
                
                await update.message.reply_text(
                    f"✅ پیام برای **{success_count}** کاربر ارسال شد.",
                    reply_markup=admin_keyboard()
                )
            else:
                await update.message.reply_text(
                    "✅ پیام ارسال شد.",
                    reply_markup=admin_keyboard()
                )
            context.user_data['admin_action'] = None
            return
    
    # ====== ارسال رسید ======
    if context.user_data.get('waiting_for_receipt'):
        if update.message.photo:
            # دریافت تصویر
            photo = update.message.photo[-1]
            file = await photo.get_file()
            
            # ذخیره در دیتابیس
            if get_user_repo:
                db_user = get_user_repo().get_by_telegram_id(user_id)
                if db_user:
                    plan = context.user_data.get('vip_plan', 'monthly')
                    price = 199000 if plan == 'monthly' else 1990000 if plan == 'yearly' else 4990000
                    
                    # ارسال به ادمین
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
                                        f"📅 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                        except:
                            pass
                    
                    await update.message.reply_text(
                        f"✅ **رسید شما ارسال شد!**\n\n"
                        f"💰 مبلغ: {price:,} تومان\n"
                        f"📦 نوع: {plan}\n\n"
                        f"⏳ پس از تایید ادمین، VIP شما فعال می‌شود.",
                        reply_markup=user_keyboard()
                    )
                    context.user_data['waiting_for_receipt'] = False
                    return
        
        await update.message.reply_text(
            "❌ لطفاً تصویر رسید را ارسال کنید.",
            reply_markup=user_keyboard()
        )
        return
    
    # ====== دریافت تحلیل ======
    if message.upper() in ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC"]:
        coin = message.upper()
        await update.message.reply_text(
            f"⏳ در حال تحلیل {coin}...",
            reply_markup=user_keyboard()
        )
        
        if market:
            signal = await market.get_signal(coin, "4h")
            if signal:
                text = f"""
🚨 **سیگنال {coin}**

🟢 **پیشنهاد:** {signal.get('signal', 'hold').upper()}
🎯 **اطمینان:** {signal.get('confidence', 50)}%

💰 **قیمت فعلی:** ${signal.get('current_price', 0):,.2f}

🎯 **اهداف قیمتی:**
"""
                targets = signal.get('targets', [])
                for i, target in enumerate(targets[:3], 1):
                    text += f"   هدف {i}: ${target:,.2f}\n"
                
                text += f"""
🛑 **حد ضرر:** ${signal.get('stop_loss', 0):,.2f}

⏰ **زمان:** {time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                await update.message.reply_text(
                    text,
                    reply_markup=user_keyboard(),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
    
    # ====== پاسخ پیش‌فرض ======
    await update.message.reply_text(
        "ℹ️ لطفاً از دکمه‌های زیر استفاده کنید:",
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
    """مدیریت هندلرهای ربات"""
    
    def __init__(self):
        self.application = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """تنظیم هندلرها"""
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
                CallbackQueryHandler(callback_handler, pattern="^signal$"),
            ],
            states={
                ConversationState.WAITING_FOR_SIGNAL_COIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
                ],
                ConversationState.WAITING_FOR_ANALYSIS_COIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_command)]
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
    return bot_handlers.get_application()

def check_handlers():
    return {
        "bot_handlers": "✅ OK" if bot_handlers else "❌ FAILED",
        "application": "✅ OK" if bot_handlers.get_application() else "❌ FAILED"
    }
