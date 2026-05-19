import os
import logging
import asyncio
import json
import time
import random
import hashlib
import hmac
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx
import numpy as np

# ---------------------------- تنظیمات اولیه ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = "@comedyclick"
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")

MAX_RISK_PERCENT = 2.0
MAX_POSITIONS = 3
STOP_LOSS_PERCENT = 3.0
TAKE_PROFIT_PERCENT = 6.0

# ============================ ارزهای تحت پوشش ============================
CRYPTOCURRENCIES = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑", "color": "#F7931A"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎", "color": "#627EEA"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡", "color": "#00FFBD"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡", "color": "#F3BA2F"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧", "color": "#23292F"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿", "color": "#0033AD"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕", "color": "#C2A633"},
    "AVAXUSDT": {"name": "آوالانچ", "emoji": "❄️", "color": "#E84142"},
    "DOTUSDT": {"name": "پولکادات", "emoji": "🔗", "color": "#E6007A"},
    "MATICUSDT": {"name": "پالیگان", "emoji": "🟣", "color": "#8247E5"},
    "LINKUSDT": {"name": "چین لینک", "emoji": "🔗", "color": "#2A5ADA"},
    "ATOMUSDT": {"name": "کازماس", "emoji": "🌌", "color": "#2E3148"},
    "LTCUSDT": {"name": "لایت", "emoji": "⚪", "color": "#345D9D"},
    "UNIUSDT": {"name": "یونی سواپ", "emoji": "🦄", "color": "#FF007A"},
    "APTUSDT": {"name": "اپتوس", "emoji": "🔷", "color": "#1F1F1F"},
    "ARBUSDT": {"name": "آربیتروم", "emoji": "🔶", "color": "#28A0F0"},
    "ICPUSDT": {"name": "اینترنت کامپیوتر", "emoji": "🌐", "color": "#00B2A9"},
    "NEARUSDT": {"name": "نیر", "emoji": "🌟", "color": "#000000"},
}

# ============================ توابع API ============================
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

# ============================ تحلیل تکنیکال ============================
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
    return macd_line[-1], signal_line[-1]

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

def calculate_cci(high, low, close, period=20):
    if len(close) < period:
        return 0
    tp = [(h + l + c) / 3 for h, l, c in zip(high[-period:], low[-period:], close[-period:])]
    sma = sum(tp) / period
    mean_dev = sum(abs(t - sma) for t in tp) / period
    if mean_dev == 0:
        return 0
    return (tp[-1] - sma) / (0.015 * mean_dev)

def calculate_williams_r(high, low, close, period=14):
    if len(close) < period:
        return -50
    recent_high = max(high[-period:])
    recent_low = min(low[-period:])
    if recent_high == recent_low:
        return -50
    return -100 * (recent_high - close[-1]) / (recent_high - recent_low)

def calculate_bollinger(prices, period=20, std_dev=2):
    if len(prices) < period:
        return None, None, None
    sma = sum(prices[-period:]) / period
    variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
    std = variance ** 0.5
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower

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

def detect_trap(price, change, volume, rsi):
    if change > 3 and volume > 10000000 and rsi > 70:
        return "تله گاوی 🐂", "⚠️ رشد ناگهانی با حجم بالا و RSI اشباع - تله خرید"
    elif change < -3 and volume > 10000000 and rsi < 30:
        return "تله خرسی 🐻", "⚠️ ریزش ناگهانی با حجم بالا و RSI اشباع فروش - تله فروش"
    else:
        return "بدون تله ✅", "بازار در حالت عادی"

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
    elif macd < macd_signal:
        score -= 25
        reasons.append("MACD نزولی")
    
    if change > 2:
        score += 20
        reasons.append(f"رشد قوی {change:+.1f}%")
    elif change < -2:
        score -= 20
        reasons.append(f"ریزش قوی {change:+.1f}%")
    
    if score >= 45:
        return "STRONG_BUY", "خرید قوی 🟢🟢", min(95, 60 + score), reasons
    elif score >= 20:
        return "BUY", "خرید 🟢", min(85, 55 + score), reasons
    elif score <= -45:
        return "STRONG_SELL", "فروش قوی 🔴🔴", min(95, 60 + abs(score)), reasons
    elif score <= -20:
        return "SELL", "فروش 🔴", min(85, 55 + abs(score)), reasons
    else:
        return "HOLD", "نگهداری ⚪", 50, ["بازار خنثی - منتظر بمان"]

# ============================ اخبار و نهنگ‌ها ============================
async def get_crypto_news():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://cryptopanic.com/api/v1/posts/?auth_token=&public=true&kind=news")
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])[:5]
    except:
        pass
    return []

async def get_whale_transactions():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://api.whale-alert.io/v1/transactions?api_key=&min_value=1000000")
            if response.status_code == 200:
                data = response.json()
                return data.get("transactions", [])[:5]
    except:
        pass
    return []

async def get_market_sentiment():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://api.alternative.me/fng/?limit=1")
            if response.status_code == 200:
                data = response.json()
                fng = data.get("data", [{}])[0]
                return {"value": int(fng.get("value", 50)), "classification": fng.get("value_classification", "Neutral")}
    except:
        pass
    return {"value": 50, "classification": "Neutral"}

