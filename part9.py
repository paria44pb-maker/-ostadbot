#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""PART 9 — MINIMAL WORKING VERSION"""

import os, sys, time, random, string, asyncio, json
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps

# ═══════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════
BOT_TOKEN = os.environ.get("BOT_TOKEN", "") or os.environ.get("BOT_TOKEN_MAIN", "")
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().lstrip('-').isdigit()]
SUPPORTED_COINS = ["BTC","ETH","BNB","SOL","XRP","ADA","DOGE","DOT","MATIC","SHIB","AVAX","LINK","UNI","ATOM","LTC"]
BOT_VERSION = "9.0.0"

# ═══════════════════════════════════════
# TELEGRAM
# ═══════════════════════════════════════
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, Defaults
)

# ═══════════════════════════════════════
# UTILS
# ═══════════════════════════════════════
def is_admin(uid): return uid in ADMIN_IDS
def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def uid(): return ''.join(random.choices(string.ascii_letters+string.digits,k=12))
def fmt_num(n): return f"{n:,}"
def fmt_price(p):
    if p>=1000: return f"${p:,.2f}"
    if p>=1: return f"${p:,.4f}"
    return f"${p:,.8f}"

# ═══════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════
class DB:
    users = {}; payments = []; signals = []
    @classmethod
    def get_user(cls,tid): return cls.users.get(str(tid))
    @classmethod
    def create_user(cls,data):
        tid=str(data.get('telegram_id'))
        if tid not in cls.users:
            data.setdefault('balance',0); data.setdefault('is_vip',False)
            data.setdefault('trial_used',False); data.setdefault('referral_code',uid()[:8])
            cls.users[tid]=data
    @classmethod
    def update_user(cls,tid,data):
        if str(tid) in cls.users: cls.users[str(tid)].update(data)
    @classmethod
    def all_users(cls): return list(cls.users.values())
    @classmethod
    def vips(cls): return [u for u in cls.users.values() if u.get('is_vip')]
    @classmethod
    def stats(cls): return {'users':len(cls.users),'vip':len(cls.vips()),'signals':len(cls.signals)}

# ═══════════════════════════════════════
# KEYBOARDS
# ═══════════════════════════════════════
class K:
    @staticmethod
    def b(text,data=None): return InlineKeyboardButton(text,callback_data=data)
    @staticmethod
    def r(*btns): return list(btns)
    @staticmethod
    def m(rows): return InlineKeyboardMarkup(rows)
    
    @classmethod
    def main(cls): return cls.m([
        cls.r(cls.b("📊 تحلیل","ana")),cls.r(cls.b("🚨 خرید","s_buy"),cls.b("📈 فروش","s_sell")),
        cls.r(cls.b("💰 کیف پول","wal"),cls.b("💎 VIP","vip")),
        cls.r(cls.b("📊 بازار","mkt"),cls.b("📖 راهنما","hlp")),
    ])
    
    @classmethod
    def admin(cls): return cls.m([
        cls.r(cls.b("🧠 داشبورد","adm_d")),cls.r(cls.b("👥 کاربران","adm_u")),
        cls.r(cls.b("💰 پرداخت‌ها","adm_p")),cls.r(cls.b("🚪 سرور","adm_s")),
        cls.r(cls.b("🔙 منوی کاربر","mu")),
    ])

# ═══════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════
def admin_only(f):
    @wraps(f)
    async def w(u,c,*a,**kw):
        if not u.effective_user or not is_admin(u.effective_user.id):
            if u.message: await u.message.reply_text("❌ دسترسی غیرمجاز",parse_mode=ParseMode.MARKDOWN)
            return
        return await f(u,c,*a,**kw)
    return w

def handle_errors(f):
    @wraps(f)
    async def w(u,c,*a,**kw):
        try: return await f(u,c,*a,**kw)
        except: pass
    return w

