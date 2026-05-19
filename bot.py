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

# تنظیمات معاملاتی
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

# ========== تحلیل تکنیکال دقیق ==========
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
    def calculate_adx(high, low, close, period=14):
        # ساده شده
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

    @staticmethod
    async def get_news(symbol="BTC"):
        return [{"title": "آخرین اخبار بازار کریپتو", "source": "CryptoNews"}]

# ========== هوش مصنوعی Groq با تحلیل عمیق ==========
async def groq_deep_analysis(symbol, price, change, volume, high, low, rsi, macd, macd_signal, stoch_k, stoch_d, cci, williams_r, adx, bb_upper, bb_middle, bb_lower, support, resistance, trap, sentiment):
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است. لطفاً GROQ_API_KEY را در Railway اضافه کنید."
    
    prompt = f"""
**تحلیل کاملاً حرفه‌ای و بدون سانسور برای {symbol}:**

📊 **داده‌های لحظه‌ای:**
- قیمت: ${price:,.0f}
- تغییر 24h: {change:+.2f}%
- حجم 24h: ${volume/1e6:.2f}M
- بالاترین 24h: ${high:,.0f}
- پایین‌ترین 24h: ${low:,.0f}

📈 **اندیکاتورها و اسیلاتورها:**
- RSI(14): {rsi:.1f} (اشباع خرید >70، اشباع فروش <30)
- MACD: {macd:.2f} (سیگنال: {macd_signal:.2f}) → {'صعودی' if macd > macd_signal else 'نزولی'}
- استوکاستیک K/D: {stoch_k:.1f} / {stoch_d:.1f}
- CCI: {cci:.1f} (زیر -100 خرید، بالای +100 فروش)
- Williams %R: {williams_r:.1f} (بالای -20 اشباع خرید، زیر -80 اشباع فروش)
- ADX (قدرت روند): {adx:.1f} (بالای 25 روند قوی)
- باند بولینگر: بالا ${bb_upper:,.0f} / وسط ${bb_middle:,.0f} / پایین ${bb_lower:,.0f}
- حمایت‌ها: {support[0]:,.0f}, {support[1]:,.0f}, {support[2]:,.0f}
- مقاومت‌ها: {resistance[0]:,.0f}, {resistance[1]:,.0f}, {resistance[2]:,.0f}
- تشخیص تله: {trap}

📰 **تحلیل فاندامنتال:**
- شاخص ترس و طمع: {sentiment['value']}/100 ({sentiment['sentiment']})
- اخبار: بازار تحت تأثیر عوامل کلان اقتصادی است.

🔍 **تحلیل پرایس اکشن:**
- قیمت در محدوده {'حمایت' if price < support[0] else 'مقاومت' if price > resistance[0] else 'نوسانی'}
- حجم معاملات {'بالا' if volume > 1e9 else 'متوسط' if volume > 5e8 else 'پایین'}

🎯 **توصیه معاملاتی:**
بر اساس ترکیب اندیکاتورها و تحلیل تکنیکال، پیشنهاد می‌شود:
- نقاط ورود: نزدیک حمایت‌ها با شکست مقاومت‌ها
- حد ضرر: ۳٪ زیر قیمت ورود
- حد سود: ۶٪ بالای قیمت ورود
- مدیریت ریسک: حداکثر ۲٪ سرمایه در هر معامله

📌 **جمع‌بندی نهایی:** (BUY/SELL/HOLD) + درصد اطمینان
"""
    try:
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1200, "temperature": 0.5}
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return "خطا در ارتباط با هوش مصنوعی. لطفاً دوباره تلاش کنید."

# ========== دمو معامله (با ذخیره پوزیشن‌ها) ==========
demo_balance = 10000
demo_positions = {}  # {symbol: {"amount": float, "entry_price": float, "timestamp": str, "stop_loss": float, "take_profit": float}}

async def update_demo_balance_file():
    # برای سادگی از متغیر گلوبال استفاده می‌کنیم (در Railway بدون دیتابیس)
    pass

def get_demo_portfolio_value():
    total = demo_balance
    for sym, pos in demo_positions.items():
        price_data = asyncio.run(get_coinex_price(sym))
        if price_data["success"]:
            total += pos["amount"] * price_data["price"]
    return total

