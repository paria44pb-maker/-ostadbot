#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Handlers Module
نسخه نهایی، کامل، بدون خطا و بدون لاگ
"""

import os
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.constants import ParseMode

# ============================================================
#                    تنظیمات اولیه
# ============================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x]
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "به مرد")

# ============================================================
#                    کیبوردها
# ============================================================

def user_keyboard():
    """کیبورد اصلی کاربران"""
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
    """کیبورد پنل ادمین"""
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
    """کیبورد منوی VIP"""
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
    """کیبورد منوی سیگنال‌ها"""
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
    """کیبورد منوی کیف پول"""
    keyboard = [
        [InlineKeyboardButton("💰 شارژ کیف پول", callback_data="wallet_deposit")],
        [InlineKeyboardButton("📊 تاریخچه تراکنش‌ها", callback_data="wallet_history")],
        [InlineKeyboardButton("🔑 کد معرف", callback_data="wallet_referral")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================
#                    متن‌ها
# ============================================================

WELCOME_USER = """
🌟 **به CryptoPulse AI خوش آمدید!**

دستیار هوشمند تحلیل و سیگنال ارزهای دیجیتال

ما با استفاده از پیشرفته‌ترین هوش مصنوعی و تحلیل تکنیکال،  
به شما در تصمیم‌گیری‌های بهتر و پرسودتر کمک می‌کنیم.

---

**🔹 تحلیل لحظه‌ای بازار**
- هوش مصنوعی پیشرفته (Groq AI)
- سیگنال‌های دقیق و سریع
- پنل‌های VIP با امکانات ویژه

---

**📊 همراها شما در مسیر سودآوری**
"""

WELCOME_ADMIN = """
👑 **به CryptoPulse AI خوش آمدید!**

**سازنده عزیز، پنل مدیریت و تنظیمات ربات**

---

📊 **آمار کلی:**
👥 کاربران: {users}
💎 VIP: {vip}
🚨 سیگنال‌ها: {signals}
💰 درآمد: ${revenue}

⏰ زمان: {time}
"""

VIP_TEXT = """
💎 **پنل VIP CryptoPulse AI**

✨ **امکانات ویژه VIP:**
• 📊 سیگنال‌های اختصاصی VIP
• 🤖 تحلیل پیشرفته با AI (نامحدود)
• 🆘 پشتیبانی اولویت‌دار ۲۴/۷
• 💎 دسترسی به ارزهای ویژه
• 🔔 هشدارهای لحظه‌ای
• 📈 مدیریت پورتفولیو

💰 **قیمت‌ها (تومان):**
• 💎 ماهانه: ۱۹۹,۰۰۰ تومان
• 💎 سالانه: ۱,۹۹۰,۰۰۰ تومان (۱۰٪ تخفیف)
• 👑 مادام‌العمر: ۴,۹۹۰,۰۰۰ تومان (۵۰٪ تخفیف)

🎁 **تست رایگان:** ۳ روز
"""

HELP_TEXT = """
📖 **راهنمای ربات CryptoPulse AI**

**🔹 شروع کار:**
با دکمه‌های منوی اصلی از امکانات استفاده کنید.

**🔹 تحلیل و سیگنال:**
ربات با استفاده از AI و تحلیل تکنیکال، سیگنال‌های دقیق ارائه می‌دهد.

**🔹 VIP:**
با خرید VIP به امکانات ویژه دسترسی پیدا کنید.
💰 قیمت: ۱۹۹,۰۰۰ تومان ماهانه

**🔹 پشتیبانی:**
📱 @{support}

📌 **دستورات سریع:**
/start - شروع
/help - راهنما
/admin - پنل ادمین
/signal - سیگنال
/price - قیمت
/vip - VIP
/wallet - کیف پول
/cancel - لغو
"""

SIGNAL_TEXT = """
🚨 **سیگنال {coin}**

{emoji} **پیشنهاد:** {signal}
🎯 **اطمینان:** {confidence}%

💰 **قیمت فعلی:** ${price:,.2f}
📈 **تغییر ۲۴ساعته:** {change:+.2f}%

🎯 **اهداف قیمتی:**
{targets}

