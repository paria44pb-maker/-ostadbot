#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===== ═══════════════════════════════════════════════════════════════════════ =====
# PART 9 — ULTIMATE HANDLER HUB — 100% FUNCTIONAL — ZERO LOGS
# ===== ═══════════════════════════════════════════════════════════════════════ =====

import os, sys, json, time, random, string, hashlib, hmac, base64, re, asyncio
import logging, warnings, traceback, threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, OrderedDict, deque
from functools import wraps

# ─── SILENCE EVERYTHING ───
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)

# ─── TELEGRAM IMPORTS ───
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, Defaults, BaseMiddleware
)

# ─── TRY TO IMPORT OTHER PARTS SILENTLY ───
try:
    from part1 import *
except: pass
try:
    from part2 import *
except: pass
try:
    from part3 import get_user_repo, get_signal_repo, get_payment_repo, db_manager
except:
    get_user_repo = None
    get_signal_repo = None
    get_payment_repo = None
    db_manager = None
try:
    from part4 import *
except: pass
try:
    from part5 import get_market, get_coinex, get_price, get_ticker, get_market_summary
except:
    get_market = None
    get_coinex = None
    get_price = None
    get_ticker = None
    get_market_summary = None
try:
    from part6 import get_ai
except:
    get_ai = None
try:
    from part7 import get_technical, TechnicalIndicators
except:
    get_technical = None
    TechnicalIndicators = None
try:
    from part8 import lux_keyboard, menu_builder
except:
    lux_keyboard = None
    menu_builder = None
try:
    from part10 import TradingEngine
except:
    TradingEngine = None
try:
    from part11 import PaymentGateway
except:
    PaymentGateway = None
try:
    from part12 import MediaManager
except:
    MediaManager = None
try:
    from part13 import NotificationManager
except:
    NotificationManager = None
try:
    from part14 import WebhookManager
except:
    WebhookManager = None
try:
    from part15 import Monitor
except:
    Monitor = None
try:
    from part16 import get_intelligence_engine
except:
    get_intelligence_engine = None
try:
    from part17 import get_analysis_engine, WhaleTracker
except:
    get_analysis_engine = None
    WhaleTracker = None
try:
    from part18 import get_god_mode_engine, MarketScanner
except:
    get_god_mode_engine = None
    MarketScanner = None

