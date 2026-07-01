#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Entry Point
نسخه نهایی - با تمام هندلرها و متغیرها
"""

import os
import sys
import asyncio
import time
import uvicorn

print("🚀 Starting CryptoPulse AI Bot v3.0...")

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
#                    SIMPLE BOT (مستقل)
# ============================================================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found!")
    exit(1)

# ============================================================
#                    KEYBOARDS
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

# ============================================================
#                    HANDLERS
# ============================================================

async def start(update, context):
    user_id = str(update.effective_user.id)
    is_admin = int(user_id) in ADMIN_IDS if user_id.isdigit() else False
    
    if is_admin:
        text = "👑 **پنل مدیریت**\n\nبه پنل ادمین خوش آمدید!"
        keyboard = admin_keyboard()
    else:
        text = "🌟 **به CryptoPulse AI خوش آمدید!**\n\nربات هوشمند تحلیل و سیگنال ارزهای دیجیتال"
        keyboard = user_keyboard()
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def admin_command(update, context):
    user_id = str(update.effective_user.id)
    is_admin = int(user_id) in ADMIN_IDS if user_id.isdigit() else False
    
    if not is_admin:
        await update.message.reply_text("❌ دسترسی غیرمجاز!")
        return
    
    await update.message.reply_text("👑 **پنل مدیریت**", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def vip_command(update, context):
    await update.message.reply_text(
        "💎 **VIP**\n\n💰 قیمت: ۱۹۹,۰۰۰ تومان\n💳 کارت: 6063731196254479\n🏦 به نام: به مرد",
        reply_markup=user_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def wallet_command(update, context):
    await update.message.reply_text(
        "💰 **کیف پول**\n\n💵 موجودی: $0.00\n📊 سود: $0.00",
        reply_markup=user_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_main":
        await query.edit_message_text("🏠 **منوی اصلی**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "analysis":
        await query.edit_message_text("📊 **تحلیل**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "signal":
        await query.edit_message_text("🚨 **سیگنال**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "wallet":
        await query.edit_message_text("💰 **کیف پول**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "vip":
        await query.edit_message_text("💎 **VIP**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "help":
        await query.edit_message_text("📖 **راهنما**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "support":
        await query.edit_message_text("🆘 **پشتیبانی**\n\n📱 @Amir92aa", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
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

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("vip", vip_command))
    app.add_handler(CommandHandler("wallet", wallet_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted!")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Bot is running with polling!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
