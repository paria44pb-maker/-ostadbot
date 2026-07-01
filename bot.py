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
║  CryptoPulse AI Bot v3.0 - Ultimate Edition                      ║
║  ───────────────────────────────────────────────────────────       ║
║  🤖 هوش مصنوعی Groq  |  📊 تحلیل تکنیکال  |  💰 صرافی CoinEx   ║
║  👑 پنل ادمین کامل  |  💎 مدیریت VIP  |  📡 کانال تلگرام        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import asyncio
import time
import uvicorn
import signal
import json
import aiohttp
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List

# ============================================================
#                    [بخش ۱] تنظیمات و متغیرهای محیطی
# ============================================================

print("\n" + "="*60)
print("🚀 CryptoPulse AI Bot v3.0 - راه‌اندازی")
print("📁 بارگذاری ۱۵ بخش...\n")
print("="*60 + "\n")

# متغیرهای محیطی
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = []
for x in os.environ.get("ADMIN_IDS", "").split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except:
            pass

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
COINEX_API_KEY = os.environ.get("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.environ.get("COINEX_SECRET_KEY", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "به مرد")
PORT = int(os.environ.get("PORT", 8080))

print("📊 بررسی متغیرهای محیطی:")
print(f"  ✅ BOT_TOKEN: {'تنظیم شده ✅' if BOT_TOKEN else 'تنظیم نشده ❌'}")
print(f"  ✅ ADMIN_IDS: {ADMIN_IDS}")
print(f"  ✅ GROQ_API_KEY: {'تنظیم شده ✅' if GROQ_API_KEY else 'تنظیم نشده ❌'}")
print(f"  ✅ COINEX_API_KEY: {'تنظیم شده ✅' if COINEX_API_KEY else 'تنظیم نشده ❌'}")
print()

# ============================================================
#                    [بخش ۲] ایموجی‌ها و ثابت‌ها
# ============================================================

class Emoji:
    MAIN = "🏠"
    ADMIN = "👑"
    VIP = "💎"
    USER = "👤"
    WALLET = "💰"
    SIGNAL = "🚨"
    ANALYSIS = "📊"
    CHART = "📈"
    SETTINGS = "⚙️"
    SUPPORT = "🆘"
    HELP = "📖"
    COIN = "🪙"
    FIRE = "🔥"
    STAR = "⭐"
    ROCKET = "🚀"
    LIGHTNING = "⚡"
    SHIELD = "🛡️"
    TROPHY = "🏆"
    CROWN = "👑"
    DIAMOND = "💎"
    MONEY = "💵"
    CREDIT_CARD = "💳"
    BANK = "🏦"
    BACK = "🔙"
    NEXT = "➡️"
    CHECK = "✅"
    CROSS = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    BUY = "🟢"
    SELL = "🔴"
    HOLD = "🟡"
    LOADING = "⏳"
    SUCCESS = "✅"
    ERROR = "❌"
    GRAPH = "📉"
    CANDLE = "🕯️"
    BELL = "🔔"
    LOCK = "🔒"
    UNLOCK = "🔓"
    KEY = "🔑"
    PHONE = "📱"
    COMPUTER = "💻"
    GLOBE = "🌍"
    FLAG = "🏁"

print("  ✅ بخش ۲: ایموجی‌ها بارگذاری شدند")

# ============================================================
#                    [بخش ۳] زمان تهران
# ============================================================

class TehranTime:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def now(self):
        import pytz
        tehran = pytz.timezone('Asia/Tehran')
        return datetime.now(tehran)
    
    def now_persian(self):
        dt = self.now()
        return dt.strftime("%Y-%m-%d %H:%M:%S")

tehran_time = TehranTime()
print("  ✅ بخش ۳: زمان تهران بارگذاری شد")

# ============================================================
#                    [بخش ۴] ابزارها و توابع کمکی
# ============================================================

def get_time():
    return tehran_time.now_persian()

def is_admin(user_id):
    try:
        return int(user_id) in ADMIN_IDS
    except:
        return False

def get_emoji(signal_type):
    emojis = {"buy": "🟢", "sell": "🔴", "hold": "🟡", "strong_buy": "💚", "strong_sell": "❤️"}
    return emojis.get(signal_type, "⚪")

def format_price(price):
    return f"${price:,.2f}"

def format_number(num):
    return f"{num:,.0f}"

print("  ✅ بخش ۴: ابزارها بارگذاری شدند")

# ============================================================
#                    [بخش ۵] دیتابیس ساده
# ============================================================

class Database:
    def __init__(self):
        self.users = {}
        self.signals = []
        self.payments = []
    
    def get_user(self, user_id):
        return self.users.get(str(user_id))
    
    def save_user(self, user_id, data):
        self.users[str(user_id)] = data
    
    def get_stats(self):
        return {
            'users': len(self.users),
            'signals': len(self.signals),
            'payments': len(self.payments)
        }

db = Database()
print("  ✅ بخش ۵: دیتابیس بارگذاری شد")

# ============================================================
#                    [بخش ۶] صرافی CoinEx
# ============================================================

async def get_coinex_price(symbol="BTC"):
    try:
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
    except Exception as e:
        print(f"CoinEx error: {e}")
    return None

print("  ✅ بخش ۶: صرافی CoinEx بارگذاری شد")

# ============================================================
#                    [بخش ۷] هوش مصنوعی Groq
# ============================================================

async def get_groq_analysis(coin, price_data):
    if not GROQ_API_KEY:
        return "⚠️ کلید API Groq تنظیم نشده است."
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
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
    except Exception as e:
        print(f"Groq error: {e}")
        return "⚠️ خطا در ارتباط با Groq."

print("  ✅ بخش ۷: هوش مصنوعی Groq بارگذاری شد")

# ============================================================
#                    [بخش ۸] تحلیل تکنیکال
# ============================================================

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

print("  ✅ بخش ۸: تحلیل تکنیکال بارگذاری شد")

# ============================================================
#                    [بخش ۹] کیبوردها و منوها
# ============================================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def user_keyboard():
    keyboard = [
        [InlineKeyboardButton(f"{Emoji.ANALYSIS} تحلیل لحظه‌ای", callback_data="analysis")],
        [InlineKeyboardButton(f"{Emoji.SIGNAL} سیگنال خرید", callback_data="signal_buy"),
         InlineKeyboardButton(f"{Emoji.CHART} سیگنال فروش", callback_data="signal_sell")],
        [InlineKeyboardButton(f"{Emoji.WALLET} کیف پول", callback_data="wallet"),
         InlineKeyboardButton(f"{Emoji.VIP} VIP", callback_data="vip")],
        [InlineKeyboardButton("📡 سیگنال‌ها", callback_data="signals_menu")],
        [InlineKeyboardButton(f"{Emoji.HELP} راهنما", callback_data="help"),
         InlineKeyboardButton(f"{Emoji.SUPPORT} پشتیبانی", callback_data="support")],
        [InlineKeyboardButton(f"{Emoji.SETTINGS} تنظیمات", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
        [InlineKeyboardButton("💎 مدیریت VIP", callback_data="admin_vip")],
        [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📡 ارسال به کانال", callback_data="admin_send_channel")],
        [InlineKeyboardButton("🔧 مدیریت API", callback_data="admin_api")],
        [InlineKeyboardButton("💾 بکاپ و بازیابی", callback_data="admin_backup")],
        [InlineKeyboardButton("🚪 خروج / مدیریت سرور", callback_data="admin_exit")],
        [InlineKeyboardButton(f"{Emoji.BACK} بازگشت به منو", callback_data="back_main")]
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
        [InlineKeyboardButton(f"{Emoji.BACK} بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

print("  ✅ بخش ۹: کیبوردها بارگذاری شدند")

# ============================================================
#                    [بخش ۱۰] متون و پیام‌ها
# ============================================================

WELCOME_USER = f"""
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

WELCOME_ADMIN = f"""
👑 **به CryptoPulse AI خوش آمدید!**

**سازنده عزیز، پنل مدیریت و تنظیمات ربات**

---

### به CryptoPulse AI خوش آمدید!
دستیار هوشمند تحلیل و سیگنال ارزهای دیجیتال

ما با استفاده از پیشرفته‌ترین هوش مصنوعی و تحلیل تکنیکال،  
به شما در تصمیم‌گیری‌های بهتر و پرسودتر کمک می‌کنیم.

---

**همراها شما در مسیر سودآوری**

---

📊 **آمار کلی:**
👥 کاربران: {db.get_stats()['users']}
💎 VIP: ۰
🚨 سیگنال‌ها: {db.get_stats()['signals']}
💰 درآمد: $۰

⏰ زمان: {get_time()}
"""

VIP_TEXT = f"""
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

HELP_TEXT = f"""
📖 **راهنمای ربات CryptoPulse AI**

**🔹 شروع کار:**
با دکمه‌های منوی اصلی از امکانات استفاده کنید.

**🔹 تحلیل و سیگنال:**
ربات با استفاده از AI و تحلیل تکنیکال، سیگنال‌های دقیق ارائه می‌دهد.

**🔹 VIP:**
با خرید VIP به امکانات ویژه دسترسی پیدا کنید.
💰 قیمت: ۱۹۹,۰۰۰ تومان ماهانه

**🔹 پشتیبانی:**
📱 @{SUPPORT_USERNAME}

📌 **دستورات سریع:**
/start - شروع
/help - راهنما
/admin - پنل ادمین
/price - قیمت
/analysis - تحلیل
/vip - VIP
/cancel - لغو
"""

print("  ✅ بخش ۱۰: متون بارگذاری شدند")

# ============================================================
#                    [بخش ۱۱] FASTAPI SERVER
# ============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(
    title="CryptoPulse AI",
    description="ربات هوشمند تحلیل و سیگنال ارزهای دیجیتال",
    version="3.0.0"
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "name": "CryptoPulse AI",
        "version": "3.0.0",
        "channel": CHANNEL_ID,
        "time": get_time(),
        "environment": "production"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "uptime": "0d 0h 0m",
        "version": "3.0.0",
        "time": get_time()
    }

@app.get("/api/v1/price/{coin}")
async def get_price(coin: str):
    data = await get_coinex_price(coin.upper())
    if data:
        return {
            "coin": coin.upper(),
            "price": data['price'],
            "change_24h": data['change'],
            "high_24h": data['high'],
            "low_24h": data['low'],
            "volume_24h": data['volume'],
            "time": get_time()
        }
    return {"error": "Price not available"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        return {"status": "ok"}
    except:
        return JSONResponse(status_code=400, content={"status": "error"})

print("  ✅ بخش ۱۱: سرور FastAPI بارگذاری شد")

# ============================================================
#                    [بخش ۱۲] هندلرهای تلگرام
# ============================================================

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram.constants import ParseMode

# وضعیت‌های گفتگو
WAITING_FOR_COIN = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    is_admin_flag = is_admin(user_id)
    
    if is_admin_flag:
        text = WELCOME_ADMIN
        keyboard = admin_keyboard()
    else:
        text = WELCOME_USER
        keyboard = user_keyboard()
    
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not is_admin(user_id):
        await update.message.reply_text(f"{Emoji.ERROR} دسترسی غیرمجاز!", reply_markup=user_keyboard())
        return
    
    await update.message.reply_text(
        WELCOME_ADMIN,
        reply_markup=admin_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_TEXT,
        reply_markup=user_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{Emoji.LOADING} در حال دریافت قیمت...", reply_markup=user_keyboard())
    
    data = await get_coinex_price("BTC")
    if data:
        text = f"""
📊 **قیمت لحظه‌ای BTC**

💰 **قیمت:** {format_price(data['price'])}
📈 **تغییر ۲۴ساعته:** {data['change']:+.2f}%
📊 **بالاترین:** {format_price(data['high'])}
📉 **پایین‌ترین:** {format_price(data['low'])}
📊 **حجم:** {format_number(data['volume'])}

⏰ **زمان:** {get_time()}
"""
        await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(f"{Emoji.ERROR} خطا در دریافت قیمت!", reply_markup=user_keyboard())

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{Emoji.LOADING} در حال دریافت تحلیل...", reply_markup=user_keyboard())
    
    price_data = await get_coinex_price("BTC")
    if price_data:
        analysis = await get_groq_analysis("BTC", price_data)
        text = f"""
📊 **تحلیل تکنیکال BTC**

🤖 **تحلیل هوش مصنوعی:**

{analysis}

💰 **قیمت فعلی:** {format_price(price_data['price'])}
📈 **تغییر ۲۴ساعته:** {price_data['change']:+.2f}%

⏰ **زمان:** {get_time()}
"""
        await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(f"{Emoji.ERROR} خطا در دریافت داده!", reply_markup=user_keyboard())

async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""
💰 **کیف پول شما**

💵 موجودی: $0.00
💳 کل واریز: $0.00
📤 کل برداشت: $0.00

🔗 کد معرف: `ABC123`
👥 تعداد معرف‌ها: 0

💎 VIP: ❌ غیرفعال
📅 انقضا: ندارد
"""
    await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(f"{Emoji.SUCCESS} عملیات لغو شد.", reply_markup=user_keyboard())
    return ConversationHandler.END

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 **دریافت سیگنال**\n\nلطفاً نام ارز را وارد کنید:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
        parse_mode=ParseMode.MARKDOWN
    )
    return WAITING_FOR_COIN

async def signal_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = update.message.text.upper()
    if coin == "❌ لغو":
        await update.message.reply_text(f"{Emoji.SUCCESS} لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END
    
    await update.message.reply_text(f"{Emoji.LOADING} در حال دریافت سیگنال {coin}...", reply_markup=user_keyboard())
    
    price_data = await get_coinex_price(coin)
    if price_data:
        signal_type = "buy" if price_data['change'] > 0 else "sell" if price_data['change'] < 0 else "hold"
        confidence = min(80, 50 + abs(price_data['change']) * 5)
        
        text = f"""
🚨 **سیگنال {coin}**

{get_emoji(signal_type)} **پیشنهاد:** {signal_type.upper()}
🎯 **اطمینان:** {confidence:.0f}%

💰 **قیمت فعلی:** {format_price(price_data['price'])}
📈 **تغییر ۲۴ساعته:** {price_data['change']:+.2f}%

🛑 **حد ضرر پیشنهادی:** {format_price(price_data['price'] * 0.97)}
🎯 **هدف اول:** {format_price(price_data['price'] * 1.02)}

⏰ **زمان:** {get_time()}
"""
        await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(f"{Emoji.ERROR} خطا در دریافت سیگنال!", reply_markup=user_keyboard())
    
    return ConversationHandler.END

print("  ✅ بخش ۱۲: هندلرها بارگذاری شدند")

# ============================================================
#                    [بخش ۱۳] CALLBACK HANDLER
# ============================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    is_admin_flag = is_admin(user_id)
    
    # بازگشت به منو
    if data == "back_main":
        if is_admin_flag:
            text = WELCOME_ADMIN
            keyboard = admin_keyboard()
        else:
            text = WELCOME_USER
            keyboard = user_keyboard()
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        return
    
    # لغو
    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text(f"{Emoji.SUCCESS} لغو شد.", reply_markup=user_keyboard())
        return
    
    # تحلیل
    if data == "analysis":
        await query.edit_message_text(f"{Emoji.LOADING} در حال دریافت تحلیل...", reply_markup=user_keyboard())
        price_data = await get_coinex_price("BTC")
        if price_data:
            analysis = await get_groq_analysis("BTC", price_data)
            text = f"""
📊 **تحلیل تکنیکال BTC**

🤖 **تحلیل هوش مصنوعی:**

{analysis}

💰 **قیمت فعلی:** {format_price(price_data['price'])}
📈 **تغییر ۲۴ساعته:** {price_data['change']:+.2f}%

⏰ **زمان:** {get_time()}
"""
            await query.edit_message_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        else:
            await query.edit_message_text(f"{Emoji.ERROR} خطا در دریافت داده!", reply_markup=user_keyboard())
        return
    
    # قیمت
    if data == "price":
        await query.edit_message_text(f"{Emoji.LOADING} در حال دریافت قیمت...", reply_markup=user_keyboard())
        data = await get_coinex_price("BTC")
        if data:
            text = f"""
📊 **قیمت لحظه‌ای BTC**

💰 **قیمت:** {format_price(data['price'])}
📈 **تغییر ۲۴ساعته:** {data['change']:+.2f}%
⏰ **زمان:** {get_time()}
"""
            await query.edit_message_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        else:
            await query.edit_message_text(f"{Emoji.ERROR} خطا در دریافت قیمت!", reply_markup=user_keyboard())
        return
    
    # VIP
    if data == "vip":
        await query.edit_message_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # راهنما
    if data == "help":
        await query.edit_message_text(HELP_TEXT, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # پشتیبانی
    if data == "support":
        await query.edit_message_text(f"""
🆘 **پشتیبانی CryptoPulse AI**

📱 **ادمین:** @{SUPPORT_USERNAME}
📧 **ایمیل:** support@cryptopulse.ai
🌐 **وبسایت:** https://cryptopulse.ai

⏰ **ساعات پاسخگویی:** ۲۴/۷
""", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]), parse_mode=ParseMode.MARKDOWN)
        return
    
    # تنظیمات
    if data == "settings":
        await query.edit_message_text("⚙️ **تنظیمات**\n\nدر حال توسعه...", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # پنل ادمین
    if data == "admin_panel":
        if not is_admin_flag:
            await query.edit_message_text(f"{Emoji.ERROR} دسترسی غیرمجاز!", reply_markup=user_keyboard())
            return
        await query.edit_message_text(WELCOME_ADMIN, reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # مدیریت کاربران
    if data == "admin_users":
        await query.edit_message_text("👥 **مدیریت کاربران**\n\nدر حال توسعه...", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # مدیریت پرداخت‌ها
    if data == "admin_payments":
        await query.edit_message_text("💰 **مدیریت پرداخت‌ها**\n\nدر حال توسعه...", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # مدیریت VIP
    if data == "admin_vip":
        await query.edit_message_text("💎 **مدیریت VIP**\n\nدر حال توسعه...", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ارسال همگانی
    if data == "admin_broadcast":
        await query.edit_message_text("📢 **ارسال همگانی**\n\nدر حال توسعه...", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # سیگنال‌ها منو
    if data == "signals_menu":
        await query.edit_message_text("📡 **منوی سیگنال‌ها**\n\nاز دکمه‌های زیر استفاده کنید:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 دریافت تحلیل", callback_data="analysis")],
            [InlineKeyboardButton("👤 حساب کاربری", callback_data="wallet")],
            [InlineKeyboardButton("📖 راهنما", callback_data="help")],
            [InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("💎 پنل VIP", callback_data="vip")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    # کیف پول
    if data == "wallet":
        text = f"""
💰 **کیف پول شما**

💵 موجودی: $0.00
💳 کل واریز: $0.00
📤 کل برداشت: $0.00

🔗 کد معرف: `ABC123`
👥 تعداد معرف‌ها: 0

💎 VIP: ❌ غیرفعال
📅 انقضا: ندارد
"""
        await query.edit_message_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # سیگنال خرید/فروش
    if data in ["signal_buy", "signal_sell"]:
        signal_type = "خرید" if "buy" in data else "فروش"
        await query.edit_message_text(
            f"📊 **سیگنال {signal_type}**\n\nلطفاً نام ارز را وارد کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_FOR_COIN
    
    # پاسخ پیش‌فرض
    await query.edit_message_text(f"{Emoji.INFO} گزینه مورد نظر در حال توسعه است...", reply_markup=user_keyboard())

print("  ✅ بخش ۱۳: Callback Handler بارگذاری شد")

# ============================================================
#                    [بخش ۱۴] Message & Photo Handlers
# ============================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message = update.message.text
    
    # ارسال رسید
    if context.user_data.get('waiting_for_receipt'):
        if update.message.photo:
            await update.message.reply_text(f"{Emoji.SUCCESS} رسید شما ارسال شد!", reply_markup=user_keyboard())
            context.user_data['waiting_for_receipt'] = False
            return
        await update.message.reply_text("❌ لطفاً تصویر ارسال کنید.", reply_markup=user_keyboard())
        return
    
    # پاسخ پیش‌فرض
    await update.message.reply_text(
        f"{Emoji.INFO} لطفاً از دکمه‌های زیر استفاده کنید:",
        reply_markup=user_keyboard()
    )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_receipt'):
        await message_handler(update, context)
    else:
        await update.message.reply_text("📸 تصویر دریافت شد!", reply_markup=user_keyboard())

print("  ✅ بخش ۱۴: Message Handler بارگذاری شد")

# ============================================================
#                    [بخش ۱۵] کلاس اصلی و اجرا
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
                WAITING_FOR_COIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
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

print("  ✅ بخش ۱۵: کلاس اصلی بارگذاری شد")

# ============================================================
#                    اجرا
# ============================================================

bot_handlers = BotHandlers()

async def run_bot():
    if not BOT_TOKEN:
        print(f"{Emoji.ERROR} BOT_TOKEN تنظیم نشده است!")
        return
    
    app = bot_handlers.get_application()
    if app:
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        print(f"\n{Emoji.SUCCESS} Telegram Bot با موفقیت اجرا شد!")
        print(f"{Emoji.INFO} ربات: @{os.environ.get('BOT_USERNAME', 'Aradarzz_bot')}")
        print(f"{Emoji.GLOBE} سرور: http://0.0.0.0:{PORT}")

async def main():
    # اجرای ربات
    bot_task = asyncio.create_task(run_bot())
    
    # اجرای سرور
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    print("\n" + "="*60)
    print(f"{Emoji.ROCKET} CryptoPulse AI Bot v3.0 - آماده اجرا")
    print("="*60 + "\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Emoji.WARNING} ربات متوقف شد")
    except Exception as e:
        print(f"{Emoji.ERROR} خطا: {e}")
        while True:
            time.sleep(1)
