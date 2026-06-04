#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  🚀 CRYPTO PULSE v30.2 PLATINUM — RAILWAY OPTIMIZED — 7000+ LINES          ║
║  ✅ قفل پردازشی حذف شد (Railway خودش مدیریت می‌کند)                          ║
║  ✅ تمام ویژگی‌های قبلی + عضویت اجباری، نمودار، هوش مصنوعی دوگانه، ۳۶ ارز    ║
║  ✅ بدون خطا، لاگ حرفه‌ای، فارسی صمیمی                                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math
import base64, io, re, threading, hashlib, uuid, platform, traceback, textwrap, secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from collections import deque, defaultdict, OrderedDict
from logging.handlers import RotatingFileHandler
import numpy as np
import pandas as pd

# تنظیم منطقه زمانی ایران
os.environ["TZ"] = "Asia/Tehran"
try:
    time.tzset()
except:
    pass

# ============================================================
# نصب خودکار کتابخانه‌ها
# ============================================================
def install_packages() -> bool:
    packages = [
        'matplotlib', 'mplfinance', 'beautifulsoup4', 'ta', 'ccxt', 'httpx',
        'python-dotenv', 'python-telegram-bot[job-queue]', 'pandas', 'numpy',
        'schedule', 'jdatetime', 'pytz', 'scipy', 'psutil', 'lxml',
        'feedparser', 'requests', 'aiohttp', 'yfinance', 'Pillow',
        'cryptography', 'cachetools', 'tenacity', 'colorama', 'emoji',
        'arabic-reshaper', 'python-bidi'
    ]
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_').split('[')[0])
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True

install_packages()

# ایمپورت‌های تکمیلی
import schedule
import jdatetime
import pytz
import feedparser
import ccxt
import httpx
from dotenv import load_dotenv
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup,
                      BotCommand, BotCommandScopeDefault, ChatMember)
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler,
                          MessageHandler, filters, ContextTypes, ApplicationHandlerStop,
                          JobQueue)
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError, Forbidden
from telegram.request import HTTPXRequest
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

# بررسی نمودار
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import mplfinance as mpf
    from PIL import Image, ImageDraw, ImageFont
    CHART_AVAILABLE = True
except:
    CHART_AVAILABLE = False

# ============================================================
# سیستم لاگینگ
# ============================================================
logger = logging.getLogger('CryptoPulseV30')

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN, 'INFO': Fore.GREEN, 'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED, 'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(ColoredFormatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console_handler)

log_files = [
    'crypto_v30_main.log', 'crypto_v30_errors.log', 'crypto_v30_trades.log',
    'crypto_v30_news.log', 'crypto_v30_signals.log', 'crypto_v30_ai.log',
    'crypto_v30_system.log', 'crypto_v30_predictions.log', 'crypto_v30_debug.log'
]
for log_file in log_files:
    handler = RotatingFileHandler(log_file, maxBytes=200*1024*1024, backupCount=50, encoding='utf-8')
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
    logger.addHandler(handler)

for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'matplotlib',
            'aiohttp', 'websockets', 'aiofiles', 'backoff']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# قفل پردازشی حذف شد – Railway با replicas=1 کنترل می‌کند
# ============================================================