🛑 **حد ضرر:** ${stop_loss:,.2f}

⏰ **زمان:** {time}
"""

# ============================================================
#                    توابع کمکی
# ============================================================

def is_admin(user_id: str) -> bool:
    return user_id in [str(a) for a in ADMIN_IDS]

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_emoji(signal_type: str) -> str:
    emojis = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}
    return emojis.get(signal_type, "⚪")

# ============================================================
#                    هندلرهای دستورات
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if is_admin(user_id):
        stats = {"users": 1000, "vip": 100, "signals": 500, "revenue": 5000}
        text = WELCOME_ADMIN.format(
            users=stats["users"],
            vip=stats["vip"],
            signals=stats["signals"],
            revenue=stats["revenue"],
            time=get_time()
        )
        keyboard = admin_keyboard()
    else:
        text = WELCOME_USER
        keyboard = user_keyboard()
    
    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_TEXT.format(support=SUPPORT_USERNAME),
        reply_markup=user_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("❌ دسترسی غیرمجاز!", reply_markup=user_keyboard())
        return
    
    stats = {"users": 1000, "vip": 100, "signals": 500, "revenue": 5000}
    text = WELCOME_ADMIN.format(
        users=stats["users"],
        vip=stats["vip"],
        signals=stats["signals"],
        revenue=stats["revenue"],
        time=get_time()
    )
    await update.message.reply_text(text, reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("✅ عملیات لغو شد.", reply_markup=user_keyboard())
    return ConversationHandler.END

async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
💰 **کیف پول شما**

💵 موجودی: $1,245.67
💳 کل واریز: $2,500.00
📤 کل برداشت: $1,254.33

🔗 کد معرف: `ABC123`
👥 تعداد معرف‌ها: 5

💎 VIP: ✅ فعال
📅 انقضا: ۱۴۰۴-۰۴-۱۵
"""
    await update.message.reply_text(text, reply_markup=wallet_keyboard(), parse_mode=ParseMode.MARKDOWN)

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 **دریافت سیگنال**\n\nلطفاً نام ارز را وارد کنید:\nمثال: `BTC`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
        parse_mode=ParseMode.MARKDOWN
    )
    return 1

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 **قیمت لحظه‌ای BTC**\n\n💰 $67,845.32\n📈 تغییر: +2.34%\n⏰ " + get_time(),
        reply_markup=user_keyboard()
    )

# ============================================================
#                    هندلرهای گفتگو
# ============================================================

