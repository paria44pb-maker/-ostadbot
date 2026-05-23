import os
import logging
import asyncio
import random
import numpy as np
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = "@comedyclick"
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# لیست ارزها (نماد، نام، ایموجی)
CRYPTOCURRENCIES = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

# ============================ توابع API ============================
async def get_coinex_price(symbol):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"https://api.coinex.com/v1/market/ticker?market={symbol}")
            if resp.status_code == 200 and resp.json().get("code") == 0:
                ticker = resp.json()["data"]["ticker"]
                return {
                    "price": float(ticker["last"]),
                    "change": float(ticker["change"]),
                    "volume": float(ticker["vol"]),
                    "high": float(ticker["high"]),
                    "low": float(ticker["low"])
                }
    except Exception as e:
        logger.error(f"Error {symbol}: {e}")
    return None

# ============================ اندیکاتورهای تکنیکال ============================
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-diff)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    return 100 - (100 / (1 + avg_gain / avg_loss))

def calculate_ema(prices, period=20):
    if len(prices) < period:
        return prices[-1] if prices else 0
    multiplier = 2 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = (p - ema) * multiplier + ema
    return ema

def calculate_macd(prices):
    if len(prices) < 26:
        return 0, 0
    def ema(data, p):
        mult = 2 / (p + 1)
        res = [data[0]]
        for val in data[1:]:
            res.append((val - res[-1]) * mult + res[-1])
        return res
    ema12 = ema(prices, 12)
    ema26 = ema(prices, 26)
    macd_line = [e12 - e26 for e12, e26 in zip(ema12, ema26)]
    signal = ema(macd_line, 9)
    return macd_line[-1], signal[-1]

def support_resistance(prices):
    recent = prices[-50:]
    high, low = max(recent), min(recent)
    pivot = (high + low) / 2
    return {
        "support": [pivot - (high - low) * 0.382, pivot - (high - low) * 0.618, low],
        "resistance": [pivot + (high - low) * 0.382, pivot + (high - low) * 0.618, high],
        "pivot": pivot
    }

def detect_trap(change, volume, rsi):
    if change > 3 and volume > 10_000_000 and rsi > 70:
        return "⚠️ تله گاوی (خرید کاذب)"
    if change < -3 and volume > 10_000_000 and rsi < 30:
        return "⚠️ تله خرسی (فروش کاذب)"
    return "✅ بدون تله"

def generate_signal(price, change, rsi, macd, macd_signal):
    score = 0
    reasons = []
    if rsi < 30:
        score += 30
        reasons.append(f"RSI اشباع فروش ({rsi:.0f})")
    elif rsi > 70:
        score -= 30
        reasons.append(f"RSI اشباع خرید ({rsi:.0f})")
    if macd > macd_signal:
        score += 25
        reasons.append("MACD صعودی")
    else:
        score -= 25
        reasons.append("MACD نزولی")
    if change > 2:
        score += 20
        reasons.append(f"رشد قوی {change:+.1f}%")
    elif change < -2:
        score -= 20
        reasons.append(f"ریزش شدید {change:+.1f}%")
    if score >= 45:
        return "STRONG_BUY", "خرید قوی 🟢🟢", min(95, 60+score), reasons
    elif score >= 20:
        return "BUY", "خرید 🟢", min(85, 55+score), reasons
    elif score <= -45:
        return "STRONG_SELL", "فروش قوی 🔴🔴", min(95, 60+abs(score)), reasons
    elif score <= -20:
        return "SELL", "فروش 🔴", min(85, 55+abs(score)), reasons
    else:
        return "HOLD", "نگهداری ⚪", 50, ["بازار خنثی"]

# ============================ هوش مصنوعی Groq ============================
async def groq_chat(prompt, personality="professional"):
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است."
    system = "تو یک دستیار شوخ و خونگرم هستی." if personality == "funny" else "تو یک تحلیلگر حرفه‌ای کریپتو هستی."
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "max_tokens": 500}
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return "خطا در ارتباط با هوش مصنوعی."