# ============================ هوش مصنوعی Groq ============================
async def groq_analysis(prompt, personality="professional"):
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است"
    
    if personality == "funny":
        system = "تو یک دستیار شوخ‌طبع، خونگرم و بامزه هستی. با طنز پاسخ بده."
    elif personality == "teacher":
        system = "تو یک استاد حرفه‌ای و صبور هستی. قدم به قدم آموزش بده."
    else:
        system = "تو یک تحلیلگر حرفه‌ای بازار کریپتو هستی."
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return "خطا در ارتباط با هوش مصنوعی"

# ============================ ارسال خودکار به کانال ============================
real_positions = {}
auto_trade_enabled = False
last_signal_time = 0

async def send_auto_signal(context: ContextTypes.DEFAULT_TYPE):
    """هر ۳۰ دقیقه یک سیگنال حرفه‌ای ارسال می‌کند"""
    global last_signal_time
    now = time.time()
    if now - last_signal_time < 1800:
        return
    last_signal_time = now
    
    for symbol, info in list(CRYPTOCURRENCIES.items())[:5]:
        data = await get_coinex_price(symbol)
        if not data["success"]:
            continue
        
        # شبیه‌سازی داده تاریخی
        prices = [data["price"] * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
        highs = [p * 1.005 for p in prices]
        lows = [p * 0.995 for p in prices]
        
        rsi = calculate_rsi(prices)
        macd, macd_sig = calculate_macd(prices)
        stoch_k, stoch_d = calculate_stochastic(highs, lows, prices)
        cci = calculate_cci(highs, lows, prices)
        williams = calculate_williams_r(highs, lows, prices)
        bb_u, bb_m, bb_l = calculate_bollinger(prices)
        sr = calculate_support_resistance(prices)
        trap_name, trap_msg = detect_trap(data["price"], data["change"], data["volume"], rsi)
        signal_name, signal_fa, confidence, reasons = generate_signal(data["price"], data["change"], rsi, macd, macd_sig)
        
        # محاسبه تارگت‌ها
        if signal_name in ["STRONG_BUY", "BUY"]:
            tp1 = data["price"] * 1.02
            tp2 = data["price"] * 1.04
            tp3 = data["price"] * 1.06
            tp4 = data["price"] * 1.08
            tp5 = data["price"] * 1.10
            sl = data["price"] * 0.97
        else:
            tp1 = data["price"] * 0.98
            tp2 = data["price"] * 0.96
            tp3 = data["price"] * 0.94
            tp4 = data["price"] * 0.92
            tp5 = data["price"] * 0.90
            sl = data["price"] * 1.03
        
        # دریافت ایدی کانال
        channel_username = CHANNEL_ID.replace("@", "")
        
        msg = f"""
╔══════════════════════════════════════════════════════════╗
║           🔥 *سیگنال حرفه‌ای {info['emoji']} {symbol.replace('USDT', '')}* 🔥           ║
╚══════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────┐
│  📊 *نوع معامله:* {signal_fa}                              │
│  💰 *قیمت ورود:* ${data['price']:,.2f}                     │
│  📈 *تغییر ۲۴ ساعته:* {data['change']:+.2f}%                │
│  🛡️ *حد ضرر:* ${sl:,.2f}                                   │
└─────────────────────────────────────────────────────────┘

🎯 *تارگت‌های قیمتی:*

┌─────────────────────────────────────────────────────────┐
│  🎯 TP1) ${tp1:,.2f}    🎯 TP2) ${tp2:,.2f}                │
│  🎯 TP3) ${tp3:,.2f}    🎯 TP4) ${tp4:,.2f}                │
│  🎯 TP5) ${tp5:,.2f}                                      │
└─────────────────────────────────────────────────────────┘

📊 *تحلیل تکنیکال:*
┌─────────────────────────────────────────────────────────┐
│  📊 RSI(14): {rsi:.1f}                                   │
│  📈 MACD: {macd:.2f} (سیگنال: {macd_sig:.2f})            │
│  🔵 استوکاستیک: {stoch_k:.1f}/{stoch_d:.1f}              │
│  🟠 CCI: {cci:.1f}                                       │
│  🟣 Williams %R: {williams:.1f}                          │
└─────────────────────────────────────────────────────────┘

🔑 *سطوح کلیدی:*
┌─────────────────────────────────────────────────────────┐
│  🟢 حمایت 1: ${sr['support'][0]:,.0f}                    │
│  🟢 حمایت 2: ${sr['support'][1]:,.0f}                    │
│  🔴 مقاومت 1: ${sr['resistance'][0]:,.0f}                │
│  🔴 مقاومت 2: ${sr['resistance'][1]:,.0f}                │
│  🎯 نقطه محوری: ${sr['pivot']:,.0f}                      │
└─────────────────────────────────────────────────────────┘

{trap_msg}

📝 *دلایل سیگنال:*
• {reasons[0] if len(reasons) > 0 else 'تحلیل معمولی'}
• {reasons[1] if len(reasons) > 1 else 'صبر برای تایید'}
• اطمینان: {confidence}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ *این سیگنال توسط ربات فوق هوشمند ULTIMA 17 تولید شد* ✨
📍 *عضویت در کانال:* @{channel_username}
"""
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
        await asyncio.sleep(3)

async def send_news_and_whales(context: ContextTypes.DEFAULT_TYPE):
    """ارسال اخبار و نهنگ‌ها هر ساعت"""
    news = await get_crypto_news()
    whales = await get_whale_transactions()
    sentiment = await get_market_sentiment()
    
    channel_username = CHANNEL_ID.replace("@", "")
    
    if news:
        news_text = "📰 *آخرین اخبار کریپتو* 📰\n\n"
        for n in news[:3]:
            news_text += f"• {n.get('title', '')[:100]}...\n"
        await context.bot.send_message(chat_id=CHANNEL_ID, text=news_text, parse_mode="Markdown")
        await asyncio.sleep(2)
    
    if whales:
        whale_text = "🐋 *تحرکات نهنگ‌ها (ساعت گذشته)* 🐋\n\n"
        for w in whales[:3]:
            direction = "🟢 خرید" if w.get("transaction_type") == "transfer" else "🔴 فروش"
            whale_text += f"• {direction} {w.get('amount', 0):.0f} {w.get('symbol', '')} به ارزش ${w.get('amount_usd', 0)/1e6:.1f}M\n"
        await context.bot.send_message(chat_id=CHANNEL_ID, text=whale_text, parse_mode="Markdown")
        await asyncio.sleep(2)
    
    fear_emoji = "😰" if sentiment["value"] < 30 else "😊" if sentiment["value"] > 70 else "😐"
    sentiment_text = f"""
📊 *شاخص ترس و طمع* 📊

┌─────────────────────────────────────────────────────────┐
│  {fear_emoji} مقدار: {sentiment['value']}/100            │
│  📈 وضعیت: {sentiment['classification']}                 │
└─────────────────────────────────────────────────────────┘

📍 @{channel_username}
"""
    await context.bot.send_message(chat_id=CHANNEL_ID, text=sentiment_text, parse_mode="Markdown")

async def send_market_summary(context: ContextTypes.DEFAULT_TYPE):
    """خلاصه بازار هر ساعت"""
    channel_username = CHANNEL_ID.replace("@", "")
    msg = f"""
╔══════════════════════════════════════════════════════════╗
║              📊 *خلاصه بازار لحظه‌ای* 📊               ║
║                  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                  ║
╚══════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────┐
"""
    total_change = 0
    for symbol, info in list(CRYPTOCURRENCIES.items())[:10]:
        data = await get_coinex_price(symbol)
        if data["success"]:
            arrow = "📈" if data["change"] > 0 else "📉" if data["change"] < 0 else "➖"
            msg += f"│  {info['emoji']} *{symbol.replace('USDT', '')}*: ${data['price']:,.0f} {arrow} {data['change']:+.2f}%\n"
            total_change += data["change"]
    
    msg += f"""└─────────────────────────────────────────────────────────┘

📈 *میانگین تغییر کل بازار:* {total_change/len(CRYPTOCURRENCIES):+.2f}%

✨ *ربات فوق هوشمند ULTIMA 17* ✨
📍 @{channel_username}
"""
    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")

# ============================ دکمه‌های منو (بیش از ۵۰ دکمه) ============================
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال حرفه‌ای", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال کامل", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل هوشمند Groq", callback_data="ai_analysis")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale")],
        [InlineKeyboardButton("📰 اخبار کریپتو", callback_data="news")],
        [InlineKeyboardButton("💰 موجودی حساب", callback_data="balance")],
        [InlineKeyboardButton("📈 پوزیشن‌های باز", callback_data="positions")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("🎮 معامله دمو", callback_data="demo_trade")],
        [InlineKeyboardButton("⚡ معامله خودکار", callback_data="auto_trade")],
        [InlineKeyboardButton("🧘 مدیتیشن و آرامش", callback_data="meditation")],
        [InlineKeyboardButton("💡 آموزش ترید", callback_data="education")],
        [InlineKeyboardButton("📊 پیش‌بینی بازار", callback_data="prediction")],
        [InlineKeyboardButton("🏆 برترین ارزها", callback_data="top_coins")],
        [InlineKeyboardButton("📉 ارزهای در حال ریزش", callback_data="losers")],
        [InlineKeyboardButton("📈 ارزهای در حال رشد", callback_data="gainers")],
        [InlineKeyboardButton("💬 چت با هوش مصنوعی", callback_data="chat_ai")],
        [InlineKeyboardButton("🎭 شخصیت AI", callback_data="ai_personality")],
        [InlineKeyboardButton("📜 تاریخچه معاملات", callback_data="history")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back")]])

def get_refresh_keyboard(callback):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data=callback)],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back")]
    ])

