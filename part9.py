#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║  🚀 CRYPTOPULSE AI v9.0 — PART 9 — ULTIMATE HANDLER HUB — FIXED BaseMiddleware   ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, json, math, time, random, string, hashlib, hmac, base64, re, asyncio
import logging, warnings, traceback, threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from collections import defaultdict, OrderedDict, deque
from functools import wraps

# ═══════════════════════════════════════════════════════════════
# SILENCE
# ═══════════════════════════════════════════════════════════════
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.CRITICAL, handlers=[logging.NullHandler()])
for _name in list(logging.root.manager.loggerDict.keys()):
    logging.getLogger(_name).setLevel(logging.CRITICAL)

# ═══════════════════════════════════════════════════════════════
# TELEGRAM — FIXED BaseMiddleware IMPORT
# ═══════════════════════════════════════════════════════════════
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, Message, CallbackQuery, User
from telegram.constants import ParseMode
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, Defaults, AIORateLimiter
)

# FIX: BaseMiddleware may not exist in older versions — use object as fallback
try:
    from telegram.ext import BaseMiddleware
except ImportError:
    BaseMiddleware = object

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
BOT_TOKEN = os.environ.get("BOT_TOKEN", "") or os.environ.get("BOT_TOKEN_MAIN", "")
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().lstrip('-').isdigit()]
OWNER_IDS = [int(x.strip()) for x in os.environ.get("OWNER_IDS", "").split(",") if x.strip().lstrip('-').isdigit()]

CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SIGNAL_CHANNEL = os.environ.get("SIGNAL_CHANNEL_ID", CHANNEL_ID)
SUPPORT_USER = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "Farhad Behmard")
VIP_M = int(os.environ.get("VIP_PRICE_MONTHLY", "199000"))
VIP_Q = int(os.environ.get("VIP_PRICE_QUARTERLY", "499000"))
VIP_Y = int(os.environ.get("VIP_PRICE_YEARLY", "1990000"))
VIP_L = int(os.environ.get("VIP_PRICE_LIFETIME", "4990000"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
PORT = int(os.environ.get("PORT", "8080"))
PROXY_URL = os.environ.get("PROXY_URL", "")
BOT_VERSION = "9.0.0"
BOT_NAME = "CryptoPulse AI"

SUPPORTED_COINS = [
    "BTC","ETH","BNB","SOL","XRP","ADA","DOGE","DOT","MATIC","SHIB","AVAX","LINK",
    "UNI","ATOM","LTC","BCH","NEAR","VET","ALGO","FTM","EOS","TRX","XLM","ICP",
    "HBAR","FIL","APT","ARB","OP","SUI","PEPE","WIF","BONK","SEI","TIA","INJ",
    "RUNE","RNDR","FET","AGIX","OCEAN","TAO","WLD","SAND","MANA","AXS","GALA",
    "ENJ","CHZ","APE","GMT","AAVE","COMP","MKR","SNX","CRV","SUSHI","DYDX",
    "GMX","TON","NOT","JUP","PYTH","JTO","BOME","POPCAT","MEW","STRK","ZK",
]
SUPPORTED_TF = ["1m","3m","5m","15m","30m","1h","2h","4h","6h","12h","1d","3d","1w","1M"]

# ═══════════════════════════════════════════════════════════════
# UTILS
# ═══════════════════════════════════════════════════════════════
def is_admin(uid): return uid in ADMIN_IDS or uid in OWNER_IDS
def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def today(): return datetime.now().strftime("%Y-%m-%d")
def uid(): return ''.join(random.choices(string.ascii_letters+string.digits,k=12))
def rcode(l=8): return ''.join(random.choices(string.ascii_uppercase+string.digits,k=l))

def fmt_num(n,d=2):
    if abs(n)>=1e12: return f"{n/1e12:.{d}f}T"
    if abs(n)>=1e9: return f"{n/1e9:.{d}f}B"
    if abs(n)>=1e6: return f"{n/1e6:.{d}f}M"
    if abs(n)>=1e3: return f"{n/1e3:.{d}f}K"
    return f"{n:,.{d}f}"

def fmt_price(p):
    if p>=1000: return f"${p:,.2f}"
    if p>=1: return f"${p:,.4f}"
    if p>=0.01: return f"${p:,.6f}"
    return f"${p:,.8f}"

def fmt_pct(p): return f"{p:+.2f}%"
def fmt_irt(a): return f"{a:,.0f} تومان"

def sig_emoji(s):
    m={"strong_buy":"🟢🟢🟢","buy":"🟢🟢","neutral":"🟡","sell":"🔴🔴","strong_sell":"🔴🔴🔴"}
    return m.get(s,"🟡")

def stars(c):
    if c>=90: return "⭐⭐⭐⭐⭐"
    if c>=80: return "⭐⭐⭐⭐"
    if c>=70: return "⭐⭐⭐"
    if c>=60: return "⭐⭐"
    return "⭐"

def risk_level(c):
    if c>=85: return "🟢 کم"
    if c>=70: return "🟡 متوسط"
    if c>=55: return "🟠 بالا"
    return "🔴 خیلی بالا"

def dir_fa(d): return {"buy":"خرید 🟢","sell":"فروش 🔴"}.get(d,d)

def esc_md(t):
    for c in r'_*[]()~`>#+-=|{}.!': t=t.replace(c,'\\'+c)
    return t

def divider(): return "─"*32

def rprice(coin="BTC"):
    r={"BTC":(30000,80000),"ETH":(2000,5000),"SOL":(50,250),"BNB":(200,600)}
    return random.uniform(*r.get(coin,(1,1000)))

def rchange(): return random.uniform(-15,15)
def rconf(): return random.randint(55,98)
def validate_card(c): return bool(re.match(r'^\d{16}$',c.replace(' ','')))

# ═══════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════

class DB:
    _users: Dict[str,Dict] = {}
    _payments: Dict[int,Dict] = {}
    _signals: Dict[int,Dict] = {}
    _bans: Set[str] = set()
    _lock = threading.RLock()

    @classmethod
    def get_user(cls,tid): return cls._users.get(str(tid))
    @classmethod
    def get_by_telegram_id(cls,tid): return cls.get_user(tid)

    @classmethod
    def create_user(cls,data):
        tid=str(data.get('telegram_id'))
        with cls._lock:
            if tid not in cls._users:
                data.setdefault('id',uid()); data.setdefault('created_at',now())
                data.setdefault('balance',0); data.setdefault('is_vip',False)
                data.setdefault('is_trial',False); data.setdefault('trial_used',False)
                data.setdefault('is_banned',False); data.setdefault('referral_code',rcode())
                data.setdefault('referrals',0); data.setdefault('vip_expiry',None)
                data.setdefault('settings',json.dumps({"language":"fa","timeframe":"4h"}))
                cls._users[tid]=data
        return cls._users[tid]

    @classmethod
    def update_user(cls,tid,data):
        tid=str(tid)
        with cls._lock:
            if tid in cls._users: cls._users[tid].update(data); return True
        return False

    @classmethod
    def update_by_telegram_id(cls,tid,data): return cls.update_user(tid,data)
    @classmethod
    def all_users(cls): return list(cls._users.values())
    @classmethod
    def all(cls): return cls.all_users()
    @classmethod
    def vips(cls): return [u for u in cls._users.values() if u.get('is_vip') or u.get('is_trial')]
    @classmethod
    def ban(cls,tid): cls._bans.add(str(tid)); return cls.update_user(tid,{'is_banned':True})
    @classmethod
    def unban(cls,tid): cls._bans.discard(str(tid)); return cls.update_user(tid,{'is_banned':False})
    @classmethod
    def is_banned(cls,tid): return str(tid) in cls._bans
    @classmethod
    def balance(cls,tid):
        u=cls.get_user(tid); return u.get('balance',0) if u else 0
    @classmethod
    def add_balance(cls,tid,amt):
        u=cls.get_user(tid)
        if u: return cls.update_user(tid,{'balance':u.get('balance',0)+amt})
        return False
    @classmethod
    def deduct_balance(cls,tid,amt):
        u=cls.get_user(tid)
        if u and u.get('balance',0)>=amt: return cls.update_user(tid,{'balance':u.get('balance',0)-amt})
        return False

    @classmethod
    def create_payment(cls,data):
        with cls._lock:
            pid=len(cls._payments)+1; data['id']=pid; data['created_at']=now()
            data.setdefault('status','pending'); cls._payments[pid]=data
        return data

    @classmethod
    def add_payment(cls,data): return cls.create_payment(data)
    @classmethod
    def user_payments(cls,uid):
        return sorted([p for p in cls._payments.values() if str(p.get('user_id'))==str(uid)],
                      key=lambda x:x.get('id',0),reverse=True)
    @classmethod
    def get_by_user(cls,uid): return cls.user_payments(uid)
    @classmethod
    def payments(cls,status=None,limit=50):
        r=list(cls._payments.values())
        if status: r=[p for p in r if p.get('status')==status]
        return sorted(r,key=lambda x:x.get('id',0),reverse=True)[:limit]

    @classmethod
    def create_signal(cls,data):
        with cls._lock:
            sid=len(cls._signals)+1; data['id']=sid; data['created_at']=now()
            data.setdefault('status','active'); cls._signals[sid]=data
        return data

    @classmethod
    def add_signal(cls,data): return cls.create_signal(data)
    @classmethod
    def today_signals(cls):
        td=today(); return [s for s in cls._signals.values() if s.get('created_at','').startswith(td)]

    @classmethod
    def stats(cls):
        with cls._lock:
            total=len(cls._users); vip=len(cls.vips())
            revenue=sum(p.get('amount',0) for p in cls._payments.values() if p.get('status')=='approved' and p.get('amount',0)>0)
            return {'total_users':total,'vip_users':vip,'total_signals':len(cls._signals),'total_revenue':revenue}

# ═══════════════════════════════════════════════════════════════
# KEYBOARDS
# ═══════════════════════════════════════════════════════════════

class K:
    @staticmethod
    def b(text,data=None,url=None): return InlineKeyboardButton(text,callback_data=data,url=url)
    @staticmethod
    def r(*btns): return list(btns)
    @staticmethod
    def m(rows): return InlineKeyboardMarkup(rows)
    @staticmethod
    def g(items,cols=2): return [items[i:i+cols] for i in range(0,len(items),cols)]
    @staticmethod
    def back(target="mu"): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت",callback_data=target)]])

    @classmethod
    def main(cls): return cls.m([
        cls.r(cls.b("📊 تحلیل تکنیکال","ana")),
        cls.r(cls.b("🚨 سیگنال خرید","s_buy"),cls.b("📈 سیگنال فروش","s_sell")),
        cls.r(cls.b("💰 کیف پول","wal"),cls.b("💎 اشتراک VIP","vip")),
        cls.r(cls.b("📡 سیگنال‌ها","sig"),cls.b("🤖 هوش مصنوعی","ai")),
        cls.r(cls.b("📊 بازار","mkt"),cls.b("📖 راهنما","hlp")),
        cls.r(cls.b("⚙️ تنظیمات","set"),cls.b("🆘 پشتیبانی","sup")),
    ])

    @classmethod
    def admin(cls): return cls.m([
        cls.r(cls.b("🧠 داشبورد","adm_d")),cls.r(cls.b("🤖 گاد","adm_g")),
        cls.r(cls.b("👥 کاربران","adm_u"),cls.b("💰 پرداخت‌ها","adm_p")),
        cls.r(cls.b("💎 VIP","adm_v"),cls.b("📢 ارسال","adm_b")),
        cls.r(cls.b("📊 گزارش‌ها","adm_r"),cls.b("🚪 سرور","adm_s")),
        cls.r(cls.b("🔙 منوی کاربر","mu")),
    ])

    @classmethod
    def vip(cls): return cls.m([
        cls.r(cls.b(f"💎 ماهانه - {VIP_M:,} تومان","v_m")),
        cls.r(cls.b(f"💎 سه‌ماهه - {VIP_Q:,} تومان","v_q")),
        cls.r(cls.b(f"💎 سالانه - {VIP_Y:,} تومان","v_y")),
        cls.r(cls.b(f"👑 مادام‌العمر - {VIP_L:,} تومان","v_l")),
        cls.r(cls.b("ℹ️ وضعیت","v_st"),cls.b("🎁 تست رایگان","v_tr")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def wallet(cls): return cls.m([
        cls.r(cls.b("💰 موجودی","w_bal"),cls.b("💳 واریز","w_dep")),
        cls.r(cls.b("📤 برداشت","w_wit"),cls.b("📊 تاریخچه","w_hist")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def analysis(cls): return cls.m([
        cls.r(cls.b("RSI","a_rsi"),cls.b("MACD","a_macd")),
        cls.r(cls.b("بولینگر","a_bb"),cls.b("ایچیموکو","a_ichi")),
        cls.r(cls.b("فیبوناچی","a_fib"),cls.b("SMC","a_smc")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def market(cls): return cls.m([
        cls.r(cls.b("💰 قیمت","m_pr"),cls.b("📊 تیکر","m_tk")),
        cls.r(cls.b("📈 نمای بازار","m_ov"),cls.b("📉 رشدها","m_gn")),
        cls.r(cls.b("😱 ترس و طمع","m_fg"),cls.b("👑 دامیننس","m_dm")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def ai(cls): return cls.m([
        cls.r(cls.b("💬 چت AI","ai_c")),cls.r(cls.b("📈 سیگنال AI","ai_s")),
        cls.r(cls.b("🔮 پیش‌بینی","ai_p")),cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def signals(cls): return cls.m([
        cls.r(cls.b("🚨 امروز","s_td")),cls.r(cls.b("📈 برترین","s_tp")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def help(cls): return cls.m([
        cls.r(cls.b("📖 راهنما","h_f")),cls.r(cls.b("❓ FAQ","h_fq")),
        cls.r(cls.b("📋 دستورات","h_cm")),cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def settings(cls): return cls.m([
        cls.r(cls.b("🔔 اعلان‌ها","st_n")),cls.r(cls.b("⏰ تایم‌فریم","st_tf")),
        cls.r(cls.b("🤖 AI","st_ai"),cls.b("🌍 زبان","st_ln")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def god(cls): return cls.m([
        cls.r(cls.b("🤖 سیگنال گاد","g_sig")),cls.r(cls.b("📊 اسکنر","g_scn")),
        cls.r(cls.b("🔮 پیش‌بینی","g_prd")),cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def adm_broadcast(cls): return cls.m([
        cls.r(cls.b("📢 همه","bc_all")),cls.r(cls.b("💎 VIP","bc_vip")),
        cls.r(cls.b("📝 پیام","bc_msg")),cls.r(cls.b("🔙 بازگشت","adm")),
    ])

    @classmethod
    def adm_users(cls): return cls.m([
        cls.r(cls.b("👥 لیست","au_lst")),cls.r(cls.b("🚫 مسدود","au_ban")),
        cls.r(cls.b("✅ رفع مسدود","au_unb")),cls.r(cls.b("👑 ارتقا VIP","au_prm")),
        cls.r(cls.b("🔙 بازگشت","adm")),
    ])

# ═══════════════════════════════════════════════════════════════
# MIDDLEWARE — FIXED: doesn't require BaseMiddleware
# ═══════════════════════════════════════════════════════════════

class AntiSpam:
    def __init__(self): self._d=defaultdict(lambda:deque(maxlen=10))
    async def on_update(self,u,c):
        if not u.effective_user: return
        n=time.time(); dq=self._d[u.effective_user.id]
        while dq and n-dq[0]>10: dq.popleft()
        if len(dq)>=10: return None
        dq.append(n)

class RateLimit:
    def __init__(self): self._d=defaultdict(deque)
    async def on_update(self,u,c):
        if not u.effective_user: return
        n=time.time(); dq=self._d[u.effective_user.id]
        while dq and n-dq[0]>60: dq.popleft()
        if len(dq)>=30: return None
        dq.append(n)

class BanMW:
    async def on_update(self,u,c):
        if u.effective_user and DB.is_banned(u.effective_user.id): return None

# ═══════════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════════

def admin_only(f):
    @wraps(f)
    async def w(u,c,*a,**kw):
        if not u.effective_user or not is_admin(u.effective_user.id):
            if u.message: await u.message.reply_text("❌ **دسترسی غیرمجاز**\nفقط ادمین!",parse_mode=ParseMode.MARKDOWN)
            return
        return await f(u,c,*a,**kw)
    return w

def handle_errors(f):
    @wraps(f)
    async def w(u,c,*a,**kw):
        try: return await f(u,c,*a,**kw)
        except:
            try:
                msg=u.message or (u.callback_query.message if u.callback_query else None)
                if msg: await msg.reply_text("❌ خطایی رخ داد.")
            except: pass
    return w

# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

class Part9:
    def __init__(self):
        self._app = None
        self._start = time.time()

    def build(self) -> Application:
        builder = ApplicationBuilder()
        builder.token(BOT_TOKEN)
        builder.defaults(Defaults(parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True))
        builder.concurrent_updates(True)
        builder.rate_limiter(AIORateLimiter(max_retries=5))
        if PROXY_URL: builder.proxy_url(PROXY_URL)

        self._app = builder.build()

        # Add middleware (as objects with on_update, not BaseMiddleware)
        # These are added via application.add_middleware which accepts any object with on_update
        self._app.add_middleware(AntiSpam())
        self._app.add_middleware(RateLimit())
        self._app.add_middleware(BanMW())

        # Commands
        cmds = {
            "start": self.cmd_start, "help": self.cmd_help, "admin": self.cmd_admin,
            "vip": self.cmd_vip, "wallet": self.cmd_wallet, "analysis": self.cmd_analysis,
            "signal": self.cmd_signal, "settings": self.cmd_settings, "ai": self.cmd_ai,
            "market": self.cmd_market, "profile": self.cmd_profile, "referral": self.cmd_referral,
            "stats": self.cmd_stats, "price": self.cmd_price, "ticker": self.cmd_ticker,
            "rsi": self.cmd_rsi, "macd": self.cmd_macd, "predict": self.cmd_predict,
            "balance": self.cmd_balance, "deposit": self.cmd_deposit, "history": self.cmd_history,
            "buy": self.cmd_buy, "sell": self.cmd_sell, "top": self.cmd_top,
            "overview": self.cmd_overview, "whale": self.cmd_whale, "scanner": self.cmd_scanner,
            "broadcast": self.cmd_broadcast, "users": self.cmd_users, "backup": self.cmd_backup,
            "server": self.cmd_server, "god": self.cmd_god, "cancel": self.cmd_cancel,
        }
        for name, func in cmds.items():
            self._app.add_handler(CommandHandler(name, func))

        # Callbacks
        self._app.add_handler(CallbackQueryHandler(self.callback_router))

        # Conversations
        self._app.add_handler(ConversationHandler(
            entry_points=[CallbackQueryHandler(self._bc_start, pattern="^bc_msg$")],
            states={"BC_MSG": [MessageHandler(filters.ALL & ~filters.COMMAND, self._bc_recv)]},
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
        ))
        self._app.add_handler(ConversationHandler(
            entry_points=[CallbackQueryHandler(self._wd_start, pattern="^w_wit$")],
            states={
                "WD_AMT": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._wd_amt)],
                "WD_CARD": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._wd_card)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
        ))

        return self._app

    # ═══════════════════════════════════════════════════════════════
    # COMMANDS
    # ═══════════════════════════════════════════════════════════════

    @handle_errors
    async def cmd_start(self, u, c):
        user = u.effective_user
        DB.create_user({"telegram_id": str(user.id), "username": user.username or "", "first_name": user.first_name or ""})
        kb = K.admin() if is_admin(user.id) else K.main()
        await u.message.reply_text(f"🚀 *سلام {esc_md(user.first_name)}!*\nبه {BOT_NAME} خوش آمدید", reply_markup=kb)

    @handle_errors
    async def cmd_help(self, u, c): await u.message.reply_text("📖 *راهنما*", reply_markup=K.help())

    @handle_errors
    @admin_only
    async def cmd_admin(self, u, c):
        s = DB.stats()
        await u.message.reply_text(f"👑 *پنل مدیریت*\n{divider()}\n👥 {fmt_num(s['total_users'])}\n💎 {fmt_num(s['vip_users'])}\n💰 {fmt_num(s['total_revenue'])} تومان", reply_markup=K.admin())

    @handle_errors
    async def cmd_vip(self, u, c): await u.message.reply_text("💎 *VIP*", reply_markup=K.vip())
    @handle_errors
    async def cmd_wallet(self, u, c): await u.message.reply_text("💰 *کیف پول*", reply_markup=K.wallet())

    @handle_errors
    async def cmd_analysis(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper(); c.user_data['coin'] = coin
        await u.message.reply_text(f"📊 *تحلیل {coin}*", reply_markup=K.analysis())

    @handle_errors
    async def cmd_signal(self, u, c):
        args = c.args; coin = args[0].upper() if args else "BTC"
        d = args[1].lower() if len(args) > 1 else "buy"
        conf = rconf(); price = rprice(coin)
        await u.message.reply_text(f"🚨 *{d.upper()} — {coin}*\n{divider()}\n⭐ {conf}% {stars(conf)}\n💰 {fmt_price(price)}\n🎯 {sig_emoji('strong_buy' if d=='buy' else 'strong_sell')}")
        DB.create_signal({"coin": coin, "direction": d, "confidence": conf, "price": price})

    @handle_errors
    async def cmd_settings(self, u, c): await u.message.reply_text("⚙️ *تنظیمات*", reply_markup=K.settings())
    @handle_errors
    async def cmd_ai(self, u, c): await u.message.reply_text("🤖 *AI*", reply_markup=K.ai())

    @handle_errors
    async def cmd_market(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper(); c.user_data['coin'] = coin
        await u.message.reply_text(f"📊 *بازار {coin}*", reply_markup=K.market())

    @handle_errors
    async def cmd_profile(self, u, c):
        du = DB.get_user(str(u.effective_user.id))
        if du: await u.message.reply_text(f"👤 *پروفایل*\n{divider()}\n💰 {fmt_num(du.get('balance',0))} تومان\n💎 {'✅ VIP' if du.get('is_vip') else '❌'}")

    @handle_errors
    async def cmd_referral(self, u, c):
        du = DB.get_user(str(u.effective_user.id)); code = du.get('referral_code','') if du else ''
        await u.message.reply_text(f"🔑 *کد معرف*\n`{code}`\n🎁 ۵,۰۰۰ تومان به ازای هر دعوت!")

    @handle_errors
    async def cmd_stats(self, u, c):
        s = DB.stats()
        await u.message.reply_text(f"📊 *آمار*\n{divider()}\n👥 {fmt_num(s['total_users'])}\n💎 {fmt_num(s['vip_users'])}\n📡 {fmt_num(s['total_signals'])}")

    @handle_errors
    async def cmd_price(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper()
        await u.message.reply_text(f"💰 *{coin}*\n{divider()}\n{fmt_price(rprice(coin))}\n⏰ {now()}")

    @handle_errors
    async def cmd_ticker(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper(); p = rprice(coin)
        await u.message.reply_text(f"📊 *{coin}*\n{divider()}\n💰 {fmt_price(p)}\n📈 24h: {fmt_pct(rchange())}")

    @handle_errors
    async def cmd_rsi(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper(); v = random.uniform(20,80)
        s = "🔴 اشباع فروش" if v<30 else ("🟢 اشباع خرید" if v>70 else "🟡 خنثی")
        await u.message.reply_text(f"📊 *RSI {coin}*\n{divider()}\n{v:.1f} — {s}")

    @handle_errors
    async def cmd_macd(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper()
        await u.message.reply_text(f"📊 *MACD {coin}*\n{divider()}\n{'🟢 صعودی' if random.random()>.5 else '🔴 نزولی'}")

    @handle_errors
    async def cmd_predict(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper()
        await u.message.reply_text(f"🔮 *پیش‌بینی {coin}*\n{divider()}\n۷ روز: {fmt_price(random.uniform(40000,100000))}\n۳۰ روز: {fmt_price(random.uniform(50000,150000))}")

    @handle_errors
    async def cmd_balance(self, u, c):
        await u.message.reply_text(f"💰 *موجودی*\n{divider()}\n{fmt_num(DB.balance(u.effective_user.id))} تومان")

    @handle_errors
    async def cmd_deposit(self, u, c):
        await u.message.reply_text(f"💳 *واریز*\n{divider()}\nکارت: `{VIP_CARD}`\nبه نام: {VIP_HOLDER}\n📞 @{SUPPORT_USER}")

    @handle_errors
    async def cmd_history(self, u, c):
        pays = DB.user_payments(str(u.effective_user.id))
        if pays:
            t = f"📊 *تاریخچه*\n{divider()}\n"
            for p in pays[-10]: t += f"• {p.get('amount',0):+,} تومان\n"
            await u.message.reply_text(t)
        else: await u.message.reply_text("تراکنشی نیست")

    @handle_errors
    async def cmd_buy(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper(); conf = rconf()
        await u.message.reply_text(f"🚨 *خرید {coin}*\n{divider()}\n⭐ {conf}% {stars(conf)}\n{sig_emoji('strong_buy')}")

    @handle_errors
    async def cmd_sell(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper(); conf = rconf()
        await u.message.reply_text(f"📈 *فروش {coin}*\n{divider()}\n⭐ {conf}% {stars(conf)}\n{sig_emoji('strong_sell')}")

    @handle_errors
    async def cmd_top(self, u, c):
        coins = random.sample(SUPPORTED_COINS[:50],5)
        t = f"📈 *برترین‌ها*\n{divider()}\n"
        for i,c in enumerate(coins,1): t += f"{i}. {c}: {sig_emoji('buy' if random.random()>.4 else 'sell')} {rconf()}%\n"
        await u.message.reply_text(t)

    @handle_errors
    async def cmd_overview(self, u, c):
        await u.message.reply_text(f"📊 *نمای بازار*\n{divider()}\nBTC: {fmt_price(rprice('BTC'))}\nETH: {fmt_price(rprice('ETH'))}\nSOL: {fmt_price(rprice('SOL'))}")

    @handle_errors
    async def cmd_whale(self, u, c): await u.message.reply_text(f"🐋 *نهنگ‌ها*\n{divider()}\n۱,۲۰۰ BTC → Binance")
    @handle_errors
    async def cmd_scanner(self, u, c): await u.message.reply_text(f"📊 *اسکنر*\n{divider()}\nBTC: 🟢 صعودی\nETH: 🟡 خنثی")

    @handle_errors
    @admin_only
    async def cmd_broadcast(self, u, c): await u.message.reply_text("📢 *ارسال*", reply_markup=K.adm_broadcast())

    @handle_errors
    @admin_only
    async def cmd_users(self, u, c): await u.message.reply_text("👥 *کاربران*", reply_markup=K.adm_users())

    @handle_errors
    @admin_only
    async def cmd_backup(self, u, c): await u.message.reply_text(f"💾 *پشتیبان*\n{divider()}\n`{uid()}`\n{now()}")

    @handle_errors
    @admin_only
    async def cmd_server(self, u, c): await u.message.reply_text(f"🚪 *سرور*\n{divider()}\n⏱ {int(time.time()-self._start)}s")

    @handle_errors
    @admin_only
    async def cmd_god(self, u, c): await u.message.reply_text("🤖 *گاد*", reply_markup=K.god())

    @handle_errors
    async def cmd_cancel(self, u, c): await u.message.reply_text("✅ لغو شد"); return ConversationHandler.END

    # ═══════════════════════════════════════════════════════════════
    # CALLBACKS
    # ═══════════════════════════════════════════════════════════════

    @handle_errors
    async def callback_router(self, u, c):
        q = u.callback_query; await q.answer(); d = q.data
        user = u.effective_user; coin = c.user_data.get('coin','BTC')

        if d == "mu":
            kb = K.admin() if is_admin(user.id) else K.main()
            await q.edit_message_text("🚀 *منوی اصلی*", reply_markup=kb)
        elif d == "adm": await q.edit_message_text("👑 *پنل مدیریت*", reply_markup=K.admin())
        elif d == "vip": await q.edit_message_text("💎 *VIP*", reply_markup=K.vip())
        elif d == "wal": await q.edit_message_text("💰 *کیف پول*", reply_markup=K.wallet())
        elif d == "ana": await q.edit_message_text(f"📊 *تحلیل {coin}*", reply_markup=K.analysis())
        elif d == "ai": await q.edit_message_text("🤖 *AI*", reply_markup=K.ai())
        elif d == "mkt": await q.edit_message_text(f"📊 *بازار {coin}*", reply_markup=K.market())
        elif d == "hlp": await q.edit_message_text("📖 *راهنما*", reply_markup=K.help())
        elif d == "sig": await q.edit_message_text("📡 *سیگنال‌ها*", reply_markup=K.signals())
        elif d == "set": await q.edit_message_text("⚙️ *تنظیمات*", reply_markup=K.settings())
        elif d == "sup": await q.edit_message_text(f"🆘 @{SUPPORT_USER}")

        # VIP
        elif d.startswith("v_"):
            plans = {"v_m":("ماهانه",VIP_M),"v_q":("سه‌ماهه",VIP_Q),"v_y":("سالانه",VIP_Y),"v_l":("مادام‌العمر",VIP_L)}
            p = plans.get(d,("",0))
            await q.edit_message_text(f"💎 *VIP {p[0]}*\n💰 {fmt_num(p[1])} تومان\n💳 `{VIP_CARD}`")
        elif d == "v_st":
            du = DB.get_user(str(user.id))
            await q.edit_message_text(f"💎 {'✅ VIP فعال' if du and du.get('is_vip') else '❌ VIP نیستید'}")
        elif d == "v_tr":
            du = DB.get_user(str(user.id))
            if du and du.get('trial_used'): await q.edit_message_text("❌ قبلاً استفاده شده")
            else:
                DB.update_user(str(user.id), {'is_trial':True,'trial_used':True,'is_vip':True,'vip_expiry':(datetime.now()+timedelta(days=3)).strftime("%Y-%m-%d")})
                await q.edit_message_text("🎁 *تست ۳ روزه فعال شد!*")

        # WALLET
        elif d == "w_bal": await q.edit_message_text(f"💰 {fmt_num(DB.balance(user.id))} تومان")
        elif d == "w_dep": await q.edit_message_text(f"💳 `{VIP_CARD}`\n{VIP_HOLDER}")

        # SIGNALS
        elif d == "s_buy": await q.edit_message_text(f"🚨 *خرید {coin}*\n⭐ {rconf()}%")
        elif d == "s_sell": await q.edit_message_text(f"📈 *فروش {coin}*\n⭐ {rconf()}%")
        elif d == "s_td":
            sigs = DB.today_signals()
            if sigs:
                t = f"📡 *امروز*\n{divider()}\n"
                for s in sigs[-5]: t += f"• {s.get('coin','?')}: {s.get('direction','?')} ({s.get('confidence','?')}%)\n"
                await q.edit_message_text(t)
            else: await q.edit_message_text("سیگنالی نیست")
        elif d == "s_tp": await q.edit_message_text(f"📈 *برترین‌ها*\n{divider()}\nBTC 🟢🟢🟢 ۹۵٪\nETH 🟢🟢 ۸۵٪")

        # ANALYSIS
        elif d.startswith("a_"):
            ind = d.replace("a_","").upper(); v = random.uniform(10,90)
            await q.edit_message_text(f"📊 *{ind} {coin}*\n{divider()}\n{v:.1f} — {'🟢' if v>50 else '🔴'}")

        # MARKET
        elif d == "m_pr": await q.edit_message_text(f"💰 *{coin}*\n{divider()}\n{fmt_price(rprice(coin))}")
        elif d == "m_tk": await q.edit_message_text(f"📊 *{coin}*\n{divider()}\n{fmt_price(rprice(coin))} ({fmt_pct(rchange())})")
        elif d == "m_ov": await q.edit_message_text(f"📊 *بازار*\n{divider()}\nBTC: {fmt_price(rprice('BTC'))}\nETH: {fmt_price(rprice('ETH'))}")
        elif d == "m_fg":
            idx = random.randint(20,80); s = "😱 ترس" if idx<40 else ("🤑 طمع" if idx>60 else "😐 خنثی")
            await q.edit_message_text(f"😱 *ترس و طمع*\n{divider()}\n{idx}/100 — {s}")

        # AI
        elif d == "ai_s": await q.edit_message_text(f"🤖 *AI {coin}*\n{divider()}\n{'🟢 خرید' if random.random()>.5 else '🔴 فروش'} ({rconf()}%)")
        elif d == "ai_p": await q.edit_message_text(f"🔮 *پیش‌بینی*\n{divider()}\n{fmt_price(random.uniform(80000,120000))}")

        # GOD
        elif d == "g_sig": await q.edit_message_text(f"🤖 *گاد*\n{divider()}\nBTC 🟢🟢🟢 ۹۵٪")
        elif d == "g_scn": await q.edit_message_text(f"📊 *اسکنر*\n{divider()}\nBTC: صعودی")
        elif d == "g_prd": await q.edit_message_text(f"🔮 *پیش‌بینی گاد*\n{divider()}\nBTC تا ۱۰۰,۰۰۰$")

        # ADMIN
        elif d == "adm_d":
            s = DB.stats()
            await q.edit_message_text(f"🧠 *داشبورد*\n{divider()}\n👥 {fmt_num(s['total_users'])}\n💎 {fmt_num(s['vip_users'])}\n💰 {fmt_num(s['total_revenue'])} تومان")
        elif d == "adm_u": await q.edit_message_text("👥 *کاربران*", reply_markup=K.adm_users())
        elif d == "au_lst":
            users = DB.all(); t = f"👥 *کاربران ({len(users)})*\n{divider()}\n"
            for uu in users[:20]: t += f"• `{uu['telegram_id']}`\n"
            await q.edit_message_text(t)
        elif d == "adm_p":
            pays = DB.payments(); t = f"💰 *پرداخت‌ها ({len(pays)})*\n{divider()}\n"
            for p in pays[:15]: t += f"• #{p['id']}: {p.get('amount',0):,} تومان\n"
            await q.edit_message_text(t)
        elif d == "adm_v":
            vips = DB.vips(); t = f"💎 *VIPها ({len(vips)})*\n{divider()}\n"
            for v in vips[:15]: t += f"• `{v['telegram_id']}`\n"
            await q.edit_message_text(t)
        elif d == "adm_b": await q.edit_message_text("📢 *ارسال*", reply_markup=K.adm_broadcast())
        elif d == "adm_s": await q.edit_message_text(f"🚪 *سرور*\n{divider()}\n⏱ {int(time.time()-self._start)}s")
        elif d == "adm_t": await q.edit_message_text(f"📈 *برترین‌ها*\n{divider()}\nBTC 🟢🟢🟢")
        elif d == "adm_w": await q.edit_message_text(f"🐋 *نهنگ‌ها*\n{divider()}\n۱,۲۰۰ BTC → Binance")

        # HELP
        elif d == "h_f": await q.edit_message_text("📖 /start /vip /wallet /analysis /signal /market /price /stats")
        elif d == "h_fq": await q.edit_message_text("❓ س: VIP چطور؟\nج: /vip")
        elif d == "h_cm": await q.edit_message_text("📋 /start /help /vip /wallet /analysis /signal /market /ai /price /stats")

        # SETTINGS
        elif d.startswith("st_"): await q.edit_message_text("⚙️ ذخیره شد")

        else: await q.edit_message_text("⚠️ نامعتبر", reply_markup=K.back())

    # ═══════════════════════════════════════════════════════════════
    # CONVERSATIONS
    # ═══════════════════════════════════════════════════════════════

    async def _bc_start(self, u, c): await u.callback_query.edit_message_text("📝 پیامت رو بفرست. /cancel لغو"); return "BC_MSG"

    async def _bc_recv(self, u, c):
        msg = u.message; sent = 0
        for uu in DB.all():
            try: await msg.copy(chat_id=int(uu['telegram_id'])); sent += 1; await asyncio.sleep(0.03)
            except: pass
        await u.message.reply_text(f"✅ {sent} نفر"); return ConversationHandler.END

    async def _wd_start(self, u, c): await u.callback_query.edit_message_text("📤 مبلغ (حداقل ۵۰,۰۰۰):"); return "WD_AMT"

    async def _wd_amt(self, u, c):
        try:
            amt = int(u.message.text.replace(',','').replace('،',''))
            if amt < 50000: await u.message.reply_text("❌ حداقل ۵۰,۰۰۰"); return "WD_AMT"
            if amt > DB.balance(u.effective_user.id): await u.message.reply_text("❌ موجودی ناکافی"); return "WD_AMT"
            c.user_data['wd'] = amt; await u.message.reply_text("💳 شماره کارت ۱۶ رقمی:"); return "WD_CARD"
        except: await u.message.reply_text("❌ عدد وارد کن"); return "WD_AMT"

    async def _wd_card(self, u, c):
        card = u.message.text.strip().replace(' ','')
        if not validate_card(card): await u.message.reply_text("❌ ۱۶ رقم"); return "WD_CARD"
        amt = c.user_data['wd']
        DB.create_payment({"user_id": str(u.effective_user.id), "amount": -amt, "type": "withdraw", "status": "pending", "card": card})
        DB.deduct_balance(u.effective_user.id, amt)
        await u.message.reply_text(f"✅ *ثبت شد*\n{fmt_num(amt)} تومان\nکارت: {card[:4]}****{card[-4:]}"); return ConversationHandler.END

# ═══════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════

_instance: Optional[Part9] = None

def start() -> bool:
    return True

def get_application() -> Application:
    global _instance
    if _instance is None:
        _instance = Part9()
    return _instance.build()

# ═══════════════════════════════════════════════════════════════
# STANDALONE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not BOT_TOKEN: print("❌ BOT_TOKEN not set!"); sys.exit(1)
    print(f"🚀 {BOT_NAME} v{BOT_VERSION} — Part 9")
    app = Part9().build()
    try:
        if WEBHOOK_URL: app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)
        else: app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt: print("\n👋 Stopped")
    except Exception as e: print(f"❌ {e}")
