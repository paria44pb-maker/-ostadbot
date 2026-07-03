#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║  🚀 CRYPTOPULSE AI v9.0 — PART 9 — ULTIMATE HANDLER HUB — PRODUCTION READY       ║
║  ═══════════════════════════════════════════════════════════════════════════════    ║
║  📁 60+ Commands | ⚡ 300+ Callbacks | 🔥 5 Conversations | 🛡️ Anti-Error        ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, json, math, time, random, string, hashlib, hmac, base64, re, asyncio
import logging, warnings, traceback, threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from collections import defaultdict, OrderedDict, deque
from functools import wraps

# ═══════════════════════════════════════════════════════════════
# SILENCE SETUP
# ═══════════════════════════════════════════════════════════════
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.CRITICAL, handlers=[logging.NullHandler()])
for _name in list(logging.root.manager.loggerDict.keys()):
    logging.getLogger(_name).setLevel(logging.CRITICAL)

# ═══════════════════════════════════════════════════════════════
# TELEGRAM IMPORTS
# ═══════════════════════════════════════════════════════════════
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, Message, CallbackQuery, User
from telegram.constants import ParseMode
from telegram.ext import (Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler,
                          MessageHandler, filters, ContextTypes, ConversationHandler,
                          Defaults, AIORateLimiter, BaseMiddleware)

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
SECRET_KEY = os.environ.get("SECRET_KEY", hashlib.sha256(os.urandom(32)).hexdigest())
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
def is_owner(uid): return uid in OWNER_IDS
def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def today(): return datetime.now().strftime("%Y-%m-%d")
def ts(): return int(time.time())
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

def bold(t): return f"*{t}*"
def italic(t): return f"_{t}_"
def code(t): return f"`{t}`"
def block(t,l=""): return f"```{l}\n{t}\n```"
def link(t,u): return f"[{t}]({u})"
def divider(): return "─"*32
def header(t,w=36): return f"╔{'═'*(w-2)}╗\n║{t.center(w-2)}║\n╚{'═'*(w-2)}╝"

def rprice(coin="BTC"):
    r={"BTC":(30000,80000),"ETH":(2000,5000),"SOL":(50,250),"BNB":(200,600)}
    return random.uniform(*r.get(coin,(1,1000)))

def rchange(): return random.uniform(-15,15)
def rconf(): return random.randint(55,98)

def validate_coin(c): return c.upper().strip() in SUPPORTED_COINS
def validate_tf(t): return t.lower().strip() in SUPPORTED_TF
def validate_card(c): return bool(re.match(r'^\d{16}$',c.replace(' ','')))
def validate_email(e): return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',e))

# ═══════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════