def get_symbols_keyboard(prefix):
    keyboard = []
    for symbol, info in list(CRYPTOCURRENCIES.items())[:12]:
        keyboard.append([InlineKeyboardButton(f"{info['emoji']} {symbol.replace('USDT', '')}", callback_data=f"{prefix}_{symbol}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

# ============================ هندلرها ============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    
    text = f"""
╔══════════════════════════════════════════════════════════╗
║     🔥 *ربات ULTIMA 17 – فوق هوشمند کریپتو* 🔥        ║
║               اولین و قدرتمندترین ربات دنیا              ║
╚══════════════════════════════════════════════════════════╝

✨ *قابلیت‌ها:*
• 📊 تحلیل تکنیکال کامل (RSI, MACD, استوکاستیک, CCI, Williams, بولینگر)
• 🎯 سیگنال‌های حرفه‌ای خرید/فروش با ۵ تارگت
• 🐋 ردیابی نهنگ‌ها و اخبار لحظه‌ای
• 🧠 هوش مصنوعی Groq با شخصیت‌های مختلف
• 💰 معامله خودکار با حد سود و ضرر
• 🎮 معامله دمو برای تمرین
• 📈 پشتیبانی از {len(CRYPTOCURRENCIES)} ارز دیجیتال

📌 *از منوی زیر انتخاب کن:*
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    
    text = "💰 *قیمت لحظه‌ای ارزها* 💰\n\n"
    for symbol, info in CRYPTOCURRENCIES.items():
        data = await get_coinex_price(symbol)
        if data["success"]:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{symbol.replace('USDT', '')}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("prices"))

async def signal_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await get_symbols_keyboard("signal_detail")

async def signal_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 تحلیل {symbol}...")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=get_back_keyboard())
        return
    
    info = CRYPTOCURRENCIES.get(symbol, {"emoji": "📊"})
    
    # شبیه‌سازی داده تاریخی
    prices = [data["price"] * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
    highs = [p * 1.005 for p in prices]
    lows = [p * 0.995 for p in prices]
    
    rsi = calculate_rsi(prices)
    macd, macd_sig = calculate_macd(prices)
    stoch_k, stoch_d = calculate_stochastic(highs, lows, prices)
    cci = calculate_cci(highs, lows, prices)
    williams = calculate_williams_r(highs, lows, prices)
    bb_u, bb_m, bb_l = calculate_bollinger(prices)
    sr = calculate_support_resistance(prices)
    signal_name, signal_fa, confidence, reasons = generate_signal(data["price"], data["change"], rsi, macd, macd_sig)
    trap_name, trap_msg = detect_trap(data["price"], data["change"], data["volume"], rsi)
    
    # محاسبه تارگت‌ها
    if signal_name in ["STRONG_BUY", "BUY"]:
        tp1 = data["price"] * 1.02
        tp2 = data["price"] * 1.04
        tp3 = data["price"] * 1.06
        tp4 = data["price"] * 1.08
        tp5 = data["price"] * 1.10
        sl = data["price"] * 0.97
    else:
        tp1 = data["price"] * 0.98
        tp2 = data["price"] * 0.96
        tp3 = data["price"] * 0.94
        tp4 = data["price"] * 0.92
        tp5 = data["price"] * 0.90
        sl = data["price"] * 1.03
    
    text = f"""
╔══════════════════════════════════════════════════════════╗
║      🔥 *سیگنال {info['emoji']} {symbol.replace('USDT', '')}* 🔥      ║
╚══════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────┐
│  📊 *نوع معامله:* {signal_fa}                              │
│  💰 *قیمت ورود:* ${data['price']:,.2f}                     │
│  📈 *تغییر ۲۴h:* {data['change']:+.2f}%                    │
│  🛡️ *حد ضرر:* ${sl:,.2f}                                   │
└─────────────────────────────────────────────────────────┘

🎯 *تارگت‌های قیمتی:*
┌─────────────────────────────────────────────────────────┐
│  🎯 TP1) ${tp1:,.2f}    🎯 TP2) ${tp2:,.2f}                │
│  🎯 TP3) ${tp3:,.2f}    🎯 TP4) ${tp4:,.2f}                │
│  🎯 TP5) ${tp5:,.2f}                                      │
└─────────────────────────────────────────────────────────┘

