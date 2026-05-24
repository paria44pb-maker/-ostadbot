import os
import logging
import asyncio
import time
import random
import json
import hmac
import hashlib
import numpy as np
import pandas as pd
import ta
import ccxt
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# ---------------------------- تنظیمات ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = "@CryptoPulse606"
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# CoinEx
COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")
COINEX_PASSPHRASE = os.getenv("COINEX_PASSPHRASE", "")
COINEX_DEMO = os.getenv("COINEX_DEMO", "True").lower() == "true"

# تنظیمات معاملاتی
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
MAX_POSITIONS = 3
RISK_PER_TRADE = 0.02
ATR_MULTIPLIER_SL = 1.5
RR_RATIO = 2.0
AUTO_TRADE_ENABLED = False
REAL_TRADE_ENABLED = False

# ---------------------------- صرافی CoinEx ----------------------------
class CoinExExchange:
    def __init__(self):
        self.exchange = ccxt.coinex({
            'apiKey': COINEX_API_KEY,
            'secret': COINEX_SECRET_KEY,
            'password': COINEX_PASSPHRASE,
            'enableRateLimit': True,
        })
        if COINEX_DEMO:
            self.exchange.set_sandbox_mode(True)

    async def fetch_ohlcv(self, symbol, timeframe='1h', limit=200):
        try:
            return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        except Exception as e:
            logger.error(f"OHLCV error: {e}")
            return None

    async def fetch_ticker(self, symbol):
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            logger.error(f"Ticker error: {e}")
            return None

    async def create_order(self, symbol, side, amount):
        try:
            return self.exchange.create_order(symbol, 'market', side, amount, None)
        except Exception as e:
            logger.error(f"Order error: {e}")
            return None

exchange = CoinExExchange()

# ---------------------------- اندیکاتورها با کتابخانه ta ----------------------------
def calculate_indicators(df):
    """محاسبه ۱۵+ اندیکاتور با کتابخانه ta"""
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    volume = df['volume'].values
    
    indicators = {}
    
    # روند (Trend)
    indicators['EMA20'] = ta.trend.ema_indicator(pd.Series(close), window=20).iloc[-1]
    indicators['EMA50'] = ta.trend.ema_indicator(pd.Series(close), window=50).iloc[-1]
    indicators['SMA20'] = ta.trend.sma_indicator(pd.Series(close), window=20).iloc[-1]
    indicators['SMA50'] = ta.trend.sma_indicator(pd.Series(close), window=50).iloc[-1]
    indicators['ADX'] = ta.trend.adx(pd.Series(high), pd.Series(low), pd.Series(close), window=14).iloc[-1]
    
    # اسیلاتورها
    indicators['RSI'] = ta.momentum.rsi(pd.Series(close), window=14).iloc[-1]
    indicators['CCI'] = ta.trend.cci(pd.Series(high), pd.Series(low), pd.Series(close), window=20).iloc[-1]
    macd = ta.trend.MACD(pd.Series(close))
    indicators['MACD'] = macd.macd().iloc[-1]
    indicators['MACD_SIGNAL'] = macd.macd_signal().iloc[-1]
    indicators['WILLIAMS_R'] = ta.momentum.williams_r(pd.Series(high), pd.Series(low), pd.Series(close), lbp=14).iloc[-1]
    indicators['MFI'] = ta.volume.money_flow_index(pd.Series(high), pd.Series(low), pd.Series(close), pd.Series(volume), window=14).iloc[-1]
    
    # نوسان
    bb = ta.volatility.BollingerBands(pd.Series(close), window=20, window_dev=2)
    indicators['BB_UPPER'] = bb.bollinger_hband().iloc[-1]
    indicators['BB_MIDDLE'] = bb.bollinger_mavg().iloc[-1]
    indicators['BB_LOWER'] = bb.bollinger_lband().iloc[-1]
    indicators['ATR'] = ta.volatility.average_true_range(pd.Series(high), pd.Series(low), pd.Series(close), window=14).iloc[-1]
    
    # حجم
    indicators['OBV'] = ta.volume.on_balance_volume(pd.Series(close), pd.Series(volume)).iloc[-1]
    
    return indicators

def calculate_support_resistance(closes):
    recent = closes[-50:]
    high = max(recent)
    low = min(recent)
    pivot = (high + low) / 2
    r1 = pivot + (high - low) * 0.382
    r2 = pivot + (high - low) * 0.618
    s1 = pivot - (high - low) * 0.382
    s2 = pivot - (high - low) * 0.618
    return {"support": [s1, s2, low], "resistance": [r1, r2, high], "pivot": pivot}