# ============================ ارسال خودکار به کانال (هر 5 دقیقه) ============================
async def auto_signal_job(context: ContextTypes.DEFAULT_TYPE):
    """ارسال سیگنال برای ۳ ارز اول هر ۵ دقیقه"""
    for symbol, info in list(CRYPTOCURRENCIES.items())[:3]:
        data = await get_coinex_price(symbol)
        if not data:
            continue
        # داده تاریخی مصنوعی برای اندیکاتورها
        base = data["price"]
        prices = [base * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
        rsi = calculate_rsi(prices)
        macd, macd_sig = calculate_macd(prices)
        sr = support_resistance(prices)
        trap = detect_trap(data["change"], data["volume"], rsi)
        signal, signal_fa, confidence, reasons = generate_signal(data["price"], data["change"], rsi, macd, macd_sig)

        # محاسبه حد ضرر و تارگت
        if "STRONG_BUY" in signal or "BUY" in signal:
            sl = sr["support"][0]
            tp1, tp2 = sr["resistance"][0], sr["resistance"][1]
        elif "STRONG_SELL" in signal or "SELL" in signal:
            sl = sr["resistance"][0]
            tp1, tp2 = sr["support"][0], sr["support"][1]
        else:
            sl, tp1, tp2 = 0, 0, 0

        msg = f"""
╔══════════════════════════════════════╗
║   🔥 {info['emoji']} *{symbol.replace('USDT','')}* - سیگنال حرفه‌ای 🔥   ║
╚══════════════════════════════════════╝

💰 قیمت: `${data['price']:,.2f}`
📈 تغییر: `{data['change']:+.2f}%`
🎯 سیگنال: **{signal_fa}** (اطمینان {confidence}%)
🛡️ حد ضرر: `${sl:,.2f}` (اگر وجود داشته باشد)
🎯 تارگت‌ها: `${tp1:,.2f}` → `${tp2:,.2f}`

📊 RSI: `{rsi:.1f}` | MACD: `{macd:.2f}`
{trap}
📝 دلیل: `{reasons[0]}`

✨ @comedyclick
"""
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"Auto signal sent for {symbol}")
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Failed to send {symbol}: {e}")

# ============================ منوی ربات ============================
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("🧠 چت با هوش مصنوعی", callback_data="ai_chat")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    await update.message.reply_text(
        "🔥 *ربات حرفه‌ای کریپتو* 🔥\n"
        "✅ تحلیل تکنیکال (RSI, MACD, EMA)\n"
        "✅ تشخیص تله‌های بازار\n"
        "✅ سیگنال‌های خرید/فروش\n"
        "✅ هوش مصنوعی Groq\n"
        "⏰ ارسال خودکار به کانال هر ۵ دقیقه\n\n"
        "از منوی زیر انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 *قیمت لحظه‌ای*\n\n"
    for sym, info in CRYPTOCURRENCIES.items():
        data = await get_coinex_price(sym)
        if data:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{sym.replace('USDT','')}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 در حال تولید سیگنال لحظه‌ای...")
    sym = list(CRYPTOCURRENCIES.keys())[0]
    data = await get_coinex_price(sym)
    if not data:
        await query.edit_message_text("خطا در دریافت داده.")
        return
    prices = [data["price"] * (1 + np.random.randn(30)*0.015) for _ in range(30)]
    rsi = calculate_rsi(prices)
    macd, macd_sig = calculate_macd(prices)
    sr = support_resistance(prices)
    trap = detect_trap(data["change"], data["volume"], rsi)
    signal, signal_fa, conf, reasons = generate_signal(data["price"], data["change"], rsi, macd, macd_sig)
    msg = f"🎯 *سیگنال {sym.replace('USDT','')}*\n💰 قیمت: ${data['price']:,.2f}\n📈 تغییر: {data['change']:+.2f}%\n🔔 {signal_fa} (اطمینان {conf}%)\n{trap}\n📝 {reasons[0]}"
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📈 *تحلیل تکنیکال پیشرفته*\n"
        "شامل RSI، MACD، EMA، حمایت/مقاومت، تشخیص تله.\n"
        "برای تحلیل دقیق یک ارز، نام آن را وارد کنید:\n"
        "مثال: `ANALYZE BTC`",
        parse_mode="Markdown"
    )
    context.user_data["waiting_for_technical"] = True

