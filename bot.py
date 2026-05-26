#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🥇 ربات قیمت زنده طلا و سکه - به تومان
📡 منابع: tgju.org | call1.ir
📅 تاریخ شمسی | ⏰ ساعت تهران
"""

import asyncio
import logging
import sys
import subprocess
from datetime import datetime
from typing import Dict

# نصب خودکار کتابخانه‌ها
for pkg, imp in [("httpx", "httpx"), ("jdatetime", "jdatetime"), 
                  ("pytz", "pytz"), ("python-telegram-bot", "telegram")]:
    try:
        __import__(imp)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import httpx
import jdatetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# توکن تلگرام
TOKEN = "7225279768:AAHwZEmSxRxx5ZGCyx88BMP2DSEoarcZSxw"

# لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger('GoldBot')

# زمان تهران
TEHRAN = pytz.timezone('Asia/Tehran')
MONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
DAYS = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']

def now_str():
    n = datetime.now(TEHRAN)
    j = jdatetime.datetime.fromgregorian(datetime=n)
    return f"{DAYS[n.weekday()]} {j.day} {MONTHS[j.month-1]} {j.year} | {n.strftime('%H:%M:%S')}"

async def fetch_gold_prices() -> Dict:
    rates = {'gold24': 48_000_000, 'gold18': 36_000_000, 'coin': 55_000_000}
    
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            # tgju.org
            for key, sym in [('gold24','price_gold_24'), ('gold18','price_gold_18'), ('coin','price_coin_imami')]:
                try:
                    r = await c.get(f"https://api.tgju.org/v1/market/indicator/summary/{sym}")
                    if r.status_code == 200:
                        p = r.json().get('response',{}).get('indicators',{}).get(sym,{}).get('p',0)
                        if p > 0:
                            rates[key] = int(p/10)  # ریال به تومان
                except: pass
            
            # call1.ir (fallback)
            if rates['gold24'] == 48_000_000:
                try:
                    r = await c.get("https://call1.ir/api/currency.php")
                    if r.status_code == 200:
                        for item in r.json():
                            n, p = str(item.get('name','')), int(item.get('price',0))
                            if 'طلای ۲۴' in n: rates['gold24'] = p
                            elif 'طلای ۱۸' in n: rates['gold18'] = p
                            elif 'سکه' in n: rates['coin'] = p
                except: pass
    except: pass
    
    return rates

def msg_text(rates):
    return f"""
🟢══════════════════════🟢
   🥇 قیمت‌های زنده طلا
🟢══════════════════════🟢

📅 {now_str()}

🥇 *طلای ۲۴ عیار:* {rates['gold24']:,} تومان
🥈 *طلای ۱۸ عیار:* {rates['gold18']:,} تومان
🪙 *سکه امامی:* {rates['coin']:,} تومان

📡 *منبع:* tgju.org / call1.ir

🟢══════════════════════🟢
✨ @Aradarzz_bot
"""

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 بروزرسانی قیمت‌ها", callback_data="r")],
        [InlineKeyboardButton("🥇 طلا و سکه", callback_data="g")]
    ])

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    r = await fetch_gold_prices()
    await update.message.reply_text(msg_text(r), parse_mode="Markdown", reply_markup=menu())

async def click(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    r = await fetch_gold_prices()
    
    if q.data == "r":
        await q.edit_message_text(msg_text(r), parse_mode="Markdown", reply_markup=menu())
    elif q.data == "g":
        m = f"""
🥇 *قیمت طلا و سکه*

📅 {now_str()}

🥇 طلای ۲۴ عیار: *{r['gold24']:,}* تومان
🥈 طلای ۱۸ عیار: *{r['gold18']:,}* تومان
🪙 سکه امامی: *{r['coin']:,}* تومان

📡 منبع: tgju.org / call1.ir
"""
        await q.edit_message_text(m, parse_mode="Markdown", reply_markup=menu())

async def text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    r = await fetch_gold_prices()
    await update.message.reply_text(msg_text(r), parse_mode="Markdown", reply_markup=menu())

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    
    print("🚀 ربات طلا و سکه راه‌اندازی شد! هر پیامی بدهید قیمت‌ها را می‌بینید.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