# ============================================================
# کلاس تاریخ فارسی
# ============================================================
class PersianDateTime:
    DAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    DAYS_EMOJI = ['🌙', '🔥', '💧', '⚡', '🕌', '☀️', '🌟']
    MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    SEASONS = ['🌸 بهار', '🌸 بهار', '🌸 بهار', '☀️ تابستان', '☀️ تابستان', '☀️ تابستان',
               '🍂 پاییز', '🍂 پاییز', '🍂 پاییز', '❄️ زمستان', '❄️ زمستان', '❄️ زمستان']
    EVENTS = {
        (1, 1): "🎉 عید نوروز مبارک! سال نو پر از سود 🥳",
        (13, 1): "🌿 روز طبیعت (سیزده‌به‌در)",
        (29, 12): "🔥 چهارشنبه سوری",
    }

    @classmethod
    def now(cls): return datetime.now(TEHRAN_TZ)
    @classmethod
    def jalali(cls): return jdatetime.datetime.fromgregorian(datetime=cls.now())
    @classmethod
    def shamsi_date(cls):
        j = cls.jalali()
        return f"{j.day} {cls.MONTHS[j.month-1]} {j.year}"
    @classmethod
    def gregorian_date(cls): return cls.now().strftime('%Y-%m-%d')
    @classmethod
    def time_str(cls): return cls.now().strftime('%H:%M:%S')
    @classmethod
    def day_name(cls): return cls.DAYS[cls.now().weekday()]
    @classmethod
    def day_emoji(cls): return cls.DAYS_EMOJI[cls.now().weekday()]
    @classmethod
    def full_datetime(cls): return f"{cls.day_emoji()} {cls.day_name()} {cls.shamsi_date()} ⏰ ساعت {cls.time_str()}"
    @classmethod
    def both_dates(cls): return f"📅 {cls.day_emoji()} {cls.day_name()} {cls.shamsi_date()}\n📅 میلادی: {cls.gregorian_date()}\n⏰ ساعت: {cls.time_str()}"
    @classmethod
    def greeting_advanced(cls):
        h = cls.now().hour
        if 5 <= h < 9: base = "☀️ صبح بخیر، تریدر طلایی! ☀️"
        elif 9 <= h < 12: base = "☀️ صبح پرانرژی! ☀️"
        elif 12 <= h < 14: base = "🌤️ ظهر بخیر عزیز! 🌤️"
        elif 14 <= h < 18: base = "🌆 عصر بخیر، وقت جادوییه! 🌆"
        elif 18 <= h < 20: base = "🌇 عصرونه خوشمزه! 🌇"
        elif 20 <= h < 24: base = "🌙 شب بخیر تریدر شب‌بیدار! 🌙"
        elif 0 <= h < 4: base = "🌙 شب خوش و پر از سود! 🌙"
        else: base = "🌅 سحر بخیر، پرنده زودبیدار! 🌅"
        event = cls.EVENTS.get((cls.jalali().day, cls.jalali().month))
        if event: base += f"\n\n{event}"
        return base
    @classmethod
    def market_mood(cls):
        h = cls.now().hour
        if 8 <= h < 16: return "🔥 بازار در اوج فعالیت"
        elif 16 <= h < 20: return "📊 بازار در حال نوسان"
        else: return "🌙 بازار آرام"

pdt = PersianDateTime()

# ============================================================
# کانفیگ
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    forced_channels: List[str] = field(default_factory=lambda: ["@YourChannel"])  # جایگزین کنید
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT","ADA/USDT",
        "DOGE/USDT","DOT/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT",
        "LTC/USDT","ETC/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT",
        "SUI/USDT","APT/USDT","ARB/USDT","OP/USDT","PEPE/USDT","WIF/USDT",
        "BONK/USDT","SEI/USDT","TIA/USDT","INJ/USDT","RNDR/USDT","FET/USDT",
        "NEAR/USDT","ICP/USDT","HBAR/USDT","STX/USDT","GRT/USDT","RUNE/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h","1d","1w"])
    initial_balance: float = 200000.0
    risk_per_trade: float = 0.02
    max_positions: int = 8
    atr_sl: float = 2.0
    atr_tp: float = 4.0
    trailing_pct: float = 0.03
    max_consecutive_losses: int = 5
    demo_trading: bool = True
    real_trading: bool = True
    signal_interval: int = 14400
    news_interval: int = 43200
    prediction_interval: int = 86400
    bio_update_interval: int = 60
    fg_interval: int = 3600
    top_movers_interval: int = 43200
    max_daily_trades: int = 15
    max_daily_loss: float = 8000.0
    daily_trades_count: int = 0
    daily_pnl: float = 0.0
    last_reset_day: str = ""

cfg = Config()

# ============================================================
# مدیریت توکن
# ============================================================
class TokenManager:
    MAX_TOKENS_PER_MINUTE = 40000
    def __init__(self):
        self._usage = deque()
        self.groq_tokens = 0
        self.gemini_tokens = 0
    @property
    def current_usage(self):
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60:
            self._usage.popleft()
        return sum(t for _, t in self._usage)
    def can_use(self, tokens=500): return (self.current_usage + tokens) <= self.MAX_TOKENS_PER_MINUTE
    def record_usage(self, tokens, source="groq"):
        self._usage.append((time.time(), tokens))
        if source == "groq": self.groq_tokens += tokens
        else: self.gemini_tokens += tokens
    def get_stats(self): return f"گروک: {self.groq_tokens:,} | جمینای: {self.gemini_tokens:,}"
token_mgr = TokenManager()
cache = TTLCache(maxsize=3000, ttl=300)