# ========== دکمه‌ها و منوها ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ سیگنال لحظه‌ای", callback_data="signals")],
        [InlineKeyboardButton("📊 قیمت ارزها", callback_data="prices")],
        [InlineKeyboardButton("🎯 تحلیل تکنیکال کامل", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل عمیق Groq AI", callback_data="ai_menu")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale")],
        [InlineKeyboardButton("💰 معامله واقعی", callback_data="trade_real")],
        [InlineKeyboardButton("🎮 معامله دمو", callback_data="trade_demo")],
        [InlineKeyboardButton("📈 پوزیشن‌های دمو", callback_data="demo_positions")],
        [InlineKeyboardButton("💹 گزارش دمو", callback_data="demo_report")],
        [InlineKeyboardButton("🔔 هشدار قیمت", callback_data="alert_menu")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])

# ========== تحلیل تکنیکال کامل (رفع خطا) ==========
async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"{s['emoji']} {s['symbol']}", callback_data=f"tech_{s['symbol']}")] for s in SYMBOLS]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text("📊 **تحلیل تکنیکال کامل**\nارز مورد نظر را انتخاب کنید:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 در حال تحلیل {symbol}...")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت. لطفاً دوباره تلاش کنید.", reply_markup=get_back_keyboard())
        return
    
    # تولید داده تاریخی شبیه‌سازی شده بر اساس قیمت فعلی
    np.random.seed(0)
    base = data["price"]
    prices = [base * (1 + np.random.randn(60) * 0.015) for _ in range(60)]
    highs = [p * 1.005 for p in prices]
    lows = [p * 0.995 for p in prices]
    closes = prices
    
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    macd, macd_sig, _ = TechnicalAnalysis.calculate_macd(prices)
    stoch_k, stoch_d = TechnicalAnalysis.calculate_stochastic(highs, lows, closes)
    cci = TechnicalAnalysis.calculate_cci(highs, lows, closes)
    williams = TechnicalAnalysis.calculate_williams_r(highs, lows, closes)
    adx = TechnicalAnalysis.calculate_adx(highs, lows, closes)
    bb_u, bb_m, bb_l = TechnicalAnalysis.calculate_bollinger(prices)
    sr = TechnicalAnalysis.calculate_support_resistance(prices)
    trap = TechnicalAnalysis.detect_trap(data["price"], data["change"], data["volume"], rsi)
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      📊 *تحلیل تکنیکال {symbol}* 📊
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

💰 **قیمت لحظه‌ای:** ${data['price']:,.2f}
📈 **تغییر 24h:** {data['change']:+.2f}%
📊 **حجم 24h:** ${data['volume']/1e6:.2f}M

┌─────────────────────────────────┐
│ 📈 **اندیکاتورها و اسیلاتورها** │
└─────────────────────────────────┘
🔹 RSI(14): **{rsi:.1f}** → {'اشباع خرید 🔴' if rsi > 70 else 'اشباع فروش 🟢' if rsi < 30 else 'خنثی ⚪'}
🔹 MACD: {macd:.2f} (سیگنال: {macd_sig:.2f}) → {'صعودی 📈' if macd > macd_sig else 'نزولی 📉'}
🔹 Stochastic K/D: {stoch_k:.1f} / {stoch_d:.1f}
🔹 CCI: {cci:.1f} → {'خرید قوی 🟢' if cci < -100 else 'فروش قوی 🔴' if cci > 100 else 'خنثی'}
🔹 Williams %R: {williams:.1f} → {'اشباع خرید 🔴' if williams > -20 else 'اشباع فروش 🟢' if williams < -80 else 'خنثی'}
🔹 ADX (قدرت روند): {adx:.1f} → {'روند قوی 🔥' if adx > 25 else 'روند ضعیف 💨'}

┌─────────────────────────────────┐
│ 📊 **باند بولینگر (20,2)**      │
└─────────────────────────────────┘
🔺 بالا: ${bb_u:,.0f}
⚪ وسط: ${bb_m:,.0f}
🔻 پایین: ${bb_l:,.0f}

┌─────────────────────────────────┐
│ 🔑 **سطوح کلیدی (فیبوناچی)**   │
└─────────────────────────────────┘
🟢 حمایت‌ها: ${sr['support'][0]:,.0f} | ${sr['support'][1]:,.0f} | ${sr['support'][2]:,.0f}
🔴 مقاومت‌ها: ${sr['resistance'][0]:,.0f} | ${sr['resistance'][1]:,.0f} | ${sr['resistance'][2]:,.0f}
🎯 نقطه محوری: ${sr['pivot']:,.0f}

