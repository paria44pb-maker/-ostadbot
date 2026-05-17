import os
import asyncio
import logging
import json
import random
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from decimal import Decimal, getcontext
from typing import Dict, List, Optional, Tuple, Any, Callable
from functools import wraps

# تنظیم دقت Decimal
getcontext().prec = 28

# وابستگی‌های ثالث
import ccxt.async_support as ccxt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
#import talib
import requests
from groq import AsyncGroq
import pyotp

# بارگذاری متغیرهای محیطی
load_dotenv()

# ==================== تنظیمات لاگینگ ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== ثابت‌های ربات ====================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# پیکربندی صرافی‌ها
EXCHANGES_CONFIG = {
    "binance": {
        "class": ccxt.binance,
        "apiKey": os.getenv("BINANCE_API_KEY"),
        "secret": os.getenv("BINANCE_SECRET"),
        "enableRateLimit": True,
        "options": {"defaultType": "spot"}
    },
    "kucoin": {
        "class": ccxt.kucoin,
        "apiKey": os.getenv("KUCOIN_API_KEY"),
        "secret": os.getenv("KUCOIN_SECRET"),
        "password": os.getenv("KUCOIN_PASSPHRASE"),
        "enableRateLimit": True,
    },
    "nobitex": {
        "class": ccxt.nobitex,
        "apiKey": os.getenv("NOBITEX_API_KEY"),
        "enableRateLimit": True,
    },
    "okx": {
        "class": ccxt.okx,
        "apiKey": os.getenv("OKX_API_KEY"),
        "secret": os.getenv("OKX_SECRET"),
        "password": os.getenv("OKX_PASSPHRASE"),
        "enableRateLimit": True,
    }
}

# لیست ارزهای تحت پوشش (به‌روز برای سال ۲۰۲۶)
SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
    "ADA/USDT", "DOGE/USDT", "TRX/USDT", "TON/USDT", "DOT/USDT",
    "MATIC/USDT", "SHIB/USDT", "LTC/USDT", "AVAX/USDT", "UNI/USDT"
]

# لیست صرافی‌های داخلی (با مدیریت ویژه)
IRANIAN_EXCHANGES = ["nobitex"]

# ==================== توابع ابزاری ====================
def safe_decimal(value: Any) -> Decimal:
    """تبدیل مقادیر مختلف به Decimal با هندل کردن خطا"""
    try:
        if value is None:
            return Decimal('0')
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            return Decimal(value)
        if isinstance(value, Decimal):
            return value
        return Decimal('0')
    except Exception as e:
        logger.error(f"خطا در تبدیل به Decimal: {e}")
        return Decimal('0')

def format_price(price: Decimal, symbol: str = "USDT") -> str:
    """فرمت‌سازی قیمت با توجه به ارز پایه"""
    try:
        if "USDT" in symbol.upper() or "USD" in symbol.upper():
            return f"${price:,.2f}"
        elif "IRT" in symbol.upper() or "IRR" in symbol.upper():
            return f"{price:,.0f} تومان"
        else:
            return f"{price:.8f}"
    except:
        return str(price)

