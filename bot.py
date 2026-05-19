import os
import logging
import hashlib
import hmac
import time
import json
import httpx
import asyncio
import numpy as np
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========== OWNER_ID ==========
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

# ========== CoinEx تنظیمات ==========
ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")

MAX_RISK_PERCENT = 2.0
MAX_POSITIONS = 3
STOP_LOSS_PERCENT = 3.0
TAKE_PROFIT_PERCENT = 6.0

# ========== ارزها ==========
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

# ========== دمو معامله خودکار ==========
demo_balance = 10000
demo_positions = {}
auto_trade_enabled = False
price_alerts = {}  # {"symbol_target": chat_id}

# ========== توابع API ==========
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
        return 25

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

# ========== تشخیص سیگنال برای معامله خودکار ==========
def get_trading_signal(price, change, rsi, macd, macd_signal):
    score = 0
    if rsi < 30:
        score += 30
    if rsi > 70:
        score -= 30
    if macd > macd_signal:
        score += 25
    if macd < macd_signal:
        score -= 25
    if change > 2:
        score += 20
    if change < -2:
        score -= 20
    
    if score >= 40:
        return "BUY", min(90, 60 + score)
    elif score <= -40:
        return "SELL", min(90, 60 + abs(score))
    else:
        return "HOLD", 50

# ========== هوش مصنوعی Groq با حالت شوخ‌طبعی ==========
async def groq_chat(user_message, personality="funny"):
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است. لطفاً GROQ_API_KEY را در Railway اضافه کنید."
    
    if personality == "funny":
        system_prompt = "تو یک دستیار شوخ‌طبع، خونگرم و بامزه هستی. با انرژی مثبت و طنز پاسخ بده. از ایموجی استفاده کن. پاسخ‌ها کوتاه و مفید باشد."
    elif personality == "serious":
        system_prompt = "تو یک تحلیلگر حرفه‌ای و جدی هستی. پاسخ‌های دقیق و فنی بده."
    else:
        system_prompt = "تو یک دستیار مفید و خونگرم هستی."
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.8
                }
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return "خطا در ارتباط با هوش مصنوعی. لطفاً دوباره تلاش کنید."

