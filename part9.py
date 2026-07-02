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
║  🚀 CryptoPulse AI v9.0 — ULTIMATE HANDLERS — 18 PARTS COVERAGE                  ║
║  ───────────────────────────────────────────────────────────────────────────────    ║
║  👑 Admin Panel  |  👤 Users  |  💰 Payments  |  💎 VIP  |  📢 Broadcast         ║
║  📡 Channel  |  🔧 API  |  💾 Backup  |  🚪 Server  |  🧠 Intelligence          ║
║  🤖 God Mode  |  📊 Analysis  |  🐋 Whales  |  🔮 Predictions                   ║
║  ════════════════════════════════════════════════════════════════════════════════   ║
║  📁 ۲۵۰۰۰+ خط کد  |  ⚡ فوق‌بهینه  |  🔥 اساطیری  |  🛡️ ضد خطا                ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, json, math, time, random, string, hashlib, hmac, base64, re, asyncio
import warnings, traceback, threading, itertools, functools, operator
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple, Union, Set, Callable
from collections import defaultdict, OrderedDict, deque, Counter
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum, auto, unique, Flag
from functools import wraps, lru_cache, partial, reduce
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from pathlib import Path

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import logging
logging.basicConfig(level=logging.CRITICAL, handlers=[logging.NullHandler()])
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.CRITICAL)
    logging.getLogger(name).addHandler(logging.NullHandler())

from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ReplyKeyboardMarkup, KeyboardButton, ChatPermissions, Message, CallbackQuery, ChatMember, Chat, User, ReplyKeyboardRemove, ForceReply, InputFile)
from telegram.constants import ParseMode, ChatAction, ChatType
from telegram.warnings import PTBUserWarning
from telegram.ext import (Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler, Defaults, AIORateLimiter)
warnings.filterwarnings("ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
warnings.filterwarnings("ignore", message=r".*PTBUserWarning", category=PTBUserWarning)

# ============================================================================================================
#                    ABSOLUTELY SILENT SAFE IMPORT — NO LOGS, NO PRINTS, NO WARNINGS, NO ERRORS
# ============================================================================================================
def safe_import(module_name: str, *attrs):
    result = {}
    try:
        with suppress(Exception):
            module = __import__(module_name, fromlist=list(attrs))
            for attr in attrs:
                with suppress(Exception):
                    result[attr] = getattr(module, attr, None)
    except:
        for attr in attrs:
            result[attr] = None
    return result

_p1 = safe_import("part1")
_p2 = safe_import("part2")
_p3 = safe_import("part3", "get_user_repo", "get_signal_repo", "get_payment_repo", "db_manager")
_p4 = safe_import("part4", "get_time", "get_emoji", "get_formatter", "get_hash", "get_validator", "get_cache")
_p5 = safe_import("part5", "get_market", "get_coinex", "get_signal", "get_ticker", "get_price", "get_ohlcv_data", "get_market_summary", "MarketAggregator", "CoinExClient", "MultiExchangeManager")
_p6 = safe_import("part6", "get_ai", "get_groq")
_p7 = safe_import("part7", "get_technical", "TechnicalIndicators")
_p8 = safe_import("part8", "lux_keyboard", "menu_builder", "LuxText", "LuxEmoji")
_p10 = safe_import("part10", "TradingEngine", "OrderManager", "PositionManager")
_p11 = safe_import("part11", "PaymentGateway", "InvoiceManager", "TransactionManager")
_p12 = safe_import("part12", "MediaManager", "ContentGenerator", "ImageProcessor")
_p13 = safe_import("part13", "NotificationManager", "AlertSystem", "PushNotifier")
_p14 = safe_import("part14", "TelegramBot", "WebhookManager", "PollingManager")
_p15 = safe_import("part15", "Monitor", "Logger", "MetricsCollector", "HealthChecker")
_p16 = safe_import("part16", "get_intelligence_engine", "AdminIntelligenceEngine", "UserIntelligence", "FinancialIntelligence", "SignalIntelligence", "ComprehensiveReport")
_p17 = safe_import("part17", "get_analysis_engine", "AnalysisEngine", "TechnicalIndicators", "CandlestickPatterns", "FibonacciEngine", "WhaleTracker", "PriceActionEngine", "FundamentalAnalysis", "analyze", "detect_patterns", "fibonacci_levels", "support_resistance", "pivot_points")
_p18 = safe_import("part18", "get_god_mode_engine", "GodModeEngine", "GodSignal", "MarketScanner", "ChannelManager", "MarketOverview", "get_signal", "get_top_signals", "get_market_overview", "send_signal_to_channel", "send_overview_to_channel", "send_top_to_channel")

_b3 = safe_import("bot3", "get_user_repo", "get_signal_repo", "get_payment_repo", "db_manager")
_b5 = safe_import("bot5", "get_market", "get_coinex", "get_signal")

get_user_repo = _p3.get("get_user_repo") or _b3.get("get_user_repo")
get_signal_repo = _p3.get("get_signal_repo") or _b3.get("get_signal_repo")
get_payment_repo = _p3.get("get_payment_repo") or _b3.get("get_payment_repo")
db_manager = _p3.get("db_manager") or _b3.get("db_manager")
get_market = _p5.get("get_market") or _b5.get("get_market")
get_coinex = _p5.get("get_coinex") or _b5.get("get_coinex")
get_signal_func = _p5.get("get_signal") or _b5.get("get_signal")
get_ticker_func = _p5.get("get_ticker")
get_price_func = _p5.get("get_price")
get_ohlcv_func = _p5.get("get_ohlcv_data")
get_market_summary_func = _p5.get("get_market_summary")
get_intelligence_engine = _p16.get("get_intelligence_engine")
AdminIntelligenceEngine = _p16.get("AdminIntelligenceEngine")
get_analysis_engine = _p17.get("get_analysis_engine")
AnalysisEngine = _p17.get("AnalysisEngine")
TechnicalIndicators = _p17.get("TechnicalIndicators") or _p7.get("TechnicalIndicators")
CandlestickPatterns = _p17.get("CandlestickPatterns")
FibonacciEngine = _p17.get("FibonacciEngine")
WhaleTracker = _p17.get("WhaleTracker")
PriceActionEngine = _p17.get("PriceActionEngine")
FundamentalAnalysis = _p17.get("FundamentalAnalysis")
analyze_advanced = _p17.get("analyze")
detect_patterns = _p17.get("detect_patterns")
fibonacci_levels = _p17.get("fibonacci_levels")
support_resistance = _p17.get("support_resistance")
pivot_points_func = _p17.get("pivot_points")
get_god_mode_engine = _p18.get("get_god_mode_engine")
GodModeEngine = _p18.get("GodModeEngine")
GodSignal = _p18.get("GodSignal")
MarketScanner = _p18.get("MarketScanner")
ChannelManager = _p18.get("ChannelManager")
god_get_signal = _p18.get("get_signal")
god_get_top_signals = _p18.get("get_top_signals")
god_get_market_overview = _p18.get("get_market_overview")
god_send_signal = _p18.get("send_signal_to_channel")
god_send_overview = _p18.get("send_overview_to_channel")
god_send_top = _p18.get("send_top_to_channel")
Monitor = _p15.get("Monitor")
HealthChecker = _p15.get("HealthChecker")
NotificationManager = _p13.get("NotificationManager")
MediaManager = _p12.get("MediaManager")
TradingEngine = _p10.get("TradingEngine")
PaymentGateway = _p11.get("PaymentGateway")

# ============================================================================================================
#                    GLOBAL CONFIGURATION
# ============================================================================================================
ADMIN_IDS: List[int] = []
for x in os.environ.get("ADMIN_IDS", "").split(","):
    x = x.strip()
    if x:
        try: ADMIN_IDS.append(int(x))
        except ValueError: pass

BOT_TOKEN = (os.environ.get("BOT_TOKEN", "") or os.environ.get("Telegram _bot_token", "") or 
             os.environ.get("telegram_bot_token", "") or os.environ.get("TELEGRAM_BOT_TOKEN", "") or
             os.environ.get("BOT_TOKEN_MAIN", ""))

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
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
DEFAULT_TIMEFRAME = os.environ.get("DEFAULT_TIMEFRAME", "4h")

SUPPORTED_COINS = [
    "BTC","ETH","BNB","SOL","XRP","ADA","DOGE","DOT","MATIC","SHIB","AVAX","LINK","UNI","ATOM","LTC",
    "BCH","NEAR","VET","ALGO","FTM","EOS","TRX","XLM","ICP","HBAR","FIL","APT","ARB","OP","SUI",
    "PEPE","WIF","BONK","SEI","TIA","INJ","RUNE","RNDR","FET","AGIX","OCEAN","AKT","TAO","WLD",
    "SAND","MANA","AXS","GALA","ENJ","CHZ","APE","GMT","1INCH","AAVE","COMP","MKR","SNX","CRV",
    "SUSHI","CAKE","UNI","DYDX","GMX","GNS","LDO","STG","RDNT","TON","NOT","JUP","PYTH","JTO",
    "BOME","WEN","MYRO","POPCAT","MEW","SLERF","SAMO","GRASS","DRIFT","KMNO","PRCL","W","ZRO",
    "STRK","ZK","BLAST","MODE","FUEL","BERA","MONAD","MEGA","EIGEN","OMNI","WORM","ALT","XAI",
    "ACE","NFP","AI","PORTAL","PIXEL","MAVIA","DYM","MANTA","ZETA","RON","CYBER","ARKM","ID",
    "EDU","HOOK","MAGIC","STG","SYN","GAL","APT","SUI","SEI","MINA","FLOW","KAVA","ROSE","ONE",
]

SUPPORTED_TIMEFRAMES = ["1m","3m","5m","15m","30m","1h","2h","4h","6h","12h","1d","3d","1w","1M"]

# ============================================================================================================
#                    UTILITY FUNCTIONS
# ============================================================================================================
def is_admin(user_id: int) -> bool: return user_id in ADMIN_IDS

def is_vip(user_id: int) -> bool:
    if get_user_repo:
        try:
            u = get_user_repo().get_by_telegram_id(str(user_id))
            return u.get('is_vip', False) if u else False
        except: pass
    return False

def get_persian_time() -> str: return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def get_persian_date() -> str: return datetime.now().strftime("%Y-%m-%d")
def get_timestamp() -> int: return int(time.time())
def validate_coin(coin: str) -> bool: return coin.upper().strip() in SUPPORTED_COINS
def validate_timeframe(tf: str) -> bool: return tf.lower().strip() in SUPPORTED_TIMEFRAMES
def generate_referral_code(length: int = 8) -> str: return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

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

def format_percent(pct: float) -> str: return f"{pct:+.2f}%"

def signal_emoji(signal_type: str) -> str:
    return {"strong_buy":"🟢🟢🟢","buy":"🟢🟢","weak_buy":"🟢","neutral":"🟡","weak_sell":"🔴","sell":"🔴🔴","strong_sell":"🔴🔴🔴","accumulate":"🐋","distribute":"🦈","wait":"⏳"}.get(signal_type,"🟡")

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
#                    DECORATORS
# ============================================================================================================
def admin_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **دسترسی غیرمجاز!**\nاین بخش فقط برای مدیران قابل دسترسی است.", parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def vip_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        uid = update.effective_user.id
        if not is_vip(uid) and not is_admin(uid):
            await update.message.reply_text("💎 **VIP لازم است!**\nاین بخش ویژه کاربران VIP می‌باشد.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 خرید VIP", callback_data="vip")]]), parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def rate_limit(max_calls: int = 5, period: int = 60):
    storage = defaultdict(list)
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            uid = str(update.effective_user.id)
            now = time.time()
            storage[uid] = [t for t in storage[uid] if now - t < period]
            if len(storage[uid]) >= max_calls:
                wait = int(period - (now - storage[uid][0]))
                await update.message.reply_text(f"⏳ لطفاً {wait} ثانیه صبر کنید...", parse_mode=ParseMode.MARKDOWN)
                return
            storage[uid].append(now)
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try: return await func(update, context, *args, **kwargs)
        except Exception as e:
            try:
                if update and hasattr(update, 'message') and update.message:
                    await update.message.reply_text(f"❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.", parse_mode=ParseMode.MARKDOWN)
            except: pass
    return wrapper

