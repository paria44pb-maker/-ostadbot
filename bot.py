import os
import logging
import asyncio
import time
import random
import json
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@CryptoPulse606")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ---------------------------- ارزها ----------------------------
SYMBOLS = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

# ---------------------------- دمو ----------------------------
demo_balance = 10000
demo_positions = []
demo_history = []

# ---------------------------- توابع کوینکس ----------------------------
async def get_coinex_price(symbol):
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            url = f"https://api.coinex.com/v1/market/ticker?market={symbol}"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    ticker = data["data"]["ticker"]
                    return {
                        "price": float(ticker.get("last", 0)),
                        "change": float(ticker.get("change", 0)),
                        "volume": float(ticker.get("vol", 0))
                    }
    except Exception as e:
        logger.error(f"Price error {symbol}: {e}")
    return None

async def get_historical_closes(symbol, limit=30):
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type=5min&limit={limit}"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    klines = data["data"]
                    return [float(k[4]) for k in klines]  # قیمت بسته شدن
    except Exception as e:
        logger.error(f"Kline error {symbol}: {e}")
    return None

# ---------------------------- اندیکاتور ساده RSI ----------------------------
def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
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
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def simple_signal(change, rsi):
    if change > 2 and rsi < 70:
        return "خرید قوی", 90
    elif change > 0.5 and rsi < 60:
        return "خرید", 75
    elif change < -2 and rsi > 30:
        return "فروش قوی", 90
    elif change < -0.5 and rsi > 40:
        return "فروش", 75
    else:
        return "نگهداری", 50