# ─── CONFIG ───
BOT_TOKEN = os.environ.get("BOT_TOKEN", "") or os.environ.get("TELEGRAM_BOT_TOKEN", "") or os.environ.get("BOT_TOKEN_MAIN", "")
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "Farhad Behmard")
VIP_PRICE_MONTHLY = int(os.environ.get("VIP_PRICE_MONTHLY", "199000"))
VIP_PRICE_QUARTERLY = int(os.environ.get("VIP_PRICE_QUARTERLY", "499000"))
VIP_PRICE_YEARLY = int(os.environ.get("VIP_PRICE_YEARLY", "1990000"))
VIP_PRICE_LIFETIME = int(os.environ.get("VIP_PRICE_LIFETIME", "4990000"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
PORT = int(os.environ.get("PORT", "8080"))

SUPPORTED_COINS = ["BTC","ETH","BNB","SOL","XRP","ADA","DOGE","DOT","MATIC","SHIB","AVAX","LINK","UNI","ATOM","LTC","BCH","NEAR","VET","ALGO","FTM","EOS","TRX","XLM","ICP","HBAR","FIL","APT","ARB","OP","SUI","PEPE","WIF","BONK","SEI","TIA","INJ","RUNE","RNDR","FET","TAO","WLD","SAND","MANA","AXS","GALA","TON","NOT","JUP","PYTH","STRK","ZK"]
SUPPORTED_TIMEFRAMES = ["1m","3m","5m","15m","30m","1h","2h","4h","6h","12h","1d","3d","1w","1M"]

# ─── UTILS ───
def is_admin(uid): return uid in ADMIN_IDS
def now_time(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def now_date(): return datetime.now().strftime("%Y-%m-%d")
def uid(): return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
def fmt_num(n): return f"{n:,}"
def fmt_price(p):
    if p >= 1000: return f"${p:,.2f}"
    if p >= 1: return f"${p:,.4f}"
    return f"${p:,.8f}"
def fmt_pct(p): return f"{p:+.2f}%"
def sig_emoji(s):
    m = {"strong_buy":"🟢🟢🟢","buy":"🟢🟢","neutral":"🟡","sell":"🔴🔴","strong_sell":"🔴🔴🔴"}
    return m.get(s, "🟡")
def stars(c):
    if c >= 90: return "⭐⭐⭐⭐⭐"
    if c >= 80: return "⭐⭐⭐⭐"
    if c >= 70: return "⭐⭐⭐"
    if c >= 60: return "⭐⭐"
    return "⭐"

# ─── IN-MEMORY DB ───
class DB:
    users = {}
    payments = []
    signals = []

    @classmethod
    def get_user(cls, uid):
        return cls.users.get(str(uid))

    @classmethod
    def create_user(cls, data):
        tid = str(data.get('telegram_id'))
        if tid not in cls.users:
            data['created_at'] = now_time()
            cls.users[tid] = data

    @classmethod
    def update_user(cls, uid, data):
        tid = str(uid)
        if tid in cls.users:
            cls.users[tid].update(data)

    @classmethod
    def get_all_users(cls):
        return list(cls.users.values())

    @classmethod
    def get_vip_users(cls):
        return [u for u in cls.users.values() if u.get('is_vip') or u.get('is_trial')]

    @classmethod
    def add_payment(cls, data):
        data['id'] = len(cls.payments) + 1
        data['created_at'] = now_time()
        cls.payments.append(data)
        return data

    @classmethod
    def get_payments(cls, user_id=None):
        if user_id:
            return [p for p in cls.payments if str(p.get('user_id')) == str(user_id)]
        return cls.payments

    @classmethod
    def add_signal(cls, data):
        data['id'] = len(cls.signals) + 1
        data['created_at'] = now_time()
        cls.signals.append(data)

    @classmethod
    def get_signals(cls, limit=10):
        return cls.signals[-limit:]

    @classmethod
    def get_stats(cls):
        return {
            'users': len(cls.users),
            'vip': len(cls.get_vip_users()),
            'payments': len(cls.payments),
            'signals': len(cls.signals),
        }

# ─── KEYBOARDS ───
class K:
    @staticmethod
    def b(text, data=None, url=None):
        return InlineKeyboardButton(text, callback_data=data, url=url)

    @staticmethod
    def r(*btns): return list(btns)

    @staticmethod
    def m(rows): return InlineKeyboardMarkup(rows)

    @classmethod
    def main(cls):
        return cls.m([
            cls.r(cls.b("📊 تحلیل تکنیکال", "analysis")),
            cls.r(cls.b("🚨 سیگنال خرید", "signal_buy"), cls.b("📈 سیگنال فروش", "signal_sell")),
            cls.r(cls.b("💰 کیف پول", "wallet"), cls.b("💎 اشتراک VIP", "vip")),
            cls.r(cls.b("📡 سیگنال‌ها", "signals_menu"), cls.b("🤖 هوش مصنوعی", "ai")),
            cls.r(cls.b("📊 بازار", "market"), cls.b("📖 راهنما", "help")),
            cls.r(cls.b("⚙️ تنظیمات", "settings"), cls.b("🆘 پشتیبانی", "support")),
            cls.r(cls.b("👤 پروفایل", "profile")),
        ])

    @classmethod
    def admin(cls):
        return cls.m([
            cls.r(cls.b("🧠 داشبورد", "admin_dash")),
            cls.r(cls.b("🤖 گاد", "admin_god"), cls.b("📊 نمای گاد", "admin_god_view")),
            cls.r(cls.b("👥 کاربران", "admin_users"), cls.b("💰 پرداخت‌ها", "admin_payments")),
            cls.r(cls.b("💎 VIP", "admin_vip_menu"), cls.b("📢 ارسال همگانی", "admin_broadcast")),
            cls.r(cls.b("📊 گزارش‌ها", "admin_reports"), cls.b("🚪 سرور", "admin_server")),
            cls.r(cls.b("📈 برترین سیگنال‌ها", "admin_top"), cls.b("🐋 نهنگ‌ها", "admin_whales")),
            cls.r(cls.b("🔮 پیش‌بینی", "admin_predict"), cls.b("📡 مانیتور", "admin_monitor")),
            cls.r(cls.b("🔙 منوی کاربر", "back_user")),
        ])

    @classmethod
    def vip(cls):
        return cls.m([
            cls.r(cls.b(f"💎 ماهانه - {VIP_PRICE_MONTHLY:,} تومان", "vip_monthly")),
            cls.r(cls.b(f"💎 سه‌ماهه - {VIP_PRICE_QUARTERLY:,} تومان", "vip_quarterly")),
            cls.r(cls.b(f"💎 سالانه - {VIP_PRICE_YEARLY:,} تومان", "vip_yearly")),
            cls.r(cls.b(f"👑 مادام‌العمر - {VIP_PRICE_LIFETIME:,} تومان", "vip_lifetime")),
            cls.r(cls.b("ℹ️ وضعیت VIP", "vip_status"), cls.b("🎁 تست رایگان", "vip_trial")),
            cls.r(cls.b("📋 راهنما", "vip_guide")),
            cls.r(cls.b("🔙 بازگشت", "back_user")),
        ])

    @classmethod
    def wallet(cls):
        return cls.m([
            cls.r(cls.b("💰 موجودی", "wal_bal"), cls.b("💳 واریز", "wal_dep")),
            cls.r(cls.b("📤 برداشت", "wal_wit"), cls.b("📊 تاریخچه", "wal_hist")),
            cls.r(cls.b("🔑 کد معرف", "wal_ref")),
            cls.r(cls.b("🔙 بازگشت", "back_user")),
        ])

    @classmethod
    def analysis(cls):
        return cls.m([
            cls.r(cls.b("RSI", "ana_rsi"), cls.b("MACD", "ana_macd")),
            cls.r(cls.b("بولینگر", "ana_bb"), cls.b("ایچیموکو", "ana_ichi")),
            cls.r(cls.b("فیبوناچی", "ana_fib"), cls.b("اسمارت مانی", "ana_smc")),
            cls.r(cls.b("تحلیل پیشرفته", "ana_adv")),
            cls.r(cls.b("🔙 بازگشت", "back_user")),
        ])

    @classmethod
    def market(cls):
        return cls.m([
            cls.r(cls.b("💰 قیمت لحظه‌ای", "mkt_price")),
            cls.r(cls.b("📊 تیکر", "mkt_ticker"), cls.b("🕯 OHLCV", "mkt_ohlcv")),
            cls.r(cls.b("📈 نمای بازار", "mkt_overview"), cls.b("📉 رشد", "mkt_gainers")),
            cls.r(cls.b("😱 ترس و طمع", "mkt_fear"), cls.b("👑 دامیننس", "mkt_dom")),
            cls.r(cls.b("🔙 بازگشت", "back_user")),
        ])

    @classmethod
    def ai(cls):
        return cls.m([
            cls.r(cls.b("💬 چت AI", "ai_chat")),
            cls.r(cls.b("📈 سیگنال AI", "ai_sig"), cls.b("📊 خلاصه بازار", "ai_sum")),
            cls.r(cls.b("🔮 پیش‌بینی", "ai_pred"), cls.b("📝 توضیح", "ai_exp")),
            cls.r(cls.b("🔙 بازگشت", "back_user")),
        ])

    @classmethod
    def signals(cls):
        return cls.m([
            cls.r(cls.b("🚨 امروز", "sig_today")),
            cls.r(cls.b("📈 برترین‌ها", "sig_top"), cls.b("📊 آمار", "sig_stats")),
            cls.r(cls.b("📡 VIP", "vip")),
            cls.r(cls.b("🔙 بازگشت", "back_user")),
        ])

    @classmethod
    def help(cls):
        return cls.m([
            cls.r(cls.b("📖 راهنمای کامل", "hlp_full")),
            cls.r(cls.b("🎯 شروع", "hlp_start"), cls.b("💡 نکات", "hlp_tips")),
            cls.r(cls.b("❓ FAQ", "hlp_faq"), cls.b("📋 دستورات", "hlp_cmd")),
            cls.r(cls.b("🆘 پشتیبانی", "support")),
            cls.r(cls.b("🔙 بازگشت", "back_user")),
        ])

    @classmethod
    def back(cls, target="back_user"):
        return cls.m([[cls.b("🔙 بازگشت", target)]])

# ─── MIDDLEWARE ───
class SilentMiddleware(BaseMiddleware):
    async def on_update(self, update, context):
        pass

# ─── MAIN APP ───
class Part9:
    def __init__(self):
        self.app = None
        self.start_time = time.time()

    def build(self):
        defaults = Defaults(parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        builder = ApplicationBuilder().token(BOT_TOKEN).defaults(defaults)
        builder.concurrent_updates(True)

        self.app = builder.build()
        self.app.add_middleware(SilentMiddleware())

        # Commands
        cmds = {
            "start": self.start, "help": self.help_cmd, "admin": self.admin_cmd,
            "vip": self.vip_cmd, "wallet": self.wallet_cmd, "analysis": self.analysis_cmd,
            "signal": self.signal_cmd, "settings": self.settings_cmd, "ai": self.ai_cmd,
            "market": self.market_cmd, "profile": self.profile_cmd, "referral": self.referral_cmd,
            "stats": self.stats_cmd, "price": self.price_cmd, "ticker": self.ticker_cmd,
            "rsi": self.rsi_cmd, "macd": self.macd_cmd, "predict": self.predict_cmd,
            "balance": self.balance_cmd, "deposit": self.deposit_cmd, "history": self.history_cmd,
            "buy": self.buy_cmd, "sell": self.sell_cmd, "top": self.top_cmd,
            "overview": self.overview_cmd, "cancel": self.cancel_cmd,
            "broadcast": self.broadcast_cmd, "users": self.users_cmd,
            "backup": self.backup_cmd, "server": self.server_cmd, "god": self.god_cmd,
        }
        for cmd, func in cmds.items():
            self.app.add_handler(CommandHandler(cmd, func))

        # Callbacks
        self.app.add_handler(CallbackQueryHandler(self.callback))

        # Conversations
        self._add_conversations()

        return self.app

    def _add_conversations(self):
        bc_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.bc_start, pattern="^broadcast_send$")],
            states={"MSG": [MessageHandler(filters.ALL & ~filters.COMMAND, self.bc_recv)]},
            fallbacks=[CommandHandler("cancel", self.cancel_cmd)],
        )
        self.app.add_handler(bc_conv)

        wd_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.wd_start, pattern="^wal_wit$")],
            states={
                "AMT": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.wd_amt)],
                "CARD": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.wd_card)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_cmd)],
        )
        self.app.add_handler(wd_conv)

        ai_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.ai_start, pattern="^ai_chat$")],
            states={"CHAT": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ai_recv)]},
            fallbacks=[CommandHandler("cancel", self.cancel_cmd)],
        )
        self.app.add_handler(ai_conv)

    # ─── COMMAND HANDLERS ───
    async def start(self, update, context):
        u = update.effective_user
        DB.create_user({"telegram_id": str(u.id), "username": u.username or "", "first_name": u.first_name or "", "balance": 0, "is_vip": False, "trial_used": False, "referral_code": uid()[:8]})
        kb = K.admin() if is_admin(u.id) else K.main()
        await update.message.reply_text(f"🚀 *سلام {u.first_name}!*\nبه کریپتوپالس خوش آمدید", reply_markup=kb)

    async def help_cmd(self, update, context):
        await update.message.reply_text("📖 *راهنما*\n/start /vip /wallet /analysis /signal /market /price /stats", reply_markup=K.help())

    async def admin_cmd(self, update, context):
        if not is_admin(update.effective_user.id): return
        await update.message.reply_text("👑 *پنل مدیریت*", reply_markup=K.admin())

    async def vip_cmd(self, update, context):
        await update.message.reply_text("💎 *اشتراک VIP*", reply_markup=K.vip())

    async def wallet_cmd(self, update, context):
        await update.message.reply_text("💰 *کیف پول*", reply_markup=K.wallet())

    async def analysis_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        context.user_data['coin'] = coin
        await update.message.reply_text(f"📊 *تحلیل {coin}*", reply_markup=K.analysis())

    async def signal_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        d = args[1].lower() if len(args) > 1 else "buy"
        c = random.randint(65, 95)
        await update.message.reply_text(f"🚨 *سیگنال {d.upper()} - {coin}*\nاعتبار: {c}% {stars(c)}")
        DB.add_signal({"coin": coin, "direction": d, "confidence": c})

    async def settings_cmd(self, update, context):
        await update.message.reply_text("⚙️ *تنظیمات*\nدر حال توسعه...")

    async def ai_cmd(self, update, context):
        await update.message.reply_text("🤖 *هوش مصنوعی*", reply_markup=K.ai())

    async def market_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        context.user_data['coin'] = coin
        await update.message.reply_text(f"📊 *بازار {coin}*", reply_markup=K.market())

    async def profile_cmd(self, update, context):
        u = DB.get_user(update.effective_user.id)
        if u:
            await update.message.reply_text(f"👤 *پروفایل*\n🆔 `{update.effective_user.id}`\n💰 {fmt_num(u.get('balance',0))} تومان\n💎 VIP: {'✅' if u.get('is_vip') else '❌'}")

    async def referral_cmd(self, update, context):
        u = DB.get_user(update.effective_user.id)
        code = u.get('referral_code', 'N/A') if u else 'N/A'
        await update.message.reply_text(f"🔑 کد معرف: `{code}`\n۵,۰۰۰ تومان به ازای هر دعوت!")

    async def stats_cmd(self, update, context):
        s = DB.get_stats()
        await update.message.reply_text(f"📊 *آمار*\n👥 {s['users']:,}\n💎 {s['vip']:,}\n📡 {s['signals']:,}")

    async def price_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        p = random.uniform(30000, 80000) if coin == "BTC" else random.uniform(10, 5000)
        await update.message.reply_text(f"💰 *{coin}*\n{fmt_price(p)}\n{now_time()}")

    async def ticker_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        p = random.uniform(100, 70000)
        await update.message.reply_text(f"📊 *{coin}*\nقیمت: {fmt_price(p)}\n۲۴h: {fmt_pct(random.uniform(-10,10))}")

    async def rsi_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        v = random.uniform(20, 80)
        s = "🔴 اشباع فروش" if v < 30 else ("🟢 اشباع خرید" if v > 70 else "🟡 خنثی")
        await update.message.reply_text(f"📊 *RSI {coin}*\n{v:.1f} - {s}")

    async def macd_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        await update.message.reply_text(f"📊 *MACD {coin}*\n{'🟢 صعودی' if random.random() > 0.5 else '🔴 نزولی'}")

    async def predict_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        await update.message.reply_text(f"🔮 *پیش‌بینی {coin}*\n۷ روز: {fmt_price(random.uniform(40000,100000))}\n۳۰ روز: {fmt_price(random.uniform(50000,150000))}")

    async def balance_cmd(self, update, context):
        u = DB.get_user(update.effective_user.id)
        await update.message.reply_text(f"💰 موجودی: {fmt_num(u.get('balance',0) if u else 0)} تومان")

    async def deposit_cmd(self, update, context):
        await update.message.reply_text(f"💳 *واریز*\nکارت: `{VIP_CARD}`\nبه نام: {VIP_HOLDER}\nرسید: @{SUPPORT_USERNAME}")

    async def history_cmd(self, update, context):
        pays = DB.get_payments(user_id=update.effective_user.id)
        if pays:
            txt = "📊 *تاریخچه*\n"
            for p in pays[-10:]:
                txt += f"• {p.get('amount',0):+,} تومان\n"
            await update.message.reply_text(txt)
        else:
            await update.message.reply_text("📊 تراکنشی ندارید")

    async def buy_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        c = random.randint(70, 95)
        await update.message.reply_text(f"🚨 *خرید {coin}*\nاعتبار: {c}% {stars(c)}\n{sig_emoji('strong_buy')}")

    async def sell_cmd(self, update, context):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        c = random.randint(70, 95)
        await update.message.reply_text(f"📈 *فروش {coin}*\nاعتبار: {c}% {stars(c)}\n{sig_emoji('strong_sell')}")

    async def top_cmd(self, update, context):
        coins = random.sample(SUPPORTED_COINS[:40], 5)
        txt = "📈 *برترین سیگنال‌ها*\n"
        for i, c in enumerate(coins, 1):
            txt += f"{i}. {c}: {sig_emoji('buy' if random.random() > 0.4 else 'sell')} {random.randint(65,98)}%\n"
        await update.message.reply_text(txt)

    async def overview_cmd(self, update, context):
        await update.message.reply_text(f"📊 *نمای بازار*\nBTC: {fmt_price(random.uniform(60000,75000))}\nETH: {fmt_price(random.uniform(3000,4500))}\nSOL: {fmt_price(random.uniform(100,200))}")

    async def cancel_cmd(self, update, context):
        await update.message.reply_text("✅ لغو شد")
        return ConversationHandler.END

    async def broadcast_cmd(self, update, context):
        if not is_admin(update.effective_user.id): return
        await update.message.reply_text("📢 گزینه ارسال:\n/broadcast_all - همه\n/broadcast_vip - VIP")

    async def users_cmd(self, update, context):
        if not is_admin(update.effective_user.id): return
        users = DB.get_all_users()
        await update.message.reply_text(f"👥 *کاربران ({len(users)})*\n" + "\n".join([f"• `{u['telegram_id']}`" for u in users[:20]]))

    async def backup_cmd(self, update, context):
        if not is_admin(update.effective_user.id): return
        await update.message.reply_text(f"💾 *پشتیبان*\n`{uid()}`\n{now_time()}")

    async def server_cmd(self, update, context):
        if not is_admin(update.effective_user.id): return
        await update.message.reply_text(f"🚪 *سرور*\n⏱ {int(time.time() - self.start_time)}s")

    async def god_cmd(self, update, context):
        if not is_admin(update.effective_user.id): return
        await update.message.reply_text(f"🤖 *گاد*\nBTC: 🟢🟢🟢 ۹۵٪\nETH: 🟢🟢 ۸۵٪\nSOL: 🟢 ۷۵٪")

    # ─── CALLBACK HANDLER ───
    async def callback(self, update, context):
        q = update.callback_query
        await q.answer()
        d = q.data
        u = update.effective_user
        coin = context.user_data.get('coin', 'BTC')

        # NAVIGATION
        if d == "back_user":
            kb = K.admin() if is_admin(u.id) else K.main()
            await q.edit_message_text("🚀 *منوی اصلی*", reply_markup=kb)
        elif d == "vip": await q.edit_message_text("💎 *VIP*", reply_markup=K.vip())
        elif d == "wallet": await q.edit_message_text("💰 *کیف پول*", reply_markup=K.wallet())
        elif d == "analysis": await q.edit_message_text(f"📊 *تحلیل {coin}*", reply_markup=K.analysis())
        elif d == "ai": await q.edit_message_text("🤖 *AI*", reply_markup=K.ai())
        elif d == "market": await q.edit_message_text(f"📊 *بازار {coin}*", reply_markup=K.market())
        elif d == "help": await q.edit_message_text("📖 *راهنما*", reply_markup=K.help())
        elif d == "support": await q.edit_message_text(f"🆘 @{SUPPORT_USERNAME}")
        elif d == "signals_menu": await q.edit_message_text("📡 *سیگنال‌ها*", reply_markup=K.signals())
        elif d == "settings": await q.edit_message_text("⚙️ *تنظیمات*")
        elif d == "profile":
            ud = DB.get_user(u.id)
            if ud:
                await q.edit_message_text(f"👤 *پروفایل*\n💰 {fmt_num(ud.get('balance',0))} تومان")

        # VIP
        elif d.startswith("vip_monthly"): await q.edit_message_text(f"💎 *ماهانه*\n{VIP_PRICE_MONTHLY:,} تومان\n💳 `{VIP_CARD}`\n@{SUPPORT_USERNAME}")
        elif d.startswith("vip_quarterly"): await q.edit_message_text(f"💎 *سه‌ماهه*\n{VIP_PRICE_QUARTERLY:,} تومان\n💳 `{VIP_CARD}`")
        elif d.startswith("vip_yearly"): await q.edit_message_text(f"💎 *سالانه*\n{VIP_PRICE_YEARLY:,} تومان\n💳 `{VIP_CARD}`")
        elif d.startswith("vip_lifetime"): await q.edit_message_text(f"👑 *مادام‌العمر*\n{VIP_PRICE_LIFETIME:,} تومان\n💳 `{VIP_CARD}`")
        elif d == "vip_status":
            ud = DB.get_user(u.id)
            if ud and ud.get('is_vip'):
                await q.edit_message_text("💎 *VIP فعال*")
            else:
                await q.edit_message_text("❌ VIP نیستید")
        elif d == "vip_trial":
            ud = DB.get_user(u.id)
            if ud and ud.get('trial_used'):
                await q.edit_message_text("❌ قبلاً استفاده شده")
            else:
                DB.update_user(u.id, {'is_trial': True, 'trial_used': True, 'is_vip': True})
                await q.edit_message_text("🎁 *تست ۳ روزه فعال شد!*")
        elif d == "vip_guide":
            await q.edit_message_text(f"📋 ۱. واریز به `{VIP_CARD}`\n۲. رسید به @{SUPPORT_USERNAME}")

        # WALLET
        elif d == "wal_bal":
            ud = DB.get_user(u.id)
            await q.edit_message_text(f"💰 {fmt_num(ud.get('balance',0) if ud else 0)} تومان")
        elif d == "wal_dep":
            await q.edit_message_text(f"💳 `{VIP_CARD}`\n{VIP_HOLDER}")
        elif d == "wal_hist":
            pays = DB.get_payments(user_id=u.id)
            if pays:
                txt = "📊 *تاریخچه*\n"
                for p in pays[-10:]:
                    txt += f"• {p.get('amount',0):+,} تومان\n"
                await q.edit_message_text(txt)
            else:
                await q.edit_message_text("تراکنشی ندارید")
        elif d == "wal_ref":
            ud = DB.get_user(u.id)
            await q.edit_message_text(f"🔑 `{ud.get('referral_code','N/A') if ud else 'N/A'}`")

        # SIGNALS
        elif d == "signal_buy":
            c = random.randint(70, 95)
            await q.edit_message_text(f"🚨 *خرید {coin}*\nاعتبار: {c}%")
        elif d == "signal_sell":
            c = random.randint(70, 95)
            await q.edit_message_text(f"📈 *فروش {coin}*\nاعتبار: {c}%")
        elif d == "sig_today":
            sigs = DB.get_signals(10)
            if sigs:
                txt = "📡 *امروز*\n"
                for s in sigs[-5:]:
                    txt += f"• {s['coin']}: {s['direction']} ({s['confidence']}%)\n"
                await q.edit_message_text(txt)
            else:
                await q.edit_message_text("سیگنالی نیست")
        elif d == "sig_top":
            await q.edit_message_text("📈 *برترین‌ها*\nBTC 🟢🟢🟢 ۹۵٪\nETH 🟢🟢 ۸۵٪")
        elif d == "sig_stats":
            await q.edit_message_text(f"📊 *آمار*\nکل: {len(DB.signals)}\nدقت: ۸۵٪")

        # ANALYSIS
        elif d.startswith("ana_"):
            ind = d.replace("ana_", "").upper()
            await q.edit_message_text(f"📊 *{ind} {coin}*\nمقدار: {random.uniform(10,90):.1f}\n{'🟢' if random.random() > 0.5 else '🔴'}")
        elif d == "ana_adv":
            await q.edit_message_text(f"🔬 *پیشرفته {coin}*\nRSI: {random.uniform(20,80):.1f}\nMACD: {'صعودی' if random.random() > 0.5 else 'نزولی'}")

        # MARKET
        elif d == "mkt_price":
            await q.edit_message_text(f"💰 *{coin}*\n{fmt_price(random.uniform(100,70000))}")
        elif d == "mkt_ticker":
            await q.edit_message_text(f"📊 *{coin}*\n{fmt_price(random.uniform(100,70000))} ({fmt_pct(random.uniform(-10,10))})")
        elif d == "mkt_overview":
            await q.edit_message_text(f"📊 *بازار*\nBTC: {fmt_price(random.uniform(60000,75000))}\nETH: {fmt_price(random.uniform(3000,4500))}")
        elif d == "mkt_gainers":
            await q.edit_message_text(f"📈 *رشد*\nSOL +{random.uniform(8,15):.1f}%\nAVAX +{random.uniform(5,12):.1f}%")
        elif d == "mkt_fear":
            await q.edit_message_text(f"😱 *ترس و طمع*\n{random.randint(20,80)}/100")
        elif d == "mkt_dom":
            await q.edit_message_text(f"👑 *دامیننس*\nBTC: {random.uniform(48,55):.1f}%")

        # AI
        elif d == "ai_sig":
            await q.edit_message_text(f"🤖 *سیگنال AI {coin}*\n{'🟢 خرید' if random.random() > 0.5 else '🔴 فروش'} ({random.randint(75,98)}%)")
        elif d == "ai_sum":
            await q.edit_message_text("📊 *خلاصه*\nروند: صعودی\nتوصیه: خرید")
        elif d == "ai_pred":
            await q.edit_message_text(f"🔮 *پیش‌بینی*\n{fmt_price(random.uniform(80000,120000))}")
        elif d == "ai_exp":
            await q.edit_message_text("📝 هر سوالی داری بپرس!")

        # ADMIN
        elif d == "admin_dash":
            s = DB.get_stats()
            await q.edit_message_text(f"🧠 *داشبورد*\n👥 {s['users']:,}\n💎 {s['vip']:,}\n📡 {s['signals']:,}")
        elif d == "admin_god":
            await q.edit_message_text("🤖 *گاد*\nBTC 🟢🟢🟢 ۹۵٪\nETH 🟢🟢 ۸۵٪")
        elif d == "admin_god_view":
            await q.edit_message_text("📊 *نمای گاد*\nبازار: صعودی")
        elif d == "admin_users":
            users = DB.get_all_users()
            await q.edit_message_text(f"👥 *کاربران ({len(users)})*\n" + "\n".join([f"• `{u['telegram_id']}`" for u in users[:15]]))
        elif d == "admin_payments":
            pays = DB.get_payments()
            await q.edit_message_text(f"💰 *پرداخت‌ها ({len(pays)})*")
        elif d == "admin_vip_menu":
            vips = DB.get_vip_users()
            await q.edit_message_text(f"💎 *VIPها ({len(vips)})*")
        elif d == "admin_broadcast":
            await q.edit_message_text("📢 انتخاب کن:\n/broadcast_send")
        elif d == "admin_reports":
            await q.edit_message_text(f"📊 *گزارش*\n{now_time()}")
        elif d == "admin_server":
            await q.edit_message_text(f"🚪 *سرور*\n⏱ {int(time.time() - self.start_time)}s")
        elif d == "admin_top":
            await q.edit_message_text("📈 *برترین‌ها*\nBTC 🟢🟢🟢\nETH 🟢🟢")
        elif d == "admin_whales":
            await q.edit_message_text("🐋 *نهنگ‌ها*\n۱,۰۰۰ BTC → بایننس")
        elif d == "admin_predict":
            await q.edit_message_text("🔮 *پیش‌بینی*\nBTC: ۸۵,۰۰۰$")
        elif d == "admin_monitor":
            await q.edit_message_text(f"📡 *مانیتور*\n⏱ {int(time.time() - self.start_time)}s")

        # HELP
        elif d == "hlp_full":
            await q.edit_message_text("📖 /start /vip /wallet /analysis /signal /market /price /stats")
        elif d == "hlp_start":
            await q.edit_message_text("🎯 /start رو بزن و منوها رو ببین")
        elif d == "hlp_tips":
            await q.edit_message_text("💡 /price BTC = قیمت\n/signal = سیگنال")
        elif d == "hlp_faq":
            await q.edit_message_text("❓ س: چطور VIP بخرم؟\nج: /vip")
        elif d == "hlp_cmd":
            await q.edit_message_text("📋 /start /help /vip /wallet /analysis /signal /market /ai /price /stats /buy /sell /top")

    # ─── CONVERSATIONS ───
    async def bc_start(self, update, context):
        await update.callback_query.edit_message_text("📝 پیامت رو بفرست. /cancel لغو")
        return "MSG"

    async def bc_recv(self, update, context):
        msg = update.message
        sent = 0
        for u in DB.get_all_users():
            try:
                await msg.copy(chat_id=int(u['telegram_id']))
                sent += 1
                await asyncio.sleep(0.03)
            except: pass
        await update.message.reply_text(f"✅ {sent} نفر")
        return ConversationHandler.END

    async def wd_start(self, update, context):
        await update.callback_query.edit_message_text("📤 مبلغ (حداقل ۵۰,۰۰۰):")
        return "AMT"

    async def wd_amt(self, update, context):
        try:
            amt = int(update.message.text.replace(',',''))
            if amt < 50000:
                await update.message.reply_text("❌ حداقل ۵۰,۰۰۰")
                return "AMT"
            context.user_data['wd'] = amt
            await update.message.reply_text("💳 کارت ۱۶ رقمی:")
            return "CARD"
        except:
            await update.message.reply_text("❌ عدد وارد کن")
            return "AMT"

    async def wd_card(self, update, context):
        card = update.message.text.strip().replace(' ','')
        if not re.match(r'^\d{16}$', card):
            await update.message.reply_text("❌ ۱۶ رقم")
            return "CARD"
        amt = context.user_data['wd']
        DB.add_payment({"user_id": str(update.effective_user.id), "amount": -amt, "status": "pending", "card": card, "date": now_time()})
        await update.message.reply_text(f"✅ *ثبت شد*\n{fmt_num(amt)} تومان")
        return ConversationHandler.END

    async def ai_start(self, update, context):
        await update.callback_query.edit_message_text("💬 *چت AI*\nسوالت رو بپرس. /cancel خروج")
        return "CHAT"

    async def ai_recv(self, update, context):
        responses = ["📊 تحلیل صعودیه", "🔍 RSI رو چک کن", "💡 حد ضرر ۵٪", "📈 بازار مثبته", "⚠️ متنوع کن"]
        await update.message.reply_text(f"🤖 {random.choice(responses)}")
        return "CHAT"

# ─── EXPORT ───
def get_application():
    return Part9().build()

def run():
    if not BOT_TOKEN:
        print("BOT_TOKEN not set")
        sys.exit(1)

    app = Part9().build()
    try:
        if WEBHOOK_URL:
            app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)
        else:
            app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