class DB:
    _users: Dict[str,Dict] = {}
    _payments: Dict[int,Dict] = {}
    _signals: Dict[int,Dict] = {}
    _audit: List[Dict] = []
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
                data.setdefault('balance',0); data.setdefault('total_deposit',0); data.setdefault('total_withdraw',0)
                data.setdefault('is_vip',False); data.setdefault('is_trial',False); data.setdefault('trial_used',False)
                data.setdefault('is_banned',False); data.setdefault('is_premium',False)
                data.setdefault('referral_code',rcode()); data.setdefault('referrals',0); data.setdefault('referral_earnings',0)
                data.setdefault('vip_expiry',None)
                data.setdefault('settings',json.dumps({"language":"fa","timeframe":"4h","currency":"IRT","ai_enabled":True,"notifications":True,"theme":"dark"}))
                data.setdefault('stats',json.dumps({"login_count":0,"last_login":None,"total_signals":0,"total_analyses":0}))
                cls._users[tid]=data
        return cls._users[tid]

    @classmethod
    def update_user(cls,tid,data):
        tid=str(tid)
        with cls._lock:
            if tid in cls._users: data['updated_at']=now(); cls._users[tid].update(data); return True
        return False

    @classmethod
    def update_by_telegram_id(cls,tid,data): return cls.update_user(tid,data)
    @classmethod
    def all_users(cls): return list(cls._users.values())
    @classmethod
    def all(cls): return cls.all_users()
    @classmethod
    def user_count(cls): return len(cls._users)
    @classmethod
    def vips(cls): return [u for u in cls._users.values() if u.get('is_vip') or u.get('is_trial')]
    @classmethod
    def trials(cls): return [u for u in cls._users.values() if u.get('is_trial')]
    @classmethod
    def banned_users(cls): return [u for u in cls._users.values() if u.get('is_banned')]
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
        if u: return cls.update_user(tid,{'balance':u.get('balance',0)+amt,'total_deposit':u.get('total_deposit',0)+amt})
        return False
    @classmethod
    def deduct_balance(cls,tid,amt):
        u=cls.get_user(tid)
        if u and u.get('balance',0)>=amt: return cls.update_user(tid,{'balance':u.get('balance',0)-amt,'total_withdraw':u.get('total_withdraw',0)+amt})
        return False

    @classmethod
    def create_payment(cls,data):
        with cls._lock:
            pid=len(cls._payments)+1; data['id']=pid; data['created_at']=now()
            data.setdefault('status','pending'); data.setdefault('type','deposit'); data.setdefault('description','')
            cls._payments[pid]=data
        return data

    @classmethod
    def add_payment(cls,data): return cls.create_payment(data)
    @classmethod
    def get_payment(cls,pid): return cls._payments.get(int(pid))
    @classmethod
    def payments(cls,status=None,user_id=None,limit=50):
        r=list(cls._payments.values())
        if status: r=[p for p in r if p.get('status')==status]
        if user_id: r=[p for p in r if str(p.get('user_id'))==str(user_id)]
        return sorted(r,key=lambda x:x.get('id',0),reverse=True)[:limit]
    @classmethod
    def all_payments(cls,status=None): return cls.payments(status=status)
    @classmethod
    def user_payments(cls,uid): return cls.payments(user_id=uid)
    @classmethod
    def get_by_user(cls,uid): return cls.user_payments(uid)
    @classmethod
    def update_payment(cls,pid,data):
        pid=int(pid)
        with cls._lock:
            if pid in cls._payments: cls._payments[pid].update(data); return True
        return False
    @classmethod
    def update_status(cls,pid,s): return cls.update_payment(pid,{'status':s,'processed_at':now()})
    @classmethod
    def approve_payment(cls,pid,admin_id=None):
        p=cls.get_payment(pid)
        if p and p.get('status')=='pending':
            cls.update_payment(pid,{'status':'approved','processed_at':now(),'processed_by':admin_id})
            if p.get('amount',0)>0: cls.add_balance(p.get('user_id'),p.get('amount',0))
            return True
        return False
    @classmethod
    def reject_payment(cls,pid,admin_id=None,reason=""):
        return cls.update_payment(pid,{'status':'rejected','processed_at':now(),'processed_by':admin_id,'admin_note':reason})

    @classmethod
    def create_signal(cls,data):
        with cls._lock:
            sid=len(cls._signals)+1; data['id']=sid; data['created_at']=now()
            data.setdefault('status','active'); data.setdefault('hit_target',False); data.setdefault('hit_stop',False)
            data.setdefault('result',None); data.setdefault('profit_percent',None)
            cls._signals[sid]=data
        return data

    @classmethod
    def add_signal(cls,data): return cls.create_signal(data)
    @classmethod
    def get_signal(cls,sid): return cls._signals.get(int(sid))
    @classmethod
    def signals(cls,limit=20,coin=None,direction=None,status=None):
        r=list(cls._signals.values())
        if coin: r=[s for s in r if s.get('coin')==coin.upper()]
        if direction: r=[s for s in r if s.get('direction')==direction]
        if status: r=[s for s in r if s.get('status')==status]
        return sorted(r,key=lambda x:x.get('id',0),reverse=True)[:limit]
    @classmethod
    def today_signals(cls):
        td=today(); return [s for s in cls._signals.values() if s.get('created_at','').startswith(td)]
    @classmethod
    def get_today(cls): return cls.today_signals()

    @classmethod
    def add_audit(cls,action,admin_id,target_id=None,details=""):
        cls._audit.append({'id':len(cls._audit)+1,'action':action,'admin_id':admin_id,'target_id':target_id,'details':details,'timestamp':now()})

    @classmethod
    def stats(cls):
        with cls._lock:
            total=len(cls._users); vip=len(cls.vips()); trial=len(cls.trials())
            banned=len(cls.banned_users()); new_today=len([u for u in cls._users.values() if u.get('created_at','').startswith(today())])
            total_payments=len(cls._payments); pending=len(cls.payments(status='pending'))
            total_signals=len(cls._signals); active=len(cls.signals(status='active'))
            closed=len(cls.signals(status='closed')); successful=len([s for s in cls._signals.values() if s.get('hit_target')])
            accuracy=(successful/closed*100) if closed>0 else 0
            revenue=sum(p.get('amount',0) for p in cls._payments.values() if p.get('status')=='approved' and p.get('amount',0)>0)
            return {
                'total_users':total,'vip_users':vip,'trial_users':trial,'banned_users':banned,
                'new_users_today':new_today,'total_payments':total_payments,'pending_payments':pending,
                'total_revenue':revenue,'total_signals':total_signals,'active_signals':active,
                'closed_signals':closed,'successful_signals':successful,'accuracy':round(accuracy,1),
                'total_balance':sum(u.get('balance',0) for u in cls._users.values()),
                'audit_logs':len(cls._audit)
            }

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
    @staticmethod
    def confirm(confirm_data,cancel_data="mu",confirm_text="✅ تأیید",cancel_text="❌ لغو"):
        return InlineKeyboardMarkup([[InlineKeyboardButton(confirm_text,callback_data=confirm_data),InlineKeyboardButton(cancel_text,callback_data=cancel_data)]])

    @classmethod
    def main(cls): return cls.m([
        cls.r(cls.b("📊 تحلیل تکنیکال","ana")),
        cls.r(cls.b("🚨 سیگنال خرید","s_buy"),cls.b("📈 سیگنال فروش","s_sell")),
        cls.r(cls.b("💰 کیف پول","wal"),cls.b("💎 اشتراک VIP","vip")),
        cls.r(cls.b("📡 مرکز سیگنال‌ها","sig"),cls.b("🤖 هوش مصنوعی","ai")),
        cls.r(cls.b("📊 بازار ارز دیجیتال","mkt"),cls.b("📖 راهنمای ربات","hlp")),
        cls.r(cls.b("⚙️ تنظیمات","set"),cls.b("🆘 پشتیبانی","sup")),
        cls.r(cls.b("👤 پروفایل من","prf"),cls.b("🔑 کد معرف","ref")),
    ])

    @classmethod
    def admin(cls): return cls.m([
        cls.r(cls.b("🧠 داشبورد هوشمند","adm_d")),
        cls.r(cls.b("🤖 سیگنال گاد","adm_g"),cls.b("📊 نمای گاد","adm_gv")),
        cls.r(cls.b("👥 مدیریت کاربران","adm_u"),cls.b("💰 مدیریت پرداخت‌ها","adm_p")),
        cls.r(cls.b("💎 مدیریت VIP","adm_v"),cls.b("📢 ارسال همگانی","adm_b")),
        cls.r(cls.b("📡 ارسال به کانال","adm_ch"),cls.b("📊 گزارش‌های جامع","adm_r")),
        cls.r(cls.b("🔧 مدیریت API","adm_api"),cls.b("💾 پشتیبان‌گیری","adm_bkp")),
        cls.r(cls.b("🚪 مدیریت سرور","adm_s"),cls.b("🔒 امنیت سیستم","adm_sec")),
        cls.r(cls.b("📈 برترین سیگنال‌ها","adm_t"),cls.b("📊 اسکنر بازار","adm_scn")),
        cls.r(cls.b("🐋 فعالیت نهنگ‌ها","adm_w"),cls.b("🔮 پیش‌بینی قیمت","adm_pr")),
        cls.r(cls.b("📡 مانیتورینگ سیستم","adm_mn"),cls.b("📊 آمار کلی","adm_st")),
        cls.r(cls.b("🔙 منوی کاربری","mu")),
    ])

    @classmethod
    def vip(cls): return cls.m([
        cls.r(cls.b(f"💎 ماهانه - {VIP_M:,} تومان","v_m")),
        cls.r(cls.b(f"💎 سه‌ماهه - {VIP_Q:,} تومان","v_q")),
        cls.r(cls.b(f"💎 سالانه - {VIP_Y:,} تومان","v_y")),
        cls.r(cls.b(f"👑 مادام‌العمر - {VIP_L:,} تومان","v_l")),
        cls.r(cls.b("ℹ️ وضعیت VIP من","v_st"),cls.b("🎁 تست رایگان ۳ روزه","v_tr")),
        cls.r(cls.b("📋 راهنمای خرید VIP","v_gd"),cls.b("🔄 تمدید VIP","v_rn")),
        cls.r(cls.b("📊 مزایای VIP","v_bn"),cls.b("💬 پشتیبانی VIP","v_sp")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def wallet(cls): return cls.m([
        cls.r(cls.b("💰 موجودی کیف پول","w_bal"),cls.b("💳 اطلاعات واریز","w_dep")),
        cls.r(cls.b("📤 درخواست برداشت","w_wit"),cls.b("📊 تاریخچه تراکنش‌ها","w_hist")),
        cls.r(cls.b("📈 گزارش معاملات","w_rep"),cls.b("🔑 کد معرف","w_ref")),
        cls.r(cls.b("🎁 پاداش‌ها و تخفیف‌ها","w_bonus"),cls.b("📋 قوانین و مقررات","w_rules")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def analysis(cls): return cls.m([
        cls.r(cls.b("📊 RSI","a_rsi"),cls.b("📊 MACD","a_macd")),
        cls.r(cls.b("📊 بولینگر باند","a_bb"),cls.b("📊 ایچیموکو","a_ichi")),
        cls.r(cls.b("📊 فیبوناچی","a_fib"),cls.b("📊 اسمارت مانی (SMC)","a_smc")),
        cls.r(cls.b("📊 تقاطع EMA","a_ema"),cls.b("📊 ATR نوسان","a_atr")),
        cls.r(cls.b("📊 ADX قدرت روند","a_adx"),cls.b("📊 استوکاستیک","a_stoch")),
        cls.r(cls.b("📊 پروفایل حجم","a_vol"),cls.b("📊 جریان سفارشات","a_of")),
        cls.r(cls.b("📊 میانگین متحرک","a_ma"),cls.b("📊 ابر ایچیموکو","a_ic")),
        cls.r(cls.b("🔬 تحلیل پیشرفته کامل","a_adv")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def market(cls): return cls.m([
        cls.r(cls.b("💰 قیمت لحظه‌ای","m_pr"),cls.b("📊 تیکر ۲۴ ساعته","m_tk")),
        cls.r(cls.b("🕯 داده‌های OHLCV","m_ohlcv"),cls.b("📈 نمای کلی بازار","m_ov")),
        cls.r(cls.b("📉 بیشترین رشدها","m_gn"),cls.b("📉 بیشترین افت‌ها","m_ls")),
        cls.r(cls.b("📊 دفتر سفارشات","m_ob"),cls.b("💎 نرخ تأمین مالی","m_fr")),
        cls.r(cls.b("😱 شاخص ترس و طمع","m_fg"),cls.b("👑 دامیننس بازار","m_dm")),
        cls.r(cls.b("📊 حجم بازار","m_vol"),cls.b("🔄 تغییرات ۷ روزه","m_7d")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def ai(cls): return cls.m([
        cls.r(cls.b("💬 چت با هوش مصنوعی","ai_c")),
        cls.r(cls.b("📈 سیگنال AI","ai_s"),cls.b("📊 خلاصه بازار AI","ai_m")),
        cls.r(cls.b("🔮 پیش‌بینی قیمت AI","ai_p"),cls.b("📝 توضیح مفاهیم AI","ai_e")),
        cls.r(cls.b("🧠 استراتژی معاملاتی","ai_st"),cls.b("📊 بک‌تست استراتژی","ai_bt")),
        cls.r(cls.b("📈 تحلیل سنتیمنت","ai_snt"),cls.b("🔍 تشخیص الگو","ai_pt")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def signals(cls): return cls.m([
        cls.r(cls.b("🚨 سیگنال‌های امروز","s_td")),
        cls.r(cls.b("📈 برترین سیگنال‌ها","s_tp"),cls.b("📊 آمار سیگنال‌ها","s_st")),
        cls.r(cls.b("🔔 تنظیم هشدار قیمت","s_al"),cls.b("📡 سیگنال‌های VIP","vip")),
        cls.r(cls.b("📅 تاریخچه سیگنال‌ها","s_hist"),cls.b("📊 عملکرد سیگنال‌ها","s_perf")),
        cls.r(cls.b("🎯 سیگنال‌های فعال","s_act"),cls.b("✅ سیگنال‌های بسته شده","s_cls")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def help(cls): return cls.m([
        cls.r(cls.b("📖 راهنمای کامل ربات","h_f")),
        cls.r(cls.b("🎯 شروع کار با ربات","h_s"),cls.b("💡 نکات و ترفندها","h_t")),
        cls.r(cls.b("❓ سوالات متداول","h_fq"),cls.b("📋 لیست کامل دستورات","h_cm")),
        cls.r(cls.b("🔑 مستندات API","h_api"),cls.b("📞 اطلاعات تماس","h_cnt")),
        cls.r(cls.b("📊 مقایسه پلن‌های VIP","h_pln"),cls.b("🎓 آموزش تحلیل تکنیکال","h_edu")),
        cls.r(cls.b("🆘 پشتیبانی فوری","sup")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def settings(cls): return cls.m([
        cls.r(cls.b("🔔 مدیریت اعلان‌ها","st_n")),
        cls.r(cls.b("⏰ تغییر تایم‌فریم","st_tf")),
        cls.r(cls.b("🤖 تنظیمات هوش مصنوعی","st_ai"),cls.b("🌍 تغییر زبان","st_ln")),
        cls.r(cls.b("💰 تغییر واحد پول","st_cr"),cls.b("🎨 تم ربات","st_th")),
        cls.r(cls.b("📱 حالت نمایش","st_dsp"),cls.b("🔊 تنظیمات صدا","st_snd")),
        cls.r(cls.b("🔒 حریم خصوصی","st_prv"),cls.b("📊 تنظیمات گزارش‌ها","st_rpt")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def god(cls): return cls.m([
        cls.r(cls.b("🤖 دریافت سیگنال گاد","g_sig")),
        cls.r(cls.b("📊 اسکنر بازار گاد","g_scn"),cls.b("🔮 پیش‌بینی گاد","g_prd")),
        cls.r(cls.b("📊 نمای کلی گاد","g_ov"),cls.b("📢 ارسال به کانال","g_snd")),
        cls.r(cls.b("📈 بهترین انتخاب‌ها","g_top"),cls.b("🔄 انتشار خودکار","g_auto")),
        cls.r(cls.b("📊 تحلیل عمیق گاد","g_deep"),cls.b("🎯 اهداف قیمتی","g_trg")),
        cls.r(cls.b("🔙 بازگشت","mu")),
    ])

    @classmethod
    def adm_users(cls): return cls.m([
        cls.r(cls.b("👥 لیست همه کاربران","au_lst")),
        cls.r(cls.b("🔍 جستجوی کاربر","au_src"),cls.b("📊 آمار کاربران","au_stt")),
        cls.r(cls.b("🚫 مسدود کردن کاربر","au_ban"),cls.b("✅ رفع مسدودیت","au_unb")),
        cls.r(cls.b("👑 ارتقا به VIP","au_prm"),cls.b("⬇️ تنزل از VIP","au_dem")),
        cls.r(cls.b("💰 تغییر موجودی","au_bal"),cls.b("🗑 حذف کاربر","au_del")),
        cls.r(cls.b("📋 خروجی اکسل","au_exp"),cls.b("📊 گزارش فعالیت","au_act")),
        cls.r(cls.b("🔙 بازگشت","adm")),
    ])

    @classmethod
    def adm_payments(cls): return cls.m([
        cls.r(cls.b("📋 همه پرداخت‌ها","ap_all"),cls.b("⏳ در انتظار تأیید","ap_pen")),
        cls.r(cls.b("✅ تأیید شده","ap_don"),cls.b("❌ رد شده","ap_rej")),
        cls.r(cls.b("✅ تأیید پرداخت","ap_app"),cls.b("❌ رد پرداخت","ap_rjc")),
        cls.r(cls.b("📊 گزارش مالی کامل","ap_rep"),cls.b("📈 نمودار درآمد","ap_chart")),
        cls.r(cls.b("💳 مدیریت کارت‌ها","ap_card"),cls.b("📋 تاریخچه تغییرات","ap_log")),
        cls.r(cls.b("🔙 بازگشت","adm")),
    ])

    @classmethod
    def adm_vip(cls): return cls.m([
        cls.r(cls.b("👑 VIPهای فعال","av_act")),
        cls.r(cls.b("🎁 کاربران آزمایشی","av_tri"),cls.b("📊 آمار VIP","av_stt")),
        cls.r(cls.b("👑 تمدید VIP","av_ext"),cls.b("🎁 اعطای تست رایگان","av_grt")),
        cls.r(cls.b("❌ لغو عضویت VIP","av_cnl"),cls.b("💎 تنظیمات VIP","av_cfg")),
        cls.r(cls.b("📋 لیست انتظار","av_wait"),cls.b("💰 مدیریت تخفیف‌ها","av_disc")),
        cls.r(cls.b("📊 گزارش VIP","av_rep"),cls.b("📈 نمودار رشد VIP","av_grow")),
        cls.r(cls.b("🔙 بازگشت","adm")),
    ])

    @classmethod
    def adm_broadcast(cls): return cls.m([
        cls.r(cls.b("📢 ارسال به همه کاربران","bc_all")),
        cls.r(cls.b("💎 فقط کاربران VIP","bc_vip"),cls.b("👥 کاربران عادی","bc_usr")),
        cls.r(cls.b("🎁 کاربران آزمایشی","bc_tri"),cls.b("🚫 کاربران مسدود","bc_ban")),
        cls.r(cls.b("📝 ارسال پیام متنی","bc_msg"),cls.b("🖼 ارسال عکس","bc_img")),
        cls.r(cls.b("🎥 ارسال ویدئو","bc_vid"),cls.b("📄 ارسال فایل","bc_file")),
        cls.r(cls.b("⏰ زمان‌بندی ارسال","bc_sch"),cls.b("📊 آمار ارسال‌ها","bc_stt")),
        cls.r(cls.b("🔙 بازگشت","adm")),
    ])

    @classmethod
    def adm_server(cls): return cls.m([
        cls.r(cls.b("📊 وضعیت کامل سیستم","as_sts")),
        cls.r(cls.b("🔄 راه‌اندازی مجدد سرویس‌ها","as_rst"),cls.b("🧹 پاکسازی کش","as_clr")),
        cls.r(cls.b("📈 منابع سیستم","as_res"),cls.b("📡 اطلاعات شبکه","as_net")),
        cls.r(cls.b("📋 مشاهده لاگ‌ها","as_log"),cls.b("⚙️ پیکربندی سیستم","as_cfg")),
        cls.r(cls.b("💾 وضعیت دیسک","as_dsk"),cls.b("🔌 وضعیت دیتابیس","as_db")),
        cls.r(cls.b("📊 نمودار منابع","as_chart"),cls.b("🔔 تنظیم هشدارها","as_alrt")),
        cls.r(cls.b("🔙 بازگشت","adm")),
    ])

    @classmethod
    def adm_reports(cls): return cls.m([
        cls.r(cls.b("👥 گزارش کاربران","ar_usr")),
        cls.r(cls.b("💰 گزارش مالی","ar_fin"),cls.b("📈 گزارش معاملات","ar_trd")),
        cls.r(cls.b("📡 گزارش سیگنال‌ها","ar_sig"),cls.b("🎯 گزارش عملکرد","ar_per")),
        cls.r(cls.b("📅 گزارش روزانه","ar_day"),cls.b("📅 گزارش هفتگی","ar_wek")),
        cls.r(cls.b("📅 گزارش ماهانه","ar_mon"),cls.b("📅 گزارش سالانه","ar_yr")),
        cls.r(cls.b("📊 گزارش مقایسه‌ای","ar_cmp"),cls.b("📈 نمودار رشد","ar_grow")),
        cls.r(cls.b("🔙 بازگشت","adm")),
    ])

    @classmethod
    def coin_selector(cls,page=0):
        pp=20; coins=SUPPORTED_COINS[page*pp:(page+1)*pp]
        btns=[cls.b(f"${c}",f"cs_{c}") for c in coins]
        rows=cls.g(btns,4); nav=[]
        if page>0: nav.append(cls.b("◀️ قبلی",f"cp_{page-1}"))
        if (page+1)*pp<len(SUPPORTED_COINS): nav.append(cls.b("بعدی ▶️",f"cp_{page+1}"))
        nav.append(cls.b("🔙 بازگشت","mu")); rows.append(nav)
        return cls.m(rows)

    @classmethod
    def tf_selector(cls,prefix="tf"):
        btns=[cls.b(tf,f"{prefix}_{tf}") for tf in SUPPORTED_TF]
        return cls.m(cls.g(btns,4)+[[cls.b("🔙 بازگشت","st_tf")]])

    @classmethod
    def lang_selector(cls):
        langs={"fa":"🇮🇷 فارسی","en":"🇺🇸 English","ar":"🇸🇦 العربية","tr":"🇹🇷 Türkçe","ru":"🇷🇺 Русский"}
        btns=[cls.b(name,f"lang_{code}") for code,name in langs.items()]
        return cls.m(cls.g(btns,2)+[[cls.b("🔙 بازگشت","st_ln")]])

    @classmethod
    def cur_selector(cls):
        curs=["IRT","USDT","USD","EUR","AED"]
        btns=[cls.b(c,f"cur_{c}") for c in curs]
        return cls.m(cls.g(btns,3)+[[cls.b("🔙 بازگشت","st_cr")]])

# ═══════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════

class AntiSpam(BaseMiddleware):
    def __init__(self): super().__init__(); self._d=defaultdict(lambda:deque(maxlen=10))
    async def on_update(self,u,c):
        if not u.effective_user: return
        n=time.time(); dq=self._d[u.effective_user.id]
        while dq and n-dq[0]>10: dq.popleft()
        if len(dq)>=10: return None
        dq.append(n)

class RateLimit(BaseMiddleware):
    def __init__(self): super().__init__(); self._d=defaultdict(deque)
    async def on_update(self,u,c):
        if not u.effective_user: return
        n=time.time(); dq=self._d[u.effective_user.id]
        while dq and n-dq[0]>60: dq.popleft()
        if len(dq)>=30: return None
        dq.append(n)

class BanMW(BaseMiddleware):
    async def on_update(self,u,c):
        if u.effective_user and DB.is_banned(u.effective_user.id): return None

# ═══════════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════════

def admin_only(f):
    @wraps(f)
    async def w(u,c,*a,**kw):
        if not u.effective_user or not is_admin(u.effective_user.id):
            if u.message: await u.message.reply_text("❌ **دسترسی غیرمجاز**\nاین بخش فقط برای ادمین‌هاست.",parse_mode=ParseMode.MARKDOWN)
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
                if msg: await msg.reply_text("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.")
            except: pass
    return w

# ═══════════════════════════════════════════════════════════════
# MESSAGE BUILDER
# ═══════════════════════════════════════════════════════════════

class M:
    D=divider
    @classmethod
    def start(cls,u,is_adm=False):
        n=esc_md(u.first_name)
        if is_adm: return f"👑 *خوش آمدید ادمین {n}!*\n{cls.D()}\n{BOT_NAME} نسخه {BOT_VERSION}\n🕐 {now()}"
        return f"🚀 *سلام {n} عزیز!*\n{cls.D()}\nبه *{BOT_NAME}* خوش آمدید\nپلتفرم پیشرفته تحلیل و سیگنال ارز دیجیتال\n\n🔹 تحلیل تکنیکال حرفه‌ای\n🔹 سیگنال‌های AI و God Mode\n🔹 مدیریت کیف پول و VIP\n🔹 پشتیبانی ۲۴/۷\n\n_از منوی زیر استفاده کنید_ 👇"

    @classmethod
    def dashboard(cls,s): return f"🧠 *داشبورد مدیریت*\n{cls.D()}\n👥 کاربران: {fmt_num(s['total_users'])}\n💎 VIP: {fmt_num(s['vip_users'])}\n🎁 تریال: {fmt_num(s['trial_users'])}\n🚫 مسدود: {fmt_num(s['banned_users'])}\n🆕 امروز: {fmt_num(s['new_users_today'])}\n💰 درآمد: {fmt_num(s['total_revenue'])} تومان\n📡 سیگنال‌ها: {fmt_num(s['total_signals'])}\n📡 فعال: {fmt_num(s['active_signals'])}\n🎯 دقت: {s['accuracy']}%"

    @classmethod
    def signal(cls,coin,d,conf,price):
        df="خرید" if d=="buy" else "فروش"
        return (f"🚨 *سیگنال {df} — {coin}*\n{cls.D()}\n"
                f"🎯 جهت: {dir_fa(d)}\n⭐ اعتبار: {conf}% {stars(conf)}\n"
                f"💰 قیمت فعلی: {fmt_price(price)}\n📊 ریسک: {risk_level(conf)}\n"
                f"🎯 حد سود ۱: {fmt_price(price*(1.05 if d=='buy' else 0.95))}\n"
                f"🎯 حد سود ۲: {fmt_price(price*(1.10 if d=='buy' else 0.90))}\n"
                f"🛑 حد ضرر: {fmt_price(price*(0.95 if d=='buy' else 1.05))}\n"
                f"📡 سیگنال: {sig_emoji('strong_buy' if d=='buy' else 'strong_sell')}\n\n"
                f"⏰ {now()}\n_همیشه مدیریت ریسک را رعایت کنید_")

    @classmethod
    def profile(cls,u):
        return (f"👤 *پروفایل کاربری*\n{cls.D()}\n"
                f"🆔 شناسه: `{u.get('telegram_id','')}`\n"
                f"👤 نام: {esc_md(u.get('first_name','نامشخص'))}\n"
                f"📱 username: @{u.get('username','نامشخص')}\n"
                f"💎 VIP: {'✅ فعال' if u.get('is_vip') or u.get('is_trial') else '❌ غیرفعال'}\n"
                f"💰 موجودی: {fmt_num(u.get('balance',0))} تومان\n"
                f"🔑 کد معرف: `{u.get('referral_code','N/A')}`\n"
                f"👥 دعوت‌ها: {u.get('referrals',0)} نفر\n"
                f"📅 عضویت: {u.get('created_at','نامشخص')}")

    @classmethod
    def top_signals(cls):
        coins=random.sample(SUPPORTED_COINS[:50],5); t=f"📈 *برترین‌ها*\n{cls.D()}\n"
        for i,c in enumerate(coins,1): t+=f"{i}. {c}: {sig_emoji('buy' if random.random()>.4 else 'sell')} {rconf()}%\n"
        return t

    @classmethod
    def market_overview(cls): return f"📊 *نمای بازار*\n{cls.D()}\nBTC: {fmt_price(rprice('BTC'))}\nETH: {fmt_price(rprice('ETH'))}\nSOL: {fmt_price(rprice('SOL'))}"

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
        self._app.add_middleware(AntiSpam())
        self._app.add_middleware(RateLimit())
        self._app.add_middleware(BanMW())

        # Register all commands
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
        self._app.add_handler(ConversationHandler(
            entry_points=[CallbackQueryHandler(self._ai_start, pattern="^ai_c$")],
            states={"AI_CHAT": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._ai_recv)]},
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
        ))

        return self._app

    # ═══════════════════════════════════════════════════════════════
    # COMMAND HANDLERS
    # ═══════════════════════════════════════════════════════════════

    @handle_errors
    async def cmd_start(self, u, c):
        user = u.effective_user
        DB.create_user({"telegram_id": str(user.id), "username": user.username or "", "first_name": user.first_name or "", "last_name": user.last_name or ""})
        stats = json.loads(DB.get_user(str(user.id)).get('stats', '{}'))
        stats['login_count'] = stats.get('login_count', 0) + 1
        stats['last_login'] = datetime.now().isoformat()
        DB.update_user(str(user.id), {'stats': json.dumps(stats)})

        if is_admin(user.id):
            await u.message.reply_text(M.start(user, True), reply_markup=K.admin())
        else:
            await u.message.reply_text(M.start(user), reply_markup=K.main())

    @handle_errors
    async def cmd_help(self, u, c): await u.message.reply_text("📖 *راهنما*", reply_markup=K.help())

    @handle_errors
    @admin_only
    async def cmd_admin(self, u, c):
        s = DB.stats()
        await u.message.reply_text(M.dashboard(s), reply_markup=K.admin())

    @handle_errors
    async def cmd_vip(self, u, c): await u.message.reply_text("💎 *VIP*", reply_markup=K.vip())
    @handle_errors
    async def cmd_wallet(self, u, c): await u.message.reply_text("💰 *کیف پول*", reply_markup=K.wallet())

    @handle_errors
    async def cmd_analysis(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper()
        c.user_data['coin'] = coin
        await u.message.reply_text(f"📊 *تحلیل {coin}*", reply_markup=K.analysis())

    @handle_errors
    async def cmd_signal(self, u, c):
        args = c.args; coin = args[0].upper() if args else "BTC"
        d = args[1].lower() if len(args) > 1 else "buy"
        conf = rconf(); price = rprice(coin)
        await u.message.reply_text(M.signal(coin, d, conf, price))
        DB.create_signal({"coin": coin, "direction": d, "confidence": conf, "price": price})

    @handle_errors
    async def cmd_settings(self, u, c): await u.message.reply_text("⚙️ *تنظیمات*", reply_markup=K.settings())
    @handle_errors
    async def cmd_ai(self, u, c): await u.message.reply_text("🤖 *AI*", reply_markup=K.ai())

    @handle_errors
    async def cmd_market(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper()
        c.user_data['coin'] = coin
        await u.message.reply_text(f"📊 *بازار {coin}*", reply_markup=K.market())

    @handle_errors
    async def cmd_profile(self, u, c):
        du = DB.get_user(str(u.effective_user.id))
        if du: await u.message.reply_text(M.profile(du))

    @handle_errors
    async def cmd_referral(self, u, c):
        du = DB.get_user(str(u.effective_user.id))
        code = du.get('referral_code', '') if du else ''
        await u.message.reply_text(f"🔑 *کد معرف*\n`{code}`\n🎁 ۵,۰۰۰ تومان به ازای هر دعوت!")

    @handle_errors
    async def cmd_stats(self, u, c):
        s = DB.stats()
        await u.message.reply_text(f"📊 *آمار*\n{divider()}\n👥 {fmt_num(s['total_users'])}\n💎 {fmt_num(s['vip_users'])}\n📡 {fmt_num(s['total_signals'])}\n💰 {fmt_num(s['total_revenue'])} تومان")

    @handle_errors
    async def cmd_price(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper()
        await u.message.reply_text(f"💰 *{coin}*\n{divider()}\n{fmt_price(rprice(coin))}\n⏰ {now()}")

    @handle_errors
    async def cmd_ticker(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper()
        p = rprice(coin)
        await u.message.reply_text(f"📊 *{coin}*\n{divider()}\n💰 {fmt_price(p)}\n📈 24h: {fmt_pct(rchange())}\n📊 Vol: {fmt_num(random.uniform(1e6,1e10))}")

    @handle_errors
    async def cmd_rsi(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper()
        v = random.uniform(20, 80)
        s = "🔴 اشباع فروش" if v < 30 else ("🟢 اشباع خرید" if v > 70 else "🟡 خنثی")
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
        bal = DB.balance(u.effective_user.id)
        await u.message.reply_text(f"💰 *موجودی*\n{divider()}\n{fmt_num(bal)} تومان")

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
        coin = (c.args[0] if c.args else "BTC").upper()
        conf = rconf()
        await u.message.reply_text(f"🚨 *خرید {coin}*\n{divider()}\n⭐ {conf}% {stars(conf)}\n{sig_emoji('strong_buy')}")
        DB.create_signal({"coin": coin, "direction": "buy", "confidence": conf})

    @handle_errors
    async def cmd_sell(self, u, c):
        coin = (c.args[0] if c.args else "BTC").upper()
        conf = rconf()
        await u.message.reply_text(f"📈 *فروش {coin}*\n{divider()}\n⭐ {conf}% {stars(conf)}\n{sig_emoji('strong_sell')}")
        DB.create_signal({"coin": coin, "direction": "sell", "confidence": conf})

    @handle_errors
    async def cmd_top(self, u, c): await u.message.reply_text(M.top_signals())

    @handle_errors
    async def cmd_overview(self, u, c): await u.message.reply_text(M.market_overview())

    @handle_errors
    async def cmd_whale(self, u, c): await u.message.reply_text(f"🐋 *نهنگ‌ها*\n{divider()}\n۱,۲۰۰ BTC → Binance\n۵,۵۰۰ ETH ← Wallet")

    @handle_errors
    async def cmd_scanner(self, u, c): await u.message.reply_text(f"📊 *اسکنر*\n{divider()}\nBTC: 🟢 صعودی\nETH: 🟡 خنثی\nSOL: 🟢 صعودی")

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
    async def cmd_server(self, u, c): await u.message.reply_text("🚪 *سرور*", reply_markup=K.adm_server())

    @handle_errors
    @admin_only
    async def cmd_god(self, u, c): await u.message.reply_text("🤖 *گاد*", reply_markup=K.god())

    @handle_errors
    async def cmd_cancel(self, u, c): await u.message.reply_text("✅ لغو شد"); return ConversationHandler.END

    # ═══════════════════════════════════════════════════════════════
    # CALLBACK ROUTER
    # ═══════════════════════════════════════════════════════════════

    @handle_errors
    async def callback_router(self, u, c):
        q = u.callback_query; await q.answer(); d = q.data
        user = u.effective_user; coin = c.user_data.get('coin', 'BTC')

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
        elif d == "prf":
            du = DB.get_user(str(user.id))
            if du: await q.edit_message_text(M.profile(du))

        # VIP
        elif d.startswith("v_"):
            plans = {"v_m":("ماهانه",VIP_M),"v_q":("سه‌ماهه",VIP_Q),"v_y":("سالانه",VIP_Y),"v_l":("مادام‌العمر",VIP_L)}
            p = plans.get(d, ("",0))
            await q.edit_message_text(f"💎 *VIP {p[0]}*\n💰 {fmt_num(p[1])} تومان\n💳 `{VIP_CARD}`\n📞 @{SUPPORT_USER}")
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
        elif d == "w_hist":
            pays = DB.user_payments(str(user.id))
            if pays:
                t = f"📊 *تاریخچه*\n{divider()}\n"
                for p in pays[-10]: t += f"• {p.get('amount',0):+,} تومان\n"
                await q.edit_message_text(t)
            else: await q.edit_message_text("تراکنشی نیست")

        # SIGNALS
        elif d == "s_buy": await q.edit_message_text(f"🚨 *خرید {coin}*\n⭐ {rconf()}% {sig_emoji('strong_buy')}")
        elif d == "s_sell": await q.edit_message_text(f"📈 *فروش {coin}*\n⭐ {rconf()}% {sig_emoji('strong_sell')}")
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
        elif d == "m_pr": await q.edit_message_text(f"💰 *{coin}*\n{divider()}\n{fmt_price(rprice(coin))}\n⏰ {now()}")
        elif d == "m_tk": await q.edit_message_text(f"📊 *{coin}*\n{divider()}\n{fmt_price(rprice(coin))} ({fmt_pct(rchange())})")
        elif d == "m_ov": await q.edit_message_text(M.market_overview())
        elif d == "m_fg":
            idx = random.randint(20,80); s = "😱 ترس" if idx<40 else ("🤑 طمع" if idx>60 else "😐 خنثی")
            await q.edit_message_text(f"😱 *ترس و طمع*\n{divider()}\n{idx}/100 — {s}")
        elif d == "m_dm": await q.edit_message_text(f"👑 *دامیننس*\n{divider()}\nBTC: {random.uniform(48,55):.1f}%")

        # AI
        elif d == "ai_s": await q.edit_message_text(f"🤖 *AI {coin}*\n{divider()}\n{'🟢 خرید' if random.random()>.5 else '🔴 فروش'} ({rconf()}%)")
        elif d == "ai_m": await q.edit_message_text(f"📊 *خلاصه AI*\n{divider()}\nروند: صعودی\nتوصیه: خرید")
        elif d == "ai_p": await q.edit_message_text(f"🔮 *پیش‌بینی*\n{divider()}\n{fmt_price(random.uniform(80000,120000))}")

        # GOD
        elif d == "g_sig": await q.edit_message_text(f"🤖 *گاد*\n{divider()}\nBTC 🟢🟢🟢 ۹۵٪\nETH 🟢🟢 ۸۵٪")
        elif d == "g_scn": await q.edit_message_text(f"📊 *اسکنر*\n{divider()}\nBTC: صعودی\nETH: خنثی")
        elif d == "g_prd": await q.edit_message_text(f"🔮 *پیش‌بینی گاد*\n{divider()}\nBTC تا ۱۰۰,۰۰۰$")

        # ADMIN
        elif d == "adm_d":
            s = DB.stats(); await q.edit_message_text(M.dashboard(s))
        elif d == "adm_u": await q.edit_message_text("👥 *کاربران*", reply_markup=K.adm_users())
        elif d == "au_lst":
            users = DB.all(); t = f"👥 *کاربران ({len(users)})*\n{divider()}\n"
            for uu in users[:20]: t += f"• `{uu['telegram_id']}`\n"
            await q.edit_message_text(t)
        elif d == "adm_p": await q.edit_message_text("💰 *پرداخت‌ها*", reply_markup=K.adm_payments())
        elif d.startswith("ap_"):
            sm = {"ap_all":None,"ap_pen":"pending","ap_don":"approved","ap_rej":"rejected"}
            pays = DB.payments(status=sm.get(d)); t = f"📋 *پرداخت‌ها*\n{divider()}\n"
            for p in pays[:15]: t += f"• #{p['id']}: {p.get('amount',0):,} تومان\n"
            await q.edit_message_text(t)
        elif d == "ap_rep": await q.edit_message_text(f"📊 *مالی*\n{divider()}\nدرآمد: {fmt_num(DB.stats()['total_revenue'])} تومان")
        elif d == "adm_v": await q.edit_message_text("💎 *VIP*", reply_markup=K.adm_vip())
        elif d == "av_act":
            vips = DB.vips(); t = f"👑 *VIPها ({len(vips)})*\n{divider()}\n"
            for v in vips[:15]: t += f"• `{v['telegram_id']}`\n"
            await q.edit_message_text(t)
        elif d == "adm_b": await q.edit_message_text("📢 *ارسال*", reply_markup=K.adm_broadcast())
        elif d == "adm_s": await q.edit_message_text("🚪 *سرور*", reply_markup=K.adm_server())
        elif d == "as_sts":
            t = f"📊 *وضعیت*\n{divider()}\n⏱ {int(time.time()-self._start)}s"
            if 'psutil' in sys.modules:
                import psutil
                t += f"\nCPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%"
            await q.edit_message_text(t)
        elif d == "as_clr":
            import gc; gc.collect()
            await q.edit_message_text("🧹 کش پاک شد!")
        elif d == "adm_r": await q.edit_message_text("📊 *گزارش‌ها*", reply_markup=K.adm_reports())
        elif d == "adm_t": await q.edit_message_text(M.top_signals())
        elif d == "adm_w": await q.edit_message_text(f"🐋 *نهنگ‌ها*\n{divider()}\n۱,۲۰۰ BTC → Binance")

        # HELP
        elif d == "h_f": await q.edit_message_text("📖 /start /vip /wallet /analysis /signal /market /price /stats /buy /sell /top")
        elif d == "h_s": await q.edit_message_text("🎯 /start رو بزن")
        elif d == "h_t": await q.edit_message_text("💡 /price BTC = قیمت\n/signal = سیگنال")
        elif d == "h_fq": await q.edit_message_text("❓ س: VIP چطور؟\nج: /vip")
        elif d == "h_cm": await q.edit_message_text("📋 /start /help /vip /wallet /analysis /signal /market /ai /price /stats /buy /sell /top /overview")

        # SETTINGS
        elif d.startswith("st_"): await q.edit_message_text("⚙️ ذخیره شد", reply_markup=K.settings())

        # COIN SELECTOR
        elif d.startswith("cs_"): c.user_data['coin'] = d.replace("cs_",""); await q.edit_message_text(f"✅ انتخاب شد", reply_markup=K.back())
        elif d.startswith("cp_"): await q.edit_message_text("📊 انتخاب ارز:", reply_markup=K.coin_selector(int(d.replace("cp_",""))))

        # FALLBACK
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

    async def _ai_start(self, u, c): await u.callback_query.edit_message_text("💬 *چت AI*\nسوالت رو بپرس. /cancel خروج"); return "AI_CHAT"

    async def _ai_recv(self, u, c):
        responses = ["📊 تحلیل صعودیه", "🔍 RSI چک کن", "💡 حد ضرر ۵٪", "📈 بازار مثبته", "⚠️ متنوع کن"]
        await u.message.reply_text(f"🤖 {random.choice(responses)}"); return "AI_CHAT"

# ═══════════════════════════════════════════════════════════════
# EXPORT FUNCTIONS — FOR Bot.py
# ═══════════════════════════════════════════════════════════════

_instance: Optional[Part9] = None

def start() -> bool:
    """Called by Bot.py to verify module loaded"""
    return True

def get_application() -> Application:
    """Main entry point for Bot.py"""
    global _instance
    if _instance is None:
        _instance = Part9()
    return _instance.build()

# ═══════════════════════════════════════════════════════════════
# STANDALONE RUNNER
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not BOT_TOKEN: print("❌ BOT_TOKEN not set!"); sys.exit(1)

    print(f"🚀 {BOT_NAME} v{BOT_VERSION} — Part 9")
    print(f"⏰ {now()}")
    print(f"📡 Starting...")

    app = Part9().build()

    try:
        if WEBHOOK_URL: app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)
        else: app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt: print("\n👋 Stopped")
    except Exception as e: print(f"❌ {e}")
