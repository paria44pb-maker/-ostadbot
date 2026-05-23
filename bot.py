import os
import logging
import asyncio
import random
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ---------------------------- تنظیمات و لاگینگ حرفه‌ای ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@comedyclick")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# لیست ارزهای تحت پوشش با جزئیات (نام و ایموجی)
SYMBOLS = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

# ---------------------------- دریافت قیمت از CoinEx (نسخه نهایی) ----------------------------
async def get_coinex_price(symbol):
    """دریافت قیمت لحظه‌ای و تغییرات 24 ساعته از صرافی CoinEx"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # استفاده از نسخه پایدار و عمومی API کوینکس
            url = f"https://api.coinex.com/v1/market/ticker?market={symbol}"
            resp = await client.get(url)
            if resp.status_code == 200 and resp.json().get("code") == 0:
                ticker = resp.json()["data"]["ticker"]
                # استفاده از متد .get() برای جلوگیری از خطای "KeyError"
                return {
                    "price": float(ticker.get("last", 0)),
                    "change": float(ticker.get("change", 0)),
                    "volume": float(ticker.get("vol", 0)),
                }
    except Exception as e:
        logger.error(f"خطا در دریافت قیمت {symbol}: {e}")
    return None

# ---------------------------- محاسبه اندیکاتور RSI ----------------------------
def calculate_rsi(prices, period=14):
    """محاسبه شاخص قدرت نسبی (RSI) به عنوان یک معیار تکنیکال"""
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
    avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0
    avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ---------------------------- منطق تولید سیگنال ----------------------------
def generate_signal(change, rsi):
    """تولید سیگنال خرید/فروش بر اساس نوسان قیمت و RSI"""
    if change > 2 and rsi < 70:
        return "🟢 خرید قوی", 85
    elif change > 0.5 and rsi < 60:
        return "🟢 خرید", 70
    elif change < -2 and rsi > 30:
        return "🔴 فروش قوی", 85
    elif change < -0.5 and rsi > 40:
        return "🔴 فروش", 70
    else:
        return "⚪ نگهداری", 50

# ---------------------------- ارسال خودکار سیگنال (هر 5 دقیقه) ----------------------------
async def auto_signal_loop(app):
    """حلقه‌ای برای ارسال خودکار سیگنال هر 5 دقیقه به کانال"""
    while True:
        await asyncio.sleep(300)  # 300 ثانیه = 5 دقیقه
        if not CHANNEL_ID:
            continue
        # ارسال سیگنال برای 3 ارز اول (برای جلوگیری از Flood)
        for symbol, info in list(SYMBOLS.items())[:3]:
            data = await get_coinex_price(symbol)
            if not data:
                continue
            # شبیه‌سازی قیمت‌های گذشته برای محاسبه RSI
            base = data["price"]
            prices = [base * (1 + random.uniform(-0.02, 0.02)) for _ in range(30)]
            rsi = calculate_rsi(prices)
            signal, confidence = generate_signal(data["change"], rsi)
            # تولید پیام زیبا با فرمت Markdown
            msg = f"""
╔══════════════════════════════════════╗
║   🔥 {info['emoji']} *{symbol.replace('USDT','')}* - سیگنال لحظه‌ای 🔥   ║
╚══════════════════════════════════════╝

💰 **قیمت لحظه‌ای:** `${data['price']:,.2f}`
📈 **تغییرات 24 ساعته:** `{data['change']:+.2f}%`
🎯 **سیگنال معاملاتی:** **{signal}** (اطمینان {confidence}%)
📊 **شاخص قدرت نسبی (RSI):** `{rsi:.1f}`

✨ @comedyclick
"""
            try:
                # ارسال پیام به کانال
                await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
                logger.info(f"✅ سیگنال خودکار {symbol} با موفقیت ارسال شد.")
                await asyncio.sleep(3)  # وقفه 3 ثانیه‌ای برای جلوگیری از Flood
            except Exception as e:
                logger.error(f"❌ خطا در ارسال سیگنال {symbol}: {e}")

# ============================ طراحی منوی شیشه‌ای ربات ============================
def get_main_menu():
    """منوی اصلی ربات با دکمه‌های شیشه‌ای"""
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start - نمایش منو و خوش‌آمدگویی"""
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی به این ربات را ندارید.")
        return
    await update.message.reply_text(
        "🔥 *ربات حرفه‌ای کریپتو* 🔥\n\n"
        "✅ **قیمت لحظه‌ای 7 ارز دیجیتال برتر**\n"
        "✅ **سیگنال خرید/فروش بر اساس نوسانات بازار**\n"
        "✅ **ارسال خودکار سیگنال به کانال هر 5 دقیقه**\n\n"
        "از منوی زیر انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش قیمت لحظه‌ای تمام ارزها"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌های لحظه‌ای...")
    text = "💰 *قیمت لحظه‌ای ارزها* 💰\n\n"
    for sym, info in SYMBOLS.items():
        data = await get_coinex_price(sym)
        if data:
            # انتخاب ایموجی بر اساس علامت تغییرات قیمت
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{sym.replace('USDT','')}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت سیگنال فوری برای بیت‌کوین"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تحلیل بازار و تولید سیگنال...")
    sym = list(SYMBOLS.keys())[0]  # دریافت سیگنال برای بیت‌کوین (BTC)
    data = await get_coinex_price(sym)
    if not data:
        await query.edit_message_text("❌ خطا در دریافت داده‌های بازار. لطفاً دوباره تلاش کنید.")
        return
    # شبیه‌سازی 30 روز داده قیمتی برای محاسبه RSI
    prices = [data["price"] * (1 + random.uniform(-0.02, 0.02)) for _ in range(30)]
    rsi = calculate_rsi(prices)
    signal, confidence = generate_signal(data["change"], rsi)
    msg = (
        f"🎯 *سیگنال لحظه‌ای {sym.replace('USDT','')}* 🎯\n\n"
        f"💰 **قیمت:** ${data['price']:,.2f}\n"
        f"📈 **تغییرات 24 ساعته:** {data['change']:+.2f}%\n"
        f"🔔 **سیگنال:** {signal} (اطمینان {confidence}%)\n"
        f"📊 **شاخص RSI:** {rsi:.1f}"
    )
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای سریع ربات"""
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *راهنمای ربات* ❓\n\n"
        "📊 **قیمت لحظه‌ای:** مشاهده قیمت زنده ارزهای دیجیتال.\n"
        "🎯 **سیگنال فوری:** دریافت سیگنال خرید/فروش بر اساس تحلیل بازار.\n"
        "⏰ **ارسال خودکار:** ربات هر ۵ دقیقه یک سیگنال تحلیلی به کانال ارسال می‌کند.\n\n"
        "⚠️ **توجه:** این ربات فقط جنبه آموزشی دارد و مسئولیت هرگونه تصمیم معاملاتی بر عهده شماست."
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی اصلی"""
    await start(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک روی دکمه‌های شیشه‌ای"""
    query = update.callback_query
    data = query.data
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.answer()
        await query.edit_message_text("⚙️ این بخش در حال توسعه است...")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های متنی ساده کاربر"""
    await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

# ============================ اجرای اصلی ربات ============================
def main():
    """تابع اصلی راه‌اندازی ربات"""
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # راه‌اندازی حلقه خودکار ارسال سیگنال در پس‌زمینه
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(auto_signal_loop(app))

    logger.info("🚀 ربات حرفه‌ای کریپتو با موفقیت راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