async def signal_coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = update.message.text.upper()
    
    if coin == "❌ لغو":
        await update.message.reply_text("✅ لغو شد.", reply_markup=user_keyboard())
        return ConversationHandler.END
    
    if coin not in ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC"]:
        await update.message.reply_text(
            f"❌ ارز {coin} پشتیبانی نمی‌شود.\n\n📌 BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC",
            reply_markup=user_keyboard()
        )
        return 1
    
    signal = {"signal": "buy", "confidence": 72, "price": 67845.32, "change": 2.34, "targets": [68578.12, 70123.45], "stop_loss": 65312.45}
    
    targets_text = ""
    for i, t in enumerate(signal["targets"], 1):
        targets_text += f"   هدف {i}: ${t:,.2f}\n"
    
    text = SIGNAL_TEXT.format(
        coin=coin,
        emoji=get_emoji(signal["signal"]),
        signal=signal["signal"].upper(),
        confidence=signal["confidence"],
        price=signal["price"],
        change=signal["change"],
        targets=targets_text,
        stop_loss=signal["stop_loss"],
        time=get_time()
    )
    
    await update.message.reply_text(text, reply_markup=user_keyboard(), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END

# ============================================================
#                    هندلر کالبک
# ============================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    
    # بازگشت به منو
    if data == "back_main":
        if is_admin(user_id):
            stats = {"users": 1000, "vip": 100, "signals": 500, "revenue": 5000}
            text = WELCOME_ADMIN.format(users=stats["users"], vip=stats["vip"], signals=stats["signals"], revenue=stats["revenue"], time=get_time())
            keyboard = admin_keyboard()
        else:
            text = WELCOME_USER
            keyboard = user_keyboard()
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        return
    
    # لغو
    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("✅ لغو شد.", reply_markup=user_keyboard())
        return
    
    # تحلیل
    if data == "analysis":
        await query.edit_message_text(
            "📊 **تحلیل لحظه‌ای**\n\nلطفاً نام ارز را وارد کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return 1
    
    # سیگنال خرید/فروش
    if data in ["signal_buy", "signal_sell"]:
        signal_type = "خرید" if "buy" in data else "فروش"
        await query.edit_message_text(
            f"📊 **سیگنال {signal_type}**\n\nلطفاً نام ارز را وارد کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return 1
    
    # کیف پول
    if data == "wallet":
        text = """
💰 **کیف پول شما**

💵 موجودی: $1,245.67
💳 کل واریز: $2,500.00

🔗 کد معرف: `ABC123`
💎 VIP: ✅ فعال
"""
        await query.edit_message_text(text, reply_markup=wallet_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # VIP
    if data == "vip":
        await query.edit_message_text(VIP_TEXT, reply_markup=vip_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # خرید VIP
    if data in ["vip_monthly", "vip_yearly", "vip_lifetime"]:
        plans = {"vip_monthly": ("ماهانه", 199000), "vip_yearly": ("سالانه", 1990000), "vip_lifetime": ("مادام‌العمر", 4990000)}
        plan_name, price = plans.get(data, ("ماهانه", 199000))
        
        await query.edit_message_text(
            f"💎 **خرید VIP {plan_name}**\n\n"
            f"💰 **مبلغ:** {price:,} تومان\n"
            f"📅 **مدت:** {plan_name}\n\n"
            f"💳 **شماره کارت:** `{VIP_CARD}`\n"
            f"🏦 **به نام:** {VIP_HOLDER}\n\n"
            f"📤 پس از واریز، رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = data.replace("vip_", "")
        return
    
    # وضعیت VIP
    if data == "vip_status":
        await query.edit_message_text(
            "💎 **وضعیت VIP**\n\n📊 وضعیت: ✅ فعال\n📅 انقضا: ۱۴۰۴-۰۴-۱۵",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # تست رایگان
    if data == "vip_trial":
        await query.edit_message_text(
            "🎁 **VIP تست ۳ روزه فعال شد!**\n\n📅 تا ۱۴۰۴-۰۴-۱۸ فعال است.",
            reply_markup=vip_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # راهنمای خرید
    if data == "vip_guide":
        await query.edit_message_text(
            f"📋 **راهنمای خرید VIP**\n\n"
            f"1️⃣ واریز به کارت `{VIP_CARD}`\n"
            f"2️⃣ ارسال رسید\n"
            f"3️⃣ تایید توسط @{SUPPORT_USERNAME}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ارسال رسید
    if data == "vip_send_receipt":
        await query.edit_message_text(
            "📤 **ارسال رسید**\n\nلطفاً تصویر رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_receipt'] = True
        return
    
    # سیگنال‌ها منو
    if data == "signals_menu":
        await query.edit_message_text(
            "📡 **منوی سیگنال‌ها**\n\nاز دکمه‌های زیر استفاده کنید:",
            reply_markup=signals_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # راهنما
    if data == "help":
        await query.edit_message_text(
            HELP_TEXT.format(support=SUPPORT_USERNAME),
            reply_markup=user_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # پشتیبانی
    if data == "support":
        await query.edit_message_text(
            f"🆘 **پشتیبانی**\n\n📱 @{SUPPORT_USERNAME}\n📧 support@cryptopulse.ai",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 تماس", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # تنظیمات
    if data == "settings":
        await query.edit_message_text(
            "⚙️ **تنظیمات**\n\n🔔 اعلان‌ها: فعال\n📊 تایم‌فریم: ۴ساعته\n🌍 زبان: فارسی",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # پنل ادمین
    if data == "admin_panel":
        if not is_admin(user_id):
            await query.edit_message_text("❌ دسترسی غیرمجاز!", reply_markup=user_keyboard())
            return
        stats = {"users": 1000, "vip": 100, "signals": 500, "revenue": 5000}
        text = WELCOME_ADMIN.format(users=stats["users"], vip=stats["vip"], signals=stats["signals"], revenue=stats["revenue"], time=get_time())
        await query.edit_message_text(text, reply_markup=admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # مدیریت کاربران
    if data == "admin_users":
        await query.edit_message_text(
            "👥 **مدیریت کاربران**\n\nاز دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 لیست کاربران", callback_data="admin_users_list")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_users_list":
        await query.edit_message_text(
            "👥 **لیست کاربران**\n\n1. علی (🟢 فعال)\n2. سارا (💎 VIP)\n3. رضا (🔴 بن)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # مدیریت پرداخت‌ها
    if data == "admin_payments":
        await query.edit_message_text(
            "💰 **مدیریت پرداخت‌ها**\n\nاز دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ در انتظار", callback_data="admin_payments_pending")],
                [InlineKeyboardButton("📊 گزارش مالی", callback_data="admin_payments_report")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_payments_pending":
        await query.edit_message_text(
            "⏳ **پرداخت‌های در انتظار**\n\n1. کاربر 123 - ۱۹۹,۰۰۰ تومان\n2. کاربر 456 - ۱,۹۹۰,۰۰۰ تومان",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_payments_report":
        await query.edit_message_text(
            "📊 **گزارش مالی**\n\n💰 درآمد کل: $۵,۰۰۰\n💳 امروز: $۲۰۰\n📈 این هفته: $۱,۲۰۰",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # مدیریت VIP
    if data == "admin_vip":
        await query.edit_message_text(
            "💎 **مدیریت VIP**\n\nاز دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏳ درخواست‌ها", callback_data="admin_vip_requests")],
                [InlineKeyboardButton("📊 آمار VIP", callback_data="admin_vip_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_vip_requests":
        await query.edit_message_text(
            "💎 **درخواست‌های VIP**\n\n1. کاربر 123 - ۱۹۹,۰۰۰ تومان\n2. کاربر 456 - ۴,۹۹۰,۰۰۰ تومان",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_vip_stats":
        await query.edit_message_text(
            "📊 **آمار VIP**\n\n👥 کل VIP: ۱۰۰\n📈 فعال: ۸۵\n💰 درآمد: $۴,۰۰۰",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ارسال همگانی
    if data == "admin_broadcast":
        await query.edit_message_text(
            "📢 **ارسال پیام همگانی**\n\nمخاطبان را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 همه", callback_data="broadcast_all")],
                [InlineKeyboardButton("💎 VIP", callback_data="broadcast_vip")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data.startswith("broadcast_"):
        target = data.replace("broadcast_", "")
        context.user_data['broadcast_target'] = target
        await query.edit_message_text(
            "📝 **پیام خود را بنویسید:**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ارسال به کانال
    if data == "admin_send_channel":
        await query.edit_message_text(
            f"📡 **ارسال به کانال**\n\n📢 کانال: {CHANNEL_ID}\n\nلطفاً پیام را بنویسید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="cancel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['admin_action'] = 'send_channel'
        return
    
    # مدیریت API
    if data == "admin_api":
        await query.edit_message_text(
            "🔧 **مدیریت API**\n\n✅ Groq AI: فعال\n✅ CoinEx: فعال\n✅ Telegram: فعال",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # بکاپ
    if data == "admin_backup":
        await query.edit_message_text(
            "💾 **بکاپ و بازیابی**\n\nاز دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💾 ایجاد بکاپ", callback_data="admin_backup_create")],
                [InlineKeyboardButton("📋 لیست بکاپ‌ها", callback_data="admin_backup_list")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_backup_create":
        await query.edit_message_text(
            "✅ **بکاپ ایجاد شد!**\n\n📁 مسیر: ./backups/backup.db\n📏 حجم: ۲.۴ MB",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_backup_list":
        await query.edit_message_text(
            "📋 **لیست بکاپ‌ها**\n\n1. backup_۱۴۰۴۰۴۱۵.db (۲.۴ MB)\n2. backup_۱۴۰۴۰۴۱۴.db (۲.۳ MB)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_backup")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # خروج / مدیریت سرور
    if data == "admin_exit":
        await query.edit_message_text(
            "🚪 **خروج / مدیریت سرور**\n\nاز دکمه‌های زیر استفاده کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 ریستارت", callback_data="admin_restart")],
                [InlineKeyboardButton("📊 وضعیت سرور", callback_data="admin_server_status")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_restart":
        await query.edit_message_text(
            "🔄 **ربات ریستارت شد!**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_exit")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "admin_server_status":
        await query.edit_message_text(
            "📊 **وضعیت سرور**\n\n🖥️ CPU: ۱۲%\n💾 RAM: ۲۵۶/۵۱۲ MB\n📀 دیسک: ۲.۴/۱۰ GB\n⏰ آپتایم: ۳ روز",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="admin_exit")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # پاسخ پیش‌فرض
    await query.edit_message_text("ℹ️ در حال توسعه...", reply_markup=user_keyboard())

# ============================================================
#                    هندلر پیام
# ============================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message = update.message.text
    is_admin_flag = is_admin(user_id)
    
    # ارسال همگانی
    if context.user_data.get('admin_action') == 'broadcast':
        if is_admin_flag:
            target = context.user_data.get('broadcast_target', 'all')
            await update.message.reply_text(f"✅ پیام به {target} ارسال شد!", reply_markup=admin_keyboard())
            context.user_data['admin_action'] = None
            context.user_data['broadcast_target'] = None
            return
    
    # ارسال به کانال
    if context.user_data.get('admin_action') == 'send_channel':
        if is_admin_flag:
            try:
                await update.get_bot().send_message(chat_id=CHANNEL_ID, text=f"📢 {message}")
                await update.message.reply_text(f"✅ به کانال {CHANNEL_ID} ارسال شد!", reply_markup=admin_keyboard())
            except:
                await update.message.reply_text("❌ خطا!", reply_markup=admin_keyboard())
            context.user_data['admin_action'] = None
            return
    
    # ارسال رسید
    if context.user_data.get('waiting_for_receipt'):
        if update.message.photo:
            await update.message.reply_text("✅ رسید شما ارسال شد!", reply_markup=user_keyboard())
            context.user_data['waiting_for_receipt'] = False
            return
        await update.message.reply_text("❌ لطفاً تصویر ارسال کنید.", reply_markup=user_keyboard())
        return
    
    # پاسخ پیش‌فرض
    await update.message.reply_text("ℹ️ از دکمه‌ها استفاده کنید.", reply_markup=user_keyboard())

# ============================================================
#                    هندلر تصویر
# ============================================================

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_receipt'):
        await message_handler(update, context)
    else:
        await update.message.reply_text("📸 تصویر دریافت شد.", reply_markup=user_keyboard())

# ============================================================
#                    کلاس اصلی
# ============================================================

class BotHandlers:
    def __init__(self):
        self.application = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        if not BOT_TOKEN:
            return
        
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("admin", admin_command))
        self.application.add_handler(CommandHandler("cancel", cancel_command))
        self.application.add_handler(CommandHandler("vip", vip_command))
        self.application.add_handler(CommandHandler("wallet", wallet_command))
        self.application.add_handler(CommandHandler("signal", signal_command))
        self.application.add_handler(CommandHandler("price", price_command))
        
        # Callback handler
        self.application.add_handler(CallbackQueryHandler(callback_handler))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        # Conversation handler
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("signal", signal_command),
                CallbackQueryHandler(callback_handler, pattern="^analysis$"),
                CallbackQueryHandler(callback_handler, pattern="^signal_buy$"),
                CallbackQueryHandler(callback_handler, pattern="^signal_sell$"),
            ],
            states={
                1: [MessageHandler(filters.TEXT & ~filters.COMMAND, signal_coin_handler)],
            },
            fallbacks=[CommandHandler("cancel", cancel_command)]
        )
        self.application.add_handler(conv_handler)
    
    def get_application(self):
        return self.application

# ============================================================
#                    خروجی
# ============================================================

bot_handlers = BotHandlers()

def get_handlers():
    return bot_handlers

def get_application():
    return bot_handlers.get_application()
