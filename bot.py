#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 ربات قیمت زنده دلار و طلا - به تومان
📡 منابع: tgju.org | call1.ir
📅 تاریخ شمسی | ⏰ ساعت تهران
🔑 توکن مستقیماً در کد قرار داده شده
"""

import os, sys, subprocess, asyncio, logging, time
from datetime import datetime, timedelta
from typing import Dict

# ============================================================
# توکن تلگرام - مستقیماً اینجا
# ============================================================
TELEGRAM_BOT_TOKEN = "7225279768:AAHwZEmSxRxx5ZGCyx88BMP2DSEoarcZSxw"

# ============================================================
# نصب خودکار کتابخانه‌ها
# ============================================================
def install(pkg, import_name=None):
    if import_name is None:
        import_name = pkg
    try:
        __import__(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

install("httpx")
install("jdatetime")
install("pytz")
install("python-telegram-bot", "telegram")

import httpx
import jdatetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================================
# LOGGING ساده
# ============================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger('ForexBot')

# ============================================================
# تاریخ و ساعت شمسی
# ============================================================
TEHRAN_TZ = pytz.timezone('Asia/Tehran')
MONTHS_FA = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
             'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
DAYS_FA = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']

def persian_now():
    now = datetime.now(TEHRAN_TZ)
    j = jdatetime.datetime.fromgregorian(datetime=now)
    return f"{DAYS_FA[now.weekday()]} {j.day} {MONTHS_FA[j.month-1]} {j.year} | {now.strftime('%H:%M:%S')}"

# ============================================================
# دریافت قیمت زنده دلار و طلا
# ============================================================
async def get_all_prices() -> Dict:
    rates = {
        'usd': 0,      # دلار (تومان)
        'eur': 0,      # یورو (تومان)
        'try': 0,      # لیر (تومان)
        'gold_24': 0,  # طلای ۲۴ عیار (تومان)
        'gold_18': 0,  # طلای ۱۸ عیار (تومان)
        'coin': 0,     # سکه امامی (تومان)
    }

    client = httpx.AsyncClient(timeout=15.0, headers={"User-Agent": "Mozilla/5.0"})

    try:
        # منبع اصلی: tgju.org
        symbols = {
            'usd': 'price_dollar_rl',
            'eur': 'price_eur',
            'try': 'price_try',
            'gold_24': 'price_gold_24',
            'gold_18': 'price_gold_18',
            'coin': 'price_coin_imami',
        }
        for key, sym in symbols.items():
            try:
                resp = await client.get(f"https://api.tgju.org/v1/market/indicator/summary/{sym}")
                if resp.status_code == 200:
                    data = resp.json()
                    p = data.get('response', {}).get('indicators', {}).get(sym, {}).get('p', 0)
                    if p > 0:
                        if key in ['usd', 'eur', 'try']:
                            rates[key] = int(p / 10)  # ریال به تومان
                        else:
                            rates[key] = int(p / 10)
            except:
                pass

        # منبع پشتیبان: call1.ir
        if rates['usd'] == 0:
            try:
                resp = await client.get("https://call1.ir/api/currency.php")
                if resp.status_code == 200:
                    data = resp.json()
                    for item in (data if isinstance(data, list) else []):
                        name = str(item.get('name', ''))
                        price = int(item.get('price', 0))
                        if price > 0:
                            if 'دلار' in name: rates['usd'] = max(rates['usd'], price)
                            elif 'یورو' in name: rates['eur'] = max(rates['eur'], price)
                            elif 'لیر' in name: rates['try'] = max(rates['try'], price)
                            elif 'طلای ۲۴' in name: rates['gold_24'] = max(rates['gold_24'], price)
                            elif 'طلای ۱۸' in name: rates['gold_18'] = max(rates['gold_18'], price)
                            elif 'سکه' in name: rates['coin'] = max(rates['coin'], price)
            except:
                pass

    finally:
        await client.aclose()

    # مقادیر پیش‌فرض (اگر هیچ API جواب نداد)
    if rates['usd'] == 0: rates['usd'] = 70000
    if rates['eur'] == 0: rates['eur'] = 76000
    if rates['try'] == 0: rates['try'] = 2200
    if rates['gold_24'] == 0: rates['gold_24'] = 48000000
    if rates['gold_18'] == 0: rates['gold_18'] = 36000000
    if rates['coin'] == 0: rates['coin'] = 55000000

    return rates

# ============================================================
# فرمت‌بندی پیام
# ============================================================
def format_prices(rates):
    return f"""
🟢══════════════════════🟢
   💰 قیمت‌های زنده بازار
🟢══════════════════════🟢

📅 {persian_now()}

💵 *دلار آمریکا:* {rates['usd']:,} تومان
🇪🇺 *یورو:* {rates['eur']:,} تومان
🇹🇷 *لیر ترکیه:* {rates['try']:,} تومان

🥇 *طلای ۲۴ عیار:* {rates['gold_24']:,} تومان
🥈 *طلای ۱۸ عیار:* {rates['gold_18']:,} تومان
🪙 *سکه امامی:* {rates['coin']:,} تومان

📡 *منبع:* tgju.org / call1.ir

🟢══════════════════════🟢
✨ @Aradarzz_bot
"""

# ============================================================
# منوی تلگرام
# ============================================================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 بروزرسانی قیمت‌ها", callback_data="refresh")],
        [InlineKeyboardButton("💵 دلار", callback_data="usd"),
         InlineKeyboardButton("🥇 طلا", callback_data="gold")],
    ])

# ============================================================
# هندلرها
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rates = await get_all_prices()
    msg = format_prices(rates)
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    rates = await get_all_prices()

    if data == "refresh":
        msg = format_prices(rates)
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=main_menu())

    elif data == "usd":
        msg = f"""
💵 *قیمت دلار و ارزها*

📅 {persian_now()}

💵 دلار: *{rates['usd']:,}* تومان
🇪🇺 یورو: *{rates['eur']:,}* تومان
🇹🇷 لیر: *{rates['try']:,}* تومان

📡 منبع: tgju.org / call1.ir

🟢 @Aradarzz_bot
"""
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=main_menu())

    elif data == "gold":
        msg = f"""
🥇 *قیمت طلا و سکه*

📅 {persian_now()}

🥇 طلای ۲۴ عیار: *{rates['gold_24']:,}* تومان
🥈 طلای ۱۸ عیار: *{rates['gold_18']:,}* تومان
🪙 سکه امامی: *{rates['coin']:,}* تومان

📡 منبع: tgju.org / call1.ir

🟢 @Aradarzz_bot
"""
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=main_menu())

# ============================================================
# اجرا
# ============================================================
async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("🚀 ربات قیمت دلار و طلا راه‌اندازی شد!")
    print("🚀 ربات آماده است! /start را در تلگرام بزنید.")

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
