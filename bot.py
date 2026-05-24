import os
import logging
import asyncio
import time
import random
import json
import numpy as np
import pandas as pd
import ta
import ccxt
import httpx
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, JobQueue
from dotenv import load_dotenv

load_dotenv()

# ---------------------------- تنظیمات اصلی ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@CryptoPulse606")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# CoinEx API
COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")
COINEX_PASSPHRASE = os.getenv("COINEX_PASSPHRASE", "")

# تنظیمات معاملاتی
SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "MATIC/USDT", "DOT/USDT", "LINK/USDT"]
TIMEFRAMES = {"15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
MAX_POSITIONS = 3
RISK_PER_TRADE = 0.02  # 2% risk per trade
ATR_MULTIPLIER_SL = 1.5
RR_RATIO = 2.0
AUTO_TRADE_ENABLED = False
REAL_TRADE_ENABLED = False
MAX_DRAWDOWN = 0.15  # 15% max drawdown

# ---------------------------- صرافی CoinEx ----------------------------
exchange = None
try:
    exchange = ccxt.coinex({
        'apiKey': COINEX_API_KEY,
        'secret': COINEX_SECRET_KEY,
        'password': COINEX_PASSPHRASE,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
        }
    })
    # تست اتصال
    exchange.load_markets()
    logger.info("✅ اتصال به CoinEx با موفقیت برقرار شد")
except Exception as e:
    logger.error(f"❌ خطا در اتصال به CoinEx: {e}")
    exchange = None

# ---------------------------- کلاس مدیریت ریسک ----------------------------
class RiskManager:
    def __init__(self, initial_balance=10000):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.peak_balance = initial_balance
        self.consecutive_losses = 0
        self.max_consecutive_losses = 5
        self.daily_loss_limit = 0.05  # 5% daily loss limit
        self.daily_pnl = 0
        self.last_reset_day = datetime.now().day
        
    def update_balance(self, new_balance):
        self.current_balance = new_balance
        if new_balance > self.peak_balance:
            self.peak_balance = new_balance
            
        # ریست روزانه
        current_day = datetime.now().day
        if current_day != self.last_reset_day:
            self.daily_pnl = 0
            self.last_reset_day = current_day
            
    def can_trade(self):
        # بررسی drawdown
        drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        if drawdown > MAX_DRAWDOWN:
            logger.warning(f"⚠️ Drawdown limit reached: {drawdown:.2%}")
            return False
            
        # بررسی ضررهای متوالی
        if self.consecutive_losses >= self.max_consecutive_losses:
            logger.warning(f"⚠️ Max consecutive losses reached: {self.consecutive_losses}")
            return False
            
        # بررسی ضرر روزانه
        if abs(self.daily_pnl) / self.initial_balance > self.daily_loss_limit:
            logger.warning(f"⚠️ Daily loss limit reached")
            return False
            
        return True
        
    def calculate_position_size(self, balance, entry_price, stop_loss_price):
        risk_amount = balance * RISK_PER_TRADE
        price_risk = abs(entry_price - stop_loss_price)
        if price_risk == 0:
            return 0
        position_size = risk_amount / price_risk
        return min(position_size, balance * 0.2 / entry_price)  # Max 20% per trade

risk_manager = RiskManager()

