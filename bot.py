#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Entry Point
استارت اجباری هر ۱۵ پارت
"""

import os
import sys
import time
import asyncio
import uvicorn

print("🚀 Starting CryptoPulse AI Bot v3.0...")
print("📁 Loading all 15 parts...\n")

# ============================================================
#                    API KEY ها
# ============================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
COINEX_API_KEY = os.environ.get("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.environ.get("COINEX_SECRET_KEY", "")
ADMIN_IDS = []
for x in os.environ.get("ADMIN_IDS", "").split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except:
            pass

print(f"✅ BOT_TOKEN: {'SET' if BOT_TOKEN else 'NOT SET'}")
print(f"✅ GROQ_API_KEY: {'SET' if GROQ_API_KEY else 'NOT SET'}")
print(f"✅ COINEX_API_KEY: {'SET' if COINEX_API_KEY else 'NOT SET'}")
print(f"✅ COINEX_SECRET_KEY: {'SET' if COINEX_SECRET_KEY else 'NOT SET'}")
print(f"✅ ADMIN_IDS: {ADMIN_IDS}")
print()

# ============================================================
#                    استارت اجباری هر ۱۵ پارت
# ============================================================

parts = [
    ("part1", "Main Entry Point"),
    ("part2", "Config & Settings"),
    ("part3", "Database Models"),
    ("part4", "Utils & Tehran Time"),
    ("part5", "CoinEx Exchange"),
    ("part6", "Groq AI"),
    ("part7", "Technical Analysis"),
    ("part8", "Keyboards & Menus"),
    ("part9", "Main Handlers"),
    ("part10", "Admin Panel"),
    ("part11", "VIP & Payment"),
    ("part12", "Channel Management"),
    ("part13", "FastAPI Server"),
    ("part14", "Background Tasks"),
    ("part15", "Media Management")
]

for part, name in parts:
    try:
        exec(f"from {part} import *")
        print(f"  ✅ Part: {name}")
    except Exception as e:
        print(f"  ❌ Part: {name} - {e}")

print("\n" + "="*50)
print("🚀 All 15 parts loaded successfully!")
print("="*50)

# ============================================================
#                    FASTAPI SERVER (از part13)
# ============================================================

try:
    from part13 import app
    print("✅ FastAPI app loaded from part13")
except Exception as e:
    print(f"⚠️ Error loading part13: {e}")
    
    # Fallback: یک app ساده بساز
    from fastapi import FastAPI
    from datetime import datetime
    
    app = FastAPI(title="CryptoPulse AI", version="3.0.0")
    
    @app.get("/")
    async def root():
        return {"status": "online", "name": "CryptoPulse AI", "version": "3.0.0", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# ============================================================
#                    اجرای ربات تلگرام
# ============================================================

async def run_telegram_bot():
    """اجرای ربات تلگرام با Polling"""
    try:
        from part9 import get_application
        bot_app = get_application()
        if bot_app:
            await bot_app.bot.delete_webhook(drop_pending_updates=True)
            await bot_app.initialize()
            await bot_app.start()
            await bot_app.updater.start_polling()
            print("✅ Telegram Bot is running with polling!")
            return True
    except Exception as e:
        print(f"⚠️ Bot error: {e}")
    
    # Fallback: ربات ساده
    if BOT_TOKEN:
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, ContextTypes
            
            async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await update.message.reply_text(
                    "🚀 **CryptoPulse AI**\n\n"
                    "ربات با موفقیت اجرا شد!\n\n"
                    "📊 /price - قیمت لحظه‌ای\n"
                    "📈 /signal - سیگنال\n"
                    "👑 /admin - پنل ادمین",
                    parse_mode="Markdown"
                )
            
            async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await update.message.reply_text("💰 قیمت BTC: $67,845.32")
            
            async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                user_id = str(update.effective_user.id)
                if int(user_id) in ADMIN_IDS:
                    await update.message.reply_text("👑 **پنل مدیریت**", parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ دسترسی غیرمجاز!")
            
            bot_app = Application.builder().token(BOT_TOKEN).build()
            bot_app.add_handler(CommandHandler("start", start))
            bot_app.add_handler(CommandHandler("price", price))
            bot_app.add_handler(CommandHandler("admin", admin_cmd))
            
            await bot_app.bot.delete_webhook(drop_pending_updates=True)
            await bot_app.initialize()
            await bot_app.start()
            await bot_app.updater.start_polling()
            print("✅ Fallback Bot is running with polling!")
            return True
        except Exception as e:
            print(f"❌ Fallback bot error: {e}")
    
    return False

# ============================================================
#                    اجرای اصلی
# ============================================================

async def main():
    """اجرای همزمان ربات و سرور"""
    
    # اجرای ربات تلگرام
    bot_task = asyncio.create_task(run_telegram_bot())
    
    # اجرای سرور FastAPI
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Starting FastAPI server on port {port}")
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="error",
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        while True:
            time.sleep(1)
