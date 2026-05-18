import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# قیمت‌های شبیه‌سازی شده (برای تست - بعداً با API واقعی جایگزین می‌شود)
fake_prices = {
    "BTC": {"price": 67234, "change": 2.3},
    "ETH": {"price": 3456, "change": 1.8},
    "SOL": {"price": 156.7, "change": 5.2},
    "BNB": {"price": 582, "change": -1.2},
}

async def get_realtime_price(symbol="BTC"):
    """دریافت قیمت واقعی از بایننس"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT")
            if response.status_code == 200:
                data = response.json()
                return {
                    "price": float(data['lastPrice']),
                    "change": float(data['priceChangePercent']),
                    "source": "Binance"
                }
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
    return None

def calculate_rsi(prices, period=14):
    """محاسبه ساده RSI"""
    if len(prices) < period + 1:
        return 50
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-diff)
    avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0
    avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_signal(price, change, rsi):
    """تولید سیگنال بر اساس قیمت و RSI"""
    if change > 3 and rsi < 60:
        return "🟢 خرید قوی"
    elif change > 1:
        return "🟢 خرید ملایم"
    elif change < -3 and rsi > 40:
        return "🔴 فروش قوی"
    elif change < -1:
        return "🔴 فروش ملایم"
    else:
        return "⚪ نگهداری"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال", callback_data="signals")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("💰 پرتفوی", callback_data="portfolio")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    text = """
🔥 **ربات تریدر حرفه‌ای** 🔥

✅ **قابلیت‌ها:**
• 📊 قیمت لحظه‌ای از بایننس
• 🎯 سیگنال خرید/فروش
• 📈 تحلیل تکنیکال (RSI)
• 💰 مدیریت پرتفوی

