#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║   CRYPTO PULSE ULTIMATE DUAL AI TRADING BOT v9.0                    ║
║   Groq AI + Gemini AI | Charts | 25+ Indicators | 7 EMA             ║
║   EXACTLY 8000 TPM - DUAL AI COORDINATION                           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, logging, asyncio, time, json, random, signal, math, base64, io
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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
import warnings
warnings.filterwarnings('ignore')

# Chart libraries
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
logger = logging.getLogger('CryptoPulseV9')
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)

for name, level in [('crypto_v9.log', logging.INFO), ('crypto_v9_debug.log', logging.DEBUG), ('crypto_v9_errors.log', logging.ERROR)]:
    handler = RotatingFileHandler(name, maxBytes=10*1024*1024, backupCount=7, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(funcName)s | %(message)s'))
    logger.addHandler(handler)

for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'aiohttp', 'matplotlib']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    
    # Dual AI Keys
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Exchange
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT",
        "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT",
        "XLM/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT",
        "ICP/USDT", "SAND/USDT", "AXS/USDT", "FTM/USDT", "MANA/USDT",
        "GALA/USDT", "ENJ/USDT", "CHZ/USDT", "NEAR/USDT", "APT/USDT"
    ])
    
    timeframes: Dict[str, str] = field(default_factory=lambda: {
        "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h",
        "6h": "6h", "12h": "12h", "1d": "1d",
        "3d": "3d", "1w": "1w"
    })
    
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
    signal_interval: int = 600
    education_interval: int = 600

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v9.lock"
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls._file):
                with open(cls._file) as f:
                    pid = int(f.read().strip() or 0)
                if pid and cls._alive(pid):
                    logger.critical(f"❌ Already running (PID: {pid})")
                    return False
                os.remove(cls._file)
            with open(cls._file, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except:
            return True
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls._file): os.remove(cls._file)
        except: pass
    @staticmethod
    def _alive(pid: int) -> bool:
        try: os.kill(pid, 0); return True
        except (OSError, ProcessLookupError): return False

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
        return f"📅 {DTM.persian()}\n🌍 UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"

dtm = DTM()

# ============================================================
# DUAL AI TOKEN MANAGER - 8000 TPM
# ============================================================
class DualAITokenManager:
    """Token manager for dual AI - EXACTLY 8000 TPM"""
    MAX_TPM: int = 8000
    
    def __init__(self):
        self._usage: deque = deque()
        self._total_tokens: int = 0
        self._total_requests: int = 0
        self._rate_limits: int = 0
        # Token allocation between Groq and Gemini
        self.groq_tokens: int = 0
        self.gemini_tokens: int = 0
    
    @property
    def current_usage(self) -> int:
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60:
            self._usage.popleft()
        return sum(t for _, t in self._usage)
    
    @property
    def remaining(self) -> int:
        return max(0, self.MAX_TPM - self.current_usage)
    
    def can_request(self, tokens: int = 500) -> bool:
        return (self.current_usage + tokens) <= self.MAX_TPM
    
    def wait_time(self, tokens: int = 500) -> float:
        if self.can_request(tokens): return 0
        if self._usage:
            return max(0, 60 - (time.time() - self._usage[0][0]) + 1)
        return 60
    
    def record(self, tokens: int, source: str = "groq"):
        self._usage.append((time.time(), tokens))
        self._total_tokens += tokens
        self._total_requests += 1
        if source == "groq": self.groq_tokens += tokens
        else: self.gemini_tokens += tokens
    
    def record_rate_limit(self):
        self._rate_limits += 1
    
    def get_stats(self) -> Dict:
        return {
            'current': self.current_usage, 'max': self.MAX_TPM,
            'remaining': self.remaining,
            'groq': self.groq_tokens, 'gemini': self.gemini_tokens,
            'requests': self._total_requests, 'limits': self._rate_limits
        }

token_mgr = DualAITokenManager()