def detect_trap(change, volume, rsi):
    if change > 3 and volume > 10000000 and rsi > 70:
        return "⚠️ تله گاوی (خرید کاذب)"
    if change < -3 and volume > 10000000 and rsi < 30:
        return "⚠️ تله خرسی (فروش کاذب)"
    return "✅ بدون تله"

def generate_signal(indicators, current_price, change, volume):
    scores = {"BUY": 0, "SELL": 0}
    signals = []
    
    # RSI
    rsi = indicators['RSI']
    if rsi < 30:
        scores["BUY"] += 30
        signals.append(("RSI", "BUY", 30, f"oversold ({rsi:.0f})"))
    elif rsi > 70:
        scores["SELL"] += 30
        signals.append(("RSI", "SELL", 30, f"overbought ({rsi:.0f})"))
    
    # MACD
    if indicators['MACD'] > indicators['MACD_SIGNAL']:
        scores["BUY"] += 25
        signals.append(("MACD", "BUY", 25, "bullish crossover"))
    else:
        scores["SELL"] += 25
        signals.append(("MACD", "SELL", 25, "bearish crossover"))
    
    # EMA
    if indicators['EMA20'] > indicators['EMA50']:
        scores["BUY"] += 20
        signals.append(("EMA", "BUY", 20, "EMA20 > EMA50"))
    else:
        scores["SELL"] += 20
        signals.append(("EMA", "SELL", 20, "EMA20 < EMA50"))
    
    # باند بولینگر
    if current_price <= indicators['BB_LOWER']:
        scores["BUY"] += 20
        signals.append(("Bollinger", "BUY", 20, "price at lower band"))
    elif current_price >= indicators['BB_UPPER']:
        scores["SELL"] += 20
        signals.append(("Bollinger", "SELL", 20, "price at upper band"))
    
    # CCI
    cci = indicators['CCI']
    if cci < -100:
        scores["BUY"] += 15
        signals.append(("CCI", "BUY", 15, f"oversold ({cci:.0f})"))
    elif cci > 100:
        scores["SELL"] += 15
        signals.append(("CCI", "SELL", 15, f"overbought ({cci:.0f})"))
    
    # تغییر قیمت
    if change > 2:
        scores["BUY"] += 15
        signals.append(("Price", "BUY", 15, f"pump {change:+.1f}%"))
    elif change < -2:
        scores["SELL"] += 15
        signals.append(("Price", "SELL", 15, f"dump {change:+.1f}%"))
    
    # ADX
    adx = indicators['ADX']
    if adx > 25:
        if scores["BUY"] > scores["SELL"]:
            scores["BUY"] += 15
            signals.append(("ADX", "BUY", 15, f"strong uptrend ({adx:.0f})"))
        else:
            scores["SELL"] += 15
            signals.append(("ADX", "SELL", 15, f"strong downtrend ({adx:.0f})"))
    
    total = scores["BUY"] - scores["SELL"]
    
    if total >= 50:
        final_signal = "خرید قوی"
        confidence = 95
    elif total >= 30:
        final_signal = "خرید"
        confidence = 80
    elif total <= -50:
        final_signal = "فروش قوی"
        confidence = 95
    elif total <= -30:
        final_signal = "فروش"
        confidence = 80
    else:
        final_signal = "نگهداری"
        confidence = 50
    
    # قدرت سیگنال با دایره
    if final_signal == "خرید قوی":
        strength = "🟢🟢🟢🟢🟢"
    elif final_signal == "خرید":
        strength = "🟢🟢🟢⚪⚪"
    elif final_signal == "فروش قوی":
        strength = "🔴🔴🔴🔴🔴"
    elif final_signal == "فروش":
        strength = "🔴🔴🔴⚪⚪"
    else:
        strength = "⚪⚪⚪⚪⚪"
    
    return final_signal, confidence, strength, signals[:5], total, rsi, indicators

