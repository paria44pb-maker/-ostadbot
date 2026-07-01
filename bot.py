#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import time
import uvicorn

print("🚀 Starting CryptoPulse AI Bot v3.0...")

# ============================================================
#                    IMPORT ALL PARTS
# ============================================================

try:
    from part1 import *
    print("✅ Part 1 loaded")
except Exception as e:
    print(f"❌ Part 1: {e}")

try:
    from part2 import *
    print("✅ Part 2 loaded")
except Exception as e:
    print(f"❌ Part 2: {e}")

try:
    from part3 import *
    print("✅ Part 3 loaded")
except Exception as e:
    print(f"❌ Part 3: {e}")

try:
    from part4 import *
    print("✅ Part 4 loaded")
except Exception as e:
    print(f"❌ Part 4: {e}")

try:
    from part5 import *
    print("✅ Part 5 loaded")
except Exception as e:
    print(f"❌ Part 5: {e}")

try:
    from part6 import *
    print("✅ Part 6 loaded")
except Exception as e:
    print(f"❌ Part 6: {e}")

try:
    from part7 import *
    print("✅ Part 7 loaded")
except Exception as e:
    print(f"❌ Part 7: {e}")

try:
    from part8 import *
    print("✅ Part 8 loaded")
except Exception as e:
    print(f"❌ Part 8: {e}")

try:
    from part9 import *
    print("✅ Part 9 loaded")
except Exception as e:
    print(f"❌ Part 9: {e}")

try:
    from part10 import *
    print("✅ Part 10 loaded")
except Exception as e:
    print(f"❌ Part 10: {e}")

try:
    from part11 import *
    print("✅ Part 11 loaded")
except Exception as e:
    print(f"❌ Part 11: {e}")

try:
    from part12 import *
    print("✅ Part 12 loaded")
except Exception as e:
    print(f"❌ Part 12: {e}")

try:
    from part13 import *
    print("✅ Part 13 loaded")
except Exception as e:
    print(f"❌ Part 13: {e}")

try:
    from part14 import *
    print("✅ Part 14 loaded")
except Exception as e:
    print(f"❌ Part 14: {e}")

try:
    from part15 import *
    print("✅ Part 15 loaded")
except Exception as e:
    print(f"❌ Part 15: {e}")

print("✅ All 15 parts loaded!")

# ============================================================
#                    SIMPLE BOT (بدون وابستگی)
# ============================================================

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "")

if not TOKEN:
    print("❌ BOT_TOKEN not found!")
    exit(1)

print("✅ BOT_TOKEN loaded!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 CryptoPulse AI is running!")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted!")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Bot is running with polling!")

# ============================================================
#                    RUN
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