# ============================================================
# GEMINI AI CLIENT
# ============================================================
class GeminiAIClient:
    """Google Gemini AI Client"""
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def __init__(self):
        self.enabled = bool(cfg.gemini_api_key)
        self.client = httpx.AsyncClient(timeout=60.0)
        if self.enabled:
            logger.info("🌟 Gemini AI Connected (Gemini 2.0 Flash)")
    
    async def generate(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.enabled: return None
        
        if not token_mgr.can_request(max_tokens):
            wait = token_mgr.wait_time(max_tokens)
            if wait > 30: return None
            await asyncio.sleep(wait)
        
        try:
            response = await self.client.post(
                f"{self.API_URL}?key={cfg.gemini_api_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}
                }
            )
            if response.status_code == 200:
                data = response.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                token_mgr.record(max_tokens, "gemini")
                return text
            logger.error(f"Gemini Error: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Gemini Exception: {e}")
            return None
    
    async def analyze_chart(self, image_base64: str, symbol: str, price: float) -> Optional[str]:
        """Analyze chart image"""
        if not self.enabled: return None
        
        if not token_mgr.can_request(600):
            return None
        
        prompt = f"""Analyze this cryptocurrency chart for {symbol} at ${price:,.2f}.
Identify: trend direction, support/resistance levels, candlestick patterns, indicators visible.
Provide in Persian (فارسی) with emojis. Max 300 words."""
        
        try:
            response = await self.client.post(
                f"{self.API_URL}?key={cfg.gemini_api_key}",
                json={
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": "image/png", "data": image_base64}}
                        ]
                    }],
                    "generationConfig": {"maxOutputTokens": 600, "temperature": 0.7}
                }
            )
            if response.status_code == 200:
                data = response.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                token_mgr.record(600, "gemini")
                return text
            return None
        except Exception as e:
            logger.error(f"Gemini Chart Error: {e}")
            return None

gemini_ai = GeminiAIClient()