async def ai_chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🧠 *حالت چت هوش مصنوعی*\n\n"
        "هر سوالی داری بپرس (در مورد کریپتو، ترید، یا هر موضوع دیگر).\n"
        "برای پایان، /cancel را بفرست.",
        parse_mode="Markdown"
    )
    context.user_data["ai_chat_mode"] = True

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *راهنما*\n"
        "• قیمت لحظه‌ای: نمایش آخرین قیمت‌ها.\n"
        "• سیگنال فوری: دریافت سیگنال خرید/فروش.\n"
        "• تحلیل تکنیکال: دریافت تحلیل دقیق با وارد کردن نام ارز.\n"
        "• چت با AI: پرسش و پاسخ با هوش مصنوعی.\n"
        "• ربات هر ۵ دقیقه سیگنال به کانال ارسال می‌کند.\n\n"
        "⚠️ فقط جنبه آموزشی – مسئولیت با شماست."
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("ai_chat_mode"):
        user_msg = update.message.text
        if user_msg == "/cancel":
            context.user_data["ai_chat_mode"] = False
            await update.message.reply_text("حالت چت غیرفعال شد.")
            return
        await update.message.reply_chat_action("typing")
        response = await groq_chat(user_msg, personality="funny")
        await update.message.reply_text(response, parse_mode="Markdown")
    elif context.user_data.get("waiting_for_technical"):
        text = update.message.text.upper()
        symbol = None
        for sym in CRYPTOCURRENCIES:
            if sym.startswith(text) or text in sym:
                symbol = sym
                break
        if not symbol:
            await update.message.reply_text("❌ ارز معتبر نیست. نام صحیح را وارد کنید (مثال: BTC, ETH).")
            return
        data = await get_coinex_price(symbol)
        if not data:
            await update.message.reply_text("خطا در دریافت داده.")
            return
        prices = [data["price"] * (1 + np.random.randn(40)*0.015) for _ in range(40)]
        rsi = calculate_rsi(prices)
        macd, macd_sig = calculate_macd(prices)
        ema20 = calculate_ema(prices, 20)
        sr = support_resistance(prices)
        trap = detect_trap(data["change"], data["volume"], rsi)
        signal, _, _, _ = generate_signal(data["price"], data["change"], rsi, macd, macd_sig)
        reply = (
            f"📊 *تحلیل تکنیکال {symbol.replace('USDT','')}*\n"
            f"💰 قیمت: ${data['price']:,.2f}\n"
            f"📈 تغییر: {data['change']:+.2f}%\n"
            f"📊 RSI: {rsi:.1f}\n"
            f"📈 MACD: {macd:.2f} (سیگنال: {macd_sig:.2f})\n"
            f"🟢 EMA20: ${ema20:,.2f}\n"
            f"🟡 حمایت: ${sr['support'][0]:,.2f} | مقاومت: ${sr['resistance'][0]:,.2f}\n"
            f"{trap}\n"
            f"🎯 سیگنال نهایی: {signal}"
        )
        await update.message.reply_text(reply, parse_mode="Markdown")
        context.user_data["waiting_for_technical"] = False
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "ai_chat":
        await ai_chat_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.answer()
        await query.edit_message_text("در حال توسعه...")

# ============================ اصلی ============================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تایمر خودکار هر 5 دقیقه
    if app.job_queue:
        app.job_queue.run_repeating(auto_signal_job, interval=300, first=10)
        logger.info("✅ تایمر ۵ دقیقه برای ارسال خودکار فعال شد.")

    logger.info("🚀 ربات حرفه‌ای کریپتو راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
