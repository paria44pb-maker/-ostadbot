#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║   CRYPTO PULSE ULTIMATE DUAL AI TRADING BOT v10.1 - FIXED           ║
║   Fixed Markdown Parse Error | All Features Preserved                ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import numpy as np
import pandas as pd
import ccxt
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
from telegram.constants import ParseMode
import warnings
warnings.filterwarnings('ignore')

# Auto install charts
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from mplfinance.original_flavor import candlestick_ohlc
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False

load_dotenv()

# ============================================================
# LOGGING
# ============================================================
logger = logging.getLogger('CryptoPulseV10')
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)

for name, level in [('crypto_v10.log', logging.INFO), ('crypto_v10_errors.log', logging.ERROR)]:
    handler = RotatingFileHandler(name, maxBytes=10*1024*1024, backupCount=7, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(funcName)s | %(message)s'))
    logger.addHandler(handler)

for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'aiohttp', 'matplotlib']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# MARKDOWN ESCAPER - Fix Parse Error
# ============================================================
def escape_markdown(text: str) -> str:
    """Escape special Markdown characters to prevent parse errors"""
    if not text:
        return ""
    # Characters that need escaping in MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    # Don't escape if already escaped
    result = []
    for char in text:
        if char in escape_chars:
            result.append('\\' + char)
        else:
            result.append(char)
    return ''.join(result)

def safe_markdown(text: str) -> str:
    """Make text safe for Markdown by escaping only problematic parts"""
    if not text:
        return ""
    # Remove nested entities that cause issues
    text = re.sub(r'\*{2,}', '*', text)
    text = re.sub(r'_{2,}', '_', text)
    text = re.sub(r'`{2,}', '`', text)
    return text

async def safe_send_message(bot, chat_id, text: str, parse_mode: str = "Markdown", reply_markup=None):
    """Send message with auto-fallback to plain text on parse error"""
    try:
        return await bot.send_message(
            chat_id=chat_id,
            text=safe_markdown(text),
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        if "parse" in str(e).lower() or "entity" in str(e).lower():
            logger.warning(f"Markdown parse error, sending as plain text")
            try:
                # Remove all markdown and send as plain text
                plain_text = re.sub(r'[*_`~\[\]\(\)]', '', text)
                return await bot.send_message(
                    chat_id=chat_id,
                    text=plain_text[:4000],
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            except:
                return await bot.send_message(
                    chat_id=chat_id,
                    text=text[:1000] + "...",
                    reply_markup=reply_markup
                )
        raise

async def safe_edit_message(bot, chat_id, message_id, text: str, parse_mode: str = "Markdown", reply_markup=None):
    """Edit message with auto-fallback"""
    try:
        return await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=safe_markdown(text),
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        if "parse" in str(e).lower() or "entity" in str(e).lower():
            logger.warning(f"Edit parse error, retrying as plain text")
            try:
                plain_text = re.sub(r'[*_`~\[\]\(\)]', '', text)
                return await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=plain_text[:4000],
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            except:
                pass
        raise

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT",
        "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT",
        "XLM/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT"
    ])
    
    timeframes: Dict[str, str] = field(default_factory=lambda: {
        "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h",
        "6h": "6h", "12h": "12h", "1d": "1d",
        "3d": "3d", "1w": "1w"
    })
    
    primary_tfs: List[str] = field(default_factory=lambda: ["4h", "1d", "1w"])
    
    initial_balance: float = 100000.0
    risk_per_trade: float = 0.02
    max_positions: int = 5
    atr_sl: float = 2.0
    atr_tp: float = 4.0
    trailing_pct: float = 0.03
    max_consecutive_losses: int = 5
    demo_trading: bool = True
    real_trading: bool = False
    auto_send: bool = True
    
    signal_interval: int = 14400  # 4 hours
    education_interval: int = 3600  # 1 hour

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v10.lock"
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls._file):
                with open(cls._file) as f:
                    pid = int(f.read().strip() or 0)
                if pid and cls._alive(pid): return False
                os.remove(cls._file)
            with open(cls._file, 'w') as f: f.write(str(os.getpid()))
            return True
        except: return True
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls._file): os.remove(cls._file)
        except: pass
    @staticmethod
    def _alive(pid: int) -> bool:
        try: os.kill(pid, 0); return True
        except: return False

for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, lambda s, f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# DATE/TIME
# ============================================================
class DTM:
    @staticmethod
    def now() -> str: return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    @staticmethod
    def persian() -> str:
        n = datetime.now()
        days = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
        months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
        return f"{days[n.weekday()]} {n.day} {months[n.month-1]} {n.year} | {n.strftime('%H:%M:%S')}"
    @staticmethod
    def header() -> str:
        return f"📅 {DTM.persian()}\n🌍 UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"

dtm = DTM()