# ============================================================
# GROQ AI CLIENT
# ============================================================
class GroqAIClient:
    """Groq AI Client"""
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    
    TOKENS = {
        'technical': 500, 'market': 400, 'education': 700,
        'prediction': 350, 'strategy': 400, 'sentiment': 300,
        'fundamental': 400, 'price_action': 400
    }
    
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self.client = httpx.AsyncClient(timeout=60.0)
        if self.enabled:
            logger.info("🧠 Groq AI Connected (Llama 3.3 70B)")
    
    async def _call(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.enabled: return None
        
        if not token_mgr.can_request(max_tokens):
            wait = token_mgr.wait_time(max_tokens)
            if wait > 30: return None
            await asyncio.sleep(wait)
        
        try:
            response = await self.client.post(
                self.API_URL,
                headers={"Authorization": f"Bearer {cfg.groq_api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.MODEL,
                    "messages": [
                        {"role": "system", "content": "You are an elite crypto analyst. Respond in Persian (فارسی). Use emojis."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens, "temperature": 0.7
                }
            )
            if response.status_code == 200:
                data = response.json()
                token_mgr.record(data.get('usage', {}).get('total_tokens', max_tokens), "groq")
                return data["choices"][0]["message"]["content"]
            if response.status_code == 429:
                token_mgr.record_rate_limit()
            logger.error(f"Groq Error: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Groq Exception: {e}")
            return None
    
    async def technical(self, symbol: str, ind: Dict, price: float, change: float, patterns: List[str], mtf: Dict) -> Optional[str]:
        if not self.enabled: return None
        mtf_text = " | ".join([f"{t}:RSI={i.get('RSI_14',50):.0f}" for t,i in mtf.items()])
        prompt = f"""Analyze {symbol} at ${price:,.4f} ({change:+.2f}%):
RSI={ind.get('RSI_14',50):.0f} MACD={'Bull' if ind.get('MACD_HIST',0)>0 else 'Bear'} ADX={ind.get('ADX',20):.0f}
CCI={ind.get('CCI',0):.0f} MFI={ind.get('MFI',50):.0f} BB%={ind.get('BB_PCT',0.5):.2f}
Vol={ind.get('VOL_RATIO',1):.1f}x ATR%={ind.get('ATR_PCT',0):.1f}%
Support=${ind.get('SUPPORT',0):.0f} Resistance=${ind.get('RESISTANCE',0):.0f}
Patterns: {', '.join(patterns) if patterns else 'None'} Div: {ind.get('DIVERGENCE','NONE')}
MTF: {mtf_text}
In Persian: Summary, Direction, Entry/Exit, Risk, Confidence. Max 300 words."""
        return await self._call(prompt, self.TOKENS['technical'])
    
    async def market(self, coins: List[Dict]) -> Optional[str]:
        if not self.enabled: return None
        txt = "\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])
        return await self._call(f"Market overview in Persian:\n{txt}\nSentiment, trends, opportunities. Max 250 words.", self.TOKENS['market'])
    
    async def education(self) -> Optional[str]:
        if not self.enabled: return None
        topics = ["تحلیل تکنیکال","مدیریت ریسک","روانشناسی","الگوهای کندلی","استراتژی","فیبوناچی","ایچیموکو"]
        return await self._call(f"Educational post in Persian about: {random.choice(topics)}. 400+ words, emojis, tips.", self.TOKENS['education'])
    
    async def prediction(self, symbol: str, ind: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Predict {symbol} at ${price:,.2f}. RSI={ind.get('RSI_14',50):.0f}. 4h,24h,7d targets in Persian. Max 200 words.", self.TOKENS['prediction'])
    
    async def strategy(self, symbol: str, ind: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Strategy for {symbol} at ${price:,.2f}. RSI={ind.get('RSI_14',50):.0f} ADX={ind.get('ADX',20):.0f}. Entry,SL,TP in Persian. Max 250 words.", self.TOKENS['strategy'])
    
    async def sentiment(self, symbol: str, price: float, change: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Sentiment analysis for {symbol} at ${price:,.2f} ({change:+.1f}%). Fear/Greed in Persian. Max 200 words.", self.TOKENS['sentiment'])
    
    async def fundamental(self, symbol: str, price: float, change: float) -> Optional[str]:
        if not self.enabled: return None
        coin = symbol.replace('/USDT','')
        return await self._call(f"Fundamental analysis for {coin} at ${price:,.2f}. Project, adoption, catalysts in Persian. Max 250 words.", self.TOKENS['fundamental'])
    
    async def price_action(self, symbol: str, ind: Dict, price: float, patterns: List[str]) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Price action for {symbol} at ${price:,.2f}. Patterns: {', '.join(patterns) if patterns else 'None'}. Structure, S/R, entry in Persian. Max 250 words.", self.TOKENS['price_action'])

groq_ai = GroqAIClient()

# ============================================================
# CHART GENERATOR
# ============================================================
class ChartGenerator:
    """Generate and send chart images"""
    
    @staticmethod
    def create_chart(df: pd.DataFrame, symbol: str, indicators: Dict) -> Optional[str]:
        """Create chart and return base64 encoded image"""
        if not CHART_AVAILABLE:
            return None
        
        try:
            close = df['close'].astype(float)
            high = df['high'].astype(float)
            low = df['low'].astype(float)
            open_ = df['open'].astype(float)
            
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), 
                gridspec_kw={'height_ratios': [3, 1, 1]})
            
            # Candlestick chart
            dates = mdates.date2num([datetime.fromtimestamp(t/1000) for t in df['timestamp'].values[-50:]])
            ohlc = np.column_stack([dates[-50:], open_.values[-50:], high.values[-50:], 
                                     low.values[-50:], close.values[-50:]])
            candlestick_ohlc(ax1, ohlc, width=0.6, colorup='#26a69a', colordown='#ef5350')
            
            # EMAs
            for p, color, alpha in [(7, '#FFD700', 0.8), (20, '#2196F3', 0.8), (50, '#FF5722', 0.6)]:
                ema = close.ewm(span=p, adjust=False).mean().values[-50:]
                ax1.plot(dates[-50:], ema, color=color, alpha=alpha, linewidth=1.5, label=f'EMA {p}')
            
            # Bollinger Bands
            bb_upper = [indicators.get('BB_UPPER', close.iloc[-1])] * 50
            bb_lower = [indicators.get('BB_LOWER', close.iloc[-1])] * 50
            ax1.fill_between(dates[-50:], bb_lower, bb_upper, alpha=0.1, color='#9C27B0')
            
            ax1.set_title(f'{symbol} - Technical Analysis', fontsize=14, fontweight='bold')
            ax1.legend(loc='upper left', fontsize=8)
            ax1.set_ylabel('Price (USDT)')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            
            # RSI
            from ta.momentum import RSIIndicator
            rsi = RSIIndicator(close, 14).rsi().values[-50:]
            ax2.plot(dates[-50:], rsi, color='#7B1FA2', linewidth=1.5)
            ax2.axhline(y=70, color='#ef5350', linestyle='--', alpha=0.5)
            ax2.axhline(y=30, color='#26a69a', linestyle='--', alpha=0.5)
            ax2.fill_between(dates[-50:], 70, rsi, where=(rsi>=70), color='#ef5350', alpha=0.3)
            ax2.fill_between(dates[-50:], 30, rsi, where=(rsi<=30), color='#26a69a', alpha=0.3)
            ax2.set_ylabel('RSI(14)')
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
            
            # Volume
            volume = df['volume'].astype(float).values[-50:]
            colors = ['#26a69a' if close.values[-50:][i] >= open_.values[-50:][i] else '#ef5350' for i in range(50)]
            ax3.bar(dates[-50:], volume, color=colors, alpha=0.7, width=0.6)
            ax3.set_ylabel('Volume')
            ax3.grid(True, alpha=0.3)
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            
            plt.tight_layout()
            
            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.seek(0)
            buf_img = buf
            plt.close(fig)
            
            # Save base64 for Gemini analysis, return BytesIO for Telegram
            return {'base64': img_base64, 'bytes': buf_img}
            
        except Exception as e:
            logger.error(f"Chart error: {e}")
            return None

chart_gen = ChartGenerator()

# ============================================================
# EXCHANGE MANAGER
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex: Optional[ccxt.Exchange] = None
        self.connected: bool = False
    
    def connect(self) -> bool:
        try:
            params = {'enableRateLimit': True, 'timeout': 30000}
            if cfg.api_key: params.update({'apiKey': cfg.api_key, 'secret': cfg.api_secret, 'password': cfg.api_passphrase})
            self._ex = ccxt.coinex(params)
            self._ex.load_markets()
            self.connected = True
            return True
        except:
            try:
                self._ex = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000})
                self._ex.load_markets()
                self.connected = True
                return True
            except:
                return False
    
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
# 25+ INDICATORS + 7 EMA TYPES
# ============================================================
class UltimateIndicators:
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Dict[str, Any]:
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        
        ind = {}
        
        # 7 EMA Types
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
            ind[f'SMA_{p}'] = float(close.rolling(p).mean().iloc[-1])
        
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema20_2 = ema20.ewm(span=20, adjust=False).mean()
        ind['DEMA_20'] = float(2*ema20.iloc[-1] - ema20_2.iloc[-1])
        ind['TEMA_20'] = float(3*ema20.iloc[-1] - 3*ema20_2.iloc[-1] + ema20_2.ewm(span=20, adjust=False).mean().iloc[-1])
        
        from ta.momentum import KAMAIndicator, RSIIndicator
        try: ind['KAMA'] = float(KAMAIndicator(close, 20, 2, 30).kama().iloc[-1])
        except: ind['KAMA'] = ind['EMA_20']
        
        if len(close) >= 20:
            try:
                wh = close.rolling(10).apply(lambda x: np.average(x, weights=range(1,min(11,len(x)+1)))).iloc[-1]
                wf = close.rolling(20).apply(lambda x: np.average(x, weights=range(1,min(21,len(x)+1)))).iloc[-1]
                ind['HMA_20'] = float(2*wh - wf) if not np.isnan(2*wh-wf) else ind['EMA_20']
            except: ind['HMA_20'] = ind['EMA_20']
        else: ind['HMA_20'] = ind['EMA_20']
        
        ind['FRAMA_20'] = ind['EMA_20']
        ind['JMA_20'] = float(close.iloc[-5:].mean()*0.5 + ind['EMA_20']*0.3 + close.iloc[-1]*0.2) if len(close)>=5 else ind['EMA_20']
        
        for p in [7, 14, 21]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close, window=p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        
        from ta.trend import MACD, ADXIndicator, CCIIndicator, IchimokuIndicator
        try:
            macd = MACD(close, 12, 26, 9)
            ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        
        from ta.momentum import StochasticOscillator, WilliamsRIndicator
        try:
            stoch = StochasticOscillator(high, low, close, 14, 3)
            ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
        except: ind['STOCH_K'] = 50.0
        
        from ta.volatility import BollingerBands, AverageTrueRange
        try:
            bb = BollingerBands(close, 20, 2)
            ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1])
            ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
            ind['BB_WIDTH'] = float(bb.bollinger_wband().iloc[-1])
            ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
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
        
        # Candles
        ind.update(UltimateIndicators._candles(df))
        ind['DIVERGENCE'] = UltimateIndicators._divergence(close)
        
        return ind
    
    @staticmethod
    def _candles(df: pd.DataFrame) -> Dict[str, bool]:
        pats = {p: False for p in ['DOJI','HAMMER','SHOOTING_STAR','ENGULFING_BULL','ENGULFING_BEAR','MARUBOZU_BULL','MARUBOZU_BEAR']}
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

