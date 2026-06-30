#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import uvicorn
from bot13 import app

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 ربات با موفقیت اجرا شد!")

async def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found!")
        return
    
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    print("✅ Telegram Bot is running!")
    
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="error")
    server = uvicorn.Server(config)
    
    await asyncio.gather(server.serve(), asyncio.Event().wait())

if __name__ == "__main__":
    asyncio.run(main())