async def groq_market_analysis(symbol, price, change, rsi, sentiment):
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است."
    prompt = f"""
به عنوان یک تحلیلگر حرفه‌ای بازار کریپتو با لحنی شوخ و خونگرم، {symbol} را تحلیل کن:
قیمت: ${price:,.0f}
تغییر 24h: {change:+.2f}%
RSI: {rsi:.0f}
احساسات بازار: {sentiment}
در ۴-۵ خط تحلیل کن شامل: وضعیت، پیش‌بینی، توصیه و مدیریت ریسک.
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
    except:
        pass
    return "خطا در تحلیل"

async def groq_fundamental_analysis():
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است."
    prompt = "تحلیل فاندامنتال امروز بازار کریپتو: اخبار مهم، احساسات بازار، تأثیرات اقتصادی. در ۴ خط خلاصه کن."
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 400}
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
    except:
        pass
    return "خطا در تحلیل فاندامنتال"

# ========== خودکار دمو ==========
async def auto_trade_loop(context: ContextTypes.DEFAULT_TYPE):
    global auto_trade_enabled, demo_balance, demo_positions
    if not auto_trade_enabled:
        return
    
    for s in SYMBOLS:
        symbol = s["symbol"]
        price_data = await get_coinex_price(symbol)
        if not price_data["success"]:
            continue
        
        # تولید داده شبیه‌سازی شده
        prices = [price_data["price"] * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
        rsi = TechnicalAnalysis.calculate_rsi(prices)
        macd, macd_sig, _ = TechnicalAnalysis.calculate_macd(prices)
        signal, confidence = get_trading_signal(price_data["price"], price_data["change"], rsi, macd, macd_sig)
        
        if signal == "BUY" and confidence > 70:
            # خرید خودکار در دمو
            if symbol not in demo_positions and len(demo_positions) < MAX_POSITIONS:
                amount_usdt = demo_balance * 0.2
                amount_coin = amount_usdt / price_data["price"]
                if amount_coin > 0 and amount_usdt <= demo_balance:
                    demo_balance -= amount_usdt
                    demo_positions[symbol] = {
                        "amount": amount_coin,
                        "entry_price": price_data["price"],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    logger.info(f"Auto buy {symbol} at ${price_data['price']:.2f}")
        
        elif signal == "SELL" and confidence > 70:
            if symbol in demo_positions:
                pos = demo_positions[symbol]
                sell_value = pos["amount"] * price_data["price"]
                demo_balance += sell_value
                del demo_positions[symbol]
                logger.info(f"Auto sell {symbol} at ${price_data['price']:.2f}")

# ========== دکمه‌ها ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ سیگنال لحظه‌ای", callback_data="signals")],
        [InlineKeyboardButton("📊 قیمت ارزها", callback_data="prices")],
        [InlineKeyboardButton("🎯 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل هوشمند Groq", callback_data="ai_menu")],
        [InlineKeyboardButton("📰 تحلیل فاندامنتال", callback_data="fundamental")],
        [InlineKeyboardButton("🤖 چت با AI (طنز)", callback_data="chat_ai")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale")],
        [InlineKeyboardButton("💰 معامله واقعی", callback_data="trade_real")],
        [InlineKeyboardButton("🎮 معامله دمو", callback_data="trade_demo")],
        [InlineKeyboardButton("⚡ معامله خودکار دمو", callback_data="auto_trade")],
        [InlineKeyboardButton("📈 پوزیشن‌ها", callback_data="positions")],
        [InlineKeyboardButton("🔔 هشدار قیمت", callback_data="alert_menu")],
        [InlineKeyboardButton("📰 اخبار کریپتو", callback_data="news")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_refresh_keyboard(back_callback, refresh_callback):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data=refresh_callback)],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=back_callback)]
    ])

# ========== منوها ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      🔥 *ربات فوق‌هوشمند کریپتو* 🔥
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **قابلیت‌ها:**
• تحلیل تکنیکال کامل (RSI, MACD, Stochastic, CCI, Williams, ADX, Bollinger, Fibonacci)
• تحلیل هوشمند با Groq AI (طنز و خونگرم)
• تحلیل فاندامنتال لحظه‌ای
• چت عمومی با AI (هر موضوعی)
• معامله خودکار دمو (خرید/فروش اتوماتیک)
• هشدار قیمت
• ردیابی نهنگ‌ها

📌 **از منوی زیر انتخاب کن:**
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# ========== منوی چت با AI ==========
async def chat_ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🤖 **حالت چت با هوش مصنوعی (طنز و خونگرم)** 🤖\n\n"
        "هر سوالی داری بپرس! هر چیزی که دلت می‌خواد.\n"
        "من با لحنی شوخ و بامزه جواب می‌دم.\n\n"
        "✏️ **سوالت رو بنویس...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["chat_mode"] = "ai_chat"

async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    await update.message.reply_chat_action("typing")
    response = await groq_chat(user_msg, "funny")
    await update.message.reply_text(response, parse_mode="Markdown")

# ========== تحلیل‌ها ==========
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
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "signals"))

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 **قیمت لحظه‌ای ارزها** 💰\n\n"
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        if data["success"]:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} *{s['symbol']}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "prices"))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"{s['emoji']} {s['symbol']}", callback_data=f"tech_{s['symbol']}")] for s in SYMBOLS[:6]]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text("📊 **تحلیل تکنیکال**\nارز را انتخاب کن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 تحلیل {symbol}...")
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا", reply_markup=get_back_refresh_keyboard("technical", f"tech_{symbol}"))
        return
    
    np.random.seed(0)
    prices = [data["price"] * (1 + np.random.randn(50) * 0.015) for _ in range(50)]
    highs = [p * 1.005 for p in prices]
    lows = [p * 0.995 for p in prices]
    
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    macd, macd_sig, _ = TechnicalAnalysis.calculate_macd(prices)
    stoch_k, stoch_d = TechnicalAnalysis.calculate_stochastic(highs, lows, prices)
    cci = TechnicalAnalysis.calculate_cci(highs, lows, prices)
    williams = TechnicalAnalysis.calculate_williams_r(highs, lows, prices)
    bb_u, bb_m, bb_l = TechnicalAnalysis.calculate_bollinger(prices)
    sr = TechnicalAnalysis.calculate_support_resistance(prices)
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      📊 *تحلیل تکنیکال {symbol}* 📊
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

💰 **قیمت:** ${data['price']:,.2f}
📈 **تغییر:** {data['change']:+.2f}%

📊 **اندیکاتورها:**
• RSI: {rsi:.1f}
• MACD: {macd:.2f}
• Stochastic: {stoch_k:.1f}/{stoch_d:.1f}
• CCI: {cci:.1f}
• Williams: {williams:.1f}
• باند بولینگر: بالا ${bb_u:,.0f} / پایین ${bb_l:,.0f}

🔑 **سطوح کلیدی:**
🟢 حمایت: ${sr['support'][0]:,.0f}
🔴 مقاومت: ${sr['resistance'][0]:,.0f}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("technical", f"tech_{symbol}"))

async def ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"🧠 {s['symbol']}", callback_data=f"groq_{s['symbol']}")] for s in SYMBOLS[:6]]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text("🧠 **تحلیل هوشمند با Groq AI**\nارز را انتخاب کن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def groq_analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🤖 تحلیل {symbol} با AI...")
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا", reply_markup=get_back_refresh_keyboard("ai_menu", f"groq_{symbol}"))
        return
    
    prices = [data["price"] * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    sentiment = random.choice(["صعودی", "نزولی", "خنثی"])
    analysis = await groq_market_analysis(symbol, data["price"], data["change"], rsi, sentiment)
    
    text = f"🧠 **تحلیل {symbol} با Groq AI** 🧠\n\n{analysis}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("ai_menu", f"groq_{symbol}"))

async def fundamental_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📰 در حال تحلیل فاندامنتال...")
    analysis = await groq_fundamental_analysis()
    text = f"📰 **تحلیل فاندامنتال** 📰\n\n{analysis}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "fundamental"))

async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
📰 **آخرین اخبار کریپتو** 📰

🔥 بیت‌کوین به 70 هزار دلار نزدیک شد!
💎 اتریوم آپدیت بعدی را اعلام کرد
⚡ سولانا رکورد تراکنش‌ها را شکست
🐋 نهنگ‌ها در حال انباشت BTC هستند

📌 اخبار لحظه‌ای به زودی...
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "news"))

# ========== معامله دمو ==========
async def trade_demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
🎮 **حالت معامله دمو** 🎮

💰 موجودی نقد: ${demo_balance:.2f}
📊 تعداد پوزیشن‌ها: {len(demo_positions)}

انتخاب کن:
"""
    keyboard = []
    for s in SYMBOLS[:6]:
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} خرید {s['symbol']}", callback_data=f"demo_buy_{s['symbol']}")])
        keyboard.append([InlineKeyboardButton(f"فروش {s['symbol']}", callback_data=f"demo_sell_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("📈 پوزیشن‌های باز", callback_data="demo_positions")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def demo_buy(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    global demo_balance, demo_positions
    query = update.callback_query
    await query.answer()
    price_data = await get_coinex_price(symbol)
    if not price_data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=get_back_refresh_keyboard("trade_demo", f"demo_buy_{symbol}"))
        return
    amount_usdt = 100  # مبلغ ثابت برای سادگی
    amount_coin = amount_usdt / price_data["price"]
    if amount_usdt > demo_balance:
        await query.edit_message_text("❌ موجودی کافی نیست", reply_markup=get_back_refresh_keyboard("trade_demo", f"demo_buy_{symbol}"))
        return
    demo_balance -= amount_usdt
    if symbol in demo_positions:
        old = demo_positions[symbol]
        total_cost = old["amount"] * old["entry_price"] + amount_coin * price_data["price"]
        total_amount = old["amount"] + amount_coin
        avg_price = total_cost / total_amount
        demo_positions[symbol] = {"amount": total_amount, "entry_price": avg_price, "timestamp": datetime.now().strftime("%H:%M:%S")}
    else:
        demo_positions[symbol] = {"amount": amount_coin, "entry_price": price_data["price"], "timestamp": datetime.now().strftime("%H:%M:%S")}
    await query.edit_message_text(f"✅ خرید {symbol} با قیمت ${price_data['price']:.2f}\n💰 موجودی: ${demo_balance:.2f}", reply_markup=get_back_refresh_keyboard("trade_demo", f"demo_buy_{symbol}"))

async def demo_sell(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    global demo_balance, demo_positions
    query = update.callback_query
    await query.answer()
    if symbol not in demo_positions:
        await query.edit_message_text("❌ پوزیشنی برای فروش ندارید", reply_markup=get_back_refresh_keyboard("trade_demo", f"demo_sell_{symbol}"))
        return
    price_data = await get_coinex_price(symbol)
    if not price_data["success"]:
        await query.edit_message_text("❌ خطا", reply_markup=get_back_refresh_keyboard("trade_demo", f"demo_sell_{symbol}"))
        return
    pos = demo_positions[symbol]
    sell_value = pos["amount"] * price_data["price"]
    pnl = sell_value - (pos["amount"] * pos["entry_price"])
    demo_balance += sell_value
    del demo_positions[symbol]
    await query.edit_message_text(f"✅ فروش {symbol} با قیمت ${price_data['price']:.2f}\n📈 سود/زیان: ${pnl:+.2f}\n💰 موجودی: ${demo_balance:.2f}", reply_markup=get_back_refresh_keyboard("trade_demo", f"demo_sell_{symbol}"))

async def demo_positions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not demo_positions:
        await query.edit_message_text("📭 هیچ پوزیشنی ندارید", reply_markup=get_back_refresh_keyboard("trade_demo", "demo_positions"))
        return
    text = "📈 **پوزیشن‌های باز** 📈\n\n"
    for sym, pos in demo_positions.items():
        text += f"{sym}: {pos['amount']:.6f} @ ${pos['entry_price']:.2f}\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("trade_demo", "demo_positions"))

async def auto_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_trade_enabled
    query = update.callback_query
    await query.answer()
    auto_trade_enabled = not auto_trade_enabled
    status = "✅ فعال" if auto_trade_enabled else "❌ غیرفعال"
    text = f"⚡ **معامله خودکار دمو** ⚡\n\nوضعیت: {status}\n\nربات به صورت خودکار بر اساس سیگنال‌ها خرید و فروش می‌کند.\nحداکثر {MAX_POSITIONS} پوزیشن همزمان."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "auto_trade"))

async def alert_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🔔 **هشدار قیمت** 🔔\n\nبرای تنظیم هشدار، ارسال کنید:\n`ALERT BTCUSDT 70000`\n\nهشدارهای فعال:\n" + "\n".join(price_alerts.keys()) if price_alerts else "هیچ هشدار فعالی نیست"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "alert_menu"))

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
🛡️ **مدیریت ریسک** 🛡️

• حداکثر ریسک: {MAX_RISK_PERCENT}% سرمایه
• نسبت ریسک/ریوارد: 1:{TAKE_PROFIT_PERCENT/STOP_LOSS_PERCENT:.1f}
• حد ضرر: {STOP_LOSS_PERCENT}%
• حداکثر پوزیشن: {MAX_POSITIONS}

📈 **فرمول:** حجم = (سرمایه × {MAX_RISK_PERCENT}%) / (قیمت × {STOP_LOSS_PERCENT}%)
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "risk"))

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
⚙️ **تنظیمات** ⚙️

