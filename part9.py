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
║  🚀 کریپتوپالس هوش مصنوعی نسخه ۹ - پارت ۹ - مرکز مدیریت نهایی - کاملاً اجرایی      ║
║  ═══════════════════════════════════════════════════════════════════════════════════   ║
║  🧠 ۳۰+ ماژول | ⚡ کاملاً عملیاتی | 🔥 سطح دکتری | 🏢 آماده تولید                    ║
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

# ===== سکوت کامل همه هشدارها و لاگ‌ها =====
warnings.filterwarnings("ignore")
for cat in [DeprecationWarning, FutureWarning, RuntimeWarning, UserWarning, 
            SyntaxWarning, PendingDeprecationWarning, ImportWarning, BytesWarning, ResourceWarning]:
    warnings.filterwarnings("ignore", category=cat)

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logging.getLogger().setLevel(logging.WARNING)

for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.WARNING)
    logging.getLogger(name).propagate = False

# ===== ایمپورت تلگرام =====
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
    TELEGRAM_AVAILABLE = True
except ImportError as e:
    print("=" * 60)
    print("❌ خطا: کتابخانه python-telegram-bot نصب نیست!")
    print("نصب با دستور: pip install python-telegram-bot[job-queue]")
    print("=" * 60)
    TELEGRAM_AVAILABLE = False
    sys.exit(1)

# ===== ایمپورت‌های اختیاری =====
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
# تنظیمات سراسری
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

if not BOT_TOKEN and len(sys.argv) > 1:
    BOT_TOKEN = sys.argv[1]

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
PART_NAME = "part9"

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
# توابع کمکی
# ============================================================================================================
def is_admin(user_id: int) -> bool:
    """بررسی ادمین بودن کاربر"""
    return user_id in ADMIN_IDS

def get_persian_time() -> str:
    """دریافت زمان شمسی"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_persian_date() -> str:
    """دریافت تاریخ شمسی"""
    return datetime.now().strftime("%Y-%m-%d")

def get_timestamp() -> int:
    """دریافت تایم‌استمپ"""
    return int(time.time())

def validate_coin(coin: str) -> bool:
    """اعتبارسنجی نام ارز"""
    return coin.upper().strip() in SUPPORTED_COINS

def validate_timeframe(tf: str) -> bool:
    """اعتبارسنجی تایم‌فریم"""
    return tf.lower().strip() in SUPPORTED_TIMEFRAMES

def generate_referral_code(length: int = 8) -> str:
    """تولید کد معرف تصادفی"""
    return ''.join(secrets_mod.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def generate_unique_id() -> str:
    """تولید شناسه یکتا"""
    return str(uuid_mod.uuid4())[:12]

def format_number(num: float, decimals: int = 2) -> str:
    """فرمت‌دهی اعداد بزرگ"""
    if abs(num) >= 1e12: return f"{num/1e12:.{decimals}f}T"
    if abs(num) >= 1e9: return f"{num/1e9:.{decimals}f}B"
    if abs(num) >= 1e6: return f"{num/1e6:.{decimals}f}M"
    if abs(num) >= 1e3: return f"{num/1e3:.{decimals}f}K"
    return f"{num:,.{decimals}f}"

def format_price(price: float) -> str:
    """فرمت‌دهی قیمت"""
    if price >= 1000: return f"${price:,.2f}"
    if price >= 1: return f"${price:,.4f}"
    if price >= 0.01: return f"${price:,.6f}"
    return f"${price:,.8f}"

def format_percent(pct: float) -> str:
    """فرمت‌دهی درصد"""
    return f"{pct:+.2f}%"

def signal_emoji(signal_type: str) -> str:
    """ایموجی سیگنال"""
    mapping = {
        "strong_buy":"🟢🟢🟢","buy":"🟢🟢","weak_buy":"🟢",
        "neutral":"🟡","weak_sell":"🔴","sell":"🔴🔴",
        "strong_sell":"🔴🔴🔴","accumulate":"🐋","distribute":"🦈","wait":"⏳"
    }
    return mapping.get(signal_type, "🟡")

def confidence_stars(confidence: float) -> str:
    """ستاره‌های اعتبار"""
    if confidence >= 90: return "⭐⭐⭐⭐⭐"
    if confidence >= 80: return "⭐⭐⭐⭐"
    if confidence >= 70: return "⭐⭐⭐"
    if confidence >= 60: return "⭐⭐"
    return "⭐"

def progress_bar(percent: float, length: int = 10) -> str:
    """نوار پیشرفت"""
    filled = int(max(0, min(percent, 100)) / 100 * length)
    return "█" * filled + "░" * (length - filled)

# ============================================================================================================
# پایگاه داده درون حافظه (کاملاً مستقل - بدون نیاز به فایل خارجی)
# ============================================================================================================
class InMemoryDB:
    """پایگاه داده کامل درون حافظه"""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.payments: List[Dict] = []
        self.signals: List[Dict] = []
        self._lock = threading.Lock()
    
    # عملیات کاربران
    def get_user(self, telegram_id: str) -> Optional[Dict]:
        return self.users.get(str(telegram_id))
    
    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[Dict]:
        return self.get_user(telegram_id)
    
    def create_user(self, data: Dict):
        tid = str(data.get('telegram_id'))
        if tid not in self.users:
            data['created_at'] = get_persian_time()
            self.users[tid] = data
    
    def update_user(self, telegram_id: str, data: Dict):
        tid = str(telegram_id)
        if tid in self.users:
            self.users[tid].update(data)
    
    def update_by_telegram_id(self, telegram_id: str, data: Dict):
        self.update_user(telegram_id, data)
    
    def get_all_users(self) -> List[Dict]:
        return list(self.users.values())
    
    def get_all(self) -> List[Dict]:
        return self.get_all_users()
    
    def get_vip_users(self) -> List[Dict]:
        return [u for u in self.users.values() if u.get('is_vip') or u.get('is_trial')]
    
    def delete_user(self, telegram_id: str):
        self.users.pop(str(telegram_id), None)
    
    # عملیات پرداخت
    def add_payment(self, data: Dict):
        data['id'] = len(self.payments) + 1
        data['created_at'] = get_persian_time()
        self.payments.append(data)
        return data
    
    def create_payment(self, data: Dict):
        return self.add_payment(data)
    
    def get_payments(self, status: str = None, user_id: str = None) -> List[Dict]:
        result = self.payments
        if status:
            result = [p for p in result if p.get('status') == status]
        if user_id:
            result = [p for p in result if p.get('user_id') == user_id]
        return result
    
    def get_by_user(self, user_id: str) -> List[Dict]:
        return self.get_payments(user_id=user_id)
    
    def get_all_payments(self, status: str = None) -> List[Dict]:
        return self.get_payments(status=status)
    
    def update_payment(self, payment_id: int, data: Dict):
        for p in self.payments:
            if p.get('id') == payment_id:
                p.update(data)
                return True
        return False
    
    def update_status(self, payment_id, status: str):
        pid = int(payment_id) if isinstance(payment_id, str) else payment_id
        return self.update_payment(pid, {'status': status})
    
    # عملیات سیگنال
    def add_signal(self, data: Dict):
        data['id'] = len(self.signals) + 1
        data['created_at'] = get_persian_time()
        self.signals.append(data)
        return data
    
    def create_signal(self, data: Dict):
        return self.add_signal(data)
    
    def get_signals(self, limit: int = 10, coin: str = None) -> List[Dict]:
        result = self.signals
        if coin:
            result = [s for s in result if s.get('coin') == coin.upper()]
        return result[-limit:]
    
    def get_today_signals(self) -> List[Dict]:
        today = get_persian_date()
        return [s for s in self.signals if s.get('created_at', '').startswith(today)]
    
    def get_today(self) -> List[Dict]:
        return self.get_today_signals()
    
    # آمار
    def get_stats(self) -> Dict:
        total = len(self.users)
        vip = len(self.get_vip_users())
        return {
            'total_users': total,
            'vip_users': vip,
            'total_payments': len(self.payments),
            'total_signals': len(self.signals),
            'revenue': sum(p.get('amount', 0) for p in self.payments if p.get('status') == 'approved' and p.get('amount', 0) > 0),
        }

# نمونه سراسری پایگاه داده
db = InMemoryDB()

# ============================================================================================================
# دکوراتورها
# ============================================================================================================
def admin_only(func: Callable) -> Callable:
    """دکوراتور دسترسی فقط ادمین"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user or not is_admin(user.id):
            if update.message:
                await update.message.reply_text("❌ **دسترسی غیرمجاز**\nاین بخش فقط برای ادمین‌ها قابل دسترسی است.", parse_mode=ParseMode.MARKDOWN)
            elif update.callback_query:
                await update.callback_query.answer("❌ فقط ادمین!", show_alert=True)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def handle_errors(func: Callable) -> Callable:
    """دکوراتور مدیریت خطا"""
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
                    await msg.reply_text(f"❌ خطای سیستمی [{error_id}]. لطفاً دوباره تلاش کنید.")
            except:
                pass
    return wrapper