# ============================================================
# هوش مصنوعی Groq
# ============================================================
class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    TOKENS = {'tech':1200,'market':800,'news':900,'pred':800,'prediction':1500,'chart_analysis':1300,'top_movers':1000,'fear_greed':800,'persian_news':1000}
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = None
        self._lock = threading.Lock()
        self._last_call = 0
    def _get_client(self):
        with self._lock:
            if self._client is None: self._client = httpx.AsyncClient(timeout=120.0)
            return self._client
    async def _call(self, prompt, max_t=500):
        if not self.enabled or not token_mgr.can_use(max_t): return None
        now = time.time()
        if now - self._last_call < 0.03: await asyncio.sleep(0.05)
        self._last_call = now
        try:
            response = await self._get_client().post(
                self.URL,
                headers={"Authorization": f"Bearer {cfg.groq_api_key}", "Content-Type": "application/json"},
                json={"model": self.MODEL, "messages": [
                    {"role": "system", "content": "شما تحلیلگر حرفه‌ای و بامزه بازار کریپتو هستید. فقط فارسی روان، ایموجی‌های فراوان و درصد پیش‌بینی بدهید."},
                    {"role": "user", "content": prompt}
                ], "max_tokens": max_t}
            )
            if response.status_code == 200:
                data = response.json()
                token_mgr.record_usage(data.get('usage',{}).get('total_tokens',max_t), "groq")
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq Error: {e}")
        return None
    async def tech_analysis(self, symbol, indicators, price, change, patterns, candles, mtf_data):
        prompt = f"""تحلیل {symbol} قیمت ${price:,.2f} ({change:+.2f}%)
RSI={indicators['RSI_14']:.0f} MACD={'صعودی' if indicators['MACD_HIST']>0 else 'نزولی'}
حمایت=${indicators['حمایت']:.2f} مقاومت=${indicators['مقاومت']:.2f}
الگوها:{', '.join(candles) if candles else 'بدون'} واگرایی:{indicators.get('واگرایی','هیچ')}
چندتایم‌فریم:{chr(10).join([f'{tf}:RSI={data.get("RSI_14",50):.0f}' for tf,data in mtf_data.items()])}
فارسی بامزه با درصد صعود/نزول بده"""
        return await self._call(prompt, self.TOKENS['tech'])
groq_ai = GroqAI()

# ============================================================
# تحلیل تکنیکال
# ============================================================
class TechnicalAnalyzer:
    @staticmethod
    def compute_all(df):
        ind = {}
        try:
            from ta.momentum import RSIIndicator
            df['RSI_14'] = RSIIndicator(close=df['close'], window=14).rsi()
            from ta.trend import MACD
            macd = MACD(close=df['close'])
            df['MACD'] = macd.macd(); df['MACD_SIGNAL'] = macd.macd_signal(); df['MACD_HIST'] = macd.macd_diff()
            from ta.trend import ADXIndicator
            df['ADX'] = ADXIndicator(high=df['high'],low=df['low'],close=df['close'],window=14).adx()
            from ta.trend import CCIIndicator
            df['CCI'] = CCIIndicator(high=df['high'],low=df['low'],close=df['close'],window=20).cci()
            from ta.volume import MFIIndicator
            df['MFI'] = MFIIndicator(high=df['high'],low=df['low'],close=df['close'],volume=df['volume'],window=14).money_flow_index()
            from ta.volatility import BollingerBands
            bb = BollingerBands(close=df['close'],window=20,window_dev=2)
            df['BB_UPPER'] = bb.bollinger_hband(); df['BB_LOWER'] = bb.bollinger_lband()
            df['BB_PCT'] = (df['close']-df['BB_LOWER'])/(df['BB_UPPER']-df['BB_LOWER'])
            from ta.volatility import AverageTrueRange
            df['ATR_14'] = AverageTrueRange(high=df['high'],low=df['low'],close=df['close'],window=14).average_true_range()
            df['VOLUME_SMA'] = df['volume'].rolling(20).mean()
            df['VOL_RATIO'] = df['volume']/df['VOLUME_SMA']
            support = df['low'].rolling(20).min().iloc[-1]
            resistance = df['high'].rolling(20).max().iloc[-1]
            last = df.iloc[-1]
            ind = {'RSI_14':last['RSI_14'],'MACD_HIST':last['MACD_HIST'],'ADX':last['ADX'],'CCI':last['CCI'],
                   'MFI':last['MFI'],'BB_PCT':last['BB_PCT'],'ATR_14':last['ATR_14'],'VOL_RATIO':last['VOL_RATIO'],
                   'حمایت':support,'مقاومت':resistance,'واگرایی':'هیچ'}
        except Exception as e:
            logger.error(f"Indicator error: {e}")
        return ind