# ---------------------------- مدیریت ریسک ----------------------------
class RiskManager:
    def __init__(self):
        self.consecutive_losses = 0
        self.open_positions = 0

    def can_trade(self):
        if self.open_positions >= MAX_POSITIONS:
            return False
        if self.consecutive_losses >= 3:
            return False
        return True

    def calculate_position_size(self, balance, current_price, atr):
        risk_amount = balance * RISK_PER_TRADE
        stop_distance = atr * ATR_MULTIPLIER_SL
        if stop_distance <= 0:
            return 0
        return risk_amount / stop_distance

    def calculate_stop_loss(self, entry_price, action, atr):
        if action == "خرید" or action == "خرید قوی":
            return entry_price - (atr * ATR_MULTIPLIER_SL)
        else:
            return entry_price + (atr * ATR_MULTIPLIER_SL)

    def calculate_take_profit(self, entry_price, action, stop_loss):
        distance = abs(entry_price - stop_loss)
        if action == "خرید" or action == "خرید قوی":
            return entry_price + (distance * RR_RATIO)
        else:
            return entry_price - (distance * RR_RATIO)

risk_manager = RiskManager()

# ---------------------------- دمو معامله ----------------------------
demo_balance = 10000
demo_positions = {}
demo_history = []

async def execute_demo_trade(symbol, signal, confidence, price, indicators):
    global demo_balance, demo_positions, demo_history
    if not AUTO_TRADE_ENABLED or confidence < 70:
        return
    
    atr = indicators['ATR']
    
    if "خرید" in signal:
        if symbol in demo_positions:
            return
        amount_usdt = demo_balance * 0.2
        if amount_usdt > demo_balance:
            return
        amount_coin = amount_usdt / price
        sl = risk_manager.calculate_stop_loss(price, signal, atr)
        tp = risk_manager.calculate_take_profit(price, signal, sl)
        demo_balance -= amount_usdt
        demo_positions[symbol] = {
            "amount": amount_coin, "entry_price": price, "sl": sl, "tp": tp,
            "entry_time": datetime.now().isoformat(), "signal": signal
        }
        logger.info(f"DEMO BUY {symbol}: {amount_coin:.6f} @ {price:.2f}")
        
    elif "فروش" in signal:
        if symbol in demo_positions:
            pos = demo_positions[symbol]
            sell_value = pos["amount"] * price
            pnl = sell_value - (pos["amount"] * pos["entry_price"])
            demo_balance += sell_value
            demo_history.append({
                "symbol": symbol, "side": "فروش", "entry_price": pos["entry_price"],
                "exit_price": price, "pnl": pnl, "time": datetime.now().isoformat()
            })
            del demo_positions[symbol]
            logger.info(f"DEMO SELL {symbol}: PnL={pnl:.2f}")

# ---------------------------- هوش مصنوعی Groq ----------------------------
async def groq_generate(prompt, max_tokens=800):
    if not GROQ_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return None