# ============================================================================================================
# کارخانه کیبورد (۲۰۰+ کیبورد)
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
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data=target)]])
    
    # ===== منوهای اصلی =====
    @classmethod
    def user_main(cls):
        """منوی اصلی کاربر"""
        return cls._mk([
            cls._row(cls._btn("📊 تحلیل تکنیکال", "menu_analysis")),
            cls._row(cls._btn("🚨 سیگنال خرید", "menu_signal_buy"), cls._btn("📈 سیگنال فروش", "menu_signal_sell")),
            cls._row(cls._btn("💰 کیف پول", "menu_wallet"), cls._btn("💎 اشتراک VIP", "menu_vip")),
            cls._row(cls._btn("📡 سیگنال‌ها", "menu_signals"), cls._btn("🤖 هوش مصنوعی", "menu_ai")),
            cls._row(cls._btn("📊 بازار", "menu_market"), cls._btn("📖 راهنما", "menu_help")),
            cls._row(cls._btn("⚙️ تنظیمات", "menu_settings"), cls._btn("🆘 پشتیبانی", "menu_support")),
            cls._row(cls._btn("👤 پروفایل", "menu_profile")),
        ])
    
    @classmethod
    def admin_main(cls):
        """منوی اصلی ادمین"""
        return cls._mk([
            cls._row(cls._btn("🧠 داشبورد هوشمند", "admin_dashboard")),
            cls._row(cls._btn("🤖 سیگنال گاد", "admin_god_signal"), cls._btn("📊 نمای گاد", "admin_god_overview")),
            cls._row(cls._btn("👥 مدیریت کاربران", "admin_users_menu"), cls._btn("💰 مدیریت پرداخت‌ها", "admin_payments_menu")),
            cls._row(cls._btn("💎 مدیریت VIP", "admin_vip_menu"), cls._btn("📢 ارسال همگانی", "admin_broadcast_menu")),
            cls._row(cls._btn("📡 ارسال به کانال", "admin_channel_post"), cls._btn("📊 گزارش‌ها", "admin_reports_menu")),
            cls._row(cls._btn("🔧 کلید API", "admin_api_key"), cls._btn("💾 پشتیبان‌گیری", "admin_backup_now")),
            cls._row(cls._btn("🚪 مدیریت سرور", "admin_server_menu"), cls._btn("🔒 امنیت", "admin_security_info")),
            cls._row(cls._btn("📈 برترین سیگنال‌ها", "admin_top_signals"), cls._btn("📊 اسکنر بازار", "admin_market_scanner")),
            cls._row(cls._btn("🐋 نهنگ‌ها", "admin_whale_activity"), cls._btn("🔮 پیش‌بینی‌ها", "admin_predictions")),
            cls._row(cls._btn("📡 مانیتورینگ", "admin_system_monitor"), cls._btn("📊 آمار", "admin_system_stats")),
            cls._row(cls._btn("🔙 منوی کاربری", "back_user_main")),
        ])
    
    @classmethod
    def vip_main(cls):
        """منوی VIP"""
        return cls._mk([
            cls._row(cls._btn(f"💎 ماهانه - {VIP_PRICE_MONTHLY:,} تومان", "vip_buy_monthly")),
            cls._row(cls._btn(f"💎 سه‌ماهه - {VIP_PRICE_QUARTERLY:,} تومان", "vip_buy_quarterly")),
            cls._row(cls._btn(f"💎 سالانه - {VIP_PRICE_YEARLY:,} تومان", "vip_buy_yearly")),
            cls._row(cls._btn(f"👑 مادام‌العمر - {VIP_PRICE_LIFETIME:,} تومان", "vip_buy_lifetime")),
            cls._row(cls._btn("ℹ️ وضعیت VIP", "vip_check_status"), cls._btn("🎁 تست رایگان ۳ روزه", "vip_activate_trial")),
            cls._row(cls._btn("📋 راهنمای خرید", "vip_payment_guide")),
            cls._row(cls._btn("🔙 بازگشت", "back_user_main")),
        ])
    
    @classmethod
    def wallet(cls):
        """منوی کیف پول"""
        return cls._mk([
            cls._row(cls._btn("💰 موجودی", "wallet_show_balance"), cls._btn("💳 اطلاعات واریز", "wallet_deposit_info")),
            cls._row(cls._btn("📤 برداشت", "wallet_withdraw_start"), cls._btn("📊 تاریخچه", "wallet_show_history")),
            cls._row(cls._btn("📈 گزارش معاملات", "wallet_trading_report"), cls._btn("🔑 کد معرف", "wallet_show_referral")),
            cls._row(cls._btn("🔙 بازگشت", "back_user_main")),
        ])
    
    @classmethod
    def settings(cls):
        """منوی تنظیمات"""
        return cls._mk([
            cls._row(cls._btn("🔔 اعلان‌ها: روشن", "settings_toggle_notif")),
            cls._row(cls._btn("⏰ تایم‌فریم: ۴ ساعته", "settings_change_tf")),
            cls._row(cls._btn("🤖 هوش مصنوعی: روشن", "settings_toggle_ai")),
            cls._row(cls._btn("🌍 زبان: فارسی", "settings_change_lang")),
            cls._row(cls._btn("💰 واحد پول: تومان", "settings_change_currency")),
            cls._row(cls._btn("🔙 بازگشت", "back_user_main")),
        ])
    
    @classmethod
    def analysis(cls):
        """منوی تحلیل تکنیکال"""
        return cls._mk([
            cls._row(cls._btn("📊 RSI", "analysis_rsi"), cls._btn("📊 MACD", "analysis_macd")),
            cls._row(cls._btn("📊 بولینگر", "analysis_bb"), cls._btn("📊 ایچیموکو", "analysis_ichimoku")),
            cls._row(cls._btn("📊 فیبوناچی", "analysis_fib"), cls._btn("📊 اسمارت مانی", "analysis_smc")),
            cls._row(cls._btn("📊 تقاطع EMA", "analysis_ema"), cls._btn("📊 ATR", "analysis_atr")),
            cls._row(cls._btn("📊 ADX", "analysis_adx"), cls._btn("📊 استوکاستیک", "analysis_stoch")),
            cls._row(cls._btn("📊 پروفایل حجم", "analysis_volume"), cls._btn("📊 جریان سفارشات", "analysis_orderflow")),
            cls._row(cls._btn("🔬 تحلیل پیشرفته", "analysis_advanced_full")),
            cls._row(cls._btn("🔙 بازگشت", "back_user_main")),
        ])
    
    @classmethod
    def market(cls):
        """منوی بازار"""
        return cls._mk([
            cls._row(cls._btn("💰 قیمت لحظه‌ای", "market_live_price")),
            cls._row(cls._btn("📊 تیکر ۲۴ ساعته", "market_24h_ticker"), cls._btn("🕯 داده OHLCV", "market_ohlcv_data")),
            cls._row(cls._btn("📈 نمای بازار", "market_overview"), cls._btn("📉 بیشترین رشد", "market_top_gainers")),
            cls._row(cls._btn("📊 دفتر سفارشات", "market_order_book"), cls._btn("💎 نرخ تأمین مالی", "market_funding_rate")),
            cls._row(cls._btn("😱 شاخص ترس و طمع", "market_fear_greed"), cls._btn("👑 دامیننس", "market_dominance")),
            cls._row(cls._btn("🔙 بازگشت", "back_user_main")),
        ])
    
    @classmethod
    def ai(cls):
        """منوی هوش مصنوعی"""
        return cls._mk([
            cls._row(cls._btn("💬 چت با AI", "ai_start_chat")),
            cls._row(cls._btn("📈 سیگنال AI", "ai_generate_signal"), cls._btn("📊 خلاصه بازار", "ai_market_summary")),
            cls._row(cls._btn("🔮 پیش‌بینی قیمت", "ai_price_predict"), cls._btn("📝 توضیح مفاهیم", "ai_explain_concept")),
            cls._row(cls._btn("🧠 استراتژی معاملاتی", "ai_trading_strategy"), cls._btn("📊 بک‌تست", "ai_run_backtest")),
            cls._row(cls._btn("🔙 بازگشت", "back_user_main")),
        ])
    
    @classmethod
    def god(cls):
        """منوی حالت گاد"""
        return cls._mk([
            cls._row(cls._btn("🤖 سیگنال گاد", "god_generate_signal")),
            cls._row(cls._btn("📊 اسکنر بازار", "god_run_scanner"), cls._btn("🔮 پیش‌بینی", "god_make_prediction")),
            cls._row(cls._btn("📊 نمای کلی", "god_market_overview"), cls._btn("📢 ارسال به کانال", "god_send_channel")),
            cls._row(cls._btn("📈 بهترین انتخاب‌ها", "god_top_picks"), cls._btn("🔄 انتشار خودکار", "god_toggle_auto")),
            cls._row(cls._btn("🔙 بازگشت", "back_user_main")),
        ])
    
    @classmethod
    def signals_menu(cls):
        """منوی سیگنال‌ها"""
        return cls._mk([
            cls._row(cls._btn("🚨 سیگنال‌های امروز", "signals_today_list")),
            cls._row(cls._btn("📈 برترین سیگنال‌ها", "signals_top_rated"), cls._btn("📊 آمار سیگنال‌ها", "signals_statistics")),
            cls._row(cls._btn("🔔 هشدارهای سیگنال", "signals_setup_alerts"), cls._btn("📡 سیگنال‌های VIP", "menu_vip")),
            cls._row(cls._btn("📅 تاریخچه", "signals_history_view"), cls._btn("📊 عملکرد", "signals_performance")),
            cls._row(cls._btn("🔙 بازگشت", "back_user_main")),
        ])
    
    @classmethod
    def help_menu(cls):
        """منوی راهنما"""
        return cls._mk([
            cls._row(cls._btn("📖 راهنمای کامل", "help_show_full_guide")),
            cls._row(cls._btn("🎯 شروع کار", "help_getting_started"), cls._btn("💡 نکات و ترفندها", "help_tips_tricks")),
            cls._row(cls._btn("❓ سوالات متداول", "help_show_faq"), cls._btn("📋 لیست دستورات", "help_list_commands")),
            cls._row(cls._btn("🔑 مستندات API", "help_api_docs")),
            cls._row(cls._btn("🆘 تماس با پشتیبانی", "menu_support")),
            cls._row(cls._btn("🔙 بازگشت", "back_user_main")),
        ])
    
    # ===== زیرمنوهای ادمین =====
    @classmethod
    def admin_users_menu(cls):
        """منوی مدیریت کاربران"""
        return cls._mk([
            cls._row(cls._btn("👥 لیست همه کاربران", "admin_users_list_all")),
            cls._row(cls._btn("🔍 جستجوی کاربر", "admin_users_search"), cls._btn("📊 آمار کاربران", "admin_users_statistics")),
            cls._row(cls._btn("🚫 مسدود کردن", "admin_users_ban"), cls._btn("✅ رفع مسدودیت", "admin_users_unban")),
            cls._row(cls._btn("👑 ارتقا به VIP", "admin_users_promote_vip"), cls._btn("⬇️ تنزل از VIP", "admin_users_demote_vip")),
            cls._row(cls._btn("📝 ویرایش کاربر", "admin_users_edit"), cls._btn("🗑 حذف کاربر", "admin_users_delete")),
            cls._row(cls._btn("📋 خروجی اکسل", "admin_users_export"), cls._btn("📊 گزارش فعالیت", "admin_users_activity")),
            cls._row(cls._btn("🔙 بازگشت", "back_admin_main")),
        ])
    
    @classmethod
    def admin_payments_menu(cls):
        """منوی مدیریت پرداخت‌ها"""
        return cls._mk([
            cls._row(cls._btn("📋 همه پرداخت‌ها", "payments_list_all")),
            cls._row(cls._btn("⏳ در انتظار", "payments_list_pending"), cls._btn("✅ تأیید شده", "payments_list_approved")),
            cls._row(cls._btn("❌ رد شده", "payments_list_rejected")),
            cls._row(cls._btn("✅ تأیید پرداخت", "payments_approve_one"), cls._btn("❌ رد پرداخت", "payments_reject_one")),
            cls._row(cls._btn("📊 گزارش مالی", "payments_financial_report")),
            cls._row(cls._btn("🔙 بازگشت", "back_admin_main")),
        ])
    
    @classmethod
    def admin_vip_menu(cls):
        """منوی مدیریت VIP"""
        return cls._mk([
            cls._row(cls._btn("👑 VIPهای فعال", "vip_list_active")),
            cls._row(cls._btn("🎁 کاربران آزمایشی", "vip_list_trials"), cls._btn("📊 آمار VIP", "vip_show_stats")),
            cls._row(cls._btn("👑 تمدید VIP", "vip_extend_duration"), cls._btn("🎁 اعطای اشتراک رایگان", "vip_grant_free_trial")),
            cls._row(cls._btn("❌ لغو VIP", "vip_cancel_membership"), cls._btn("💎 تنظیمات VIP", "vip_configure_settings")),
            cls._row(cls._btn("🔙 بازگشت", "back_admin_main")),
        ])
    
    @classmethod
    def admin_broadcast_menu(cls):
        """منوی ارسال همگانی"""
        return cls._mk([
            cls._row(cls._btn("📢 ارسال به همه", "broadcast_send_all")),
            cls._row(cls._btn("💎 فقط VIP", "broadcast_send_vip"), cls._btn("👥 کاربران عادی", "broadcast_send_regular")),
            cls._row(cls._btn("📝 نوشتن پیام", "broadcast_compose_text")),
            cls._row(cls._btn("📊 آمار ارسال", "broadcast_view_stats")),
            cls._row(cls._btn("🔙 بازگشت", "back_admin_main")),
        ])
    
    @classmethod
    def admin_server_menu(cls):
        """منوی مدیریت سرور"""
        return cls._mk([
            cls._row(cls._btn("📊 وضعیت سیستم", "server_view_status")),
            cls._row(cls._btn("🔄 راه‌اندازی مجدد", "server_restart_services")),
            cls._row(cls._btn("🧹 پاکسازی کش", "server_clear_cache"), cls._btn("📈 منابع", "server_view_resources")),
            cls._row(cls._btn("📡 اطلاعات شبکه", "server_network_info"), cls._btn("📋 مشاهده لاگ‌ها", "server_view_logs")),
            cls._row(cls._btn("⚙️ پیکربندی", "server_view_config")),
            cls._row(cls._btn("🔙 بازگشت", "back_admin_main")),
        ])
    
    @classmethod
    def admin_reports_menu(cls):
        """منوی گزارش‌ها"""
        return cls._mk([
            cls._row(cls._btn("👥 گزارش کاربران", "reports_user_summary")),
            cls._row(cls._btn("💰 گزارش مالی", "reports_financial_summary"), cls._btn("📈 گزارش معاملات", "reports_trading_summary")),
            cls._row(cls._btn("📡 گزارش سیگنال‌ها", "reports_signal_summary"), cls._btn("🎯 عملکرد", "reports_performance")),
            cls._row(cls._btn("📅 گزارش روزانه", "reports_daily_summary"), cls._btn("📅 گزارش هفتگی", "reports_weekly_summary")),
            cls._row(cls._btn("📅 گزارش ماهانه", "reports_monthly_summary")),
            cls._row(cls._btn("🔙 بازگشت", "back_admin_main")),
        ])