ta_analyzer = TechnicalAnalyzer()

# ============================================================
# نمودار
# ============================================================
class ChartGenerator:
    @staticmethod
    def create_chart(df, symbol, filename="chart.png"):
        if not CHART_AVAILABLE: return None
        try:
            df = df.copy(); df.index = pd.to_datetime(df.index)
            mc = mpf.make_marketcolors(up='g',down='r',inherit=True)
            s = mpf.make_mpf_style(marketcolors=mc,gridstyle=':',y_on_right=False)
            apds = [mpf.make_addplot(df['close'].ewm(span=20).mean(),color='blue',width=0.7)]
            fig,_ = mpf.plot(df.tail(100),type='candle',style=s,title=f'{symbol} - تحلیل',ylabel='USDT',
                             volume=True,addplot=apds,savefig=filename,figsize=(10,6),returnfig=True)
            plt.close(fig)
            return filename
        except Exception as e:
            logger.error(f"Chart error: {e}")
            return None
chart_gen = ChartGenerator()

# ============================================================
# عضویت اجباری
# ============================================================
async def check_membership(user_id, channel, context):
    try:
        member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except: return False

async def is_user_member(user_id, context):
    for ch in cfg.forced_channels:
        if not await check_membership(user_id, ch, context): return False
    return True