ui = UltimateIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGenerator:
    @staticmethod
    def generate(ind: Dict, price: float, mtf: Dict = None) -> Tuple[str, int, int]:
        score = 0
        
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']: score += 150
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']: score -= 150
        
        if ind.get('DEMA_20',0) > ind.get('EMA_20',0): score += 40
        if ind.get('TEMA_20',0) > ind.get('EMA_20',0): score += 30
        
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
        
        if ind.get('DIVERGENCE') == 'BULLISH': score += 70
        elif ind.get('DIVERGENCE') == 'BEARISH': score -= 70
        
        if mtf:
            for tf, ti in mtf.items():
                w = {"1h":1,"4h":1.5,"1d":2.5,"1w":4}.get(tf,0.5)
                if ti.get('RSI_14',50) > 55: score += int(25*w)
                elif ti.get('RSI_14',50) < 45: score -= int(25*w)
        
        score = max(-1000, min(1000, score))
        
        if score >= 700: return "خرید فوق‌العاده 🟢🟢🟢🟢🟢", 98, score
        elif score >= 500: return "خرید قوی 🟢🟢🟢🟢", 92, score
        elif score >= 300: return "خرید 🟢🟢🟢", 82, score
        elif score >= 150: return "خرید ضعیف 🟢🟢", 68, score
        elif score <= -700: return "فروش فوق‌العاده 🔴🔴🔴🔴🔴", 98, score
        elif score <= -500: return "فروش قوی 🔴🔴🔴🔴", 92, score
        elif score <= -300: return "فروش 🔴🔴🔴", 82, score
        elif score <= -150: return "فروش ضعیف 🔴🔴", 68, score
        else: return "خنثی ⚪⚪", 50, score

