#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import uvicorn
from bot13 import app

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ==================== هندلرها ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 **CryptoPulse AI**\n\n"
        "ربات هوشمند تحلیل و سیگنال ارزهای دیجیتال\n\n"
        "📊 /signal - دریافت سیگنال\n"
        "💰 /price - قیمت لحظه‌ای\n"
        "💎 /vip - پنل VIP\n"
        "🆘 /support - پشتیبانی",
        parse_mode="Markdown"
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 در حال دریافت سیگنال...")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 در حال دریافت قیمت...")

# ==================== اجرا ====================

async def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found!")
        return
    
    # ربات تلگرام
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("signal", signal))
    bot_app.add_handler(CommandHandler("price", price))
    
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    print("✅ Telegram Bot is running!")
    
    # سرور
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="error")
    server = uvicorn.Server(config)
    
    await asyncio.gather(
        server.serve(),
        asyncio.Event().wait()
    )

if __name__ == "__main__":
    asyncio.run(main())
