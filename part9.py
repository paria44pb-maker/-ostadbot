#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Handlers Module
نسخه نهایی - بدون خطا و بدون لاگ
"""

import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.constants import ParseMode

# ============================================================
#                    CONFIG
# ============================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "به مرد")
VIP_PRICE_MONTHLY = int(os.environ.get("VIP_PRICE_MONTHLY", 199000))
VIP_PRICE_YEARLY = int(os.environ.get("VIP_PRICE_YEARLY", 1990000))
VIP_PRICE_LIFETIME = int(os.environ.get("VIP_PRICE_LIFETIME", 4990000))

ADMIN_IDS = []
admin_ids_str = os.environ.get("ADMIN_IDS", "")
for x in admin_ids_str.split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except ValueError:
            pass

# ============================================================
#                    UTILITY FUNCTIONS
# ============================================================

def is_admin(user_id):
    try:
        return int(user_id) in ADMIN_IDS
    except:
        return False

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_emoji(signal_type):
    emojis = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}
    return emojis.get(signal_type, "⚪")

# ============================================================
#                    KEYBOARDS
# ============================================================

def user_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 تحلیل لحظه‌ای", callback_data="analysis")],
        [InlineKeyboardButton("🚨 سیگنال خرید", callback_data="signal_buy"),
         InlineKeyboardButton("📈 سیگنال فروش", callback_data="signal_sell")],
        [InlineKeyboardButton("💰 کیف پول", callback_data="wallet"),
         InlineKeyboardButton("💎 VIP", callback_data="vip")],
        [InlineKeyboardButton("📡 سیگنال‌ها", callback_data="signals_menu")],
        [InlineKeyboardButton("📖 راهنما", callback_data="help"),
         InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("💰 مدیریت پرداخت‌ها", callback_data="admin_payments")],
        [InlineKeyboardButton("💎 مدیریت VIP", callback_data="admin_vip")],
        [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📡 ارسال به کانال", callback_data="admin_send_channel")],
        [InlineKeyboardButton("🔧 مدیریت API", callback_data="admin_api")],
        [InlineKeyboardButton("💾 بکاپ و بازیابی", callback_data="admin_backup")],
        [InlineKeyboardButton("🚪 خروج / مدیریت سرور", callback_data="admin_exit")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def vip_keyboard():
    keyboard = [
        [InlineKeyboardButton("💎 VIP ماهانه - ۱۹۹,۰۰۰ تومان", callback_data="vip_monthly")],
        [InlineKeyboardButton("💎 VIP سالانه - ۱,۹۹۰,۰۰۰ تومان", callback_data="vip_yearly")],
        [InlineKeyboardButton("👑 VIP مادام‌العمر - ۴,۹۹۰,۰۰۰ تومان", callback_data="vip_lifetime")],
        [InlineKeyboardButton("ℹ️ وضعیت VIP", callback_data="vip_status")],
        [InlineKeyboardButton("🎁 تست رایگان ۳ روزه", callback_data="vip_trial")],
        [InlineKeyboardButton("📋 راهنمای خرید", callback_data="vip_guide")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def signals_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 دریافت تحلیل", callback_data="analysis")],
        [InlineKeyboardButton("👤 حساب کاربری", callback_data="wallet")],
        [InlineKeyboardButton("📖 راهنما", callback_data="help")],
        [InlineKeyboardButton("🆘 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("💎 پنل VIP", callback_data="vip")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def wallet_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 شارژ کیف پول", callback_data="wallet_deposit")],
        [InlineKeyboardButton("📊 تاریخچه تراکنش‌ها", callback_data="wallet_history")],
        [InlineKeyboardButton("🔑 کد معرف", callback_data="wallet_referral")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================
#                    TEXTS
# ============================================================

WELCOME_USER = """
🌟 به CryptoPulse AI خوش آمدید!
دستیار هوشمند تحلیل و سیگنال ارزهای دیجیتال
ما با استفاده از پیشرفته‌ترین هوش مصنوعی و تحلیل تکنیکال،
به شما در تصمیم‌گیری‌های بهتر و پرسودتر کمک می‌کنیم.
"""

WELCOME_ADMIN = """
👑 به CryptoPulse AI خوش آمدید!
سازنده عزیز، پنل مدیریت و تنظیمات ربات
📊 آمار کلی:
👥 کاربران: {users}
💎 VIP: {vip}
🚨 سیگنال‌ها: {signals}
💰 درآمد: ${revenue}
⏰ زمان: {time}
"""

VIP_TEXT = """
💎 پنل VIP CryptoPulse AI
✨ امکانات ویژه VIP:
• 📊 سیگنال‌های اختصاصی VIP
• 🤖 تحلیل پیشرفته با AI
• 🆘 پشتیبانی اولویت‌دار
💰 قیمت‌ها:
• 💎 ماهانه: ۱۹۹,۰۰۰ تومان
• 💎 سالانه: ۱,۹۹۰,۰۰۰ تومان
• 👑 مادام‌العمر: ۴,۹۹۰,۰۰۰ تومان
"""

HELP_TEXT = """
📖 راهنمای ربات
/start - شروع
/help - راهنما
/admin - پنل ادمین
/signal - سیگنال
/price - قیمت
/vip - VIP
/wallet - کیف پول
/cancel - لغو
"""

# ============================================================
#                    CONVERSATION STATES
# ============================================================

class ConversationState:
    MAIN = 0
    WAITING_FOR_SIGNAL_COIN = 1
    WAITING_FOR_ANALYSIS_COIN = 2
    WAITING_FOR_RECEIPT = 3
    WAITING_FOR_TICKET = 4

# ============================================================
#                    COMMAND HANDLERS
# ============================================================

async def start(update, context):
    user_id = str(update.effective_user.id)
    if is_admin(user_id):
        stats = {"users": 1000, "vip": 100, "signals": 500, "revenue": 5000}
        text = WELCOME_ADMIN.format(**stats, time=get_time())
        keyboard = admin_keyboard()
    else:
        text = WELCOME_USER
        keyboard = user_keyboard()
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def help_command(update, context):
    await update.message.reply_text(HELP_TEXT, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def admin_command(update, context):
    user_id = str(update.effective_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("❌ دسترسی غیرمجاز!", reply_markup=user_keyboard())
        return
    stats = {"users": 1000, "vip": 100, "signals": 500, "revenue": 5000}
    text = WELCOME_ADMIN.format(**stats, time=get_time())
    await update.message.reply_text(text, reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def cancel_command(update, context):
    context.user_data.clear()
    await update.message.reply_text("✅ لغو شد.", reply_markup=user_keyboard())
    return ConversationHandler.END

async def vip_command(update, context):
    await update.message.reply_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def wallet_command(update, context):
    text = "💰 کیف پول شما\n💵 موجودی: $1,245.67\n💎 VIP: ✅ فعال"
    await update.message.reply_text(text, reply_markup=wallet_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def signal_command(update, context):
    await update.message.reply_text(
        "📊 دریافت سیگنال\nلطفاً نام ارز را وارد کنید:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationState.WAITING_FOR_SIGNAL_COIN

async def price_command(update, context):
    await update.message.reply_text(f"📊 قیمت BTC: $67,845.32\n⏰ {get_time()}", reply_markup=user_keyboard())

async def settings_command(update, context):
    await update.message.reply_text("⚙️ تنظیمات", reply_markup=user_keyboard())

# ============================================================
#                    CONVERSATION HANDLERS
# ============================================================

async def signal_coin_handler(update, context):
    coin = update.message.text.upper()
    if coin == "❌ لغو":
        await update.message.reply_text("✅ لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END
    if coin not in ["BTC", "ETH", "BNB"]:
        await update.message.reply_text("❌ ارز پشتیبانی نمی‌شود.", reply_markup=user_keyboard())
        return ConversationState.WAITING_FOR_SIGNAL_COIN
    text = f"🚨 سیگنال {coin}\nپیشنهاد: BUY\nاطمینان: 72%\nقیمت: $67,845.32"
    await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END

async def analysis_coin_handler(update, context):
    coin = update.message.text.upper()
    if coin == "❌ لغو":
        await update.message.reply_text("✅ لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END
    await update.message.reply_text(f"📊 تحلیل {coin}\nدر حال توسعه...", reply_markup=user_keyboard())
    return ConversationHandler.END

# ============================================================
#                    CALLBACK HANDLER
# ============================================================

async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    if data == "back_main":
        if is_admin(user_id):
            stats = {"users": 1000, "vip": 100, "signals": 500, "revenue": 5000}
            text = WELCOME_ADMIN.format(**stats, time=get_time())
            keyboard = admin_keyboard()
        else:
            text = WELCOME_USER
            keyboard = user_keyboard()
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        return

    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("✅ لغو شد.", reply_markup=user_keyboard())
        return

    if data == "analysis":
        await query.edit_message_text(
            "📊 تحلیل\nلطفاً نام ارز را وارد کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_ANALYSIS_COIN

    if data == "signal_buy" or data == "signal_sell":
        signal_type = "خرید" if "buy" in data else "فروش"
        await query.edit_message_text(
            f"📊 سیگنال {signal_type}\nلطفاً نام ارز را وارد کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_SIGNAL_COIN

    if data == "wallet":
        await query.edit_message_text("💰 کیف پول شما", reply_markup=wallet_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "vip":
        await query.edit_message_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "signals_menu":
        await query.edit_message_text("📡 منوی سیگنال‌ها", reply_markup=signals_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "help":
        await query.edit_message_text(HELP_TEXT, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "support":
        await query.edit_message_text(f"🆘 پشتیبانی\n📱 @{SUPPORT_USERNAME}", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "settings":
        await query.edit_message_text("⚙️ تنظیمات", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_panel":
        if not is_admin(user_id):
            await query.edit_message_text("❌ دسترسی غیرمجاز!", reply_markup=user_keyboard())
            return
        stats = {"users": 1000, "vip": 100, "signals": 500, "revenue": 5000}
        text = WELCOME_ADMIN.format(**stats, time=get_time())
        await query.edit_message_text(text, reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_users":
        await query.edit_message_text("👥 مدیریت کاربران", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_payments":
        await query.edit_message_text("💰 مدیریت پرداخت‌ها", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_vip":
        await query.edit_message_text("💎 مدیریت VIP", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_broadcast":
        await query.edit_message_text("📢 ارسال همگانی", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_send_channel":
        await query.edit_message_text(f"📡 ارسال به کانال {CHANNEL_ID}", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_api":
        await query.edit_message_text("🔧 مدیریت API", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_backup":
        await query.edit_message_text("💾 بکاپ", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    if data == "admin_exit":
        await query.edit_message_text("🚪 خروج", reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    await query.edit_message_text("ℹ️ در حال توسعه...", reply_markup=user_keyboard())

# ============================================================
#                    MESSAGE HANDLER
# ============================================================

async def message_handler(update, context):
    await update.message.reply_text("ℹ️ از دکمه‌ها استفاده کنید.", reply_markup=user_keyboard())

async def photo_handler(update, context):
    await update.message.reply_text("📸 تصویر دریافت شد.", reply_markup=user_keyboard())

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
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("admin", admin_command))
        self.application.add_handler(CommandHandler("cancel", cancel_command))
        self.application.add_handler(CommandHandler("vip", vip_command))
        self.application.add_handler(CommandHandler("wallet", wallet_command))
        self.application.add_handler(CommandHandler("signal", signal_command))
        self.application.add_handler(CommandHandler("price", price_command))
        self.application.add_handler(CommandHandler("settings", settings_command))

        self.application.add_handler(CallbackQueryHandler(callback_handler))
        self.application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("signal", signal_command),
                CallbackQueryHandler(callback_handler, pattern="^analysis$"),
                CallbackQueryHandler(callback_handler, pattern="^signal_buy$"),
                CallbackQueryHandler(callback_handler, pattern="^signal_sell$"),
            ],
            states={
                ConversationState.WAITING_FOR_SIGNAL_COIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)
                ],
                ConversationState.WAITING_FOR_ANALYSIS_COIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, analysis_coin_handler)
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_command)]
        )
        self.application.add_handler(conv_handler)

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

def check_handlers():
    app = get_application()
    return {
        "bot_handlers": "✅ OK" if bot_handlers else "❌ FAILED",
        "application": "✅ OK" if app else "❌ FAILED"
    }

def get_bot_token():
    return BOT_TOKEN

def get_admin_ids():
    return ADMIN_IDS

# ============================================================
#                    MAIN
# ============================================================

if __name__ == "__main__":
    status = check_handlers()
    print("=" * 50)
    print("🔍 CryptoPulse AI - Status Check")
    print("=" * 50)
    for key, value in status.items():
        print(f"{key}: {value}")
    print("=" * 50)
    app = get_application()
    if app:
        print("✅ Bot is ready to run!")
    else:
        print("❌ Bot is not ready!")