# ============================================================
# TOKEN MANAGER
# ============================================================
class TokenManager:
    MAX_TPM: int = 8000
    def __init__(self):
        self._usage: deque = deque()
        self.groq_tokens: int = 0
        self.gemini_tokens: int = 0
    @property
    def current(self) -> int:
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60: self._usage.popleft()
        return sum(t for _, t in self._usage)
    def can(self, tokens: int = 500) -> bool: return (self.current + tokens) <= self.MAX_TPM
    def wait(self, tokens: int = 500) -> float:
        if self.can(tokens): return 0
        if self._usage: return max(0, 60 - (time.time() - self._usage[0][0]) + 1)
        return 60
    def record(self, tokens: int, source: str = "groq"):
        self._usage.append((time.time(), tokens))
        if source == "groq": self.groq_tokens += tokens
        else: self.gemini_tokens += tokens
    def stats(self) -> Dict:
        return {'current': self.current, 'max': self.MAX_TPM, 'groq': self.groq_tokens, 'gemini': self.gemini_tokens}

token_mgr = TokenManager()

# ============================================================
# GEMINI AI
# ============================================================
class GeminiAI:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    def __init__(self):
        self.api_key = cfg.gemini_api_key
        self.enabled = bool(self.api_key and len(self.api_key) > 10)
        self.client = httpx.AsyncClient(timeout=60.0)
        if self.enabled: logger.info("🌟 Gemini AI Connected")
    async def generate(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.enabled: return None
        if not token_mgr.can(max_tokens):
            wait = token_mgr.wait(max_tokens)
            if wait > 30: return None
            await asyncio.sleep(wait)
        try:
            resp = await self.client.post(f"{self.URL}?key={self.api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}})
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text: token_mgr.record(max_tokens, "gemini"); return text
            return None
        except: return None

gemini_ai = GeminiAI()

# ============================================================
# GROQ AI
# ============================================================
class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    TOKENS = {'technical': 500, 'market': 400, 'education': 700, 'prediction': 350, 'strategy': 400, 'sentiment': 300, 'fundamental': 400, 'price_action': 400}
    
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self.client = httpx.AsyncClient(timeout=60.0)
        if self.enabled: logger.info("🧠 Groq AI Connected")
    
    async def _call(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.enabled: return None
        if not token_mgr.can(max_tokens):
            wait = token_mgr.wait(max_tokens)
            if wait > 30: return None
            await asyncio.sleep(wait)
        try:
            resp = await self.client.post(self.URL,
                headers={"Authorization": f"Bearer {cfg.groq_api_key}", "Content-Type": "application/json"},
                json={"model": self.MODEL, "messages": [{"role": "system", "content": "You are a crypto analyst. Respond in Persian (فارسی). Use emojis."}, {"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7})
            if resp.status_code == 200:
                data = resp.json()
                token_mgr.record(data.get('usage', {}).get('total_tokens', max_tokens), "groq")
                return data["choices"][0]["message"]["content"]
            return None
        except: return None
    
    async def technical(self, symbol: str, ind: Dict, price: float, change: float, patterns: List[str], mtf: Dict) -> Optional[str]:
        if not self.enabled: return None
        mtf_text = " | ".join([f"{t}:RSI={i.get('RSI_14',50):.0f}" for t,i in mtf.items()])
        return await self._call(f"Analyze {symbol} at ${price:,.2f}. RSI={ind.get('RSI_14',50):.0f} MACD={'Bull' if ind.get('MACD_HIST',0)>0 else 'Bear'} ADX={ind.get('ADX',20):.0f}. Support=${ind.get('SUPPORT',0):.0f} Resistance=${ind.get('RESISTANCE',0):.0f}. MTF:{mtf_text}. In Persian: Summary, Direction, Entry/Exit. Max 250 words.", self.TOKENS['technical'])
    
    async def market(self, coins: List[Dict]) -> Optional[str]:
        if not self.enabled: return None
        txt = "\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])
        return await self._call(f"Market overview in Persian:\n{txt}\nSentiment, trends. Max 200 words.", self.TOKENS['market'])
    
    async def education(self) -> Optional[str]:
        if not self.enabled: return None
        topics = ["تحلیل تکنیکال","مدیریت ریسک","روانشناسی","الگوهای کندلی","استراتژی","فیبوناچی","ایچیموکو"]
        return await self._call(f"Educational post in Persian about: {random.choice(topics)}. 400+ words, emojis, tips, golden nugget.", self.TOKENS['education'])
    
    async def prediction(self, symbol: str, ind: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Predict {symbol} at ${price:,.2f}. 4h,24h,7d targets in Persian. Max 150 words.", self.TOKENS['prediction'])
    
    async def strategy(self, symbol: str, ind: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Strategy for {symbol} at ${price:,.2f}. Entry,SL,TP in Persian. Max 200 words.", self.TOKENS['strategy'])
    
    async def sentiment(self, symbol: str, price: float, change: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Sentiment for {symbol} at ${price:,.2f} ({change:+.1f}%). Fear/Greed in Persian. Max 150 words.", self.TOKENS['sentiment'])
    
    async def fundamental(self, symbol: str, price: float, change: float) -> Optional[str]:
        if not self.enabled: return None
        coin = symbol.replace('/USDT','')
        return await self._call(f"Fundamental analysis for {coin} at ${price:,.2f}. Project, adoption in Persian. Max 200 words.", self.TOKENS['fundamental'])
    
    async def price_action(self, symbol: str, ind: Dict, price: float, patterns: List[str]) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Price action for {symbol} at ${price:,.2f}. Patterns: {', '.join(patterns) if patterns else 'None'}. Structure, S/R in Persian. Max 200 words.", self.TOKENS['price_action'])

groq_ai = GroqAI()

# ============================================================
# EXCHANGE
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex: Optional[ccxt.Exchange] = None
        self.connected: bool = False
    def connect(self) -> bool:
        try:
            params = {'enableRateLimit': True, 'timeout': 30000}
            if cfg.api_key: params.update({'apiKey': cfg.api_key, 'secret': cfg.api_secret, 'password': cfg.api_passphrase})
            self._ex = ccxt.coinex(params); self._ex.load_markets(); self.connected = True; return True
        except:
            try: self._ex = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000}); self._ex.load_markets(); self.connected = True; return True
            except: return False
    def ticker(self, s: str) -> Optional[Dict]:
        try: return self._ex.fetch_ticker(s) if self.connected else None
        except: return None
    def ohlcv(self, s: str, tf: str, limit: int = 200) -> Optional[pd.DataFrame]:
        try:
            if not self.connected: return None
            d = self._ex.fetch_ohlcv(s, tf, limit=limit)
            return pd.DataFrame(d, columns=['timestamp','open','high','low','close','volume']) if d and len(d)>30 else None
        except: return None

exchange_mgr = ExchangeManager()

# ============================================================
# 25+ INDICATORS
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df: pd.DataFrame) -> Dict[str, Any]:
        close = df['close'].astype(float); high = df['high'].astype(float)
        low = df['low'].astype(float); volume = df['volume'].astype(float)
        ind = {}
        
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
        ind['EMA_LONG'] = float(close.ewm(span=200, adjust=False).mean().iloc[-1])
        ind['EMA_MID'] = float(close.ewm(span=100, adjust=False).mean().iloc[-1])
        ind['EMA_SHORT'] = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
        
        from ta.momentum import RSIIndicator
        for p in [7, 14, 21]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close, window=p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        
        from ta.trend import MACD, ADXIndicator, CCIIndicator
        try: macd = MACD(close, 12, 26, 9); ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        
        from ta.momentum import StochasticOscillator
        try: stoch = StochasticOscillator(high, low, close, 14, 3); ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
        except: ind['STOCH_K'] = 50.0
        
        from ta.volatility import BollingerBands, AverageTrueRange
        try:
            bb = BollingerBands(close, 20, 2)
            ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1]); ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
            ind['BB_WIDTH'] = float(bb.bollinger_wband().iloc[-1]); ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        
        try: ind['ATR_14'] = float(AverageTrueRange(high, low, close, 14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1]*0.01
        ind['ATR_PCT'] = float(ind['ATR_14']/close.iloc[-1]*100)
        
        try: ind['ADX'] = float(ADXIndicator(high, low, close, 14).adx().iloc[-1])
        except: ind['ADX'] = 20.0
        try: ind['CCI'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high, low, close, volume, 14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        
        vs = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else volume.iloc[-1]
        ind['VOL_RATIO'] = float(volume.iloc[-1]/vs if vs>0 else 1)
        ind['SUPPORT'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['RESISTANCE'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        
        h, l, c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        ind['PIVOT'] = float((h+l+c)/3)
        
        h50 = high.rolling(50).max().iloc[-1] if len(high)>=50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low)>=50 else low.min()
        diff = h50 - l50
        for lvl in [0.382, 0.5, 0.618]:
            ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff*lvl)
        
        ind.update(UltraIndicators._candles(df))
        ind['DIVERGENCE'] = UltraIndicators._divergence(close)
        ind['TREND_STR'] = float((close.iloc[-1]-close.iloc[-50])/close.iloc[-50]*100) if len(close)>=50 else 0
        
        return ind
    
    @staticmethod
    def _candles(df: pd.DataFrame) -> Dict[str, bool]:
        pats = {p: False for p in ['DOJI','HAMMER','SHOOTING_STAR','ENGULFING_BULL','ENGULFING_BEAR','MARUBOZU_BULL','MARUBOZU_BEAR','THREE_WHITE','THREE_BLACK']}
        if len(df) < 2: return pats
        o, h, l, c = df['open'].iloc[-1], df['high'].iloc[-1], df['low'].iloc[-1], df['close'].iloc[-1]
        po, pc = df['open'].iloc[-2], df['close'].iloc[-2]
        body, tr = abs(c-o), h-l
        if tr == 0: return pats
        pats['DOJI'] = body <= tr*0.08
        pats['HAMMER'] = (min(c,o)-l) > body*2 and c > o
        pats['SHOOTING_STAR'] = (h-max(c,o)) > body*2 and c < o
        pats['ENGULFING_BULL'] = c > o and pc < po
        pats['ENGULFING_BEAR'] = c < o and pc > po
        pats['MARUBOZU_BULL'] = c > o and (h-c) < body*0.1
        pats['MARUBOZU_BEAR'] = c < o and (o-l) < body*0.1
        if len(df) >= 3:
            o3, c3 = df['open'].iloc[-3], df['close'].iloc[-3]
            pats['THREE_WHITE'] = c>o and pc>po and c3>o3
            pats['THREE_BLACK'] = c<o and pc<po and c3<o3
        return pats
    
    @staticmethod
    def _divergence(price: pd.Series) -> str:
        if len(price) < 20: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price, 14).rsi()
        rp, rr = price.iloc[-20:], rsi.iloc[-20:]
        if rp.iloc[-1] < rp.min() and rr.iloc[-1] > rr.min(): return "BULLISH"
        if rp.iloc[-1] > rp.max() and rr.iloc[-1] < rr.max(): return "BEARISH"
        return "NONE"

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind: Dict, price: float, mtf: Dict = None) -> Tuple[str, int, int]:
        score = 0
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']: score += 150
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']: score -= 150
        
        rsi = ind['RSI_14']
        if rsi < 30: score += 120
        elif rsi > 70: score -= 120
        
        if ind.get('MACD_HIST',0) > 0: score += 70
        else: score -= 70
        if ind.get('STOCH_K',50) < 20: score += 70
        elif ind.get('STOCH_K',50) > 80: score -= 70
        if ind.get('BB_PCT',0.5) < 0.1: score += 100
        elif ind.get('BB_PCT',0.5) > 0.9: score -= 100
        if ind.get('VOL_RATIO',1) > 2: score += 50 if score>0 else -50
        if ind.get('MFI',50) < 20: score += 60
        elif ind.get('MFI',50) > 80: score -= 60
        
        if ind.get('ENGULFING_BULL'): score += 80
        if ind.get('HAMMER'): score += 50
        if ind.get('ENGULFING_BEAR'): score -= 80
        if ind.get('SHOOTING_STAR'): score -= 50
        if ind.get('THREE_WHITE'): score += 60
        if ind.get('THREE_BLACK'): score -= 60
        if ind.get('DIVERGENCE') == 'BULLISH': score += 70
        elif ind.get('DIVERGENCE') == 'BEARISH': score -= 70
        if ind.get('EMA_LONG',0) > ind.get('EMA_MID',0): score += 50
        
        if mtf:
            for tf, ti in mtf.items():
                w = {"4h":2,"1d":3,"1w":5}.get(tf,1)
                if ti.get('RSI_14',50) > 55: score += int(25*w)
                elif ti.get('RSI_14',50) < 45: score -= int(25*w)
        
        score = max(-1000, min(1000, score))
        if score >= 700: return "خرید فوق العاده", 98, score
        elif score >= 500: return "خرید قوی", 92, score
        elif score >= 300: return "خرید", 82, score
        elif score >= 150: return "خرید ضعیف", 68, score
        elif score <= -700: return "فروش فوق العاده", 98, score
        elif score <= -500: return "فروش قوی", 92, score
        elif score <= -300: return "فروش", 82, score
        elif score <= -150: return "فروش ضعیف", 68, score
        else: return "خنثی", 50, score

sg = SignalGen()

# ============================================================
# TRADER
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance; self.positions: Dict = {}; self.history: List = []; self.closses = 0
        self.load()
    def load(self):
        try:
            with open('trader_v10.json','r') as f: d = json.load(f); self.balance = d.get('balance', cfg.initial_balance); self.history = d.get('history', [])
        except: pass
    def save(self):
        try:
            with open('trader_v10.json','w') as f: json.dump({'balance': self.balance, 'history': self.history[-500:]}, f)
        except: pass
    def open(self, symbol: str, entry: float, sl: float, tp: float) -> Optional[Dict]:
        if len(self.positions) >= cfg.max_positions or self.closses >= cfg.max_consecutive_losses: return None
        risk = self.balance * cfg.risk_per_trade
        if self.closses > 0: risk *= (0.5**self.closses)
        sz = min(risk/abs(entry-sl), self.balance*0.25/entry) if abs(entry-sl)>0 else 0
        if sz <= 0 or sz*entry > self.balance: return None
        self.balance -= sz*entry
        self.positions[symbol] = {'symbol':symbol,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry}
        self.save(); return self.positions[symbol]
    def update(self, symbol: str, price: float) -> Optional[Dict]:
        if symbol not in self.positions: return None
        p = self.positions[symbol]; p['high'] = max(p['high'], price)
        if (price-p['entry'])/p['entry'] > cfg.trailing_pct: p['sl'] = p['high']*(1-cfg.trailing_pct)
        if price >= p['tp']: return self.close(symbol, price, "TP")
        if price <= p['sl']: return self.close(symbol, price, "SL")
        return None
    def close(self, symbol: str, price: float, reason: str) -> Dict:
        p = self.positions.pop(symbol); pnl = (price-p['entry'])*p['size']
        self.balance += p['size']*price; self.closses = 0 if pnl>0 else self.closses+1
        t = {'symbol':symbol,'entry':p['entry'],'exit':price,'pnl':pnl,'reason':reason,'time':datetime.now().isoformat()}
        self.history.append(t); self.save(); return t
    def stats(self) -> Dict:
        total = max(1, len(self.history)); wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100}

trader = Trader()

# ============================================================
# FORMATTER - SIMPLIFIED
# ============================================================
class Fmt:
    @staticmethod
    def signal(a: Dict, groq_text: str = None, gemini_text: str = None, tf_4h: Dict = None, tf_1d: Dict = None, tf_1w: Dict = None) -> str:
        s = a['symbol'].replace('/USDT',''); i = a['indicators']
        pats = [k for k,v in i.items() if isinstance(v,bool) and v]
        
        msg = f"""
══════════════════════════════════════
     SIGNAL {s}
══════════════════════════════════════

{dtm.header()}

Price: ${a['price']:,.4f}
Change: {a['change']:+.2f}%
Signal: {a['signal']}
Confidence: {a['confidence']}% | Score: {a['score']}/1000

--- EMAs ---
EMA_7: ${i.get('EMA_7',0):,.2f}
EMA_20: ${i.get('EMA_20',0):,.2f}
EMA_50: ${i.get('EMA_50',0):,.2f}
EMA_100: ${i.get('EMA_100',0):,.2f}
EMA_200: ${i.get('EMA_200',0):,.2f}

--- Indicators ---
RSI(14): {i['RSI_14']:.1f} | RSI(7): {i.get('RSI_7',50):.1f}
MACD: {'Bullish' if i.get('MACD_HIST',0)>0 else 'Bearish'}
ADX: {i['ADX']:.1f} | CCI: {i['CCI']:.1f} | MFI: {i['MFI']:.1f}
Stochastic K: {i.get('STOCH_K',50):.1f}
BB Width: {i.get('BB_WIDTH',0):.4f}
ATR(14): {i['ATR_14']:.4f}
Volume Ratio: {i.get('VOL_RATIO',1):.1f}x

--- Candles ---
Patterns: {', '.join(pats) if pats else 'None'}
Divergence: {i.get('DIVERGENCE','NONE')}

--- Levels ---
Resistance: ${i['RESISTANCE']:,.4f}
Support: ${i['SUPPORT']:,.4f}
Fib 0.618: ${i.get('FIB_618',0):,.4f}

SL: ${a['price']-i['ATR_14']*cfg.atr_sl:,.4f}
TP: ${a['price']+i['ATR_14']*cfg.atr_tp:,.4f}"""

        if tf_4h:
            msg += f"""

--- 4H Timeframe ---
RSI: {tf_4h.get('RSI_14',50):.0f} | MACD: {'Bullish' if tf_4h.get('MACD_HIST',0)>0 else 'Bearish'}
EMA_50: ${tf_4h.get('EMA_50',0):,.2f} | ADX: {tf_4h.get('ADX',20):.0f}"""

        if tf_1d:
            msg += f"""

--- 1D Timeframe ---
RSI: {tf_1d.get('RSI_14',50):.0f} | MACD: {'Bullish' if tf_1d.get('MACD_HIST',0)>0 else 'Bearish'}
EMA_50: ${tf_1d.get('EMA_50',0):,.2f} | ADX: {tf_1d.get('ADX',20):.0f}"""

        if tf_1w:
            msg += f"""

--- 1W Timeframe ---
RSI: {tf_1w.get('RSI_14',50):.0f} | MACD: {'Bullish' if tf_1w.get('MACD_HIST',0)>0 else 'Bearish'}
EMA_50: ${tf_1w.get('EMA_50',0):,.2f} | ADX: {tf_1w.get('ADX',20):.0f}"""

        if groq_text:
            msg += f"\n\n--- Groq AI ---\n{groq_text[:400]}"
        if gemini_text:
            msg += f"\n\n--- Gemini AI ---\n{gemini_text[:400]}"
        
        msg += f"""

--- Final ---
Signal: {a['signal']} | Confidence: {a['confidence']}%

══════════════════════════════════════
CryptoPulse606 | {dtm.now()}"""
        return msg
    
    @staticmethod
    def edu(content: str = None) -> str:
        if content:
            return f"""
══════════════════════════════════════
     EDUCATIONAL CONTENT
══════════════════════════════════════

{dtm.header()}

{content}

══════════════════════════════════════
CryptoPulse606 | {dtm.now()}"""
        return f"""
══════════════════════════════════════
     DAILY LESSON
══════════════════════════════════════

{dtm.header()}

Market Analysis Tips:
- Follow the trend
- Risk/Reward >= 1:2
- Max 2% risk per trade
- Always use stop loss

══════════════════════════════════════
CryptoPulse606 | {dtm.now()}"""

fmt = Fmt()

# ============================================================
# MENUS
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Prices", callback_data="p"),
             InlineKeyboardButton("Signal BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("Scan", callback_data="scan")],
            [InlineKeyboardButton("4H Analysis", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("1D Analysis", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("1W Analysis", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("Groq AI", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("Gemini AI", callback_data="gem_BTC/USDT"),
             InlineKeyboardButton("Chart", callback_data="chart_BTC/USDT")],
            [InlineKeyboardButton("Market", callback_data="market"),
             InlineKeyboardButton("Strategy", callback_data="strat"),
             InlineKeyboardButton("Sentiment", callback_data="sent")],
            [InlineKeyboardButton("Fundamental", callback_data="fund"),
             InlineKeyboardButton("Price Action", callback_data="pa"),
             InlineKeyboardButton("Prediction", callback_data="pred")],
            [InlineKeyboardButton("Portfolio", callback_data="port"),
             InlineKeyboardButton("Performance", callback_data="perf"),
             InlineKeyboardButton("History", callback_data="hist")],
            [InlineKeyboardButton("Auto Trade", callback_data="auto"),
             InlineKeyboardButton("Settings", callback_data="set"),
             InlineKeyboardButton("Status", callback_data="status")],
            [InlineKeyboardButton("Education", callback_data="edu"),
             InlineKeyboardButton("Patterns", callback_data="patterns"),
             InlineKeyboardButton("Fear/Greed", callback_data="fear")],
            [InlineKeyboardButton("Whales", callback_data="whale"),
             InlineKeyboardButton("Altcoins", callback_data="alt"),
             InlineKeyboardButton("7D Forecast", callback_data="pred7")],
            [InlineKeyboardButton("Compare", callback_data="compare"),
             InlineKeyboardButton("Live Chart", callback_data="live"),
             InlineKeyboardButton("Alerts", callback_data="alerts")],
            [InlineKeyboardButton("EMERGENCY STOP", callback_data="stop"),
             InlineKeyboardButton("Refresh", callback_data="ref"),
             InlineKeyboardButton("Help", callback_data="help")],
        ])
    
    @staticmethod
    def tech() -> InlineKeyboardMarkup:
        kb, row = [], []
        for s in cfg.symbols[:20]:
            row.append(InlineKeyboardButton(s.replace('/USDT',''), callback_data=f"s_{s}"))
            if len(row) == 4: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([InlineKeyboardButton("Back", callback_data="back")])
        return InlineKeyboardMarkup(kb)

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Crypto Pulse v10.1\n\n"
        "Groq AI + Gemini AI\n"
        "25+ Indicators | 4H/1D/1W\n"
        "Signal every 4 hours\n"
        "Education every 1 hour\n\n"
        "Select from menu:",
        reply_markup=Menu.main()
    )

async def signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"Analyzing {symbol.replace('/USDT','')}...")
    
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("Error", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        return
    
    ind = ui.calc(df)
    mtf = {}
    for tf_name in cfg.primary_tfs:
        dft = exchange_mgr.ohlcv(symbol, tf_name, 100)
        if dft is not None: mtf[tf_name] = ui.calc(dft)
    
    sig, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    tf_4h = mtf.get('4h'); tf_1d = mtf.get('1d'); tf_1w = mtf.get('1w')
    
    groq_text = await groq_ai.technical(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    gemini_text = None
    if gemini_ai.enabled:
        gemini_text = await gemini_ai.generate(f"Analyze {symbol} at ${t['last']:,.2f}. 4h/1d/1w outlook in Persian. Max 250 words.", 400)
    
    analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
                'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
    
    msg = fmt.signal(analysis, groq_text, gemini_text, tf_4h, tf_1d, tf_1w)
    
    await safe_edit_message(ctx.bot, q.message.chat_id, q.message.message_id, msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Refresh", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("Chart", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("Back", callback_data="back")
        ]]))

async def tf_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT", tf: str = "4h"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"Analyzing {tf} timeframe for {symbol.replace('/USDT','')}...")
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, tf, 200)
    if not t or df is None:
        await q.edit_message_text("Error", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        return
    
    ind = ui.calc(df)
    sig, conf, score = sg.generate(ind, t['last'])
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    msg = f"""
═══ {tf} Analysis - {symbol.replace('/USDT','')} ═══

{dtm.header()}

Price: ${t['last']:,.4f}
Signal: {sig} | Confidence: {conf}%

EMA 7: ${ind.get('EMA_7',0):,.2f}
EMA 20: ${ind.get('EMA_20',0):,.2f}
EMA 50: ${ind.get('EMA_50',0):,.2f}
EMA 200: ${ind.get('EMA_200',0):,.2f}

RSI(14): {ind['RSI_14']:.0f}
MACD: {'Bullish' if ind.get('MACD_HIST',0)>0 else 'Bearish'}
ADX: {ind['ADX']:.0f}
CCI: {ind['CCI']:.0f}
Patterns: {', '.join(pats) if pats else 'None'}
Divergence: {ind.get('DIVERGENCE','NONE')}

Support: ${ind['SUPPORT']:,.2f}
Resistance: ${ind['RESISTANCE']:,.2f}
Fib 0.618: ${ind.get('FIB_618',0):,.2f}

══════════════════════════════════════
CryptoPulse606 | {dtm.now()}"""
    
    await safe_edit_message(ctx.bot, q.message.chat_id, q.message.message_id, msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Refresh", callback_data=f"tf{tf}_{symbol}"),
            InlineKeyboardButton("Chart", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("Back", callback_data="back")
        ]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    try:
        if d == "back": await q.edit_message_text("Main Menu", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"{dtm.header()}\nPRICES:\n\n"
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'G' if t.get('percentage',0)>0 else 'R'} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="p"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d.startswith("tf4_"): await tf_handler(update, ctx, d[4:], "4h")
        elif d.startswith("tf1d_"): await tf_handler(update, ctx, d[5:], "1d")
        elif d.startswith("tf1w_"): await tf_handler(update, ctx, d[5:], "1w")
        elif d.startswith("ai_"): await signal_handler(update, ctx, d[3:] if len(d)>3 else "BTC/USDT")
        elif d.startswith("gem_"):
            if not gemini_ai.enabled:
                await q.edit_message_text("Gemini API Key not set", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
                return
            await signal_handler(update, ctx, d[4:] if len(d)>4 else "BTC/USDT")
        elif d.startswith("chart_"):
            await q.edit_message_text("Chart feature - use /chart command", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "market":
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
            m = await groq_ai.market(top)
            if m: await q.edit_message_text(f"{dtm.header()}\nMARKET:\n\n{m}\n\nCryptoPulse606", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="market"), InlineKeyboardButton("Back", callback_data="back")]]))
            else: await q.edit_message_text("Error", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "strat":
            t = exchange_mgr.ticker("BTC/USDT"); df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
            if t and df is not None:
                ind = ui.calc(df); s = await groq_ai.strategy("BTC/USDT", ind, t['last'])
                if s: await q.edit_message_text(f"{dtm.header()}\nBTC STRATEGY:\n\n{s}\n\nCryptoPulse606", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="strat"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "sent":
            t = exchange_mgr.ticker("BTC/USDT")
            if t:
                s = await groq_ai.sentiment("BTC/USDT", t['last'], t.get('percentage',0))
                if s: await q.edit_message_text(f"{dtm.header()}\nBTC SENTIMENT:\n\n{s}\n\nCryptoPulse606", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="sent"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "fund":
            t = exchange_mgr.ticker("BTC/USDT")
            if t:
                s = await groq_ai.fundamental("BTC/USDT", t['last'], t.get('percentage',0))
                if s: await q.edit_message_text(f"{dtm.header()}\nBTC FUNDAMENTAL:\n\n{s}\n\nCryptoPulse606", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="fund"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "pa":
            t = exchange_mgr.ticker("BTC/USDT"); df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
            if t and df is not None:
                ind = ui.calc(df); pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                s = await groq_ai.price_action("BTC/USDT", ind, t['last'], pats)
                if s: await q.edit_message_text(f"{dtm.header()}\nBTC PRICE ACTION:\n\n{s}\n\nCryptoPulse606", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="pa"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "pred":
            t = exchange_mgr.ticker("BTC/USDT"); df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
            if t and df is not None:
                ind = ui.calc(df); s = await groq_ai.prediction("BTC/USDT", ind, t['last'])
                if s: await q.edit_message_text(f"{dtm.header()}\nBTC PREDICTION:\n\n{s}\n\nCryptoPulse606", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="pred"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "scan":
            if not exchange_mgr.connected: exchange_mgr.connect()
            res = []
            for sym in cfg.symbols:
                t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 100)
                if t and df is not None:
                    ind = ui.calc(df); sig, conf, score = sg.generate(ind, t['last'])
                    res.append({'symbol': sym, 'price': t['last'], 'signal': sig, 'confidence': conf, 'score': score})
            res.sort(key=lambda x: abs(x['score']), reverse=True)
            txt = f"{dtm.header()}\nSCAN:\n\n"
            for i, r in enumerate(res[:12], 1): txt += f"{i}. {'G' if 'خرید' in r['signal'] else 'R' if 'فروش' in r['signal'] else 'N'} {r['symbol'].replace('/USDT','')}: ${r['price']:,.4f} | {r['signal']} | {r['confidence']}%\n"
            await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="scan"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "tech": await q.edit_message_text("Select coin:", reply_markup=Menu.tech())
        elif d == "port":
            s = trader.stats()
            await q.edit_message_text(f"{dtm.header()}\nPORTFOLIO:\nBalance: ${s['balance']:,.2f}\nPnL: ${s['pnl']:+,.2f}\nPositions: {len(trader.positions)}\nTrades: {s['total']} | Wins: {s['wins']} ({s['rate']:.0f}%)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="port"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d in ["perf", "hist"]:
            s = trader.stats()
            await q.edit_message_text(f"{dtm.header()}\nPERFORMANCE:\nBalance: ${s['balance']:,.2f}\nPnL: ${s['pnl']:+,.2f}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "auto":
            await q.edit_message_text(f"Auto Trade:\nDemo: {'ON' if cfg.demo_trading else 'OFF'}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"Demo: {'ON' if cfg.demo_trading else 'OFF'}", callback_data="td"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "td": cfg.demo_trading = not cfg.demo_trading
        elif d in ["set", "status"]:
            await q.edit_message_text(f"{dtm.header()}\nSETTINGS:\nExchange: {'OK' if exchange_mgr.connected else 'FAIL'}\nGroq: {'OK' if groq_ai.enabled else 'FAIL'}\nGemini: {'OK' if gemini_ai.enabled else 'FAIL'}\nSignal: Every 4H\nEducation: Every 1H", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "edu":
            content = await groq_ai.education()
            await q.edit_message_text(fmt.edu(content), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Refresh", callback_data="edu"), InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "EMERGENCY")
            await q.edit_message_text("All positions closed", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text("Main Menu", reply_markup=Menu.main())
        elif d == "help": await q.edit_message_text("Use /start", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        elif d in ["patterns", "fear", "whale", "alt", "pred7", "compare", "live", "alerts"]:
            await q.edit_message_text("Coming soon...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))
        else: await q.answer("OK")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("Error")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(10)
    logger.info("4H Signal Loop Started")
    
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            
            await safe_send_message(app.bot, cfg.channel_id, f"4-Hour Analysis Cycle Starting...\n{dtm.header()}")
            
            for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 200)
                    if t and df is not None:
                        ind = ui.calc(df)
                        mtf = {}
                        for tf_name in cfg.primary_tfs:
                            dft = exchange_mgr.ohlcv(sym, tf_name, 100)
                            if dft is not None: mtf[tf_name] = ui.calc(dft)
                        
                        sig, conf, score = sg.generate(ind, t['last'], mtf)
                        pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                        
                        tf_4h = mtf.get('4h'); tf_1d = mtf.get('1d'); tf_1w = mtf.get('1w')
                        
                        groq_text = await groq_ai.technical(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
                        gemini_text = None
                        if gemini_ai.enabled and sym in ["BTC/USDT", "ETH/USDT"]:
                            gemini_text = await gemini_ai.generate(f"Analyze {sym} at ${t['last']:,.2f} in Persian. Max 200 words.", 350)
                        
                        analysis = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0),
                                   'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                        
                        msg = fmt.signal(analysis, groq_text, gemini_text, tf_4h, tf_1d, tf_1w)
                        await safe_send_message(app.bot, cfg.channel_id, msg)
                        logger.info(f"Signal: {sym}")
                        await asyncio.sleep(120)
                except Exception as e: logger.error(f"Signal {sym}: {e}")
            
            # Market overview
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
            market = await groq_ai.market(top)
            if market:
                await safe_send_message(app.bot, cfg.channel_id, f"{dtm.header()}\nMARKET OVERVIEW:\n\n{market}\n\nCryptoPulse606")
            
            # Position check
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    if t:
                        result = trader.update(sym, t['last'])
                        if result:
                            emoji = "PROFIT" if result['pnl']>0 else "LOSS"
                            await safe_send_message(app.bot, cfg.channel_id, f"{emoji}: {sym} closed | ${result['pnl']:+,.2f}")
                except: pass
            
            await safe_send_message(app.bot, cfg.channel_id, f"4-Hour Cycle Complete.\nNext signal in 4 hours.\n\nCryptoPulse606")
            
        except Exception as e: logger.error(f"Loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education(app: Application):
    await asyncio.sleep(30)
    logger.info("1H Education Loop Started")
    
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.education()
                if content:
                    await safe_send_message(app.bot, cfg.channel_id, fmt.edu(content))
                    logger.info("Education sent")
        except Exception as e: logger.error(f"Edu: {e}")
        await asyncio.sleep(cfg.education_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    
    exchange_mgr.connect()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_education(app))
    
    logger.info("="*50)
    logger.info("CRYPTO PULSE v10.1 - FIXED")
    logger.info(f"Groq: {'OK' if groq_ai.enabled else 'FAIL'} | Gemini: {'OK' if gemini_ai.enabled else 'FAIL'}")
    logger.info(f"Signal: Every 4H | Education: Every 1H")
    logger.info("="*50)
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Exception as e: logger.critical(f"Fatal: {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except: ProcessLock.release()