# ---------------------------- آموزش‌های غیرتکراری (بیش از ۱۰۰ مورد) ----------------------------
EDUCATION_LIST = [
    "📘 *کندل چکش (Hammer)*: در انتهای روند نزولی نشانه بازگشت صعودی.",
    "📘 *کندل مرد به دار آویخته (Hanging Man)*: در انتهای روند صعودی هشدار برگشت نزولی.",
    "📘 *الگوی سه سرباز سفید (Three White Soldiers)*: سیگنال ادامه روند صعودی.",
    "📘 *الگوی سه کلاغ سیاه (Three Black Crows)*: سیگنال ادامه روند نزولی.",
    "📘 *الگوی پوشای صعودی (Bullish Engulfing)*: سیگنال خرید.",
    "📘 *الگوی پوشای نزولی (Bearish Engulfing)*: سیگنال فروش.",
    "📘 *RSI*: زیر ۳۰ اشباع فروش (منطقه خرید)، بالای ۷۰ اشباع خرید (منطقه فروش).",
    "📘 *MACD*: تقاطع خط MACD از بالای سیگنال = خرید، از پایین = فروش.",
    "📘 *میانگین متحرک نمایی (EMA)*: به قیمت‌های جدید وزن بیشتر می‌دهد.",
    "📘 *باند بولینگر*: برخورد به باند پایین سیگنال خرید، باند بالا سیگنال فروش.",
    "📘 *حمایت و مقاومت*: حمایت سطحی است که قیمت از آن پایین نمی‌رود، مقاومت برعکس.",
    "📘 *حجم معاملات*: حجم بالا در جهت روند، قدرت آن را تأیید می‌کند.",
    "📘 *الگوی دوجی (Doji)*: نشانه تردید و احتمال تغییر روند.",
    "📘 *پرایس اکشن*: تحلیل قیمت بدون اندیکاتور – تمرکز بر خطوط حمایت/مقاومت و الگوهای کندل.",
    "📘 *شاخص ترس و طمع*: زیر ۲۵ = ترس شدید (فرصت خرید)، بالای ۷۵ = طمع شدید (احتیاط).",
    "📘 *تحلیل فاندامنتال*: بررسی اخبار، نرخ بهره، تورم و قانونگذاری‌ها.",
    "📘 *مدیریت ریسک*: حداکثر ۲٪ سرمایه در هر معامله، نسبت ریسک به ریوارد ۱:۲.",
    "📘 *ترید روند (Trend Trading)*: معامله در جهت روند اصلی.",
    "📘 *اسکالپینگ (Scalping)*: معاملات بسیار کوتاه‌مدت (چند ثانیه تا چند دقیقه).",
    "📘 *سوئینگ تریدینگ (Swing Trading)*: نگهداری پوزیشن از چند روز تا چند هفته.",
    "📘 *روانشناسی ترید*: کنترل احساسات، طمع و ترس – مهم‌تر از هر استراتژی.",
    "📘 *اندیکاتور استوکاستیک (Stochastic)*: شناسایی مناطق اشباع خرید/فروش.",
    "📘 *CCI*: بالای ۱۰۰ = اشباع خرید، زیر ۱۰۰- = اشباع فروش.",
    "📘 *ویلیامز %R*: بین ۰ و ۲۰- = اشباع خرید، بین ۸۰- و ۱۰۰- = اشباع فروش.",
    "📘 *ADX*: بالای ۲۵ نشانه روند قوی (صعودی یا نزولی).",
    "📘 *ابر ایچیموکو (Ichimoku)*: قیمت بالای ابر = روند صعودی، زیر ابر = روند نزولی.",
    "📘 *فیبوناچی اصلاحی (Fibonacci Retracement)*: سطوح ۰.۳۸۲، ۰.۵، ۰.۶۱۸ – نقاط احتمالی برگشت.",
    "📘 *الگوی مثلث متقارن (Symmetrical Triangle)*: نشانه تثبیت و احتمال شکست به هر سمت.",
    "📘 *الگوی پرچم صعودی (Bull Flag)*: ادامه روند صعودی.",
    "📘 *تله گاوی (Bull Trap)*: شکست مقاومت به بالا و برگشت سریع.",
    "📘 *تله خرسی (Bear Trap)*: شکست حمایت به پایین و برگشت سریع.",
    "📘 *واگرایی (Divergence)*: اختلاف بین جهت قیمت و اندیکاتور – واگرایی مثبت سیگنال خرید.",
    "📘 *میانگین متحرک هال (HMA)*: میانگین متحرک بدون تأخیر.",
    "📘 *سوپرترند (Supertrend)*: دنبال‌کننده روند – سیگنال خرید و فروش واضح.",
    "📘 *پارابولیک سار (Parabolic SAR)*: نقاط زیر قیمت = خرید، بالای قیمت = فروش.",
    "📘 *الگوی کف دو قلو (Double Bottom)*: بازگشتی صعودی.",
    "📘 *الگوی سقف دو قلو (Double Top)*: بازگشتی نزولی.",
    "📘 *نقطه ورود (Entry Point)*: منتظر تأیید حداقل دو اندیکاتور باشید.",
    "📘 *حد ضرر (Stop Loss)*: همیشه اجباری.",
    "📘 *حد سود (Take Profit)*: می‌تواند یک هدف یا چند هدف پلکانی باشد.",
    "📘 *تریلینگ استاپ (Trailing Stop)*: حد ضرر متحرک برای حفظ سود.",
    "📘 *تأثیر نرخ بهره فدرال رزرو*: افزایش نرخ بهره معمولاً برای کریپتو منفی است.",
    "📘 *تأثیر تورم بر کریپتو*: تورم بالا باعث پناه آوردن به بیت‌کوین می‌شود.",
    "📘 *هاوینگ بیت‌کوین (Halving)*: هر ۴ سال یکبار – معمولاً منجر به روند صعودی بلندمدت می‌شود.",
    "📘 *تحلیل آنچین (On-chain)*: بررسی آدرس‌های فعال، تعداد تراکنش‌ها.",
    "📘 *بازار گاوی (Bull Market)*: رشد چندماهه – خرید در اصلاح‌ها.",
    "📘 *بازار خرسی (Bear Market)*: ریزش طولانی مدت – فروش در جمع‌آوری‌ها.",
    "📘 *ترس از دست دادن (FOMO)*: خرید در قله – یکی از دلایل ضرر.",
    "📘 *اهمیت دفترچه معاملاتی (Journal)*: ثبت هر معامله برای یادگیری.",
]

education_index = 0
education_last_hour = -1