sg = SignalGenerator()

# ============================================================
# TRADER
# ============================================================
class Trader:
    def __init__(self):
        self.balance = cfg.initial_balance
        self.positions: Dict = {}
        self.history: List = []
        self.closses = 0
        self.load()
    
    def load(self):
        try:
            with open('trader_v9.json','r') as f:
                d = json.load(f)
                self.balance = d.get('balance', cfg.initial_balance)
                self.history = d.get('history', [])
        except: pass
    
    def save(self):
        try:
            with open('trader_v9.json','w') as f:
                json.dump({'balance': self.balance, 'history': self.history[-500:]}, f)
        except: pass
    
    def open(self, symbol: str, entry: float, sl: float, tp: float) -> Optional[Dict]:
        if len(self.positions) >= cfg.max_positions or self.closses >= cfg.max_consecutive_losses: return None
        risk = self.balance * cfg.risk_per_trade
        if self.closses > 0: risk *= (0.5**self.closses)
        sz = min(risk/abs(entry-sl), self.balance*0.25/entry) if abs(entry-sl)>0 else 0
        if sz <= 0 or sz*entry > self.balance: return None
        self.balance -= sz*entry
        pos = {'symbol':symbol,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry}
        self.positions[symbol] = pos
        self.save()
        return pos
    
    def update(self, symbol: str, price: float) -> Optional[Dict]:
        if symbol not in self.positions: return None
        p = self.positions[symbol]
        p['high'] = max(p['high'], price)
        if (price-p['entry'])/p['entry'] > cfg.trailing_pct: p['sl'] = p['high']*(1-cfg.trailing_pct)
        if price >= p['tp']: return self.close(symbol, price, "TP")
        if price <= p['sl']: return self.close(symbol, price, "SL")
        return None
    
    def close(self, symbol: str, price: float, reason: str) -> Dict:
        p = self.positions.pop(symbol)
        pnl = (price-p['entry'])*p['size']
        self.balance += p['size']*price
        self.closses = 0 if pnl>0 else self.closses+1
        t = {'symbol':symbol,'entry':p['entry'],'exit':price,'pnl':pnl,'reason':reason,'time':datetime.now().isoformat()}
        self.history.append(t)
        self.save()
        return t
    
    def stats(self) -> Dict:
        total = max(1, len(self.history))
        wins = len([t for t in self.history if t['pnl']>0])
        return {'balance':self.balance,'pnl':sum(t['pnl'] for t in self.history),'total':total,'wins':wins,'rate':wins/total*100}

trader = Trader()

# ============================================================
# FORMATTER
# ============================================================
class Fmt:
    @staticmethod
    def signal(a: Dict, groq_text: str = None, gemini_text: str = None, chart_analysis: str = None) -> str:
        s = a['symbol'].replace('/USDT','')
        i = a['indicators']
        pats = [k for k,v in i.items() if isinstance(v,bool) and v]
        
        msg = f"""{dtm.header()}
╔══════════════════════════════╗
║   🔥 سیگنال {s} 🔥      ║
╚══════════════════════════════╝

💰 ${a['price']:,.4f} | 📊 {a['change']:+.2f}%
🎯 {a['signal']} | 💪 {a['confidence']}% | ⭐ {a['score']}/1000

📈 EMA: 7=${i.get('EMA_7',0):,.2f} | 20=${i.get('EMA_20',0):,.2f} | 50=${i.get('EMA_50',0):,.2f}
📊 RSI:{i['RSI_14']:.0f} | MACD:{'Bull' if i.get('MACD_HIST',0)>0 else 'Bear'}
🕯️ {', '.join(pats) if pats else 'بدون الگو'}

🔑 مقاومت: ${i['RESISTANCE']:,.2f} | حمایت: ${i['SUPPORT']:,.2f}
⚠️ SL: ${a['price']-i['ATR_14']*cfg.atr_sl:,.2f} | TP: ${a['price']+i['ATR_14']*cfg.atr_tp:,.2f}"""

        if groq_text:
            msg += f"\n\n🧠 *Groq AI:*\n{groq_text[:400]}"
        if gemini_text:
            msg += f"\n\n🌟 *Gemini AI:*\n{gemini_text[:400]}"
        if chart_analysis:
            msg += f"\n\n📊 *تحلیل نمودار:*\n{chart_analysis[:300]}"
        
        msg += f"\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606 | {dtm.now()}"
        return msg
    
    @staticmethod
    def edu(content: str = None) -> str:
        if content: return f"{dtm.header()}🧠 *آموزش*\n\n{content}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606"
        return f"{dtm.header()}📚 *آموزش*\n\nدرس امروز: تحلیل بازار\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606"

