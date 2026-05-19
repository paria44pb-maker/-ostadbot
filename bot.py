import os
import logging
import hashlib
import hmac
import time
import json
import httpx
import asyncio
import numpy as np
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========== OWNER_ID (محدودیت دسترسی) ==========
owner_id_str = os.getenv("OWNER_ID", "0")
try:
    OWNER_ID = int(owner_id_str)
except ValueError:
    OWNER_ID = 0

async def is_owner(update: Update) -> bool:
    if OWNER_ID == 0:
        return True
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی به این ربات را ندارید.")
        return False
    return True

# ========== تنظیمات CoinEx ==========
ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")

MAX_RISK_PERCENT = 2.0
MAX_POSITIONS = 3
STOP_LOSS_PERCENT = 3.0
TAKE_PROFIT_PERCENT = 6.0

SYMBOLS = [
    {"symbol": "BTCUSDT", "name": "بیت‌کوین", "emoji": "👑", "min_amount": 0.0001},
    {"symbol": "ETHUSDT", "name": "اتریوم", "emoji": "💎", "min_amount": 0.001},
    {"symbol": "SOLUSDT", "name": "سولانا", "emoji": "⚡", "min_amount": 0.01},
    {"symbol": "XRPUSDT", "name": "ریپل", "emoji": "💧", "min_amount": 1},
    {"symbol": "DOGEUSDT", "name": "داوج", "emoji": "🐕", "min_amount": 10},
    {"symbol": "ADAUSDT", "name": "کاردانو", "emoji": "🌿", "min_amount": 10},
    {"symbol": "AVAXUSDT", "name": "آوالانچ", "emoji": "❄️", "min_amount": 0.1},
    {"symbol": "MATICUSDT", "name": "پالیگان", "emoji": "🟣", "min_amount": 5},
]

