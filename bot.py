import os
import logging
import hashlib
import hmac
import time
import json
import httpx
import asyncio
import numpy as np
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========== اصلاح خط ۱۹ ==========
owner_id_str = os.getenv("OWNER_ID", "0")
OWNER_ID = int(owner_id_str) if owner_id_str and owner_id_str.strip().isdigit() else 0
# =================================

# ========== تنظیمات CoinEx ==========
ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")

# ========== تنظیمات معاملاتی ==========
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

# ========== چک دسترسی ==========
async def is_owner(update: Update) -> bool:
    if OWNER_ID == 0:
        return True
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی به این ربات را ندارید.")
        return False
    return True

# ========== API CoinEx ==========
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
    body = {
        "market": symbol,
        "market_type": "SPOT",
        "side": side,
        "order_type": order_type,
        "amount": str(amount)
    }
    if price and order_type == "limit":
        body["price"] = str(price)
    return await coinex_request("POST", "/order/limit", body)

# ========== تحلیل تکنیکال کامل ==========
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
            return {"type": "BULL_TRAP", "message": "⚠️ تله گاوی! رشد ناگهانی با حجم بالا و RSI اشباع", "risk": "HIGH"}
        elif change < -3 and volume > 10000000 and rsi < 30:
            return {"type": "BEAR_TRAP", "message": "⚠️ تله خرسی! ریزش ناگهانی با حجم بالا و RSI اشباع فروش", "risk": "HIGH"}
        return {"type": "NONE", "message": "✅ بدون تله", "risk": "LOW"}

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
                    return {"sentiment": fng.get("value_classification", "Neutral"), "value": int(fng.get("value", 50)), "source": "Alternative.me"}
        except:
            pass
        return {"sentiment": "Neutral", "value": 50, "source": "Estimated"}

# ========== هوش مصنوعی Groq ==========
async def groq_full_analysis(symbol, price, change, volume, high, low, rsi, macd, macd_signal, stoch_k, stoch_d, cci, williams_r, adx, bb_upper, bb_middle, bb_lower, support, resistance, trap, sentiment):
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است. لطفاً GROQ_API_KEY را در Railway اضافه کنید."
    prompt = f"""به عنوان یک تحلیلگر حرفه‌ای بازار کریپتو با دقت بالا، {symbol} را مو به مو تحلیل کن:

📊 **داده‌های لحظه‌ای:**
- قیمت: ${price:,.0f}
- تغییر 24h: {change:+.2f}%
- حجم 24h: ${volume/1e6:.2f}M
- بالاترین: ${high:,.0f}
- پایین‌ترین: ${low:,.0f}

📈 **اندیکاتورها و اسیلاتورها:**
- RSI(14): {rsi:.1f}
- MACD: {macd:.2f} (سیگنال: {macd_signal:.2f})
- Stochastic K/D: {stoch_k:.1f} / {stoch_d:.1f}
- CCI: {cci:.1f}
- Williams %R: {williams_r:.1f}
- ADX (قدرت روند): {adx:.1f}
- باند بولینگر: بالا ${bb_upper:,.0f}, وسط ${bb_middle:,.0f}, پایین ${bb_lower:,.0f}

🔑 **سطوح کلیدی:**
- حمایت‌ها: {support['support'][0]:,.0f}, {support['support'][1]:,.0f}, {support['support'][2]:,.0f}
- مقاومت‌ها: {resistance['resistance'][0]:,.0f}, {resistance['resistance'][1]:,.0f}, {resistance['resistance'][2]:,.0f}
- نقطه محوری: {support['pivot']:,.0f}

⚠️ **تشخیص تله:**
{trap['message']}

📊 **احساسات بازار:**
- شاخص ترس و طمع: {sentiment['value']}/100 ({sentiment['sentiment']})

**تحلیل کامل بنویس شامل:**
1. وضعیت روند (صعودی/نزولی/رنج) و قدرت آن
2. سیگنال‌های خرید/فروش از هر اندیکاتور
3. نقاط ورود و خروج پیشنهادی (با قیمت)
4. مدیریت ریسک (حد ضرر و حد سود)
5. پیش‌بینی کوتاه مدت (12-24 ساعت)
6. توصیه نهایی (BUY/SELL/HOLD) با درصد اطمینان

پاسخ را به صورت حرفه‌ای و مفصل بنویس."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return "خطا در ارتباط با هوش مصنوعی. لطفاً دوباره تلاش کنید."

# ========== تولید نمودار متنی ساده ==========
def generate_text_chart(price, support, resistance):
    width = 20
    price_pos = int((price - support) / (resistance - support) * width) if resistance != support else width//2
    chart = "```\n"
    chart += "مقاومت ↑ " + "─" * width + "\n"
    chart += " " * (price_pos + 6) + "● قیمت\n" if price_pos >=0 else ""
    chart += "حمایت   ↓ " + "─" * width + "\n"
    chart += "```"
    return chart

# ========== دکمه‌ها ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ سیگنال لحظه‌ای", callback_data="signals")],
        [InlineKeyboardButton("📊 قیمت ارزها", callback_data="prices")],
        [InlineKeyboardButton("🎯 تحلیل تکنیکال کامل", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل هوشمند Groq", callback_data="ai_menu")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale")],
        [InlineKeyboardButton("💰 معامله (واقعی)", callback_data="trade_real")],
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
demo_positions = {}

async def trade_demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
🎮 **حالت دمو (آموزشی)** 🎮

💰 **موجودی دمو:** ${demo_balance:,.2f} USDT

📌 برای معامله دمو، ارز مورد نظر را انتخاب کن:
"""
    keyboard = []
    for s in SYMBOLS:
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} خرید {s['symbol']}", callback_data=f"demo_buy_{s['symbol']}")])
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} فروش {s['symbol']}", callback_data=f"demo_sell_{s['symbol']}")])
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
    await query.edit_message_text(f"✅ **خرید دمو {symbol}**\n💰 قیمت: ${price_data['price']:,.4f}\n📦 مقدار: {amount:.6f}\n💵 باقی‌مانده: ${demo_balance:,.2f}", parse_mode="Markdown", reply_markup=get_back_keyboard())

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
    await query.edit_message_text(f"✅ **فروش دمو {symbol}**\n💰 قیمت: ${price_data['price']:,.4f}\n💵 موجودی جدید: ${demo_balance:,.2f}", parse_mode="Markdown", reply_markup=get_back_keyboard())

