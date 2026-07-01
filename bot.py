#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import time
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

print(f"✅ BOT_TOKEN: {'SET' if BOT_TOKEN else 'NOT SET'}")
print(f"✅ GROQ_API_KEY: {'SET' if GROQ_API_KEY else 'NOT SET'}")
print(f"✅ COINEX_API_KEY: {'SET' if COINEX_API_KEY else 'NOT SET'}")
print(f"✅ COINEX_SECRET_KEY: {'SET' if COINEX_SECRET_KEY else 'NOT SET'}")
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
#                    اجرای ربات و سرور
# ============================================================

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="CryptoPulse AI", version="3.0.0")

@app.get("/")
async def root():
    return {"status": "online", "name": "CryptoPulse AI", "version": "3.0.0", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

async def run_bot():
    try:
        from part9 import get_application
        bot_app = get_application()
        if bot_app:
            await bot_app.bot.delete_webhook(drop_pending_updates=True)
            await bot_app.initialize()
            await bot_app.start()
            await bot_app.updater.start_polling()
            print("✅ Telegram Bot is running with polling!")
    except Exception as e:
        print(f"⚠️ Bot error: {e}")

async def main():
    bot_task = asyncio.create_task(run_bot())
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), log_level="error")
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