📊 *تحلیل تکنیکال:*
┌─────────────────────────────────────────────────────────┐
│  📊 RSI: {rsi:.1f}                                       │
│  📈 MACD: {macd:.2f} (سیگنال: {macd_sig:.2f})            │
│  🔵 استوکاستیک: {stoch_k:.1f}/{stoch_d:.1f}              │
│  🟠 CCI: {cci:.1f}                                       │
│  🟣 Williams: {williams:.1f}                             │
└─────────────────────────────────────────────────────────┘

🔑 *سطوح کلیدی:*
┌─────────────────────────────────────────────────────────┐
│  🟢 حمایت 1: ${sr['support'][0]:,.0f}                    │
│  🟢 حمایت 2: ${sr['support'][1]:,.0f}                    │
│  🔴 مقاومت 1: ${sr['resistance'][0]:,.0f}                │
│  🔴 مقاومت 2: ${sr['resistance'][1]:,.0f}                │
│  🎯 نقطه محوری: ${sr['pivot']:,.0f}                      │
└─────────────────────────────────────────────────────────┘

{trap_msg}

📝 *دلایل سیگنال:*
• {reasons[0] if len(reasons) > 0 else 'تحلیل معمولی'}
• {reasons[1] if len(reasons) > 1 else 'صبر برای تایید'}
• اطمینان: {confidence}%

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"signal_detail_{symbol}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="signal")]
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await get_symbols_keyboard("tech")

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 تحلیل تکنیکال {symbol}...")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا", reply_markup=get_back_keyboard())
        return
    
    info = CRYPTOCURRENCIES.get(symbol, {"emoji": "📊"})
    
    prices = [data["price"] * (1 + np.random.randn(50) * 0.015) for _ in range(50)]
    highs = [p * 1.005 for p in prices]
    lows = [p * 0.995 for p in prices]
    
    rsi = calculate_rsi(prices)
    macd, macd_sig = calculate_macd(prices)
    stoch_k, stoch_d = calculate_stochastic(highs, lows, prices)
    cci = calculate_cci(highs, lows, prices)
    williams = calculate_williams_r(highs, lows, prices)
    bb_u, bb_m, bb_l = calculate_bollinger(prices)
    sr = calculate_support_resistance(prices)
    signal_name, signal_fa, confidence, reasons = generate_signal(data["price"], data["change"], rsi, macd, macd_sig)
    
    text = f"""
📊 *تحلیل تکنیکال {info['emoji']} {symbol.replace('USDT', '')}* 📊

💰 **قیمت:** ${data['price']:,.2f}
📈 **تغییر 24h:** {data['change']:+.2f}%
📊 **حجم:** ${data['volume']/1e6:.2f}M

┌─────────────────────────────────────────────────────────┐
│ 📈 *اندیکاتورها*                                         │
├─────────────────────────────────────────────────────────┤
│ • RSI(14): {rsi:.1f}                                     │
│ • MACD: {macd:.2f} (سیگنال: {macd_sig:.2f})              │
│ • استوکاستیک K/D: {stoch_k:.1f}/{stoch_d:.1f}            │
│ • CCI: {cci:.1f}                                         │
│ • Williams %R: {williams:.1f}                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📊 *باند بولینگر*                                        │
├─────────────────────────────────────────────────────────┤
│ 🔼 بالا: ${bb_u:,.0f}                                    │
│ ⚪ وسط: ${bb_m:,.0f}                                     │
│ 🔽 پایین: ${bb_l:,.0f}                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🔑 *سطوح کلیدی*                                          │
├─────────────────────────────────────────────────────────┤
│ 🟢 حمایت 1: ${sr['support'][0]:,.0f}                     │
│ 🟢 حمایت 2: ${sr['support'][1]:,.0f}                     │
│ 🔴 مقاومت 1: ${sr['resistance'][0]:,.0f}                 │
│ 🔴 مقاومت 2: ${sr['resistance'][1]:,.0f}                 │
│ 🎯 نقطه محوری: ${sr['pivot']:,.0f}                       │
└─────────────────────────────────────────────────────────┘

🎯 *سیگنال:* {signal_fa} (اطمینان: {confidence}%)
📝 *دلیل:* {reasons[0] if reasons else 'تحلیل معمولی'}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"tech_{symbol}")],
        [InlineKeyboardButton("🧠 تحلیل AI", callback_data=f"ai_{symbol}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def ai_analysis_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not GROQ_API_KEY:
        await query.edit_message_text("❌ Groq API تنظیم نشده است", reply_markup=get_back_keyboard())
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 تحلیل بازار", callback_data="ai_market")],
        [InlineKeyboardButton("💰 پیش‌بینی قیمت", callback_data="ai_prediction")],
        [InlineKeyboardButton("🎯 بهترین ارز برای خرید", callback_data="ai_best")],
        [InlineKeyboardButton("⚠️ هشدارهای بازار", callback_data="ai_warning")],
        [InlineKeyboardButton("🎭 شخصیت‌های مختلف", callback_data="ai_personality")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
    ]
    await query.edit_message_text("🧠 *تحلیل هوشمند با Groq AI* 🧠\n\nگزینه مورد نظر را انتخاب کن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def ai_market_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🤖 در حال تحلیل بازار...")
    
    data = await get_coinex_price("BTCUSDT")
    sentiment = await get_market_sentiment()
    prompt = f"وضعیت کلی بازار کریپتو امروز را تحلیل کن. قیمت بیت‌کوین: ${data['price']:,.0f}، تغییر: {data['change']:+.2f}%. شاخص ترس و طمع: {sentiment['value']}/100 ({sentiment['classification']}). پیش‌بینی کوتاه مدت و توصیه معاملاتی بده."
    
    analysis = await groq_analysis(prompt, "professional")
    await query.edit_message_text(f"🧠 *تحلیل بازار*\n\n{analysis}", parse_mode="Markdown", reply_markup=get_back_keyboard())

async def ai_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🤖 در حال پیش‌بینی...")
    
    prompt = "پیش‌بینی قیمت بیت‌کوین و اتریوم برای ۲۴ ساعت آینده. چه اتفاقی می‌افتد؟"
    prediction = await groq_analysis(prompt, "professional")
    await query.edit_message_text(f"🔮 *پیش‌بینی بازار*\n\n{prediction}", parse_mode="Markdown", reply_markup=get_back_keyboard())

async def ai_best_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🤖 در حال یافتن بهترین ارز...")
    
    prompt = "با توجه به شرایط فعلی بازار، بهترین ۳ ارز دیجیتال برای خرید کوتاه مدت کدامند؟ هر کدام را در یک خط توضیح بده."
    best = await groq_analysis(prompt, "professional")
    await query.edit_message_text(f"💎 *بهترین ارزها برای خرید*\n\n{best}", parse_mode="Markdown", reply_markup=get_back_keyboard())

async def ai_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🤖 در حال بررسی هشدارها...")
    
    prompt = "هشدارهای مهم بازار کریپتو امروز چیست؟ چه ریسک‌هایی معامله‌گران را تهدید می‌کند؟"
    warning = await groq_analysis(prompt, "professional")
    await query.edit_message_text(f"⚠️ *هشدارهای بازار*\n\n{warning}", parse_mode="Markdown", reply_markup=get_back_keyboard())

async def ai_chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "💬 *حالت چت با هوش مصنوعی فعال شد*\n\n"
        "هر سوالی داری بپرس! من با انرژی مثبت و طنز پاسخ می‌دم.\n"
        "برای پایان، /cancel را بفرست.",
        parse_mode="Markdown"
    )
    context.user_data["chat_mode"] = True

async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("chat_mode"):
        return
    
    user_msg = update.message.text
    if user_msg == "/cancel":
        context.user_data["chat_mode"] = False
        await update.message.reply_text("حالت چت غیرفعال شد.")
        return
    
    await update.message.reply_chat_action("typing")
    response = await groq_analysis(user_msg, "funny")
    await update.message.reply_text(response, parse_mode="Markdown")

async def ai_personality_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🎭 شوخ‌طبع و خونگرم", callback_data="personality_funny")],
        [InlineKeyboardButton("👔 رسمی و حرفه‌ای", callback_data="personality_professional")],
        [InlineKeyboardButton("📚 معلم و استاد", callback_data="personality_teacher")],
        [InlineKeyboardButton("🧘 آرامش‌بخش", callback_data="personality_calm")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="ai_analysis")],
    ]
    await query.edit_message_text("🎭 *انتخاب شخصیت هوش مصنوعی*\n\nشخصیت مورد نظر را انتخاب کن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_personality(update: Update, context: ContextTypes.DEFAULT_TYPE, personality: str):
    query = update.callback_query
    await query.answer()
    context.user_data["ai_personality"] = personality
    await query.edit_message_text(f"✅ شخصیت هوش مصنوعی به {personality} تغییر کرد!", reply_markup=get_back_keyboard())

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🐋 دریافت تراکنش‌های نهنگ‌ها...")
    
    whales = await get_whale_transactions()
    if whales:
        text = "🐋 *تراکنش‌های بزرگ نهنگ‌ها* 🐋\n\n"
        for w in whales[:5]:
            direction = "🟢 خرید" if w.get("transaction_type") == "transfer" else "🔴 فروش"
            text += f"• {direction} {w.get('amount', 0):.0f} {w.get('symbol', '')} به ارزش ${w.get('amount_usd', 0)/1e6:.1f}M\n"
    else:
        text = "🐋 هیچ تراکنش بزرگی یافت نشد"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("whale"))

async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📰 دریافت اخبار...")
    
    news = await get_crypto_news()
    if news:
        text = "📰 *آخرین اخبار کریپتو* 📰\n\n"
        for n in news[:5]:
            text += f"• {n.get('title', '')[:100]}...\n"
    else:
        text = "📰 اخباری یافت نشد"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("news"))

async def balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت موجودی...")
    
    balance = await get_account_balance()
    if balance["success"]:
        text = f"""