# ========== هندلر تحلیل تکنیکال کامل ==========
async def technical_full_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for s in SYMBOLS:
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} {s['symbol']}", callback_data=f"tech_full_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n📊 *تحلیل تکنیکال کامل (مو به مو)*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\nارز مورد نظر را انتخاب کن:"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_full_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 در حال تحلیل کامل {symbol}...")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text(f"❌ خطا در تحلیل {symbol}", reply_markup=get_back_keyboard())
        return
    
    # شبیه‌سازی داده‌های تاریخی
    base_price = data["price"]
    np.random.seed(0)
    prices = [base_price * (1 + np.random.randn(50) * 0.015)]
    highs = [p * 1.005 for p in prices]
    lows = [p * 0.995 for p in prices]
    closes = prices
    
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    macd, macd_signal, macd_hist = TechnicalAnalysis.calculate_macd(prices)
    stoch_k, stoch_d = TechnicalAnalysis.calculate_stochastic(highs, lows, closes)
    cci = TechnicalAnalysis.calculate_cci(highs, lows, closes)
    williams_r = TechnicalAnalysis.calculate_williams_r(highs, lows, closes)
    adx = TechnicalAnalysis.calculate_adx(highs, lows, closes)
    bb_upper, bb_middle, bb_lower = TechnicalAnalysis.calculate_bollinger(prices)
    sr = TechnicalAnalysis.calculate_support_resistance(prices)
    trap = TechnicalAnalysis.detect_trap(data["price"], data["change"], data["volume"], rsi)
    
    chart = generate_text_chart(data["price"], sr["support"][0], sr["resistance"][0])
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      📊 *تحلیل کامل تکنیکال {symbol}* 📊
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

💰 **قیمت لحظه‌ای:** ${data['price']:,.4f}
📈 **تغییر 24h:** {data['change']:+.2f}%
📊 **حجم 24h:** ${data['volume']/1e6:.2f}M
📈 **بالاترین 24h:** ${data['high']:,.4f}
📉 **پایین‌ترین 24h:** ${data['low']:,.4f}