def create_glass_keyboard(buttons: List[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
    """ایجاد صفحه کلید شیشه‌ای شفاف با قابلیت تنظیمات پیشرفته"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for btn in row:
            if 'url' in btn:
                keyboard_row.append(InlineKeyboardButton(btn['text'], url=btn['url']))
            else:
                keyboard_row.append(InlineKeyboardButton(btn['text'], callback_data=btn['callback']))
        keyboard.append(keyboard_row)
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard():
    """منوی اصلی ربات با دکمه‌های شیشه‌ای و پیشرفته"""
    return create_glass_keyboard([
        [{"text": "💰 قیمت لحظه‌ای", "callback": "prices_menu"}],
        [{"text": "📈 تحلیل تکنیکال", "callback": "technical_menu"}],
        [{"text": "🧠 تحلیل هوشمند AI", "callback": "ai_menu"}],
        [{"text": "🐋 ردیابی نهنگ‌ها", "callback": "whale_menu"}],
        [{"text": "📊 پرتفوی و معاملات", "callback": "portfolio_menu"}],
        [{"text": "⚙️ تنظیمات", "callback": "settings_menu"}],
        [{"text": "❓ راهنما و پشتیبانی", "callback": "help_menu"}]
    ])

def get_prices_keyboard(current_page: int = 0, symbols_per_page: int = 5):
    """صفحه کلید داینامیک برای نمایش قیمت‌ها با صفحه‌بندی شیشه‌ای"""
    total_pages = (len(SYMBOLS) + symbols_per_page - 1) // symbols_per_page
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append({"text": "◀️ صفحه قبل", "callback": f"prices_page_{current_page-1}"})
    if current_page < total_pages - 1:
        nav_buttons.append({"text": "صفحه بعد ▶️", "callback": f"prices_page_{current_page+1}"})
    buttons = []
    for btn in nav_buttons:
        buttons.append([btn])
    buttons.append([{"text": "🔄 بروزرسانی", "callback": f"prices_refresh_{current_page}"}])
    buttons.append([{"text": "🔙 بازگشت به منو", "callback": "back_to_main"}])
    return create_glass_keyboard(buttons)

# ==================== مدیریت هوشمند صرافی‌ها ====================
class ExchangeManager:
    """مدیریت چندین صرافی به صورت همزمان با قابلیت بازگردانی خودکار"""

    def __init__(self):
        self.exchanges = {}
        self.nobitex_client = None
        self.nobitex_token = None
        self.nobitex_token_expiry = 0

    async def init_exchanges(self):
        """مقداردهی اولیه اتصالات به صرافی‌ها"""
        for name, config in EXCHANGES_CONFIG.items():
            try:
                if name == "nobitex":
                    continue  # نوبیتکس به صورت جداگانه مدیریت می‌شود
                exchange = config["class"]({k: v for k, v in config.items() if k != "class"})
                await exchange.load_markets()
                self.exchanges[name] = exchange
                logger.info(f"✅ صرافی {name} با موفقیت متصل شد")
            except Exception as e:
                logger.error(f"❌ خطا در اتصال به صرافی {name}: {e}")

        # راه‌اندازی کلاینت اختصاصی نوبیتکس با مدیریت OTP
        await self.init_nobitex_client()
        return self

    async def init_nobitex_client(self):
        """مقداردهی کلاینت اختصاصی نوبیتکس با احراز هویت دو مرحله‌ای"""
        try:
            api_key = os.getenv("NOBITEX_API_KEY")
            if not api_key:
                logger.warning("NOBITEX_API_KEY تنظیم نشده است")
                return

            # تنظیم session برای نوبیتکس
            self.nobitex_client = requests.Session()
            self.nobitex_client.headers.update({
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json"
            })

            # بررسی و دریافت توکن معتبر با 2FA
            await self.refresh_nobitex_token()
            logger.info("✅ کلاینت نوبیتکس با موفقیت مقداردهی شد")
        except Exception as e:
            logger.error(f"❌ خطا در مقداردهی نوبیتکس: {e}")

    async def refresh_nobitex_token(self):
        """بروزرسانی توکن نوبیتکس با استفاده از OTP (در صورت فعال بودن 2FA)"""
        try:
            totp_secret = os.getenv("NOBITEX_2FA_SECRET")
            if totp_secret:
                totp_code = pyotp.TOTP(totp_secret).now()
                self.nobitex_client.headers.update({"X-TOTP": totp_code})

            response = self.nobitex_client.post(
                "https://api.nobitex.ir/auth/token/",
                json={}
            )

            if response.status_code == 200:
                data = response.json()
                self.nobitex_token = data.get("token")
                self.nobitex_token_expiry = time.time() + 30 * 24 * 60 * 60  # 30 روز
                self.nobitex_client.headers.update({"Authorization": f"Bearer {self.nobitex_token}"})
                logger.info("✅ توکن نوبیتکس با موفقیت بروزرسانی شد")
            else:
                logger.error(f"خطا در دریافت توکن نوبیتکس: {response.text}")
        except Exception as e:
            logger.error(f"خطا در بروزرسانی توکن نوبیتکس: {e}")

    async def fetch_price(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """دریافت قیمت از یک صرافی مشخص با هندلینگ خطا"""
        try:
            if exchange_name == "nobitex":
                return await self.fetch_nobitex_price(symbol)
            elif exchange_name in self.exchanges:
                ticker = await self.exchanges[exchange_name].fetch_ticker(symbol)
                return {
                    "exchange": exchange_name,
                    "symbol": symbol,
                    "price": safe_decimal(ticker.get("last", 0)),
                    "bid": safe_decimal(ticker.get("bid", 0)),
                    "ask": safe_decimal(ticker.get("ask", 0)),
                    "high": safe_decimal(ticker.get("high", 0)),
                    "low": safe_decimal(ticker.get("low", 0)),
                    "volume": safe_decimal(ticker.get("quoteVolume", 0)),
                    "change": safe_decimal(ticker.get("percentage", 0)),
                    "timestamp": ticker.get("timestamp", int(time.time() * 1000))
                }
        except Exception as e:
            logger.error(f"خطا در دریافت قیمت از {exchange_name} برای {symbol}: {e}")
        return None

    async def fetch_nobitex_price(self, symbol: str) -> Optional[Dict]:
        """دریافت قیمت از نوبیتکس با هندلینگ خطا و مدیریت توکن"""
        try:
            # تبدیل فرمت نماد به فرمت نوبیتکس (BTCUSDT -> BTC-Usdt)
            nobitex_symbol = symbol.replace("/", "-").upper()

            # بررسی اعتبار توکن
            if time.time() > self.nobitex_token_expiry - 86400:  # 1 روز مانده به انقضا
                await self.refresh_nobitex_token()

            response = self.nobitex_client.post(
                "https://api.nobitex.ir/market/stats",
                json={"srcCurrency": nobitex_symbol.split("-")[0], "dstCurrency": nobitex_symbol.split("-")[1]}
            )

            if response.status_code == 200:
                data = response.json().get("stats", {})
                price = safe_decimal(data.get("bestSell", 0)) or safe_decimal(data.get("bestBuy", 0))
                return {
                    "exchange": "nobitex",
                    "symbol": symbol,
                    "price": price,
                    "bid": safe_decimal(data.get("bestBuy", 0)),
                    "ask": safe_decimal(data.get("bestSell", 0)),
                    "high": safe_decimal(data.get("high24h", 0)),
                    "low": safe_decimal(data.get("low24h", 0)),
                    "volume": safe_decimal(data.get("volumeSrc", 0)),
                    "change": safe_decimal(data.get("change24h", 0)),
                    "timestamp": int(time.time() * 1000)
                }
        except Exception as e:
            logger.error(f"خطا در دریافت قیمت از نوبیتکس برای {symbol}: {e}")
        return None

    async def fetch_all_prices(self, symbol: str) -> Dict[str, Dict]:
        """دریافت قیمت از تمام صرافی‌های فعال به صورت همزمان"""
        tasks = []
        for exchange_name in list(self.exchanges.keys()) + (["nobitex"] if self.nobitex_client else []):
            tasks.append(self.fetch_price(exchange_name, symbol))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        prices = {}
        for result in results:
            if result and isinstance(result, dict):
                prices[result["exchange"]] = result
        return prices

    async def close(self):
        """بستن تمام اتصالات صرافی‌ها"""
        for exchange in self.exchanges.values():
            await exchange.close()
        if self.nobitex_client:
            self.nobitex_client.close()

# ==================== تحلیل تکنیکال پیشرفته ====================
class TechnicalAnalyzer:
    """موتور تحلیل تکنیکال با استفاده از TA-Lib و اندیکاتورهای پیشرفته"""

    @staticmethod
    async def fetch_ohlcv(exchange, symbol: str, timeframe: str = "1h", limit: int = 200) -> pd.DataFrame:
        """دریافت داده‌های OHLCV از صرافی و تبدیل به دیتافریم"""
        try:
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            logger.error(f"خطا در دریافت داده‌های OHLCV: {e}")
            return pd.DataFrame()

    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Dict:
        """محاسبه تمام اندیکاتورهای مهم تکنیکال"""
        if df.empty:
            return {}

        close = df["close"].values.astype(np.float64)
        high = df["high"].values.astype(np.float64)
        low = df["low"].values.astype(np.float64)
        volume = df["volume"].values.astype(np.float64)

        indicators = {}

        # اندیکاتورهای روندی
        indicators["sma_20"] = talib.SMA(close, timeperiod=20)[-1] if len(close) >= 20 else None
        indicators["sma_50"] = talib.SMA(close, timeperiod=50)[-1] if len(close) >= 50 else None
        indicators["ema_12"] = talib.EMA(close, timeperiod=12)[-1] if len(close) >= 12 else None
        indicators["ema_26"] = talib.EMA(close, timeperiod=26)[-1] if len(close) >= 26 else None

        # اندیکاتورهای مومنتوم
        indicators["rsi_14"] = talib.RSI(close, timeperiod=14)[-1] if len(close) >= 14 else None
        macd, macd_signal, macd_hist = talib.MACD(close)
        indicators["macd"] = macd[-1] if len(macd) > 0 else None
        indicators["macd_signal"] = macd_signal[-1] if len(macd_signal) > 0 else None
        indicators["macd_histogram"] = macd_hist[-1] if len(macd_hist) > 0 else None

        # اندیکاتورهای نوسان
        upper, middle, lower = talib.BBANDS(close)
        indicators["bb_upper"] = upper[-1] if len(upper) > 0 else None
        indicators["bb_middle"] = middle[-1] if len(middle) > 0 else None
        indicators["bb_lower"] = lower[-1] if len(lower) > 0 else None
        indicators["stoch_k"], indicators["stoch_d"] = talib.STOCH(high, low, close)

        # اندیکاتور حجم
        indicators["obv"] = talib.OBV(close, volume)[-1] if len(volume) > 0 else None
        indicators["ad"] = talib.AD(high, low, close, volume)[-1] if len(volume) > 0 else None

        # میانگین‌های متحرک اضافی برای تحلیل روند
        indicators["sma_200"] = talib.SMA(close, timeperiod=200)[-1] if len(close) >= 200 else None
        indicators["ema_200"] = talib.EMA(close, timeperiod=200)[-1] if len(close) >= 200 else None

        # تشخیص الگوهای کندل استیک
        patterns = [
            talib.CDLDOJI, talib.CDLHAMMER, talib.CDLINVERTEDHAMMER,
            talib.CDLMORNINGSTAR, talib.CDLEVENINGSTAR, talib.CDLENGULFING
        ]
        pattern_names = ["doji", "hammer", "inverted_hammer", "morning_star", "evening_star", "engulfing"]
        for pattern, name in zip(patterns, pattern_names):
            result = pattern(open, high, low, close)[-1]
            if result != 0:
                indicators[f"pattern_{name}"] = "bullish" if result > 0 else "bearish"

        return indicators

    @staticmethod
    def generate_signal(indicators: Dict) -> Dict:
        """تولید سیگنال معاملاتی بر اساس ترکیب اندیکاتورها"""
        signal = {
            "action": "HOLD",
            "strength": 0,  # 0-100
            "reasons": [],
            "risk": "MEDIUM"
        }

        # منطق سیگنال خرید
        buy_score = 0
        sell_score = 0

        # RSI
        rsi = indicators.get("rsi_14")
        if rsi and rsi < 30:
            buy_score += 30
            signal["reasons"].append(f"RSI oversold ({rsi:.1f})")
        elif rsi and rsi > 70:
            sell_score += 30
            signal["reasons"].append(f"RSI overbought ({rsi:.1f})")

        # MACD
        macd = indicators.get("macd")
        macd_signal = indicators.get("macd_signal")
        if macd and macd_signal and macd > macd_signal:
            buy_score += 25
            signal["reasons"].append("MACD bullish crossover")
        elif macd and macd_signal and macd < macd_signal:
            sell_score += 25
            signal["reasons"].append("MACD bearish crossover")

        # میانگین‌های متحرک
        sma_20 = indicators.get("sma_20")
        sma_50 = indicators.get("sma_50")
        close = indicators.get("close", 0)
        if sma_20 and sma_50 and sma_20 > sma_50:
            buy_score += 20
            signal["reasons"].append("Golden crossover (SMA20 > SMA50)")
        elif sma_20 and sma_50 and sma_20 < sma_50:
            sell_score += 20
            signal["reasons"].append("Death cross (SMA20 < SMA50)")

        # قیمت نسبت به باندهای بولینگر
        bb_lower = indicators.get("bb_lower")
        bb_upper = indicators.get("bb_upper")
        if bb_lower and close and close <= bb_lower:
            buy_score += 15
            signal["reasons"].append("Price at lower Bollinger Band")
        elif bb_upper and close and close >= bb_upper:
            sell_score += 15
            signal["reasons"].append("Price at upper Bollinger Band")

        # الگوهای کندل استیک
        for key, value in indicators.items():
            if key.startswith("pattern_"):
                if value == "bullish":
                    buy_score += 20
                    signal["reasons"].append(f"Bullish pattern: {key.replace('pattern_', '')}")
                elif value == "bearish":
                    sell_score += 20
                    signal["reasons"].append(f"Bearish pattern: {key.replace('pattern_', '')}")

        # تعیین سیگنال نهایی
        if buy_score > sell_score and buy_score >= 40:
            signal["action"] = "BUY"
            signal["strength"] = min(100, buy_score)
            signal["risk"] = "LOW" if buy_score > 70 else "MEDIUM"
        elif sell_score > buy_score and sell_score >= 40:
            signal["action"] = "SELL"
            signal["strength"] = min(100, sell_score)
            signal["risk"] = "LOW" if sell_score > 70 else "MEDIUM"
        else:
            signal["strength"] = max(buy_score, sell_score)

        return signal

# ==================== تحلیل هوشمند با Groq AI ====================
class GroqAnalyst:
    """موتور تحلیل هوشمند با استفاده از Groq AI"""

    def __init__(self):
        self.client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    async def analyze_market(
        self,
        symbol: str,
        technical_data: Dict,
        price_data: Dict,
        news_data: Optional[str] = None
    ) -> Dict:
        """تحلیل پیشرفته بازار با هوش مصنوعی Groq"""
        if not self.client:
            return {"error": "GROQ_API_KEY تنظیم نشده است"}

        prompt = f"""
        شما یک تحلیلگر حرفه‌ای بازار ارزهای دیجیتال هستید. لطفاً بر اساس داده‌های زیر یک تحلیل کامل ارائه دهید:

        نماد: {symbol}
        قیمت فعلی: ${price_data.get('price', 'نامشخص')}
        تغییر 24h: {price_data.get('change', 'نامشخص')}%
        حجم معاملات: ${price_data.get('volume', 'نامشخص')}

        داده‌های تکنیکال:
        - RSI(14): {technical_data.get('rsi_14', 'نامشخص')}
        - MACD: {technical_data.get('macd', 'نامشخص')}
        - Signal: {technical_data.get('macd_signal', 'نامشخص')}
        - SMA20: {technical_data.get('sma_20', 'نامشخص')}
        - SMA50: {technical_data.get('sma_50', 'نامشخص')}
        - باند بالایی بولینگر: {technical_data.get('bb_upper', 'نامشخص')}
        - باند پایینی بولینگر: {technical_data.get('bb_lower', 'نامشخص')}

        {"اخبار مرتبط: " + news_data if news_data else ""}

        لطفاً پاسخ خود را در قالب JSON با کلیدهای زیر ارائه دهید:
        {{
            "signal": "BUY/SELL/HOLD",
            "confidence": 0-100,
            "technical_view": "تحلیل تکنیکال",
            "risk_assessment": "ارزیابی ریسک",
            "key_levels": {{
                "resistance": ["مقاومت اول", "مقاومت دوم"],
                "support": ["حمایت اول", "حمایت دوم"]
            }},
            "recommendation": "توصیه نهایی معاملاتی",
            "ai_analysis_summary": "خلاصه تحلیل هوش مصنوعی"
        }}
        """

        try:
            completion = await self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            result = json.loads(completion.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"خطا در تحلیل با Groq: {e}")
            return {"error": str(e), "signal": "HOLD", "confidence": 0}

# ==================== حافظه و یادگیری ====================
class MemoryManager:
    """مدیریت حافظه و یادگیری ربات از معاملات گذشته"""

    def __init__(self, data_file: str = "memory_data.json"):
        self.data_file = data_file
        self.trades = []
        self.patterns = []
        self.load_memory()

    def load_memory(self):
        """بارگذاری داده‌های حافظه از فایل"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.trades = data.get("trades", [])
                    self.patterns = data.get("patterns", [])
        except Exception as e:
            logger.error(f"خطا در بارگذاری حافظه: {e}")

    def save_memory(self):
        """ذخیره داده‌های حافظه در فایل"""
        try:
            with open(self.data_file, "w") as f:
                json.dump({"trades": self.trades, "patterns": self.patterns}, f, indent=2)
        except Exception as e:
            logger.error(f"خطا در ذخیره حافظه: {e}")

    def add_trade(self, trade_data: Dict):
        """ثبت معامله جدید در حافظه"""
        trade_data["timestamp"] = datetime.now().isoformat()
        self.trades.append(trade_data)
        self.save_memory()

    def get_win_rate(self) -> float:
        """محاسبه نرخ موفقیت معاملات گذشته"""
        if not self.trades:
            return 0.0
        winning_trades = sum(1 for trade in self.trades if trade.get("profit", 0) > 0)
        return (winning_trades / len(self.trades)) * 100

    def get_best_patterns(self) -> List[Dict]:
        """شناسایی بهترین الگوهای معاملاتی بر اساس تاریخچه"""
        pattern_stats = {}
        for trade in self.trades:
            pattern = trade.get("pattern", "unknown")
            if pattern not in pattern_stats:
                pattern_stats[pattern] = {"wins": 0, "total": 0, "profit": 0}
            pattern_stats[pattern]["total"] += 1
            if trade.get("profit", 0) > 0:
                pattern_stats[pattern]["wins"] += 1
            pattern_stats[pattern]["profit"] += trade.get("profit", 0)

        best_patterns = []
        for pattern, stats in pattern_stats.items():
            if stats["total"] >= 3:
                win_rate = (stats["wins"] / stats["total"]) * 100
                best_patterns.append({
                    "pattern": pattern,
                    "win_rate": win_rate,
                    "total_trades": stats["total"],
                    "total_profit": stats["profit"]
                })
        return sorted(best_patterns, key=lambda x: x["win_rate"], reverse=True)

# ==================== ربات اصلی ====================
class CryptoBot:
    """ربات اصلی معاملاتی"""

    def __init__(self):
        self.exchange_manager = ExchangeManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.groq_analyst = GroqAnalyst()
        self.memory_manager = MemoryManager()
        self.application = None

    async def init(self):
        """مقداردهی اولیه ربات"""
        await self.exchange_manager.init_exchanges()
        return self

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /start - نمایش منوی اصلی شیشه‌ای"""
        welcome_text = (
            "🌟 **به ربات هوشمند کریپتو خوش آمدید** 🌟\n\n"
            "من یه ربات پیشرفته و تمام‌هوشمند برای تحلیل و معامله ارزهای دیجیتال هستم.\n\n"
            "⚡ **قابلیت‌های ویژه:**\n"
            "• اتصال به ۴ صرافی معتبر بین‌المللی و نوبیتکس\n"
            "• تحلیل تکنیکال با بیش از ۲۰ اندیکاتور پیشرفته\n"
            "• تحلیل هوشمند بازار با هوش مصنوعی Groq\n"
            "• ردیابی نهنگ‌ها و تحلیل‌های آنچین\n"
            "• حافظه و یادگیری از معاملات گذشته\n"
            "• منوی کاملاً شیشه‌ای و کاربرپسند\n\n"
            "از منوی زیر قابلیت مورد نظر خودتون رو انتخاب کنید 👇"
        )
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت تمام دکمه‌های شیشه‌ای ربات"""
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "back_to_main":
            await query.edit_message_text(
                "🔙 **بازگشت به منوی اصلی**",
                parse_mode="Markdown",
                reply_markup=get_main_menu_keyboard()
            )
        elif data == "prices_menu":
            await self.show_prices_menu(query, context)
        elif data.startswith("prices_page_"):
            page = int(data.split("_")[2])
            await self.show_prices_page(query, context, page)
        elif data.startswith("prices_refresh_"):
            page = int(data.split("_")[2])
            await self.show_prices_page(query, context, page, force_refresh=True)
        elif data == "technical_menu":
            await self.technical_menu(query, context)
        elif data.startswith("analyze_"):
            symbol = data.split("_")[1]
            await self.technical_analysis(query, context, symbol)
        elif data == "ai_menu":
            await self.ai_menu(query, context)
        elif data.startswith("ai_analyze_"):
            symbol = data.split("_")[2]
            await self.ai_analysis(query, context, symbol)
        elif data == "whale_menu":
            await self.whale_menu(query, context)
        elif data == "portfolio_menu":
            await self.portfolio_menu(query, context)
        elif data == "settings_menu":
            await self.settings_menu(query, context)
        elif data == "help_menu":
            await self.help_menu(query, context)

    async def show_prices_menu(self, query, context):
        """نمایش منوی قیمت‌ها با صفحه‌بندی"""
        await self.show_prices_page(query, context, 0)

    async def show_prices_page(self, query, context, page: int, force_refresh: bool = False):
        """نمایش صفحه مشخصی از قیمت‌ها"""
        symbols_per_page = 5
        start_idx = page * symbols_per_page
        end_idx = min(start_idx + symbols_per_page, len(SYMBOLS))
        current_symbols = SYMBOLS[start_idx:end_idx]

        message = "📊 **قیمت لحظه‌ای ارزهای دیجیتال** 📊\n\n"
        for symbol in current_symbols:
            prices = await self.exchange_manager.fetch_all_prices(symbol)
            main_price = prices.get("binance", {}).get("price") or prices.get("nobitex", {}).get("price")
            if main_price:
                price_str = format_price(main_price, symbol.split("/")[1])
                exchange_names = list(prices.keys())
                message += f"• **{symbol}**: {price_str}\n   📊 {', '.join(exchange_names)}\n\n"
            else:
                message += f"• **{symbol}**: 🔴 در دسترس نیست\n\n"

        message += f"\n📌 صفحه {page + 1} از { (len(SYMBOLS) + symbols_per_page - 1) // symbols_per_page }"
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=get_prices_keyboard(page, symbols_per_page)
        )

    async def technical_menu(self, query, context):
        """نمایش منوی تحلیل تکنیکال"""
        keyboard = []
        for symbol in SYMBOLS[:10]:  # نمایش ۱۰ ارز اول
            keyboard.append([{"text": f"📈 {symbol}", "callback": f"analyze_{symbol}"}])
        keyboard.append([{"text": "🔙 بازگشت", "callback": "back_to_main"}])
        await query.edit_message_text(
            "📈 **تحلیل تکنیکال پیشرفته** 📈\n\n"
            "لطفاً ارز مورد نظر خود را برای تحلیل انتخاب کنید:\n"
            "• تحلیل شامل RSI، MACD، باندهای بولینگر و الگوهای کندل استیک\n"
            "• سیگنال معاملاتی خودکار بر اساس ترکیب اندیکاتورها",
            parse_mode="Markdown",
            reply_markup=create_glass_keyboard(keyboard)
        )

    async def technical_analysis(self, query, context, symbol: str):
        """انجام تحلیل تکنیکال روی یک ارز مشخص"""
        await query.edit_message_text(f"📊 در حال تحلیل {symbol} ... ⏳", parse_mode="Markdown")

        try:
            # دریافت داده از بایننس (صرافی اصلی)
            exchange = self.exchange_manager.exchanges.get("binance")
            if not exchange:
                await query.edit_message_text("❌ خطا: صرافی بایننس در دسترس نیست", reply_markup=get_main_menu_keyboard())
                return

            # دریافت داده‌های OHLCV
            df = await self.technical_analyzer.fetch_ohlcv(exchange, symbol, "1h", 200)

            if df.empty:
                await query.edit_message_text(f"❌ خطا در دریافت داده‌های {symbol}", reply_markup=get_main_menu_keyboard())
                return

            # محاسبه اندیکاتورها
            indicators = self.technical_analyzer.calculate_all_indicators(df)

            # دریافت قیمت فعلی
            ticker = await exchange.fetch_ticker(symbol)
            current_price = safe_decimal(ticker.get("last", 0))

            # تولید سیگنال
            signal = self.technical_analyzer.generate_signal(indicators)

            # ساخت پیام تحلیل
            analysis_text = f"📈 **تحلیل تکنیکال {symbol}** 📈\n\n"
            analysis_text += f"💰 **قیمت فعلی:** {format_price(current_price, symbol.split('/')[1])}\n\n"

            analysis_text += "**📊 اندیکاتورهای اصلی:**\n"
            analysis_text += f"• RSI(14): {indicators.get('rsi_14', 'نامشخص'):.1f}\n"
            analysis_text += f"• MACD: {indicators.get('macd', 'نامشخص'):.4f}\n"
            analysis_text += f"• Signal: {indicators.get('macd_signal', 'نامشخص'):.4f}\n"
            analysis_text += f"• SMA20: {format_price(safe_decimal(indicators.get('sma_20', 0)), symbol.split('/')[1])}\n"
            analysis_text += f"• SMA50: {format_price(safe_decimal(indicators.get('sma_50', 0)), symbol.split('/')[1])}\n\n"

            analysis_text += "🎯 **سیگنال معاملاتی:**\n"
            if signal["action"] == "BUY":
                analysis_text += f"🟢 **خرید** - قدرت: {signal['strength']}%\n"
            elif signal["action"] == "SELL":
                analysis_text += f"🔴 **فروش** - قدرت: {signal['strength']}%\n"
            else:
                analysis_text += f"⚪ **نگهداری** - قدرت: {signal['strength']}%\n"

            analysis_text += f"📊 **ریسک:** {signal['risk']}\n"
            if signal["reasons"]:
                analysis_text += "\n**📝 دلایل سیگنال:**\n"
                for reason in signal["reasons"][:5]:
                    analysis_text += f"• {reason}\n"

            # دکمه بازگشت
            keyboard = [[{"text": "🔙 بازگشت به منوی تکنیکال", "callback": "technical_menu"}]]
            await query.edit_message_text(
                analysis_text,
                parse_mode="Markdown",
                reply_markup=create_glass_keyboard(keyboard)
            )

        except Exception as e:
            logger.error(f"خطا در تحلیل تکنیکال {symbol}: {e}")
            await query.edit_message_text(
                f"❌ خطا در تحلیل {symbol}: {str(e)}",
                reply_markup=get_main_menu_keyboard()
            )

    async def ai_menu(self, query, context):
        """نمایش منوی تحلیل هوشمند AI"""
        keyboard = []
        for symbol in SYMBOLS[:10]:
            keyboard.append([{"text": f"🧠 {symbol}", "callback": f"ai_analyze_{symbol}"}])
        keyboard.append([{"text": "🔙 بازگشت", "callback": "back_to_main"}])
        await query.edit_message_text(
            "🧠 **تحلیل هوشمند بازار با AI** 🧠\n\n"
            "تحلیل پیشرفته با استفاده از هوش مصنوعی Groq:\n"
            "• ترکیب تحلیل تکنیکال و فاندامنتال\n"
            "• ارزیابی ریسک و سطوح کلیدی\n"
            "• توصیه معاملاتی با درصد اطمینان\n\n"
            "لطفاً ارز مورد نظر را انتخاب کنید:",
            parse_mode="Markdown",
            reply_markup=create_glass_keyboard(keyboard)
        )

    async def ai_analysis(self, query, context, symbol: str):
        """انجام تحلیل هوشمند با Groq AI"""
        await query.edit_message_text(f"🤖 در حال تحلیل {symbol} با هوش مصنوعی... ⏳", parse_mode="Markdown")

        try:
            exchange = self.exchange_manager.exchanges.get("binance")
            if not exchange:
                await query.edit_message_text("❌ خطا: صرافی بایننس در دسترس نیست", reply_markup=get_main_menu_keyboard())
                return

            # دریافت داده‌های تکنیکال
            df = await self.technical_analyzer.fetch_ohlcv(exchange, symbol, "1h", 200)
            if df.empty:
                await query.edit_message_text(f"❌ خطا در دریافت داده‌های {symbol}", reply_markup=get_main_menu_keyboard())
                return

            indicators = self.technical_analyzer.calculate_all_indicators(df)

            # دریافت قیمت فعلی
            ticker = await exchange.fetch_ticker(symbol)
            price_data = {
                "price": ticker.get("last", 0),
                "change": ticker.get("percentage", 0),
                "volume": ticker.get("quoteVolume", 0),
            }

            # تحلیل با Groq
            analysis = await self.groq_analyst.analyze_market(symbol, indicators, price_data)

            if "error" in analysis:
                await query.edit_message_text(f"❌ {analysis['error']}", reply_markup=get_main_menu_keyboard())
                return

            # ساخت پیام تحلیل
            message = f"🤖 **تحلیل هوشمند {symbol} با AI** 🤖\n\n"
            message += f"💰 **قیمت فعلی:** {format_price(safe_decimal(price_data['price']), symbol.split('/')[1])}\n"
            message += f"📊 **تغییر ۲۴ ساعته:** {price_data['change']:.2f}%\n\n"

            message += f"🎯 **سیگنال نهایی:** "
            if analysis.get("signal") == "BUY":
                message += "🟢 **خرید**\n"
            elif analysis.get("signal") == "SELL":
                message += "🔴 **فروش**\n"
            else:
                message += "⚪ **نگهداری**\n"

            message += f"⚡ **اطمینان AI:** {analysis.get('confidence', 0)}%\n"
            message += f"📈 **تحلیل تکنیکال:** {analysis.get('technical_view', 'نامشخص')}\n"
            message += f"⚠️ **ارزیابی ریسک:** {analysis.get('risk_assessment', 'نامشخص')}\n"

            # سطوح کلیدی
            key_levels = analysis.get("key_levels", {})
            if key_levels:
                message += "\n🔑 **سطوح کلیدی:**\n"
                if key_levels.get("resistance"):
                    message += f"• مقاومت‌ها: {', '.join(key_levels['resistance'])}\n"
                if key_levels.get("support"):
                    message += f"• حمایت‌ها: {', '.join(key_levels['support'])}\n"

            message += f"\n💡 **توصیه نهایی:**\n{analysis.get('recommendation', 'نامشخص')}\n"
            message += f"\n🧠 **خلاصه تحلیل AI:**\n{analysis.get('ai_analysis_summary', 'نامشخص')}"

            keyboard = [[{"text": "🔙 بازگشت به منوی AI", "callback": "ai_menu"}]]
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=create_glass_keyboard(keyboard)
            )

        except Exception as e:
            logger.error(f"خطا در تحلیل هوشمند {symbol}: {e}")
            await query.edit_message_text(
                f"❌ خطا در تحلیل هوشمند: {str(e)}",
                reply_markup=get_main_menu_keyboard()
            )

    async def whale_menu(self, query, context):
        """نمایش منوی ردیابی نهنگ‌ها"""
        message = (
            "🐋 **ردیابی نهنگ‌ها و تحلیل آنچین** 🐋\n\n"
            "🔍 **قابلیت‌های ردیابی نهنگ:**\n"
            "• رصد تراکنش‌های بزرگ بالای ۱ میلیون دلار\n"
            "• تحلیل حرکت وال‌ها بین صرافی‌ها\n"
            "• شناسایی الگوهای انباشت و توزیع\n"
            "• هشدار لحظه‌ای ورود و خروج نهنگ‌ها\n\n"
            "📌 این بخش در حال توسعه است و به زودی تکمیل می‌شود.\n"
            "🔄 پیشنهاد می‌شود از بخش تحلیل تکنیکال و هوشمند استفاده کنید."
        )
        keyboard = [[{"text": "🔙 بازگشت به منو", "callback": "back_to_main"}]]
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=create_glass_keyboard(keyboard)
        )

    async def portfolio_menu(self, query, context):
        """نمایش منوی پرتفوی و معاملات"""
        win_rate = self.memory_manager.get_win_rate()
        best_patterns = self.memory_manager.get_best_patterns()

        message = (
            "📊 **پرتفوی و مدیریت معاملات** 📊\n\n"
            f"🎯 **نرخ موفقیت کلی:** {win_rate:.1f}%\n"
            f"📝 **تعداد کل معاملات:** {len(self.memory_manager.trades)}\n\n"
        )

        if best_patterns:
            message += "🏆 **بهترین الگوهای معاملاتی:**\n"
            for pattern in best_patterns[:3]:
                message += f"• {pattern['pattern']}: {pattern['win_rate']:.1f}% موفقیت ({pattern['total_trades']} معامله)\n"

        message += (
            "\n⚡ **قابلیت‌های مدیریت:**\n"
            "• ثبت خودکار معاملات\n"
            "• تحلیل بازدهی استراتژی‌ها\n"
            "• یادگیری از معاملات موفق و ناموفق\n\n"
            "📌 برای ثبت معامله جدید از طریق دستورات استفاده کنید."
        )
        keyboard = [[{"text": "🔙 بازگشت به منو", "callback": "back_to_main"}]]
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=create_glass_keyboard(keyboard)
        )

    async def settings_menu(self, query, context):
        """نمایش منوی تنظیمات"""
        message = (
            "⚙️ **تنظیمات ربات** ⚙️\n\n"
            "🔧 **تنظیمات قابل سفارشی‌سازی:**\n"
            "• انتخاب صرافی پیش‌فرض\n"
            "• تنظیم هشدار قیمت\n"
            "• فعال/غیرفعال کردن تحلیل خودکار\n"
            "• تنظیم حد ضرر و حد سود\n\n"
            "📌 این بخش در حال توسعه است.\n"
            "برای تنظیمات اولیه از متغیرهای محیطی استفاده کنید."
        )
        keyboard = [[{"text": "🔙 بازگشت به منو", "callback": "back_to_main"}]]
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=create_glass_keyboard(keyboard)
        )

    async def help_menu(self, query, context):
        """نمایش منوی راهنما"""
        message = (
            "❓ **راهنما و پشتیبانی** ❓\n\n"
            "📚 **دستورات قابل استفاده:**\n"
            "• /start - نمایش منوی اصلی\n"
            "• /help - نمایش این راهنما\n"
            "• /status - وضعیت اتصال به صرافی‌ها\n\n"
            "🔧 **نیازمندی‌های فنی:**\n"
            "• Python 3.9+\n"
            "• TA-Lib (نیاز به نصب جداگانه)\n"
            "• متغیرهای محیطی معتبر\n\n"
            "💬 **پشتیبانی:**\n"
            "در صورت بروز مشکل، لاگ‌های Railway را بررسی کنید.\n\n"
            "⚠️ **هشدار ریسک:**\n"
            "این ربات فقط برای اهداف آموزشی و اطلاع‌رسانی است. تصمیمات معاملاتی با مسئولیت خودتان انجام می‌شود."
        )
        keyboard = [[{"text": "🔙 بازگشت به منو", "callback": "back_to_main"}]]
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=create_glass_keyboard(keyboard)
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /status - نمایش وضعیت اتصال به صرافی‌ها"""
        status_text = "🔌 **وضعیت اتصال به صرافی‌ها** 🔌\n\n"
        for name, exchange in self.exchange_manager.exchanges.items():
            status_text += f"✅ {name}: متصل\n"
        if self.exchange_manager.nobitex_client:
            status_text += "✅ nobitex: متصل (با پشتیبانی 2FA)\n"
        await update.message.reply_text(status_text, parse_mode="Markdown")

    async def run(self):
        """اجرای اصلی ربات"""
        self.application = Application.builder().token(TELEGRAM_TOKEN).build()

        # ثبت هندلرها
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_menu))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))

        # راه‌اندازی ربات
        logger.info("ربات هوشمند کریپتو راه‌اندازی شد...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await asyncio.Event().wait()  # منتظر ماندن تا زمان دریافت سیگنال پایان

# اجرای ربات
async def main():
    bot = CryptoBot()
    await bot.init()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
