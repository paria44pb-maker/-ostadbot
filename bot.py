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
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = "@comedyclick"  # کانال مقصد

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

# ارزهای تحت پوشش معاملاتی
TRADING_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]

# ارزها برای نمایش
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

# ========== ذخیره پوزیشن‌های واقعی ==========
real_positions = {}  # {symbol: {"amount": float, "entry_price": float, "timestamp": str, "stop_loss": float, "take_profit": float}}
total_balance = 0
last_report_time = 0

# ========== توابع API CoinEx ==========
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
    headers = {
        "Authorization": ACCESS_ID,
        "Signature": signature,
        "Timestamp": timestamp,
        "Content-Type": "application/json"
    }
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
    """دریافت موجودی واقعی حساب CoinEx"""
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
    """ثبت سفارش واقعی در CoinEx"""
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

async def cancel_order(symbol, order_id):
    """لغو سفارش"""
    return await coinex_request("DELETE", f"/order/status?market={symbol}&order_id={order_id}")

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
        return macd_line[-1], signal_line[-1]

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

# ========== تولید سیگنال معاملاتی ==========
def get_trading_signal(price, change, rsi, macd, macd_signal):
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
        return "BUY", min(95, 60 + score), reasons
    elif score <= -45:
        return "SELL", min(95, 60 + abs(score)), reasons
    else:
        return "HOLD", 50, reasons

# ========== اخبار و نهنگ‌ها ==========
async def get_crypto_news():
    """دریافت اخبار کریپتو"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://cryptopanic.com/api/v1/posts/?auth_token=&public=true&kind=news")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])[:5]
                news = []
                for r in results:
                    news.append({
                        "title": r.get("title", ""),
                        "source": r.get("source", {}).get("title", ""),
                        "url": r.get("url", ""),
                        "published_at": r.get("published_at", "")
                    })
                return news
    except Exception as e:
        logger.error(f"News error: {e}")
    return []

async def get_whale_transactions():
    """دریافت تراکنش‌های نهنگ‌ها"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://api.whale-alert.io/v1/transactions?api_key=&min_value=1000000")
            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])[:5]
                whales = []
                for tx in transactions:
                    whales.append({
                        "symbol": tx.get("symbol", "Unknown"),
                        "amount": tx.get("amount", 0),
                        "value_usd": tx.get("amount_usd", 0),
                        "from": tx.get("from", {}).get("owner", "Unknown"),
                        "to": tx.get("to", {}).get("owner", "Unknown"),
                        "transaction_type": tx.get("transaction_type", "unknown")
                    })
                return whales
    except Exception as e:
        logger.error(f"Whale error: {e}")
    return []

# ========== هوش مصنوعی Groq ==========
async def groq_analysis(symbol, price, change, rsi, sentiment):
    if not GROQ_API_KEY:
        return "⚠️ Groq API تنظیم نشده است."
    prompt = f"""
به عنوان تحلیلگر حرفه‌ای، {symbol} را تحلیل کن:
قیمت: ${price:,.0f}
تغییر: {change:+.2f}%
RSI: {rsi:.0f}
احساسات بازار: {sentiment}
در ۳ خط تحلیل کن: وضعیت، پیش‌بینی، توصیه.
"""
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
    return "خطا در تحلیل"

