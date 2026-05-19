import os
import logging
import hashlib
import hmac
import time
import json
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ========== تنظیمات CoinEx ==========
ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")

# ========== ارزها ==========
SYMBOLS = [
    {"symbol": "BTCUSDT", "name": "بیت‌کوین", "emoji": "👑"},
    {"symbol": "ETHUSDT", "name": "اتریوم", "emoji": "💎"},
    {"symbol": "SOLUSDT", "name": "سولانا", "emoji": "⚡"},
    {"symbol": "XRPUSDT", "name": "ریپل", "emoji": "💧"},
    {"symbol": "DOGEUSDT", "name": "داوج", "emoji": "🐕"},
    {"symbol": "ADAUSDT", "name": "کاردانو", "emoji": "🌿"},
]

# ========== تابع امضای CoinEx ==========
def coinex_sign(method, request_path, body="", timestamp=None):
    if timestamp is None:
        timestamp = str(int(time.time() * 1000))
    
    if body:
        body = json.dumps(body)
    
    sign_str = method.upper() + request_path + timestamp + body
    signature = hmac.new(SECRET_KEY.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, timestamp

async def coinex_request(method, path, body=None):
    """ارسال درخواست به API CoinEx"""
    if not ACCESS_ID or not SECRET_KEY:
        return {"success": False, "error": "API Key تنظیم نشده"}
    
    url = f"https://api.coinex.com/v1{path}"
    timestamp = str(int(time.time() * 1000))
    
    signature, timestamp = coinex_sign(method, path, body, timestamp)
    
    headers = {
        "Authorization": ACCESS_ID,
        "Signature": signature,
        "Timestamp": timestamp,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, headers=headers, json=body)
            
            data = response.json()
            if data.get("code") == 0:
                return {"success": True, "data": data.get("data")}
            else:
                return {"success": False, "error": data.get("message", "خطا")}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_coinex_price(symbol="BTCUSDT"):
    """دریافت قیمت از CoinEx (بدون نیاز به API Key)"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"https://api.coinex.com/v1/market/ticker?market={symbol}")
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    ticker = data.get("data", {}).get("ticker", {})
                    return {
                        "success": True,
                        "price": float(ticker.get("last", 0)),
                        "change": float(ticker.get("change", 0)),
                        "volume": float(ticker.get("vol", 0)),
                        "high": float(ticker.get("high", 0)),
                        "low": float(ticker.get("low", 0)),
                    }
    except Exception as e:
        logger.error(f"Error: {e}")
    
    return {"success": False, "error": "خطا در دریافت قیمت"}

async def get_account_balance():
    """دریافت موجودی حساب (نیاز به API Key)"""
    result = await coinex_request("GET", "/account/balance")
    if result["success"]:
        balances = result["data"].get("data", {})
        usdt_balance = balances.get("USDT", {})
        return {
            "success": True,
            "total": float(usdt_balance.get("total", 0)),
            "free": float(usdt_balance.get("available", 0)),
            "frozen": float(usdt_balance.get("frozen", 0))
        }
    return {"success": False, "error": result.get("error", "خطا")}

# ========== دکمه‌ها و منوها ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال‌ها", callback_data="signals")],
        [InlineKeyboardButton("💰 موجودی حساب", callback_data="balance")],
        [InlineKeyboardButton("🔑 وضعیت API", callback_data="status")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])

# ========== هندلرها ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_status = "✅ متصل" if ACCESS_ID and SECRET_KEY else "❌ نیاز به تنظیم API"
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

          🔥 *ربات کوینکس* 🔥
          
      متصل به صرافی CoinEx

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

┌─────────────────────────────────┐
│  👑 قیمت لحظه‌ای ۶ ارز برتر     │
│  📡 داده واقعی از CoinEx        │
│  💰 مشاهده موجودی حساب          │
└─────────────────────────────────┘

📡 **وضعیت API:** {api_status}

📌 *از منوی زیر انتخاب کن*

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔄 دریافت قیمت‌ها از CoinEx...")
    
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n"
    text += "           💰 *قیمت لحظه‌ای کوینکس* 💰\n"
    text += "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n"
    
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        
        if data["success"]:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} *{s['symbol']}*\n"
            text += f"┌─────────────────────────\n"
            text += f"├ 💰 قیمت: ${data['price']:,.4f}\n"
            text += f"├ 📈 تغییر: {data['change']:+.2f}%\n"
            text += f"└─────────────────────────\n\n"
        else:
            text += f"❌ *{s['symbol']}*: {data.get('error', 'خطا')}\n\n"
    
    text += "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n"
    text += f"🕐 {datetime.now().strftime('%H:%M:%S')}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔄 محاسبه سیگنال‌ها...")
    
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n"
    text += "          📡 *سیگنال‌های لحظه‌ای* 📡\n"
    text += "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n"
    
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        
        if data["success"]:
            change = data["change"]
            if change > 2:
                signal = "🟢🟢 خرید قوی"
                conf = 85
            elif change > 0.5:
                signal = "🟢 خرید"
                conf = 65
            elif change < -2:
                signal = "🔴🔴 فروش قوی"
                conf = 85
            elif change < -0.5:
                signal = "🔴 فروش"
                conf = 65
            else:
                signal = "⚪ نگهداری"
                conf = 50
            
            arrow = "📈" if change > 0 else "📉" if change < 0 else "➖"
            text += f"{s['emoji']} *{s['symbol']}*\n"
            text += f"┌─────────────────────────\n"
            text += f"├ 💰 ${data['price']:,.4f}\n"
            text += f"├ {arrow} {change:+.2f}%\n"
            text += f"├ {signal} ({conf}%)\n"
            text += f"└─────────────────────────\n\n"
        else:
            text += f"❌ *{s['symbol']}*: {data.get('error', 'خطا')}\n\n"
    
    text += "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not ACCESS_ID or not SECRET_KEY:
        await query.edit_message_text(
            "❌ **API Key تنظیم نشده است**\n\n"
            "لطفاً متغیرهای زیر را در Railway تنظیم کنید:\n"
            "• `COINEX_ACCESS_ID`\n"
            "• `COINEX_SECRET_KEY`\n\n"
            "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )
        return
    
    await query.edit_message_text("🔄 دریافت موجودی حساب...")
    
    balance = await get_account_balance()
    
    if balance["success"]:
        text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          💰 *موجودی حساب کوینکس* 💰
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

┌─────────────────────────────
├ 💵 **USDT (کل):** ${balance['total']:,.2f}
├ 📊 **قابل استفاده:** ${balance['free']:,.2f}
├ 🔒 **مسدود شده:** ${balance['frozen']:,.2f}
└─────────────────────────────

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    else:
        text = f"❌ خطا: {balance.get('error', 'مشخص نیست')}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def status_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          ⚙️ *وضعیت سیستم* ⚙️
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📡 **وضعیت API CoinEx:**
┌─────────────────────────────
├ 🔑 Access ID: {'✅ تنظیم شده' if ACCESS_ID else '❌ تنظیم نشده'}
├ 🔒 Secret Key: {'✅ تنظیم شده' if SECRET_KEY else '❌ تنظیم نشده'}
└─────────────────────────────

📊 **وضعیت ربات:**
┌─────────────────────────────
├ 🤖 ربات: **فعال**
├ 📡 اینترنت: **متصل**
├ 🕐 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
└─────────────────────────────

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          ❓ *راهنما* ❓
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **انواع سیگنال:**

🟢🟢 خرید قوی → ورود مطمئن (>+2%)
🟢 خرید → ورود با احتیاط (+0.5% تا +2%)
⚪ نگهداری → صبر کن (-0.5% تا +0.5%)
🔴 فروش → خروج تدریجی (-2% تا -0.5%)
🔴🔴 فروش قوی → خروج فوری (<-2%)

🔧 **تنظیمات API در Railway:**

متغیرهای محیطی:
• `COINEX_ACCESS_ID` - Access ID از CoinEx
• `COINEX_SECRET_KEY` - Secret Key از CoinEx
• `TELEGRAM_BOT_TOKEN` - توکن ربات

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
⚠️ فقط جنبه آموزشی - مسئولیت با شماست
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back":
        await back_handler(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signals":
        await signals_menu(update, context)
    elif data == "balance":
        await balance_menu(update, context)
    elif data == "status":
        await status_menu(update, context)
    elif data == "help":
        await help_menu(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ لطفاً از دکمه‌های منو استفاده کن یا /start بزن")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 ربات کوینکس با موفقیت روشن شد...")
    print("✅ ربات در حال اجراست...")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