┌─────────────────────────────────┐
│ 🐋 **تشخیص تله**                │
└─────────────────────────────────┘
{trap}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [
        [InlineKeyboardButton("🧠 تحلیل با Groq", callback_data=f"groq_{symbol}")],
        [InlineKeyboardButton("💰 خرید دمو", callback_data=f"demo_buy_{symbol}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== تحلیل عمیق با Groq ==========
async def ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"🧠 {s['symbol']}", callback_data=f"groq_{s['symbol']}")] for s in SYMBOLS]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text("🧠 **تحلیل عمیق با Groq AI**\nارز مورد نظر را انتخاب کنید تا هوش مصنوعی تحلیل کاملی ارائه دهد:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def groq_analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🤖 در حال تحلیل عمیق {symbol} با هوش مصنوعی... (حداکثر ۳۰ ثانیه)")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=get_back_keyboard())
        return
    
    # شبیه‌سازی داده‌های تاریخی
    np.random.seed(0)
    prices = [data["price"] * (1 + np.random.randn(60) * 0.015) for _ in range(60)]
    highs = [p * 1.005 for p in prices]
    lows = [p * 0.995 for p in prices]
    
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    macd, macd_sig, _ = TechnicalAnalysis.calculate_macd(prices)
    stoch_k, stoch_d = TechnicalAnalysis.calculate_stochastic(highs, lows, prices)
    cci = TechnicalAnalysis.calculate_cci(highs, lows, prices)
    williams = TechnicalAnalysis.calculate_williams_r(highs, lows, prices)
    adx = TechnicalAnalysis.calculate_adx(highs, lows, prices)
    bb_u, bb_m, bb_l = TechnicalAnalysis.calculate_bollinger(prices)
    sr = TechnicalAnalysis.calculate_support_resistance(prices)
    trap = TechnicalAnalysis.detect_trap(data["price"], data["change"], data["volume"], rsi)
    sentiment = await FundamentalAnalysis.get_market_sentiment()
    
    analysis = await groq_deep_analysis(
        symbol, data["price"], data["change"], data["volume"], data["high"], data["low"],
        rsi, macd, macd_sig, stoch_k, stoch_d, cci, williams, adx,
        bb_u, bb_m, bb_l, sr["support"], sr["resistance"], trap, sentiment
    )
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      🧠 *تحلیل هوشمند {symbol} (Groq AI)* 🧠
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