# ---------------------------- ارسال خودکار به کانال ----------------------------
async def auto_signal_loop(app):
    await asyncio.sleep(10)
    logger.info(f"شروع حلقه خودکار – ارسال به کانال {CHANNEL_ID}")
    
    while True:
        await asyncio.sleep(300)  # 5 دقیقه
        logger.info("شروع ارسال سیگنال خودکار...")
        
        for symbol in SYMBOLS[:3]:
            try:
                # دریافت داده
                ohlcv = await exchange.fetch_ohlcv(symbol, '1h', 100)
                if not ohlcv:
                    continue
                
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                ticker = await exchange.fetch_ticker(symbol)
                if not ticker:
                    continue
                
                current_price = ticker['last']
                change = ticker['percentage']
                volume = ticker['quoteVolume'] if 'quoteVolume' in ticker else 0
                
                # محاسبه اندیکاتورها
                indicators = calculate_indicators(df)
                closes = df['close'].values
                sr = calculate_support_resistance(closes)
                rsi = indicators['RSI']
                trap = detect_trap(change, volume, rsi)
                
                # سیگنال
                signal, confidence, strength, top_signals, total, rsi_val, ind = generate_signal(indicators, current_price, change, volume)
                
                # حد ضرر و سود
                atr = indicators['ATR']
                if "خرید" in signal:
                    sl = current_price - (atr * ATR_MULTIPLIER_SL)
                    tp = current_price + (atr * ATR_MULTIPLIER_SL * RR_RATIO)
                else:
                    sl = current_price + (atr * ATR_MULTIPLIER_SL)
                    tp = current_price - (atr * ATR_MULTIPLIER_SL * RR_RATIO)
                
                # معامله دمو
                await execute_demo_trade(symbol, signal, confidence, current_price, indicators)
                
                # ساخت پیام
                signals_text = "\n".join([f"• {s[0]}: {s[3]}" for s in top_signals[:4]])
                
                msg = f"""
🌿 *『 {symbol.replace('USDT', '')} 』* 🌿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 **قیمت:** `${current_price:,.2f}`
📈 **تغییر 24h:** `{change:+.2f}%`
🎯 **سیگنال:** `{signal}` (اطمینان {confidence}%)
💪 **قدرت:** {strength}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **اندیکاتورها:**
• RSI: `{indicators['RSI']:.1f}`
• MACD: `{indicators['MACD']:.2f}`
• EMA20: `${indicators['EMA20']:,.2f}` | EMA50: `${indicators['EMA50']:,.2f}`
• باند بولینگر: پایین `${indicators['BB_LOWER']:,.2f}` | بالا `${indicators['BB_UPPER']:,.2f}`
• CCI: `{indicators['CCI']:.1f}` | ADX: `{indicators['ADX']:.1f}`
• ATR: `${indicators['ATR']:.2f}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ **حد ضرر:** `${sl:,.2f}`
🎯 **هدف:** `${tp:,.2f}`
{trap}
📝 **سیگنال‌های برتر:**
{signals_text}
📊 **امتیاز نهایی:** `{total:+d}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""
                await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
                logger.info(f"سیگنال {symbol} ارسال شد")
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Error in auto signal for {symbol}: {e}")
        
        # ارسال محتوای AI هر 2 ساعت
        if int(time.time()) % 7200 < 300 and GROQ_API_KEY:
            try:
                topics = ["تحلیل تکنیکال", "مدیریت ریسک", "روانشناسی ترید", "اخبار کریپتو"]
                prompt = f"یه متن آموزشی کوتاه و مفید درباره {random.choice(topics)} برای تریدرهای کریپتو بنویس. حدود 200-300 کلمه. با لحن حرفه‌ای و دوستانه."
                ai_content = await groq_generate(prompt, 600)
                if ai_content:
                    await app.bot.send_message(chat_id=CHANNEL_ID, text=f"🧠 *تحلیل هوشمند*\n\n{ai_content}\n\n✨ @CryptoPulse606", parse_mode="Markdown")
                    logger.info("AI content sent")
            except Exception as e:
                logger.error(f"AI content error: {e}")

# ---------------------------- منوی ربات ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("💰 پورتفوی دمو", callback_data="demo")],
        [InlineKeyboardButton("⚡ معامله خودکار", callback_data="auto_trade")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    
    text = """
🔥 *ربات فوق‌هوشمند کریپتو* 🔥

✅ ۱۵+ اندیکاتور تکنیکال
✅ سیگنال لحظه‌ای با قدرت (دایره‌های سبز/قرمز)
✅ معامله خودکار دمو
✅ تحلیل هوشمند با Groq
✅ ارسال خودکار به کانال هر ۵ دقیقه