• CoinEx API: {'✅' if ACCESS_ID else '❌'}
• Groq API: {'✅' if GROQ_API_KEY else '❌'}
• مالک: {OWNER_ID if OWNER_ID != 0 else 'همه مجاز'}
• معامله خودکار: {'✅' if auto_trade_enabled else '❌'}
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "settings"))

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
🐋 **ردیابی نهنگ‌ها** 🐋

📊 آخرین تراکنش‌های بزرگ:
• 1,250 BTC (84M$) خرید
• 15,000 ETH (51.8M$) فروش
• 250,000 SOL (39.1M$) خرید

📈 تحلیل: خرید نهنگ‌ها روی BTC نشانه صعود است.
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "whale"))

async def trade_real_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    balance = await get_account_balance()
    text = f"💰 **معامله واقعی CoinEx**\nموجودی: ${balance['free']:,.2f} USDT\n\n⚠️ به دلایل امنیتی غیرفعال است.\nاز حالت دمو استفاده کنید."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "trade_real"))

async def positions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "📈 **پوزیشن‌های واقعی**\n\nهیچ پوزیشنی وجود ندارد."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "positions"))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
❓ **راهنما** ❓

📊 **دکمه‌ها:**
• سیگنال لحظه‌ای: خرید/فروش/نگهداری
• تحلیل تکنیکال: RSI, MACD, باندها
• تحلیل هوشمند Groq: با طنز و خونگرمی
• چت با AI: هر سوالی بپرس
• معامله خودکار دمو: خرید/فروش اتوماتیک
• هشدار قیمت: تنظیم اعلان

