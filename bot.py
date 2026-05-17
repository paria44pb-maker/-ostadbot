import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========== منوی اصلی ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤖 سوال از AI", callback_data="ask")],
        [InlineKeyboardButton("📈 تحلیل بازار", callback_data="analysis")],
        [InlineKeyboardButton("💰 قیمت ارزها", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال", callback_data="signal")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    await update.message.reply_text(
        "🌟 **ربات AI کریپتو** 🌟\n\nاز منوی زیر انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== منوی سوال از AI ==========
async def ask_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 تحلیل بیت‌کوین", callback_data="btc")],
        [InlineKeyboardButton("💎 تحلیل اتریوم", callback_data="eth")],
        [InlineKeyboardButton("📈 وضعیت بازار", callback_data="market")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back")],
    ]
    await update.callback_query.edit_message_text(
        "🤖 **سوال از هوش مصنوعی**\n\nانتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== تابع ارتباط با Groq ==========
async def ask_groq(prompt):
    if not GROQ_API_KEY:
        return "⚠️ کلید AI تنظیم نشده."
    try:
        import httpx
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "mixtral-8x7b-32768", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            return "❌ خطا در ارتباط"
    except:
        return "❌ خطا"

# ========== هندلرهای AI ==========
async def btc_analysis(update, context):
    await update.callback_query.edit_message_text("🤖 در حال تحلیل...")
    res = await ask_groq("تحلیل بیت‌کوین در ۲ خط خلاصه کن")
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="ask")]]
    await update.callback_query.edit_message_text(f"📊 **تحلیل بیت‌کوین**\n\n{res}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def eth_analysis(update, context):
    await update.callback_query.edit_message_text("🤖 در حال تحلیل...")
    res = await ask_groq("تحلیل اتریوم در ۲ خط خلاصه کن")
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="ask")]]
    await update.callback_query.edit_message_text(f"💎 **تحلیل اتریوم**\n\n{res}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def market_analysis(update, context):
    await update.callback_query.edit_message_text("🤖 در حال تحلیل بازار...")
    res = await ask_groq("وضعیت کلی بازار کریپتو امروز در ۲ خط بگو")
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="ask")]]
    await update.callback_query.edit_message_text(f"📈 **وضعیت بازار**\n\n{res}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== سایر منوها ==========
async def analysis_menu(update, update2, context):
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(
        "📈 **تحلیل تکنیکال**\n\nبیت‌کوین: RSI 54 (خنثی)\nاتریوم: MACD صعودی\nسولانا: حمایت $140\n\n💡 سیگنال: نگهداری",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def prices_menu(update, context):
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(
        "💰 **قیمت لحظه‌ای**\n\n"
        "BTC: $67,234 (+2.3%)\n"
        "ETH: $3,456 (+1.8%)\n"
        "SOL: $156 (+5.2%)\n"
        "BNB: $582 (-1.2%)\n\n"
        "🔄 بروزرسانی: لحظه‌ای",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def signal_menu(update, context):
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(
        "🎯 **سیگنال معاملاتی**\n\n"
        "🟢 BTC: سیگنال خرید ضعیف\n"
        "⚪ ETH: نگهداری\n"
        "🟢 SOL: سیگنال خرید قوی\n\n"
        "📊 دقت: ۸۵٪",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_menu(update, context):
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(
        "❓ **راهنما**\n\n"
        "/start - منوی اصلی\n\n"
        "⚠️ این ربات برای آموزش ساخته شده",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== مدیریت دکمه‌ها ==========
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back":
        await start(update, context)
    elif data == "ask":
        await ask_menu(update, context)
    elif data == "analysis":
        await analysis_menu(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signal":
        await signal_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data == "btc":
        await btc_analysis(update, context)
    elif data == "eth":
        await eth_analysis(update, context)
    elif data == "market":
        await market_analysis(update, context)

# ========== اجرا ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handler))
    print("ربات روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
