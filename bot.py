#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║   CRYPTO PULSE ULTIMATE DUAL AI TRADING BOT v10.0 - GLASS EDITION   ║
║   Groq AI + Gemini AI | 50+ Glass Buttons | 4h/1d/1w Timeframes     ║
║   Long/Mid EMAs | Full Indicators | Auto Install Charts              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io
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
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# AUTO INSTALL CHARTS
# ============================================================
def auto_install_charts():
    """Auto install matplotlib and mplfinance if missing"""
    try:
        import matplotlib
        from mplfinance.original_flavor import candlestick_ohlc
        return True
    except ImportError:
        logger.info("📦 Installing matplotlib & mplfinance...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "mplfinance", "--quiet"])
            return True
        except:
            return False

CHART_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from mplfinance.original_flavor import candlestick_ohlc
    CHART_AVAILABLE = True
except ImportError:
    pass

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

for name, level in [('crypto_v10.log', logging.INFO), ('crypto_v10_debug.log', logging.DEBUG), ('crypto_v10_errors.log', logging.ERROR)]:
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
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
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
    
    # Primary TFs for deep analysis
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
                if pid and cls._alive(pid):
                    logger.critical(f"❌ Already running (PID: {pid})")
                    return False
                os.remove(cls._file)
            with open(cls._file, 'w') as f:
                f.write(str(os.getpid()))
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
        return f"📅 {DTM.persian()}\n🌍 UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"

dtm = DTM()

# ============================================================
# TOKEN MANAGER - 8000 TPM
# ============================================================
class TokenManager:
    MAX_TPM: int = 8000
    def __init__(self):
        self._usage: deque = deque()
        self.groq_tokens: int = 0
        self.gemini_tokens: int = 0
        self._requests: int = 0
    @property
    def current(self) -> int:
        now = time.time()
        while self._usage and now - self._usage[0][0] > 60:
            self._usage.popleft()
        return sum(t for _, t in self._usage)
    @property
    def remaining(self) -> int: return max(0, self.MAX_TPM - self.current)
    def can(self, tokens: int = 500) -> bool: return (self.current + tokens) <= self.MAX_TPM
    def wait(self, tokens: int = 500) -> float:
        if self.can(tokens): return 0
        if self._usage: return max(0, 60 - (time.time() - self._usage[0][0]) + 1)
        return 60
    def record(self, tokens: int, source: str = "groq"):
        self._usage.append((time.time(), tokens))
        self._requests += 1
        if source == "groq": self.groq_tokens += tokens
        else: self.gemini_tokens += tokens
    def stats(self) -> Dict:
        return {'current': self.current, 'max': self.MAX_TPM, 'remaining': self.remaining,
                'groq': self.groq_tokens, 'gemini': self.gemini_tokens, 'requests': self._requests}

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
        else: logger.warning("⚠️ Gemini API Key not set")
    
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
        except Exception as e: logger.error(f"Gemini: {e}"); return None
    
    async def analyze_chart(self, b64: str, symbol: str, price: float) -> Optional[str]:
        if not self.enabled or not token_mgr.can(600): return None
        try:
            resp = await self.client.post(f"{self.URL}?key={self.api_key}",
                json={"contents": [{"parts": [{"text": f"Analyze chart for {symbol} at ${price:,.2f}. Trend, S/R, patterns in Persian."}, {"inline_data": {"mime_type": "image/png", "data": b64}}]}], "generationConfig": {"maxOutputTokens": 600, "temperature": 0.7}})
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text: token_mgr.record(600, "gemini"); return text
            return None
        except Exception as e: logger.error(f"Gemini Chart: {e}"); return None

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
                json={"model": self.MODEL, "messages": [{"role": "system", "content": "You are an elite crypto analyst. Respond in Persian (فارسی). Use emojis."}, {"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7})
            if resp.status_code == 200:
                data = resp.json()
                token_mgr.record(data.get('usage', {}).get('total_tokens', max_tokens), "groq")
                return data["choices"][0]["message"]["content"]
            return None
        except Exception as e: logger.error(f"Groq: {e}"); return None
    
    async def technical(self, symbol: str, ind: Dict, price: float, change: float, patterns: List[str], mtf: Dict) -> Optional[str]:
        if not self.enabled: return None
        mtf_text = " | ".join([f"{t}:RSI={i.get('RSI_14',50):.0f}" for t,i in mtf.items()])
        prompt = f"""Analyze {symbol} at ${price:,.4f} ({change:+.2f}%):
RSI={ind.get('RSI_14',50):.0f} MACD={'Bull' if ind.get('MACD_HIST',0)>0 else 'Bear'} ADX={ind.get('ADX',20):.0f}
CCI={ind.get('CCI',0):.0f} MFI={ind.get('MFI',50):.0f} BB%={ind.get('BB_PCT',0.5):.2f}
Vol={ind.get('VOL_RATIO',1):.1f}x Support=${ind.get('SUPPORT',0):.0f} Resistance=${ind.get('RESISTANCE',0):.0f}
Patterns: {', '.join(patterns) if patterns else 'None'} Div: {ind.get('DIVERGENCE','NONE')}
MTF: {mtf_text}
In Persian: Summary, Direction, Entry/Exit, Risk, Confidence. Max 300 words."""
        return await self._call(prompt, self.TOKENS['technical'])
    
    async def market(self, coins: List[Dict]) -> Optional[str]:
        if not self.enabled: return None
        txt = "\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])
        return await self._call(f"Market overview in Persian:\n{txt}\nSentiment, trends. Max 250 words.", self.TOKENS['market'])
    
    async def education(self) -> Optional[str]:
        if not self.enabled: return None
        topics = ["تحلیل تکنیکال","مدیریت ریسک","روانشناسی","الگوهای کندلی","استراتژی","فیبوناچی","ایچیموکو","پرایس اکشن","فاندامنتال","واگرایی"]
        return await self._call(f"Educational post in Persian about: {random.choice(topics)}. 400+ words, emojis, step-by-step guide, golden nugget.", self.TOKENS['education'])
    
    async def prediction(self, symbol: str, ind: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Predict {symbol} at ${price:,.2f}. RSI={ind.get('RSI_14',50):.0f}. 4h,24h,7d targets in Persian. Max 200 words.", self.TOKENS['prediction'])
    
    async def strategy(self, symbol: str, ind: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Strategy for {symbol} at ${price:,.2f}. RSI={ind.get('RSI_14',50):.0f} ADX={ind.get('ADX',20):.0f}. Entry,SL,TP in Persian. Max 250 words.", self.TOKENS['strategy'])
    
    async def sentiment(self, symbol: str, price: float, change: float) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Sentiment for {symbol} at ${price:,.2f} ({change:+.1f}%). Fear/Greed in Persian. Max 200 words.", self.TOKENS['sentiment'])
    
    async def fundamental(self, symbol: str, price: float, change: float) -> Optional[str]:
        if not self.enabled: return None
        coin = symbol.replace('/USDT','')
        return await self._call(f"Fundamental analysis for {coin} at ${price:,.2f}. Project, adoption, catalysts in Persian. Max 250 words.", self.TOKENS['fundamental'])
    
    async def price_action(self, symbol: str, ind: Dict, price: float, patterns: List[str]) -> Optional[str]:
        if not self.enabled: return None
        return await self._call(f"Price action for {symbol} at ${price:,.2f}. Patterns: {', '.join(patterns) if patterns else 'None'}. Structure, S/R, entry in Persian. Max 250 words.", self.TOKENS['price_action'])

groq_ai = GroqAI()

# ============================================================
# CHART GENERATOR
# ============================================================
class ChartGenerator:
    @staticmethod
    def create(df: pd.DataFrame, symbol: str, indicators: Dict) -> Optional[Dict]:
        if not CHART_AVAILABLE: return None
        try:
            close = df['close'].astype(float); high = df['high'].astype(float)
            low = df['low'].astype(float); open_ = df['open'].astype(float)
            
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 11), gridspec_kw={'height_ratios': [3, 1, 1]})
            
            dates = mdates.date2num([datetime.fromtimestamp(t/1000) for t in df['timestamp'].values[-60:]])
            ohlc = np.column_stack([dates[-60:], open_.values[-60:], high.values[-60:], low.values[-60:], close.values[-60:]])
            candlestick_ohlc(ax1, ohlc, width=0.6, colorup='#26a69a', colordown='#ef5350')
            
            for p, color in [(7, '#FFD700'), (20, '#2196F3'), (50, '#FF5722'), (100, '#9C27B0'), (200, '#FF9800')]:
                ema = close.ewm(span=p, adjust=False).mean().values[-60:]
                ax1.plot(dates[-60:], ema, color=color, alpha=0.7, linewidth=1.2, label=f'EMA{p}')
            
            ax1.fill_between(dates[-60:], [indicators.get('BB_LOWER',close.iloc[-1])]*60, [indicators.get('BB_UPPER',close.iloc[-1])]*60, alpha=0.1, color='#9C27B0')
            ax1.set_title(f'{symbol}', fontsize=14, fontweight='bold')
            ax1.legend(loc='upper left', fontsize=7)
            ax1.grid(True, alpha=0.3)
            
            from ta.momentum import RSIIndicator
            rsi = RSIIndicator(close, 14).rsi().values[-60:]
            ax2.plot(dates[-60:], rsi, color='#7B1FA2', linewidth=1.5)
            ax2.axhline(y=70, color='#ef5350', linestyle='--', alpha=0.5)
            ax2.axhline(y=30, color='#26a69a', linestyle='--', alpha=0.5)
            ax2.set_ylabel('RSI'); ax2.set_ylim(0, 100); ax2.grid(True, alpha=0.3)
            
            volume = df['volume'].astype(float).values[-60:]
            colors = ['#26a69a' if close.values[-60:][i] >= open_.values[-60:][i] else '#ef5350' for i in range(60)]
            ax3.bar(dates[-60:], volume, color=colors, alpha=0.7, width=0.6)
            ax3.set_ylabel('Volume'); ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.seek(0)
            plt.close(fig)
            return {'base64': b64, 'bytes': buf}
        except Exception as e: logger.error(f"Chart: {e}"); return None

chart_gen = ChartGenerator()

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
# 25+ INDICATORS + 7 EMA + LONG/MID TERM
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df: pd.DataFrame) -> Dict[str, Any]:
        close = df['close'].astype(float); high = df['high'].astype(float)
        low = df['low'].astype(float); volume = df['volume'].astype(float)
        ind = {}
        
        # EMAs - Short/Mid/Long Term
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
        ind['JMA_20'] = float(close.iloc[-5:].mean()*0.5 + ind['EMA_20']*0.3 + close.iloc[-1]*0.2) if len(close)>=5 else ind['EMA_20']
        
        # Long/Mid term EMAs
        ind['EMA_LONG'] = float(close.ewm(span=200, adjust=False).mean().iloc[-1])
        ind['EMA_MID'] = float(close.ewm(span=100, adjust=False).mean().iloc[-1])
        ind['EMA_SHORT'] = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
        
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
        
        # Pivot
        h, l, c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        ind['PIVOT'] = float((h+l+c)/3); ind['R1'] = float(2*ind['PIVOT']-l); ind['S1'] = float(2*ind['PIVOT']-h)
        
        # Fibonacci
        h50 = high.rolling(50).max().iloc[-1] if len(high)>=50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low)>=50 else low.min()
        diff = h50 - l50
        for lvl in [0.236, 0.382, 0.5, 0.618, 0.786]:
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
        if ind.get('THREE_WHITE'): score += 60
        if ind.get('THREE_BLACK'): score -= 60
        if ind.get('DIVERGENCE') == 'BULLISH': score += 70
        elif ind.get('DIVERGENCE') == 'BEARISH': score -= 70
        if ind.get('EMA_LONG',0) > ind.get('EMA_MID',0) > ind.get('EMA_SHORT',0): score += 50
        if mtf:
            for tf, ti in mtf.items():
                w = {"4h":2,"1d":3,"1w":5}.get(tf,1)
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
        pos = {'symbol':symbol,'size':sz,'entry':entry,'sl':sl,'tp':tp,'high':entry}
        self.positions[symbol] = pos; self.save(); return pos
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
# FORMATTER - GLASS PREMIUM STYLE
# ============================================================
class Fmt:
    @staticmethod
    def signal(a: Dict, groq_text: str = None, gemini_text: str = None, chart_analysis: str = None, tf_4h: Dict = None, tf_1d: Dict = None, tf_1w: Dict = None) -> str:
        s = a['symbol'].replace('/USDT',''); i = a['indicators']
        pats = [k for k,v in i.items() if isinstance(v,bool) and v]
        
        msg = f"""
╔══════════════════════════════════════════════════════╗
║         🔥 سیگنال جامع {s} 🔥                   ║
╚══════════════════════════════════════════════════════╝

{dtm.header()}

💰 *قیمت:* ${a['price']:,.4f}
📊 *تغییر ۲۴h:* {a['change']:+.2f}%
🎯 *سیگنال:* {a['signal']}
💪 *اطمینان:* {a['confidence']}% | ⭐ *امتیاز:* {a['score']}/1000

┏━━━━━━ 📈 EMA های میان‌مدت و بلندمدت ━━━━━━┓
• EMA_7 (کوتاه): ${i.get('EMA_7',0):,.2f}
• EMA_20 (کوتاه): ${i.get('EMA_20',0):,.2f}
• EMA_50 (میان‌مدت): ${i.get('EMA_50',0):,.2f}
• EMA_100 (میان‌مدت): ${i.get('EMA_100',0):,.2f}
• EMA_200 (بلندمدت): ${i.get('EMA_200',0):,.2f}
• DEMA_20: ${i.get('DEMA_20',0):,.2f}
• TEMA_20: ${i.get('TEMA_20',0):,.2f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━ 📊 اندیکاتورها و اسیلاتورها ━━━━━━┓
• RSI(14): {i['RSI_14']:.1f} | RSI(7): {i.get('RSI_7',50):.1f}
• MACD: {'صعودی ⬆️' if i.get('MACD_HIST',0)>0 else 'نزولی ⬇️'}
• ADX: {i['ADX']:.1f} | CCI: {i['CCI']:.1f} | MFI: {i['MFI']:.1f}
• Stochastic K: {i.get('STOCH_K',50):.1f}
• BB Width: {i.get('BB_WIDTH',0):.4f} | BB %B: {i.get('BB_PCT',0.5):.2f}
• ATR(14): {i['ATR_14']:.4f} | ATR%: {i.get('ATR_PCT',0):.2f}%
• حجم نسبی: {i.get('VOL_RATIO',1):.1f}x
• قدرت روند: {i.get('TREND_STR',0):.1f}%
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━ 🕯️ الگوهای کندلی ━━━━━━┓
• الگوها: {', '.join(pats) if pats else 'بدون الگوی خاص'}
• واگرایی: {i.get('DIVERGENCE','NONE')}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━ 🔑 سطوح کلیدی و فیبوناچی ━━━━━━┓
• مقاومت: ${i['RESISTANCE']:,.4f} | R1: ${i.get('R1',0):,.4f}
• پیوت: ${i.get('PIVOT',0):,.4f}
• حمایت: ${i['SUPPORT']:,.4f} | S1: ${i.get('S1',0):,.4f}
• Fib 0.382: ${i.get('FIB_382',0):,.4f}
• Fib 0.618: ${i.get('FIB_618',0):,.4f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"""

        if tf_4h:
            msg += f"""
┏━━━━━━ ⏰ تایم‌فریم ۴ ساعته ━━━━━━┓
• RSI: {tf_4h.get('RSI_14',50):.0f} | MACD: {'صعودی' if tf_4h.get('MACD_HIST',0)>0 else 'نزولی'}
• EMA_50: ${tf_4h.get('EMA_50',0):,.2f} | EMA_200: ${tf_4h.get('EMA_200',0):,.2f}
• ADX: {tf_4h.get('ADX',20):.0f} | BB%: {tf_4h.get('BB_PCT',0.5):.2f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"""

        if tf_1d:
            msg += f"""
┏━━━━━━ ⏰ تایم‌فریم ۱ روزه ━━━━━━┓
• RSI: {tf_1d.get('RSI_14',50):.0f} | MACD: {'صعودی' if tf_1d.get('MACD_HIST',0)>0 else 'نزولی'}
• EMA_50: ${tf_1d.get('EMA_50',0):,.2f} | EMA_200: ${tf_1d.get('EMA_200',0):,.2f}
• ADX: {tf_1d.get('ADX',20):.0f} | BB%: {tf_1d.get('BB_PCT',0.5):.2f}
• قدرت روند: {tf_1d.get('TREND_STR',0):.1f}%
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"""

        if tf_1w:
            msg += f"""
┏━━━━━━ ⏰ تایم‌فریم ۱ هفته ━━━━━━┓
• RSI: {tf_1w.get('RSI_14',50):.0f} | MACD: {'صعودی' if tf_1w.get('MACD_HIST',0)>0 else 'نزولی'}
• EMA_50: ${tf_1w.get('EMA_50',0):,.2f} | EMA_200: ${tf_1w.get('EMA_200',0):,.2f}
• ADX: {tf_1w.get('ADX',20):.0f} | BB%: {tf_1w.get('BB_PCT',0.5):.2f}
• قدرت روند: {tf_1w.get('TREND_STR',0):.1f}%
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"""

        msg += f"""
⚠️ *حد ضرر:* ${a['price']-i['ATR_14']*cfg.atr_sl:,.4f}
🎯 *حد سود:* ${a['price']+i['ATR_14']*cfg.atr_tp:,.4f}
📊 *ریسک/ریوارد:* 1:{cfg.atr_tp/cfg.atr_sl:.1f}"""

        if groq_text:
            msg += f"\n\n🧠 *تحلیل Groq AI:*\n{groq_text[:500]}"
        if gemini_text:
            msg += f"\n\n🌟 *تحلیل Gemini AI:*\n{gemini_text[:400]}"
        if chart_analysis:
            msg += f"\n\n📊 *تحلیل نمودار:*\n{chart_analysis[:300]}"
        
        msg += f"""

╔══════════════════════════════════════════════════════╗
║  📋 *نتیجه‌گیری نهایی:*                             ║
║  سیگنال: {a['signal'][:30]}                        ║
║  اطمینان: {a['confidence']}% | امتیاز: {a['score']}/1000           ║
║  وضعیت: {'مناسب برای ورود ✅' if a['confidence'] >= 70 else 'نیاز به بررسی بیشتر ⚠️'}                ║
╚══════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606 | {dtm.now()}"""
        return msg
    
    @staticmethod
    def edu(content: str = None) -> str:
        if content:
            return f"""
╔══════════════════════════════════════════════════════╗
║         📚 آموزش تخصصی کریپتو 📚                   ║
╚══════════════════════════════════════════════════════╝

{dtm.header()}

🧠 *{content}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606 | {dtm.now()}"""
        return f"""
╔══════════════════════════════════════════════════════╗
║         📚 آموزش تخصصی 📚                           ║
╚══════════════════════════════════════════════════════╝

{dtm.header()}

📖 *درس امروز:* تحلیل حرفه‌ای بازار کریپتو

🔍 *نکات کلیدی:*
✨ روند دوست شماست - خلاف آن معامله نکنید
✨ ریسک/ریوارد حداقل ۱:۲ را رعایت کنید
✨ بیش از ۲٪ سرمایه را در یک معامله ریسک نکنید
✨ حد ضرر اجباری است - بدون استثنا
✨ بعد از ۳ ضرر متوالی استراحت کنید
✨ ژورنال معاملاتی داشته باشید
✨ صبوری = سودآوری

💡 *رمز موفقیت:* ۲۰٪ استراتژی + ۳۰٪ مدیریت ریسک + ۵۰٪ روانشناسی

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606 | {dtm.now()}"""

fmt = Fmt()

# ============================================================
# 50+ GLASS BUTTONS MENUS
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌ها", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan")],
            [InlineKeyboardButton("📈 تحلیل ۴h", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("📈 تحلیل ۱d", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("📈 تحلیل ۱w", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 Groq AI", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("🌟 Gemini AI", callback_data="gem_BTC/USDT"),
             InlineKeyboardButton("📊 نمودار", callback_data="chart_BTC/USDT")],
            [InlineKeyboardButton("📰 تحلیل بازار", callback_data="market"),
             InlineKeyboardButton("📊 استراتژی BTC", callback_data="strat"),
             InlineKeyboardButton("💭 احساسات", callback_data="sent")],
            [InlineKeyboardButton("📰 فاندامنتال", callback_data="fund"),
             InlineKeyboardButton("📊 پرایس اکشن", callback_data="pa"),
             InlineKeyboardButton("🔮 پیش‌بینی", callback_data="pred")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf"),
             InlineKeyboardButton("📋 تاریخچه", callback_data="hist")],
            [InlineKeyboardButton("🤖 معاملات خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("🔑 وضعیت", callback_data="status")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("🕯️ الگوها", callback_data="patterns"),
             InlineKeyboardButton("📉 ترس و طمع", callback_data="fear")],
            [InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale"),
             InlineKeyboardButton("💎 آلت‌کوین", callback_data="alt"),
             InlineKeyboardButton("🔮 پیش‌بینی ۷ روز", callback_data="pred7")],
            [InlineKeyboardButton("📊 مقایسه", callback_data="compare"),
             InlineKeyboardButton("📈 نمودار زنده", callback_data="live"),
             InlineKeyboardButton("🔔 هشدارها", callback_data="alerts")],
            [InlineKeyboardButton("⏸️ توقف اضطراری", callback_data="stop"),
             InlineKeyboardButton("🔄 بروزرسانی", callback_data="ref"),
             InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ])
    
    @staticmethod
    def tech() -> InlineKeyboardMarkup:
        kb, row = [], []
        for s in cfg.symbols[:20]:
            row.append(InlineKeyboardButton(s.replace('/USDT',''), callback_data=f"s_{s}"))
            if len(row) == 4: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        return InlineKeyboardMarkup(kb)

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"""
╔══════════════════════════════════════════════════════╗
║   🤖 CRYPTO PULSE v10.0 - GLASS EDITION 🤖         ║
║   Dual AI | 50+ Buttons | 4h/1d/1w | Full Indicators ║
╚══════════════════════════════════════════════════════╝

{dtm.header()}

✨ *امکانات:*
🧠 Groq AI (Llama 3.3 70B) + 🌟 Gemini AI (2.0 Flash)
📊 ۲۵+ اندیکاتور | ۷ EMA | فیبوناچی | پیوت
⏰ تایم‌فریم: ۴h + ۱d + ۱w
📈 EMA بلندمدت و میان‌مدت
🕯️ ۱۰+ الگوی کندلی
📊 نمودار + تحلیل تصویری
📢 سیگنال هر ۴ ساعت | 📚 آموزش هر ۱ ساعت
💰 معاملات خودکار دمو

👇 *انتخاب کنید:*
""",
        parse_mode="Markdown", reply_markup=Menu.main()
    )

async def signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🔄 تحلیل جامع {symbol.replace('/USDT','')}...")
    
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calc(df)
    mtf = {}
    for tf_name in cfg.primary_tfs:
        dft = exchange_mgr.ohlcv(symbol, tf_name, 100)
        if dft is not None: mtf[tf_name] = ui.calc(dft)
    
    sig, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    tf_4h = mtf.get('4h')
    tf_1d = mtf.get('1d')
    tf_1w = mtf.get('1w')
    
    groq_text = await groq_ai.technical(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    gemini_text = None
    if gemini_ai.enabled:
        gemini_text = await gemini_ai.generate(
            f"Comprehensive analysis of {symbol} at ${t['last']:,.2f}. Include 4h, 1d, 1w outlook. Technical + Fundamental + Price Action in Persian. Max 300 words.", 500
        )
    
    analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
                'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
    
    msg = fmt.signal(analysis, groq_text, gemini_text, None, tf_4h, tf_1d, tf_1w)
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def tf_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT", tf: str = "4h"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"⏰ تحلیل تایم‌فریم {tf} برای {symbol.replace('/USDT','')}...")
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, tf, 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calc(df)
    sig, conf, score = sg.generate(ind, t['last'])
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    msg = f"""
╔══════════════════════════════════════════════════════╗
║     ⏰ تحلیل تایم‌فریم {tf} - {symbol.replace('/USDT','')}     ║
╚══════════════════════════════════════════════════════╝

{dtm.header()}

💰 قیمت: ${t['last']:,.4f}
🎯 سیگنال: {sig} | 💪 {conf}% | ⭐ {score}/1000

📈 EMA: 7=${ind.get('EMA_7',0):,.2f} | 20=${ind.get('EMA_20',0):,.2f} | 50=${ind.get('EMA_50',0):,.2f} | 200=${ind.get('EMA_200',0):,.2f}
📊 RSI:{ind['RSI_14']:.0f} | MACD:{'Bull' if ind.get('MACD_HIST',0)>0 else 'Bear'} | ADX:{ind['ADX']:.0f}
🕯️ الگوها: {', '.join(pats) if pats else 'بدون الگو'}
🔄 واگرایی: {ind.get('DIVERGENCE','NONE')}
🔑 حمایت: ${ind['SUPPORT']:,.2f} | مقاومت: ${ind['RESISTANCE']:,.2f}
📊 Fib 0.618: ${ind.get('FIB_618',0):,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606 | {dtm.now()}"""
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"tf{tf}_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def chart_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    
    if not CHART_AVAILABLE:
        if auto_install_charts():
            await q.edit_message_text("📦 کتابخانه‌ها نصب شد. دوباره تلاش کنید.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data=f"chart_{symbol}"), InlineKeyboardButton("🔙", callback_data="back")]]))
        else:
            await q.edit_message_text("❌ نصب نشد. دستی: pip install matplotlib mplfinance", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    await q.edit_message_text(f"📊 در حال ساخت نمودار {symbol.replace('/USDT','')}...")
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calc(df)
    chart_data = chart_gen.create(df, symbol, ind)
    
    if chart_data:
        await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=chart_data['bytes'],
            caption=f"📊 *{symbol.replace('/USDT','')}* | ${t['last']:,.4f} | {t.get('percentage',0):+.2f}%", parse_mode="Markdown")
        
        if gemini_ai.enabled and chart_data.get('base64'):
            chart_analysis = await gemini_ai.analyze_chart(chart_data['base64'], symbol, t['last'])
            if chart_analysis:
                await q.edit_message_text(f"{dtm.header()}📊 *تحلیل نمودار*\n\n{chart_analysis}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data=f"chart_{symbol}"), InlineKeyboardButton("🔙", callback_data="back")]]))
                return
        
        await q.edit_message_text("✅ نمودار ارسال شد", reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"chart_{symbol}"), InlineKeyboardButton("🔙", callback_data="back")]]))
    else:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def gemini_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    if not gemini_ai.enabled:
        await q.edit_message_text("❌ GEMINI_API_KEY تنظیم نیست", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    await q.edit_message_text("🌟 Gemini analysis...")
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]])); return
    ind = ui.calc(df)
    text = await gemini_ai.generate(f"Full analysis of {symbol} at ${t['last']:,.2f}. Technical, fundamental, price action, 4h/1d/1w outlook in Persian with emojis. Max 400 words.", 600)
    if text:
        await q.edit_message_text(f"{dtm.header()}🌟 *Gemini AI*\n\n{text}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data=f"gem_{symbol}"), InlineKeyboardButton("🔙", callback_data="back")]]))
    else:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    try:
        if d == "back": await q.edit_message_text("🤖 *منوی اصلی*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"{dtm.header()}💰 *قیمت‌ها*\n\n"
            for sym in cfg.symbols[:15]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d.startswith("tf4_"): await tf_handler(update, ctx, d[4:], "4h")
        elif d.startswith("tf1d_"): await tf_handler(update, ctx, d[5:], "1d")
        elif d.startswith("tf1w_"): await tf_handler(update, ctx, d[5:], "1w")
        elif d.startswith("ai_"): await signal_handler(update, ctx, d[3:] if len(d)>3 else "BTC/USDT")
        elif d.startswith("gem_"): await gemini_handler(update, ctx, d[4:] if len(d)>4 else "BTC/USDT")
        elif d.startswith("chart_"): await chart_handler(update, ctx, d[6:] if len(d)>6 else "BTC/USDT")
        elif d == "market":
            top = []; 
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
            m = await groq_ai.market(top)
            if m: await q.edit_message_text(f"{dtm.header()}📰 *بازار*\n\n{m}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="market"), InlineKeyboardButton("🔙", callback_data="back")]]))
            else: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "strat":
            t = exchange_mgr.ticker("BTC/USDT"); df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
            if t and df is not None:
                ind = ui.calc(df); s = await groq_ai.strategy("BTC/USDT", ind, t['last'])
                if s: await q.edit_message_text(f"{dtm.header()}📊 *استراتژی BTC*\n\n{s}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="strat"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "sent":
            t = exchange_mgr.ticker("BTC/USDT")
            if t:
                s = await groq_ai.sentiment("BTC/USDT", t['last'], t.get('percentage',0))
                if s: await q.edit_message_text(f"{dtm.header()}💭 *احساسات*\n\n{s}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="sent"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "fund":
            t = exchange_mgr.ticker("BTC/USDT")
            if t:
                s = await groq_ai.fundamental("BTC/USDT", t['last'], t.get('percentage',0))
                if s: await q.edit_message_text(f"{dtm.header()}📰 *فاندامنتال*\n\n{s}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="fund"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "pa":
            t = exchange_mgr.ticker("BTC/USDT"); df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
            if t and df is not None:
                ind = ui.calc(df); pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                s = await groq_ai.price_action("BTC/USDT", ind, t['last'], pats)
                if s: await q.edit_message_text(f"{dtm.header()}📊 *پرایس اکشن*\n\n{s}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="pa"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "pred":
            t = exchange_mgr.ticker("BTC/USDT"); df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
            if t and df is not None:
                ind = ui.calc(df); s = await groq_ai.prediction("BTC/USDT", ind, t['last'])
                if s: await q.edit_message_text(f"{dtm.header()}🔮 *پیش‌بینی*\n\n{s}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="pred"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "scan":
            if not exchange_mgr.connected: exchange_mgr.connect()
            res = []
            for sym in cfg.symbols:
                t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 100)
                if t and df is not None:
                    ind = ui.calc(df); sig, conf, score = sg.generate(ind, t['last'])
                    res.append({'symbol': sym, 'price': t['last'], 'signal': sig, 'confidence': conf, 'score': score})
            res.sort(key=lambda x: abs(x['score']), reverse=True)
            txt = f"{dtm.header()}🔍 *اسکن بازار*\n\n"
            for i, r in enumerate(res[:12], 1): txt += f"{i}. {'🟢' if 'خرید' in r['signal'] else '🔴' if 'فروش' in r['signal'] else '⚪'} {r['symbol'].replace('/USDT','')}: ${r['price']:,.4f} | {r['signal'][:12]} | {r['confidence']}%\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="scan"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "tech": await q.edit_message_text("📈 *انتخاب ارز:*", parse_mode="Markdown", reply_markup=Menu.tech())
        elif d == "port":
            s = trader.stats()
            await q.edit_message_text(f"{dtm.header()}💰 *پورتفوی*\n💵 ${s['balance']:,.2f}\n📈 PnL: ${s['pnl']:+,.2f}\n📊 پوزیشن: {len(trader.positions)}\n📋 {s['total']} | برد: {s['wins']} ({s['rate']:.0f}%)", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d in ["perf", "hist"]:
            s = trader.stats()
            await q.edit_message_text(f"{dtm.header()}📊 *عملکرد*\n💰 ${s['balance']:,.2f}\n📈 ${s['pnl']:+,.2f}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "auto":
            await q.edit_message_text(f"🤖 *خودکار*\n🎮 دمو: {'✅' if cfg.demo_trading else '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"دمو: {'✅' if cfg.demo_trading else '❌'}", callback_data="td"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "td": cfg.demo_trading = not cfg.demo_trading
        elif d in ["set", "status"]:
            ts = token_mgr.stats()
            await q.edit_message_text(f"{dtm.header()}⚙️ *تنظیمات*\n🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'}\n🧠 Groq: {'✅' if groq_ai.enabled else '❌'}\n🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}\n📊 TPM: {ts['current']}/{ts['max']}\n⏰ سیگنال: هر ۴ ساعت\n📚 آموزش: هر ۱ ساعت", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "edu":
            content = await groq_ai.education()
            await q.edit_message_text(fmt.edu(content), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "EMERGENCY")
            await q.edit_message_text("⏸️ بسته شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "help": await q.edit_message_text("❓ /start", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d in ["patterns", "fear", "whale", "alt", "pred7", "compare", "live", "alerts"]:
            await q.edit_message_text("⚡ در حال توسعه...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        else: await q.answer("⚡")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(10)
    logger.info(f"📢 4-Hour Signal Loop Started")
    
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            
            logger.info(f"🔄 4-Hour Cycle Start at {dtm.now()}")
            
            await app.bot.send_message(cfg.channel_id, 
                f"""
╔══════════════════════════════════════════════════════╗
║   🔄 شروع تحلیل دوره‌ای ۴ ساعته                    ║
╚══════════════════════════════════════════════════════╝

{dtm.header()}

📊 *در حال تحلیل ۷ ارز برتر با:*
🧠 Groq AI + 🌟 Gemini AI
📈 ۲۵+ اندیکاتور | ۷ EMA | فیبوناچی
⏰ تایم‌فریم: ۴h + ۱d + ۱w

لطفاً منتظر بمانید...""", parse_mode="Markdown")
            
            for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"]:
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
                            gemini_text = await gemini_ai.generate(f"Analyze {sym} at ${t['last']:,.2f}. 4h/1d/1w outlook in Persian. Max 250 words.", 400)
                        
                        chart_analysis = None
                        if sym == "BTC/USDT" and CHART_AVAILABLE and gemini_ai.enabled:
                            chart_data = chart_gen.create(df, sym, ind)
                            if chart_data:
                                await app.bot.send_photo(cfg.channel_id, chart_data['bytes'], caption=f"📊 *{sym.replace('/USDT','')}* | ${t['last']:,.4f}")
                                if chart_data.get('base64'):
                                    chart_analysis = await gemini_ai.analyze_chart(chart_data['base64'], sym, t['last'])
                        
                        analysis = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0),
                                   'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                        
                        msg = fmt.signal(analysis, groq_text, gemini_text, chart_analysis, tf_4h, tf_1d, tf_1w)
                        await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                        logger.info(f"📤 Signal: {sym}")
                        await asyncio.sleep(120)
                except Exception as e: logger.error(f"Signal {sym}: {e}")
            
            # Extra analyses
            if groq_ai.enabled:
                try:
                    btc_t = exchange_mgr.ticker("BTC/USDT")
                    btc_df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
                    if btc_t and btc_df is not None:
                        btc_ind = ui.calc(btc_df); btc_pats = [k for k,v in btc_ind.items() if isinstance(v,bool) and v]
                        for func, title in [(groq_ai.strategy, "📊 *استراتژی BTC*"), (groq_ai.sentiment, "💭 *احساسات BTC*"), (groq_ai.fundamental, "📰 *فاندامنتال BTC*"), (groq_ai.price_action, "📊 *پرایس اکشن BTC*")]:
                            result = await func("BTC/USDT", btc_ind if func != groq_ai.sentiment else None, btc_t['last'], btc_t.get('percentage',0) if func == groq_ai.sentiment else None, btc_pats if func == groq_ai.price_action else None)
                            if result:
                                await app.bot.send_message(cfg.channel_id, f"{dtm.header()}{title}\n\n{result}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown")
                                await asyncio.sleep(30)
                except Exception as e: logger.error(f"BTC extra: {e}")
            
            # Market overview
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage',0)})
            market = await groq_ai.market(top)
            if market:
                await app.bot.send_message(cfg.channel_id, f"{dtm.header()}📰 *تحلیل بازار*\n\n{market}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown")
            
            # Position check
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    if t:
                        result = trader.update(sym, t['last'])
                        if result:
                            emoji = "🟢" if result['pnl']>0 else "🔴"
                            await app.bot.send_message(cfg.channel_id, f"{dtm.header()}{emoji} *پوزیشن بسته شد*\n📊 {sym}\n💰 ${result['pnl']:+,.2f}", parse_mode="Markdown")
                except: pass
            
            await app.bot.send_message(cfg.channel_id, 
                f"""
╔══════════════════════════════════════════════════════╗
║   ✅ پایان تحلیل دوره‌ای ۴ ساعته                   ║
╚══════════════════════════════════════════════════════╝

{dtm.header()}

📊 *سیگنال بعدی:* ۴ ساعت دیگر
⏰ *آموزش بعدی:* ۱ ساعت دیگر
🧠 *تحلیل توسط:* Groq AI + Gemini AI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606""", parse_mode="Markdown")
            
            stats = token_mgr.stats()
            logger.info(f"✅ 4H Cycle Done | TPM:{stats['current']}/{stats['max']}")
            
        except Exception as e: logger.error(f"Loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education(app: Application):
    """آموزش هر ۱ ساعت"""
    await asyncio.sleep(30)
    logger.info(f"📚 1-Hour Education Loop Started")
    
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.education()
                if content:
                    msg = fmt.edu(content)
                    await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                    logger.info("📚 Education sent")
        except Exception as e: logger.error(f"Edu: {e}")
        await asyncio.sleep(cfg.education_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    
    exchange_mgr.connect()
    
    # Auto install charts
    if not CHART_AVAILABLE:
        logger.info("📦 Attempting auto-install of chart libraries...")
        auto_install_charts()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_education(app))
    
    logger.info("="*60)
    logger.info("🚀 CRYPTO PULSE v10.0 - GLASS EDITION")
    logger.info(f"🧠 Groq: {'✅' if groq_ai.enabled else '❌'} | 🌟 Gemini: {'✅' if gemini_ai.enabled else '❌'}")
    logger.info(f"📊 Charts: {'✅' if CHART_AVAILABLE else '❌'}")
    logger.info(f"⏰ Signal: Every 4 Hours | 📚 Education: Every 1 Hour")
    logger.info(f"📢 50+ Glass Buttons | 4h/1d/1w Timeframes")
    logger.info("="*60)
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Exception as e: logger.critical(f"❌ {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except: ProcessLock.release()