# ---------------------------- دیتابیس ساده ----------------------------
class SimpleDatabase:
    def __init__(self, filename='trading_data.json'):
        self.filename = filename
        self.data = self.load()
        
    def load(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return {
                "positions": {},
                "history": [],
                "balance": 10000,
                "stats": {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "total_pnl": 0
                }
            }
    
    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    def add_trade(self, trade):
        self.data["history"].append(trade)
        self.data["stats"]["total_trades"] += 1
        if trade["pnl"] > 0:
            self.data["stats"]["winning_trades"] += 1
        else:
            self.data["stats"]["losing_trades"] += 1
        self.data["stats"]["total_pnl"] += trade["pnl"]
        self.save()

db = SimpleDatabase()

# ---------------------------- اندیکاتورهای تکنیکال پیشرفته ----------------------------
def calculate_advanced_indicators(df):
    """محاسبه اندیکاتورهای پیشرفته"""
    close = pd.Series(df['close'].values)
    high = pd.Series(df['high'].values)
    low = pd.Series(df['low'].values)
    volume = pd.Series(df['volume'].values)
    
    indicators = {}
    
    # میانگین‌های متحرک
    for period in [7, 14, 20, 50, 100, 200]:
        indicators[f'SMA_{period}'] = ta.trend.sma_indicator(close, window=period).iloc[-1]
        indicators[f'EMA_{period}'] = ta.trend.ema_indicator(close, window=period).iloc[-1]
    
    # RSI
    indicators['RSI'] = ta.momentum.rsi(close, window=14).iloc[-1]
    indicators['RSI_FAST'] = ta.momentum.rsi(close, window=7).iloc[-1]
    
    # MACD
    macd = ta.trend.MACD(close)
    indicators['MACD'] = macd.macd().iloc[-1]
    indicators['MACD_SIGNAL'] = macd.macd_signal().iloc[-1]
    indicators['MACD_HIST'] = macd.macd_diff().iloc[-1]
    
    # بولینگر باند
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    indicators['BB_UPPER'] = bb.bollinger_hband().iloc[-1]
    indicators['BB_MIDDLE'] = bb.bollinger_mavg().iloc[-1]
    indicators['BB_LOWER'] = bb.bollinger_lband().iloc[-1]
    indicators['BB_WIDTH'] = (indicators['BB_UPPER'] - indicators['BB_LOWER']) / indicators['BB_MIDDLE']
    indicators['BB_POSITION'] = (close.iloc[-1] - indicators['BB_LOWER']) / (indicators['BB_UPPER'] - indicators['BB_LOWER'])
    
    # استوکاستیک
    indicators['STOCH_K'] = ta.momentum.stoch(high, low, close, window=14, smooth_window=3).iloc[-1]
    indicators['STOCH_D'] = ta.momentum.stoch_signal(high, low, close, window=14, smooth_window=3).iloc[-1]
    
    # ATR
    indicators['ATR'] = ta.volatility.average_true_range(high, low, close, window=14).iloc[-1]
    indicators['ATR_PERCENT'] = (indicators['ATR'] / close.iloc[-1]) * 100
    
    # MFI
    indicators['MFI'] = ta.volume.money_flow_index(high, low, close, volume, window=14).iloc[-1]
    
    # OBV
    indicators['OBV'] = ta.volume.on_balance_volume(close, volume).iloc[-1]
    indicators['OBV_CHANGE'] = ((indicators['OBV'] - ta.volume.on_balance_volume(close, volume).iloc[-5]) / abs(ta.volume.on_balance_volume(close, volume).iloc[-5])) * 100
    
    # ADX
    indicators['ADX'] = ta.trend.adx(high, low, close, window=14).iloc[-1]
    indicators['PLUS_DI'] = ta.trend.plus_di(high, low, close, window=14).iloc[-1]
    indicators['MINUS_DI'] = ta.trend.minus_di(high, low, close, window=14).iloc[-1]
    
    # CCI
    indicators['CCI'] = ta.trend.cci(high, low, close, window=20).iloc[-1]
    
    # Williams %R
    indicators['WILLIAMS_R'] = ta.momentum.williams_r(high, low, close, lbp=14).iloc[-1]
    
    # Ichimoku
    high_9 = high.rolling(window=9).max()
    low_9 = low.rolling(window=9).min()
    high_26 = high.rolling(window=26).max()
    low_26 = low.rolling(window=26).min()
    high_52 = high.rolling(window=52).max()
    low_52 = low.rolling(window=52).min()
    
    indicators['ICHIMOKU_CONVERSION'] = ((high_9 + low_9) / 2).iloc[-1]
    indicators['ICHIMOKU_BASE'] = ((high_26 + low_26) / 2).iloc[-1]
    indicators['ICHIMOKU_SPAN_A'] = ((indicators['ICHIMOKU_CONVERSION'] + indicators['ICHIMOKU_BASE']) / 2)
    indicators['ICHIMOKU_SPAN_B'] = ((high_52 + low_52) / 2).iloc[-1]
    
    # حجم
    volume_sma = volume.rolling(window=20).mean().iloc[-1]
    indicators['VOLUME_RATIO'] = volume.iloc[-1] / volume_sma if volume_sma > 0 else 1
    
    # فیبوناچی
    high_50 = high.rolling(window=50).max().iloc[-1]
    low_50 = low.rolling(window=50).min().iloc[-1]
    diff = high_50 - low_50
    indicators['FIB_236'] = high_50 - diff * 0.236
    indicators['FIB_382'] = high_50 - diff * 0.382
    indicators['FIB_500'] = high_50 - diff * 0.500
    indicators['FIB_618'] = high_50 - diff * 0.618
    indicators['FIB_786'] = high_50 - diff * 0.786
    
    return indicators

def calculate_support_resistance(df, periods=[20, 50, 100]):
    """محاسبه سطوح حمایت و مقاومت پیشرفته"""
    closes = df['close'].values
    highs = df['high'].values
    lows = df['low'].values
    
    levels = {
        'support': [],
        'resistance': []
    }
    
    for period in periods:
        if len(closes) >= period:
            recent_high = max(highs[-period:])
            recent_low = min(lows[-period:])
            pivot = (recent_high + recent_low + closes[-1]) / 3
            
            levels['support'].extend([
                recent_low,
                pivot - (recent_high - recent_low) * 0.382,
                pivot - (recent_high - recent_low) * 0.618
            ])
            
            levels['resistance'].extend([
                pivot + (recent_high - recent_low) * 0.382,
                pivot + (recent_high - recent_low) * 0.618,
                recent_high
            ])
    
    return {
        'support': sorted(set(levels['support']))[:5],
        'resistance': sorted(set(levels['resistance']))[:5]
    }

def detect_patterns(df):
    """تشخیص الگوهای کندلی"""
    patterns = []
    close = df['close'].values
    open_ = df['open'].values
    high = df['high'].values
    low = df['low'].values
    
    # آخرین کندل
    last_close = close[-1]
    last_open = open_[-1]
    last_high = high[-1]
    last_low = low[-1]
    
    # کندل قبلی
    prev_close = close[-2] if len(close) > 1 else last_close
    prev_open = open_[-2] if len(open_) > 1 else last_open
    prev_high = high[-2] if len(high) > 1 else last_high
    prev_low = low[-2] if len(low) > 1 else last_low
    
    body = abs(last_close - last_open)
    upper_shadow = last_high - max(last_close, last_open)
    lower_shadow = min(last_close, last_open) - last_low
    
    # دوجی
    if body <= (last_high - last_low) * 0.1:
        patterns.append("🕯️ دوجی (بازگشتی)")
    
    # هامر
    if lower_shadow > body * 2 and upper_shadow < body * 0.5:
        patterns.append("🔨 هامر (صعودی)")
    
    # شوتینگ استار
    if upper_shadow > body * 2 and lower_shadow < body * 0.5:
        patterns.append("⭐ شوتینگ استار (نزولی)")
    
    # اینگالفینگ صعودی
    if last_close > last_open and prev_close < prev_open and last_open < prev_close and last_close > prev_open:
        patterns.append("📈 اینگالفینگ صعودی")
    
    # اینگالفینگ نزولی
    if last_close < last_open and prev_close > prev_open and last_open > prev_close and last_close < prev_open:
        patterns.append("📉 اینگالفینگ نزولی")
    
    return patterns

def generate_advanced_signal(indicators, price, patterns, mtf_data):
    """تولید سیگنال پیشرفته با وزن‌دهی هوشمند"""
    signal_score = 0
    max_score = 100
    
    # 1. روند (30 امتیاز)
    if indicators['EMA_20'] > indicators['EMA_50'] > indicators['EMA_200']:
        signal_score += 30
    elif indicators['EMA_20'] < indicators['EMA_50'] < indicators['EMA_200']:
        signal_score -= 30
    
    # 2. مومنتوم (25 امتیاز)
    rsi = indicators['RSI']
    if 30 <= rsi <= 70:
        if rsi > 50:
            signal_score += (rsi - 50) * 0.5
        else:
            signal_score -= (50 - rsi) * 0.5
    elif rsi < 30:
        signal_score += 15  # Oversold
    elif rsi > 70:
        signal_score -= 15  # Overbought
    
    # 3. MACD (20 امتیاز)
    if indicators['MACD'] > indicators['MACD_SIGNAL']:
        if indicators['MACD_HIST'] > 0:
            signal_score += 20
        else:
            signal_score += 10
    else:
        if indicators['MACD_HIST'] < 0:
            signal_score -= 20
        else:
            signal_score -= 10
    
    # 4. حجم (10 امتیاز)
    if indicators['VOLUME_RATIO'] > 1.5:
        signal_score += 5 if signal_score > 0 else -5
    
    # 5. الگوهای کندلی (15 امتیاز)
    for pattern in patterns:
        if "صعودی" in pattern or "هامر" in pattern:
            signal_score += 15
        elif "نزولی" in pattern or "شوتینگ" in pattern:
            signal_score -= 15
    
    # نرمال‌سازی
    signal_score = max(-max_score, min(max_score, signal_score))
    
    # تعیین سیگنال
    if signal_score >= 60:
        signal = "خرید قوی 🟢"
        confidence = min(95, 60 + signal_score * 0.35)
    elif signal_score >= 30:
        signal = "خرید 🟡"
        confidence = 50 + signal_score * 0.5
    elif signal_score <= -60:
        signal = "فروش قوی 🔴"
        confidence = min(95, 60 + abs(signal_score) * 0.35)
    elif signal_score <= -30:
        signal = "فروش 🟠"
        confidence = 50 + abs(signal_score) * 0.5
    else:
        signal = "خنثی ⚪"
        confidence = 50
    
    # تحلیل مولتی تایم‌فریم
    mtf_confirmation = 0
    for tf, tf_indicators in mtf_data.items():
        if tf_indicators.get('RSI', 50) > 50:
            mtf_confirmation += 1 if signal_score > 0 else -1
        else:
            mtf_confirmation -= 1 if signal_score > 0 else 1
    
    if abs(mtf_confirmation) >= 3:
        confidence += 5
    elif abs(mtf_confirmation) <= 1:
        confidence -= 5
    
    confidence = max(0, min(100, confidence))
    
    return signal, confidence, signal_score

# ---------------------------- معاملات واقعی ----------------------------
async def execute_real_trade(symbol, side, amount, price, stop_loss, take_profit):
    """اجرای معامله واقعی در CoinEx"""
    if not exchange or not REAL_TRADE_ENABLED:
        return None
    
    try:
        if side == "buy":
            # سفارش خرید
            order = exchange.create_order(
                symbol=symbol,
                type='limit',
                side='buy',
                amount=amount,
                price=price
            )
            
            # تنظیم حد ضرر و حد سود
            if order and stop_loss and take_profit:
                exchange.create_order(
                    symbol=symbol,
                    type='stop_limit',
                    side='sell',
                    amount=amount,
                    price=stop_loss,
                    params={'stopPrice': stop_loss}
                )
                exchange.create_order(
                    symbol=symbol,
                    type='limit',
                    side='sell',
                    amount=amount,
                    price=take_profit
                )
            
            logger.info(f"✅ Real BUY executed: {symbol} {amount} @ {price}")
            return order
            
        elif side == "sell":
            order = exchange.create_order(
                symbol=symbol,
                type='limit',
                side='sell',
                amount=amount,
                price=price
            )
            logger.info(f"✅ Real SELL executed: {symbol} {amount} @ {price}")
            return order
            
    except Exception as e:
        logger.error(f"❌ Real trade error: {e}")
        return None

# ---------------------------- اسکن بازار ----------------------------
async def market_scanner():
    """اسکن تمام نمادها و یافتن بهترین فرصت‌ها"""
    opportunities = []
    
    for symbol in SYMBOLS:
        try:
            ticker = exchange.fetch_ticker(symbol)
            ohlcv = exchange.fetch_ohlcv(symbol, '1h', 100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            indicators = calculate_advanced_indicators(df)
            patterns = detect_patterns(df)
            mtf_data = calculate_multi_timeframe_analysis(symbol)
            
            signal, confidence, score = generate_advanced_signal(indicators, ticker['last'], patterns, mtf_data)
            
            if confidence >= 75:
                opportunities.append({
                    'symbol': symbol,
                    'signal': signal,
                    'confidence': confidence,
                    'score': score,
                    'price': ticker['last'],
                    'change_24h': ticker['percentage'],
                    'volume': ticker['quoteVolume'],
                    'indicators': indicators
                })
                
        except Exception as e:
            logger.error(f"Scanner error for {symbol}: {e}")
    
    # مرتب‌سازی بر اساس اطمینان
    opportunities.sort(key=lambda x: x['confidence'], reverse=True)
    return opportunities[:5]  # 5 فرصت برتر

# ---------------------------- هوش مصنوعی پیشرفته ----------------------------
async def ai_analysis(symbol, indicators, patterns, market_data):
    """تحلیل پیشرفته با هوش مصنوعی"""
    if not GROQ_API_KEY:
        return None
        
    prompt = f"""
    تحلیل تکنیکال حرفه‌ای برای {symbol}:
    
    قیمت فعلی: ${market_data['price']:,.2f}
    تغییر 24h: {market_data['change_24h']:+.2f}%
    
    اندیکاتورها:
    - RSI: {indicators.get('RSI', 0):.1f}
    - MACD: {indicators.get('MACD', 0):.4f}
    - ADX: {indicators.get('ADX', 0):.1f}
    - BB Width: {indicators.get('BB_WIDTH', 0):.3f}
    - Volume Ratio: {indicators.get('VOLUME_RATIO', 0):.2f}
    
    الگوهای شناسایی شده: {', '.join(patterns) if patterns else 'بدون الگو'}
    
    لطفاً تحلیل کوتاه و پیش‌بینی روند ارائه دهید (حداکثر ۲۰۰ کلمه).
    شامل: جهت روند، نقاط ورود/خروج پیشنهادی، و هشدارهای مهم.
    """
    
    return await groq_generate(prompt, 500)

async def groq_generate(prompt, max_tokens=800):
    """ارتباط با Groq API"""
    if not GROQ_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Groq error: {e}")
    return None

def calculate_multi_timeframe_analysis(symbol):
    """تحلیل مولتی تایم‌فریم"""
    results = {}
    for tf_name, tf_value in TIMEFRAMES.items():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, tf_value, limit=100)
            if ohlcv and len(ohlcv) > 20:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                indicators = calculate_advanced_indicators(df)
                results[tf_name] = indicators
        except Exception as e:
            logger.error(f"MTF error for {symbol} {tf_name}: {e}")
    return results

# ---------------------------- مدیریت معاملات ----------------------------
class TradingBot:
    def __init__(self):
        self.demo_balance = 10000
        self.demo_positions = {}
        self.demo_history = []
        self.real_positions = {}
        self.last_trade_time = {}
        
    async def check_positions(self):
        """بررسی و مدیریت پوزیشن‌های باز"""
        symbols_to_check = list(self.demo_positions.keys()) + list(self.real_positions.keys())
        
        for symbol in set(symbols_to_check):
            try:
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # بررسی پوزیشن‌های دمو
                if symbol in self.demo_positions:
                    pos = self.demo_positions[symbol]
                    
                    # حد ضرر
                    if current_price <= pos['sl']:
                        await self.close_demo_position(symbol, current_price, "حد ضرر")
                    # حد سود
                    elif current_price >= pos['tp']:
                        await self.close_demo_position(symbol, current_price, "حد سود")
                    # ترلینگ استاپ
                    elif current_price > pos['entry_price'] * 1.02:  # 2% سود
                        new_sl = current_price * 0.99  # 1% ترلینگ
                        if new_sl > pos['sl']:
                            pos['sl'] = new_sl
                            logger.info(f"🔄 Trailing stop updated for {symbol}: {new_sl:.2f}")
                
                # بررسی پوزیشن‌های واقعی
                if symbol in self.real_positions and REAL_TRADE_ENABLED:
                    pos = self.real_positions[symbol]
                    if current_price <= pos['sl'] or current_price >= pos['tp']:
                        await self.close_real_position(symbol, current_price)
                        
            except Exception as e:
                logger.error(f"Position check error for {symbol}: {e}")
    
    async def open_demo_position(self, symbol, signal, confidence, price, atr):
        """باز کردن پوزیشن دمو"""
        if not AUTO_TRADE_ENABLED or confidence < 75:
            return
            
        if not risk_manager.can_trade():
            return
            
        if symbol in self.demo_positions:
            return
            
        if len(self.demo_positions) >= MAX_POSITIONS:
            return
        
        # محاسبه حد ضرر و حد سود
        if "خرید" in signal:
            stop_loss = price - (atr * ATR_MULTIPLIER_SL)
            take_profit = price + (atr * ATR_MULTIPLIER_SL * RR_RATIO)
            
            # محاسبه حجم پوزیشن
            position_size = risk_manager.calculate_position_size(self.demo_balance, price, stop_loss)
            
            if position_size <= 0:
                return
                
            cost = position_size * price
            if cost > self.demo_balance:
                position_size = self.demo_balance * 0.95 / price
                cost = position_size * price
            
            self.demo_balance -= cost
            self.demo_positions[symbol] = {
                'amount': position_size,
                'entry_price': price,
                'sl': stop_loss,
                'tp': take_profit,
                'entry_time': datetime.now(),
                'atr': atr
            }
            
            logger.info(f"📈 DEMO BUY: {symbol} {position_size:.6f} @ ${price:.2f}")
            
            # اگر معاملات واقعی فعال است
            if REAL_TRADE_ENABLED and exchange:
                await execute_real_trade(symbol, "buy", position_size, price, stop_loss, take_profit)
                
        elif "فروش" in signal and symbol in self.demo_positions:
            await self.close_demo_position(symbol, price, "سیگنال فروش")
    
    async def close_demo_position(self, symbol, current_price, reason=""):
        """بستن پوزیشن دمو"""
        if symbol not in self.demo_positions:
            return
            
        pos = self.demo_positions[symbol]
        sell_value = pos['amount'] * current_price
        entry_value = pos['amount'] * pos['entry_price']
        pnl = sell_value - entry_value
        
        self.demo_balance += sell_value
        
        # ثبت در تاریخچه
        trade_record = {
            'symbol': symbol,
            'type': 'SELL',
            'entry_price': pos['entry_price'],
            'exit_price': current_price,
            'amount': pos['amount'],
            'pnl': pnl,
            'pnl_percent': (pnl / entry_value) * 100,
            'entry_time': pos['entry_time'].isoformat() if isinstance(pos['entry_time'], datetime) else pos['entry_time'],
            'exit_time': datetime.now().isoformat(),
            'reason': reason,
            'holding_time': str(datetime.now() - (pos['entry_time'] if isinstance(pos['entry_time'], datetime) else datetime.now()))
        }
        
        self.demo_history.append(trade_record)
        db.add_trade(trade_record)
        
        # به‌روزرسانی مدیریت ریسک
        if pnl < 0:
            risk_manager.consecutive_losses += 1
        else:
            risk_manager.consecutive_losses = 0
        risk_manager.update_balance(self.demo_balance)
        
        del self.demo_positions[symbol]
        logger.info(f"📉 DEMO SELL: {symbol} @ ${current_price:.2f}, PnL: ${pnl:.2f} ({pnl/entry_value*100:.1f}%) - {reason}")
        
        return trade_record
    
    async def close_real_position(self, symbol, current_price):
        """بستن پوزیشن واقعی"""
        if not REAL_TRADE_ENABLED or not exchange:
            return
            
        if symbol in self.real_positions:
            pos = self.real_positions[symbol]
            await execute_real_trade(symbol, "sell", pos['amount'], current_price, None, None)
            del self.real_positions[symbol]

trading_bot = TradingBot()

# ---------------------------- ارسال خودکار سیگنال‌ها ----------------------------
async def auto_signal_loop(app):
    """حلقه اصلی ارسال سیگنال‌های خودکار"""
    await asyncio.sleep(10)
    last_ai_time = 0
    last_scanner_time = 0
    
    while True:
        try:
            # بررسی پوزیشن‌ها هر 1 دقیقه
            await trading_bot.check_positions()
            
            # اسکن بازار هر 5 دقیقه
            current_time = time.time()
            if current_time - last_scanner_time > 300:  # 5 دقیقه
                last_scanner_time = current_time
                
                opportunities = await market_scanner()
                
                for opp in opportunities[:3]:  # 3 سیگنال برتر
                    symbol = opp['symbol']
                    
                    # بررسی شرایط معامله
                    if opp['confidence'] >= 80:
                        await trading_bot.open_demo_position(
                            symbol,
                            opp['signal'],
                            opp['confidence'],
                            opp['price'],
                            opp['indicators'].get('ATR', opp['price'] * 0.02)
                        )
                    
                    # ارسال سیگنال به کانال
                    message = format_signal_message(symbol, opp)
                    await app.bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=message,
                        parse_mode="Markdown"
                    )
                    await asyncio.sleep(2)
            
            # تحلیل AI هر 2 ساعت
            if GROQ_API_KEY and current_time - last_ai_time > 7200:
                last_ai_time = current_time
                
                try:
                    btc_ticker = exchange.fetch_ticker("BTC/USDT")
                    btc_ohlcv = exchange.fetch_ohlcv("BTC/USDT", '1h', 100)
                    btc_df = pd.DataFrame(btc_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    btc_indicators = calculate_advanced_indicators(btc_df)
                    btc_patterns = detect_patterns(btc_df)
                    
                    ai_insight = await ai_analysis(
                        "BTC/USDT",
                        btc_indicators,
                        btc_patterns,
                        {
                            'price': btc_ticker['last'],
                            'change_24h': btc_ticker['percentage']
                        }
                    )
                    
                    if ai_insight:
                        ai_message = f"""
🧠 *تحلیل هوش مصنوعی بازار*

{ai_insight}

━━━━━━━━━━━━━━━━━━━━━━
⚠️ این یک تحلیل آموزشی است، نه توصیه مالی.
✨ @CryptoPulse606
"""
                        await app.bot.send_message(
                            chat_id=CHANNEL_ID,
                            text=ai_message,
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    logger.error(f"AI analysis error: {e}")
            
        except Exception as e:
            logger.error(f"Auto signal loop error: {e}")
        
        await asyncio.sleep(60)  # چک هر 1 دقیقه

def format_signal_message(symbol, opportunity):
    """فرمت‌بندی پیام سیگنال"""
    ind = opportunity['indicators']
    signal_emoji = "🟢" if "خرید" in opportunity['signal'] else "🔴" if "فروش" in opportunity['signal'] else "⚪"
    
    message = f"""
╔══════════════════════════════════╗
║   {signal_emoji} *سیگنال معاملاتی* {signal_emoji}   ║
╚══════════════════════════════════╝

💰 *{symbol.replace('/USDT', '')}* | ${opportunity['price']:,.2f}
📊 تغییر 24h: {opportunity['change_24h']:+.2f}%

🎯 *سیگنال:* {opportunity['signal']}
💪 *قدرت سیگنال:* {opportunity['confidence']:.0f}%

📈 *اندیکاتورهای کلیدی:*
• RSI(14): {ind.get('RSI', 0):.1f}
• MACD: {'صعودی ⬆️' if ind.get('MACD', 0) > ind.get('MACD_SIGNAL', 0) else 'نزولی ⬇️'}
• ADX: {ind.get('ADX', 0):.1f} | {'روند قوی' if ind.get('ADX', 0) > 25 else 'روند ضعیف'}
• حجم: {'بالا 📊' if ind.get('VOLUME_RATIO', 1) > 1.5 else 'نرمال'}

🔑 *سطوح کلیدی:*
• حمایت: ${ind.get('BB_LOWER', 0):.2f}
• مقاومت: ${ind.get('BB_UPPER', 0):.2f}

⚠️ *مدیریت ریسک:*
• حد ضرر پیشنهادی: ${opportunity['price'] - ind.get('ATR', 0) * 1.5:.2f}
• حد سود پیشنهادی: ${opportunity['price'] + ind.get('ATR', 0) * 3:.2f}

━━━━━━━━━━━━━━━━━━━━━━
⚠️ سیگنال آموزشی - مسئولیت معامله با شماست
✨ @CryptoPulse606
"""
    return message

# ---------------------------- منوهای تلگرام ----------------------------
def get_main_menu():
    """منوی اصلی پیشرفته"""
    keyboard = [
        [InlineKeyboardButton("📊 قیمت‌های لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 بهترین سیگنال‌ها", callback_data="best_signals")],
        [InlineKeyboardButton("🔍 اسکن بازار", callback_data="market_scan")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("⏰ تحلیل مولتی تایم‌فریم", callback_data="mtf")],
        [InlineKeyboardButton("🤖 معاملات خودکار", callback_data="auto_trade")],
        [InlineKeyboardButton("💰 پورتفوی", callback_data="portfolio")],
        [InlineKeyboardButton("📊 گزارش عملکرد", callback_data="performance")],
        [InlineKeyboardButton("📚 آموزش‌ها", callback_data="education")],
        [InlineKeyboardButton("📰 اخبار بازار", callback_data="news")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_education_menu():
    """منوی آموزش‌ها"""
    keyboard = [
        [InlineKeyboardButton("📘 مبتدی", callback_data="edu_beginner")],
        [InlineKeyboardButton("📗 متوسط", callback_data="edu_intermediate")],
        [InlineKeyboardButton("📕 پیشرفته", callback_data="edu_advanced")],
        [InlineKeyboardButton("📙 استراتژی‌ها", callback_data="edu_strategies")],
        [InlineKeyboardButton("📓 روانشناسی معامله", callback_data="edu_psychology")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------------------- هندلرهای تلگرام ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ربات"""
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ دسترسی غیرمجاز!")
        return
    
    welcome_text = """
╔═══════════════════════════════════════╗
║  🤖 *ربات معامله‌گر هوشمند کریپتو*   ║
║       نسخه حرفه‌ای V2.0              ║
╚═══════════════════════════════════════╝

✨ *قابلیت‌های کلیدی:*

📊 *تحلیل تکنیکال پیشرفته*
• ۲۰+ اندیکاتور تکنیکال
• تحلیل مولتی تایم‌فریم
• تشخیص الگوهای کندلی

🎯 *سیگنال‌های هوشمند*
• اسکن خودکار بازار
• سیگنال با درصد اطمینان
• مدیریت ریسک خودکار

🤖 *معاملات خودکار*
• معاملات دمو و واقعی
• حد ضرر و سود داینامیک
• ترلینگ استاپ

📚 *آموزش جامع*
• از مبتدی تا پیشرفته
• استراتژی‌های معاملاتی
• روانشناسی بازار

⚠️ *هشدار: این ربات فقط برای اهداف آموزشی است.*
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())

async def show_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش قیمت‌های لحظه‌ای"""
    query = update.callback_query
    await query.answer()
    
    text = "💰 *قیمت‌های لحظه‌ای بازار* 💰\n\n"
    
    for symbol in SYMBOLS:
        try:
            ticker = exchange.fetch_ticker(symbol)
            emoji = "🟢" if ticker['percentage'] > 0 else "🔴" if ticker['percentage'] < 0 else "⚪"
            text += f"{emoji} *{symbol.replace('/USDT', '')}*: ${ticker['last']:,.2f} ({ticker['percentage']:+.2f}%)\n"
            text += f"   حجم: ${ticker['quoteVolume']:,.0f} | بالا: ${ticker['high']:,.2f} | پایین: ${ticker['low']:,.2f}\n\n"
        except Exception as e:
            text += f"⚪ *{symbol.replace('/USDT', '')}*: خطا در دریافت\n"
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices"), 
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_best_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش بهترین سیگنال‌ها"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔍 در حال اسکن بازار...")
    
    opportunities = await market_scanner()
    
    if opportunities:
        text = "🎯 *بهترین فرصت‌های معاملاتی* 🎯\n\n"
        
        for i, opp in enumerate(opportunities[:5], 1):
            signal_emoji = "🟢" if "خرید" in opp['signal'] else "🔴" if "فروش" in opp['signal'] else "⚪"
            text += f"{i}. {signal_emoji} *{opp['symbol'].replace('/USDT', '')}*\n"
            text += f"   قیمت: ${opp['price']:,.2f} | سیگنال: {opp['signal']}\n"
            text += f"   اطمینان: {opp['confidence']:.1f}% | تغییر: {opp['change_24h']:+.2f}%\n\n"
    else:
        text = "❌ هیچ فرصت معاملاتی با اطمینان بالا یافت نشد."
    
    keyboard = [[InlineKeyboardButton("🔄 اسکن مجدد", callback_data="best_signals"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پورتفوی"""
    query = update.callback_query
    await query.answer()
    
    # محاسبه آمار
    total_trades = len(trading_bot.demo_history)
    winning_trades = len([t for t in trading_bot.demo_history if t['pnl'] > 0])
    losing_trades = total_trades - winning_trades
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    total_pnl = sum(t.get('pnl', 0) for t in trading_bot.demo_history)
    
    text = f"""
💰 *پورتفوی معاملاتی* 💰

📊 *موجودی:* ${trading_bot.demo_balance:,.2f}
📈 *سود/زیان کل:* ${total_pnl:+,.2f}

📊 *پوزیشن‌های باز:* {len(trading_bot.demo_positions)}
"""
    
    if trading_bot.demo_positions:
        text += "\n*پوزیشن‌های فعال:*\n"
        for symbol, pos in trading_bot.demo_positions.items():
            try:
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                pnl = (current_price - pos['entry_price']) * pos['amount']
                pnl_percent = (current_price - pos['entry_price']) / pos['entry_price'] * 100
                text += f"\n📌 *{symbol.replace('/USDT', '')}*\n"
                text += f"   ورود: ${pos['entry_price']:,.2f} | فعلی: ${current_price:,.2f}\n"
                text += f"   PnL: ${pnl:+,.2f} ({pnl_percent:+.2f}%)\n"
            except:
                pass
    
    text += f"""
\n📈 *آمار کلی:*
• کل معاملات: {total_trades}
• معاملات موفق: {winning_trades}
• نرخ موفقیت: {win_rate:.1f}%
"""
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="portfolio"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_performance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش گزارش عملکرد"""
    query = update.callback_query
    await query.answer()
    
    total_trades = len(trading_bot.demo_history)
    
    if total_trades == 0:
        text = "📊 *هنوز معامله‌ای انجام نشده است*"
    else:
        # محاسبه آمار پیشرفته
        pnls = [t['pnl'] for t in trading_bot.demo_history]
        win_trades = [t for t in trading_bot.demo_history if t['pnl'] > 0]
        lose_trades = [t for t in trading_bot.demo_history if t['pnl'] <= 0]
        
        total_pnl = sum(pnls)
        win_rate = len(win_trades) / total_trades * 100
        
        avg_win = sum(t['pnl'] for t in win_trades) / len(win_trades) if win_trades else 0
        avg_loss = sum(t['pnl'] for t in lose_trades) / len(lose_trades) if lose_trades else 0
        
        max_win = max(pnls) if pnls else 0
        max_loss = min(pnls) if pnls else 0
        
        # محاسبه شارپ ریشیو ساده
        if len(pnls) > 1:
            returns = np.array(pnls) / trading_bot.demo_balance * 100
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe = 0
        
        text = f"""
📊 *گزارش عملکرد معاملاتی* 📊

💰 *موجودی فعلی:* ${trading_bot.demo_balance:,.2f}
💵 *سود/زیان کل:* ${total_pnl:+,.2f}

📈 *آمار معاملات:*
• کل معاملات: {total_trades}
• معاملات موفق: {len(win_trades)} ({win_rate:.1f}%)
• معاملات ناموفق: {len(lose_trades)} ({100-win_rate:.1f}%)

📊 *تحلیل عملکرد:*
• میانگین سود: ${avg_win:+,.2f}
• میانگین ضرر: ${avg_loss:+,.2f}
• نسبت سود به ضرر: {abs(avg_win/avg_loss) if avg_loss != 0 else '∞':.2f}
• بهترین معامله: ${max_win:+,.2f}
• بدترین معامله: ${max_loss:+,.2f}

📉 *شاخص‌های ریسک:*
• Sharpe Ratio: {sharpe:.2f}
• حداکثر Drawdown: {(max(pnls) - min(pnls)) / trading_bot.demo_balance * 100:.1f}%
"""
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="performance"),
                 InlineKeyboardButton("📊 جزئیات بیشتر", callback_data="detailed_stats"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def auto_trade_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیمات معاملات خودکار"""
    global AUTO_TRADE_ENABLED, REAL_TRADE_ENABLED
    query = update.callback_query
    await query.answer()
    
    text = f"""
⚙️ *تنظیمات معاملات خودکار* ⚙️

🎮 *معاملات دمو:* {'✅ فعال' if AUTO_TRADE_ENABLED else '❌ غیرفعال'}
💹 *معاملات واقعی:* {'✅ فعال' if REAL_TRADE_ENABLED else '❌ غیرفعال'}

📊 *تنظیمات فعلی:*
• حداکثر پوزیشن: {MAX_POSITIONS}
• ریسک هر معامله: {RISK_PER_TRADE*100}%
• نسبت سود به ضرر: {RR_RATIO}
• حد ضرر ATR: {ATR_MULTIPLIER_SL}x

⚠️ *هشدار:* معاملات واقعی نیازمند API و موجودی واقعی است!
"""
    
    keyboard = [
        [InlineKeyboardButton(f"{'🔴' if AUTO_TRADE_ENABLED else '🟢'} معاملات دمو", callback_data="toggle_demo")],
        [InlineKeyboardButton(f"{'🔴' if REAL_TRADE_ENABLED else '🟢'} معاملات واقعی", callback_data="toggle_real")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ---------------------------- هندلر اصلی ----------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک‌های منو"""
    query = update.callback_query
    data = query.data
    
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await show_prices(update, context)
    elif data == "best_signals":
        await show_best_signals(update, context)
    elif data == "portfolio":
        await show_portfolio(update, context)
    elif data == "performance":
        await show_performance(update, context)
    elif data == "auto_trade":
        await auto_trade_settings(update, context)
    elif data == "toggle_demo":
        global AUTO_TRADE_ENABLED
        AUTO_TRADE_ENABLED = not AUTO_TRADE_ENABLED
        await auto_trade_settings(update, context)
    elif data == "toggle_real":
        global REAL_TRADE_ENABLED
        if not REAL_TRADE_ENABLED and not exchange:
            await query.answer("❌ صرافی متصل نیست!", show_alert=True)
            return
        REAL_TRADE_ENABLED = not REAL_TRADE_ENABLED
        await auto_trade_settings(update, context)
    elif data == "education":
        await query.edit_message_text("📚 *بخش آموزش*\nدسته مورد نظر را انتخاب کنید:", 
                                     parse_mode="Markdown", reply_markup=get_education_menu())
    elif data.startswith("edu_"):
        # هندلر آموزش‌ها
        await query.edit_message_text("📚 محتوای آموزشی در حال آماده‌سازی...\n\nاین بخش به زودی تکمیل می‌شود.",
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="education")]]))
    else:
        await query.edit_message_text("⚡ این بخش در حال توسعه است...",
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های متنی"""
    await update.message.reply_text("لطفاً از منوی ربات استفاده کنید. /start")

# ---------------------------- اجرای اصلی ----------------------------
async def main():
    """تابع اصلی اجرای ربات"""
    # بررسی تنظیمات
    if not TOKEN:
        logger.error("❌ توکن تلگرام تنظیم نشده است!")
        return
    
    if not exchange:
        logger.warning("⚠️ اتصال به صرافی برقرار نشد. فقط اطلاعات محدود در دسترس است.")
    
    # ساخت اپلیکیشن
    app = Application.builder().token(TOKEN).build()
    
    # اضافه کردن هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # شروع حلقه خودکار
    asyncio.create_task(auto_signal_loop(app))
    
    logger.info("🚀 ربات معامله‌گر هوشمند راه‌اندازی شد!")
    
    # اجرای ربات
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # نگه داشتن ربات
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 ربات خاموش شد.")
    except Exception as e:
        logger.error(f"❌ خطای بحرانی: {e}")
