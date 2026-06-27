#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import logging
from datetime import datetime

# ============================================================
# ✅ توکن را مستقیماً اینجا قرار دهید (فقط برای تست)
# ============================================================
BOT_TOKEN = "7225279768:AAHB8ZQdgzhFoeV8tPryyReJ-Gq_Y8pI90U"

# ============================================================
# VALIDATE TOKEN
# ============================================================
if not BOT_TOKEN or len(BOT_TOKEN) < 30:
    print("❌ Invalid token!")
    sys.exit(1)

print(f"✅ Token loaded (length: {len(BOT_TOKEN)})")

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# BOT
# ============================================================
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# ============================================================
# KEYBOARD
# ============================================================
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 قیمت لحظه‌ای", callback_data="price"),
         InlineKeyboardButton(text="🕐 زمان", callback_data="time")],
        [InlineKeyboardButton(text="💎 وضعیت", callback_data="status")],
    ])

# ============================================================
# COMMAND HANDLERS
# ============================================================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome = f"""💎 VIP PLATINUM BOT ✅

سلام! ربات با موفقیت فعال شد.

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

از دکمه‌های زیر استفاده کنید:"""
    await message.answer(welcome, reply_markup=main_keyboard())

@dp.message(Command("time"))
async def cmd_time(message: Message):
    await message.answer(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# ============================================================
# CALLBACK HANDLERS
# ============================================================
@dp.callback_query(F.data == "price")
async def cb_price(callback):
    await callback.answer()
    await callback.message.edit_text(
        "📊 **قیمت لحظه‌ای**\n\n"
        "در حال دریافت قیمت‌ها...\n"
        "برای دریافت قیمت از دستور /price استفاده کنید.",
        reply_markup=main_keyboard()
    )

@dp.callback_query(F.data == "time")
async def cb_time(callback):
    await callback.answer()
    await callback.message.edit_text(
        f"🕐 {datetime.now().strftime('%H:%M:%S')}",
        reply_markup=main_keyboard()
    )

@dp.callback_query(F.data == "status")
async def cb_status(callback):
    await callback.answer()
    await callback.message.edit_text(
        "✅ **وضعیت ربات**\n\n"
        "🔹 ربات: فعال ✅\n"
        "🔹 توکن: معتبر ✅\n"
        "🔹 نسخه: v45.0\n"
        "🔹 وضعیت: آنلاین",
        reply_markup=main_keyboard()
    )

# ============================================================
# MAIN
# ============================================================
async def main():
    logger.info("🚀 VIP PLATINUM BOT STARTED!")
    logger.info(f"✅ Bot token loaded (length: {len(BOT_TOKEN)})")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