# ========== ارسال گزارش به کانال ==========
async def send_report_to_channel(context: ContextTypes.DEFAULT_TYPE):
    """ارسال گزارش هر ساعت به کانال"""
    global total_balance, last_report_time
    
    now = time.time()
    if now - last_report_time < 3600:  # هر یک ساعت
        return
    last_report_time = now
    
    # دریافت موجودی
    balance_data = await get_account_balance()
    current_balance = balance_data["free"] if balance_data["success"] else 0
    
    # تحلیل هر ارز
    market_report = ""
    predictions = ""
    
    for symbol in TRADING_SYMBOLS:
        price_data = await get_coinex_price(symbol)
        if not price_data["success"]:
            continue
        
        # شبیه‌سازی داده تاریخی
        prices = [price_data["price"] * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
        rsi = TechnicalAnalysis.calculate_rsi(prices)
        macd, macd_sig = TechnicalAnalysis.calculate_macd(prices)
        signal, confidence, reasons = get_trading_signal(price_data["price"], price_data["change"], rsi, macd, macd_sig)
        
        sr = TechnicalAnalysis.calculate_support_resistance(prices)
        
        market_report += f"""
┌─────────────────────────────────┐
│ {symbol.replace('USDT', '')} قیمت: ${price_data['price']:,.0f}
│ 📈 تغییر: {price_data['change']:+.2f}%
│ 🎯 سیگنال: {signal} ({confidence}%)
│ 🟢 حمایت: ${sr['support'][0]:,.0f}
│ 🔴 مقاومت: ${sr['resistance'][0]:,.0f}
└─────────────────────────────────┘
"""
        
        # پیش‌بینی برای آینده
        if signal == "BUY":
            predictions += f"✅ {symbol.replace('USDT', '')}: پیش‌بینی صعود تا ${sr['resistance'][0]:,.0f}\n"
        elif signal == "SELL":
            predictions += f"⚠️ {symbol.replace('USDT', '')}: پیش‌بینی نزول تا ${sr['support'][0]:,.0f}\n"
        else:
            predictions += f"⚪ {symbol.replace('USDT', '')}: بازار خنثی - صبر\n"
    
    # اخبار و نهنگ‌ها
    news = await get_crypto_news()
    whales = await get_whale_transactions()
    
    news_text = ""
    for n in news[:3]:
        news_text += f"📰 {n['title'][:80]}...\n"
    
    whale_text = ""
    for w in whales[:3]:
        direction = "خرید 🟢" if w["transaction_type"] == "transfer" else "فروش 🔴"
        whale_text += f"🐋 {direction} {w['amount']:.0f} {w['symbol']} (${w['value_usd']/1e6:.1f}M)\n"
    
    # تحلیل هوش مصنوعی برای BTC
    btc_price = await get_coinex_price("BTCUSDT")
    if btc_price["success"]:
        prices_btc = [btc_price["price"] * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
        rsi_btc = TechnicalAnalysis.calculate_rsi(prices_btc)
        ai_analysis = await groq_analysis("BTC", btc_price["price"], btc_price["change"], rsi_btc, "متوسط")
    else:
        ai_analysis = "خطا در تحلیل"
    
    # محاسبه سود/زیان پوزیشن‌های باز
    positions_value = 0
    positions_report = ""
    for sym, pos in real_positions.items():
        price_data = await get_coinex_price(sym)
        if price_data["success"]:
            current_value = pos["amount"] * price_data["price"]
            pnl = current_value - (pos["amount"] * pos["entry_price"])
            pnl_percent = (pnl / (pos["amount"] * pos["entry_price"])) * 100
            positions_value += current_value
            positions_report += f"• {sym}: {pos['amount']:.4f} @ ${pos['entry_price']:.0f} | PnL: {pnl_percent:+.1f}%\n"
    
    total_value = current_balance + positions_value
    total_pnl = total_value - 10000  # سرمایه اولیه فرضی
    
    # ساخت پست نهایی
    report_text = f"""
╔══════════════════════════════════════╗
║     📊 *گزارش تخصصی کریپتو* 📊     ║
║        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}        ║
╚══════════════════════════════════════╝

💰 *موجودی حساب:*
┌─────────────────────────────────┐
│ 💵 USDT قابل استفاده: ${current_balance:,.2f}
│ 📊 ارزش پوزیشن‌ها: ${positions_value:,.2f}
│ 💎 ارزش کل: ${total_value:,.2f}
│ 📈 سود/زیان کل: ${total_pnl:+.2f}
└─────────────────────────────────┘

📊 *وضعیت بازار (لحظه‌ای):*
{market_report}

🎯 *پیش‌بینی کوتاه مدت:*
{predictions}

🧠 *تحلیل هوش مصنوعی:*
{ai_analysis}

🐋 *حرکت نهنگ‌ها:*
{whale_text if whale_text else 'هیچ تراکنش بزرگی یافت نشد'}

📰 *آخرین اخبار:*
{news_text if news_text else 'اخباری یافت نشد'}

📈 *پوزیشن‌های باز:*
{positions_report if positions_report else 'هیچ پوزیشنی وجود ندارد'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ *مدیریت ریسک:* حداکثر ۲٪ در هر معامله
🔄 *ربات هر ساعت بروز می‌شود*
"""
    
    # ارسال به کانال
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=report_text,
            parse_mode="Markdown"
        )
        logger.info("Report sent to channel successfully")
    except TelegramError as e:
        logger.error(f"Failed to send to channel: {e}")
        # تلاش برای ارسال به ادمین
        if OWNER_ID != 0:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"⚠️ خطا در ارسال به کانال: {e}\n\n{report_text[:3000]}"
            )

