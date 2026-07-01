#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import time
import uvicorn
from fastapi import FastAPI
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
#                    FASTAPI SERVER
# ============================================================

app = FastAPI(title="CryptoPulse AI", version="3.0.0")

@app.get("/")
async def root():
    return {"status": "online", "name": "CryptoPulse AI", "version": "3.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ============================================================
#                    TELEGRAM BOT
# ============================================================

def user_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 تحلیل", callback_data="analysis")],
        [InlineKeyboardButton("🚨 سیگنال", callback_data="signal")],
        [InlineKeyboardButton("💰 کیف پول", callback_data="wallet")],
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

async def start(update, context):
    user_id = str(update.effective_user.id)
    is_admin = int(user_id) in ADMIN_IDS if user_id.isdigit() else False
    
    if is_admin:
        text = "👑 **پنل مدیریت**"
        keyboard = admin_keyboard()
    else:
        text = "🌟 **به CryptoPulse AI خوش آمدید!**"
        keyboard = user_keyboard()
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def admin_command(update, context):
    user_id = str(update.effective_user.id)
    is_admin = int(user_id) in ADMIN_IDS if user_id.isdigit() else False
    
    if not is_admin:
        await update.message.reply_text("❌ دسترسی غیرمجاز!")
        return
    
    await update.message.reply_text("👑 **پنل مدیریت**", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_main":
        await query.edit_message_text("🏠 **منوی اصلی**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
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
    if BOT_TOKEN:
        bot_app = Application.builder().token(BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("admin", admin_command))
        bot_app.add_handler(CallbackQueryHandler(callback_handler))
        
        await bot_app.bot.delete_webhook(drop_pending_updates=True)
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling()
        print("✅ Telegram Bot is running!")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        while True:
            time.sleep(1)
