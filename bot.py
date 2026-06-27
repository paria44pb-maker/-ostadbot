#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ============================================================
# TOKEN LOADING - ONLY FROM token.txt
# ============================================================

TOKEN_FILE = "token.txt"
BOT_TOKEN = None

if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        BOT_TOKEN = f.read().strip()
    if BOT_TOKEN:
        print(f"✅ Token loaded from {TOKEN_FILE} (length: {len(BOT_TOKEN)})")
    else:
        print(f"❌ {TOKEN_FILE} is empty!")
else:
    # ایجاد فایل token.txt
    with open(TOKEN_FILE, "w") as f:
        f.write("# Paste your Telegram bot token here and remove the #\n")
        f.write("# Example: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n")
        f.write("\nYOUR_TOKEN_HERE\n")
    print(f"📝 {TOKEN_FILE} created. Please add your token and restart.")
    sys.exit(1)

if not BOT_TOKEN or BOT_TOKEN == "YOUR_TOKEN_HERE" or BOT_TOKEN.startswith("#"):
    print("❌ Invalid token in token.txt. Please paste your actual token.")
    sys.exit(1)

# ============================================================
# VALIDATE TOKEN FORMAT
# ============================================================
import re
if not re.match(r'^\d+:[A-Za-z0-9_-]+$', BOT_TOKEN):
    print("⚠️ Token format looks invalid. But will try anyway...")

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# BOT
# ============================================================
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("✅ ربات با موفقیت فعال شد! 💎")

@dp.message(Command("time"))
async def time_cmd(message: Message):
    from datetime import datetime
    await message.answer(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

@dp.message()
async def echo(message: Message):
    await message.answer("سلام! از دکمه‌ها یا دستورات استفاده کنید.")

# ============================================================
# MAIN
# ============================================================
async def main():
    logger.info("🚀 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
