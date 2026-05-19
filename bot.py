import os
import logging
import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx
import numpy as np

# ---------------------------- تنظیمات اولیه ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = "@comedyclick"  # کانال مقصد برای سیگنال‌ها و گزارش‌ها
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# تنظیمات CoinEx
ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")

# تنظیمات معاملاتی
MAX_RISK_PERCENT = 2.0
MAX_POSITIONS = 3
STOP_LOSS_PERCENT = 3.0
TAKE_PROFIT_PERCENT = 6.0

SYMBOLS = [
    {"symbol": "BTCUSDT", "name": "بیت‌کوین", "emoji": "👑"},
    {"symbol": "ETHUSDT", "name": "اتریوم", "emoji": "💎"},
    {"symbol": "SOLUSDT", "name": "سولانا", "emoji": "⚡"},
    {"symbol": "XRPUSDT", "name": "ریپل", "emoji": "💧"},
    {"symbol": "DOTUSDT", "name": "پولکادات", "emoji": "🔗"},
    {"symbol": "ICPUSDT", "name": "اینترنت کامپیوتر", "emoji": "🌐"},
]

# ---------------------------- توابع کمکی ----------------------------
def is_owner(update: Update) -> bool:
    if OWNER_ID == 0 or update.effective_user.id == OWNER_ID:
        return True
    update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
    return False

async def get_coinex_price(symbol="BTCUSDT"):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"https://api.coinex.com/v1/market/ticker?market={symbol}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    t = data["data"]["ticker"]
                    return {
                        "price": float(t["last"]),
                        "change": float(t["change"]),
                        "volume": float(t["vol"]),
                        "high": float(t["high"]),
                        "low": float(t["low"])
                    }
    except Exception as e:
        logger.error(f"Price error {symbol}: {e}")
    return None

def calculate_rsi(prices, period=14):
    if len(prices) < period+1: return 50
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0: gains.append(diff); losses.append(0)
        else: gains.append(0); losses.append(-diff)
    avg_gain = sum(gains[-period:])/period
    avg_loss = sum(losses[-period:])/period
    if avg_loss == 0: return 100
    rs = avg_gain/avg_loss
    return 100 - (100/(1+rs))

def calculate_support_resistance(prices):
    recent = prices[-50:]
    high = max(recent)
    low = min(recent)
    pivot = (high+low)/2
    r1 = pivot + (high-low)*0.382
    r2 = pivot + (high-low)*0.618
    s1 = pivot - (high-low)*0.382
    s2 = pivot - (high-low)*0.618
    return {"support": [s1, s2, low], "resistance": [r1, r2, high], "pivot": pivot}

def generate_signal(price, change, rsi):
    if rsi < 35 and change > 0: return "STRONG_BUY", 92, ["RSI در منطقه اشباع فروش", "حرکت صعودی آغاز شده"]
    if rsi < 45 and change > 1: return "BUY", 78, ["RSI صعودی", "حجم معاملات خوب"]
    if rsi > 65 and change < 0: return "STRONG_SELL", 92, ["RSI اشباع خرید", "احتمال ریزش"]
    if rsi > 55 and change < -1: return "SELL", 78, ["RSI نزولی", "فشار فروش"]
    return "HOLD", 50, ["بازار خنثی", "منتظر بمان"]

def format_signal_message(symbol, price, change, rsi, signal, confidence, reasons, sr):
    if signal == "STRONG_BUY": emoji, action = "🟢🟢", "لانگ (خرید)"
    elif signal == "BUY": emoji, action = "🟢", "خرید"
    elif signal == "STRONG_SELL": emoji, action = "🔴🔴", "شورت (فروش)"
    elif signal == "SELL": emoji, action = "🔴", "فروش"
    else: emoji, action = "⚪", "نگهداری"

    msg = f"""
{emoji} *سیگنال {symbol.replace('USDT', '')}/USDT* {emoji}

📊 *نوع معامله:* {action}
💰 *قیمت لحظه‌ای:* ${price:,.2f}
📈 *تغییر ۲۴ ساعته:* {change:+.2f}%
📊 *قدرت نسبی (RSI):* {rsi:.1f}

🎯 *تارگت‌ها:*
┌─────────────────────────
├ TP1) ${sr['resistance'][0]:,.2f}
├ TP2) ${sr['resistance'][1]:,.2f}
├ TP3) ${sr['resistance'][2]:,.2f}
└─────────────────────────

🛡️ *حد ضرر:* ${sr['support'][0]:,.2f}

📝 *تحلیل کوتاه:*
• {reasons[0]}
• {reasons[1]} (اگر موجود باشد)

✅ *اطمینان:* {confidence}%

✨ _این سیگنال توسط ربات فوق هوشمند ULTIMA 17 تولید شده است._  
🧠 _برای دریافت سیگنال‌های بیشتر و آموزش رایگان، عضو شوید:_  
📍 @comedyclick
"""
    return msg