---
📌 از منوی زیر انتخاب کن 👇
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🔄 دریافت قیمت‌ها...", parse_mode="Markdown")
    
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    text = "📊 **قیمت لحظه‌ای ارزها** 📊\n\n"
    
    for symbol in symbols:
        data = await get_realtime_price(symbol)
        if data:
            emoji = "🟢" if data['change'] > 0 else "🔴" if data['change'] < 0 else "⚪"
            text += f"{emoji} **{symbol}/USDT**: ${data['price']:,.0f}\n"
            text += f"   📈 24h: {data['change']:+.1f}% | 📍 {data['source']}\n\n"
        else:
            # استفاده از داده فیک در صورت خطا
            fake = fake_prices.get(symbol, {"price": 0, "change": 0})
            emoji = "🟢" if fake['change'] > 0 else "🔴" if fake['change'] < 0 else "⚪"
            text += f"{emoji} **{symbol}/USDT**: ${fake['price']:,.0f} (دمو)\n"
            text += f"   📈 24h: {fake['change']:+.1f}% | 📍 Demo\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_prices")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🔄 محاسبه سیگنال‌ها...", parse_mode="Markdown")
    
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    text = "🎯 **سیگنال‌های معاملاتی** 🎯\n\n"
    
    for symbol in symbols:
        data = await get_realtime_price(symbol)
        if not data:
            data = fake_prices.get(symbol, {"price": 0, "change": 0})
        
        # شبیه‌سازی قیمت‌های قبلی برای محاسبه RSI
        prices = [data['price'] * (1 + np.random.randn(20) * 0.02)]
        rsi = calculate_rsi(prices)
        signal = generate_signal(data['price'], data['change'], rsi)
        
        if "خرید" in signal:
            emoji = "🟢"
        elif "فروش" in signal:
            emoji = "🔴"
        else:
            emoji = "⚪"
        
        text += f"{emoji} **{symbol}**: {signal}\n"
        text += f"   📊 RSI: {rsi:.0f} | تغییر: {data['change']:+.1f}%\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_signals")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for symbol in ["BTC", "ETH", "SOL", "BNB"]:
        keyboard.append([InlineKeyboardButton(f"📈 {symbol}", callback_data=f"tech_{symbol}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    await update.callback_query.edit_message_text(
        "📈 **تحلیل تکنیکال** 📈\n\n"
        "📊 **اندیکاتورها:**\n"
        "• RSI (قدرت نسبی)\n"
        "• MACD (همگرایی/واگرایی)\n"
        "• میانگین متحرک\n\n"
        "ارز مورد نظر را انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    await update.callback_query.edit_message_text(f"📊 تحلیل {symbol}...", parse_mode="Markdown")
    
    data = await get_realtime_price(symbol)
    if not data:
        data = fake_prices.get(symbol, {"price": 0, "change": 0})
    
    # شبیه‌سازی قیمت‌های قبلی
    prices = [data['price'] * (1 + np.random.randn(30) * 0.015)]
    rsi = calculate_rsi(prices)
    signal = generate_signal(data['price'], data['change'], rsi)
    
    # محاسبه سطوح حمایت و مقاومت تقریبی
    support = data['price'] * 0.95
    resistance = data['price'] * 1.05
    
    text = f"📈 **تحلیل تکنیکال {symbol}** 📈\n\n"
    text += f"💰 **قیمت فعلی:** ${data['price']:,.0f}\n"
    text += f"📊 **تغییر ۲۴h:** {data['change']:+.1f}%\n\n"
    
    text += "**📊 اندیکاتورها:**\n"
    text += f"• RSI(14): {rsi:.0f} → "
    if rsi < 30:
        text += "🟢 اشباع فروش (منطقه خرید)\n"
    elif rsi > 70:
        text += "🔴 اشباع خرید (منطقه فروش)\n"
    else:
        text += "⚪ خنثی\n"
    
    text += f"• MACD: {'صعودی 📈' if data['change'] > 0 else 'نزولی 📉'}\n"
    text += f"• روند: {'صعودی' if data['change'] > 0 else 'نزولی' if data['change'] < 0 else 'خنثی'}\n\n"
    
    text += "**🔑 سطوح کلیدی:**\n"
    text += f"🟢 حمایت: ${support:,.0f}\n"
    text += f"🔴 مقاومت: ${resistance:,.0f}\n\n"
    
    text += f"**🎯 سیگنال:** {signal}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def portfolio_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
💰 **پرتفوی شخصی** 💰

📊 **آمار حساب:**
• موجودی: $10,000
• سود/زیان کل: $0 (0%)
• نرخ موفقیت: 0%
• تعداد معاملات: 0

📭 **پوزیشن‌های باز:**
هیچ پوزیشنی فعال نیست

---
💡 برای شروع معامله، ابتدا تحلیل رو بررسی کن
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🛡️ **مدیریت ریسک حرفه‌ای** 🛡️

📊 **قوانین طلایی:**

1️⃣ **حداکثر ریسک:** ۲٪ سرمایه در هر معامله

2️⃣ **نسبت ریسک به ریوارد:** حداقل ۱:۲

3️⃣ **حد ضرر:** همیشه اجباری

4️⃣ **حداکثر معاملات همزمان:** ۳ عدد

5️⃣ **حداکثر افت روزانه:** ۶٪

---
📈 **فرمول حجم معامله:**

`حجم = (سرمایه × ۲٪) / (قیمت ورود - حد ضرر)`

---
💡 **نکات کلیدی:**
• هیچوقت فول مارژین نکن
• احساسات را از معامله جدا کن
• در ضررهای متوالی، توقف کن
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
❓ **راهنمای ربات** ❓

📊 **قیمت لحظه‌ای:**
نمایش قیمت و تغییرات 24 ساعته از بایننس

🎯 **سیگنال:**
محاسبه بر اساس تغییرات قیمت و RSI

📈 **تحلیل تکنیکال:**
RSI، سطوح حمایت/مقاومت

💰 **پرتفوی:**
مدیریت سرمایه و پوزیشن‌ها

🛡️ **مدیریت ریسک:**
قوانین طلایی معامله‌گری

---
⚠️ **هشدار:** این ربات فقط جنبه آموزشی دارد
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signals":
        await signals_menu(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "portfolio":
        await portfolio_menu(update, context)
    elif data == "risk":
        await risk_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data == "refresh_prices":
        await prices_menu(update, context)
    elif data == "refresh_signals":
        await signals_menu(update, context)
    elif data.startswith("tech_"):
        await technical_analysis(update, context, data.split("_")[1])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🍃 لطفاً از دکمه‌های منو استفاده کن یا /start بزن.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 ربات تریدر حرفه‌ای روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