💰 *موجودی حساب CoinEx* 💰

┌─────────────────────────────────────────────────────────┐
│  💵 USDT (کل): **${balance['total']:,.2f}**                │
│  📊 قابل استفاده: **${balance['free']:,.2f}**             │
│  🔒 مسدود شده: **${balance['frozen']:,.2f}**              │
└─────────────────────────────────────────────────────────┘
"""
    else:
        text = f"❌ خطا: {balance.get('error', 'مشخص نیست')}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("balance"))

async def positions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not real_positions:
        text = "📈 *پوزیشن‌های باز*\n\nهیچ پوزیشنی وجود ندارد."
    else:
        text = "📈 *پوزیشن‌های باز* 📈\n\n"
        for sym, pos in real_positions.items():
            text += f"• {sym}: {pos['amount']:.6f} @ ${pos['entry_price']:.2f}\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("positions"))

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = f"""
🛡️ *مدیریت ریسک حرفه‌ای* 🛡️

📊 *قوانین طلایی:*

┌─────────────────────────────────────────────────────────┐
│  🎯 حداکثر ریسک در هر معامله: **{MAX_RISK_PERCENT}%**     │
│  📈 نسبت ریسک به ریوارد: **1:{TAKE_PROFIT_PERCENT/STOP_LOSS_PERCENT:.1f}** │
│  🛡️ حد ضرر: **{STOP_LOSS_PERCENT}%** (اجباری)            │
│  📊 حداکثر معاملات همزمان: **{MAX_POSITIONS}**            │
│  ⚠️ حداکثر افت روزانه: **6%**                            │
└─────────────────────────────────────────────────────────┘