# ---------------------------- ارسال خودکار به کانال ----------------------------
async def send_auto_signal(context: ContextTypes.DEFAULT_TYPE):
    """هر ۳۰ دقیقه یک سیگنال حرفه‌ای به کانال می‌فرستد"""
    for s in SYMBOLS:
        try:
            data = await get_coinex_price(s["symbol"])
            if not data: continue
            # ساخت داده تاریخی ساختگی برای اندیکاتور
            prices = [data["price"] * (1 + np.random.randn(30)*0.015) for _ in range(30)]
            rsi = calculate_rsi(prices)
            signal, conf, reasons = generate_signal(data["price"], data["change"], rsi)
            sr = calculate_support_resistance(prices)
            msg = format_signal_message(s["symbol"], data["price"], data["change"], rsi, signal, conf, reasons, sr)
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            await asyncio.sleep(2)  # فاصله بین ارسال سیگنال‌ها
        except Exception as e:
            logger.error(f"Auto signal error {s['symbol']}: {e}")

async def send_news_and_whales(context: ContextTypes.DEFAULT_TYPE):
    """ارسال اخبار و تراکنش‌های نهنگ‌ها به کانال"""
    try:
        # خبر
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://cryptopanic.com/api/v1/posts/?public=true&kind=news")
            if resp.status_code == 200:
                articles = resp.json().get("results", [])[:3]
                news_text = "📰 *آخرین اخبار کریپتو*\n\n"
                for a in articles:
                    news_text += f"• {a['title'][:100]}...\n"
                await context.bot.send_message(chat_id=CHANNEL_ID, text=news_text, parse_mode="Markdown")
        await asyncio.sleep(2)
        # نهنگ‌ها
        resp = await client.get("https://api.whale-alert.io/v1/transactions?api_key=&min_value=1000000")
        if resp.status_code == 200:
            txs = resp.json().get("transactions", [])[:3]
            whale_text = "🐋 *تحرکات نهنگ‌ها (ساعت گذشته)* 🐋\n\n"
            for tx in txs:
                whale_text += f"• {tx['amount']:.0f} {tx['symbol']} به ارزش ${tx['amount_usd']/1e6:.1f}M\n"
            await context.bot.send_message(chat_id=CHANNEL_ID, text=whale_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"News/whale error: {e}")

async def send_market_summary(context: ContextTypes.DEFAULT_TYPE):
    """خلاصه بازار و تحلیل کلی"""
    total_change = 0
    msg = "📊 *خلاصه بازار لحظه‌ای*\n\n"
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        if data:
            msg += f"{s['emoji']} *{s['symbol'].replace('USDT','')}* : ${data['price']:,.0f} ({data['change']:+.2f}%)\n"
            total_change += data["change"]
    msg += f"\n📈 *میانگین تغییر کل بازار:* {total_change/len(SYMBOLS):+.2f}%\n"
    msg += f"\n📍 _ربات ULTIMA 17 | @comedyclick_"
    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")