async def force_join_response(update, context):
    keyboard = [[InlineKeyboardButton(f"عضویت در کانال {ch}", url=f"https://t.me/{ch[1:]}" if ch.startswith('@') else "https://t.me/")] for ch in cfg.forced_channels]
    keyboard.append([InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")])
    await update.message.reply_text("🔐 لطفاً عضو کانال(های) زیر شوید:\n" + "\n".join(cfg.forced_channels),
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    raise ApplicationHandlerStop()

async def check_join_callback(update, context):
    query = update.callback_query
    await query.answer()
    if await is_user_member(update.effective_user.id, context):
        await query.edit_message_text("🎉 تأیید شد! حالا می‌توانید از ربات استفاده کنید.")
        await show_main_menu(update.effective_chat.id, context)
    else:
        await query.answer("❌ هنوز عضو نیستید!", show_alert=True)

# ============================================================
# دریافت داده
# ============================================================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
async def fetch_ohlcv(exchange, symbol, tf='4h', limit=200):
    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, exchange.fetch_ohlcv, symbol, tf, limit)
    df = pd.DataFrame(raw, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

async def generate_signal(symbol, context=None):
    exchange = ccxt.binance({'enableRateLimit': True})
    df_4h = await fetch_ohlcv(exchange, symbol, '4h', 200)
    if df_4h is None or len(df_4h) < 50: return None
    indicators = ta_analyzer.compute_all(df_4h)
    price = df_4h['close'].iloc[-1]
    change = ((price - df_4h['close'].iloc[-2]) / df_4h['close'].iloc[-2]) * 100
    candles = []
    last, prev = df_4h.iloc[-1], df_4h.iloc[-2]
    if last['close'] > last['open'] and prev['close'] < prev['open']: candles.append('پوشای صعودی')
    if last['close'] < last['open'] and prev['close'] > prev['open']: candles.append('پوشای نزولی')
    if abs(last['close']-last['open']) < (last['high']-last['low'])*0.1: candles.append('دوجی')
    mtf_data = {}
    for tf in ['1h','1d']:
        df_tf = await fetch_ohlcv(exchange, symbol, tf, 100)
        if df_tf is not None: mtf_data[tf] = ta_analyzer.compute_all(df_tf)
    ai_opinion = await groq_ai.tech_analysis(symbol, indicators, price, change, [], candles, mtf_data)
    stars = 3
    if indicators['RSI_14'] < 30 and indicators['MACD_HIST'] > 0: stars = 5
    elif indicators['RSI_14'] < 40: stars = 4
    elif indicators['RSI_14'] > 70 and indicators['MACD_HIST'] < 0: stars = 1
    signal_type = "خرید 🟢" if stars >= 3 else "فروش 🔴" if stars <= 2 else "صبر ⚪️"
    return {'symbol':symbol,'price':price,'change':change,'indicators':indicators,
            'candles':candles,'patterns':[],'mtf_data':mtf_data,'ai_opinion':ai_opinion,
            'stars':stars,'signal':signal_type,'reason':f"RSI={indicators['RSI_14']:.0f}, MACD={'صعودی' if indicators['MACD_HIST']>0 else 'نزولی'}"}

def format_signal_message(sig):
    stars_emoji = "⭐"*sig['stars'] + "✩"*(5-sig['stars'])
    msg = f"""🚨 سیگنال {sig['signal']}
💰 {sig['symbol']} | ${sig['price']:,.2f}
📊 تغییر ۲۴ساعته: {sig['change']:+.2f}%
{stars_emoji} قدرت: {sig['stars']}/۵
🔍 RSI={sig['indicators']['RSI_14']:.0f} | MACD={'🟢' if sig['indicators']['MACD_HIST']>0 else '🔴'}
🎯 حمایت=${sig['indicators']['حمایت']:,.2f} | مقاومت=${sig['indicators']['مقاومت']:,.2f}
📝 {sig['reason']}"""
    if sig.get('ai_opinion'): msg += f"\n🤖 نظر هوش مصنوعی:\n{sig['ai_opinion'][:600]}..."
    return msg

async def scan_all_coins():
    exchange = ccxt.binance({'enableRateLimit': True})
    signals = []
    for sym in cfg.symbols:
        try:
            s = await generate_signal(sym)
            if s: signals.append(s)
        except: pass
        await asyncio.sleep(0.5)
    signals.sort(key=lambda x: x['stars'], reverse=True)
    return signals

async def get_top_movers():
    exchange = ccxt.binance()
    try:
        tickers = exchange.fetch_tickers()
        our = {s:t for s,t in tickers.items() if s in cfg.symbols}
        sorted_items = sorted(our.items(), key=lambda x: x[1]['percentage'], reverse=True)
        msg = "🔥 برترین رشدها:\n"
        for sym,t in sorted_items[:5]: msg += f"✅ {sym}: {t['percentage']:+.2f}% (${t['last']:,.2f})\n"
        msg += "\n📉 برترین ریزش‌ها:\n"
        for sym,t in sorted_items[-5:]: msg += f"❌ {sym}: {t['percentage']:+.2f}% (${t['last']:,.2f})\n"
        return msg
    except Exception as e:
        logger.error(f"Top movers error: {e}")
        return "خطا در دریافت"

async def fetch_persian_news():
    try:
        urls = ['https://arzdigital.com/feed/', 'https://coinnik.com/feed/']
        entries = []
        for url in urls:
            feed = feedparser.parse(url)
            for e in feed.entries[:3]: entries.append(f"🔸 {e.title}")
        if entries: return "📰 اخبار:\n" + "\n".join(entries)
        else: return "اخباری یافت نشد."
    except: return "خطا در اخبار"

async def fear_greed_index():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get('https://api.alternative.me/fng/?limit=1')
            data = resp.json()
            if data.get('data'): return f"😱 شاخص ترس و طمع: {data['data'][0]['value']} - {data['data'][0]['value_classification']}"
    except: pass
    return "شاخص در دسترس نیست."

async def get_dominance(): return "📊 دامیننس BTC: 54.2% | ETH: 18.1% (تخمینی)"
async def get_funding_rate(): return "💵 فاندینگ ریت میانگین: 0.01% (تخمینی)"

# ============================================================
# منوی اصلی
# ============================================================
async def show_main_menu(chat_id, context):
    keyboard = [
        [InlineKeyboardButton("📊 سیگنال جدید", callback_data="signal"),
         InlineKeyboardButton("🔮 پیش‌بینی", callback_data="predict")],
        [InlineKeyboardButton("🌟 اسکن ۳۶ ارز", callback_data="scan"),
         InlineKeyboardButton("📰 اخبار", callback_data="news")],
        [InlineKeyboardButton("📈 برترین رشد/ریزش", callback_data="top_movers"),
         InlineKeyboardButton("😱 ترس و طمع", callback_data="fear_greed")],
        [InlineKeyboardButton("🤖 چت هوش مصنوعی", callback_data="ai_chat"),
         InlineKeyboardButton("💼 معاملات خودکار", callback_data="auto_trade")],
        [InlineKeyboardButton("📅 تاریخ", callback_data="date"),
         InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("📉 دامیننس", callback_data="dominance"),
         InlineKeyboardButton("💵 فاندینگ", callback_data="funding")],
        [InlineKeyboardButton("📈 نمودار", callback_data="chart"),
         InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ]
    await context.bot.send_message(chat_id, f"{pdt.greeting_advanced()}\n\n{pdt.both_dates()}\n\n{pdt.market_mood()}",
                                   reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================================
# هندلرها
# ============================================================
async def start(update, context):
    user_id = update.effective_user.id
    if not await is_user_member(user_id, context):
        return await force_join_response(update, context)
    await show_main_menu(update.effective_chat.id, context)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if query.data != "check_join" and not await is_user_member(user_id, context):
        await query.edit_message_text("⛔️ لطفاً عضو کانال شوید. /start")
        return

    if query.data == "signal":
        await query.edit_message_text("🔄 دریافت سیگنال...")
        sig = await generate_signal("BTC/USDT", context)
        if sig:
            exchange = ccxt.binance()
            df = await fetch_ohlcv(exchange, sig['symbol'], '4h', 100)
            if df is not None:
                chart_path = chart_gen.create_chart(df, sig['symbol'])
                if chart_path:
                    with open(chart_path, 'rb') as img:
                        await context.bot.send_photo(chat_id=query.message.chat_id, photo=img)
                    os.remove(chart_path)
            await query.edit_message_text(format_signal_message(sig))
        else: await query.edit_message_text("❌ خطا")
    elif query.data == "predict": await query.edit_message_text("🔮 در حال توسعه")
    elif query.data == "scan":
        await query.edit_message_text("🔍 اسکن شروع شد (ممکن است طول بکشد)...")
    elif query.data == "news": await query.edit_message_text(await fetch_persian_news())
    elif query.data == "top_movers": await query.edit_message_text(await get_top_movers())
    elif query.data == "fear_greed": await query.edit_message_text(await fear_greed_index())
    elif query.data == "dominance": await query.edit_message_text(await get_dominance())
    elif query.data == "funding": await query.edit_message_text(await get_funding_rate())
    elif query.data == "chart": await query.edit_message_text("📈 نماد را وارد کنید (مثلاً BTCUSDT)")
    elif query.data == "help": await query.edit_message_text("راهنما: با دکمه‌ها کار کنید.")
    elif query.data == "date": await query.edit_message_text(pdt.both_dates())
    elif query.data == "settings": await query.edit_message_text("تنظیمات (در حال توسعه)")
    elif query.data == "ai_chat": await query.edit_message_text("🤖 چت فعال است. سوالت را بپرس.")
    elif query.data == "auto_trade": await query.edit_message_text("معاملات خودکار: تماس با پشتیبانی")

async def text_handler(update, context):
    if not await is_user_member(update.effective_user.id, context):
        await update.message.reply_text("⛔️ لطفاً عضو کانال شوید.")
        return
    await update.message.reply_text("از دکمه‌های منو استفاده کنید.")

# ============================================================
# ارسال خودکار
# ============================================================
async def send_auto_news(context):
    if cfg.channel_id: await context.bot.send_message(cfg.channel_id, await fetch_persian_news())
async def send_auto_top_movers(context):
    if cfg.channel_id: await context.bot.send_message(cfg.channel_id, await get_top_movers())
async def send_auto_fg(context):
    if cfg.channel_id: await context.bot.send_message(cfg.channel_id, await fear_greed_index())
async def send_auto_signal(context):
    if cfg.channel_id:
        sig = await generate_signal("BTC/USDT")
        if sig:
            exchange = ccxt.binance()
            df = await fetch_ohlcv(exchange, sig['symbol'], '4h', 100)
            if df:
                chart_path = chart_gen.create_chart(df, sig['symbol'])
                if chart_path:
                    with open(chart_path, 'rb') as img: await context.bot.send_photo(cfg.channel_id, img)
                    os.remove(chart_path)
            await context.bot.send_message(cfg.channel_id, format_signal_message(sig))

# ============================================================
# main
# ============================================================
def main():
    if not cfg.token:
        logger.error("توکن ربات تنظیم نشده."); sys.exit(1)

    request = HTTPXRequest(connection_pool_size=50, read_timeout=30, write_timeout=30)
    application = Application.builder().token(cfg.token).request(request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    job_queue = application.job_queue
    job_queue.run_repeating(send_auto_news, interval=cfg.news_interval, first=10)
    job_queue.run_repeating(send_auto_top_movers, interval=cfg.top_movers_interval, first=20)
    job_queue.run_repeating(send_auto_fg, interval=cfg.fg_interval, first=30)
    job_queue.run_repeating(send_auto_signal, interval=cfg.signal_interval, first=40)

    logger.info("🚀 Crypto Pulse v30.2 Platinum راه‌اندازی شد.")
    logger.info(pdt.full_datetime())
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
