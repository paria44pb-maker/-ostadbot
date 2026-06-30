#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Entry Point
"""

import os
import sys
import asyncio
import time

print("🚀 Starting CryptoPulse AI Bot v3.0...")
print("📁 Loading all 15 parts...\n")

# ============================================================
#                    IMPORT ALL PARTS
# ============================================================

parts = [
    ("Part 1", "Main Entry Point"),
    ("Part 2", "Config & Settings"),
    ("Part 3", "Database Models"),
    ("Part 4", "Utils & Tehran Time"),
    ("Part 5", "CoinEx Exchange"),
    ("Part 6", "Groq AI"),
    ("Part 7", "Technical Analysis"),
    ("Part 8", "Keyboards & Menus"),
    ("Part 9", "Main Handlers"),
    ("Part 10", "Admin Panel"),
    ("Part 11", "VIP & Payment"),
    ("Part 12", "Channel Management"),
    ("Part 13", "FastAPI Server"),
    ("Part 14", "Background Tasks"),
    ("Part 15", "Media Management")
]

for part, name in parts:
    try:
        exec(f"from part{part.split()[1]} import *")
        print(f"  ✅ {part}: {name}")
    except Exception as e:
        print(f"  ❌ {part}: {e}")

print("\n" + "="*50)
print("🚀 All parts loaded!")
print("="*50)

# ============================================================
#                    RUN BOT
# ============================================================

async def run_bot():
    try:
        from part9 import get_application
        app = get_application()
        
        if app:
            print("✅ Bot application created!")
            
            # حذف Webhook
            try:
                await app.bot.delete_webhook(drop_pending_updates=True)
                print("✅ Webhook deleted!")
            except Exception as e:
                print(f"⚠️ Webhook delete error: {e}")
            
            # شروع با Polling
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print("✅ Bot is running with polling!")
            
            while True:
                await asyncio.sleep(1)
        else:
            print("⚠️ No bot application found.")
            
    except Exception as e:
        print(f"❌ Bot error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
            time.sleep(1)