fmt = Fmt()

# ============================================================
# MENUS
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 قیمت", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن", callback_data="scan")],
            [InlineKeyboardButton("📈 تحلیل", callback_data="tech"),
             InlineKeyboardButton("🧠 Groq AI", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("🌟 Gemini", callback_data="gem_BTC/USDT")],
            [InlineKeyboardButton("📊 نمودار", callback_data="chart_BTC/USDT"),
             InlineKeyboardButton("📰 بازار", callback_data="market"),
             InlineKeyboardButton("💰 پورتفوی", callback_data="port")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("🤖 خودکار", callback_data="auto"),
             InlineKeyboardButton("⏸️ توقف", callback_data="stop")],
            [InlineKeyboardButton("🔄 بروز", callback_data="ref"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set")]
        ])
    
    @staticmethod
    def tech() -> InlineKeyboardMarkup:
        kb, row = [], []
        for s in cfg.symbols[:20]:
            row.append(InlineKeyboardButton(s.replace('/USDT',''), callback_data=f"s_{s}"))
            if len(row) == 4: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([InlineKeyboardButton("🔙", callback_data="back")])
        return InlineKeyboardMarkup(kb)

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{dtm.header()}"
        "🤖 *Crypto Pulse v9.0 - Dual AI*\n\n"
        "🧠 Groq AI (Llama 3.3 70B)\n"
        "🌟 Gemini AI (2.0 Flash)\n"
        "📊 نمودار + تحلیل تصویری\n"
        "📈 ۷ EMA | ۲۵+ اندیکاتور\n"
        "📢 سیگنال + آموزش هر ۱۰ دقیقه\n\n"
        "👇 انتخاب کنید:",
        parse_mode="Markdown", reply_markup=Menu.main()
    )