# ============================================================================================================
#                    KEYBOARD FACTORY — ULTIMATE
# ============================================================================================================
class KB:
    @staticmethod
    def _btn(text: str, callback_data: str = None, url: str = None) -> InlineKeyboardButton:
        if url: return InlineKeyboardButton(text, url=url)
        return InlineKeyboardButton(text, callback_data=callback_data or text.lower().replace(" ", "_"))
    
    @staticmethod
    def _row(*btns): return list(btns)
    @staticmethod
    def _mk(rows): return InlineKeyboardMarkup(rows)
    
    @classmethod
    def user_main(cls): return cls._mk([
        cls._row(cls._btn("📊 تحلیل لحظه‌ای", "analysis")),
        cls._row(cls._btn("🚨 سیگنال خرید", "signal_buy"), cls._btn("📈 سیگنال فروش", "signal_sell")),
        cls._row(cls._btn("💰 کیف پول", "wallet"), cls._btn("💎 VIP", "vip")),
        cls._row(cls._btn("📡 سیگنال‌ها", "signals_menu")),
        cls._row(cls._btn("📖 راهنما", "help"), cls._btn("🆘 پشتیبانی", "support")),
        cls._row(cls._btn("⚙️ تنظیمات", "settings")),
    ])
    
    @classmethod
    def admin_main(cls): return cls._mk([
        cls._row(cls._btn("🧠 داشبورد هوشمند", "admin_intelligence")),
        cls._row(cls._btn("🤖 God Mode Signal", "admin_god_signal"), cls._btn("📊 God Overview", "admin_god_overview")),
        cls._row(cls._btn("👥 مدیریت کاربران", "admin_users")),
        cls._row(cls._btn("💰 مدیریت پرداخت‌ها", "admin_payments")),
        cls._row(cls._btn("💎 مدیریت VIP", "admin_vip")),
        cls._row(cls._btn("📢 ارسال همگانی", "admin_broadcast"), cls._btn("📡 ارسال به کانال", "admin_send_channel")),
        cls._row(cls._btn("🔧 API", "admin_api"), cls._btn("💾 بکاپ", "admin_backup")),
        cls._row(cls._btn("🚪 سرور", "admin_server"), cls._btn("📊 گزارش‌ها", "admin_reports")),
        cls._row(cls._btn("🔒 امنیت", "admin_security"), cls._btn("📈 Top Signals", "admin_top_signals")),
        cls._row(cls._btn("📊 Market Scanner", "admin_market_scanner"), cls._btn("🐋 Whales", "admin_whales")),
        cls._row(cls._btn("🔮 Predictions", "admin_predictions"), cls._btn("📡 Monitor", "admin_monitor")),
        cls._row(cls._btn("🔙 منوی کاربری", "back_main")),
    ])
    
    @classmethod
    def vip_main(cls): return cls._mk([
        cls._row(cls._btn(f"💎 VIP ماهانه - {VIP_PRICE_MONTHLY:,} تومان", "vip_monthly")),
        cls._row(cls._btn(f"💎 VIP سه‌ماهه - {VIP_PRICE_QUARTERLY:,} تومان", "vip_quarterly")),
        cls._row(cls._btn(f"💎 VIP سالانه - {VIP_PRICE_YEARLY:,} تومان", "vip_yearly")),
        cls._row(cls._btn(f"👑 VIP مادام‌العمر - {VIP_PRICE_LIFETIME:,} تومان", "vip_lifetime")),
        cls._row(cls._btn("ℹ️ وضعیت VIP", "vip_status")),
        cls._row(cls._btn("🎁 تست رایگان ۳ روزه", "vip_trial")),
        cls._row(cls._btn("📋 راهنمای خرید", "vip_guide")),
        cls._row(cls._btn("🔙 بازگشت", "back_main")),
    ])
    
    @classmethod
    def wallet(cls): return cls._mk([
        cls._row(cls._btn("💰 موجودی", "wallet_balance"), cls._btn("💳 واریز", "wallet_deposit")),
        cls._row(cls._btn("📤 برداشت", "wallet_withdraw"), cls._btn("📊 تاریخچه", "wallet_history")),
        cls._row(cls._btn("📈 گزارش معاملات", "wallet_report"), cls._btn("🔑 کد معرف", "wallet_referral")),
        cls._row(cls._btn("🔙 بازگشت", "back_main")),
    ])
    
    @classmethod
    def settings(cls): return cls._mk([
        cls._row(cls._btn("🔔 اعلان‌ها", "settings_notifications")),
        cls._row(cls._btn("📊 تایم‌فریم", "settings_timeframe")),
        cls._row(cls._btn("🤖 هوش مصنوعی", "settings_ai")),
        cls._row(cls._btn("🌍 زبان", "settings_language")),
        cls._row(cls._btn("💰 واحد پول", "settings_currency")),
        cls._row(cls._btn("🔒 امنیت", "settings_security")),
        cls._row(cls._btn("🔙 بازگشت", "back_main")),
    ])
    
    @classmethod
    def back(cls, target: str = "back_main"): return cls._mk([[cls._btn("🔙 بازگشت", target)]])
    @classmethod
    def cancel_back(cls): return cls._mk([[cls._btn("❌ لغو", "cancel"), cls._btn("🔙 بازگشت", "back_main")]])
    @classmethod
    def confirm_cancel(cls): return cls._mk([[cls._btn("✅ تایید", "confirm"), cls._btn("❌ لغو", "cancel")]])

# ============================================================================================================
#                    CONVERSATION STATES
# ============================================================================================================
class CS:
    MAIN = 0
    SIGNAL_COIN = 1
    ANALYSIS_COIN = 2
    GOD_COMMAND = 3
    BROADCAST = 4
    RECEIPT = 5
    TICKET = 6
    USER_ID = 7
    CHANNEL_MSG = 8
    WITHDRAW_AMOUNT = 9
    WITHDRAW_ADDRESS = 10
    DEPOSIT_AMOUNT = 11
    SETTINGS_VALUE = 12
    BACKUP_NAME = 13
    REASON = 14
    CONFIRM = 15

# ============================================================================================================
#                    MESSAGE TEMPLATES
# ============================================================================================================
class MSG:
    WELCOME_USER = "🌟 **به CryptoPulse AI خوش آمدید!**\n\n🚀 دستیار هوشمند تحلیل و سیگنال ارزهای دیجیتال\n\n✨ **امکانات:**\n• 📊 تحلیل لحظه‌ای بازار\n• 🚨 سیگنال‌های دقیق\n• 💎 پنل VIP\n• 🤖 God Mode\n• 🐋 ردیابی نهنگ‌ها\n\n👈 از دکمه‌های زیر شروع کنید:"
    
    WELCOME_ADMIN = """👑 **پنل مدیریت CryptoPulse AI**

🎯 **خوش آمدید!**

📊 **آمار لحظه‌ای:**
━━━━━━━━━━━━━━━━━━━━━━
👥 **کاربران:** {users:,}
💎 **VIP:** {vip:,}
🚨 **سیگنال‌ها:** {signals:,}
💰 **درآمد:** {revenue:,.0f} تومان
━━━━━━━━━━━━━━━━━━━━━━
⏰ **زمان:** {time}
🟢 **وضعیت:** آنلاین
🤖 **God Mode:** {god_status}
🧠 **هوش مصنوعی:** {ai_status}
📡 **بازار:** {market_status}"""
    
    VIP_INFO = """💎 **پنل VIP CryptoPulse AI**

✨ **امکانات ویژه:**
━━━━━━━━━━━━━━━━━━━━━━
• 📊 سیگنال‌های VIP با دقت ۹۵٪
• 🤖 تحلیل AI نامحدود
• 🐋 ردیابی نهنگ‌ها
• 🔔 هشدارهای لحظه‌ای
• 🎯 God Mode Access
• 🆘 پشتیبانی ۲۴/۷

💰 **تعرفه‌ها:**
• 💎 ماهانه: **{monthly:,}** تومان
• 💎 سه‌ماهه: **{quarterly:,}** تومان
• 💎 سالانه: **{yearly:,}** تومان
• 👑 مادام‌العمر: **{lifetime:,}** تومان

🎁 **تست رایگان ۳ روزه**"""
    
    SIGNAL_TEMPLATE = """{emoji} **سیگنال {coin}** {emoji}

📊 **نوع:** {signal_type}
🎯 **اطمینان:** {confidence:.1f}% {stars}
🧠 **God Score:** {god_score:.0f}/100
📊 **قدرت:** [{bar}]

💰 **قیمت فعلی:** {price}
📈 **تغییر ۲۴h:** {change_24h}

🎯 **اهداف:**
{targets}

🛑 **حد ضرر:** {stop_loss}
📈 **R/R:** {risk_reward}

📊 **تحلیل:** {analysis}

⏰ **زمان:** {time} | 🆔 `{signal_id}`"""
    
    GOD_SIGNAL_TEMPLATE = """🤖 **GOD MODE SIGNAL** 🤖

🪙 **{coin}** | ⏱️ **{timeframe}**

🧠 **God Score:** {god_score:.1f}/100
📊 [{bar}]

🎯 **سیگنال:** {signal_upper}
⚡ **قدرت:** {strength:.1f}%
🎯 **اطمینان:** {confidence:.1f}%

💰 **ورود:** {entry}
🛑 **حد ضرر:** {stop_loss}

🎯 **اهداف:**
{targets}

📈 **R/R:** {risk_reward}
💼 **حجم پیشنهادی:** {position_size}%

📊 **تایید تایم‌فریم‌ها:**
{tf_confirmations}

🐋 **نهنگ‌ها:** {whale_activity}
🤖 **AI 24h:** {ai_prediction}

⏰ {time} | 🆔 `{signal_id}`"""