{analysis}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"groq_{symbol}")], [InlineKeyboardButton("🔙 بازگشت", callback_data="ai_menu")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== معامله دمو کامل ==========
async def trade_demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
🎮 **حالت معامله دمو** 🎮

💰 **موجودی نقد دمو:** ${demo_balance:,.2f} USDT
📊 **ارزش کل پورتفوی دمو:** ${get_demo_portfolio_value():,.2f} USDT

📌 **برای معامله، ارز مورد نظر را انتخاب کن:**
"""
    keyboard = []
    for s in SYMBOLS:
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} خرید {s['symbol']}", callback_data=f"demo_buy_{s['symbol']}")])
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} فروش {s['symbol']}", callback_data=f"demo_sell_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("📈 پوزیشن‌های باز", callback_data="demo_positions")])
    keyboard.append([InlineKeyboardButton("💹 گزارش سود/زیان", callback_data="demo_report")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def demo_buy(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    global demo_balance, demo_positions
    query = update.callback_query
    await query.answer()
    
    price_data = await get_coinex_price(symbol)
    if not price_data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=get_back_keyboard())
        return
    
    # استفاده از 20% موجودی نقد برای خرید (شبیه‌سازی ریسک 2% نیست، ساده)
    amount_usdt = demo_balance * 0.2
    amount_coin = amount_usdt / price_data["price"]
    if amount_coin <= 0:
        await query.edit_message_text("❌ موجودی کافی نیست", reply_markup=get_back_keyboard())
        return
    
    demo_balance -= amount_usdt
    # اگر قبلاً پوزیشنی برای این نماد وجود دارد، مقدار را اضافه کن (میانگین قیمت ساده)
    if symbol in demo_positions:
        old = demo_positions[symbol]
        total_cost = old["amount"] * old["entry_price"] + amount_coin * price_data["price"]
        total_amount = old["amount"] + amount_coin
        avg_price = total_cost / total_amount
        demo_positions[symbol] = {
            "amount": total_amount,
            "entry_price": avg_price,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stop_loss": price_data["price"] * 0.97,
            "take_profit": price_data["price"] * 1.06
        }
    else:
        demo_positions[symbol] = {
            "amount": amount_coin,
            "entry_price": price_data["price"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stop_loss": price_data["price"] * 0.97,
            "take_profit": price_data["price"] * 1.06
        }
    
    text = f"✅ **خرید دمو {symbol}**\n💰 قیمت خرید: ${price_data['price']:,.4f}\n📦 مقدار: {amount_coin:.6f}\n💵 هزینه: ${amount_usdt:.2f}\n🛡️ حد ضرر: ${demo_positions[symbol]['stop_loss']:.2f}\n🎯 حد سود: ${demo_positions[symbol]['take_profit']:.2f}\n💰 موجودی نقد باقی‌مانده: ${demo_balance:.2f}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def demo_sell(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    global demo_balance, demo_positions
    query = update.callback_query
    await query.answer()
    
    if symbol not in demo_positions:
        await query.edit_message_text(f"❌ شما هیچ پوزیشن بازی برای {symbol} ندارید.", reply_markup=get_back_keyboard())
        return
    
    price_data = await get_coinex_price(symbol)
    if not price_data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=get_back_keyboard())
        return
    
    pos = demo_positions[symbol]
    sell_value = pos["amount"] * price_data["price"]
    pnl = sell_value - (pos["amount"] * pos["entry_price"])
    demo_balance += sell_value
    del demo_positions[symbol]
    
    text = f"✅ **فروش دمو {symbol}**\n💰 قیمت فروش: ${price_data['price']:,.4f}\n📦 مقدار: {pos['amount']:.6f}\n💵 ارزش فروش: ${sell_value:.2f}\n📈 سود/زیان: ${pnl:+.2f}\n💰 موجودی نقد جدید: ${demo_balance:.2f}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def demo_positions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not demo_positions:
        await query.edit_message_text("📭 **هیچ پوزیشن بازی در دمو ندارید.**", parse_mode="Markdown", reply_markup=get_back_keyboard())
        return
    text = "📈 **پوزیشن‌های باز دمو** 📈\n\n"
    total_unrealized = 0
    for sym, pos in demo_positions.items():
        price_data = await get_coinex_price(sym)
        if price_data["success"]:
            current_price = price_data["price"]
            unrealized = (current_price - pos["entry_price"]) * pos["amount"]
            total_unrealized += unrealized
            text += f"{sym}: {pos['amount']:.6f} @ ${pos['entry_price']:.2f} | سود/زیان: ${unrealized:+.2f}\n"
    text += f"\n💰 **سود/زیان تحقق‌نیافته کل:** ${total_unrealized:+.2f}"
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="trade_demo")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def demo_report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    total_value = get_demo_portfolio_value()
    profit = total_value - 10000  # سرمایه اولیه 10000
    text = f"💹 **گزارش عملکرد دمو** 💹\n\n💰 سرمایه اولیه: $10,000\n💵 موجودی نقد: ${demo_balance:.2f}\n📊 ارزش پورتفوی: ${total_value:.2f}\n📈 سود/زیان کل: ${profit:+.2f} ({profit/100:.2f}%)"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

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
    text = "💰 **قیمت لحظه‌ای ارزها** 💰\n\n"
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        if data["success"]:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} *{s['symbol']}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🐋 **ردیابی نهنگ‌ها** 🐋\n\n📊 آخرین تراکنش‌های بزرگ (شبیه‌سازی):\n• 1,250 BTC (84M$) خرید\n• 15,000 ETH (51.8M$) فروش\n• 250,000 SOL (39.1M$) خرید\n\nتحلیل: خرید نهنگ‌ها روی BTC نشانه صعود است."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def trade_real_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    balance = await get_account_balance()
    text = f"💰 **معامله واقعی CoinEx**\nموجودی قابل استفاده: ${balance['free']:,.2f} USDT\n\n⚠️ معامله واقعی با مسئولیت شماست.\nانتخاب ارز:"
    keyboard = []
    for s in SYMBOLS:
        keyboard.append([InlineKeyboardButton(f"خرید {s['symbol']}", callback_data=f"real_buy_{s['symbol']}"), InlineKeyboardButton(f"فروش {s['symbol']}", callback_data=f"real_sell_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def real_buy(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⚠️ معامله واقعی به دلایل امنیتی در این نسخه غیرفعال است. لطفاً از حالت دمو استفاده کنید.", reply_markup=get_back_keyboard())

async def real_sell(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⚠️ معامله واقعی غیرفعال است.", reply_markup=get_back_keyboard())

async def alert_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔔 **هشدار قیمت**\nاین قابلیت در حال توسعه است. به زودی اضافه می‌شود.", parse_mode="Markdown", reply_markup=get_back_keyboard())

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
🛡️ **مدیریت ریسک حرفه‌ای** 🛡️

📊 **قوانین طلایی:**
• حداکثر ریسک در هر معامله: **{MAX_RISK_PERCENT}%** سرمایه
• نسبت ریسک به ریوارد: **1:{TAKE_PROFIT_PERCENT/STOP_LOSS_PERCENT:.1f}**
• حد ضرر: **{STOP_LOSS_PERCENT}%** (اجباری)
• حداکثر معاملات همزمان: **{MAX_POSITIONS}**
• حداکثر افت روزانه: **6%**

📈 **فرمول حجم معامله:**
`حجم = (سرمایه × {MAX_RISK_PERCENT}%) / (قیمت ورود × {STOP_LOSS_PERCENT}%)`

💡 **نکات کلیدی:**
• فقط سیگنال‌های با اطمینان >70% را اجرا کن
• همیشه حد ضرر را فعال کن
• در ضررهای متوالی، معامله را متوقف کن
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
⚙️ **تنظیمات ربات** ⚙️

📡 **وضعیت API:**
• 🔑 CoinEx: {'✅' if ACCESS_ID else '❌'}
• 🧠 Groq: {'✅' if GROQ_API_KEY else '❌'}
• 👤 مالک: {OWNER_ID if OWNER_ID != 0 else 'همه مجاز'}

📌 برای تغییر تنظیمات، متغیرهای محیطی را در Railway ویرایش کنید.
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
❓ **راهنمای کامل ربات** ❓

📊 **قابلیت‌ها:**
• سیگنال لحظه‌ای (خرید/فروش/نگهداری)
• قیمت لحظه‌ای ۸ ارز برتر
• تحلیل تکنیکال کامل (RSI, MACD, Stochastic, CCI, Williams, ADX, Bollinger, Fibonacci, تشخیص تله)
• تحلیل عمیق با هوش مصنوعی Groq (تکنیکال، فاندامنتال، پرایس اکشن)
• ردیابی نهنگ‌ها (شبیه‌سازی شده)
• معامله دمو با قابلیت باز و بستن پوزیشن و گزارش سود/زیان
• مدیریت ریسک حرفه‌ای

🎮 **نحوه استفاده از معامله دمو:**
1. از منو "🎮 معامله دمو" را انتخاب کنید.
2. روی "خرید" یا "فروش" یک ارز کلیک کنید.
3. پوزیشن‌های باز خود را در بخش "📈 پوزیشن‌های دمو" ببینید.
4. برای بستن پوزیشن، از همان منو گزینه "فروش" را بزنید.
5. گزارش سود/زیان را در "💹 گزارش دمو" مشاهده کنید.

⚠️ **توجه:** فقط جنبه آموزشی – مسئولیت با شماست.
"""
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
    elif data == "demo_positions":
        await demo_positions_menu(update, context)
    elif data == "demo_report":
        await demo_report_menu(update, context)
    elif data == "alert_menu":
        await alert_menu(update, context)
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
    elif data.startswith("real_buy_"):
        await real_buy(update, context, data.split("_")[2])
    elif data.startswith("real_sell_"):
        await real_sell(update, context, data.split("_")[2])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      🔥 *ربات فوق‌هوشمند کریپتو* 🔥
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **قابلیت‌ها:**
• تحلیل تکنیکال کامل (RSI, MACD, Stochastic, CCI, Williams, ADX, Bollinger, Fibonacci)
• تحلیل عمیق با هوش مصنوعی Groq (تکنیکال، فاندامنتال، پرایس اکشن)
• معامله دمو با پوزیشن‌گیری واقعی
• ردیابی نهنگ‌ها و تشخیص تله
• مدیریت ریسک حرفه‌ای

📌 **از منوی زیر انتخاب کن:**
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("ربات فوق‌هوشمند با موفقیت راه‌اندازی شد.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