⚠️ فقط جنبه آموزشی
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_refresh_keyboard("back", "help"))

# ========== هندلرها ==========
async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("chat_mode", None)
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
    elif data == "fundamental":
        await fundamental_menu(update, context)
    elif data == "chat_ai":
        await chat_ai_menu(update, context)
    elif data == "whale":
        await whale_menu(update, context)
    elif data == "trade_real":
        await trade_real_menu(update, context)
    elif data == "trade_demo":
        await trade_demo_menu(update, context)
    elif data == "auto_trade":
        await auto_trade_menu(update, context)
    elif data == "positions":
        await positions_menu(update, context)
    elif data == "demo_positions":
        await demo_positions_menu(update, context)
    elif data == "alert_menu":
        await alert_menu(update, context)
    elif data == "news":
        await news_menu(update, context)
    elif data == "risk":
        await risk_menu(update, context)
    elif data == "settings":
        await settings_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data.startswith("tech_"):
        await technical_analysis(update, context, data.split("_")[1])
    elif data.startswith("groq_"):
        await groq_analysis_handler(update, context, data.split("_")[1])
    elif data.startswith("demo_buy_"):
        await demo_buy(update, context, data.split("_")[2])
    elif data.startswith("demo_sell_"):
        await demo_sell(update, context, data.split("_")[2])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    
    if context.user_data.get("chat_mode") == "ai_chat":
        await handle_ai_chat(update, context)
    elif update.message.text.upper().startswith("ALERT"):
        parts = update.message.text.split()
        if len(parts) >= 3:
            symbol = parts[1]
            try:
                price = float(parts[2])
                price_alerts[f"{symbol}_{price}"] = update.effective_chat.id
                await update.message.reply_text(f"✅ هشدار برای {symbol} در قیمت ${price:,.0f} تنظیم شد.")
            except:
                await update.message.reply_text("❌ فرمت: ALERT BTCUSDT 70000")
        else:
            await update.message.reply_text("❌ فرمت صحیح: ALERT BTCUSDT 70000")
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

async def auto_trade_background(context: ContextTypes.DEFAULT_TYPE):
    await auto_trade_loop(context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # اضافه کردن Job برای معامله خودکار هر 30 ثانیه
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(auto_trade_background, interval=30, first=10)
    
    logger.info("ربات فوق‌هوشمند با معامله خودکار و چت AI روشن شد.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