┌─────────────────────────────────┐
│ 📊 **اندیکاتورها و اسیلاتورها** │
└─────────────────────────────────┘
🟢 **RSI(14):** {rsi:.1f} → {'اشباع خرید' if rsi > 70 else 'اشباع فروش' if rsi < 30 else 'خنثی'}
🟡 **MACD:** {macd:.2f} (سیگنال: {macd_signal:.2f}) → {'صعودی' if macd > macd_signal else 'نزولی'}
🔵 **Stochastic K/D:** {stoch_k:.1f} / {stoch_d:.1f}
🟠 **CCI:** {cci:.1f} → {'خرید قوی' if cci < -100 else 'فروش قوی' if cci > 100 else 'خنثی'}
🟣 **Williams %R:** {williams_r:.1f} → {'اشباع خرید' if williams_r > -20 else 'اشباع فروش' if williams_r < -80 else 'خنثی'}
🔺 **ADX (قدرت روند):** {adx:.1f} → {'روند قوی' if adx > 25 else 'روند ضعیف'}

┌─────────────────────────────────┐
│ 📈 **باند بولینگر (20,2)**      │
└─────────────────────────────────┘
🔼 بالا: ${bb_upper:,.4f}
⚪ وسط: ${bb_middle:,.4f}
🔽 پایین: ${bb_lower:,.4f}

┌─────────────────────────────────┐
│ 🔑 **سطوح کلیدی (فیبوناچی)**   │
└─────────────────────────────────┘
🟢 حمایت‌ها: ${sr['support'][0]:,.2f} | ${sr['support'][1]:,.2f} | ${sr['support'][2]:,.2f}
🔴 مقاومت‌ها: ${sr['resistance'][0]:,.2f} | ${sr['resistance'][1]:,.2f} | ${sr['resistance'][2]:,.2f}
🎯 نقطه محوری: ${sr['pivot']:,.2f}

┌─────────────────────────────────┐
│ 🐋 **تشخیص تله**                │
└─────────────────────────────────┘
{trap['message']}