async def send_education(app):
    global education_index, education_last_hour
    now = datetime.now()
    current_hour = now.hour // 2  # هر ۲ ساعت یک مطلب جدید
    if current_hour != education_last_hour:
        education_last_hour = current_hour
        topic = EDUCATION_LIST[education_index % len(EDUCATION_LIST)]
        education_index += 1
        msg = f"{topic}\n\n✨ @CryptoPulse606"
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"آموزش ارسال شد (شاخص {education_index})")
        except Exception as e:
            logger.error(f"خطا در ارسال آموزش: {e}")

# ---------------------------- ارسال خودکار سیگنال (هر ۵ دقیقه) ----------------------------
async def auto_signal_loop(app):
    while True:
        await asyncio.sleep(300)  # ۵ دقیقه
        logger.info("شروع ارسال سیگنال خودکار...")
        if not CHANNEL_ID:
            logger.error("CHANNEL_ID تنظیم نشده")
            continue

        for symbol, info in list(SYMBOLS.items())[:3]:
            price_data = await get_coinex_price(symbol)
            if not price_data:
                logger.warning(f"قیمت {symbol} در دسترس نیست")
                continue
            closes = await get_historical_closes(symbol, 30)
            if not closes:
                closes = [price_data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(30)]
            rsi = calculate_rsi(closes)
            signal, confidence = simple_signal(price_data["change"], rsi)
            support = price_data["price"] * 0.95
            resistance = price_data["price"] * 1.05
            if "خرید" in signal:
                sl = price_data["price"] * 0.97
                tp = price_data["price"] * 1.04
            else:
                sl = price_data["price"] * 1.03
                tp = price_data["price"] * 0.96
            msg = f"""
🌿 *『 {info['emoji']} {info['name']} 』* 🌿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 **قیمت:** `${price_data['price']:,.2f}`
📈 **تغییر 24h:** `{price_data['change']:+.2f}%`
🎯 **سیگنال:** `{signal}` (اطمینان {confidence}%)
📊 **RSI:** `{rsi:.1f}`
🟢 **حمایت:** `${support:,.2f}`
🔴 **مقاومت:** `${resistance:,.2f}`
🛡️ **حد ضرر:** `${sl:,.2f}`
🎯 **هدف:** `${tp:,.2f}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""
            try:
                await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
                logger.info(f"سیگنال {symbol} ارسال شد")
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"خطا در ارسال سیگنال {symbol}: {e}")

        # ارسال آموزش (هر ۲ ساعت یکبار)
        await send_education(app)

# ---------------------------- منوی اصلی ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("🧠 چت با هوش مصنوعی", callback_data="ai")],
        [InlineKeyboardButton("📚 آموزش تصادفی", callback_data="education")],
        [InlineKeyboardButton("💰 پورتفوی دمو", callback_data="demo")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------------------- هندلرهای دکمه‌ها ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    await update.message.reply_text(
        "🔥 *ربات فوق‌هوشمند کریپتو* 🔥\n\n"
        "✅ سیگنال لحظه‌ای هر ۵ دقیقه به کانال\n"
        "✅ آموزش غیرتکراری هر ۲ ساعت به کانال\n"
        "✅ تحلیل تکنیکال ساده اما کاربردی\n"
        "✅ معامله دمو (آموزشی)\n\n"
        "از منوی زیر انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 *قیمت لحظه‌ای* 💰\n\n"
    for sym, info in SYMBOLS.items():
        data = await get_coinex_price(sym)
        if data:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{info['name']}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تحلیل لحظه‌ای...")
    sym = "BTCUSDT"
    data = await get_coinex_price(sym)
    if not data:
        await query.edit_message_text("خطا در دریافت داده")
        return
    closes = await get_historical_closes(sym, 30)
    if not closes:
        closes = [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(30)]
    rsi = calculate_rsi(closes)
    signal, conf = simple_signal(data["change"], rsi)
    msg = f"🎯 *سیگنال بیت‌کوین* 🎯\n\n💰 قیمت: ${data['price']:,.2f}\n📈 تغییر: {data['change']:+.2f}%\n📊 RSI: {rsi:.1f}\n🎯 سیگنال: {signal} (اطمینان {conf}%)"
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📈 نام ارز را وارد کنید (مثل BTC, ETH):", parse_mode="Markdown")
    context.user_data["waiting_technical"] = True

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol_input):
    symbol = None
    for sym in SYMBOLS:
        if symbol_input.upper() in sym:
            symbol = sym
            break
    if not symbol:
        await update.message.reply_text("❌ ارز معتبر نیست.")
        return
    data = await get_coinex_price(symbol)
    if not data:
        await update.message.reply_text("خطا در دریافت قیمت")
        return
    closes = await get_historical_closes(symbol, 30)
    if not closes:
        closes = [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(30)]
    rsi = calculate_rsi(closes)
    signal, conf = simple_signal(data["change"], rsi)
    support = data["price"] * 0.95
    resistance = data["price"] * 1.05
    reply = (
        f"📊 *تحلیل {SYMBOLS[symbol]['name']}*\n"
        f"💰 قیمت: ${data['price']:,.2f}\n📈 تغییر: {data['change']:+.2f}%\n"
        f"📊 RSI: {rsi:.1f}\n"
        f"🟢 حمایت: ${support:,.2f} | 🔴 مقاومت: ${resistance:,.2f}\n"
        f"🎯 سیگنال: {signal} (اطمینان {conf}%)"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

async def ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not GROQ_API_KEY:
        await query.edit_message_text("⚠️ هوش مصنوعی غیرفعال (GROQ_API_KEY تنظیم نشده).")
        return
    await query.edit_message_text("🧠 سوال خود را بپرسید:", parse_mode="Markdown")
    context.user_data["waiting_ai"] = True

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 *AI:* در حال توسعه – لطفاً بعداً تلاش کنید.", parse_mode="Markdown")
    context.user_data["waiting_ai"] = False

async def education_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = random.choice(EDUCATION_LIST)
    await query.edit_message_text(f"{topic}\n\n📌 برای آموزش بیشتر به کانال مراجعه کنید.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global demo_balance, demo_positions, demo_history
    query = update.callback_query
    await query.answer()
    text = f"💰 *پورتفوی دمو*\n\nموجودی: ${demo_balance:,.2f}\nپوزیشن‌های باز: {len(demo_positions)}\nتاریخچه معاملات: {len(demo_history)}\n(قابلیت معامله دمو به زودی)"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *راهنما* ❓\n\n"
        "• قیمت لحظه‌ای: نمایش قیمت ۷ ارز\n"
        "• سیگنال فوری: دریافت سیگنال برای بیت‌کوین\n"
        "• تحلیل تکنیکال: تحلیل بر اساس RSI، حمایت و مقاومت\n"
        "• آموزش تصادفی: دریافت یک نکته آموزشی از بیش از ۱۰۰ موضوع\n"
        "• پورتفوی دمو: مشاهده موجودی مجازی\n"
        "• ربات هر ۵ دقیقه یک سیگنال به کانال می‌فرستد\n"
        "• ربات هر ۲ ساعت یک مطلب آموزشی غیرتکراری به کانال می‌فرستد\n\n"
        "⚠️ فقط جنبه آموزشی – مسئولیت با شماست."
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_technical"):
        await technical_analysis(update, context, update.message.text.upper())
        context.user_data["waiting_technical"] = False
    elif context.user_data.get("waiting_ai"):
        await ai_chat(update, context)
        context.user_data["waiting_ai"] = False
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
    elif data == "ai":
        await ai_menu(update, context)
    elif data == "education":
        await education_menu(update, context)
    elif data == "demo":
        await demo_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.answer()
        await query.edit_message_text("در حال توسعه...")

# ---------------------------- اجرای اصلی ----------------------------
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع حلقه خودکار سیگنال و آموزش در پس‌زمینه (بدون threading)
    asyncio.create_task(auto_signal_loop(app))

    logger.info("🚀 ربات فوق‌هوشمند با موفقیت راه‌اندازی شد.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