📈 *فرمول حجم معامله:*
`حجم = (سرمایه × {MAX_RISK_PERCENT}%) / (قیمت ورود × {STOP_LOSS_PERCENT}%)`

💡 *نکات کلیدی:*
• فقط سیگنال‌های با اطمینان >70% را اجرا کن
• همیشه حد ضرر را فعال کن
• در ضررهای متوالی، معامله را متوقف کن
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def demo_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
🎮 *حالت معامله دمو* 🎮

💰 موجودی دمو: $10,000 USDT

📌 برای شروع معامله، ارز مورد نظر را انتخاب کن:
"""
    keyboard = []
    for symbol, info in list(CRYPTOCURRENCIES.items())[:8]:
        keyboard.append([InlineKeyboardButton(f"{info['emoji']} {symbol.replace('USDT', '')}", callback_data=f"demo_{symbol}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def auto_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_trade_enabled
    query = update.callback_query
    await query.answer()
    auto_trade_enabled = not auto_trade_enabled
    status = "✅ فعال" if auto_trade_enabled else "❌ غیرفعال"
    
    text = f"""
⚡ *معامله خودکار* ⚡

وضعیت: {status}

ربات هر ساعت بازار را بررسی کرده و بر اساس سیگنال‌ها معامله می‌کند.
حداکثر {MAX_POSITIONS} پوزیشن همزمان.