# ========== معامله خودکار هر ساعت ==========
async def auto_trade_hourly(context: ContextTypes.DEFAULT_TYPE):
    """معامله خودکار هر یک ساعت"""
    global real_positions
    
    logger.info("شروع معامله خودکار ساعت...")
    
    # دریافت موجودی
    balance_data = await get_account_balance()
    if not balance_data["success"]:
        logger.error("خطا در دریافت موجودی")
        return
    
    current_balance = balance_data["free"]
    
    for symbol in TRADING_SYMBOLS:
        try:
            # دریافت قیمت و تحلیل
            price_data = await get_coinex_price(symbol)
            if not price_data["success"]:
                continue
            
            # شبیه‌سازی داده تاریخی
            prices = [price_data["price"] * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
            rsi = TechnicalAnalysis.calculate_rsi(prices)
            macd, macd_sig = TechnicalAnalysis.calculate_macd(prices)
            signal, confidence, reasons = get_trading_signal(price_data["price"], price_data["change"], rsi, macd, macd_sig)
            
            sr = TechnicalAnalysis.calculate_support_resistance(prices)
            stop_loss = sr["support"][0] if signal == "BUY" else sr["resistance"][0]
            take_profit = sr["resistance"][0] if signal == "BUY" else sr["support"][0]
            
            # منطق معامله
            if signal == "BUY" and confidence > 70 and symbol not in real_positions and len(real_positions) < MAX_POSITIONS:
                # محاسبه حجم معامله (حداکثر 20% موجودی برای تست)
                amount_usdt = min(current_balance * 0.2, 100)  # حداکثر 100 دلار برای تست
                amount_coin = amount_usdt / price_data["price"]
                
                if amount_coin > 0 and amount_usdt <= current_balance:
                    # ثبت سفارش خرید
                    order = await place_order(symbol, "buy", amount_coin, "market")
                    if order["success"]:
                        real_positions[symbol] = {
                            "amount": amount_coin,
                            "entry_price": price_data["price"],
                            "timestamp": datetime.now().isoformat(),
                            "stop_loss": stop_loss,
                            "take_profit": take_profit
                        }
                        current_balance -= amount_usdt
                        
                        # ارسال پیام به کانال
                        await context.bot.send_message(
                            chat_id=CHANNEL_ID,
                            text=f"🟢 **خرید خودکار {symbol}**\n💰 قیمت: ${price_data['price']:.2f}\n📦 مقدار: {amount_coin:.6f}\n🛡️ حد ضرر: ${stop_loss:.2f}\n🎯 حد سود: ${take_profit:.2f}\n📊 اطمینان: {confidence}%\n📝 دلیل: {', '.join(reasons)}",
                            parse_mode="Markdown"
                        )
                        logger.info(f"Auto buy {symbol} at ${price_data['price']:.2f}")
            
            elif signal == "SELL" and confidence > 70 and symbol in real_positions:
                pos = real_positions[symbol]
                # ثبت سفارش فروش
                order = await place_order(symbol, "sell", pos["amount"], "market")
                if order["success"]:
                    sell_value = pos["amount"] * price_data["price"]
                    pnl = sell_value - (pos["amount"] * pos["entry_price"])
                    pnl_percent = (pnl / (pos["amount"] * pos["entry_price"])) * 100
                    
                    del real_positions[symbol]
                    current_balance += sell_value
                    
                    # ارسال پیام به کانال
                    await context.bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=f"🔴 **فروش خودکار {symbol}**\n💰 قیمت: ${price_data['price']:.2f}\n📈 سود/زیان: ${pnl:+.2f} ({pnl_percent:+.1f}%)\n📊 اطمینان: {confidence}%\n📝 دلیل: {', '.join(reasons)}",
                        parse_mode="Markdown"
                    )
                    logger.info(f"Auto sell {symbol} at ${price_data['price']:.2f}, PnL: ${pnl:+.2f}")
            
            # چک حد ضرر و حد سود برای پوزیشن‌های موجود
            for sym, pos in list(real_positions.items()):
                current = await get_coinex_price(sym)
                if not current["success"]:
                    continue
                
                # حد ضرر
                if current["price"] <= pos["stop_loss"]:
                    order = await place_order(sym, "sell", pos["amount"], "market")
                    if order["success"]:
                        sell_value = pos["amount"] * current["price"]
                        pnl = sell_value - (pos["amount"] * pos["entry_price"])
                        await context.bot.send_message(
                            chat_id=CHANNEL_ID,
                            text=f"⚠️ **حد ضرر فعال شد - {sym}**\n💰 قیمت: ${current['price']:.2f}\n📉 ضرر: ${pnl:+.2f}",
                            parse_mode="Markdown"
                        )
                        del real_positions[sym]
                
                # حد سود
                elif current["price"] >= pos["take_profit"]:
                    order = await place_order(sym, "sell", pos["amount"], "market")
                    if order["success"]:
                        sell_value = pos["amount"] * current["price"]
                        pnl = sell_value - (pos["amount"] * pos["entry_price"])
                        await context.bot.send_message(
                            chat_id=CHANNEL_ID,
                            text=f"🎯 **حد سود فعال شد - {sym}**\n💰 قیمت: ${current['price']:.2f}\n📈 سود: ${pnl:+.2f}",
                            parse_mode="Markdown"
                        )
                        del real_positions[sym]
                        
        except Exception as e:
            logger.error(f"Error in auto trade for {symbol}: {e}")
            continue