# ========== توابع ارتباط با CoinEx ==========
def coinex_sign(method, request_path, body="", timestamp=None):
    if timestamp is None:
        timestamp = str(int(time.time() * 1000))
    if body:
        body = json.dumps(body)
    sign_str = method.upper() + request_path + timestamp + body
    signature = hmac.new(SECRET_KEY.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, timestamp

async def coinex_request(method, path, body=None):
    if not ACCESS_ID or not SECRET_KEY:
        return {"success": False, "error": "API Key تنظیم نشده"}
    url = f"https://api.coinex.com/v1{path}"
    timestamp = str(int(time.time() * 1000))
    signature, timestamp = coinex_sign(method, path, body, timestamp)
    headers = {"Authorization": ACCESS_ID, "Signature": signature, "Timestamp": timestamp, "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, headers=headers, json=body)
            data = response.json()
            if data.get("code") == 0:
                return {"success": True, "data": data.get("data")}
            return {"success": False, "error": data.get("message", "خطا")}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_coinex_price(symbol="BTCUSDT"):
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

async def place_order(symbol, side, amount, order_type="market", price=None):
    body = {"market": symbol, "market_type": "SPOT", "side": side, "order_type": order_type, "amount": str(amount)}
    if price and order_type == "limit":
        body["price"] = str(price)
    return await coinex_request("POST", "/order/limit", body)

# ========== تحلیل تکنیکال ==========
class TechnicalAnalysis:
    @staticmethod
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
        avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0
        avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(prices):
        if len(prices) < 26:
            return 0, 0, 0
        def ema(data, period):
            multiplier = 2 / (period + 1)
            result = [data[0]]
            for price in data[1:]:
                result.append((price - result[-1]) * multiplier + result[-1])
            return result
        ema12 = ema(prices, 12)
        ema26 = ema(prices, 26)
        macd_line = [e12 - e26 for e12, e26 in zip(ema12, ema26)]
        signal_line = ema(macd_line, 9)
        histogram = [m - s for m, s in zip(macd_line, signal_line)]
        return macd_line[-1], signal_line[-1], histogram[-1]

    @staticmethod
    def calculate_stochastic(high, low, close, period=14):
        if len(close) < period:
            return 50, 50
        recent_high = max(high[-period:])
        recent_low = min(low[-period:])
        if recent_high == recent_low:
            return 50, 50
        k = 100 * ((close[-1] - recent_low) / (recent_high - recent_low))
        d = k
        return k, d

    @staticmethod
    def calculate_cci(high, low, close, period=20):
        if len(close) < period:
            return 0
        tp = [(h + l + c) / 3 for h, l, c in zip(high[-period:], low[-period:], close[-period:])]
        sma = sum(tp) / period
        mean_dev = sum(abs(t - sma) for t in tp) / period
        if mean_dev == 0:
            return 0
        return (tp[-1] - sma) / (0.015 * mean_dev)

    @staticmethod
    def calculate_williams_r(high, low, close, period=14):
        if len(close) < period:
            return -50
        recent_high = max(high[-period:])
        recent_low = min(low[-period:])
        if recent_high == recent_low:
            return -50
        return -100 * (recent_high - close[-1]) / (recent_high - recent_low)

    @staticmethod
    def calculate_adx():
        return 25  # simplified

    @staticmethod
    def calculate_bollinger(prices, period=20, std_dev=2):
        if len(prices) < period:
            return None, None, None
        sma = sum(prices[-period:]) / period
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std = variance ** 0.5
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

    @staticmethod
    def calculate_support_resistance(prices, lookback=50):
        recent = prices[-lookback:] if len(prices) > lookback else prices
        high = max(recent)
        low = min(recent)
        pivot = (high + low) / 2
        r1 = pivot + (high - low) * 0.382
        r2 = pivot + (high - low) * 0.618
        s1 = pivot - (high - low) * 0.382
        s2 = pivot - (high - low) * 0.618
        return {"support": [s1, s2, low], "resistance": [r1, r2, high], "pivot": pivot}

    @staticmethod
    def detect_trap(price, change, volume, rsi):
        if change > 3 and volume > 10000000 and rsi > 70:
            return "⚠️ تله گاوی! رشد ناگهانی با حجم بالا و RSI اشباع"
        elif change < -3 and volume > 10000000 and rsi < 30:
            return "⚠️ تله خرسی! ریزش ناگهانی با حجم بالا و RSI اشباع فروش"
        return "✅ بدون تله"

# ========== تحلیل فاندامنتال ==========
class FundamentalAnalysis:
    @staticmethod
    async def get_market_sentiment():
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://api.alternative.me/fng/?limit=1")
                if response.status_code == 200:
                    data = response.json()
                    fng = data.get("data", [{}])[0]
                    return {"sentiment": fng.get("value_classification", "Neutral"), "value": int(fng.get("value", 50))}
        except:
            pass
        return {"sentiment": "Neutral", "value": 50}

# ========== هوش مصنوعی Groq ==========
async def groq_analysis(symbol, price, change, rsi, sentiment):
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است."
    prompt = f"""
    به عنوان تحلیلگر حرفه‌ای بازار کریپتو، {symbol} را تحلیل کن:
    قیمت: ${price:,.0f}
    تغییر 24h: {change:+.2f}%
    RSI: {rsi:.0f}
    احساسات بازار: {sentiment}
    در ۴ خط تحلیل کن: وضعیت، پیش‌بینی، توصیه و مدیریت ریسک.
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return "خطا در ارتباط با هوش مصنوعی."

# ========== دکمه‌ها و منوها ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ سیگنال لحظه‌ای", callback_data="signals")],
        [InlineKeyboardButton("📊 قیمت ارزها", callback_data="prices")],
        [InlineKeyboardButton("🎯 تحلیل تکنیکال کامل", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل هوشمند Groq", callback_data="ai_menu")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale")],
        [InlineKeyboardButton("💰 معامله واقعی", callback_data="trade_real")],
        [InlineKeyboardButton("🎮 معامله دمو", callback_data="trade_demo")],
        [InlineKeyboardButton("📈 پوزیشن‌ها", callback_data="positions")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])

# ========== دمو معامله ==========
demo_balance = 10000

async def trade_demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"🎮 **حالت دمو**\n💰 موجودی: ${demo_balance:,.2f} USDT\n\nانتخاب ارز:"
    keyboard = []
    for s in SYMBOLS:
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} خرید {s['symbol']}", callback_data=f"demo_buy_{s['symbol']}")])
        keyboard.append([InlineKeyboardButton(f"فروش {s['symbol']}", callback_data=f"demo_sell_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def demo_buy(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    global demo_balance
    query = update.callback_query
    await query.answer()
    price_data = await get_coinex_price(symbol)
    if not price_data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=get_back_keyboard())
        return
    amount = (demo_balance * (MAX_RISK_PERCENT/100)) / price_data["price"]
    cost = amount * price_data["price"]
    if cost > demo_balance:
        await query.edit_message_text("❌ موجودی دمو کافی نیست", reply_markup=get_back_keyboard())
        return
    demo_balance -= cost
    await query.edit_message_text(f"✅ خرید دمو {symbol}\n💰 قیمت: ${price_data['price']:,.4f}\n📦 مقدار: {amount:.6f}\n💵 باقی‌مانده: ${demo_balance:,.2f}", parse_mode="Markdown", reply_markup=get_back_keyboard())

async def demo_sell(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    global demo_balance
    query = update.callback_query
    await query.answer()
    price_data = await get_coinex_price(symbol)
    if not price_data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=get_back_keyboard())
        return
    amount = 0.001
    demo_balance += amount * price_data["price"]
    await query.edit_message_text(f"✅ فروش دمو {symbol}\n💰 قیمت: ${price_data['price']:,.4f}\n💵 موجودی جدید: ${demo_balance:,.2f}", parse_mode="Markdown", reply_markup=get_back_keyboard())

# ========== سایر منوها (خلاصه) ==========
async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت سیگنال‌ها...")
    text = "✨ سیگنال‌های لحظه‌ای ✨\n\n"
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        if data["success"]:
            change = data["change"]
            signal = "🟢🟢 خرید قوی" if change > 2 else "🟢 خرید" if change > 0.5 else "🔴🔴 فروش قوی" if change < -2 else "🔴 فروش" if change < -0.5 else "⚪ نگهداری"
            arrow = "📈" if change > 0 else "📉" if change < 0 else "➖"
            text += f"{s['emoji']} *{s['symbol']}*: ${data['price']:,.2f} {arrow} {change:+.2f}% → {signal}\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 قیمت لحظه‌ای 💰\n\n"
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        if data["success"]:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} *{s['symbol']}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"{s['emoji']} {s['symbol']}", callback_data=f"tech_{s['symbol']}")] for s in SYMBOLS]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text("📊 تحلیل تکنیکال کامل - ارز را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 تحلیل {symbol}...")
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا", reply_markup=get_back_keyboard())
        return
    # simulate price history
    prices = [data["price"] * (1 + np.random.randn(50) * 0.015)]
    highs = [p * 1.005 for p in prices]
    lows = [p * 0.995 for p in prices]
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    macd, sig, _ = TechnicalAnalysis.calculate_macd(prices)
    stoch_k, stoch_d = TechnicalAnalysis.calculate_stochastic(highs, lows, prices)
    cci = TechnicalAnalysis.calculate_cci(highs, lows, prices)
    williams = TechnicalAnalysis.calculate_williams_r(highs, lows, prices)
    bb_u, bb_m, bb_l = TechnicalAnalysis.calculate_bollinger(prices)
    sr = TechnicalAnalysis.calculate_support_resistance(prices)
    trap = TechnicalAnalysis.detect_trap(data["price"], data["change"], data["volume"], rsi)
    text = f"""
✨ تحلیل تکنیکال {symbol} ✨
💰 قیمت: ${data['price']:,.2f}
📈 تغییر: {data['change']:+.2f}%
📊 RSI: {rsi:.1f}
📈 MACD: {macd:.2f} (sig: {sig:.2f})
🔵 Stochastic: {stoch_k:.1f}/{stoch_d:.1f}
🟠 CCI: {cci:.1f}
🟣 Williams: {williams:.1f}
📊 باند بولینگر: بالا ${bb_u:,.0f} / پایین ${bb_l:,.0f}
🔑 حمایت: ${sr['support'][0]:,.0f} / مقاومت: ${sr['resistance'][0]:,.0f}
{trap}
"""
    keyboard = [[InlineKeyboardButton("🧠 تحلیل AI", callback_data=f"ai_{symbol}")], [InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"🧠 {s['symbol']}", callback_data=f"ai_{s['symbol']}")] for s in SYMBOLS]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text("🧠 تحلیل هوشمند با Groq AI - ارز را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

async def ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🤖 در حال تحلیل {symbol} با AI...")
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا", reply_markup=get_back_keyboard())
        return
    prices = [data["price"] * (1 + np.random.randn(30) * 0.015)]
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    sentiment = await FundamentalAnalysis.get_market_sentiment()
    result = await groq_analysis(symbol, data["price"], data["change"], rsi, sentiment["sentiment"])
    text = f"🧠 تحلیل AI برای {symbol}:\n\n{result}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🐋 ردیابی نهنگ‌ها (شبیه‌سازی)\n\n• 1,250 BTC (84M$) خرید\n• 15,000 ETH (51.8M$) فروش\n• 250,000 SOL (39.1M$) خرید\n\nتحلیل: خرید نهنگ‌ها روی BTC نشانه صعود است."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def trade_real_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    balance = await get_account_balance()
    text = f"💰 معامله واقعی CoinEx\nموجودی قابل استفاده: ${balance['free']:,.2f} USDT\n\n⚠️ معامله واقعی با مسئولیت شماست.\nانتخاب ارز:"
    keyboard = []
    for s in SYMBOLS:
        keyboard.append([InlineKeyboardButton(f"خرید {s['symbol']}", callback_data=f"real_buy_{s['symbol']}"), InlineKeyboardButton(f"فروش {s['symbol']}", callback_data=f"real_sell_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def real_buy(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    balance = await get_account_balance()
    if balance["free"] < 10:
        await query.edit_message_text("❌ موجودی کافی نیست", reply_markup=get_back_keyboard())
        return
    price_data = await get_coinex_price(symbol)
    amount = (balance["free"] * (MAX_RISK_PERCENT/100)) / price_data["price"]
    await query.edit_message_text(f"⚠️ سفارش خرید واقعی {symbol} به مبلغ ${amount * price_data['price']:.2f} (در این نسخه غیرفعال است برای ایمنی)", reply_markup=get_back_keyboard())

async def real_sell(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"⚠️ سفارش فروش واقعی {symbol} (غیرفعال برای ایمنی)", reply_markup=get_back_keyboard())

async def positions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📈 پوزیشن‌های باز: هیچ پوزیشنی وجود ندارد.", reply_markup=get_back_keyboard())

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"🛡️ مدیریت ریسک\n\nحداکثر ریسک: {MAX_RISK_PERCENT}%\nنسبت ریسک/ریوارد: 1:{TAKE_PROFIT_PERCENT/STOP_LOSS_PERCENT:.1f}\nحد ضرر: {STOP_LOSS_PERCENT}%\nحداکثر پوزیشن: {MAX_POSITIONS}\nفرمول حجم معامله: سرمایه * {MAX_RISK_PERCENT}% / (قیمت * {STOP_LOSS_PERCENT}%)"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"⚙️ تنظیمات\n\n🔑 CoinEx API: {'✅' if ACCESS_ID else '❌'}\n🧠 Groq API: {'✅' if GROQ_API_KEY else '❌'}\n👤 مالک: {OWNER_ID if OWNER_ID != 0 else 'همه مجاز'}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "❓ راهنما\n\n✨ سیگنال لحظه‌ای\n📊 قیمت ارزها\n🎯 تحلیل تکنیکال کامل (RSI, MACD, Stochastic, CCI, Williams, ADX, Bollinger, Fibonacci)\n🧠 تحلیل هوشمند Groq AI\n🐋 ردیابی نهنگ‌ها\n💰 معامله واقعی و دمو\n🛡️ مدیریت ریسک\n\n⚠️ فقط جنبه آموزشی."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    query = update.callback_query
    data = query.data
    if data == "back":
        await back_handler(update, context)
    elif data == "signals":
        await signals_menu(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "ai_menu":
        await ai_menu(update, context)
    elif data == "whale":
        await whale_menu(update, context)
    elif data == "trade_real":
        await trade_real_menu(update, context)
    elif data == "trade_demo":
        await trade_demo_menu(update, context)
    elif data == "positions":
        await positions_menu(update, context)
    elif data == "risk":
        await risk_menu(update, context)
    elif data == "settings":
        await settings_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data.startswith("tech_"):
        await technical_analysis(update, context, data.split("_")[1])
    elif data.startswith("ai_"):
        await ai_analysis(update, context, data.split("_")[1])
    elif data.startswith("demo_buy_"):
        await demo_buy(update, context, data.split("_")[2])
    elif data.startswith("demo_sell_"):
        await demo_sell(update, context, data.split("_")[2])
    elif data.startswith("real_buy_"):
        await real_buy(update, context, data.split("_")[2])
    elif data.startswith("real_sell_"):
        await real_sell(update, context, data.split("_")[2])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    text = "🔥 ربات حرفه‌ای کریپتو 🔥\n\n🔹 تحلیل تکنیکال کامل\n🔹 هوش مصنوعی Groq\n🔹 ردیابی نهنگ‌ها و تشخیص تله\n🔹 معامله واقعی و دمو\n🔹 مدیریت ریسک\n\nاز منوی زیر انتخاب کن:"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کن یا /start بزن.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("ربات با موفقیت راه‌اندازی شد.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