📊 **نمودار قیمت:**
{chart}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🧠 تحلیل هوشمند", callback_data=f"groq_{symbol}")], [InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"tech_full_{symbol}")], [InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== تحلیل هوشمند Groq ==========
async def groq_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for s in SYMBOLS:
        keyboard.append([InlineKeyboardButton(f"🧠 {s['symbol']} (تحلیل AI)", callback_data=f"groq_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n🧠 *تحلیل هوشمند با Groq AI*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\nارز مورد نظر را انتخاب کن تا هوش مصنوعی مو به مو تحلیل کند:"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def groq_analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🤖 در حال تحلیل {symbol} با هوش مصنوعی... (لطفاً صبر کنید)")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text(f"❌ خطا در دریافت قیمت {symbol}", reply_markup=get_back_keyboard())
        return
    
    base_price = data["price"]
    np.random.seed(0)
    prices = [base_price * (1 + np.random.randn(50) * 0.015)]
    highs = [p * 1.005 for p in prices]
    lows = [p * 0.995 for p in prices]
    closes = prices
    
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    macd, macd_signal, _ = TechnicalAnalysis.calculate_macd(prices)
    stoch_k, stoch_d = TechnicalAnalysis.calculate_stochastic(highs, lows, closes)
    cci = TechnicalAnalysis.calculate_cci(highs, lows, closes)
    williams_r = TechnicalAnalysis.calculate_williams_r(highs, lows, closes)
    adx = TechnicalAnalysis.calculate_adx(highs, lows, closes)
    bb_upper, bb_middle, bb_lower = TechnicalAnalysis.calculate_bollinger(prices)
    sr = TechnicalAnalysis.calculate_support_resistance(prices)
    trap = TechnicalAnalysis.detect_trap(data["price"], data["change"], data["volume"], rsi)
    sentiment = await FundamentalAnalysis.get_market_sentiment()
    
    analysis = await groq_full_analysis(symbol, data["price"], data["change"], data["volume"], data["high"], data["low"], rsi, macd, macd_signal, stoch_k, stoch_d, cci, williams_r, adx, bb_upper, bb_middle, bb_lower, sr, sr, trap, sentiment)
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      🧠 *تحلیل هوشمند {symbol} (Groq AI)* 🧠
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

{analysis}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"groq_{symbol}")], [InlineKeyboardButton("🔙 بازگشت", callback_data="ai_menu")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== سایر منوها ==========
async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت سیگنال‌ها...")
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n📡 *سیگنال‌های لحظه‌ای*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n"
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
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n💰 *قیمت لحظه‌ای*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n"
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        if data["success"]:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} *{s['symbol']}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n🐋 *ردیابی نهنگ‌ها*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n📊 آخرین تراکنش‌های بزرگ:\n• 1,250 BTC (84M$) خرید\n• 15,000 ETH (51.8M$) فروش\n• 250,000 SOL (39.1M$) خرید\n\nتحلیل: خرید نهنگ‌ها روی BTC نشانه صعود است."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def trade_real_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    balance = await get_account_balance()
    text = f"✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n💰 *معامله واقعی (CoinEx)*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\nموجودی قابل استفاده: ${balance['free']:,.2f} USDT\n\n⚠️ توجه: این معامله واقعی است. با احتیاط انجام دهید.\n\nبرای معامله، ارز مورد نظر را انتخاب کن:"
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
    await query.edit_message_text(f"⚠️ در حالت واقعی، سفارش خرید {symbol} به مبلغ ${amount * price_data['price']:.2f} ثبت خواهد شد. (برای امنیت، غیرفعال است)", reply_markup=get_back_keyboard())

async def real_sell(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"⚠️ در حالت واقعی، سفارش فروش {symbol} ثبت خواهد شد. (برای امنیت، غیرفعال است)", reply_markup=get_back_keyboard())

async def positions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n📈 *پوزیشن‌های باز*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\nهیچ پوزیشن بازی وجود ندارد."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n🛡️ *مدیریت ریسک*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n📊 قوانین طلایی:\n1️⃣ حداکثر ریسک: {MAX_RISK_PERCENT}% سرمایه\n2️⃣ نسبت R/R: 1:{TAKE_PROFIT_PERCENT/STOP_LOSS_PERCENT:.1f}\n3️⃣ حد ضرر: {STOP_LOSS_PERCENT}% اجباری\n4️⃣ حداکثر پوزیشن: {MAX_POSITIONS}\n\n📈 فرمول حجم معامله:\nحجم = (سرمایه × {MAX_RISK_PERCENT}%) / (قیمت × {STOP_LOSS_PERCENT}%)"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n⚙️ *تنظیمات*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n📡 وضعیت API:\n🔑 Access ID: {'✅' if ACCESS_ID else '❌'}\n🔒 Secret Key: {'✅' if SECRET_KEY else '❌'}\n🧠 Groq API: {'✅' if GROQ_API_KEY else '❌'}\n\n👤 مالک ربات: {OWNER_ID if OWNER_ID != 0 else 'تنظیم نشده (همه مجاز)'}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n❓ *راهنما*\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n📊 سیگنال‌ها: خرید/فروش بر اساس تغییر قیمت\n🎯 تحلیل تکنیکال کامل: RSI, MACD, Stochastic, CCI, Williams, ADX, Bollinger, سطوح فیبوناچی، تشخیص تله، نمودار ساده\n🧠 تحلیل هوشمند Groq: تحلیل مو به مو با AI\n🐋 ردیابی نهنگ‌ها\n💰 معامله واقعی و دمو\n🛡️ مدیریت ریسک\n\n⚠️ فقط جنبه آموزشی – مسئولیت با شماست"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back":
        await back_handler(update, context)
    elif data == "signals":
        await signals_menu(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "technical":
        await technical_full_menu(update, context)
    elif data == "ai_menu":
        await groq_menu(update, context)
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
    elif data.startswith("tech_full_"):
        await technical_full_analysis(update, context, data.split("_")[2])
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
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n🔥 *ربات حرفه‌ای کریپتو* 🔥\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n🔹 تحلیل تکنیکال کامل (RSI, MACD, Stochastic, CCI, Williams, ADX, Bollinger, Fibonacci)\n🔹 تحلیل هوشمند با Groq AI\n🔹 ردیابی نهنگ‌ها و تشخیص تله\n🔹 معامله واقعی و دمو\n🔹 مدیریت ریسک حرفه‌ای\n\n📌 از منوی زیر انتخاب کن"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    await update.message.reply_text("✨ لطفاً از دکمه‌های منو استفاده کن یا /start بزن")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 ربات حرفه‌ای کریپتو روشن شد...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