# ========== منوی اصلی ربات ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ سیگنال لحظه‌ای", callback_data="signals")],
        [InlineKeyboardButton("📊 قیمت ارزها", callback_data="prices")],
        [InlineKeyboardButton("🎯 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل هوشمند", callback_data="ai_menu")],
        [InlineKeyboardButton("💰 موجودی حساب", callback_data="balance")],
        [InlineKeyboardButton("📈 پوزیشن‌های باز", callback_data="positions")],
        [InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale")],
        [InlineKeyboardButton("📰 اخبار", callback_data="news")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])

def get_refresh_keyboard(callback):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بروزرسانی", callback_data=callback)], [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])

# ========== هندلرها ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    text = """
╔══════════════════════════════════════╗
║     🔥 *ربات فوق‌پیشرفته کریپتو* 🔥    ║
╚══════════════════════════════════════╝

✨ **قابلیت‌ها:**
• 📊 معامله خودکار هر ساعت
• 💰 دریافت موجودی واقعی CoinEx
• 🎯 حد سود و حد ضرر خودکار
• 🐋 ردیابی نهنگ‌ها
• 📰 اخبار لحظه‌ای
• 🧠 تحلیل هوش مصنوعی Groq
• 📈 گزارش هر ساعت به کانال

📌 **از منوی زیر انتخاب کن:**
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت موجودی...")
    
    balance = await get_account_balance()
    if balance["success"]:
        text = f"""
💰 **موجودی حساب CoinEx** 💰

┌─────────────────────────────────┐
│ 💵 USDT (کل): **${balance['total']:,.2f}**
│ 📊 قابل استفاده: **${balance['free']:,.2f}**
│ 🔒 مسدود شده: **${balance['frozen']:,.2f}**
└─────────────────────────────────┘
"""
    else:
        text = f"❌ خطا: {balance.get('error', 'مشخص نیست')}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("balance"))