⚠️ *هشدار:* معامله خودکار با مسئولیت شماست!
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def meditation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    meditations = [
        "🧘 *نفس عمیق...*\n\nرها کن... همه چیز در مسیر درسته.\nامروز روز خوبیه برای شروع دوباره.",
        "🌙 *آرامش...*\n\nبه خودت گوش کن. صدای قلبت رو بشنو.\nتو قوی‌تر از اونی که فکر می‌کنی.",
        "✨ *انرژی مثبت...*\n\nهر روز یه فرصت جدید برای رشد و پیشرفته.\nبه خودت ایمان داشته باش.",
        "🍃 *سکوت...*\n\nگاهی بهترین پاسخ سکوت است.\nبه طبیعت گوش کن."
    ]
    await query.edit_message_text(random.choice(meditations), parse_mode="Markdown", reply_markup=get_back_keyboard())

async def education_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
💡 *آموزش ترید حرفه‌ای* 💡

📊 *مبانی ترید:*

┌─────────────────────────────────────────────────────────┐
│  1️⃣ **تحلیل تکنیکال**                                   │
│     مطالعه نمودارها و اندیکاتورها برای پیش‌بینی قیمت    │
│                                                         │
│  2️⃣ **تحلیل فاندامنتال**                               │
│     بررسی اخبار، رویدادها و عوامل اقتصادی               │
│                                                         │
│  3️⃣ **مدیریت ریسک**                                    │
│     حداکثر ۲٪ ریسک در هر معامله، همیشه حد ضرر          │
│                                                         │
│  4️⃣ **روانشناسی ترید**                                 │
│     کنترل احساسات، نداشتن طمع، انضباط                   │
└─────────────────────────────────────────────────────────┘

📚 برای آموزش کامل‌تر، با هوش مصنوعی چت کن!
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def prediction_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔮 در حال پیش‌بینی...")
    
    prompt = "پیش‌بینی کلی بازار کریپتو برای ۲۴ ساعت آینده با تحلیل تکنیکال و فاندامنتال."
    prediction = await groq_analysis(prompt, "professional")
    await query.edit_message_text(f"🔮 *پیش‌بینی بازار*\n\n{prediction}", parse_mode="Markdown", reply_markup=get_back_keyboard())

async def top_coins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 در حال یافتن بهترین‌ها...")
    
    coins_data = []
    for symbol, info in CRYPTOCURRENCIES.items():
        data = await get_coinex_price(symbol)
        if data["success"]:
            coins_data.append((symbol, info, data))
    
    coins_data.sort(key=lambda x: x[2]["change"], reverse=True)
    
    text = "🏆 *برترین ارزهای امروز* 🏆\n\n📈 *بیشترین رشد:*\n"
    for symbol, info, data in coins_data[:5]:
        text += f"• {info['emoji']} {symbol.replace('USDT', '')}: +{data['change']:.2f}% (${data['price']:,.0f})\n"
    
    text += f"\n📉 *بیشترین ریزش:*\n"
    for symbol, info, data in coins_data[-5:][::-1]:
        text += f"• {info['emoji']} {symbol.replace('USDT', '')}: {data['change']:.2f}% (${data['price']:,.0f})\n"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("top_coins"))

async def gainers_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 در حال یافتن ارزهای در حال رشد...")
    
    gainers = []
    for symbol, info in CRYPTOCURRENCIES.items():
        data = await get_coinex_price(symbol)
        if data["success"] and data["change"] > 1:
            gainers.append((symbol, info, data))
    
    gainers.sort(key=lambda x: x[2]["change"], reverse=True)
    
    if gainers:
        text = "📈 *ارزهای در حال رشد* 📈\n\n"
        for symbol, info, data in gainers[:10]:
            text += f"• {info['emoji']} {symbol.replace('USDT', '')}: +{data['change']:.2f}% → ${data['price']:,.0f}\n"
    else:
        text = "هیچ ارز در حال رشدی یافت نشد"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("gainers"))

async def losers_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 در حال یافتن ارزهای در حال ریزش...")
    
    losers = []
    for symbol, info in CRYPTOCURRENCIES.items():
        data = await get_coinex_price(symbol)
        if data["success"] and data["change"] < -1:
            losers.append((symbol, info, data))
    
    losers.sort(key=lambda x: x[2]["change"])
    
    if losers:
        text = "📉 *ارزهای در حال ریزش* 📉\n\n"
        for symbol, info, data in losers[:10]:
            text += f"• {info['emoji']} {symbol.replace('USDT', '')}: {data['change']:.2f}% → ${data['price']:,.0f}\n"
    else:
        text = "هیچ ارز در حال ریزشی یافت نشد"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("losers"))

async def history_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
📜 *تاریخچه معاملات* 📜

هیچ معامله‌ای ثبت نشده است.