# ═══════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════
class Part9:
    def __init__(self): self._app=None; self._start=time.time()
    
    def build(self):
        builder = ApplicationBuilder()
        builder.token(BOT_TOKEN)
        builder.defaults(Defaults(parse_mode=ParseMode.MARKDOWN))
        builder.concurrent_updates(True)
        self._app = builder.build()
        
        cmds = {
            "start":self.cmd_start,"help":self.cmd_help,"admin":self.cmd_admin,
            "vip":self.cmd_vip,"wallet":self.cmd_wallet,"price":self.cmd_price,
            "stats":self.cmd_stats,"cancel":self.cmd_cancel,
        }
        for name,func in cmds.items():
            self._app.add_handler(CommandHandler(name,func))
        
        self._app.add_handler(CallbackQueryHandler(self.callback))
        return self._app
    
    @handle_errors
    async def cmd_start(self,u,c):
        user=u.effective_user
        DB.create_user({"telegram_id":str(user.id),"username":user.username or "","first_name":user.first_name or ""})
        kb = K.admin() if is_admin(user.id) else K.main()
        await u.message.reply_text(f"🚀 *سلام {user.first_name}!*\nبه CryptoPulse AI خوش آمدید",reply_markup=kb)
    
    async def cmd_help(self,u,c): await u.message.reply_text("📖 /start /vip /wallet /price /stats")
    
    @admin_only
    async def cmd_admin(self,u,c):
        s=DB.stats()
        await u.message.reply_text(f"👑 *پنل مدیریت*\n👥 {s['users']}\n💎 {s['vip']}",reply_markup=K.admin())
    
    async def cmd_vip(self,u,c): await u.message.reply_text("💎 *VIP*\nبرای خرید به پشتیبانی پیام دهید")
    async def cmd_wallet(self,u,c): await u.message.reply_text("💰 *کیف پول*\nموجودی: ۰ تومان")
    
    async def cmd_price(self,u,c):
        coin=(c.args[0] if c.args else "BTC").upper()
        p=random.uniform(30000,80000) if coin=="BTC" else random.uniform(10,5000)
        await u.message.reply_text(f"💰 *{coin}*\n{fmt_price(p)}")
    
    async def cmd_stats(self,u,c):
        s=DB.stats()
        await u.message.reply_text(f"📊 *آمار*\n👥 {s['users']}\n💎 {s['vip']}\n📡 {s['signals']}")
    
    async def cmd_cancel(self,u,c): await u.message.reply_text("✅ لغو شد"); return ConversationHandler.END
    
    async def callback(self,u,c):
        q=u.callback_query; await q.answer(); d=q.data; user=u.effective_user
        
        if d=="mu":
            kb=K.admin() if is_admin(user.id) else K.main()
            await q.edit_message_text("🚀 *منوی اصلی*",reply_markup=kb)
        elif d=="ana": await q.edit_message_text("📊 *تحلیل*\n/analysis BTC")
        elif d=="s_buy": await q.edit_message_text("🚨 *خرید*\n/buy BTC")
        elif d=="s_sell": await q.edit_message_text("📈 *فروش*\n/sell BTC")
        elif d=="wal": await q.edit_message_text("💰 *کیف پول*\nموجودی: ۰ تومان")
        elif d=="vip": await q.edit_message_text("💎 *VIP*\nبرای خرید پیام دهید")
        elif d=="mkt": await q.edit_message_text("📊 *بازار*\nBTC: $65,000")
        elif d=="hlp": await q.edit_message_text("📖 /start /vip /wallet /price")
        elif d=="adm_d":
            s=DB.stats()
            await q.edit_message_text(f"🧠 *داشبورد*\n👥 {s['users']}\n💎 {s['vip']}")
        elif d=="adm_u":
            users=DB.all_users()
            await q.edit_message_text(f"👥 *کاربران ({len(users)})*")
        elif d=="adm_p": await q.edit_message_text(f"💰 *پرداخت‌ها*\n{len(DB.payments)} تراکنش")
        elif d=="adm_s": await q.edit_message_text(f"🚪 *سرور*\n⏱ {int(time.time()-self._start)}s")
        else: await q.edit_message_text("⚠️ نامعتبر")

# ═══════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════
_instance = None

def start():
    return True

def get_application():
    global _instance
    if _instance is None:
        _instance = Part9()
    return _instance.build()

# ═══════════════════════════════════════
# STANDALONE
# ═══════════════════════════════════════
if __name__ == "__main__":
    if not BOT_TOKEN: print("BOT_TOKEN not set!"); sys.exit(1)
    print(f"🚀 CryptoPulse AI v{BOT_VERSION} — Part 9")
    app = Part9().build()
    app.run_polling(drop_pending_updates=True)