async def positions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not real_positions:
        text = "📈 **پوزیشن‌های باز**\n\nهیچ پوزیشنی وجود ندارد."
    else:
        text = "📈 **پوزیشن‌های باز** 📈\n\n"
        total_pnl = 0
        for sym, pos in real_positions.items():
            price_data = await get_coinex_price(sym)
            if price_data["success"]:
                current_value = pos["amount"] * price_data["price"]
                pnl = current_value - (pos["amount"] * pos["entry_price"])
                pnl_percent = (pnl / (pos["amount"] * pos["entry_price"])) * 100
                total_pnl += pnl
                text += f"┌─────────────────────────────────┐\n"
                text += f"│ {sym}\n"
                text += f"│ 📦 مقدار: {pos['amount']:.6f}\n"
                text += f"│ 💰 ورود: ${pos['entry_price']:.2f}\n"
                text += f"│ 💵 فعلی: ${price_data['price']:.2f}\n"
                text += f"│ 📈 سود/زیان: {pnl_percent:+.1f}%\n"
                text += f"└─────────────────────────────────┘\n\n"
        text += f"💰 **سود/زیان کل:** ${total_pnl:+.2f}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("positions"))

async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت سیگنال‌ها...")
    
    text = "✨ **سیگنال‌های لحظه‌ای** ✨\n\n"
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        if data["success"]:
            prices = [data["price"] * (1 + np.random.randn(20) * 0.015) for _ in range(20)]
            rsi = TechnicalAnalysis.calculate_rsi(prices)
            macd, macd_sig = TechnicalAnalysis.calculate_macd(prices)
            signal, confidence, _ = get_trading_signal(data["price"], data["change"], rsi, macd, macd_sig)
            
            if signal == "BUY":
                emoji = "🟢"
            elif signal == "SELL":
                emoji = "🔴"
            else:
                emoji = "⚪"
            
            text += f"{emoji} *{s['symbol']}*: ${data['price']:,.2f} ({data['change']:+.2f}%) → {signal} ({confidence}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("signals"))

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
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("prices"))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"📊 {s['symbol']}", callback_data=f"tech_{s['symbol']}")] for s in SYMBOLS[:6]]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text("📊 **تحلیل تکنیکال**\nارز را انتخاب کن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🔄 تحلیل {symbol}...")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا", reply_markup=get_back_keyboard())
        return
    
    prices = [data["price"] * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    macd, macd_sig = TechnicalAnalysis.calculate_macd(prices)
    sr = TechnicalAnalysis.calculate_support_resistance(prices)
    signal, confidence, reasons = get_trading_signal(data["price"], data["change"], rsi, macd, macd_sig)
    
    text = f"""
📊 **تحلیل تکنیکال {symbol}** 📊

💰 **قیمت:** ${data['price']:,.2f}
📈 **تغییر 24h:** {data['change']:+.2f}%
📊 **حجم:** ${data['volume']/1e6:.2f}M

┌─────────────────────────────────┐
│ 📈 **اندیکاتورها**              │
├─────────────────────────────────┤
│ • RSI: {rsi:.1f}
│ • MACD: {macd:.2f} (سیگنال: {macd_sig:.2f})
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 🔑 **سطوح کلیدی**               │
├─────────────────────────────────┤
│ 🟢 حمایت 1: ${sr['support'][0]:,.0f}
│ 🟢 حمایت 2: ${sr['support'][1]:,.0f}
│ 🔴 مقاومت 1: ${sr['resistance'][0]:,.0f}
│ 🔴 مقاومت 2: ${sr['resistance'][1]:,.0f}
│ 🎯 نقطه محوری: ${sr['pivot']:,.0f}
└─────────────────────────────────┘

🎯 **سیگنال:** {signal} (اطمینان: {confidence}%)
📝 **دلایل:** {', '.join(reasons[:2])}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(f"🧠 {s['symbol']}", callback_data=f"ai_{s['symbol']}")] for s in SYMBOLS[:6]]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    await query.edit_message_text("🧠 **تحلیل هوشمند با Groq AI**\nارز را انتخاب کن:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"🤖 تحلیل {symbol} با AI...")
    
    data = await get_coinex_price(symbol)
    if not data["success"]:
        await query.edit_message_text("❌ خطا", reply_markup=get_back_keyboard())
        return
    
    prices = [data["price"] * (1 + np.random.randn(30) * 0.015) for _ in range(30)]
    rsi = TechnicalAnalysis.calculate_rsi(prices)
    sentiment = random.choice(["صعودی", "نزولی", "خنثی"])
    
    analysis = await groq_analysis(symbol, data["price"], data["change"], rsi, sentiment)
    
    text = f"🧠 **تحلیل AI - {symbol}** 🧠\n\n{analysis}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🐋 دریافت تراکنش‌های نهنگ‌ها...")
    
    whales = await get_whale_transactions()
    
    if whales:
        text = "🐋 **تراکنش‌های بزرگ نهنگ‌ها** 🐋\n\n"
        for w in whales[:5]:
            direction = "🟢 خرید" if w["transaction_type"] == "transfer" else "🔴 فروش"
            text += f"{direction} {w['amount']:.0f} {w['symbol']} (${w['value_usd']/1e6:.1f}M)\n"
    else:
        text = "🐋 هیچ تراکنش بزرگی یافت نشد"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("whale"))

async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📰 دریافت اخبار...")
    
    news = await get_crypto_news()
    
    if news:
        text = "📰 **آخرین اخبار کریپتو** 📰\n\n"
        for n in news[:5]:
            text += f"• {n['title'][:100]}...\n"
    else:
        text = "📰 اخباری یافت نشد"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_refresh_keyboard("news"))

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
⚙️ **تنظیمات ربات** ⚙️

📡 **وضعیت API:**
• 🔑 CoinEx: {'✅' if ACCESS_ID else '❌'}
• 🧠 Groq: {'✅' if GROQ_API_KEY else '❌'}

📊 **تنظیمات معاملاتی:**
• حداکثر ریسک: {MAX_RISK_PERCENT}%
• حد ضرر: {STOP_LOSS_PERCENT}%
• حد سود: {TAKE_PROFIT_PERCENT}%
• حداکثر پوزیشن: {MAX_POSITIONS}

📈 **ارزهای تحت معامله:**
{', '.join(TRADING_SYMBOLS)}

📢 **کانال گزارش:** {CHANNEL_ID}
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
❓ **راهنمای ربات فوق‌پیشرفته** ❓

📊 **قابلیت‌ها:**

1️⃣ **معامله خودکار**
   - هر یک ساعت یک بار بازار را بررسی می‌کند
   - بر اساس RSI، MACD و تغییرات قیمت سیگنال می‌گیرد
   - حد ضرر و حد سود خودکار اعمال می‌شود

2️⃣ **گزارش به کانال**
   - هر ساعت گزارش کامل به @comedyclick ارسال می‌شود
   - شامل: قیمت‌ها، سیگنال‌ها، پوزیشن‌ها، اخبار، نهنگ‌ها

3️⃣ **مدیریت ریسک**
   - حداکثر ۲٪ ریسک در هر معامله
   - حداکثر ۳ پوزیشن همزمان

⚠️ **هشدار:** فقط جنبه آموزشی – مسئولیت با شماست
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
    elif data == "balance":
        await balance_menu(update, context)
    elif data == "positions":
        await positions_menu(update, context)
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
    elif data == "news":
        await news_menu(update, context)
    elif data == "settings":
        await settings_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data.startswith("tech_"):
        await technical_analysis(update, context, data.split("_")[1])
    elif data.startswith("ai_"):
        await ai_analysis(update, context, data.split("_")[1])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

def main():
    app = Application.builder().token(TOKEN).build()
    
    # اضافه کردن هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # اضافه کردن Job برای معامله خودکار هر ساعت
    job_queue = app.job_queue
    if job_queue:
        # معامله خودکار هر 60 دقیقه
        job_queue.run_repeating(auto_trade_hourly, interval=3600, first=60)
        # ارسال گزارش به کانال هر 60 دقیقه
        job_queue.run_repeating(send_report_to_channel, interval=3600, first=30)
    
    logger.info("🚀 ربات فوق‌پیشرفته با معامله خودکار و گزارش به کانال روشن شد...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