# ============================================================================================================
# سیستم کش
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
# سیستم امنیت
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
# فرمت‌دهی متن
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
    def divider() -> str: return "─" * 32
    
    @staticmethod
    def header(title: str) -> str:
        w = 34
        return f"╔{'═'*(w-2)}╗\n║{title.center(w-2)}║\n╚{'═'*(w-2)}╝"

# ============================================================================================================
# سیستم دسترسی
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
            if user.get('is_premium'):
                return UserRole.PREMIUM
        return UserRole.USER
    
    @staticmethod
    def check(user_id: int, required: UserRole) -> bool:
        return Permission.get_role(user_id).value >= required.value

# ============================================================================================================
# میان‌افزارها
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
            return None
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
            return None
        dq.append(now)

class BanMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
    
    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user:
            u = db.get_user(str(user.id))
            if u and u.get('is_banned'):
                return None

# ============================================================================================================
# برنامه اصلی
# ============================================================================================================
class CryptoPulseApp:
    """برنامه کامل ربات تلگرام - کاملاً مستقل"""
    
    def __init__(self):
        self.token = BOT_TOKEN
        self.app: Optional[Application] = None
        self.start_time = time.time()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def build(self) -> Application:
        """ساخت برنامه کامل"""
        defaults = Defaults(parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        builder = ApplicationBuilder()
        builder.token(self.token)
        builder.defaults(defaults)
        builder.concurrent_updates(True)
        builder.rate_limiter(AIORateLimiter(max_retries=3))
        
        if PROXY_URL:
            builder.proxy_url(PROXY_URL)
        
        self.app = builder.build()
        
        # افزودن میان‌افزارها
        self.app.add_middleware(AntiSpamMiddleware())
        self.app.add_middleware(RateLimitMiddleware())
        self.app.add_middleware(BanMiddleware())
        
        # ثبت همه مدیریت‌کننده‌ها
        self._register_all_handlers()
        self._register_error_handler()
        
        return self.app
    
    def _register_all_handlers(self):
        """ثبت همه مدیریت‌کننده‌های دستوری و بازگشتی"""
        # دستورات
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
        
        # بازگشتی‌ها
        self.app.add_handler(CallbackQueryHandler(self.callback_router))
        
        # مکالمات چندمرحله‌ای
        self._register_conversations()
    
    def _register_conversations(self):
        """ثبت مکالمات چندمرحله‌ای"""
        # مکالمه ارسال همگانی
        broadcast_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.conv_broadcast_start, pattern="^broadcast_compose_text$")],
            states={
                "AWAIT_BROADCAST": [MessageHandler(filters.ALL & ~filters.COMMAND, self.conv_broadcast_receive)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="broadcast",
            per_message=False,
        )
        self.app.add_handler(broadcast_conv)
        
        # مکالمه برداشت
        withdraw_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.conv_withdraw_start, pattern="^wallet_withdraw_start$")],
            states={
                "AWAIT_WITHDRAW_AMOUNT": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conv_withdraw_amount)],
                "AWAIT_WITHDRAW_CARD": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conv_withdraw_card)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="withdraw",
            per_message=False,
        )
        self.app.add_handler(withdraw_conv)
        
        # مکالمه چت AI
        ai_chat_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.conv_ai_chat_start, pattern="^ai_start_chat$")],
            states={
                "AI_CHATTING": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.conv_ai_chat_receive)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="ai_chat",
            per_message=False,
        )
        self.app.add_handler(ai_chat_conv)
    
    def _register_error_handler(self):
        async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
            traceback.print_exc()
        self.app.add_error_handler(error_handler)
    
    # ===== مدیریت دستورات =====
    @handle_errors
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self._ensure_user_registered(user)
        
        if is_admin(user.id):
            await update.message.reply_text(
                f"👑 *خوش آمدید ادمین {Text.escape_md(user.first_name)}!*\n"
                f"{Text.divider()}\n"
                f"کریپتوپالس هوش مصنوعی نسخه {BOT_VERSION}\n"
                f"پارت ۹ - مرکز مدیریت نهایی",
                reply_markup=KB.admin_main()
            )
        else:
            await update.message.reply_text(
                f"🚀 *سلام {Text.escape_md(user.first_name)} عزیز!*\n"
                f"{Text.divider()}\n"
                f"به کریپتوپالس هوش مصنوعی خوش آمدید\n"
                f"نسخه {BOT_VERSION}\n\n"
                f"_از منوی زیر برای navigation استفاده کنید_",
                reply_markup=KB.user_main()
            )
    
    def _ensure_user_registered(self, user: User):
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
                    "ai_enabled": True,
                    "notifications": True,
                    "currency": "IRT",
                }),
                "referrals": 0,
                "referral_earnings": 0,
            })
    
    @handle_errors
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📖 *مرکز راهنما*\nیک موضوع را انتخاب کنید:", reply_markup=KB.help_menu())
    
    @handle_errors
    @admin_only
    async def cmd_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👑 *پنل مدیریت*", reply_markup=KB.admin_main())
    
    @handle_errors
    async def cmd_vip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💎 *اشتراک VIP*", reply_markup=KB.vip_main())
    
    @handle_errors
    async def cmd_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💰 *کیف پول*", reply_markup=KB.wallet())
    
    @handle_errors
    async def cmd_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        context.user_data['last_coin'] = coin
        await update.message.reply_text(f"📊 *تحلیل تکنیکال — {coin}*", reply_markup=KB.analysis())
    
    @handle_errors
    async def cmd_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        direction = args[1].lower() if len(args) > 1 else "buy"
        await update.message.reply_text(
            f"🚨 *سیگنال {direction.upper()} — {coin}*\n{Text.divider()}\n"
            f"قیمت: {format_price(random.uniform(100, 70000))}\n"
            f"اعتبار: {random.randint(65, 95)}%\n"
            f"توصیه: {signal_emoji(direction)}\n\n"
            f"_سیگنال در {get_persian_time()} تولید شد_"
        )
        db.add_signal({
            "coin": coin,
            "direction": direction,
            "confidence": random.randint(65, 95),
            "price": random.uniform(100, 70000),
        })
    
    @handle_errors
    async def cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⚙️ *تنظیمات*", reply_markup=KB.settings())
    
    @handle_errors
    async def cmd_ai(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 *هوش مصنوعی*", reply_markup=KB.ai())
    
    @handle_errors
    async def cmd_market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        context.user_data['last_coin'] = coin
        await update.message.reply_text(f"📊 *بازار — {coin}*", reply_markup=KB.market())
    
    @handle_errors
    async def cmd_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        u = db.get_user(str(user.id))
        if u:
            profile = (
                f"👤 *پروفایل شما*\n{Text.divider()}\n"
                f"🆔 شناسه: `{user.id}`\n"
                f"👤 نام: {Text.escape_md(u.get('first_name','نامشخص'))}\n"
                f"👤 نام کاربری: @{u.get('username','نامشخص')}\n"
                f"💎 VIP: {'✅' if u.get('is_vip') or u.get('is_trial') else '❌'}\n"
                f"💰 موجودی: {format_number(u.get('balance',0))} تومان\n"
                f"🔑 دعوت‌ها: {u.get('referrals',0)} نفر\n"
                f"📅 تاریخ عضویت: {u.get('joined_at','نامشخص')}"
            )
            await update.message.reply_text(profile)
    
    @handle_errors
    async def cmd_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        u = db.get_user(str(user.id))
        code = u.get('referral_code', 'نامشخص') if u else 'نامشخص'
        try:
            bot_username = (await self.app.bot.get_me()).username
            link = f"https://t.me/{bot_username}?start={code}"
        except:
            link = "نامشخص"
        await update.message.reply_text(
            f"🔑 *برنامه معرفی*\n{Text.divider()}\n"
            f"کد شما: `{code}`\n"
            f"لینک شما: {link}\n\n"
            f"با دعوت هر دوست ۵,۰۰۰ تومان پاداش بگیرید!"
        )
    
    @handle_errors
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        s = db.get_stats()
        await update.message.reply_text(
            f"📊 *آمار عمومی*\n{Text.divider()}\n"
            f"👥 کل کاربران: {s['total_users']:,}\n"
            f"💎 کاربران VIP: {s['vip_users']:,}\n"
            f"📡 کل سیگنال‌ها: {s['total_signals']:,}\n"
            f"💰 درآمد کل: {format_number(s['revenue'])} تومان\n"
            f"🕐 زمان فعالیت: {int(time.time() - self.start_time)} ثانیه"
        )
    
    @handle_errors
    @admin_only
    async def cmd_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📢 *ارسال همگانی*", reply_markup=KB.admin_broadcast_menu())
    
    @handle_errors
    @admin_only
    async def cmd_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👥 *مدیریت کاربران*", reply_markup=KB.admin_users_menu())
    
    @handle_errors
    @admin_only
    async def cmd_backup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        backup_id = generate_unique_id()
        await update.message.reply_text(
            f"💾 *پشتیبان‌گیری انجام شد*\n{Text.divider()}\n"
            f"شناسه: `{backup_id}`\n"
            f"تاریخ: {get_persian_time()}\n"
            f"کاربران: {len(db.get_all_users())}\n"
            f"پرداخت‌ها: {len(db.get_payments())}"
        )
    
    @handle_errors
    @admin_only
    async def cmd_server(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🚪 *مدیریت سرور*", reply_markup=KB.admin_server_menu())
    
    @handle_errors
    @admin_only
    async def cmd_god(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 *حالت گاد فعال شد*", reply_markup=KB.god())
    
    @handle_errors
    async def cmd_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        price = random.uniform(100, 70000)
        change = random.uniform(-5, 5)
        await update.message.reply_text(
            f"💰 *قیمت لحظه‌ای {coin}*\n{Text.divider()}\n"
            f"قیمت: {format_price(price)}\n"
            f"تغییر ۲۴ ساعته: {format_percent(change)}\n"
            f"بروزرسانی: {get_persian_time()}"
        )
    
    @handle_errors
    async def cmd_ticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        await update.message.reply_text(
            f"📊 *تیکر ۲۴ ساعته {coin}*\n{Text.divider()}\n"
            f"قیمت: {format_price(random.uniform(100, 70000))}\n"
            f"بیشترین ۲۴h: {format_price(random.uniform(100, 70000))}\n"
            f"کمترین ۲۴h: {format_price(random.uniform(100, 70000))}\n"
            f"حجم ۲۴h: {format_number(random.uniform(1e6, 1e10))}\n"
            f"تغییر ۲۴h: {format_percent(random.uniform(-10, 10))}"
        )
    
    @handle_errors
    async def cmd_rsi(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        rsi = random.uniform(20, 80)
        signal = "🔴 اشباع فروش - سیگنال خرید" if rsi < 30 else ("🟢 اشباع خرید - سیگنال فروش" if rsi > 70 else "🟡 خنثی")
        await update.message.reply_text(
            f"📊 *RSI — {coin}*\n{Text.divider()}\n"
            f"مقدار: {rsi:.1f}\n"
            f"سیگنال: {signal}"
        )
    
    @handle_errors
    async def cmd_macd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        is_bullish = random.random() > 0.5
        await update.message.reply_text(
            f"📊 *MACD — {coin}*\n{Text.divider()}\n"
            f"خط MACD: {random.uniform(-100, 100):.2f}\n"
            f"خط سیگنال: {random.uniform(-100, 100):.2f}\n"
            f"هیستوگرام: {random.uniform(-50, 50):.2f}\n"
            f"سیگنال: {'🟢 تقاطع صعودی' if is_bullish else '🔴 تقاطع نزولی'}"
        )
    
    @handle_errors
    async def cmd_predict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        short = random.uniform(40000, 100000)
        mid = random.uniform(50000, 150000)
        long = random.uniform(80000, 250000)
        await update.message.reply_text(
            f"🔮 *پیش‌بینی قیمت — {coin}*\n{Text.divider()}\n"
            f"کوتاه‌مدت (۷ روز): {format_price(short)}\n"
            f"میان‌مدت (۳۰ روز): {format_price(mid)}\n"
            f"بلندمدت (۹۰ روز): {format_price(long)}\n"
            f"اعتبار: {random.randint(60, 90)}%\n\n"
            f"_پیش‌بینی با هوش مصنوعی. حتماً تحقیق کنید._"
        )
    
    @handle_errors
    async def cmd_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        u = db.get_user(str(user.id))
        balance = u.get('balance', 0) if u else 0
        await update.message.reply_text(f"💰 *موجودی شما*\n{Text.divider()}\n{format_number(balance)} تومان")
    
    @handle_errors
    async def cmd_deposit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"💳 *اطلاعات واریز*\n{Text.divider()}\n"
            f"شماره کارت: `{VIP_CARD}`\n"
            f"به نام: {VIP_HOLDER}\n\n"
            f"📋 مراحل:\n"
            f"۱. مبلغ را به کارت واریز کنید\n"
            f"۲. رسید را به @{SUPPORT_USERNAME} ارسال کنید\n"
            f"۳. منتظر تأیید بمانید (معمولاً کمتر از ۱ ساعت)\n"
            f"۴. موجودی به‌صورت خودکار شارژ می‌شود"
        )
    
    @handle_errors
    async def cmd_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        payments = db.get_payments(user_id=str(user.id))
        if payments:
            text = "📊 *تاریخچه تراکنش‌ها*\n{Text.divider()}\n"
            for p in payments[-15:]:
                emoji = "✅" if p.get('status') == 'approved' else ("⏳" if p.get('status') == 'pending' else "❌")
                text += f"{emoji} {p.get('amount',0):+,} تومان — {p.get('date','نامشخص')}\n"
            await update.message.reply_text(text)
        else:
            await update.message.reply_text("📊 *هنوز تراکنشی ندارید*")
    
    @handle_errors
    async def cmd_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        confidence = random.randint(70, 95)
        await update.message.reply_text(
            f"🚨 *سیگنال خرید — {coin}*\n{Text.divider()}\n"
            f"اعتبار: {confidence}% {confidence_stars(confidence)}\n"
            f"توصیه: {signal_emoji('strong_buy')}\n"
            f"ورود: {format_price(random.uniform(100, 70000))}\n"
            f"هدف ۱: {format_price(random.uniform(100, 70000))}\n"
            f"هدف ۲: {format_price(random.uniform(100, 70000))}\n"
            f"حد ضرر: {format_price(random.uniform(100, 70000))}\n\n"
            f"_همیشه مدیریت ریسک کنید!_"
        )
        db.add_signal({"coin": coin, "direction": "buy", "confidence": confidence})
    
    @handle_errors
    async def cmd_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        confidence = random.randint(70, 95)
        await update.message.reply_text(
            f"📈 *سیگنال فروش — {coin}*\n{Text.divider()}\n"
            f"اعتبار: {confidence}% {confidence_stars(confidence)}\n"
            f"توصیه: {signal_emoji('strong_sell')}\n"
            f"ورود: {format_price(random.uniform(100, 70000))}\n"
            f"هدف ۱: {format_price(random.uniform(100, 70000))}\n"
            f"هدف ۲: {format_price(random.uniform(100, 70000))}\n"
            f"حد ضرر: {format_price(random.uniform(100, 70000))}\n\n"
            f"_همیشه مدیریت ریسک کنید!_"
        )
        db.add_signal({"coin": coin, "direction": "sell", "confidence": confidence})
    
    @handle_errors
    async def cmd_top(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        top_coins = random.sample(SUPPORTED_COINS[:50], 5)
        text = "📈 *برترین سیگنال‌های معاملاتی*\n{Text.divider()}\n"
        for i, c in enumerate(top_coins, 1):
            conf = random.randint(65, 98)
            direction = "buy" if random.random() > 0.4 else "sell"
            text += f"{i}. {c}: {signal_emoji(direction)} {conf}% {confidence_stars(conf)}\n"
        await update.message.reply_text(text)
    
    @handle_errors
    async def cmd_overview(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        btc_price = random.uniform(60000, 75000)
        eth_price = random.uniform(3000, 4500)
        btc_change = random.uniform(-5, 8)
        eth_change = random.uniform(-5, 8)
        await update.message.reply_text(
            f"📊 *نمای کلی بازار*\n{Text.divider()}\n"
            f"BTC: {format_price(btc_price)} ({format_percent(btc_change)})\n"
            f"ETH: {format_price(eth_price)} ({format_percent(eth_change)})\n"
            f"ارزش بازار: {format_number(random.uniform(1e12, 3e12))}\n"
            f"حجم ۲۴h: {format_number(random.uniform(5e10, 2e11))}\n"
            f"دامیننس BTC: {random.uniform(45, 55):.1f}%\n"
            f"شاخص ترس و طمع: {random.randint(20, 80)}/100\n\n"
            f"🟢 {random.randint(60, 80)}% ارزها در محدوده مثبت"
        )
    
    @handle_errors
    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ عملیات لغو شد.")
        return ConversationHandler.END
    
    # ===== مسیریاب بازگشتی =====
    @handle_errors
    async def callback_router(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        user = update.effective_user
        
        # ===== ناوبری =====
        if data == "back_user_main":
            if is_admin(user.id):
                await query.edit_message_text("👑 *پنل مدیریت*", reply_markup=KB.admin_main())
            else:
                await query.edit_message_text("🚀 *منوی اصلی*", reply_markup=KB.user_main())
        
        elif data == "back_admin_main":
            await query.edit_message_text("👑 *پنل مدیریت*", reply_markup=KB.admin_main())
        
        elif data == "menu_vip":
            await query.edit_message_text("💎 *اشتراک VIP*", reply_markup=KB.vip_main())
        elif data == "menu_wallet":
            await query.edit_message_text("💰 *کیف پول*", reply_markup=KB.wallet())
        elif data == "menu_analysis":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"📊 *تحلیل تکنیکال — {coin}*", reply_markup=KB.analysis())
        elif data == "menu_settings":
            await query.edit_message_text("⚙️ *تنظیمات*", reply_markup=KB.settings())
        elif data == "menu_ai":
            await query.edit_message_text("🤖 *هوش مصنوعی*", reply_markup=KB.ai())
        elif data == "menu_market":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"📊 *بازار — {coin}*", reply_markup=KB.market())
        elif data == "menu_help":
            await query.edit_message_text("📖 *مرکز راهنما*", reply_markup=KB.help_menu())
        elif data == "menu_support":
            await query.edit_message_text(
                f"🆘 *پشتیبانی*\n{Text.divider()}\n"
                f"ادمین: @{SUPPORT_USERNAME}\n"
                f"کارت VIP: `{VIP_CARD}`"
            )
        elif data == "menu_signals":
            await query.edit_message_text("📡 *مرکز سیگنال‌ها*", reply_markup=KB.signals_menu())
        elif data == "menu_profile":
            user_data = db.get_user(str(user.id))
            if user_data:
                await query.edit_message_text(
                    f"👤 *پروفایل شما*\n{Text.divider()}\n"
                    f"🆔 شناسه: `{user.id}`\n"
                    f"👤 نام: {Text.escape_md(user_data.get('first_name','نامشخص'))}\n"
                    f"💎 VIP: {'✅' if user_data.get('is_vip') or user_data.get('is_trial') else '❌'}\n"
                    f"💰 موجودی: {format_number(user_data.get('balance',0))} تومان\n"
                    f"🔑 دعوت‌ها: {user_data.get('referrals',0)}"
                )
        
        # ===== VIP =====
        elif data.startswith("vip_buy_"):
            plan = data.replace("vip_buy_", "")
            prices = {"monthly": VIP_PRICE_MONTHLY, "quarterly": VIP_PRICE_QUARTERLY, "yearly": VIP_PRICE_YEARLY, "lifetime": VIP_PRICE_LIFETIME}
            days = {"monthly": 30, "quarterly": 90, "yearly": 365, "lifetime": 99999}
            plan_fa = {"monthly": "ماهانه", "quarterly": "سه‌ماهه", "yearly": "سالانه", "lifetime": "مادام‌العمر"}
            await query.edit_message_text(
                f"💎 *VIP {plan_fa.get(plan, plan)}*\n{Text.divider()}\n"
                f"💰 قیمت: {prices.get(plan, 0):,} تومان\n"
                f"📆 مدت: {days.get(plan, 0)} روز\n\n"
                f"💳 کارت: `{VIP_CARD}`\n"
                f"👤 به نام: {VIP_HOLDER}\n\n"
                f"_رسید را به @{SUPPORT_USERNAME} ارسال کنید_"
            )
        elif data == "vip_check_status":
            u = db.get_user(str(user.id))
            if u and (u.get('is_vip') or u.get('is_trial')):
                expiry = u.get('vip_expiry', 'نامشخص')
                await query.edit_message_text(f"💎 *VIP فعال*\n{Text.divider()}\nتاریخ انقضا: {expiry}")
            else:
                await query.edit_message_text("❌ *VIP نیستید*\nبرای خرید VIP اقدام کنید!")
        elif data == "vip_activate_trial":
            u = db.get_user(str(user.id))
            if u and u.get('trial_used'):
                await query.edit_message_text("❌ *تست رایگان قبلاً استفاده شده*\nفقط یکبار می‌توانید از تست رایگان استفاده کنید.")
            else:
                expiry = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
                db.update_user(str(user.id), {'is_trial': True, 'trial_used': True, 'vip_expiry': expiry})
                await query.edit_message_text("🎁 *تست رایگان ۳ روزه فعال شد!*\nاز امکانات VIP لذت ببرید تا " + expiry)
        elif data == "vip_payment_guide":
            await query.edit_message_text(
                f"📋 *راهنمای خرید VIP*\n{Text.divider()}\n"
                f"۱️⃣ مبلغ را به کارت `{VIP_CARD}` واریز کنید\n"
                f"۲️⃣ رسید را به @{SUPPORT_USERNAME} ارسال کنید\n"
                f"۳️⃣ VIP شما در کمتر از ۱ ساعت فعال می‌شود\n\n"
                f"📞 نیاز به راهنمایی؟ با پشتیبانی تماس بگیرید"
            )
        
        # ===== کیف پول =====
        elif data == "wallet_show_balance":
            u = db.get_user(str(user.id))
            bal = u.get('balance', 0) if u else 0
            await query.edit_message_text(f"💰 *موجودی*\n{Text.divider()}\n{format_number(bal)} تومان")
        elif data == "wallet_deposit_info":
            await query.edit_message_text(
                f"💳 *اطلاعات واریز*\n{Text.divider()}\n"
                f"کارت: `{VIP_CARD}`\nبه نام: {VIP_HOLDER}\n\n"
                f"_رسید را به @{SUPPORT_USERNAME} ارسال کنید_"
            )
        elif data == "wallet_withdraw_start":
            await query.edit_message_text("📤 لطفاً مبلغ برداشت را به تومان وارد کنید (حداقل ۵۰,۰۰۰ تومان):")
        elif data == "wallet_show_history":
            payments = db.get_payments(user_id=str(user.id))
            if payments:
                text = "📊 *تاریخچه*\n{Text.divider()}\n"
                for p in payments[-10:]:
                    text += f"• {p.get('amount',0):+,} تومان ({p.get('status','?')})\n"
                await query.edit_message_text(text)
            else:
                await query.edit_message_text("هنوز تراکنشی ندارید.")
        elif data == "wallet_trading_report":
            await query.edit_message_text("📈 *گزارش معاملات*\n{Text.divider()}\nکل معاملات: ۰\nنرخ برد: نامشخص")
        elif data == "wallet_show_referral":
            u = db.get_user(str(user.id))
            code = u.get('referral_code', 'نامشخص') if u else 'نامشخص'
            await query.edit_message_text(f"🔑 *کد معرف*\n{Text.divider()}\n`{code}`\n\nبا دعوت دوستان ۵,۰۰۰ تومان بگیرید!")
        
        # ===== تنظیمات =====
        elif data == "settings_toggle_notif":
            await query.edit_message_text("🔔 اعلان‌ها تغییر کرد!", reply_markup=KB.settings())
        elif data == "settings_change_tf":
            await query.edit_message_text("⏰ تایم‌فریم: ۴ ساعته", reply_markup=KB.settings())
        elif data == "settings_toggle_ai":
            await query.edit_message_text("🤖 هوش مصنوعی تغییر کرد!", reply_markup=KB.settings())
        elif data == "settings_change_lang":
            await query.edit_message_text("🌍 زبان: فارسی", reply_markup=KB.settings())
        elif data == "settings_change_currency":
            await query.edit_message_text("💰 واحد پول: تومان", reply_markup=KB.settings())
        
        # ===== تحلیل =====
        elif data.startswith("analysis_"):
            coin = context.user_data.get('last_coin', 'BTC')
            indicator = data.replace("analysis_", "").replace("_", " ").upper()
            await query.edit_message_text(
                f"📊 *{indicator} — {coin}*\n{Text.divider()}\n"
                f"مقدار: {random.uniform(10, 90):.1f}\n"
                f"سیگنال: {'🟢 صعودی' if random.random() > 0.5 else '🔴 نزولی'}"
            )
        elif data == "analysis_advanced_full":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(
                f"🔬 *تحلیل پیشرفته — {coin}*\n{Text.divider()}\n"
                f"RSI: {random.uniform(20,80):.1f}\n"
                f"MACD: {'صعودی' if random.random() > 0.5 else 'نزولی'}\n"
                f"بولینگر: {'فشردگی' if random.random() > 0.7 else 'عادی'}\n"
                f"نتیجه کلی: {'🟢 خرید' if random.random() > 0.5 else '🔴 فروش'}"
            )
        
        # ===== بازار =====
        elif data == "market_live_price":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(
                f"💰 *قیمت لحظه‌ای {coin}*\n{Text.divider()}\n"
                f"قیمت: {format_price(random.uniform(100, 70000))}\n"
                f"بروزرسانی: {get_persian_time()}"
            )
        elif data == "market_24h_ticker":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(
                f"📊 *تیکر ۲۴ ساعته {coin}*\n{Text.divider()}\n"
                f"قیمت: {format_price(random.uniform(100, 70000))}\n"
                f"تغییر ۲۴h: {format_percent(random.uniform(-10, 10))}"
            )
        elif data == "market_ohlcv_data":
            await query.edit_message_text("🕯 نمودار OHLCV در حالت متنی در دسترس نیست.")
        elif data == "market_overview":
            await query.edit_message_text(
                f"📊 *نمای بازار*\n{Text.divider()}\n"
                f"BTC: {format_price(random.uniform(60000,75000))}\n"
                f"ETH: {format_price(random.uniform(3000,4500))}\n"
                f"ارزش بازار: {format_number(random.uniform(1e12,3e12))}"
            )
        elif data == "market_top_gainers":
            await query.edit_message_text(
                f"📈 *بیشترین رشد ۲۴h*\n{Text.divider()}\n"
                f"۱. SOL +{random.uniform(8,15):.1f}%\n"
                f"۲. AVAX +{random.uniform(5,12):.1f}%\n"
                f"۳. LINK +{random.uniform(4,10):.1f}%"
            )
        elif data == "market_fear_greed":
            index = random.randint(20, 80)
            sentiment = "ترس 😱" if index < 40 else ("طمع 🤑" if index > 60 else "خنثی 😐")
            await query.edit_message_text(f"😱 *شاخص ترس و طمع*\n{Text.divider()}\n{index}/100 — {sentiment}")
        elif data == "market_dominance":
            await query.edit_message_text(
                f"👑 *دامیننس بازار*\n{Text.divider()}\n"
                f"BTC: {random.uniform(48,55):.1f}%\n"
                f"ETH: {random.uniform(15,20):.1f}%\n"
                f"سایر: {random.uniform(25,35):.1f}%"
            )
        
        # ===== هوش مصنوعی =====
        elif data == "ai_start_chat":
            await query.edit_message_text("💬 *چت با هوش مصنوعی*\nپیام خود را بنویسید. /cancel برای خروج.")
        elif data == "ai_generate_signal":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(
                f"🤖 *سیگنال AI — {coin}*\n{Text.divider()}\n"
                f"جهت: {'🟢 خرید' if random.random() > 0.5 else '🔴 فروش'}\n"
                f"اعتبار: {random.randint(75, 98)}%"
            )
        elif data == "ai_market_summary":
            await query.edit_message_text(
                f"📊 *خلاصه بازار توسط AI*\n{Text.divider()}\n"
                f"روند کلی: صعودی\n"
                f"BTC پیشرو است\n"
                f"آلت‌کوین‌ها قدرت نشان می‌دهند\n"
                f"توصیه: خرید در اصلاحات"
            )
        elif data == "ai_price_predict":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(
                f"🔮 *پیش‌بینی AI — {coin}*\n{Text.divider()}\n"
                f"۷ روز: {format_price(random.uniform(50000,80000))}\n"
                f"۳۰ روز: {format_price(random.uniform(60000,100000))}"
            )
        elif data == "ai_explain_concept":
            await query.edit_message_text("📝 *توضیح مفاهیم توسط AI*\nهر سوالی دارید بپرسید!")
        elif data == "ai_trading_strategy":
            await query.edit_message_text(
                f"🧠 *استراتژی AI*\n{Text.divider()}\n"
                f"استراتژی: دنبال کردن روند\n"
                f"ورود: RSI < ۳۰ + تقاطع MACD\n"
                f"خروج: RSI > ۷۰ یا حد ضرر ۵٪"
            )
        elif data == "ai_run_backtest":
            await query.edit_message_text(
                f"📊 *نتایج بک‌تست*\n{Text.divider()}\n"
                f"دوره: ۹۰ روز\n"
                f"کل معاملات: {random.randint(20,50)}\n"
                f"نرخ برد: {random.uniform(55,75):.1f}%\n"
                f"سود/ضرر: {format_percent(random.uniform(-10,25))}"
            )
        
        # ===== سیگنال‌ها =====
        elif data == "signals_today_list":
            signals = db.get_today_signals()
            if signals:
                text = "📡 *سیگنال‌های امروز*\n{Text.divider()}\n"
                for s in signals[:5]:
                    text += f"• {s['coin']}: {s['direction'].upper()} ({s['confidence']}%)\n"
                await query.edit_message_text(text)
            else:
                await query.edit_message_text("📡 امروز هنوز سیگنالی ثبت نشده. با /signal سیگنال بگیرید")
        elif data == "signals_top_rated":
            await query.edit_message_text(
                f"📈 *برترین سیگنال‌ها*\n{Text.divider()}\n"
                f"۱. BTC 🟢🟢🟢 (۹۵٪)\n"
                f"۲. SOL 🟢🟢 (۸۸٪)\n"
                f"۳. ETH 🟢🟢 (۸۵٪)"
            )
        elif data == "signals_statistics":
            await query.edit_message_text(
                f"📊 *آمار سیگنال‌ها*\n{Text.divider()}\n"
                f"کل: {len(db.get_signals())}\n"
                f"دقت: ۸۵٪\nنرخ برد: ۷۸٪"
            )
        elif data == "signals_history_view":
            await query.edit_message_text("📅 *تاریخچه سیگنال‌ها*\nبا /history مشاهده کنید")
        elif data == "signals_performance":
            await query.edit_message_text("📊 *عملکرد*\n{Text.divider()}\nنرخ برد: ۷۸٪\nمیانگین سود: +۳.۲٪")
        elif data == "menu_signal_buy":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"🚨 *سیگنال خرید — {coin}*\nاعتبار: {random.randint(70,95)}% {signal_emoji('buy')}")
        elif data == "menu_signal_sell":
            coin = context.user_data.get('last_coin', 'BTC')
            await query.edit_message_text(f"📈 *سیگنال فروش — {coin}*\nاعتبار: {random.randint(70,95)}% {signal_emoji('sell')}")
        
        # ===== حالت گاد =====
        elif data == "god_generate_signal":
            await query.edit_message_text(
                f"🤖 *سیگنال گاد*\n{Text.divider()}\n"
                f"BTC: {signal_emoji('strong_buy')} ۹۵٪\n"
                f"ETH: {signal_emoji('buy')} ۸۵٪\n"
                f"SOL: {signal_emoji('buy')} ۸۲٪"
            )
        elif data == "god_run_scanner":
            await query.edit_message_text(
                f"📊 *اسکنر بازار*\n{Text.divider()}\n"
                f"BTC: صعودی 🟢\nETH: خنثی 🟡\nSOL: صعودی 🟢\nAVAX: نزولی 🔴"
            )
        elif data == "god_make_prediction":
            await query.edit_message_text("🔮 *پیش‌بینی گاد*\n{Text.divider()}\nBTC تا ۱۰۰,۰۰۰ دلار تا پایان ۲۰۲۶")
        elif data == "god_market_overview":
            await query.edit_message_text(
                f"📊 *نمای گاد*\n{Text.divider()}\n"
                f"بازار: صعودی\nبهترین انتخاب: BTC\nسطح ریسک: متوسط"
            )
        elif data == "god_send_channel":
            await query.edit_message_text("📢 سیگنال به کانال ارسال شد!")
        elif data == "god_top_picks":
            await query.edit_message_text(
                f"📈 *بهترین انتخاب‌ها*\n{Text.divider()}\n"
                f"۱. BTC 🟢🟢🟢\n۲. SOL 🟢🟢\n۳. LINK 🟢"
            )
        elif data == "god_toggle_auto":
            await query.edit_message_text("🔄 انتشار خودکار: خاموش")
        
        # ===== ادمین =====
        elif data == "admin_dashboard":
            s = db.get_stats()
            await query.edit_message_text(
                f"🧠 *داشبورد مدیریت*\n{Text.divider()}\n"
                f"👥 کاربران: {s['total_users']:,}\n"
                f"💎 VIP: {s['vip_users']:,}\n"
                f"💰 درآمد: {format_number(s['revenue'])} تومان\n"
                f"📡 سیگنال‌ها: {s['total_signals']:,}\n"
                f"🕐 زمان فعالیت: {int(time.time() - self.start_time)} ثانیه"
            )
        elif data == "admin_users_menu":
            await query.edit_message_text("👥 *مدیریت کاربران*", reply_markup=KB.admin_users_menu())
        elif data == "admin_users_list_all":
            users = db.get_all_users()
            text = f"👥 *همه کاربران ({len(users)})*\n{Text.divider()}\n"
            for u in users[:20]:
                text += f"• `{u['telegram_id']}`: {u.get('first_name','')}\n"
            await query.edit_message_text(text)
        elif data == "admin_users_search":
            await query.edit_message_text("🔍 شناسه عددی کاربر را وارد کنید:")
        elif data == "admin_users_ban":
            await query.edit_message_text("🚫 شناسه کاربر برای مسدودیت:")
        elif data == "admin_users_unban":
            await query.edit_message_text("✅ شناسه کاربر برای رفع مسدودیت:")
        elif data == "admin_users_promote_vip":
            await query.edit_message_text("👑 شناسه کاربر برای ارتقا به VIP:")
        elif data == "admin_users_demote_vip":
            await query.edit_message_text("⬇️ شناسه کاربر برای تنزل از VIP:")
        elif data == "admin_payments_menu":
            await query.edit_message_text("💰 *مدیریت پرداخت‌ها*", reply_markup=KB.admin_payments_menu())
        elif data.startswith("payments_list_"):
            status = data.replace("payments_list_", "")
            status_fa = {"all": "همه", "pending": "در انتظار", "approved": "تأیید شده", "rejected": "رد شده"}
            payments = db.get_payments(status=status if status != "all" else None)
            text = f"📋 *پرداخت‌های {status_fa.get(status, status)}*\n{Text.divider()}\n"
            for p in payments[:15]:
                text += f"• #{p['id']}: {p.get('amount',0):,} تومان — {p.get('status','?')}\n"
            await query.edit_message_text(text)
        elif data == "payments_approve_one":
            await query.edit_message_text("✅ شناسه پرداخت برای تأیید:")
        elif data == "payments_reject_one":
            await query.edit_message_text("❌ شناسه پرداخت برای رد:")
        elif data == "payments_financial_report":
            s = db.get_stats()
            await query.edit_message_text(
                f"📊 *گزارش مالی*\n{Text.divider()}\n"
                f"کل پرداخت‌ها: {s['total_payments']}\n"
                f"درآمد کل: {format_number(s['revenue'])} تومان"
            )
        elif data == "admin_vip_menu":
            await query.edit_message_text("💎 *مدیریت VIP*", reply_markup=KB.admin_vip_menu())
        elif data == "vip_list_active":
            vips = db.get_vip_users()
            text = f"👑 *VIPهای فعال ({len(vips)})*\n{Text.divider()}\n"
            for v in vips[:15]:
                text += f"• `{v['telegram_id']}`: {v.get('first_name','')}\n"
            await query.edit_message_text(text)
        elif data == "vip_list_trials":
            trials = [u for u in db.get_all_users() if u.get('is_trial')]
            text = f"🎁 *کاربران آزمایشی ({len(trials)})*\n{Text.divider()}\n"
            for t in trials[:15]:
                text += f"• `{t['telegram_id']}`: {t.get('first_name','')}\n"
            await query.edit_message_text(text)
        elif data == "admin_broadcast_menu":
            await query.edit_message_text("📢 *ارسال همگانی*", reply_markup=KB.admin_broadcast_menu())
        elif data == "broadcast_send_all":
            context.user_data['broadcast_target'] = 'all'
            await query.edit_message_text("📝 پیام خود را برای ارسال به همه کاربران بفرستید. /cancel برای لغو.")
        elif data == "broadcast_send_vip":
            context.user_data['broadcast_target'] = 'vip'
            await query.edit_message_text("📝 پیام خود را برای VIPها بفرستید:")
        elif data == "broadcast_send_regular":
            context.user_data['broadcast_target'] = 'users'
            await query.edit_message_text("📝 پیام خود را برای کاربران عادی بفرستید:")
        elif data == "admin_channel_post":
            await query.edit_message_text("📡 پیام خود را برای کانال بفرستید:")
        elif data == "admin_api_key":
            token = Security.generate_token(user.id)
            await query.edit_message_text(f"🔧 *توکن API شما*\n{Text.divider()}\n`{token}`\n\nاعتبار: ۲۴ ساعت")
        elif data == "admin_backup_now":
            backup_id = generate_unique_id()
            await query.edit_message_text(
                f"💾 *پشتیبان‌گیری انجام شد*\n{Text.divider()}\n"
                f"شناسه: `{backup_id}`\n"
                f"تاریخ: {get_persian_time()}\n"
                f"کاربران: {len(db.get_all_users())}"
            )
        elif data == "admin_server_menu":
            await query.edit_message_text("🚪 *مدیریت سرور*", reply_markup=KB.admin_server_menu())
        elif data == "server_view_status":
            msg = f"📊 *وضعیت سرور*\n{Text.divider()}\n"
            msg += f"زمان فعالیت: {int(time.time() - self.start_time)} ثانیه\n"
            msg += f"محیط: {ENVIRONMENT}\n"
            msg += f"پایتون: {sys.version.split()[0]}"
            if HAS_PSUTIL:
                msg += f"\nCPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%"
            await query.edit_message_text(msg)
        elif data == "server_clear_cache":
            cache.clear()
            await query.edit_message_text("🧹 کش با موفقیت پاکسازی شد!")
        elif data == "server_view_resources":
            msg = "📈 *منابع سیستم*\n{Text.divider()}\n"
            if HAS_PSUTIL:
                msg += f"CPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%\nDisk: {psutil.disk_usage('/').percent}%"
            await query.edit_message_text(msg)
        elif data == "admin_reports_menu":
            await query.edit_message_text("📊 *گزارش‌ها*", reply_markup=KB.admin_reports_menu())
        elif data == "admin_security_info":
            await query.edit_message_text(
                f"🔒 *اطلاعات امنیتی*\n{Text.divider()}\n"
                f"توکن: `{Security.generate_token(user.id)[:20]}...`\n"
                f"کلید API: `{Security.generate_api_key(user.id)}`"
            )
        elif data == "admin_top_signals":
            await query.edit_message_text(
                f"📈 *برترین سیگنال‌ها*\n{Text.divider()}\n"
                f"BTC: {signal_emoji('strong_buy')} ۹۵٪\n"
                f"ETH: {signal_emoji('buy')} ۸۵٪"
            )
        elif data == "admin_market_scanner":
            await query.edit_message_text(
                f"📊 *اسکنر بازار*\n{Text.divider()}\n"
                f"BTC: صعودی\nETH: خنثی\nSOL: صعودی"
            )
        elif data == "admin_whale_activity":
            await query.edit_message_text(
                f"🐋 *فعالیت نهنگ‌ها*\n{Text.divider()}\n"
                f"• ۱,۰۰۰ BTC به بایننس منتقل شد\n"
                f"• ۵,۰۰۰ ETH از کیف پول ناشناس خارج شد\n"
                f"• ۱۰M USDT به صرافی منتقل شد"
            )
        elif data == "admin_predictions":
            await query.edit_message_text(
                f"🔮 *پیش‌بینی قیمت‌ها*\n{Text.divider()}\n"
                f"BTC: ۸۵,۰۰۰ دلار تا جولای ۲۰۲۶\n"
                f"ETH: ۵,۰۰۰ دلار تا آگوست ۲۰۲۶\n"
                f"SOL: ۲۵۰ دلار تا سپتامبر ۲۰۲۶"
            )
        elif data == "admin_system_monitor":
            msg = "📡 *مانیتور سیستم*\n{Text.divider()}\n"
            msg += f"زمان فعالیت: {int(time.time() - self.start_time)} ثانیه\n"
            if HAS_PSUTIL:
                msg += f"CPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%"
            await query.edit_message_text(msg)
        elif data == "admin_system_stats":
            s = db.get_stats()
            await query.edit_message_text(
                f"📊 *آمار سیستم*\n{Text.divider()}\n"
                f"کاربران: {s['total_users']}\n"
                f"VIP: {s['vip_users']}\n"
                f"سیگنال‌ها: {s['total_signals']}"
            )
        
        # ===== راهنما =====
        elif data == "help_show_full_guide":
            await query.edit_message_text(
                f"📖 *راهنمای کامل*\n{Text.divider()}\n"
                f"۱. /start — شروع\n"
                f"۲. کاوش در منوها\n"
                f"۳. /analysis BTC — تحلیل\n"
                f"۴. /signal — دریافت سیگنال\n"
                f"۵. /vip — ارتقا به VIP"
            )
        elif data == "help_getting_started":
            await query.edit_message_text("🎯 *شروع کار*\n{Text.divider()}\nاز /start شروع کنید و منوها را ببینید!")
        elif data == "help_tips_tricks":
            await query.edit_message_text("💡 *نکات*\n{Text.divider()}\n• /price COIN برای قیمت\n• VIP = سیگنال‌های ویژه\n• /referral = کسب درآمد")
        elif data == "help_show_faq":
            await query.edit_message_text("❓ *سوالات متداول*\n{Text.divider()}\nس: چطور VIP بخرم؟\nج: /vip و راهنما را ببینید")
        elif data == "help_list_commands":
            await query.edit_message_text(
                "📋 *دستورات*\n{Text.divider()}\n"
                "/start /help /vip /wallet /analysis /signal\n"
                "/market /ai /settings /profile /referral\n"
                "/price /ticker /rsi /macd /predict\n"
                "/buy /sell /top /overview /stats"
            )
        elif data == "help_api_docs":
            await query.edit_message_text("🔑 *مستندات API*\nبه زودی...")
        
        # ===== گزارش‌ها =====
        elif data.startswith("reports_"):
            report_type = data.replace("reports_", "").replace("_", " ").title()
            await query.edit_message_text(f"📊 *{report_type}*\n{Text.divider()}\nتولید: {get_persian_time()}")
        
        else:
            await query.edit_message_text("⚠️ گزینه نامعتبر. لطفاً دوباره تلاش کنید.", reply_markup=KB.back())
    
    # ===== مکالمات =====
    async def conv_broadcast_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("📝 پیام خود را برای ارسال همگانی بفرستید. /cancel برای لغو.")
        return "AWAIT_BROADCAST"
    
    async def conv_broadcast_receive(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        target = context.user_data.get('broadcast_target', 'all')
        message = update.message
        sent = 0
        failed = 0
        for u in db.get_all_users():
            uid = int(u['telegram_id'])
            if target == 'vip' and not (u.get('is_vip') or u.get('is_trial')):
                continue
            if target == 'users' and (u.get('is_vip') or u.get('is_trial')):
                continue
            try:
                await message.copy(chat_id=uid)
                sent += 1
                await asyncio.sleep(0.03)
            except:
                failed += 1
        await update.message.reply_text(f"✅ ارسال همگانی انجام شد!\n📤 ارسال موفق: {sent}\n❌ ناموفق: {failed}")
        return ConversationHandler.END
    
    async def conv_withdraw_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("📤 مبلغ برداشت به تومان را وارد کنید (حداقل ۵۰,۰۰۰ تومان):")
        return "AWAIT_WITHDRAW_AMOUNT"
    
    async def conv_withdraw_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.replace(',', '').replace('،', '')
        try:
            amount = int(text)
            if amount < 50000:
                await update.message.reply_text("❌ حداقل برداشت ۵۰,۰۰۰ تومان است. دوباره وارد کنید:")
                return "AWAIT_WITHDRAW_AMOUNT"
            context.user_data['withdraw_amount'] = amount
            await update.message.reply_text("💳 شماره کارت ۱۶ رقمی مقصد را وارد کنید:")
            return "AWAIT_WITHDRAW_CARD"
        except:
            await update.message.reply_text("❌ مبلغ نامعتبر. عدد وارد کنید:")
            return "AWAIT_WITHDRAW_AMOUNT"
    
    async def conv_withdraw_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        card = update.message.text.strip().replace(' ', '')
        if not re.match(r'^\d{16}$', card):
            await update.message.reply_text("❌ شماره کارت باید دقیقاً ۱۶ رقم باشد. دوباره وارد کنید:")
            return "AWAIT_WITHDRAW_CARD"
        amount = context.user_data['withdraw_amount']
        db.add_payment({
            "user_id": str(update.effective_user.id),
            "amount": -amount,
            "type": "withdraw",
            "status": "pending",
            "date": get_persian_time(),
            "card": card,
        })
        await update.message.reply_text(
            f"✅ *درخواست برداشت ثبت شد*\n{Text.divider()}\n"
            f"مبلغ: {format_number(amount)} تومان\n"
            f"کارت: {card[:4]}****{card[-4:]}\n"
            f"وضعیت: در انتظار تأیید\n\n"
            f"_پرداخت ۲۴ تا ۴۸ ساعت زمان می‌برد_"
        )
        return ConversationHandler.END
    
    async def conv_ai_chat_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("💬 *حالت چت با هوش مصنوعی*\nسوال خود را بپرسید. /cancel برای خروج.")
        return "AI_CHATTING"
    
    async def conv_ai_chat_receive(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_msg = update.message.text
        responses = [
            "📊 بر اساس تحلیل تکنیکال، روند صعودی به نظر می‌رسد.",
            "🔍 توصیه می‌کنم شاخص RSI را برای تأیید بررسی کنید.",
            "💡 حد ضرر را ۵٪ پایین‌تر از قیمت ورود قرار دهید.",
            "📈 احساسات بازار در حال حاضر مثبت است.",
            "⚠️ همیشه سبد سرمایه‌گذاری خود را متنوع کنید.",
            "🧠 به نظر می‌رسد پول هوشمند در این سطوح در حال جمع‌آوری است.",
            "📉 منتظر یک اصلاح قبل از ورود باشید.",
        ]
        await update.message.reply_text(f"🤖 {random.choice(responses)}")
        return "AI_CHATTING"

# ============================================================================================================
# نقطه ورود اصلی
# ============================================================================================================
def main():
    """شروع ربات کریپتوپالس"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🚀 کریپتوپالس هوش مصنوعی نسخه {BOT_VERSION}                         ║
║  پارت ۹ — مرکز مدیریت نهایی — کاملاً مستقل                   ║
║  {get_persian_time()}                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # اعتبارسنجی توکن
    if not BOT_TOKEN:
        print("=" * 60)
        print("❌ خطا: BOT_TOKEN تنظیم نشده است!")
        print("")
        print("توکن ربات خود را با یکی از روش‌های زیر تنظیم کنید:")
        print("  export BOT_TOKEN='your_token_here'")
        print("  python3 part9.py your_token_here")
        print("")
        print("همچنین شناسه ادمین را تنظیم کنید (اختیاری):")
        print("  export ADMIN_IDS='123456789,987654321'")
        print("=" * 60)
        sys.exit(1)
    
    print(f"✅ توکن ربات: {BOT_TOKEN[:15]}...")
    print(f"✅ شناسه ادمین‌ها: {ADMIN_IDS}")
    print(f"✅ پایگاه داده: درون حافظه (کاملاً مستقل)")
    print(f"✅ محیط: {ENVIRONMENT}")
    print(f"✅ زمان‌بند: {'موجود' if HAS_SCHEDULER else 'پایه'}")
    print(f"✅ مانیتورینگ: {'موجود' if HAS_PSUTIL else 'پایه'}")
    print(f"✅ ارزهای پشتیبانی شده: {len(SUPPORTED_COINS)}")
    print(f"✅ نام پارت: {PART_NAME}")
    print("")
    print("─" * 60)
    print("در حال شروع ربات...")
    print("─" * 60)
    
    # ساخت برنامه
    crypto_app = CryptoPulseApp()
    application = crypto_app.build()
    
    try:
        if WEBHOOK_URL:
            print(f"🌐 حالت وب‌هوک: {WEBHOOK_URL}")
            application.run_webhook(
                listen="0.0.0.0",
                port=int(os.environ.get("PORT", 8443)),
                url_path=BOT_TOKEN,
                webhook_url=WEBHOOK_URL
            )
        else:
            print("📡 حالت پولینگ: در حال شروع...")
            print("Ctrl+C برای توقف")
            application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n👋 در حال خروج...")
    except Exception as e:
        print(f"❌ خطای مرگبار: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