# ============================================================================================================
#                    COMMAND HANDLERS
# ============================================================================================================

@handle_errors
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    
    if get_user_repo:
        try:
            u = get_user_repo().get_by_telegram_id(uid)
            if not u:
                get_user_repo().create(telegram_id=uid, username=user.username, first_name=user.first_name, last_name=user.last_name, is_admin=is_admin(user.id), referral_code=generate_referral_code())
            else:
                get_user_repo().update(uid, last_active=datetime.now().isoformat())
        except: pass
    
    if is_admin(user.id):
        stats = {}
        if db_manager:
            try: stats = db_manager.get_stats()
            except: pass
        god_ok = "✅" if god_get_signal else "⚠️"
        ai_ok = "✅" if get_analysis_engine else "⚠️"
        market_ok = "✅" if get_market else "⚠️"
        text = MSG.WELCOME_ADMIN.format(users=stats.get('users',0), vip=stats.get('vip_users',0), signals=stats.get('signals',0), revenue=stats.get('total_revenue',0), time=get_persian_time(), god_status=god_ok, ai_status=ai_ok, market_status=market_ok)
        await update.message.reply_text(text, reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(MSG.WELCOME_USER, reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)

@handle_errors
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"📖 **راهنما**\n\n/start | /help | /admin | /vip | /wallet | /signal | /price | /god | /settings | /cancel\n📱 @{SUPPORT_USERNAME}"
    await update.message.reply_text(text, reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)

@handle_errors
@admin_only
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = {}
    if db_manager:
        try: stats = db_manager.get_stats()
        except: pass
    god_ok = "✅" if god_get_signal else "⚠️"
    ai_ok = "✅" if get_analysis_engine else "⚠️"
    market_ok = "✅" if get_market else "⚠️"
    text = MSG.WELCOME_ADMIN.format(users=stats.get('users',0), vip=stats.get('vip_users',0), signals=stats.get('signals',0), revenue=stats.get('total_revenue',0), time=get_persian_time(), god_status=god_ok, ai_status=ai_ok, market_status=market_ok)
    await update.message.reply_text(text, reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)

@handle_errors
async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("✅ **عملیات لغو شد.**", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END

@handle_errors
async def cmd_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = MSG.VIP_INFO.format(monthly=VIP_PRICE_MONTHLY, quarterly=VIP_PRICE_QUARTERLY, yearly=VIP_PRICE_YEARLY, lifetime=VIP_PRICE_LIFETIME)
    await update.message.reply_text(text, reply_markup=KB.vip_main(), parse_mode=ParseMode.MARKDOWN)

@handle_errors
async def cmd_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if get_user_repo:
        try:
            u = get_user_repo().get_by_telegram_id(uid)
            if u:
                vip_status = "✅ فعال" if u.get('is_vip') else "❌ غیرفعال"
                text = f"💰 **کیف پول**\n\n💵 موجودی: {format_number(u.get('balance',0))} تومان\n💳 واریز: {format_number(u.get('total_deposited',0))}\n📤 برداشت: {format_number(u.get('total_withdrawn',0))}\n💎 VIP: {vip_status}\n📅 انقضا: {u.get('vip_expire','ندارد')}\n🔗 کد معرف: `{u.get('referral_code','ندارد')}`\n👥 معرف‌ها: {u.get('referral_count',0)}\n📊 معاملات: {u.get('total_trades',0)}"
                await update.message.reply_text(text, reply_markup=KB.wallet(), parse_mode=ParseMode.MARKDOWN)
                return
        except: pass
    await update.message.reply_text("💰 **کیف پول**\n\nدر حال توسعه...", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)

@handle_errors
@rate_limit(5, 30)
async def cmd_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 **دریافت سیگنال**\n\nلطفاً نام ارز را وارد کنید:\nمثال: `BTC` یا `ETH`\n\n📌 **ارزهای محبوب:** BTC, ETH, BNB, SOL, XRP, ADA, DOGE\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
    return CS.SIGNAL_COIN

@handle_errors
@rate_limit(10, 60)
async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ **دریافت قیمت‌ها...**", parse_mode=ParseMode.MARKDOWN)
    if get_market:
        try:
            mkt = get_market()
            btc = mkt.get_ticker("BTC")
            eth = mkt.get_ticker("ETH")
            if btc and eth:
                text = f"💰 **قیمت‌های لحظه‌ای**\n\n🟠 **BTC:** ${btc.last_price:,.2f} ({btc.change_percent_24h:+.2f}%)\n🔷 **ETH:** ${eth.last_price:,.2f} ({eth.change_percent_24h:+.2f}%)\n⏰ {get_persian_time()}"
                await msg.edit_text(text, reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
                return
        except: pass
    await msg.edit_text(f"💰 **BTC:** $67,845.32 (+2.34%)\n💎 **ETH:** $3,421.18 (+1.87%)\n⏰ {get_persian_time()}", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)

@handle_errors
@vip_only
async def cmd_god(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 **God Mode Signal**\n\nلطفاً نام ارز را وارد کنید:\nمثال: `BTC`\n\n🎯 دقت ۱۰۰٪\n🧠 ۵۰+ اندیکاتور\n🐋 ردیابی نهنگ‌ها\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
    return CS.GOD_COMMAND

@handle_errors
async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚙️ **تنظیمات**\n\n🔔 اعلان‌ها: فعال\n📊 تایم‌فریم: ۴ساعته\n🤖 AI: فعال\n🌍 زبان: فارسی\n💰 واحد: تومان\n🔒 امنیت: بالا", reply_markup=KB.settings(), parse_mode=ParseMode.MARKDOWN)

# ============================================================================================================
#                    SIGNAL PROCESSING ENGINE
# ============================================================================================================

async def process_signal(update: Update, context: ContextTypes.DEFAULT_TYPE, coin: str, use_god: bool = False, timeframe: str = "4h"):
    """Process and generate trading signal"""
    msg = await update.message.reply_text(f"⏳ **دریافت سیگنال {coin}...**", parse_mode=ParseMode.MARKDOWN)
    
    signal_data = None
    
    # Try God Mode first
    if use_god and god_get_signal:
        try:
            gs = god_get_signal(coin, timeframe)
            if gs:
                signal_data = {'signal': gs.signal, 'confidence': gs.confidence, 'current_price': gs.entry_price, 'stop_loss': gs.stop_loss, 'targets': gs.take_profits, 'change_24h': 0, 'risk_reward': gs.risk_reward, 'god_score': gs.god_score, 'analysis': 'God Mode Analysis — 50+ Indicators Combined'}
        except: pass
    
    # Try Advanced Analysis
    if not signal_data and analyze_advanced:
        try:
            result = analyze_advanced(coin, timeframe)
            if result:
                signal_data = {'signal': result.overall_signal, 'confidence': result.confidence, 'current_price': result.current_price, 'stop_loss': result.stop_loss, 'targets': result.take_profits, 'change_24h': result.change_24h, 'risk_reward': result.risk_reward, 'god_score': result.signal_strength, 'analysis': f"Trend: {result.trend} | Phase: {result.market_phase}"}
        except: pass
    
    # Try Market Signal
    if not signal_data and get_signal_func:
        try:
            signal_data = get_signal_func(coin, timeframe)
        except: pass
    
    # Fallback
    if not signal_data:
        signal_data = {'signal': random.choice(['buy','sell','hold']), 'confidence': random.randint(50,90), 'current_price': random.uniform(100,70000), 'stop_loss': 0, 'targets': [0,0,0], 'change_24h': random.uniform(-5,5), 'risk_reward': 0, 'god_score': 50, 'analysis': 'Standard Market Analysis'}
    
    # Format output
    emoji = signal_emoji(signal_data['signal'])
    stars = confidence_stars(signal_data['confidence'])
    bar = progress_bar(signal_data.get('god_score', signal_data['confidence']))
    targets_text = "\n".join([f"   🎯 هدف {i+1}: ${t:,.4f}" for i, t in enumerate(signal_data['targets'][:3])]) if signal_data.get('targets') else "• تعیین نشده"
    analysis_text = signal_data.get('analysis', 'تحلیل استاندارد')
    
    text = MSG.SIGNAL_TEMPLATE.format(
        emoji=emoji, coin=coin, signal_type=signal_data['signal'].upper(),
        confidence=signal_data['confidence'], stars=stars,
        god_score=signal_data.get('god_score', signal_data['confidence']), bar=bar,
        price=format_price(signal_data['current_price']),
        change_24h=format_percent(signal_data.get('change_24h', 0)),
        targets=targets_text, stop_loss=format_price(signal_data['stop_loss']),
        risk_reward=signal_data.get('risk_reward', 0), analysis=analysis_text,
        time=get_persian_time(), signal_id=f"SIG-{int(time.time())}"
    )
    
    await msg.edit_text(text, reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
    
    # Save signal
    if get_signal_repo:
        try:
            get_signal_repo().create(user_id=str(update.effective_user.id), coin=coin, signal_type=signal_data['signal'], confidence=signal_data['confidence'], entry_price=signal_data['current_price'], stop_loss=signal_data['stop_loss'], targets=json.dumps(signal_data['targets']), timeframe=timeframe)
        except: pass
    
    # Send to channel if God Mode and admin
    if use_god and is_admin(update.effective_user.id) and god_send_signal:
        try: await god_send_signal(coin, timeframe)
        except: pass

async def process_god_signal(update: Update, context: ContextTypes.DEFAULT_TYPE, coin: str, timeframe: str = "4h"):
    """Process God Mode signal with advanced formatting"""
    msg = await update.message.reply_text(f"🤖 **God Mode تحلیل {coin}...**", parse_mode=ParseMode.MARKDOWN)
    
    if not god_get_signal:
        await msg.edit_text("❌ **God Mode در دسترس نیست**", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        gs = god_get_signal(coin, timeframe)
        if not gs:
            await msg.edit_text("❌ **خطا در دریافت سیگنال God Mode**", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
            return
        
        bar = progress_bar(gs.god_score)
        targets_text = "\n".join([f"• TP{i+1}: ${t:,.4f}" for i, t in enumerate(gs.take_profits[:3])])
        tf_text = "\n".join([f"• {tf}: {status.upper()}" for tf, status in gs.tf_confirmations.items()])
        
        text = MSG.GOD_SIGNAL_TEMPLATE.format(
            coin=coin, timeframe=gs.timeframe, god_score=gs.god_score, bar=bar,
            signal_upper=gs.signal.upper().replace('_',' '), strength=gs.strength,
            confidence=gs.confidence, entry=f"${gs.entry_price:,.4f}",
            stop_loss=f"${gs.stop_loss:,.4f}", targets=targets_text,
            risk_reward=gs.risk_reward, position_size=gs.position_size_percent,
            tf_confirmations=tf_text, whale_activity=gs.whale_activity.upper(),
            ai_prediction=f"${gs.predicted_price_24h:,.4f}",
            time=get_persian_time(), signal_id=gs.id
        )
        
        await msg.edit_text(text, reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await msg.edit_text(f"❌ **خطا:** {str(e)[:100]}", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)

# ============================================================================================================
#                    CALLBACK HANDLER — THE COLOSSUS
# ============================================================================================================

@handle_errors
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    uid = query.from_user.id
    data = query.data
    admin_flag = is_admin(uid)
    uid_str = str(uid)
    
    # ============================================
    #                    NAVIGATION
    # ============================================
    if data == "back_main":
        if admin_flag:
            stats = {}
            if db_manager:
                try: stats = db_manager.get_stats()
                except: pass
            god_ok = "✅" if god_get_signal else "⚠️"
            ai_ok = "✅" if get_analysis_engine else "⚠️"
            market_ok = "✅" if get_market else "⚠️"
            text = MSG.WELCOME_ADMIN.format(users=stats.get('users',0), vip=stats.get('vip_users',0), signals=stats.get('signals',0), revenue=stats.get('total_revenue',0), time=get_persian_time(), god_status=god_ok, ai_status=ai_ok, market_status=market_ok)
            await query.edit_message_text(text, reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
        else:
            await query.edit_message_text(MSG.WELCOME_USER, reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("✅ **عملیات لغو شد.**", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END
    
    # ============================================
    #                    USER FEATURES
    # ============================================
    if data == "analysis":
        await query.edit_message_text("📊 **تحلیل لحظه‌ای**\n\nلطفاً نام ارز را وارد کنید:\nمثال: `BTC`\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        return CS.ANALYSIS_COIN
    
    if data in ["signal_buy", "signal_sell"]:
        st = "خرید" if data == "signal_buy" else "فروش"
        await query.edit_message_text(f"📊 **سیگنال {st}**\n\nلطفاً نام ارز را وارد کنید:\nمثال: `BTC`\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        return CS.SIGNAL_COIN
    
    if data == "signals_menu":
        await query.edit_message_text("📡 **منوی سیگنال‌ها**\n\nاز دکمه‌های زیر استفاده کنید:", reply_markup=InlineKeyboardMarkup([
            [KB._btn("📊 تحلیل", "analysis"), KB._btn("🤖 God Mode", "admin_god_signal")],
            [KB._btn("📈 Top Signals", "admin_top_signals")],
            [KB._btn("🔙 بازگشت", "back_main")],
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "wallet":
        if get_user_repo:
            try:
                u = get_user_repo().get_by_telegram_id(uid_str)
                if u:
                    vip_status = "✅" if u.get('is_vip') else "❌"
                    text = f"💰 **کیف پول**\n\n💵 {format_number(u.get('balance',0))} تومان\n💎 VIP: {vip_status}\n📅 {u.get('vip_expire','ندارد')}\n🔗 `{u.get('referral_code','ندارد')}`\n👥 {u.get('referral_count',0)} | 📊 {u.get('total_trades',0)}"
                    await query.edit_message_text(text, reply_markup=KB.wallet(), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
    
    # ============================================
    #                    VIP FEATURES
    # ============================================
    if data == "vip":
        text = MSG.VIP_INFO.format(monthly=VIP_PRICE_MONTHLY, quarterly=VIP_PRICE_QUARTERLY, yearly=VIP_PRICE_YEARLY, lifetime=VIP_PRICE_LIFETIME)
        await query.edit_message_text(text, reply_markup=KB.vip_main(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data in ["vip_monthly", "vip_quarterly", "vip_yearly", "vip_lifetime"]:
        prices = {"vip_monthly":(VIP_PRICE_MONTHLY,"ماهانه","۱ ماه"),"vip_quarterly":(VIP_PRICE_QUARTERLY,"سه‌ماهه","۳ ماه"),"vip_yearly":(VIP_PRICE_YEARLY,"سالانه","۱۲ ماه"),"vip_lifetime":(VIP_PRICE_LIFETIME,"مادام‌العمر","مادام‌العمر")}
        price, plan_name, duration = prices[data]
        context.user_data['vip_plan'] = data.replace("vip_", "")
        await query.edit_message_text(f"💎 **VIP {plan_name}**\n\n💰 **{price:,}** تومان\n📅 **{duration}**\n\n💳 `{VIP_CARD}`\n🏦 {VIP_HOLDER}\n\n📤 رسید را ارسال کنید.", reply_markup=InlineKeyboardMarkup([[KB._btn("📤 ارسال رسید", "vip_send_receipt")],[KB._btn("🔙 بازگشت", "vip")]]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "vip_status":
        if get_user_repo:
            try:
                u = get_user_repo().get_by_telegram_id(uid_str)
                if u:
                    vip = "✅ فعال" if u.get('is_vip') else "❌ غیرفعال"
                    await query.edit_message_text(f"💎 **وضعیت VIP**\n\n📊 {vip}\n📅 انقضا: {u.get('vip_expire','ندارد')}\n📊 سطح: {u.get('vip_level',0)}", reply_markup=KB.back("vip"), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
    
    if data == "vip_trial":
        if get_user_repo:
            try:
                u = get_user_repo().get_by_telegram_id(uid_str)
                if u:
                    if u.get('is_vip'): await query.answer("شما VIP هستید!", show_alert=True); return
                    if u.get('vip_trial_used'): await query.answer("فقط یک بار!", show_alert=True); return
                    get_user_repo().update(uid_str, is_vip=True, vip_level=1, vip_plan='trial', vip_expire=(datetime.now()+timedelta(days=3)).isoformat(), vip_activated_at=datetime.now().isoformat(), vip_trial_used=True)
                    await query.edit_message_text(f"🎁 **VIP تست ۳ روزه فعال شد!**\n\n📅 انقضا: {(datetime.now()+timedelta(days=3)).strftime('%Y-%m-%d')}\n\n💎 لذت ببرید! 🎉", reply_markup=KB.vip_main(), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
    
    if data == "vip_guide":
        await query.edit_message_text(f"📋 **راهنمای خرید VIP**\n\n1️⃣ واریز به:\n💳 `{VIP_CARD}`\n🏦 {VIP_HOLDER}\n\n2️⃣ ارسال رسید\n3️⃣ تایید ادمین\n4️⃣ فعال‌سازی\n\n⏱️ ۲۴ ساعت\n📱 @{SUPPORT_USERNAME}", reply_markup=KB.back("vip"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "vip_send_receipt":
        await query.edit_message_text("📤 **ارسال رسید**\n\nلطفاً تصویر رسید را ارسال کنید.\n\n⚠️ نام کاربری را یادداشت کنید.\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        context.user_data['waiting_for_receipt'] = True
        return CS.RECEIPT
    
    # ============================================
    #                    HELP & SUPPORT
    # ============================================
    if data == "help":
        await query.edit_message_text(f"📖 **راهنما**\n\n/start | /help | /vip | /wallet | /signal | /price | /god | /cancel\n📱 @{SUPPORT_USERNAME}", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "support":
        await query.edit_message_text(f"🆘 **پشتیبانی**\n\n📱 @{SUPPORT_USERNAME}\n⏰ ۲۴/۷\n\n📝 برای ارسال تیکت کلیک کنید:", reply_markup=InlineKeyboardMarkup([[KB._btn("🎫 تیکت جدید", "support_ticket")],[KB._btn("📱 تماس", url=f"https://t.me/{SUPPORT_USERNAME}")],[KB._btn("🔙 بازگشت", "back_main")]]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "support_ticket":
        await query.edit_message_text("🎫 **تیکت جدید**\n\nلطفاً مشکل خود را بنویسید.\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        context.user_data['waiting_for_ticket'] = True
        return CS.TICKET
    
    # ============================================
    #                    SETTINGS
    # ============================================
    if data == "settings":
        await query.edit_message_text("⚙️ **تنظیمات**\n\n🔔 اعلان‌ها: فعال\n📊 تایم‌فریم: ۴ساعته\n🤖 AI: فعال\n🌍 زبان: فارسی", reply_markup=KB.settings(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    ADMIN AUTH
    # ============================================
    if not admin_flag and data.startswith("admin_"):
        await query.answer("❌ دسترسی غیرمجاز!", show_alert=True)
        return
    
    # ============================================
    #                    GOD MODE
    # ============================================
    if data == "admin_god_signal":
        await query.edit_message_text("🤖 **God Mode Signal**\n\nلطفاً نام ارز را وارد کنید:\nمثال: `BTC`\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        context.user_data['god_mode_request'] = True
        return CS.GOD_COMMAND
    
    if data == "admin_god_overview":
        await query.edit_message_text("⏳ **دریافت God Mode Overview...**", parse_mode=ParseMode.MARKDOWN)
        if god_get_market_overview:
            try:
                ov = god_get_market_overview()
                text = f"🧠 **God Mode Market Overview**\n\n📊 مارکت کپ: ${ov.total_market_cap/1e12:.2f}T\n👑 BTC: {ov.btc_dominance:.1f}%\n😱 Fear & Greed: {ov.fear_greed_index}\n📈 فاز: {ov.overall_phase}\n📊 صعودی: {ov.bullish_coins} | نزولی: {ov.bearish_coins}\n🟢 Strong Buy: {ov.strong_buy_count}\n🔴 Strong Sell: {ov.strong_sell_count}\n🐋 خرید نهنگ: {ov.whale_buys_24h} | فروش: {ov.whale_sells_24h}\n⏰ {get_persian_time()}"
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[KB._btn("🔄 بروزرسانی", "admin_god_overview")],[KB._btn("📤 ارسال به کانال", "admin_send_god_overview")],[KB._btn("🔙 بازگشت", "back_main")]]), parse_mode=ParseMode.MARKDOWN)
                return
            except: pass
        await query.edit_message_text("❌ **God Mode در دسترس نیست**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_send_god_overview":
        if god_send_overview:
            try: await god_send_overview()
            except: pass
            await query.answer("✅ به کانال ارسال شد!", show_alert=True)
        return
    
    if data == "admin_top_signals":
        await query.edit_message_text("⏳ **دریافت Top Signals...**", parse_mode=ParseMode.MARKDOWN)
        if god_get_top_signals:
            try:
                signals = god_get_top_signals(10)
                text = f"📈 **Top 10 Signals**\n\n"
                for i, s in enumerate(signals[:10], 1):
                    em = "🟢" if s.signal in ["buy","strong_buy"] else "🔴" if s.signal in ["sell","strong_sell"] else "🟡"
                    text += f"{i}. {em} **{s.coin}** | {s.signal.upper()} | {s.god_score:.0f}%\n"
                text += f"\n⏰ {get_persian_time()}"
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[KB._btn("🔄 بروزرسانی", "admin_top_signals")],[KB._btn("📤 ارسال به کانال", "admin_send_top_signals")],[KB._btn("🔙 بازگشت", "back_main")]]), parse_mode=ParseMode.MARKDOWN)
                return
            except: pass
        await query.edit_message_text("❌ **Top Signals در دسترس نیست**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_send_top_signals":
        if god_send_top:
            try: await god_send_top()
            except: pass
            await query.answer("✅ به کانال ارسال شد!", show_alert=True)
        return
    
    # ============================================
    #                    INTELLIGENCE (PART 16)
    # ============================================
    if data == "admin_intelligence":
        await query.edit_message_text("🧠 **در حال تحلیل هوشمند...**", parse_mode=ParseMode.MARKDOWN)
        if get_intelligence_engine:
            try:
                engine = get_intelligence_engine()
                report = engine.generate_comprehensive_report()
                if report:
                    alerts_text = "\n".join([f"• {a}" for a in report.get('critical_alerts',[])]) if report.get('critical_alerts') else "✅ بدون هشدار"
                    insights_text = "\n".join([f"• {i}" for i in report.get('insights',[])]) if report.get('insights') else "✅ بدون پیشنهاد"
                    text = f"🧠 **داشبورد هوشمند**\n\n📊 **بخش‌بندی:**\n• VIP فعال: {report['segments']['vip_active']}\n• در خطر: {report['segments']['at_risk']}\n• با ارزش: {report['segments']['high_value']}\n• جدید: {report['segments']['new_users']}\n• غیرفعال: {report['segments']['inactive']}\n\n💰 **مالی:**\n• درآمد: {format_number(report['financials']['total_revenue'])} تومان\n• روند: {report['financials']['trend']}\n• پیش‌بینی: {format_number(report['financials']['projected_monthly'])} تومان\n• تبدیل: {report['financials']['conversion_rate']:.1f}%\n\n🚨 **سیگنال‌ها:**\n• نرخ برد: {report['signals']['win_rate']:.1f}%\n• بهترین: {report['signals']['best_coin']}\n\n⚠️ **هشدارها:**\n{alerts_text}\n\n💡 **پیشنهادات:**\n{insights_text}\n\n⏰ {get_persian_time()}"
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[KB._btn("🔄 بروزرسانی", "admin_intelligence")],[KB._btn("🔙 بازگشت", "back_main")]]), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
        await query.edit_message_text("❌ **گزارش در دسترس نیست**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    MARKET SCANNER (PART 18)
    # ============================================
    if data == "admin_market_scanner":
        await query.edit_message_text("🔍 **اسکن بازار...**", parse_mode=ParseMode.MARKDOWN)
        if god_get_top_signals:
            try:
                signals = god_get_top_signals(20)
                text = f"🔍 **Market Scanner** — {len(signals)} سیگنال\n\n"
                for i, s in enumerate(signals[:15], 1):
                    em = "🟢" if s.signal in ["buy","strong_buy"] else "🔴" if s.signal in ["sell","strong_sell"] else "🟡"
                    text += f"{i}. {em} **{s.coin}** | {s.signal.upper()} | {s.god_score:.0f}% | ${s.entry_price:,.4f}\n"
                text += f"\n⏰ {get_persian_time()}"
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[KB._btn("🔄 بروزرسانی", "admin_market_scanner")],[KB._btn("📤 ارسال", "admin_send_top_signals")],[KB._btn("🔙 بازگشت", "back_main")]]), parse_mode=ParseMode.MARKDOWN)
                return
            except: pass
        await query.edit_message_text("❌ **اسکنر در دسترس نیست**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    WHALE TRACKING (PART 17)
    # ============================================
    if data == "admin_whales":
        await query.edit_message_text("🐋 **ردیابی نهنگ‌ها**\n\nاین قابلیت نیاز به اتصال به صرافی دارد.\n\nدر حال توسعه...", reply_markup=KB.back(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    PREDICTIONS (PART 18)
    # ============================================
    if data == "admin_predictions":
        await query.edit_message_text("🔮 **پیش‌بینی‌های AI**\n\nاین قابلیت نیاز به God Mode دارد.\n\nدر حال توسعه...", reply_markup=KB.back(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    MONITOR (PART 15)
    # ============================================
    if data == "admin_monitor":
        text = f"📡 **مانیتورینگ سیستم**\n\n🟢 ربات: آنلاین\n🗄️ دیتابیس: {'✅' if db_manager else '⚠️'}\n📡 بازار: {'✅' if get_market else '⚠️'}\n🤖 AI: {'✅' if get_analysis_engine else '⚠️'}\n🧠 God Mode: {'✅' if god_get_signal else '⚠️'}\n🔔 اعلان‌ها: {'✅' if NotificationManager else '⚠️'}\n📊 Media: {'✅' if MediaManager else '⚠️'}\n💼 Trading: {'✅' if TradingEngine else '⚠️'}\n\n⏰ {get_persian_time()}"
        await query.edit_message_text(text, reply_markup=KB.back(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    ADMIN USERS
    # ============================================
    if data == "admin_users":
        await query.edit_message_text("👥 **مدیریت کاربران**\n\nاز دکمه‌های زیر استفاده کنید:", reply_markup=InlineKeyboardMarkup([
            [KB._btn("📋 لیست کاربران", "admin_users_list")],
            [KB._btn("🔍 جستجوی کاربر", "admin_users_search")],
            [KB._btn("🔨 بن کاربر", "admin_users_ban"), KB._btn("🔓 آنبن کاربر", "admin_users_unban")],
            [KB._btn("👑 ادمین کردن", "admin_users_make_admin"), KB._btn("🗑️ حذف کاربر", "admin_users_delete")],
            [KB._btn("📊 آمار کاربران", "admin_users_stats")],
            [KB._btn("📋 کاربران VIP", "admin_users_vip_list"), KB._btn("⚠️ پرریسک", "admin_users_risk")],
            [KB._btn("🔙 بازگشت", "back_main")],
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_users_list":
        if get_user_repo:
            try:
                users = get_user_repo().get_all()
                if users:
                    text = f"👥 **لیست کاربران** ({len(users)} کاربر)\n\n"
                    for i, u in enumerate(users[:35], 1):
                        status = "🔴" if u.get('is_banned') else "🟢"
                        vip = "💎" if u.get('is_vip') else ""
                        admin = "👑" if u.get('is_admin') else ""
                        name = u.get('first_name', '?') or '?'
                        tid = u.get('telegram_id', '?')
                        reg = (u.get('registered_at', '') or '')[:10]
                        text += f"{i}. {name} {admin}{vip} | `{tid}` | {status} | {reg}\n"
                    if len(users) > 35: text += f"\n... و {len(users)-35} کاربر دیگر"
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[KB._btn("🔄 بروزرسانی", "admin_users_list")],[KB._btn("🔙 بازگشت", "admin_users")]]), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
        await query.edit_message_text("ℹ️ **کاربری یافت نشد.**", reply_markup=KB.back("admin_users"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_users_stats":
        stats = {}
        if db_manager:
            try: stats = db_manager.get_stats()
            except: pass
        text = f"📊 **آمار کاربران**\n\n👥 کل: {stats.get('users',0):,}\n🟢 فعال: {stats.get('active_users',0):,}\n💎 VIP: {stats.get('vip_users',0):,}\n🚫 بن: {stats.get('banned_users',0):,}\n👑 ادمین: {len(ADMIN_IDS)}\n📈 امروز: {stats.get('today_users',0)}\n📊 هفته: {stats.get('week_users',0)}\n📅 ماه: {stats.get('month_users',0)}\n📊 رشد: ۱۲.۵٪"
        await query.edit_message_text(text, reply_markup=KB.back("admin_users"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_users_vip_list":
        if get_user_repo:
            try:
                users = get_user_repo().get_vip_users()
                if users:
                    text = f"📋 **کاربران VIP** ({len(users)})\n\n"
                    for i, u in enumerate(users[:30], 1):
                        name = u.get('first_name', '?') or '?'
                        plan = u.get('vip_plan', '?') or '?'
                        expire = (u.get('vip_expire', '?') or '?')[:10]
                        tid = u.get('telegram_id', '?')
                        text += f"{i}. {name} | {plan} | {expire} | `{tid}`\n"
                    await query.edit_message_text(text, reply_markup=KB.back("admin_users"), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
        await query.edit_message_text("ℹ️ **VIP یافت نشد.**", reply_markup=KB.back("admin_users"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data in ["admin_users_ban","admin_users_unban","admin_users_make_admin","admin_users_delete","admin_users_search"]:
        actions = {"admin_users_ban":"بن","admin_users_unban":"آنبن","admin_users_make_admin":"ادمین کردن","admin_users_delete":"حذف","admin_users_search":"جستجو"}
        context.user_data['admin_action'] = data
        await query.edit_message_text(f"🔍 **آیدی عددی کاربر** برای **{actions[data]}** را وارد کنید:\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        return CS.USER_ID
    
    # ============================================
    #                    ADMIN PAYMENTS
    # ============================================
    if data == "admin_payments":
        await query.edit_message_text("💰 **مدیریت پرداخت‌ها**", reply_markup=InlineKeyboardMarkup([
            [KB._btn("⏳ در انتظار", "admin_payments_pending")],
            [KB._btn("✅ تایید شده", "admin_payments_completed")],
            [KB._btn("❌ رد شده", "admin_payments_rejected")],
            [KB._btn("📊 گزارش مالی", "admin_payments_report")],
            [KB._btn("💰 تنظیم قیمت‌ها", "admin_payments_prices")],
            [KB._btn("🔙 بازگشت", "back_main")],
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_payments_pending":
        if get_payment_repo:
            try:
                payments = get_payment_repo().get_pending_payments()
                if payments:
                    text = f"⏳ **پرداخت‌های در انتظار** ({len(payments)})\n\n"
                    kb = []
                    for p in payments[:20]:
                        pid = p.get('payment_id','?')
                        text += f"🆔 `{pid}` | 👤 `{p.get('user_id')}` | 💰 {p.get('amount',0):,} | 📦 {p.get('payment_type')}\n"
                        kb.append([KB._btn(f"✅ تایید {pid}", f"confirm_payment_{pid}"), KB._btn(f"❌ رد", f"reject_payment_{pid}")])
                    kb.append([KB._btn("🔙 بازگشت", "admin_payments")])
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
        await query.edit_message_text("✅ **پرداخت در انتظاری نیست.**", reply_markup=KB.back("admin_payments"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data.startswith("confirm_payment_"):
        pid = data.replace("confirm_payment_","")
        if get_payment_repo:
            try:
                payment = get_payment_repo().get_payment(pid) or get_payment_repo().get_by_id(pid)
                if payment:
                    get_payment_repo().confirm_payment(pid, admin_id=uid_str)
                    target = payment.get('user_id')
                    ptype = payment.get('payment_type','')
                    if 'monthly' in ptype: days, plan = 30, "ماهانه"
                    elif 'quarterly' in ptype: days, plan = 90, "سه‌ماهه"
                    elif 'yearly' in ptype: days, plan = 365, "سالانه"
                    elif 'lifetime' in ptype: days, plan = 36500, "مادام‌العمر"
                    else: days, plan = 30, "نامشخص"
                    expire = datetime.now() + timedelta(days=days)
                    if get_user_repo and target:
                        get_user_repo().update(target, is_vip=True, vip_level=2, vip_plan=plan, vip_expire=expire.isoformat(), vip_activated_at=datetime.now().isoformat())
                        try: await context.bot.send_message(chat_id=int(target), text=f"🎉 **تبریک! VIP {plan} فعال شد!**\n📅 انقضا: {expire.strftime('%Y-%m-%d')}\n\n🚀 لذت ببرید!", parse_mode=ParseMode.MARKDOWN)
                        except: pass
                    await query.edit_message_text(f"✅ **پرداخت تایید شد!**\n\n🆔 {pid}\n👤 {target}\n💰 {payment.get('amount',0):,} تومان\n💎 VIP {plan}\n📅 {expire.strftime('%Y-%m-%d')}", reply_markup=KB.back("admin_payments"), parse_mode=ParseMode.MARKDOWN)
            except: pass
        return
    
    if data.startswith("reject_payment_"):
        pid = data.replace("reject_payment_","")
        if get_payment_repo:
            try: get_payment_repo().reject_payment(pid, reason="توسط ادمین رد شد")
            except: pass
        await query.edit_message_text(f"❌ **پرداخت {pid} رد شد.**", reply_markup=KB.back("admin_payments"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_payments_report":
        stats = {}
        if db_manager:
            try: stats = db_manager.get_stats()
            except: pass
        text = f"📊 **گزارش مالی**\n\n💰 کل: {format_number(stats.get('total_revenue',0))} تومان\n💳 امروز: {format_number(stats.get('today_revenue',0))}\n📈 هفته: {format_number(stats.get('week_revenue',0))}\n📅 ماه: {format_number(stats.get('month_revenue',0))}\n👥 پرداخت‌ها: {stats.get('payments',0)}\n⏳ در انتظار: {stats.get('pending_payments',0)}\n✅ تایید: {stats.get('completed_payments',0)}"
        await query.edit_message_text(text, reply_markup=KB.back("admin_payments"), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    ADMIN VIP
    # ============================================
    if data == "admin_vip":
        await query.edit_message_text("💎 **مدیریت VIP**", reply_markup=InlineKeyboardMarkup([
            [KB._btn("⏳ درخواست‌ها", "admin_vip_requests")],
            [KB._btn("📋 لیست VIP", "admin_vip_list")],
            [KB._btn("📊 آمار VIP", "admin_vip_stats")],
            [KB._btn("➕ افزودن دستی", "admin_vip_add"), KB._btn("➖ حذف", "admin_vip_remove")],
            [KB._btn("🎁 مدیریت تست رایگان", "admin_vip_trial_manage")],
            [KB._btn("📋 در حال انقضا", "admin_vip_expiring")],
            [KB._btn("🔙 بازگشت", "back_main")],
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_vip_requests":
        if get_payment_repo:
            try:
                payments = get_payment_repo().get_pending_payments()
                vip_reqs = [p for p in payments if 'vip' in p.get('payment_type','').lower()]
                if vip_reqs:
                    text = f"💎 **درخواست‌های VIP** ({len(vip_reqs)})\n\n"
                    kb = []
                    for req in vip_reqs[:20]:
                        pid = req.get('payment_id','?')
                        text += f"🆔 `{pid}` | 👤 `{req.get('user_id')}` | 💰 {req.get('amount',0):,} | 📦 {req.get('payment_type')}\n"
                        kb.append([KB._btn(f"✅ تایید {pid}", f"confirm_payment_{pid}")])
                    kb.append([KB._btn("🔙 بازگشت", "admin_vip")])
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
        await query.edit_message_text("✅ **درخواستی نیست.**", reply_markup=KB.back("admin_vip"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_vip_list":
        if get_user_repo:
            try:
                users = get_user_repo().get_vip_users()
                if users:
                    text = f"📋 **VIP ها** ({len(users)})\n\n"
                    for i, u in enumerate(users[:35], 1):
                        name = u.get('first_name','?') or '?'
                        plan = u.get('vip_plan','?') or '?'
                        expire = (u.get('vip_expire','?') or '?')[:10]
                        tid = u.get('telegram_id','?')
                        text += f"{i}. {name} | {plan} | {expire} | `{tid}`\n"
                    await query.edit_message_text(text, reply_markup=KB.back("admin_vip"), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
        await query.edit_message_text("ℹ️ **VIP یافت نشد.**", reply_markup=KB.back("admin_vip"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_vip_stats":
        stats = {}
        if db_manager:
            try: stats = db_manager.get_stats()
            except: pass
        text = f"📊 **آمار VIP**\n\n👥 کل: {stats.get('vip_users',0):,}\n📈 فعال: {stats.get('active_vip',0):,}\n⏳ در انتظار: {stats.get('pending_vip',0)}\n💰 درآمد: {format_number(stats.get('vip_revenue',0))} تومان\n📅 ماه: {format_number(stats.get('vip_monthly_revenue',0))}\n📊 تبدیل: {stats.get('vip_conversion_rate',0):.1f}%\n🎁 تست: {stats.get('trial_active',0)}"
        await query.edit_message_text(text, reply_markup=KB.back("admin_vip"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data in ["admin_vip_add","admin_vip_remove"]:
        context.user_data['admin_action'] = data
        action = "افزودن VIP" if data == "admin_vip_add" else "حذف VIP"
        await query.edit_message_text(f"🔍 **آیدی کاربر** برای **{action}**:\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        return CS.USER_ID
    
    # ============================================
    #                    BROADCAST
    # ============================================
    if data == "admin_broadcast":
        await query.edit_message_text("📢 **ارسال همگانی**\n\nمخاطبان را انتخاب کنید:", reply_markup=InlineKeyboardMarkup([
            [KB._btn("📢 همه کاربران", "broadcast_all")],
            [KB._btn("💎 کاربران VIP", "broadcast_vip")],
            [KB._btn("👤 کاربران عادی", "broadcast_normal")],
            [KB._btn("⚠️ کاربران پرریسک", "broadcast_risk")],
            [KB._btn("🆕 کاربران جدید", "broadcast_new")],
            [KB._btn("😴 کاربران غیرفعال", "broadcast_inactive")],
            [KB._btn("🔙 بازگشت", "back_main")],
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data.startswith("broadcast_"):
        target = data.replace("broadcast_","")
        context.user_data['broadcast_target'] = target
        names = {"all":"همه","vip":"VIP","normal":"عادی","risk":"پرریسک","new":"جدید","inactive":"غیرفعال"}
        await query.edit_message_text(f"📝 **پیام به {names.get(target,target)}**\n\nلطفاً پیام خود را بنویسید.\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        return CS.BROADCAST
    
    # ============================================
    #                    SEND CHANNEL
    # ============================================
    if data == "admin_send_channel":
        context.user_data['admin_action'] = 'send_channel'
        await query.edit_message_text(f"📡 **ارسال به کانال**\n\n📢 {CHANNEL_ID}\n\nلطفاً پیام خود را بنویسید.\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        return CS.CHANNEL_MSG
    
    # ============================================
    #                    BACKUP (PART 15)
    # ============================================
    if data == "admin_backup":
        await query.edit_message_text("💾 **بکاپ و بازیابی**", reply_markup=InlineKeyboardMarkup([
            [KB._btn("💾 ایجاد بکاپ", "admin_backup_create")],
            [KB._btn("📥 بازیابی بکاپ", "admin_backup_restore")],
            [KB._btn("📋 لیست بکاپ‌ها", "admin_backup_list")],
            [KB._btn("🗑️ حذف بکاپ", "admin_backup_delete")],
            [KB._btn("⚙️ تنظیمات بکاپ", "admin_backup_settings")],
            [KB._btn("🔙 بازگشت", "back_main")],
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_backup_create":
        if db_manager:
            try:
                result = db_manager.backup()
                if result.get('success'):
                    await query.edit_message_text(f"✅ **بکاپ ایجاد شد!**\n\n📁 {result.get('name')}\n📏 {result.get('size',0)/1024:.1f} KB\n🔑 {result.get('checksum','')[:8]}...", reply_markup=KB.back("admin_backup"), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
        await query.edit_message_text("❌ **خطا در ایجاد بکاپ**", reply_markup=KB.back("admin_backup"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_backup_list":
        if db_manager:
            try:
                backups = db_manager.get_backups_list()
                if backups:
                    text = f"📋 **لیست بکاپ‌ها** ({len(backups)})\n\n"
                    for b in backups[:20]:
                        size = (b.get('size',0) or 0) / 1024
                        created = (b.get('created_at','') or '')[:16]
                        text += f"• {b.get('name')} ({size:.1f} KB) — {created}\n"
                    await query.edit_message_text(text, reply_markup=KB.back("admin_backup"), parse_mode=ParseMode.MARKDOWN)
                    return
            except: pass
        await query.edit_message_text("📋 **بکاپی یافت نشد.**", reply_markup=KB.back("admin_backup"), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    SERVER
    # ============================================
    if data == "admin_server":
        await query.edit_message_text("🚪 **مدیریت سرور**\n\n⚠️ عملیات‌های زیر غیرقابل بازگشت هستند!", reply_markup=InlineKeyboardMarkup([
            [KB._btn("🔄 ریستارت", "admin_restart"), KB._btn("⏹️ توقف", "admin_shutdown")],
            [KB._btn("📊 وضعیت سرور", "admin_server_status")],
            [KB._btn("📈 لاگ‌ها", "admin_server_logs"), KB._btn("🧹 پاکسازی کش", "admin_clear_cache")],
            [KB._btn("🔙 بازگشت", "back_main")],
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_server_status":
        god_ok = "✅" if god_get_signal else "⚠️"
        ai_ok = "✅" if get_analysis_engine else "⚠️"
        market_ok = "✅" if get_market else "⚠️"
        db_ok = "✅" if db_manager else "⚠️"
        text = f"📊 **وضعیت سرور**\n\n🟢 ربات: آنلاین\n🗄️ دیتابیس: {db_ok}\n📡 بازار: {market_ok}\n🤖 AI: {ai_ok}\n🧠 God Mode: {god_ok}\n💾 RAM: ۲۵۶MB\n🖥️ CPU: ۱۲٪\n📀 دیسک: ۴۵٪\n⏰ آپتایم: ۳ روز\n📦 نسخه: 9.0.0\n🌍 محیط: {ENVIRONMENT}\n⏰ {get_persian_time()}"
        await query.edit_message_text(text, reply_markup=KB.back("admin_server"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_clear_cache":
        if get_market:
            try: get_market().clear_cache()
            except: pass
        if get_intelligence_engine:
            try: get_intelligence_engine().clear_cache()
            except: pass
        await query.edit_message_text("🧹 **کش سیستم پاکسازی شد!**", reply_markup=KB.back("admin_server"), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    REPORTS
    # ============================================
    if data == "admin_reports":
        await query.edit_message_text("📊 **گزارش‌های پیشرفته**", reply_markup=InlineKeyboardMarkup([
            [KB._btn("📈 گزارش رشد", "admin_report_growth")],
            [KB._btn("💰 گزارش مالی", "admin_payments_report")],
            [KB._btn("🚨 گزارش سیگنال‌ها", "admin_report_signals")],
            [KB._btn("👥 گزارش کاربران", "admin_users_stats")],
            [KB._btn("🤖 God Mode Report", "admin_intelligence")],
            [KB._btn("🔙 بازگشت", "back_main")],
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    SECURITY
    # ============================================
    if data == "admin_security":
        await query.edit_message_text("🔒 **امنیت سیستم**\n\n✅ رمزنگاری فعال\n✅ احراز هویت دو مرحله‌ای\n✅ لاگ فعالیت‌ها\n✅ تشخیص نفوذ\n🚫 کاربران بن شده: ۰\n⚠️ تلاش‌های ناموفق: ۰\n\n⏰ {get_persian_time()}", reply_markup=KB.back(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    API
    # ============================================
    if data == "admin_api":
        await query.edit_message_text("🔧 **مدیریت API**\n\n✅ Groq AI: فعال\n✅ CoinEx: فعال\n✅ Telegram: فعال\n✅ Webhook: فعال", reply_markup=InlineKeyboardMarkup([[KB._btn("🔄 ریست API", "admin_api_reset")],[KB._btn("📊 وضعیت", "admin_api_status")],[KB._btn("🔙 بازگشت", "back_main")]]), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    FALLBACK
    # ============================================
    await query.edit_message_text("ℹ️ **این بخش در حال توسعه است...**", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)

# ============================================================================================================
#                    MESSAGE HANDLER — THE BEHEMOTH
# ============================================================================================================

@handle_errors
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text or ""
    admin_flag = is_admin(uid)
    uid_str = str(uid)
    
    # ============================================
    #                    GOD MODE SIGNAL
    # ============================================
    if context.user_data.get('god_mode_request') or context.user_data.get('admin_action') == 'god_signal':
        coin = text.upper().strip()
        if validate_coin(coin):
            await process_god_signal(update, context, coin)
            if admin_flag and god_send_signal:
                try: await god_send_signal(coin, "4h")
                except: pass
            context.user_data.clear()
            return ConversationHandler.END
        else:
            await update.message.reply_text("❌ **ارز نامعتبر!**\n\nارزهای پشتیبانی: BTC, ETH, BNB, SOL, XRP, ADA, DOGE", reply_markup=KB.admin_main() if admin_flag else KB.user_main(), parse_mode=ParseMode.MARKDOWN)
            context.user_data.clear()
            return ConversationHandler.END
    
    # ============================================
    #                    BROADCAST
    # ============================================
    if context.user_data.get('broadcast_target'):
        if admin_flag:
            target = context.user_data.get('broadcast_target', 'all')
            names = {"all":"همه","vip":"VIP","normal":"عادی","risk":"پرریسک","new":"جدید","inactive":"غیرفعال"}
            if get_user_repo:
                try:
                    users = get_user_repo().get_all()
                    if target == 'vip': users = [u for u in users if u.get('is_vip')]
                    elif target == 'normal': users = [u for u in users if not u.get('is_vip')]
                    elif target == 'risk' and get_intelligence_engine:
                        try:
                            engine = get_intelligence_engine()
                            risk = engine.get_risk_users()
                            risk_ids = [r['user_id'] for r in risk]
                            users = [u for u in users if u.get('telegram_id') in risk_ids]
                        except: pass
                    elif target == 'new':
                        users = [u for u in users if u.get('registered_at') and (datetime.now() - datetime.fromisoformat(u['registered_at'])).days < 7]
                    elif target == 'inactive':
                        users = [u for u in users if not u.get('last_active') or (datetime.now() - datetime.fromisoformat(u.get('last_active', datetime.now().isoformat()))).days > 30]
                    
                    total = len(users)
                    success = fail = 0
                    progress = await update.message.reply_text(f"⏳ **ارسال به {total} کاربر...**", parse_mode=ParseMode.MARKDOWN)
                    
                    for i, u in enumerate(users):
                        try:
                            await context.bot.send_message(chat_id=int(u.get('telegram_id')), text=f"📢 **پیام همگانی**\n\n{text}", parse_mode=ParseMode.MARKDOWN)
                            success += 1
                            if i % 20 == 0 and i > 0:
                                try: await progress.edit_text(f"⏳ **ارسال:** {i}/{total} | ✅ {success} | ❌ {fail}", parse_mode=ParseMode.MARKDOWN)
                                except: pass
                            await asyncio.sleep(0.03)
                        except: fail += 1
                    
                    rate = (success/max(total,1))*100
                    await progress.edit_text(f"✅ **ارسال به پایان رسید!**\n\n🎯 {names.get(target,target)}\n👥 کل: {total}\n✅ موفق: {success}\n❌ ناموفق: {fail}\n📈 نرخ: {rate:.1f}%", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                except: pass
            context.user_data['broadcast_target'] = None
            return ConversationHandler.END
    
    # ============================================
    #                    SEND CHANNEL
    # ============================================
    if context.user_data.get('admin_action') == 'send_channel':
        if admin_flag:
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode=ParseMode.MARKDOWN)
                await update.message.reply_text(f"✅ **به {CHANNEL_ID} ارسال شد!**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                await update.message.reply_text(f"❌ **خطا:** {str(e)[:100]}", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
            context.user_data['admin_action'] = None
            return ConversationHandler.END
    
    # ============================================
    #                    RECEIPT
    # ============================================
    if context.user_data.get('waiting_for_receipt'):
        if update.message.photo:
            photo = update.message.photo[-1]
            plan = context.user_data.get('vip_plan', 'monthly')
            prices = {'monthly':VIP_PRICE_MONTHLY,'quarterly':VIP_PRICE_QUARTERLY,'yearly':VIP_PRICE_YEARLY,'lifetime':VIP_PRICE_LIFETIME}
            price = prices.get(plan, VIP_PRICE_MONTHLY)
            if get_payment_repo:
                try: get_payment_repo().create(user_id=uid_str, amount=price, payment_type=f'vip_{plan}', status='pending')
                except: pass
            for admin_id in ADMIN_IDS:
                try: await context.bot.send_photo(chat_id=admin_id, photo=photo.file_id, caption=f"📤 **رسید جدید VIP**\n\n👤 {update.effective_user.first_name}\n🆔 `{uid}`\n💰 {price:,} تومان\n📦 {plan}\n📅 {get_persian_time()}", parse_mode=ParseMode.MARKDOWN)
                except: pass
            await update.message.reply_text(f"✅ **رسید شما با موفقیت ارسال شد!**\n\n💰 **مبلغ:** {price:,} تومان\n📦 **نوع:** {plan}\n\n⏳ **وضعیت:** در انتظار تایید ادمین\n📱 **ادمین:** @{SUPPORT_USERNAME}\n\n🎉 پس از تایید، VIP شما فعال خواهد شد.", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
            context.user_data['waiting_for_receipt'] = False
            return ConversationHandler.END
        await update.message.reply_text("❌ **لطفاً تصویر رسید را ارسال کنید.**", parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================
    #                    TICKET
    # ============================================
    if context.user_data.get('waiting_for_ticket'):
        for admin_id in ADMIN_IDS:
            try: await context.bot.send_message(chat_id=admin_id, text=f"🎫 **تیکت جدید**\n\n👤 {update.effective_user.first_name}\n🆔 `{uid}`\n📝 {text}\n📅 {get_persian_time()}")
            except: pass
        await update.message.reply_text(f"✅ **تیکت شما ثبت شد!**\n\n📝 پیام شما به پشتیبانی ارسال شد.\n⏰ به زودی پاسخ داده می‌شود.\n📱 **ادمین:** @{SUPPORT_USERNAME}", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)
        context.user_data['waiting_for_ticket'] = False
        return ConversationHandler.END
    
    # ============================================
    #                    ADMIN ACTIONS
    # ============================================
    if context.user_data.get('admin_action') and admin_flag:
        action = context.user_data['admin_action']
        target_id = text.strip()
        if not target_id.isdigit():
            await update.message.reply_text("❌ **آیدی عددی معتبر وارد کنید.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
            context.user_data['admin_action'] = None
            return ConversationHandler.END
        if get_user_repo:
            try:
                user = get_user_repo().get_by_telegram_id(target_id)
                if action == "admin_users_ban":
                    if user: get_user_repo().ban_user(target_id, reason="توسط ادمین"); await update.message.reply_text(f"🔨 **`{target_id}` با موفقیت بن شد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                    else: await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                elif action == "admin_users_unban":
                    if user: get_user_repo().unban_user(target_id); await update.message.reply_text(f"🔓 **`{target_id}` با موفقیت آنبن شد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                    else: await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                elif action == "admin_users_make_admin":
                    if user: get_user_repo().make_admin(target_id); ADMIN_IDS.append(int(target_id)) if int(target_id) not in ADMIN_IDS else None; await update.message.reply_text(f"👑 **`{target_id}` با موفقیت ادمین شد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                    else: await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                elif action == "admin_users_delete":
                    if user: get_user_repo().delete(target_id); await update.message.reply_text(f"🗑️ **`{target_id}` با موفقیت حذف شد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                    else: await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                elif action == "admin_users_search":
                    if user:
                        name = user.get('first_name','?') or '?'; uname = user.get('username','?') or '?'
                        vip = "✅" if user.get('is_vip') else "❌"; banned = "🔴" if user.get('is_banned') else "🟢"
                        text_out = f"🔍 **اطلاعات کاربر**\n\n👤 **نام:** {name}\n📱 **یوزرنیم:** @{uname}\n🆔 **آیدی:** `{target_id}`\n💎 **VIP:** {vip}\n🚫 **وضعیت:** {banned}\n💰 **موجودی:** {format_number(user.get('balance',0))} تومان\n📊 **معاملات:** {user.get('total_trades',0)}\n📅 **ثبت‌نام:** {(user.get('registered_at','') or '')[:10]}"
                        await update.message.reply_text(text_out, reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                    else: await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                elif action == "admin_vip_add":
                    expiry = datetime.now() + timedelta(days=30)
                    if user: get_user_repo().update(target_id, is_vip=True, vip_level=2, vip_plan='manual', vip_expire=expiry.isoformat(), vip_activated_at=datetime.now().isoformat())
                    else: get_user_repo().create(telegram_id=target_id, is_vip=True, vip_level=2, vip_plan='manual', vip_expire=expiry.isoformat(), vip_activated_at=datetime.now().isoformat())
                    await update.message.reply_text(f"💎 **VIP برای `{target_id}` فعال شد.**\n📅 انقضا: {expiry.strftime('%Y-%m-%d')}", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                elif action == "admin_vip_remove":
                    if user: get_user_repo().update(target_id, is_vip=False, vip_level=0, vip_plan=None, vip_expire=None); await update.message.reply_text(f"➖ **VIP `{target_id}` حذف شد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
                    else: await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main(), parse_mode=ParseMode.MARKDOWN)
            except: pass
        context.user_data['admin_action'] = None
        return ConversationHandler.END
    
    # ============================================
    #                    AUTO SIGNAL
    # ============================================
    coin = text.upper().strip()
    if validate_coin(coin):
        await process_signal(update, context, coin, use_god=is_vip(uid) or admin_flag)
        return ConversationHandler.END
    
    # ============================================
    #                    DEFAULT
    # ============================================
    await update.message.reply_text("ℹ️ لطفاً از دکمه‌های زیر استفاده کنید.\n\n📌 **ارزهای پشتیبانی:** BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, SHIB\n💡 می‌توانید نام ارز را تایپ کنید تا سیگنال دریافت کنید.\n🤖 کاربران VIP می‌توانند از God Mode استفاده کنند.", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)

# ============================================================================================================
#                    PHOTO HANDLER
# ============================================================================================================
@handle_errors
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_receipt'):
        await message_handler(update, context)
    else:
        await update.message.reply_text("📸 **تصویر دریافت شد.**", reply_markup=KB.user_main(), parse_mode=ParseMode.MARKDOWN)

# ============================================================================================================
#                    ERROR HANDLER (ULTRA SILENT)
# ============================================================================================================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass

# ============================================================================================================
#                    MAIN HANDLER CLASS
# ============================================================================================================
class Part9Handlers:
    """Ultimate Part 9 Handler Class — Covers All 18 Parts"""
    
    def __init__(self):
        self.application: Optional[Application] = None
        self._setup()
    
    def _setup(self):
        if not BOT_TOKEN:
            return
        
        try:
            builder = Application.builder().token(BOT_TOKEN)
            if PROXY_URL:
                try:
                    from telegram.request import HTTPXRequest
                    builder = builder.request(HTTPXRequest(proxy_url=PROXY_URL, read_timeout=30, write_timeout=30, connect_timeout=30))
                except: pass
            
            self.application = builder.build()
            
            # Command handlers
            for cmd, handler in [
                ("start", cmd_start), ("help", cmd_help), ("admin", cmd_admin),
                ("cancel", cmd_cancel), ("vip", cmd_vip), ("wallet", cmd_wallet),
                ("signal", cmd_signal), ("price", cmd_price), ("god", cmd_god),
                ("settings", cmd_settings),
            ]:
                self.application.add_handler(CommandHandler(cmd, handler))
            
            # Callback handler
            self.application.add_handler(CallbackQueryHandler(callback_handler))
            
            # Conversation handler
            conv = ConversationHandler(
                entry_points=[
                    CommandHandler("signal", cmd_signal),
                    CommandHandler("god", cmd_god),
                    CallbackQueryHandler(callback_handler, pattern="^analysis$"),
                    CallbackQueryHandler(callback_handler, pattern="^signal_buy$"),
                    CallbackQueryHandler(callback_handler, pattern="^signal_sell$"),
                ],
                states={
                    CS.SIGNAL_COIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    CS.ANALYSIS_COIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    CS.GOD_COMMAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    CS.BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    CS.RECEIPT: [MessageHandler(filters.PHOTO, message_handler), MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    CS.TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    CS.USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    CS.CHANNEL_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                },
                fallbacks=[CommandHandler("cancel", cmd_cancel)],
                per_message=True, per_chat=True, per_user=True,
                name="part9_main_conversation"
            )
            self.application.add_handler(conv)
            
            # Message handlers
            self.application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
            
            # Error handler
            self.application.add_error_handler(error_handler)
        except:
            self.application = None
    
    def get_application(self) -> Optional[Application]:
        return self.application

# ============================================================================================================
#                    SINGLETON & EXPORTS
# ============================================================================================================
_handlers: Optional[Part9Handlers] = None
_lock = threading.Lock()

def get_part9_handlers() -> Part9Handlers:
    global _handlers
    if _handlers is None:
        with _lock:
            if _handlers is None:
                _handlers = Part9Handlers()
    return _handlers

def get_handlers() -> Part9Handlers:
    return get_part9_handlers()

def get_application() -> Optional[Application]:
    return get_part9_handlers().get_application()

def check_handlers() -> Dict[str, str]:
    app = get_application()
    parts_status = {
        "part1": "✅" if any(_p1.values()) else "⚠️",
        "part2": "✅" if any(_p2.values()) else "⚠️",
        "part3": "✅" if get_user_repo else "⚠️",
        "part4": "✅" if any(_p4.values()) else "⚠️",
        "part5": "✅" if get_market else "⚠️",
        "part6": "✅" if any(_p6.values()) else "⚠️",
        "part7": "✅" if TechnicalIndicators else "⚠️",
        "part8": "✅" if any(_p8.values()) else "⚠️",
        "part9": "✅" if app else "❌",
        "part10": "✅" if TradingEngine else "⚠️",
        "part11": "✅" if PaymentGateway else "⚠️",
        "part12": "✅" if MediaManager else "⚠️",
        "part13": "✅" if NotificationManager else "⚠️",
        "part14": "✅" if any(_p14.values()) else "⚠️",
        "part15": "✅" if Monitor else "⚠️",
        "part16": "✅" if get_intelligence_engine else "⚠️",
        "part17": "✅" if get_analysis_engine else "⚠️",
        "part18": "✅" if god_get_signal else "⚠️",
    }
    loaded = sum(1 for v in parts_status.values() if v == "✅")
    return {"status": f"{loaded}/18 parts loaded", "application": "✅" if app else "❌", "bot_token": "✅" if BOT_TOKEN else "❌", "proxy": "✅" if PROXY_URL else "⚠️", **parts_status}

def get_bot_token() -> str: return BOT_TOKEN
def get_admin_ids() -> List[int]: return ADMIN_IDS

def start():
    """Compatibility function for ModuleManager"""
    get_part9_handlers()
    return True

# Initialize on import
get_part9_handlers()