از منوی زیر انتخاب کنید:
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    
    text = "💰 *قیمت لحظه‌ای* 💰\n\n"
    for symbol in SYMBOLS[:5]:
        ticker = await exchange.fetch_ticker(symbol)
        if ticker:
            emoji = "🟢" if ticker['percentage'] > 0 else "🔴" if ticker['percentage'] < 0 else "⚪"
            text += f"{emoji} *{symbol.replace('USDT', '')}*: ${ticker['last']:,.2f} ({ticker['percentage']:+.2f}%)\n"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تحلیل لحظه‌ای...")
    
    symbol = "BTCUSDT"
    ohlcv = await exchange.fetch_ohlcv(symbol, '1h', 100)
    ticker = await exchange.fetch_ticker(symbol)
    
    if not ohlcv or not ticker:
        await query.edit_message_text("❌ خطا در دریافت داده")
        return
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    indicators = calculate_indicators(df)
    signal, confidence, strength, top_signals, total, rsi_val, ind = generate_signal(indicators, ticker['last'], ticker['percentage'], ticker.get('quoteVolume', 0))
    
    signals_text = "\n".join([f"• {s[0]}: {s[3]}" for s in top_signals[:3]])
    msg = f"""
🎯 *سیگنال لحظه‌ای BTC* 🎯

💰 قیمت: ${ticker['last']:,.2f}
📈 تغییر: {ticker['percentage']:+.2f}%
🎯 سیگنال: {signal} (اطمینان {confidence}%)
💪 قدرت: {strength}
📊 امتیاز: {total:+d}

📝 جزئیات:
{signals_text}
"""
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📈 نام ارز را وارد کنید (BTC, ETH, SOL):", parse_mode="Markdown")
    context.user_data["waiting_technical"] = True

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol_input):
    symbol = None
    for s in SYMBOLS:
        if symbol_input.upper() in s:
            symbol = s
            break
    if not symbol:
        await update.message.reply_text("❌ ارز معتبر نیست.")
        return
    
    ohlcv = await exchange.fetch_ohlcv(symbol, '1h', 100)
    ticker = await exchange.fetch_ticker(symbol)
    if not ohlcv or not ticker:
        await update.message.reply_text("خطا در دریافت داده")
        return
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    indicators = calculate_indicators(df)
    closes = df['close'].values
    sr = calculate_support_resistance(closes)
    signal, confidence, strength, top_signals, total, rsi_val, ind = generate_signal(indicators, ticker['last'], ticker['percentage'], ticker.get('quoteVolume', 0))
    
    reply = f"""
📊 *تحلیل {symbol.replace('USDT', '')}* 📊

💰 قیمت: ${ticker['last']:,.2f}
📈 تغییر: {ticker['percentage']:+.2f}%
🎯 سیگنال: {signal} (اطمینان {confidence}%)
💪 قدرت: {strength}
📊 امتیاز نهایی: {total:+d}

📈 **اندیکاتورها:**
• RSI: {indicators['RSI']:.1f}
• MACD: {indicators['MACD']:.2f}
• EMA20: ${indicators['EMA20']:,.2f} | EMA50: ${indicators['EMA50']:,.2f}
• باند بولینگر: پایین ${indicators['BB_LOWER']:,.2f} | بالا ${indicators['BB_UPPER']:,.2f}
• CCI: {indicators['CCI']:.1f} | ADX: {indicators['ADX']:.1f}

🔑 **حمایت و مقاومت:**
🟢 حمایت: ${sr['support'][0]:,.2f}
🔴 مقاومت: ${sr['resistance'][0]:,.2f}
"""
    await update.message.reply_text(reply, parse_mode="Markdown")

async def demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global demo_balance, demo_positions, demo_history
    query = update.callback_query
    await query.answer()
    
    pos_text = ""
    for sym, pos in demo_positions.items():
        pos_text += f"• {sym}: {pos['amount']:.6f} @ ${pos['entry_price']:.2f}\n"
    
    total_pnl = sum(h.get('pnl', 0) for h in demo_history)
    
    text = f"""
💰 *پورتفوی دمو* 💰

موجودی نقد: ${demo_balance:,.2f}
پوزیشن‌های باز: {len(demo_positions)}
{pos_text if pos_text else 'هیچ پوزیشنی ندارد'}

تاریخچه: {len(demo_history)} معامله
سود/زیان کل: ${total_pnl:+.2f}
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def auto_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_TRADE_ENABLED
    query = update.callback_query
    await query.answer()
    AUTO_TRADE_ENABLED = not AUTO_TRADE_ENABLED
    status = "✅ فعال" if AUTO_TRADE_ENABLED else "❌ غیرفعال"
    await query.edit_message_text(f"⚡ *معامله خودکار دمو*\n\nوضعیت: {status}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = """
❓ *راهنما* ❓

📌 قابلیت‌ها:
• قیمت لحظه‌ای ۵ ارز برتر
• سیگنال بر اساس ۱۵+ اندیکاتور
• قدرت سیگنال با دایره‌های سبز/قرمز
• معامله خودکار دمو (قابل فعال/غیرفعال)
• تحلیل هوشمند با Groq (اختیاری)

⏰ ربات هر ۵ دقیقه سیگنال به کانال @CryptoPulse606 می‌فرستد.

⚠️ فقط جنبه آموزشی – مسئولیت با شماست
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

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
    elif data == "demo":
        await demo_menu(update, context)
    elif data == "auto_trade":
        await auto_trade_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.edit_message_text("در حال توسعه...")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_technical"):
        await technical_analysis(update, context, update.message.text.upper())
        context.user_data["waiting_technical"] = False
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

# ---------------------------- اجرای اصلی ----------------------------
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # راه‌اندازی حلقه خودکار
    asyncio.create_task(auto_signal_loop(app))
    
    logger.info("🚀 ربات فوق‌هوشمند کریپتو با {len(SYMBOLS)} ارز راه‌اندازی شد.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
