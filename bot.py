#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import time
import aiohttp
import uvicorn
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

print("🚀 Starting CryptoPulse AI Bot...")

# ============================================================
#                    LOAD ENV
# ============================================================

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
PORT = int(os.environ.get("PORT", 8080))

print(f"✅ BOT_TOKEN: {'SET' if BOT_TOKEN else 'NOT SET'}")
print(f"✅ ADMIN_IDS: {ADMIN_IDS}")
print(f"✅ GROQ_API_KEY: {'SET' if GROQ_API_KEY else 'NOT SET'}")
print(f"✅ COINEX_API_KEY: {'SET' if COINEX_API_KEY else 'NOT SET'}")
print()

# ============================================================
#                    COINEX PRICE
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

# ============================================================
#                    GROQ AI
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

# ============================================================
#                    FASTAPI SERVER
# ============================================================

app = FastAPI(title="CryptoPulse AI", version="3.0.0")

@app.get("/")
async def root():
    return {"status": "online", "name": "CryptoPulse AI", "version": "3.0.0", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/api/v1/price/{coin}")
async def get_price(coin: str):
    data = await get_coinex_price(coin.upper())
    if data:
        return {"coin": coin.upper(), **data, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    return {"error": "Price not available"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        return {"status": "ok"}
    except:
        return JSONResponse(status_code=400, content={"status": "error"})

# ============================================================
#                    TELEGRAM BOT
# ============================================================

def user_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 تحلیل", callback_data="analysis")],
        [InlineKeyboardButton("🚨 سیگنال", callback_data="signal")],
        [InlineKeyboardButton("💰 قیمت", callback_data="price")],
        [InlineKeyboardButton("💎 VIP", callback_data="vip")],
        [InlineKeyboardButton("📖 راهنما", callback_data="help")],
        [InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
        [InlineKeyboardButton("💎 مدیریت VIP", callback_data="admin_vip")],
        [InlineKeyboardButton("📢 ارسال همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    is_admin = int(user_id) in ADMIN_IDS if user_id.isdigit() else False
    
    if is_admin:
        text = "👑 **پنل مدیریت**\n\nبه پنل ادمین خوش آمدید!"
        keyboard = admin_keyboard()
    else:
        text = "🌟 **به CryptoPulse AI خوش آمدید!**\n\nربات هوشمند تحلیل و سیگنال ارزهای دیجیتال"
        keyboard = user_keyboard()
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    is_admin = int(user_id) in ADMIN_IDS if user_id.isdigit() else False
    
    if not is_admin:
        await update.message.reply_text("❌ دسترسی غیرمجاز!")
        return
    
    await update.message.reply_text("👑 **پنل مدیریت**", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال دریافت قیمت...", reply_markup=user_keyboard())
    
    data = await get_coinex_price("BTC")
    if data:
        text = f"""
📊 **قیمت لحظه‌ای BTC**

💰 **قیمت:** ${data['price']:,.2f}
📈 **تغییر ۲۴ساعته:** {data['change']:+.2f}%
📊 **بالاترین:** ${data['high']:,.2f}
📉 **پایین‌ترین:** ${data['low']:,.2f}
📊 **حجم:** ${data['volume']:,.0f}

⏰ **زمان:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ خطا در دریافت قیمت!", reply_markup=user_keyboard())

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال دریافت تحلیل از AI...", reply_markup=user_keyboard())
    
    price_data = await get_coinex_price("BTC")
    if price_data:
        analysis = await get_groq_analysis("BTC", price_data)
        text = f"""
📊 **تحلیل تکنیکال BTC**

🤖 **تحلیل هوش مصنوعی:**

{analysis}

💰 **قیمت فعلی:** ${price_data['price']:,.2f}
📈 **تغییر ۲۴ساعته:** {price_data['change']:+.2f}%

⏰ **زمان:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ خطا در دریافت داده!", reply_markup=user_keyboard())

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_main":
        await query.edit_message_text("🏠 **منوی اصلی**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "price":
        await query.edit_message_text("⏳ در حال دریافت قیمت...", reply_markup=user_keyboard())
        price_data = await get_coinex_price("BTC")
        if price_data:
            text = f"""
📊 **قیمت لحظه‌ای BTC**

💰 **قیمت:** ${price_data['price']:,.2f}
📈 **تغییر ۲۴ساعته:** {price_data['change']:+.2f}%
⏰ **زمان:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            await query.edit_message_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        else:
            await query.edit_message_text("❌ خطا در دریافت قیمت!", reply_markup=user_keyboard())
    elif data == "analysis":
        await query.edit_message_text("⏳ در حال دریافت تحلیل...", reply_markup=user_keyboard())
        price_data = await get_coinex_price("BTC")
        if price_data:
            analysis = await get_groq_analysis("BTC", price_data)
            text = f"""
📊 **تحلیل تکنیکال BTC**

🤖 **تحلیل هوش مصنوعی:**

{analysis}

💰 **قیمت فعلی:** ${price_data['price']:,.2f}
📈 **تغییر ۲۴ساعته:** {price_data['change']:+.2f}%

⏰ **زمان:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            await query.edit_message_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        else:
            await query.edit_message_text("❌ خطا در دریافت داده!", reply_markup=user_keyboard())
    elif data == "admin_users":
        await query.edit_message_text("👥 **مدیریت کاربران**", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "admin_payments":
        await query.edit_message_text("💰 **مدیریت پرداخت‌ها**", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "admin_vip":
        await query.edit_message_text("💎 **مدیریت VIP**", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "admin_broadcast":
        await query.edit_message_text("📢 **ارسال همگانی**", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        await query.edit_message_text("ℹ️ در حال توسعه...", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)

# ============================================================
#                    MAIN
# ============================================================

async def run_bot():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found!")
        return
    
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("admin", admin_command))
    bot_app.add_handler(CommandHandler("price", price_command))
    bot_app.add_handler(CommandHandler("analysis", analysis_command))
    bot_app.add_handler(CallbackQueryHandler(callback_handler))
    
    await bot_app.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted!")
    
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    print("✅ Telegram Bot is running with polling!")

async def main():
    bot_task = asyncio.create_task(run_bot())
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        while True:
            time.sleep(1)
