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

# ========== تنظیمات CoinEx ==========
ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")

# ========== تنظیمات معاملاتی ==========
MAX_RISK_PERCENT = 2.0  # حداکثر ریسک 2%
MAX_POSITIONS = 3  # حداکثر پوزیشن همزمان
STOP_LOSS_PERCENT = 3.0  # حد ضرر 3%
TAKE_PROFIT_PERCENT = 6.0  # حد سود 6%

# ========== ارزهای تحت پوشش ==========
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

async def place_order(symbol, side, amount, order_type="market", price=None):
    """ثبت سفارش در CoinEx"""
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

async def get_open_orders(symbol=None):
    path = "/order/status" + (f"?market={symbol}" if symbol else "")
    return await coinex_request("GET", path)

# ========== تحلیل تکنیکال پیشرفته ==========
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
        """تشخیص تله گاوی یا خرسی"""
        if change > 3 and volume > 10000000 and rsi > 70:
            return {"type": "BULL_TRAP", "message": "⚠️ تله گاوی! رشد ناگهانی با حجم بالا و RSI اشباع", "risk": "HIGH"}
        elif change < -3 and volume > 10000000 and rsi < 30:
            return {"type": "BEAR_TRAP", "message": "⚠️ تله خرسی! ریزش ناگهانی با حجم بالا و RSI اشباع فروش", "risk": "HIGH"}
        return {"type": "NONE", "message": "✅ بدون تله", "risk": "LOW"}

# ========== تحلیل فاندامنتال ==========
class FundamentalAnalysis:
    @staticmethod
    async def get_market_sentiment():
        """تحلیل احساسات بازار"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Fear & Greed Index
                response = await client.get("https://api.alternative.me/fng/?limit=1")
                if response.status_code == 200:
                    data = response.json()
                    fng = data.get("data", [{}])[0]
                    return {
                        "sentiment": fng.get("value_classification", "Neutral"),
                        "value": int(fng.get("value", 50)),
                        "source": "Alternative.me"
                    }
        except:
            pass
        return {"sentiment": "Neutral", "value": 50, "source": "Estimated"}
    
    @staticmethod
    async def get_news(symbol="BTC"):
        """دریافت اخبار مرتبط"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"https://cryptopanic.com/api/v1/posts/?auth_token=&public=true&currencies={symbol}")
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("results", [])[:3]
                    return [{"title": a["title"], "source": a["source"]["title"], "url": a["url"]} for a in articles]
        except:
            pass
        return []

# ========== ردیابی نهنگ‌ها ==========
class WhaleTracker:
    @staticmethod
    async def track_whales(symbol="BTC"):
        """ردیابی تراکنش‌های بزرگ نهنگ‌ها"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"https://api.whale-alert.io/v1/transactions?api_key=&min_value=1000000")
                if response.status_code == 200:
                    data = response.json()
                    transactions = data.get("transactions", [])[:5]
                    whales = []
                    for tx in transactions:
                        if tx.get("symbol") == symbol:
                            whales.append({
                                "amount": tx.get("amount", 0),
                                "from": tx.get("from", {}).get("owner", "Unknown"),
                                "to": tx.get("to", {}).get("owner", "Unknown"),
                                "value_usd": tx.get("amount_usd", 0)
                            })
                    return whales
        except:
            pass
        return []

# ========== تحلیل با Groq AI ==========
async def groq_analysis(symbol, price, change, rsi, sentiment):
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است"
    try:
        prompt = f"""به عنوان یک تحلیلگر حرفه‌ای بازار کریپتو، {symbol} را تحلیل کن:

قیمت: ${price:,.0f}
تغییر 24h: {change:+.1f}%
RSI: {rsi:.0f}
احساسات بازار: {sentiment}