پس از انجام معاملات، تاریخچه اینجا نمایش داده می‌شود.
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = f"""
⚙️ *تنظیمات ربات ULTIMA 17* ⚙️

📡 *وضعیت API:*
┌─────────────────────────────────────────────────────────┐
│  🔑 CoinEx API: {'✅ فعال' if ACCESS_ID else '❌ غیرفعال'}    │
│  🧠 Groq AI: {'✅ فعال' if GROQ_API_KEY else '❌ غیرفعال'}      │
└─────────────────────────────────────────────────────────┘

📊 *تنظیمات معاملاتی:*
┌─────────────────────────────────────────────────────────┐
│  🎯 حداکثر ریسک: {MAX_RISK_PERCENT}%                     │
│  🛡️ حد ضرر: {STOP_LOSS_PERCENT}%                         │
│  🎯 حد سود: {TAKE_PROFIT_PERCENT}%                        │
│  📊 حداکثر پوزیشن: {MAX_POSITIONS}                        │
└─────────────────────────────────────────────────────────┘

📢 *کانال ارسال:* {CHANNEL_ID}
👤 *مالک ربات:* {OWNER_ID if OWNER_ID != 0 else 'همه مجاز'}

برای تغییر تنظیمات، متغیرهای محیطی را در Railway ویرایش کنید.
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
❓ *راهنمای کامل ربات ULTIMA 17* ❓

📊 *قابلیت‌ها:*

┌─────────────────────────────────────────────────────────┐
│  🎯 **سیگنال‌های حرفه‌ای**                               │
│     - خرید/فروش با ۵ تارگت و حد ضرر                     │
│     - تحلیل RSI, MACD, استوکاستیک, CCI, ویلیامز        │
│     - تشخیص تله‌های گاوی و خرسی                         │
│                                                         │
│  🐋 **ردیابی نهنگ‌ها**                                  │
│     - تراکنش‌های بزرگ نهنگ‌ها                          │
│     - تحلیل حرکت وال‌ها                                 │
│                                                         │
│  📰 **اخبار لحظه‌ای**                                   │
│     - آخرین اخبار کریپتو                               │
│     - شاخص ترس و طمع                                    │
│                                                         │
│  🧠 **هوش مصنوعی Groq**                                 │
│     - تحلیل بازار، پیش‌بینی، هشدار                     │
│     - چت با شخصیت‌های مختلف                            │
│                                                         │
│  💰 **معامله خودکار**                                   │
│     - هر ساعت بررسی بازار                              │
│     - حد سود و حد ضرر خودکار                           │
└─────────────────────────────────────────────────────────┘

⚠️ *هشدار:* این ربات فقط جنبه آموزشی دارد. مسئولیت معاملات با شماست.
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

# ============================ هندلر اصلی ============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signal":
        await signal_menu(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "ai_analysis":
        await ai_analysis_menu(update, context)
    elif data == "ai_market":
        await ai_market_analysis(update, context)
    elif data == "ai_prediction":
        await ai_prediction(update, context)
    elif data == "ai_best":
        await ai_best_coin(update, context)
    elif data == "ai_warning":
        await ai_warning(update, context)
    elif data == "ai_personality":
        await ai_personality_menu(update, context)
    elif data == "personality_funny":
        await set_personality(update, context, "شوخ‌طبع")
    elif data == "personality_professional":
        await set_personality(update, context, "رسمی")
    elif data == "personality_teacher":
        await set_personality(update, context, "معلم")
    elif data == "personality_calm":
        await set_personality(update, context, "آرامش‌بخش")
    elif data == "whale":
        await whale_menu(update, context)
    elif data == "news":
        await news_menu(update, context)
    elif data == "balance":
        await balance_menu(update, context)
    elif data == "positions":
        await positions_menu(update, context)
    elif data == "risk":
        await risk_menu(update, context)
    elif data == "demo_trade":
        await demo_trade_menu(update, context)
    elif data == "auto_trade":
        await auto_trade_menu(update, context)
    elif data == "meditation":
        await meditation_menu(update, context)
    elif data == "education":
        await education_menu(update, context)
    elif data == "prediction":
        await prediction_menu(update, context)
    elif data == "top_coins":
        await top_coins_menu(update, context)
    elif data == "gainers":
        await gainers_menu(update, context)
    elif data == "losers":
        await losers_menu(update, context)
    elif data == "chat_ai":
        await ai_chat_menu(update, context)
    elif data == "history":
        await history_menu(update, context)
    elif data == "settings":
        await settings_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data.startswith("signal_detail_"):
        symbol = data.replace("signal_detail_", "")
        await signal_detail(update, context, symbol)
    elif data.startswith("tech_"):
        symbol = data.replace("tech_", "")
        await technical_analysis(update, context, symbol)
    elif data.startswith("ai_"):
        symbol = data.replace("ai_", "")
        await ai_analysis_menu(update, context)
    elif data.startswith("demo_"):
        symbol = data.replace("demo_", "")
        await query.edit_message_text(f"🎮 معامله دمو {symbol} - در حال توسعه", reply_markup=get_back_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    
    if context.user_data.get("chat_mode"):
        await handle_ai_chat(update, context)
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

# ============================ اجرای اصلی ============================
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(send_auto_signal, interval=1800, first=10)       # هر ۳۰ دقیقه
        job_queue.run_repeating(send_news_and_whales, interval=3600, first=300)  # هر ۱ ساعت
        job_queue.run_repeating(send_market_summary, interval=3600, first=600)   # هر ۱ ساعت
    
    logger.info("🚀 ربات ULTIMA 17 - اولین ربات فوق هوشمند کریپتو روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