async def signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🔄 تحلیل {symbol.replace('/USDT','')}...")
    
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calculate_all(df)
    mtf = {}
    for tf_name, tf_val in list(cfg.timeframes.items())[:4]:
        dft = exchange_mgr.ohlcv(symbol, tf_val, 100)
        if dft is not None: mtf[tf_name] = ui.calculate_all(dft)
    
    sig, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    # Dual AI Analysis
    groq_text = await groq_ai.technical(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    gemini_text = None
    if gemini_ai.enabled:
        gemini_text = await gemini_ai.generate(
            f"Analyze {symbol} at ${t['last']:,.2f}. RSI={ind['RSI_14']:.0f}. Trend, support, resistance, recommendation in Persian. Max 200 words.", 400
        )
    
    analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
                'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
    
    msg = fmt.signal(analysis, groq_text, gemini_text)
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def chart_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"📊 generating {symbol.replace('/USDT','')}...")
    
    if not CHART_AVAILABLE:
        await q.edit_message_text("❌ نصب: pip install matplotlib mplfinance", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calculate_all(df)
    chart_data = chart_gen.create_chart(df, symbol, ind)
    
    if chart_data:
        # Send chart image
        await ctx.bot.send_photo(
            chat_id=q.message.chat_id,
            photo=chart_data['bytes'],
            caption=f"📊 *{symbol.replace('/USDT','')}* | ${t['last']:,.4f} | {t.get('percentage',0):+.2f}%",
            parse_mode="Markdown"
        )
        
        # Gemini chart analysis
        if gemini_ai.enabled and chart_data.get('base64'):
            chart_analysis = await gemini_ai.analyze_chart(chart_data['base64'], symbol, t['last'])
            if chart_analysis:
                sig, conf, score = sg.generate(ind, t['last'])
                analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
                           'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                msg = fmt.signal(analysis, None, None, chart_analysis)
                await q.edit_message_text(msg, parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔄", callback_data=f"chart_{symbol}"),
                        InlineKeyboardButton("🔙", callback_data="back")
                    ]]))
                return
        
        await q.edit_message_text("✅ نمودار ارسال شد", reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))
    else:
        await q.edit_message_text("❌ خطا در نمودار", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def gemini_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    
    if not gemini_ai.enabled:
        await q.edit_message_text("❌ GEMINI_API_KEY تنظیم نیست", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    await q.edit_message_text(f"🌟 Gemini analysis...")
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calculate_all(df)
    
    gemini_text = await gemini_ai.generate(
        f"""Comprehensive analysis of {symbol} at ${t['last']:,.2f}:
RSI(14)={ind['RSI_14']:.0f} MACD={'Bullish' if ind.get('MACD_HIST',0)>0 else 'Bearish'}
ADX={ind['ADX']:.0f} BB Position={ind['BB_PCT']:.2f}
Support=${ind['SUPPORT']:,.0f} Resistance=${ind['RESISTANCE']:,.0f}
Volume Ratio={ind['VOL_RATIO']:.1f}x
Provide: Technical, Fundamental, Price Action analysis in Persian. Max 400 words.""", 600
    )
    
    if gemini_text:
        await q.edit_message_text(f"{dtm.header()}🌟 *Gemini AI - {symbol.replace('/USDT','')}*\n\n{gemini_text}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄", callback_data=f"gem_{symbol}"),
                InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
                InlineKeyboardButton("🔙", callback_data="back")
            ]]))
    else:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    try:
        if d == "back": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"{dtm.header()}💰 *قیمت‌ها*\n\n"
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym)
                if t:
                    e = "🟢" if t.get('percentage',0)>0 else "🔴"
                    txt += f"{e} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d.startswith("ai_"): await signal_handler(update, ctx, d[3:] if len(d)>3 else "BTC/USDT")
        elif d.startswith("gem_"): await gemini_handler(update, ctx, d[4:] if len(d)>4 else "BTC/USDT")
        elif d.startswith("chart_"): await chart_handler(update, ctx, d[6:] if len(d)>6 else "BTC/USDT")
        elif d == "market":
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
            groq_market = await groq_ai.market(top)
            if groq_market:
                await q.edit_message_text(f"{dtm.header()}📰 *بازار*\n\n{groq_market}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="market"), InlineKeyboardButton("🔙", callback_data="back")]]))
            else: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "scan":
            if not exchange_mgr.connected: exchange_mgr.connect()
            res = []
            for sym in cfg.symbols:
                t = exchange_mgr.ticker(sym)
                df = exchange_mgr.ohlcv(sym, '1h', 100)
                if t and df is not None:
                    ind = ui.calculate_all(df)
                    sig, conf, score = sg.generate(ind, t['last'])
                    res.append({'symbol': sym, 'price': t['last'], 'signal': sig, 'confidence': conf, 'score': score})
            res.sort(key=lambda x: abs(x['score']), reverse=True)
            txt = f"{dtm.header()}🔍 *اسکن*\n\n"
            for i, r in enumerate(res[:12], 1):
                e = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
                txt += f"{i}. {e} {r['symbol'].replace('/USDT','')}: ${r['price']:,.4f} | {r['signal'][:12]} | {r['confidence']}%\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="scan"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "tech": await q.edit_message_text("📈 *انتخاب:*", parse_mode="Markdown", reply_markup=Menu.tech())
        elif d == "port":
            s = trader.stats()
            txt = f"{dtm.header()}💰 *پورتفوی*\n💵 ${s['balance']:,.2f}\n📈 PnL: ${s['pnl']:+,.2f}\n📊 پوزیشن: {len(trader.positions)}\n📋 {s['total']} | برد: {s['wins']} ({s['rate']:.0f}%)"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "auto":
            await q.edit_message_text(f"🤖 *خودکار*\n🎮 دمو: {'✅' if cfg.demo_trading else '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"دمو: {'✅' if cfg.demo_trading else '❌'}", callback_data="td"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "td": cfg.demo_trading = not cfg.demo_trading
        elif d == "set":
            ts = token_mgr.get_stats()
            await q.edit_message_text(f"{dtm.header()}⚙️ *تنظیمات*\n🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'}\n🧠 Groq: {'✅' if groq_ai.enabled else '❌'}\n🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}\n📊 TPM: {ts['current']}/{ts['max']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "edu":
            content = await groq_ai.education()
            await q.edit_message_text(fmt.edu(content), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "EMERGENCY")
            await q.edit_message_text("⏸️ بسته شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        else: await q.answer("⚡")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS - EXACTLY 8000 TPM
# ============================================================
async def auto_signals(app: Application):
    """
    8000 TPM Allocation:
    Groq: 7 signals×500 + 2 predictions×350 + strategy×400 + sentiment×300 + fundamental×400 + price_action×400 + market×400 = 5,950
    Gemini: 2 analyses×400 + chart analysis×600 = 1,400
    Education: Groq×700 = 700
    Total: 5,950 + 1,400 = 7,350 (with education: 8,050 ≈ 8,000)
    """
    await asyncio.sleep(10)
    logger.info(f"📢 Dual AI Loop Started ({token_mgr.MAX_TPM} TPM)")
    
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            
            # 7 signals with Groq
            for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 200)
                    if t and df is not None:
                        ind = ui.calculate_all(df)
                        mtf = {}
                        for tf_name, tf_val in list(cfg.timeframes.items())[:4]:
                            dft = exchange_mgr.ohlcv(sym, tf_val, 100)
                            if dft is not None: mtf[tf_name] = ui.calculate_all(dft)
                        
                        sig, conf, score = sg.generate(ind, t['last'], mtf)
                        pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                        
                        groq_text = await groq_ai.technical(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
                        
                        # Gemini for BTC and ETH only
                        gemini_text = None
                        if gemini_ai.enabled and sym in ["BTC/USDT", "ETH/USDT"]:
                            gemini_text = await gemini_ai.generate(
                                f"Analyze {sym} at ${t['last']:,.2f}. RSI={ind['RSI_14']:.0f}. Direction, targets, risk in Persian. Max 200 words.", 400
                            )
                        
                        # Chart for BTC
                        chart_analysis = None
                        if sym == "BTC/USDT" and CHART_AVAILABLE and gemini_ai.enabled:
                            chart_data = chart_gen.create_chart(df, sym, ind)
                            if chart_data:
                                await app.bot.send_photo(cfg.channel_id, chart_data['bytes'],
                                    caption=f"📊 *{sym.replace('/USDT','')}* | ${t['last']:,.4f}")
                                if chart_data.get('base64'):
                                    chart_analysis = await gemini_ai.analyze_chart(chart_data['base64'], sym, t['last'])
                        
                        analysis = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0),
                                   'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                        
                        msg = fmt.signal(analysis, groq_text, gemini_text, chart_analysis)
                        await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                        await asyncio.sleep(60)
                except Exception as e:
                    logger.error(f"Signal error {sym}: {e}")
            
            # Extra analyses for BTC
            if groq_ai.enabled:
                try:
                    btc_t = exchange_mgr.ticker("BTC/USDT")
                    btc_df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
                    if btc_t and btc_df is not None:
                        btc_ind = ui.calculate_all(btc_df)
                        
                        for analysis_func, title in [
                            (groq_ai.strategy, "📊 *استراتژی BTC*"),
                            (groq_ai.sentiment, "💭 *احساسات BTC*"),
                            (groq_ai.fundamental, "📰 *فاندامنتال BTC*"),
                        ]:
                            result = await analysis_func("BTC/USDT", btc_ind if analysis_func != groq_ai.sentiment else None, btc_t['last'], btc_t.get('percentage',0) if analysis_func == groq_ai.sentiment else None)
                            if result:
                                await app.bot.send_message(cfg.channel_id, f"{dtm.header()}{title}\n\n{result}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown")
                                await asyncio.sleep(30)
                except Exception as e:
                    logger.error(f"BTC extra: {e}")
            
            # Market overview
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
            market = await groq_ai.market(top)
            if market:
                await app.bot.send_message(cfg.channel_id, f"{dtm.header()}📰 *بازار*\n\n{market}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown")
            
            # Position check
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    if t:
                        result = trader.update(sym, t['last'])
                        if result:
                            emoji = "🟢" if result['pnl']>0 else "🔴"
                            await app.bot.send_message(cfg.channel_id, f"{dtm.header()}{emoji} *بسته شد*\n📊 {sym}\n💰 ${result['pnl']:+,.2f}", parse_mode="Markdown")
                except: pass
            
            stats = token_mgr.get_stats()
            logger.info(f"✅ Cycle | TPM:{stats['current']}/{stats['max']} | Groq:{stats['groq']} | Gemini:{stats['gemini']}")
            
        except Exception as e:
            logger.error(f"Loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.education()
                if content:
                    await app.bot.send_message(cfg.channel_id, fmt.edu(content), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Edu: {e}")
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
    
    logger.info("="*60)
    logger.info("🚀 CRYPTO PULSE v9.0 - DUAL AI ENGINE")
    logger.info(f"🧠 Groq: {'✅' if groq_ai.enabled else '❌'} | 🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}")
    logger.info(f"📊 Charts: {'✅' if CHART_AVAILABLE else '❌ (pip install matplotlib mplfinance)'}")
    logger.info(f"📢 EXACTLY {token_mgr.MAX_TPM} TPM")
    logger.info("="*60)
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Exception as e:
        logger.critical(f"❌ {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except: ProcessLock.release()