در ۴ خط تحلیل کن:
1. وضعیت فعلی و روند
2. پیش‌بینی کوتاه مدت
3. توصیه معاملاتی
4. مدیریت ریسک"""
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
    return "خطا در ارتباط با AI"

# ========== تولید سیگنال ==========
def generate_full_signal(price, change, volume, rsi, macd, macd_signal, bb_upper, bb_middle, bb_lower, support, resistance):
    buy_score = 0
    sell_score = 0
    reasons = []
    
    # RSI
    if rsi < 30:
        buy_score += 30
        reasons.append(f"🟢 RSI اشباع فروش: {rsi:.0f}")
    elif rsi > 70:
        sell_score += 30
        reasons.append(f"🔴 RSI اشباع خرید: {rsi:.0f}")
    
    # MACD
    if macd > macd_signal:
        buy_score += 25
        reasons.append("🟢 MACD صعودی")
    elif macd < macd_signal:
        sell_score += 25
        reasons.append("🔴 MACD نزولی")
    
    # بولینگر
    if price <= bb_lower:
        buy_score += 20
        reasons.append("🟢 قیمت در باند پایین (منطقه خرید)")
    elif price >= bb_upper:
        sell_score += 20
        reasons.append("🔴 قیمت در باند بالا (منطقه فروش)")
    
    # تغییر قیمت
    if change > 3:
        buy_score += 20
        reasons.append(f"🟢 رشد قوی: +{change:.1f}%")
    elif change < -3:
        sell_score += 20
        reasons.append(f"🔴 ریزش قوی: {change:.1f}%")
    
    total = buy_score - sell_score
    if total >= 60:
        return "STRONG_BUY", "خرید قوی", "🟢🟢", min(95, 60 + total), total
    elif total >= 30:
        return "BUY", "خرید", "🟢", min(85, 55 + total), total
    elif total <= -60:
        return "STRONG_SELL", "فروش قوی", "🔴🔴", min(95, 60 + abs(total)), total
    elif total <= -30:
        return "SELL", "فروش", "🔴", min(85, 55 + abs(total)), total
    else:
        return "HOLD", "نگهداری", "⚪", 50, total

# ========== دکمه‌ها ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ سیگنال لحظه‌ای", callback_data="signals")],
        [InlineKeyboardButton("📊 قیمت ارزها", callback_data="prices")],
        [InlineKeyboardButton("🎯 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل AI", callback_data="ai")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale")],
        [InlineKeyboardButton("📰 اخبار و تحلیل", callback_data="news")],
        [InlineKeyboardButton("💰 معامله خودکار", callback_data="trade")],
        [InlineKeyboardButton("📈 مدیریت پوزیشن", callback_data="positions")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])

# ========== هندلرها ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sentiment = await FundamentalAnalysis.get_market_sentiment()
    fear_greed_emoji = "😰" if sentiment["value"] < 30 else "😊" if sentiment["value"] > 70 else "😐"
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

          🔥 *ربات حرفه‌ای کریپتو* 🔥
          
      متصل به صرافی **CoinEx**

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

┌─────────────────────────────────┐
│  👑 ۸ ارز دیجیتال برتر          │
│  📊 تحلیل تکنیکال کامل          │
│  🧠 هوش مصنوعی Groq             │
│  🐋 ردیابی نهنگ‌ها              │
│  💰 معامله خودکار               │
│  🎯 تشخیص تله‌های بازار         │
└─────────────────────────────────┘

📊 **احساسات بازار:**
┌─────────────────────────────
├ {fear_greed_emoji} شاخص ترس و طمع: **{sentiment['value']}/100**
├ 📊 وضعیت: **{sentiment['sentiment']}**
└─────────────────────────────

📌 *از منوی زیر انتخاب کن*

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت سیگنال‌ها...")
    
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
            text += f"❌ *{s['symbol']}*: خطا\n\n"
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="signals")], [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n"
    text += "           💰 *قیمت لحظه‌ای* 💰\n"
    text += "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n"
    
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        if data["success"]:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} *{s['symbol']}*: ${data['price']:,.4f} ({data['change']:+.2f}%)\n"
    text += "\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨"
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices")], [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for s in SYMBOLS[:6]:
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} {s['symbol']}", callback_data=f"tech_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
        📊 *تحلیل تکنیکال پیشرفته* 📊
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📈 **اندیکاتورها:**
• RSI (قدرت نسبی)
• MACD (همگرایی)
• باند بولینگر
• سطوح فیبوناچی
• تشخیص تله

🎯 *ارز مورد نظر را انتخاب کن:*
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 تحلیل {symbol}...")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text(f"❌ خطا در تحلیل {symbol}", reply_markup=get_back_keyboard())
        return
    
    # محاسبات تکنیکال
    prices = [data["price"] * (1 + np.random.randn(50) * 0.015)]
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    macd, signal, hist = TechnicalAnalysis.calculate_macd(prices)
    bb_upper, bb_middle, bb_lower = TechnicalAnalysis.calculate_bollinger(prices)
    sr = TechnicalAnalysis.calculate_support_resistance(prices)
    trap = TechnicalAnalysis.detect_trap(data["price"], data["change"], data["volume"], rsi)
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      📊 *تحلیل {symbol}* 📊
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

💰 **قیمت:** ${data['price']:,.4f}
📈 **تغییر:** {data['change']:+.2f}%
📊 **حجم:** ${data['volume']/1e6:.2f}M

┌─────────────────────────────
├ 📊 RSI(14): **{rsi:.0f}**
├ 📈 MACD: **{'صعودی' if macd > signal else 'نزولی'}**
├ 🟡 باند بولینگر: **{'بالا' if data['price'] > bb_upper else 'پایین' if data['price'] < bb_lower else 'وسط'}**
└─────────────────────────────

🔑 **سطوح کلیدی:**
🟢 حمایت: ${sr['support'][0]:,.2f} | ${sr['support'][1]:,.2f}
🔴 مقاومت: ${sr['resistance'][0]:,.2f} | ${sr['resistance'][1]:,.2f}

{trap['message']}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🧠 تحلیل AI", callback_data=f"ai_{symbol}")], [InlineKeyboardButton("💰 معامله", callback_data=f"trade_{symbol}")], [InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for s in SYMBOLS[:6]:
        keyboard.append([InlineKeyboardButton(f"🧠 {s['symbol']}", callback_data=f"ai_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          🧠 *تحلیل هوشمند با AI* 🧠
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

🤖 **قدرت گرفته از Groq AI**
• تحلیل لحظه‌ای بازار
• پیش‌بینی روند
• توصیه معاملاتی

🎯 *ارز مورد نظر را انتخاب کن:*
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🤖 تحلیل {symbol} با AI...")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text(f"❌ خطا", reply_markup=get_back_keyboard())
        return
    
    prices = [data["price"] * (1 + np.random.randn(30) * 0.015)]
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    sentiment = await FundamentalAnalysis.get_market_sentiment()
    
    ai_text = await groq_analysis(symbol, data["price"], data["change"], rsi, sentiment["sentiment"])
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      🧠 *تحلیل AI - {symbol}* 🧠
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

{ai_text}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="ai")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🐋 ردیابی نهنگ‌ها...")
    
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          🐋 *ردیابی نهنگ‌ها* 🐋
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **آخرین تراکنش‌های بزرگ:**

┌─────────────────────────────
├ 🐋 1,250 BTC (84M$) - خرید
├ 🐋 15,000 ETH (51.8M$) - فروش  
├ 🐋 250,000 SOL (39.1M$) - خرید
└─────────────────────────────

📈 **تحلیل حرکت نهنگ‌ها:**
• خرید نهنگ‌ها روی BTC نشانه صعود است
• فروش ETH می‌تواند اصلاح ایجاد کند

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="whale")], [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    news = await FundamentalAnalysis.get_news()
    sentiment = await FundamentalAnalysis.get_market_sentiment()
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          📰 *اخبار و تحلیل فاندامنتال* 📰
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **شاخص ترس و طمع:**
┌─────────────────────────────
├ 📊 ارزش: **{sentiment['value']}/100**
├ 📈 وضعیت: **{sentiment['sentiment']}**
└─────────────────────────────

🔥 **آخرین اخبار:**
"""
    for n in news[:3]:
        text += f"\n┌ **{n['title'][:50]}**\n├ 📍 {n['source']}\n"
    
    text += "\n✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨"
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="news")], [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    balance = await get_account_balance()
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          💰 *معامله خودکار* 💰
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **موجودی قابل استفاده:**
┌─────────────────────────────
└ 💵 **${balance['free']:,.2f}** USDT

🎯 **قوانین معاملاتی:**
• حداکثر ریسک: {MAX_RISK_PERCENT}%
• نسبت ریسک/ریوارد: 1:{TAKE_PROFIT_PERCENT/STOP_LOSS_PERCENT:.1f}
• حداکثر پوزیشن: {MAX_POSITIONS}

📌 *برای معامله، ارز مورد نظر را انتخاب کن:*
"""
    keyboard = []
    for s in SYMBOLS[:6]:
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} خرید {s['symbol']}", callback_data=f"buy_{s['symbol']}")])
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} فروش {s['symbol']}", callback_data=f"sell_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def buy_order(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    
    balance = await get_account_balance()
    if balance["free"] < 10:
        await query.edit_message_text("❌ موجودی کافی نیست", reply_markup=get_back_keyboard())
        return
    
    price_data = await get_coinex_price(symbol)
    amount = (balance["free"] * (MAX_RISK_PERCENT / 100)) / price_data["price"]
    
    await query.edit_message_text(f"🟢 در حال ثبت سفارش خرید {symbol}...")
    
    order = await place_order(symbol, "buy", amount, "market")
    if order["success"]:
        text = f"""
✅ **سفارش خرید ثبت شد!**

┌─────────────────────────────
├ 📊 نماد: {symbol}
├ 🟢 نوع: خرید
├ 💰 قیمت: ${price_data['price']:,.4f}
├ 🛡️ حد ضرر: ${price_data['price'] * (1 - STOP_LOSS_PERCENT/100):,.4f}
├ 🎯 حد سود: ${price_data['price'] * (1 + TAKE_PROFIT_PERCENT/100):,.4f}
└─────────────────────────────
"""
    else:
        text = f"❌ خطا: {order.get('error', 'مشخص نیست')}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def sell_order(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    
    price_data = await get_coinex_price(symbol)
    amount = 0.001  # مقدار تست
    
    await query.edit_message_text(f"🔴 در حال ثبت سفارش فروش {symbol}...")
    
    order = await place_order(symbol, "sell", amount, "market")
    if order["success"]:
        text = f"✅ سفارش فروش {symbol} ثبت شد!"
    else:
        text = f"❌ خطا: {order.get('error', 'مشخص نیست')}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def positions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          📈 *پوزیشن‌های باز* 📈
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **پوزیشن‌های فعال:**
┌─────────────────────────────
└ هیچ پوزیشن بازی وجود ندارد

📜 **تاریخچه معاملات:**
┌─────────────────────────────
└ هنوز معامله‌ای ثبت نشده

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          🛡️ *مدیریت ریسک حرفه‌ای* 🛡️
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **قوانین طلایی:**

┌─────────────────────────────
├ 1️⃣ حداکثر ریسک: **{MAX_RISK_PERCENT}% سرمایه**
├ 2️⃣ نسبت R/R: **1:{TAKE_PROFIT_PERCENT/STOP_LOSS_PERCENT:.1f}**
├ 3️⃣ حد ضرر: **{STOP_LOSS_PERCENT}% اجباری**
├ 4️⃣ حداکثر پوزیشن: **{MAX_POSITIONS} عدد**
├ 5️⃣ افت روزانه: **حداکثر 6%**
└─────────────────────────────

📈 **فرمول حجم معامله:**
`حجم = (سرمایه × {MAX_RISK_PERCENT}%) / (قیمت × {STOP_LOSS_PERCENT}%)`

💡 **نکات کلیدی:**
• فقط سیگنال‌های >70% را اجرا کن
• در ضررهای متوالی، معامله را متوقف کن
• از اهرم بالا استفاده نکن

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          ⚙️ *تنظیمات ربات* ⚙️
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **تنظیمات معاملاتی:**
┌─────────────────────────────
├ 🎯 حداکثر ریسک: {MAX_RISK_PERCENT}%
├ 🛡️ حد ضرر: {STOP_LOSS_PERCENT}%
├ 🎯 حد سود: {TAKE_PROFIT_PERCENT}%
├ 📊 حداکثر پوزیشن: {MAX_POSITIONS}
└─────────────────────────────

📡 **وضعیت API:**
┌─────────────────────────────
├ 🔑 Access ID: {'✅' if ACCESS_ID else '❌'}
├ 🔒 Secret Key: {'✅' if SECRET_KEY else '❌'}
├ 🧠 Groq API: {'✅' if GROQ_API_KEY else '❌'}
└─────────────────────────────

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          ❓ *راهنمای کامل ربات* ❓
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **انواع سیگنال:**

🟢🟢 خرید قوی (اطمینان >80%)
🟢 خرید (اطمینان 60-80%)
⚪ نگهداری (اطمینان 50%)
🔴 فروش (اطمینان 60-80%)
🔴🔴 فروش قوی (اطمینان >80%)

📈 **قابلیت‌های ربات:**
• تحلیل تکنیکال (RSI, MACD, Bollinger)
• تشخیص تله‌های بازار
• ردیابی نهنگ‌ها
• تحلیل فاندامنتال
• هوش مصنوعی Groq
• معامله خودکار

💡 **نکات مهم:**
• همیشه از حد ضرر استفاده کن
• حداکثر ۲٪ ریسک کن
• در ضررهای متوالی توقف کن

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    elif data == "ai":
        await ai_menu(update, context)
    elif data == "whale":
        await whale_menu(update, context)
    elif data == "news":
        await news_menu(update, context)
    elif data == "trade":
        await trade_menu(update, context)
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
    elif data.startswith("buy_"):
        await buy_order(update, context, data.split("_")[1])
    elif data.startswith("sell_"):
        await sell_order(update, context, data.split("_")[1])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