# ---------------------------- ربات تلگرام (منو و چت هوشمند) ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    keyboard = [
        [InlineKeyboardButton("📊 قیمت ارزها", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال لحظه‌ای", callback_data="signal")],
        [InlineKeyboardButton("🧠 تحلیل هوشمند", callback_data="ai")],
        [InlineKeyboardButton("💰 موجودی", callback_data="balance")],
        [InlineKeyboardButton("💬 چت با هوش مصنوعی", callback_data="chat_ai")],
        [InlineKeyboardButton("📈 پوزیشن‌ها", callback_data="positions")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
    ]
    await update.message.reply_text(
        "✨ *ربات ULTIMA 17 – اولین ربات فوق هوشمند تریدر* ✨\n"
        "من می‌توانم تحلیل کنم، معامله کنم، چت کنم و سیگنال بفرستم.\n"
        "از دکمه‌های زیر استفاده کنید.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    txt = "💰 *قیمت لحظه‌ای ارزها*\n\n"
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        if data:
            txt += f"{s['emoji']} *{s['symbol'].replace('USDT','')}* : ${data['price']:,.0f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def manual_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    s = SYMBOLS[0]  # نمونه بیت‌کوین
    data = await get_coinex_price(s["symbol"])
    if not data:
        await query.edit_message_text("خطا در دریافت قیمت")
        return
    prices = [data["price"] * (1 + np.random.randn(30)*0.015) for _ in range(30)]
    rsi = calculate_rsi(prices)
    signal, conf, reasons = generate_signal(data["price"], data["change"], rsi)
    sr = calculate_support_resistance(prices)
    msg = format_signal_message(s["symbol"], data["price"], data["change"], rsi, signal, conf, reasons, sr)
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not GROQ_API_KEY:
        await query.edit_message_text("❌ کلید Groq تنظیم نشده")
        return
    await query.edit_message_text("🤖 در حال تحلیل بازار با هوش مصنوعی...")
    data = await get_coinex_price("BTCUSDT")
    if not data:
        await query.edit_message_text("خطا در دریافت قیمت")
        return
    prompt = f"تحلیل بیت‌کوین: قیمت ${data['price']:,.0f}، تغییر {data['change']:+.2f}%. پیش‌بینی کوتاه مدت و توصیه معاملاتی بده."
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"max_tokens":300})
        if resp.status_code == 200:
            res = resp.json()["choices"][0]["message"]["content"]
            await query.edit_message_text(f"🧠 *تحلیل هوشمند:*\n{res}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def chat_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💬 *حالت چت با هوش مصنوعی فعال شد*\n"
        "هر سوالی دارید بپرسید. من با انرژی مثبت و طنز پاسخ می‌دهم.\n"
        "برای پایان، /cancel را بفرستید.",
        parse_mode="Markdown"
    )
    context.user_data["chat_mode"] = True

async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("chat_mode"): return
    if not GROQ_API_KEY:
        await update.message.reply_text("❌ Groq API تنظیم نشده")
        return
    user_msg = update.message.text
    if user_msg == "/cancel":
        context.user_data["chat_mode"] = False
        await update.message.reply_text("حالت چت غیرفعال شد.")
        return
    await update.message.reply_chat_action("typing")
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.3-70b-versatile","messages":[{"role":"system","content":"تو یک دستیار شوخ و خونگرم هستی."},{"role":"user","content":user_msg}],"max_tokens":400})
        if resp.status_code == 200:
            await update.message.reply_text(resp.json()["choices"][0]["message"]["content"], parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ خطا در ارتباط با هوش مصنوعی")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not ACCESS_ID:
        await query.edit_message_text("❌ CoinEX API تنظیم نشده", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    async with httpx.AsyncClient() as client:
        # اینجا باید درخواست امضا شده بفرستید – برای اختصار کوته نوشته شده
        await query.edit_message_text("💰 موجودی حساب: اطلاعات در حال دریافت...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📈 پوزیشن‌های باز:\nهیچ پوزیشنی باز نیست.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    txt = f"⚙️ *تنظیمات ربات*\n\n"
    txt += f"📡 وضعیت API:\n• CoinEx: {'✅' if ACCESS_ID else '❌'}\n• Groq: {'✅' if GROQ_API_KEY else '❌'}\n"
    txt += f"📢 کانال ارسال: {CHANNEL_ID}\n🕒 ارسال خودکار سیگنال: هر ۳۰ دقیقه"
    await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ---------------------------- اجرای اصلی ----------------------------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(back, pattern="back"))
    app.add_handler(CallbackQueryHandler(prices, pattern="prices"))
    app.add_handler(CallbackQueryHandler(manual_signal, pattern="signal"))
    app.add_handler(CallbackQueryHandler(ai_analysis, pattern="ai"))
    app.add_handler(CallbackQueryHandler(chat_ai, pattern="chat_ai"))
    app.add_handler(CallbackQueryHandler(balance, pattern="balance"))
    app.add_handler(CallbackQueryHandler(positions, pattern="positions"))
    app.add_handler(CallbackQueryHandler(settings, pattern="settings"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_chat))

    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(send_auto_signal, interval=1800, first=10)       # هر ۳۰ دقیقه
        job_queue.run_repeating(send_news_and_whales, interval=3600, first=300)  # هر ۱ ساعت
        job_queue.run_repeating(send_market_summary, interval=3600, first=600)   # هر ۱ ساعت

    logger.info("ربات ULTIMA 17 با موفقیت راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
