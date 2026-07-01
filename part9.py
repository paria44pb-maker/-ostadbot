#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Handlers Module
"""

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# ============================================================
#                    CONFIG
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

# ============================================================
#                    KEYBOARDS
# ============================================================

def user_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 تحلیل", callback_data="analysis")],
        [InlineKeyboardButton("🚨 سیگنال", callback_data="signal")],
        [InlineKeyboardButton("💰 قیمت", callback_data="price")],
        [InlineKeyboardButton("💎 VIP", callback_data="vip")],
        [InlineKeyboardButton("📖 راهنما", callback_data="help")],
        [InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("👑 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
        [InlineKeyboardButton("💎 مدیریت VIP", callback_data="admin_vip")],
        [InlineKeyboardButton("📢 ارسال همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================
#                    HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    is_admin = int(user_id) in ADMIN_IDS if user_id.isdigit() else False
    
    if is_admin:
        text = "👑 **پنل مدیریت**\n\nبه پنل ادمین خوش آمدید!"
        keyboard = admin_keyboard()
    else:
        text = "🌟 **به CryptoPulse AI خوش آمدید!**\n\nربات هوشمند تحلیل و سیگنال ارزهای دیجیتال"
        keyboard = user_keyboard()
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    is_admin = int(user_id) in ADMIN_IDS if user_id.isdigit() else False
    
    if not is_admin:
        await update.message.reply_text("❌ دسترسی غیرمجاز!")
        return
    
    await update.message.reply_text("👑 **پنل مدیریت**", reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 **قیمت BTC: $67,845.32**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_main":
        await query.edit_message_text("🏠 **منوی اصلی**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    elif data == "price":
        await query.edit_message_text("💰 **قیمت BTC: $67,845.32**", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
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
#                    MAIN HANDLER CLASS
# ============================================================

class BotHandlers:
    def __init__(self):
        self.application = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        if not BOT_TOKEN:
            return
        
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("admin", admin_command))
        self.application.add_handler(CommandHandler("price", price_command))
        self.application.add_handler(CallbackQueryHandler(callback_handler))
    
    def get_application(self):
        return self.application

# ============================================================
#                    EXPORT
# ============================================================

bot_handlers = BotHandlers()

def get_handlers():
    return bot_handlers

def get_application():
    return bot_handlers.get_application() if bot_handlers else None
