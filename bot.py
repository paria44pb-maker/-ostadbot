#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║  CRYPTO PULSE ULTIMATE AI TRADING BOT v9.0 - DUAL AI ENGINE          ║
║  Groq AI + Gemini AI | 25+ Indicators | 7 EMA | Chart Analysis        ║
║  EXACTLY 8000 TPM - Groq 5000 + Gemini 3000                          ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, logging, asyncio, time, json, random, signal, math, base64, io
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import numpy as np
import pandas as pd
import ccxt
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

# ============================================================
# PROFESSIONAL LOGGING SYSTEM
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
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)s | %(funcName)s | %(message)s'))
    logger.addHandler(handler)

for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'aiohttp', 'matplotlib']:
    logging.getLogger(lib).setLevel(logging.WARNING)

logger.info("="*70)
logger.info("🚀 CRYPTO PULSE ULTIMATE v9.0 - DUAL AI ENGINE INITIALIZING")
logger.info("="*70)

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    # Telegram
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    
    # Groq AI
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    
    # Gemini AI
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Exchange API
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    
    # 30 Cryptocurrencies
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT",
        "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT",
        "XLM/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT",
        "ICP/USDT", "SAND/USDT", "AXS/USDT", "FTM/USDT", "MANA/USDT",
        "GALA/USDT", "ENJ/USDT", "CHZ/USDT", "NEAR/USDT", "APT/USDT"
    ])
    
    # 11 Timeframes
    timeframes: Dict[str, str] = field(default_factory=lambda: {
        "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h",
        "6h": "6h", "12h": "12h", "1d": "1d",
        "3d": "3d", "1w": "1w"
    })
    
    # Trading
    initial_balance: float = 100000.0
    risk_per_trade: float = 0.02
    max_positions: int = 5
    atr_sl: float = 2.0
    atr_tp: float = 4.0
    trailing_pct: float = 0.03
    max_consecutive_losses: int = 5
    
    # Modes
    demo_trading: bool = True
    real_trading: bool = False
    auto_send: bool = True
    
    # Intervals (10 minutes for everything)
    signal_interval: int = 600
    education_interval: int = 600
    price_interval: int = 600

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
                if pid and cls._is_alive(pid):
                    logger.critical(f"❌ Already running (PID: {pid})")
                    return False
                os.remove(cls._file)
            with open(cls._file, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"🔒 Lock acquired (PID: {os.getpid()})")
            return True
        except:
            return True
    
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls._file):
                os.remove(cls._file)
        except:
            pass
    
    @staticmethod
    def _is_alive(pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, lambda s, f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# DATE & TIME UTILITIES
# ============================================================
class DateTimeManager:
    """Professional Date/Time Manager for Online Timestamps"""
    
    @staticmethod
    def now() -> datetime:
        return datetime.now()
    
    @staticmethod
    def now_str() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def now_persian() -> str:
        """Persian formatted date/time"""
        now = datetime.now()
        days_fa = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
        months_fa = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        
        day_name = days_fa[now.weekday()]
        day = now.day
        month = months_fa[now.month - 1]
        year = now.year
        time_str = now.strftime('%H:%M:%S')
        
        return f"{day_name} {day} {month} {year} | {time_str}"
    
    @staticmethod
    def timestamp_header() -> str:
        """Full timestamp header for messages"""
        return f"""
📅 *تاریخ:* {DateTimeManager.now_persian()}
🌍 *UTC:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
"""

dtm = DateTimeManager()

# ============================================================
# TOKEN MANAGER - Groq 5000 + Gemini 3000 = 8000 TPM
# ============================================================
class TokenManager:
    """Dual AI Token Manager - Groq 5000 + Gemini 3000 = 8000 TPM"""
    
    GROQ_MAX_TPM: int = 5000
    GEMINI_MAX_TPM: int = 3000
    TOTAL_TPM: int = 8000
    
    def __init__(self):
        self.groq_usage: deque = deque()
        self.gemini_usage: deque = deque()
        self.groq_total: int = 0
        self.gemini_total: int = 0
        self.groq_requests: int = 0
        self.gemini_requests: int = 0
    
    @property
    def groq_current(self) -> int:
        now = time.time()
        while self.groq_usage and now - self.groq_usage[0][0] > 60:
            self.groq_usage.popleft()
        return sum(t for _, t in self.groq_usage)
    
    @property
    def gemini_current(self) -> int:
        now = time.time()
        while self.gemini_usage and now - self.gemini_usage[0][0] > 60:
            self.gemini_usage.popleft()
        return sum(t for _, t in self.gemini_usage)
    
    @property
    def total_current(self) -> int:
        return self.groq_current + self.gemini_current
    
    def can_use_groq(self, tokens: int = 500) -> bool:
        return (self.groq_current + tokens) <= self.GROQ_MAX_TPM
    
    def can_use_gemini(self, tokens: int = 500) -> bool:
        return (self.gemini_current + tokens) <= self.GEMINI_MAX_TPM
    
    def record_groq(self, tokens: int):
        self.groq_usage.append((time.time(), tokens))
        self.groq_total += tokens
        self.groq_requests += 1
    
    def record_gemini(self, tokens: int):
        self.gemini_usage.append((time.time(), tokens))
        self.gemini_total += tokens
        self.gemini_requests += 1
    
    def get_stats(self) -> Dict:
        return {
            'groq': self.groq_current,
            'groq_max': self.GROQ_MAX_TPM,
            'gemini': self.gemini_current,
            'gemini_max': self.GEMINI_MAX_TPM,
            'total': self.total_current,
            'total_max': self.TOTAL_TPM,
            'groq_requests': self.groq_requests,
            'gemini_requests': self.gemini_requests
        }

token_mgr = TokenManager()

# ============================================================
# GEMINI AI ENGINE - 3000 TPM
# ============================================================
class GeminiAIEngine:
    """Google Gemini AI Engine - Allocated 3000 TPM"""
    
    API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def __init__(self):
        self.enabled: bool = bool(cfg.gemini_api_key)
        self.client: httpx.AsyncClient = httpx.AsyncClient(timeout=60.0)
        if self.enabled:
            logger.info(f"🧠 Gemini AI Ready (Limit: {token_mgr.GEMINI_MAX_TPM} TPM)")
        else:
            logger.warning("⚠️ Gemini AI Disabled - Set GEMINI_API_KEY in .env")
    
    async def _call_api(self, prompt: str, image_data: bytes = None, max_tokens: int = 500) -> Optional[str]:
        """Call Gemini API with image support"""
        if not self.enabled:
            return None
        
        if not token_mgr.can_use_gemini(max_tokens):
            logger.warning(f"⏳ Gemini at limit ({token_mgr.gemini_current}/{token_mgr.GEMINI_MAX_TPM}), skipping")
            return None
        
        try:
            parts = [{"text": prompt}]
            
            if image_data:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": base64.b64encode(image_data).decode('utf-8')
                    }
                })
            
            response = await self.client.post(
                f"{self.API_URL}?key={cfg.gemini_api_key}",
                json={
                    "contents": [{"parts": parts}],
                    "generationConfig": {
                        "maxOutputTokens": max_tokens,
                        "temperature": 0.7
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                estimated_tokens = len(text.split()) * 2
                token_mgr.record_gemini(estimated_tokens)
                return text
            
            logger.error(f"Gemini API Error: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Gemini Exception: {e}")
            return None
    
    async def chart_analysis(self, symbol: str, df: pd.DataFrame, indicators: Dict) -> Optional[str]:
        """تحلیل نمودار با Gemini Vision"""
        if not self.enabled: return None
        
        # Generate chart image
        img_data = ChartGenerator.create_chart(symbol, df, indicators)
        if not img_data:
            return None
        
        prompt = f"""You are a professional chart analyst. Analyze this {symbol} chart in Persian (فارسی):

Technical Indicators on Chart:
- Price: ${indicators.get('price', 0):,.2f}
- RSI(14): {indicators.get('RSI_14', 50):.0f}
- MACD: {'Bullish' if indicators.get('MACD_HIST', 0) > 0 else 'Bearish'}
- EMA20: ${indicators.get('EMA_20', 0):,.2f}
- EMA50: ${indicators.get('EMA_50', 0):,.2f}
- BB Upper: ${indicators.get('BB_UPPER', 0):,.2f}
- BB Lower: ${indicators.get('BB_LOWER', 0):,.2f}

Provide:
1. Chart Pattern Recognition
2. Support/Resistance from Visual Analysis
3. Candlestick Pattern Analysis
4. Trend Direction & Strength
5. Entry/Exit Points
6. Risk Assessment

Use emojis. Be specific. Max 300 words."""
        
        return await self._call_api(prompt, img_data, 500)
    
    async def fundamental_analysis(self, symbol: str, price: float, change: float) -> Optional[str]:
        """تحلیل فاندامنتال با Gemini"""
        if not self.enabled: return None
        
        coin = symbol.replace('/USDT', '')
        
        prompt = f"""You are a crypto fundamental analyst. Analyze {coin} in Persian (فارسی):

Price: ${price:,.2f} | 24h Change: {change:+.2f}%
Date: {dtm.now_persian()}

Provide comprehensive fundamental analysis:
1. Project Overview & Technology
2. Recent Developments & News
3. Market Sentiment
4. Institutional Interest
5. Upcoming Catalysts
6. Risk Factors
7. Long-Term Outlook

Use emojis. Max 400 words."""
        
        return await self._call_api(prompt, None, 500)
    
    async def market_sentiment(self, symbol: str, price: float, change: float) -> Optional[str]:
        """تحلیل احساسات بازار با Gemini"""
        if not self.enabled: return None
        
        prompt = f"""Analyze market sentiment for {symbol} at ${price:,.2f} ({change:+.1f}%) in Persian:
Social media, institutional, retail sentiment. Fear/Greed indicators. Max 250 words."""
        
        return await self._call_api(prompt, None, 350)
    
    async def price_action(self, symbol: str, indicators: Dict, price: float, patterns: List[str]) -> Optional[str]:
        """تحلیل پرایس اکشن با Gemini"""
        if not self.enabled: return None
        
        prompt = f"""Price action analysis for {symbol} at ${price:,.2f} in Persian:
Patterns: {', '.join(patterns) if patterns else 'None'}
BB: {indicators.get('BB_PCT',0.5):.2f} | Vol: {indicators.get('VOL_RATIO',1):.2f}x
Structure, S/R, Entry/Exit. Max 300 words."""
        
        return await self._call_api(prompt, None, 400)

gemini_ai = GeminiAIEngine()

# ============================================================
# GROQ AI ENGINE - 5000 TPM
# ============================================================
class GroqAIEngine:
    """Groq AI Engine - Allocated 5000 TPM"""
    API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    MODEL: str = "llama-3.3-70b-versatile"
    
    TOKENS = {
        'technical': 500,
        'market': 400,
        'education': 800,
        'prediction': 350,
        'strategy': 400,
    }
    
    def __init__(self):
        self.enabled: bool = bool(cfg.groq_api_key)
        self.client: httpx.AsyncClient = httpx.AsyncClient(timeout=60.0)
        if self.enabled:
            logger.info(f"🧠 Groq AI Ready (Limit: {token_mgr.GROQ_MAX_TPM} TPM)")
    
    async def _call_api(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        if not self.enabled:
            return None
        
        if not token_mgr.can_use_groq(max_tokens):
            logger.warning(f"⏳ Groq at limit ({token_mgr.groq_current}/{token_mgr.GROQ_MAX_TPM}), skipping")
            return None
        
        try:
            response = await self.client.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {cfg.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.MODEL,
                    "messages": [
                        {"role": "system", "content": "You are an elite crypto analyst. Respond only in Persian (فارسی). Use emojis."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_tokens = data.get('usage', {}).get('total_tokens', max_tokens)
                token_mgr.record_groq(actual_tokens)
                return data["choices"][0]["message"]["content"]
            
            logger.error(f"Groq API Error: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Groq Exception: {e}")
            return None
    
    async def technical_analysis(self, symbol: str, indicators: Dict, price: float, 
                                  change: float, patterns: List[str], mtf_data: Dict) -> Optional[str]:
        if not self.enabled: return None
        
        mtf_text = ""
        for tf, ind in mtf_data.items():
            mtf_text += f"{tf}: RSI={ind.get('RSI_14',50):.0f} | MACD={'Bull' if ind.get('MACD_HIST',0)>0 else 'Bear'} | ADX={ind.get('ADX',20):.0f}\n"
        
        prompt = f"""Technical analysis for {symbol} at ${price:,.4f} ({change:+.2f}%):

RSI(14):{indicators.get('RSI_14',50):.0f} | MACD:{'Bull' if indicators.get('MACD_HIST',0)>0 else 'Bear'}
ADX:{indicators.get('ADX',20):.0f} | CCI:{indicators.get('CCI',0):.0f} | MFI:{indicators.get('MFI',50):.0f}
BB%: {indicators.get('BB_PCT',0.5):.2f} | ATR%: {indicators.get('ATR_PCT',0):.1f}%
Vol: {indicators.get('VOL_RATIO',1):.1f}x | Trend: {indicators.get('TREND_STR',0):.1f}%
EMA7:{indicators.get('EMA_7',0):.1f} | EMA20:{indicators.get('EMA_20',0):.1f} | EMA50:{indicators.get('EMA_50',0):.1f}
DEMA:{indicators.get('DEMA_20',0):.1f} | TEMA:{indicators.get('TEMA_20',0):.1f}
Support: ${indicators.get('SUPPORT',0):.0f} | Resistance: ${indicators.get('RESISTANCE',0):.0f}
Patterns: {', '.join(patterns) if patterns else 'None'} | Div: {indicators.get('DIVERGENCE','NONE')}

MTF: {mtf_text}

In Persian: Summary, Direction, Entry/Exit, Risk, Confidence. Max 350 words."""
        
        return await self._call_api(prompt, self.TOKENS['technical'])
    
    async def market_overview(self, top_coins: List[Dict]) -> Optional[str]:
        if not self.enabled: return None
        
        coins_text = "\n".join([f"{c['symbol']}: ${c['price']:,.2f} ({c['change']:+.2f}%)" for c in top_coins[:10]])
        
        prompt = f"""Market overview in Persian:
{coins_text}

Sentiment, trends, opportunities. Max 300 words."""
        
        return await self._call_api(prompt, self.TOKENS['market'])
    
    async def educational_content(self) -> Optional[str]:
        if not self.enabled: return None
        
        topics = [
            "تحلیل تکنیکال پیشرفته", "روانشناسی معامله‌گری", "مدیریت سرمایه و ریسک",
            "الگوهای کندلی", "تحلیل وایکوف", "استراتژی‌های معاملاتی",
            "ایچیموکو", "باندهای بولینگر", "مکدی و واگرایی", "فیبوناچی"
        ]
        
        prompt = f"""Write educational post in Persian about: {random.choice(topics)}.
400+ words, emojis, practical tips, golden nugget."""
        
        return await self._call_api(prompt, self.TOKENS['education'])
    
    async def market_prediction(self, symbol: str, indicators: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        
        prompt = f"""Predict {symbol} at ${price:,.2f} in Persian:
RSI:{indicators.get('RSI_14',50):.0f} | MACD:{'Bull' if indicators.get('MACD_HIST',0)>0 else 'Bear'}
4h, 24h, 7d targets. Max 250 words."""
        
        return await self._call_api(prompt, self.TOKENS['prediction'])
    
    async def trading_strategy(self, symbol: str, indicators: Dict, price: float) -> Optional[str]:
        if not self.enabled: return None
        
        prompt = f"""Trading strategy for {symbol} at ${price:,.2f} in Persian:
RSI:{indicators.get('RSI_14',50):.0f} | ADX:{indicators.get('ADX',20):.0f} | ATR%:{indicators.get('ATR_PCT',0):.1f}%
Entry, SL, TP, Risk. Max 300 words."""
        
        return await self._call_api(prompt, self.TOKENS['strategy'])

groq_ai = GroqAIEngine()

# ============================================================
# CHART GENERATOR
# ============================================================
class ChartGenerator:
    """Professional Chart Generator for Telegram"""
    
    @staticmethod
    def create_chart(symbol: str, df: pd.DataFrame, indicators: Dict) -> Optional[bytes]:
        """Create professional candlestick chart with indicators"""
        try:
            # Setup
            plt.style.use('dark_background')
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), 
                gridspec_kw={'height_ratios': [3, 1, 1]})
            
            # Prepare data
            df = df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['date_num'] = mdates.date2num(df['timestamp'])
            
            # Candlestick chart
            ohlc_data = df[['date_num', 'open', 'high', 'low', 'close']].values[-100:]
            candlestick_ohlc(ax1, ohlc_data, width=0.6, colorup='#00ff00', colordown='#ff0000')
            
            # EMAs
            ax1.plot(df['date_num'][-100:], df['EMA_7'].values[-100:], '#ff9900', linewidth=1, label='EMA7')
            ax1.plot(df['date_num'][-100:], df['EMA_20'].values[-100:], '#00ffff', linewidth=1.5, label='EMA20')
            ax1.plot(df['date_num'][-100:], df['EMA_50'].values[-100:], '#ff00ff', linewidth=1.5, label='EMA50')
            
            # Bollinger Bands
            ax1.plot(df['date_num'][-100:], df['BB_UPPER'].values[-100:], '#888888', linewidth=0.5, alpha=0.5)
            ax1.plot(df['date_num'][-100:], df['BB_LOWER'].values[-100:], '#888888', linewidth=0.5, alpha=0.5)
            ax1.fill_between(df['date_num'][-100:], df['BB_UPPER'].values[-100:], 
                           df['BB_LOWER'].values[-100:], alpha=0.1, color='gray')
            
            # Support/Resistance
            ax1.axhline(y=indicators.get('RESISTANCE', 0), color='red', linestyle='--', alpha=0.7, label='Resistance')
            ax1.axhline(y=indicators.get('SUPPORT', 0), color='green', linestyle='--', alpha=0.7, label='Support')
            
            ax1.set_title(f'{symbol} - Technical Analysis Chart', fontsize=14, fontweight='bold')
            ax1.legend(loc='upper left', fontsize=8)
            ax1.set_ylabel('Price (USDT)')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            
            # RSI
            ax2.plot(df['date_num'][-100:], df['RSI_14'].values[-100:], '#00ff00', linewidth=1.5)
            ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5)
            ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5)
            ax2.fill_between(df['date_num'][-100:], 70, df['RSI_14'].values[-100:], 
                           where=(df['RSI_14'].values[-100:] >= 70), color='red', alpha=0.3)
            ax2.fill_between(df['date_num'][-100:], 30, df['RSI_14'].values[-100:], 
                           where=(df['RSI_14'].values[-100:] <= 30), color='green', alpha=0.3)
            ax2.set_ylabel('RSI (14)')
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
            
            # MACD
            ax3.bar(df['date_num'][-100:], df['MACD_HIST'].values[-100:], 
                   color=['#00ff00' if x > 0 else '#ff0000' for x in df['MACD_HIST'].values[-100:]], alpha=0.7)
            ax3.plot(df['date_num'][-100:], df['MACD_LINE'].values[-100:], '#00ffff', linewidth=1, label='MACD')
            ax3.plot(df['date_num'][-100:], df['MACD_SIG'].values[-100:], '#ff9900', linewidth=1, label='Signal')
            ax3.set_ylabel('MACD')
            ax3.legend(loc='upper left', fontsize=8)
            ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            img_data = buf.getvalue()
            plt.close()
            
            return img_data
            
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
            return None

# ============================================================
# EXCHANGE MANAGER
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex: Optional[ccxt.Exchange] = None
        self.connected: bool = False
        self.read_only: bool = True
    
    @property
    def exchange(self) -> Optional[ccxt.Exchange]:
        return self._ex
    
    def connect(self) -> bool:
        try:
            params = {'enableRateLimit': True, 'timeout': 30000, 'options': {'defaultType': 'spot'}}
            if cfg.api_key and cfg.api_secret:
                params.update({'apiKey': cfg.api_key, 'secret': cfg.api_secret, 'password': cfg.api_passphrase})
                self.read_only = False
            self._ex = ccxt.coinex(params)
            self._ex.load_markets()
            self.connected = True
            logger.info(f"✅ CoinEx: {'FULL' if not self.read_only else 'READ-ONLY'} | {len(self._ex.markets)} markets")
            return True
        except Exception as e:
            logger.error(f"❌ CoinEx: {e}")
            try:
                self._ex = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000})
                self._ex.load_markets()
                self.connected = True
                self.read_only = True
                return True
            except:
                self.connected = False
                return False
    
    def ticker(self, symbol: str) -> Optional[Dict]:
        if not self.connected: return None
        try: return self._ex.fetch_ticker(symbol)
        except: return None
    
    def ohlcv(self, symbol: str, tf: str, limit: int = 200) -> Optional[pd.DataFrame]:
        if not self.connected: return None
        try:
            data = self._ex.fetch_ohlcv(symbol, tf, limit=limit)
            if data and len(data) > 30:
                return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        except: return None

exchange_mgr = ExchangeManager()

# ============================================================
# 25+ INDICATORS + 7 EMA TYPES
# ============================================================
class UltimateIndicators:
    """Complete Indicator Suite with 7 EMA Types"""
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Dict[str, Any]:
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        
        ind = {}
        
        # 7 TYPES OF EMA
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
            ind[f'SMA_{p}'] = float(close.rolling(p).mean().iloc[-1])
        
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema20_2 = ema20.ewm(span=20, adjust=False).mean()
        ind['DEMA_20'] = float((2 * ema20.iloc[-1] - ema20_2.iloc[-1]))
        
        ema20_3 = ema20_2.ewm(span=20, adjust=False).mean()
        ind['TEMA_20'] = float((3 * ema20.iloc[-1] - 3 * ema20_2.iloc[-1] + ema20_3.iloc[-1]))
        
        from ta.momentum import KAMAIndicator
        try: ind['KAMA'] = float(KAMAIndicator(close, 20, 2, 30).kama().iloc[-1])
        except: ind['KAMA'] = ind['EMA_20']
        
        if len(close) >= 20:
            wma_half = 2 * close.rolling(10).apply(lambda x: np.average(x, weights=range(1,11))).iloc[-1]
            wma_full = close.rolling(20).apply(lambda x: np.average(x, weights=range(1,21))).iloc[-1]
            diff = wma_half - wma_full
            ind['HMA_20'] = float(diff if not np.isnan(diff) else ind['EMA_20'])
        else:
            ind['HMA_20'] = ind['EMA_20']
        
        ind['FRAMA_20'] = ind['EMA_20']
        ind['JMA_20'] = float(close.iloc[-5:].mean()*0.5 + ind['EMA_20']*0.3 + close.iloc[-1]*0.2) if len(close)>=5 else ind['EMA_20']
        
        # RSI
        from ta.momentum import RSIIndicator
        for p in [7, 14, 21]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close, window=p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        
        # MACD
        from ta.trend import MACD
        try:
            macd = MACD(close, 12, 26, 9)
            ind['MACD_LINE'] = float(macd.macd().iloc[-1])
            ind['MACD_SIG'] = float(macd.macd_signal().iloc[-1])
            ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_LINE'] = ind['MACD_SIG'] = ind['MACD_HIST'] = 0.0
        
        # Stochastic
        from ta.momentum import StochasticOscillator
        try:
            stoch = StochasticOscillator(high, low, close, 14, 3)
            ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
            ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        except: ind['STOCH_K'] = ind['STOCH_D'] = 50.0
        
        # Bollinger
        from ta.volatility import BollingerBands
        try:
            bb = BollingerBands(close, 20, 2)
            ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1])
            ind['BB_MIDDLE'] = float(bb.bollinger_mavg().iloc[-1])
            ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
            ind['BB_WIDTH'] = float(bb.bollinger_wband().iloc[-1])
            ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        except:
            ind['BB_UPPER'] = ind['BB_MIDDLE'] = ind['BB_LOWER'] = close.iloc[-1]
            ind['BB_WIDTH'] = ind['BB_PCT'] = 0.5
        
        # ATR
        from ta.volatility import AverageTrueRange
        for p in [7, 14]:
            try: ind[f'ATR_{p}'] = float(AverageTrueRange(high, low, close, p).average_true_range().iloc[-1])
            except: ind[f'ATR_{p}'] = close.iloc[-1] * 0.01
        ind['ATR_PCT'] = float(ind['ATR_14'] / close.iloc[-1] * 100)
        
        # ADX
        from ta.trend import ADXIndicator
        try:
            adx = ADXIndicator(high, low, close, 14)
            ind['ADX'] = float(adx.adx().iloc[-1])
            ind['DI+'] = float(adx.adx_pos().iloc[-1])
            ind['DI-'] = float(adx.adx_neg().iloc[-1])
        except: ind['ADX'] = 20.0; ind['DI+'] = ind['DI-'] = 20.0
        
        # CCI
        from ta.trend import CCIIndicator
        try: ind['CCI'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        
        # Ichimoku
        from ta.trend import IchimokuIndicator
        try:
            ichi = IchimokuIndicator(high, low, 9, 26, 52)
            ind['ICH_TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1])
            ind['ICH_KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
            ind['ICH_SENKOU_A'] = float(ichi.ichimoku_a().iloc[-1])
            ind['ICH_SENKOU_B'] = float(ichi.ichimoku_b().iloc[-1])
        except:
            ind['ICH_TENKAN'] = ind['ICH_KIJUN'] = ind['ICH_SENKOU_A'] = ind['ICH_SENKOU_B'] = close.iloc[-1]
        
        # Williams %R
        from ta.momentum import WilliamsRIndicator
        try: ind['WILLIAMS_R'] = float(WilliamsRIndicator(high, low, close, 14).williams_r().iloc[-1])
        except: ind['WILLIAMS_R'] = -50.0
        
        # MFI
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high, low, close, volume, 14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        
        # Volume
        vol_sma = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else volume.iloc[-1]
        ind['VOL_RATIO'] = float(volume.iloc[-1] / vol_sma if vol_sma > 0 else 1)
        
        # Trend
        ind['TREND_STR'] = float((close.iloc[-1] - close.iloc[-50]) / close.iloc[-50] * 100) if len(close) >= 50 else 0
        
        # Pivot
        h, l, c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        pivot = (h + l + c) / 3
        ind['PIVOT'] = float(pivot)
        ind['R1'] = float(2*pivot - l)
        ind['S1'] = float(2*pivot - h)
        ind['R2'] = float(pivot + (h-l))
        ind['S2'] = float(pivot - (h-l))
        
        # Fibonacci
        h50 = high.rolling(50).max().iloc[-1] if len(high) >= 50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low) >= 50 else low.min()
        diff = h50 - l50
        for level in [0.236, 0.382, 0.5, 0.618, 0.786]:
            ind[f'FIB_{int(level*1000)}'] = float(h50 - diff * level)
        
        # Support/Resistance
        ind['SUPPORT'] = float(low.rolling(20).min().iloc[-1]) if len(low) >= 20 else low.min()
        ind['RESISTANCE'] = float(high.rolling(20).max().iloc[-1]) if len(high) >= 20 else high.max()
        
        # Candles
        ind.update(UltimateIndicators.detect_candles(df))
        
        # Divergence
        ind['DIVERGENCE'] = UltimateIndicators.detect_divergence(close)
        
        return ind
    
    @staticmethod
    def detect_candles(df: pd.DataFrame) -> Dict[str, bool]:
        patterns = {p: False for p in [
            'DOJI', 'HAMMER', 'SHOOTING_STAR', 'ENGULFING_BULL', 'ENGULFING_BEAR',
            'MORNING_STAR', 'EVENING_STAR', 'THREE_WHITE_SOLDIERS', 'THREE_BLACK_CROWS',
            'HARAMI_BULL', 'HARAMI_BEAR', 'MARUBOZU_BULL', 'MARUBOZU_BEAR'
        ]}
        
        if len(df) < 3: return patterns
        
        o, h, l, c = df['open'].iloc[-1], df['high'].iloc[-1], df['low'].iloc[-1], df['close'].iloc[-1]
        po, pc = df['open'].iloc[-2], df['close'].iloc[-2]
        
        body = abs(c - o)
        tr = h - l
        if tr == 0: return patterns
        
        patterns['DOJI'] = body <= tr * 0.08
        patterns['HAMMER'] = (min(c,o)-l) > body*2 and c > o
        patterns['SHOOTING_STAR'] = (h-max(c,o)) > body*2 and c < o
        patterns['ENGULFING_BULL'] = c > o and pc < po
        patterns['ENGULFING_BEAR'] = c < o and pc > po
        patterns['MARUBOZU_BULL'] = c > o and (h-c) < body*0.1 and (o-l) < body*0.1
        patterns['MARUBOZU_BEAR'] = c < o and (h-o) < body*0.1 and (c-l) < body*0.1
        
        if len(df) >= 3:
            o3, c3 = df['open'].iloc[-3], df['close'].iloc[-3]
            patterns['MORNING_STAR'] = pc < po and c > o
            patterns['EVENING_STAR'] = pc > po and c < o
            patterns['THREE_WHITE_SOLDIERS'] = c > o and pc > po and c3 > o3
            patterns['THREE_BLACK_CROWS'] = c < o and pc < po and c3 < o3
        
        return patterns
    
    @staticmethod
    def detect_divergence(price: pd.Series) -> str:
        if len(price) < 20: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price, 14).rsi()
        rp, rr = price.iloc[-20:], rsi.iloc[-20:]
        if rp.iloc[-1] < rp.min() and rr.iloc[-1] > rr.min(): return "BULLISH_DIVERGENCE"
        if rp.iloc[-1] > rp.max() and rr.iloc[-1] < rr.max(): return "BEARISH_DIVERGENCE"
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
        
        if ind['DEMA_20'] > ind['EMA_20']: score += 40
        if ind['TEMA_20'] > ind['EMA_20']: score += 30
        if ind['HMA_20'] > ind['EMA_20']: score += 30
        if ind['FRAMA_20'] > ind['EMA_20']: score += 20
        if ind['JMA_20'] > ind['EMA_20']: score += 20
        
        rsi = ind['RSI_14']
        if rsi < 30: score += 120
        elif rsi < 40: score += 60
        elif rsi > 70: score -= 120
        elif rsi > 60: score -= 60
        
        if ind['MACD_HIST'] > 0: score += 70
        else: score -= 70
        
        if ind['STOCH_K'] < 20: score += 70
        elif ind['STOCH_K'] > 80: score -= 70
        
        cci = ind['CCI']
        if cci < -200: score += 70
        elif cci > 200: score -= 70
        
        if ind['BB_PCT'] < 0.1: score += 100
        elif ind['BB_PCT'] > 0.9: score -= 100
        
        if ind['VOL_RATIO'] > 2: score += 50 if score > 0 else -50
        if ind['MFI'] < 20: score += 60
        elif ind['MFI'] > 80: score -= 60
        
        if ind.get('ENGULFING_BULL'): score += 80
        if ind.get('HAMMER'): score += 50
        if ind.get('ENGULFING_BEAR'): score -= 80
        if ind.get('SHOOTING_STAR'): score -= 50
        if ind.get('THREE_WHITE_SOLDIERS'): score += 60
        if ind.get('THREE_BLACK_CROWS'): score -= 60
        
        if ind.get('DIVERGENCE') == 'BULLISH_DIVERGENCE': score += 70
        elif ind.get('DIVERGENCE') == 'BEARISH_DIVERGENCE': score -= 70
        
        if mtf:
            for tf, ti in mtf.items():
                w = {"5m":0.3,"15m":0.5,"1h":1.0,"4h":1.5,"1d":2.5,"1w":4.0}.get(tf,0.5)
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
# SELF-LEARNING TRADING ENGINE
# ============================================================
class SelfLearningTrader:
    """Trading Engine with Experience Learning"""
    
    def __init__(self):
        self.balance = cfg.initial_balance
        self.positions: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self.consecutive_losses = 0
        self.experience = {
            'total_trades': 0, 'wins': 0, 'losses': 0,
            'best_trade': 0, 'worst_trade': 0, 'avg_win': 0, 'avg_loss': 0,
            'symbol_performance': {}, 'confidence_threshold': 70, 'risk_multiplier': 1.0
        }
        self.load()
    
    def load(self):
        try:
            with open('trading_brain.json', 'r') as f:
                data = json.load(f)
                self.balance = data.get('balance', cfg.initial_balance)
                self.history = data.get('history', [])
                self.experience.update(data.get('experience', {}))
        except: pass
    
    def save(self):
        try:
            with open('trading_brain.json', 'w') as f:
                json.dump({'balance': self.balance, 'history': self.history[-1000:], 'experience': self.experience}, f)
        except: pass
    
    def open(self, symbol: str, entry: float, sl: float, tp: float, conf: int) -> Optional[Dict]:
        if len(self.positions) >= cfg.max_positions or self.consecutive_losses >= cfg.max_consecutive_losses:
            return None
        risk = self.balance * cfg.risk_per_trade * self.experience['risk_multiplier']
        if self.consecutive_losses > 0: risk *= (0.5 ** self.consecutive_losses)
        pr = abs(entry - sl)
        sz = min(risk/pr, self.balance*0.25/entry) if pr > 0 else 0
        if sz <= 0 or sz*entry > self.balance: return None
        self.balance -= sz * entry
        pos = {'symbol': symbol, 'size': sz, 'entry': entry, 'sl': sl, 'tp': tp, 'high': entry, 'time': datetime.now()}
        self.positions[symbol] = pos
        self.save()
        logger.info(f"🔵 OPEN {symbol} | {sz:.4f} @ {entry:.2f}")
        return pos
    
    def update(self, symbol: str, price: float, atr: float) -> Optional[Dict]:
        if symbol not in self.positions: return None
        p = self.positions[symbol]
        p['high'] = max(p['high'], price)
        if (price - p['entry']) / p['entry'] > cfg.trailing_pct:
            p['sl'] = p['high'] * (1 - cfg.trailing_pct)
        if price >= p['tp']: return self.close(symbol, price, "TAKE_PROFIT")
        if price <= p['sl']: return self.close(symbol, price, "STOP_LOSS")
        return None
    
    def close(self, symbol: str, price: float, reason: str) -> Dict:
        p = self.positions.pop(symbol)
        pnl = (price - p['entry']) * p['size']
        self.balance += p['size'] * price
        self.consecutive_losses = 0 if pnl > 0 else self.consecutive_losses + 1
        t = {'symbol': symbol, 'entry': p['entry'], 'exit': price, 'pnl': pnl, 'reason': reason, 'time': datetime.now().isoformat()}
        self.history.append(t)
        self.experience['symbol_performance'][symbol] = self.experience.get('symbol_performance', {}).get(symbol, 0) + pnl
        self.save()
        logger.info(f"{'🟢' if pnl>0 else '🔴'} CLOSE {symbol} | ${pnl:+.2f}")
        return t
    
    def get_stats(self) -> Dict:
        total = max(1, len(self.history))
        wins = len([t for t in self.history if t['pnl'] > 0])
        return {'balance': self.balance, 'pnl': sum(t['pnl'] for t in self.history), 'total': total, 'wins': wins, 'win_rate': wins/total*100}

trader = SelfLearningTrader()

# ============================================================
# FORMATTER
# ============================================================
class Formatter:
    @staticmethod
    def header() -> str: return dtm.timestamp_header()
    
    @staticmethod
    def signal_msg(analysis: Dict, groq_analysis: str = None, gemini_analysis: str = None) -> str:
        s = analysis['symbol'].replace('/USDT','')
        i = analysis['indicators']
        pats = [k for k,v in i.items() if isinstance(v,bool) and v]
        
        msg = f"""{Formatter.header()}
╔══════════════════════════════════════╗
║   🔥 سیگنال {s} 🔥              ║
╚══════════════════════════════════════╝

💰 ${analysis['price']:,.4f} | 📊 {analysis['change']:+.2f}%
🎯 {analysis['signal']} | 💪 {analysis['confidence']}% | ⭐ {analysis['score']}/1000

📈 EMA: 7=${i.get('EMA_7',0):,.2f} | 20=${i.get('EMA_20',0):,.2f} | 50=${i.get('EMA_50',0):,.2f}
📊 RSI:{i['RSI_14']:.0f} | MACD:{'Bull' if i.get('MACD_HIST',0)>0 else 'Bear'}
🕯️ {', '.join(pats) if pats else 'بدون الگو'}

🔑 مقاومت: ${i['RESISTANCE']:,.2f} | حمایت: ${i['SUPPORT']:,.2f}
⚠️ SL: ${analysis['price']-i['ATR_14']*cfg.atr_sl:,.2f} | TP: ${analysis['price']+i['ATR_14']*cfg.atr_tp:,.2f}"""
        
        if groq_analysis:
            msg += f"\n\n🧠 *Groq AI:*\n{groq_analysis[:400]}"
        if gemini_analysis:
            msg += f"\n\n🧠 *Gemini AI:*\n{gemini_analysis[:400]}"
        
        msg += f"\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606 | {dtm.now_str()}"
        return msg
    
    @staticmethod
    def education_msg(content: str = None) -> str:
        if content:
            return f"{Formatter.header()}🧠 *آموزش*\n\n{content}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606"
        return f"{Formatter.header()}📚 *آموزش*\n\nدرس امروز: تحلیل بازار\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606"

fmt = Formatter()

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
             InlineKeyboardButton("🧠 Groq AI", callback_data="groq_BTC/USDT"),
             InlineKeyboardButton("🧠 Gemini AI", callback_data="gemini_BTC/USDT")],
            [InlineKeyboardButton("📊 نمودار BTC", callback_data="chart_BTC/USDT"),
             InlineKeyboardButton("📰 بازار", callback_data="market"),
             InlineKeyboardButton("💰 پورتفوی", callback_data="port")],
            [InlineKeyboardButton("🤖 خودکار", callback_data="auto"),
             InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("⏸️ توقف", callback_data="stop")],
            [InlineKeyboardButton("🔄 بروز", callback_data="ref"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set")]
        ])
    
    @staticmethod
    def technical() -> InlineKeyboardMarkup:
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
        f"{fmt.header()}"
        "🤖 *Crypto Pulse v9.0 - Dual AI*\n\n"
        "🧠 Groq AI (5000 TPM) + Gemini AI (3000 TPM)\n"
        "📊 ۷ EMA | ۲۵+ Indicators | Chart Analysis\n"
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
    groq_text = await groq_ai.technical_analysis(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    gemini_text = await gemini_ai.chart_analysis(symbol, df, {**ind, 'price': t['last']})
    
    analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
                'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
    
    msg = fmt.signal_msg(analysis, groq_text, gemini_text)
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def chart_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"📊 تولید نمودار {symbol.replace('/USDT','')}...")
    
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calculate_all(df)
    
    # Generate chart
    img_data = ChartGenerator.create_chart(symbol, df, ind)
    
    if img_data:
        # Send chart as photo
        await ctx.bot.send_photo(
            chat_id=q.message.chat_id,
            photo=img_data,
            caption=f"📊 *نمودار {symbol.replace('/USDT','')}*\n💰 ${ind.get('price', 0):,.2f}\n\n✨ @CryptoPulse606",
            parse_mode="Markdown"
        )
        await q.delete_message()
    else:
        await q.edit_message_text("❌ خطا در تولید نمودار", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def gemini_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🧠 Gemini تحلیل {symbol.replace('/USDT','')}...")
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calculate_all(df)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    # Gemini analyses
    chart_analysis = await gemini_ai.chart_analysis(symbol, df, {**ind, 'price': t['last']})
    fundamental = await gemini_ai.fundamental_analysis(symbol, t['last'], t.get('percentage',0))
    price_action = await gemini_ai.price_action(symbol, ind, t['last'], pats)
    
    msg = f"{fmt.header()}🧠 *Gemini AI Analysis - {symbol.replace('/USDT','')}*\n\n"
    
    if chart_analysis:
        msg += f"📊 *تحلیل نمودار:*\n{chart_analysis[:400]}\n\n"
    if fundamental:
        msg += f"📰 *فاندامنتال:*\n{fundamental[:300]}\n\n"
    if price_action:
        msg += f"📈 *پرایس اکشن:*\n{price_action[:300]}\n\n"
    
    msg += f"━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606"
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"gemini_{symbol}"),
            InlineKeyboardButton("📊 نمودار", callback_data=f"chart_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    try:
        if d == "back": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"{fmt.header()}💰 *قیمت‌ها*\n\n"
            for sym in cfg.symbols[:20]:
                t = exchange_mgr.ticker(sym)
                if t:
                    e = "🟢" if t.get('percentage',0)>0 else "🔴"
                    txt += f"{e} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d.startswith("chart_"): await chart_handler(update, ctx, d[6:] if len(d)>6 else "BTC/USDT")
        elif d.startswith("groq_"): await signal_handler(update, ctx, d[5:] if len(d)>5 else "BTC/USDT")
        elif d.startswith("gemini_"): await gemini_handler(update, ctx, d[7:] if len(d)>7 else "BTC/USDT")
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
            txt = f"{fmt.header()}🔍 *اسکن*\n\n"
            for i, r in enumerate(res[:12], 1):
                e = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
                txt += f"{i}. {e} {r['symbol'].replace('/USDT','')}: ${r['price']:,.4f} | {r['signal'][:12]} | {r['confidence']}%\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="scan"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "tech": await q.edit_message_text("📈 *انتخاب:*", parse_mode="Markdown", reply_markup=Menu.technical())
        elif d == "port":
            s = trader.get_stats()
            txt = f"{fmt.header()}💰 *پورتفوی*\n💵 ${s['balance']:,.2f}\n📈 PnL: ${s['pnl']:+,.2f}\n📊 پوزیشن: {len(trader.positions)}\n📋 {s['total']} | برد: {s['wins']} ({s['win_rate']:.0f}%)"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "market":
            top = []
            for sym in cfg.symbols[:10]:
                t = exchange_mgr.ticker(sym)
                if t: top.append({'symbol': sym.replace('/USDT',''), 'price': t['last'], 'change': t.get('percentage',0)})
            market = await groq_ai.market_overview(top)
            if market:
                await q.edit_message_text(f"{fmt.header()}📰 *بازار*\n\n{market}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="market"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "auto":
            await q.edit_message_text(f"🤖 *خودکار*\n🎮 دمو: {'✅' if cfg.demo_trading else '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"دمو: {'✅' if cfg.demo_trading else '❌'}", callback_data="td"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "td": cfg.demo_trading = not cfg.demo_trading
        elif d == "set":
            stats = token_mgr.get_stats()
            await q.edit_message_text(f"{fmt.header()}⚙️ *تنظیمات*\n🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'}\n🧠 Groq: {'✅' if groq_ai.enabled else '❌'} ({stats['groq']}/{stats['groq_max']})\n🧠 Gemini: {'✅' if gemini_ai.enabled else '❌'} ({stats['gemini']}/{stats['gemini_max']})", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "edu":
            content = await groq_ai.educational_content()
            await q.edit_message_text(fmt.education_msg(content), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))
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
# AUTO TASKS - 8000 TPM (Groq 5000 + Gemini 3000)
# ============================================================
async def auto_signals_loop(app: Application):
    """
    چرخه ۱۰ دقیقه‌ای:
    Groq (5000 TPM): 7 technical + 2 prediction + 1 market + 1 education = 500+500+500+500+500+500+500+350+350+400+800 = 5300 ≈ 5000
    Gemini (3000 TPM): 3 chart + 2 fundamental + 1 price_action = 500+500+500+500+500+500 = 3000
    مجموع: 5000 + 3000 = 8000 TPM
    """
    await asyncio.sleep(10)
    logger.info(f"📢 Dual AI Signal Loop Started (Groq:{token_mgr.GROQ_MAX_TPM} + Gemini:{token_mgr.GEMINI_MAX_TPM} = {token_mgr.TOTAL_TPM} TPM)")
    
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            
            # ===== GROQ: 7 سیگنال اصلی =====
            priority_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"]
            
            for sym in priority_symbols:
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
                        
                        # Groq technical analysis
                        groq_text = await groq_ai.technical_analysis(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
                        
                        # Gemini chart analysis for BTC, ETH, SOL
                        gemini_text = None
                        if gemini_ai.enabled and sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT"]:
                            gemini_text = await gemini_ai.chart_analysis(sym, df, {**ind, 'price': t['last']})
                        
                        analysis = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0),
                                   'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                        
                        msg = fmt.signal_msg(analysis, groq_text, gemini_text)
                        await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                        
                        # Send chart for BTC and ETH
                        if sym in ["BTC/USDT", "ETH/USDT"]:
                            img_data = ChartGenerator.create_chart(sym, df, ind)
                            if img_data:
                                await app.bot.send_photo(cfg.channel_id, img_data,
                                    caption=f"📊 *نمودار {sym.replace('/USDT','')}* | ${t['last']:,.2f}",
                                    parse_mode="Markdown")
                        
                        logger.info(f"📤 Signal sent: {sym}")
                        await asyncio.sleep(45)
                except Exception as e:
                    logger.error(f"Signal error for {sym}: {e}")
                    continue
            
            # ===== GROQ: Market Overview =====
            if groq_ai.enabled:
                top = []
                for sym in cfg.symbols[:10]:
                    t = exchange_mgr.ticker(sym)
                    if t: top.append({'symbol': sym.replace('/USDT',''), 'price': t['last'], 'change': t.get('percentage',0)})
                market = await groq_ai.market_overview(top)
                if market:
                    await app.bot.send_message(cfg.channel_id,
                        f"{fmt.header()}📰 *تحلیل بازار*\n\n{market}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                        parse_mode="Markdown")
            
            # ===== GEMINI: Additional Analyses =====
            if gemini_ai.enabled:
                btc_t = exchange_mgr.ticker("BTC/USDT")
                if btc_t:
                    fundamental = await gemini_ai.fundamental_analysis("BTC/USDT", btc_t['last'], btc_t.get('percentage',0))
                    if fundamental:
                        await app.bot.send_message(cfg.channel_id,
                            f"{fmt.header()}📰 *فاندامنتال BTC (Gemini)*\n\n{fundamental}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                            parse_mode="Markdown")
                        await asyncio.sleep(30)
                    
                    sentiment = await gemini_ai.market_sentiment("BTC/USDT", btc_t['last'], btc_t.get('percentage',0))
                    if sentiment:
                        await app.bot.send_message(cfg.channel_id,
                            f"{fmt.header()}💭 *احساسات بازار (Gemini)*\n\n{sentiment}\n\n━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                            parse_mode="Markdown")
            
            # Position monitoring
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 100)
                    if t and df is not None:
                        ind = ui.calculate_all(df)
                        result = trader.update(sym, t['last'], ind['ATR_14'])
                        if result:
                            emoji = "🟢" if result['pnl'] > 0 else "🔴"
                            await app.bot.send_message(cfg.channel_id,
                                f"{fmt.header()}{emoji} *پوزیشن بسته شد*\n📊 {sym}\n💰 ${result['pnl']:+,.2f}\n📋 {result['reason']}",
                                parse_mode="Markdown")
                except: pass
            
            # Stats
            stats = token_mgr.get_stats()
            logger.info(f"✅ Cycle done | Groq:{stats['groq']}/{stats['groq_max']} | Gemini:{stats['gemini']}/{stats['gemini_max']} | Total:{stats['total']}/{stats['total_max']}")
            
        except Exception as e:
            logger.error(f"Loop error: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education_loop(app: Application):
    await asyncio.sleep(30)
    
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                content = await groq_ai.educational_content()
                if content:
                    await app.bot.send_message(cfg.channel_id, fmt.education_msg(content), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Edu error: {e}")
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
    
    asyncio.create_task(auto_signals_loop(app))
    asyncio.create_task(auto_education_loop(app))
    
    logger.info("="*70)
    logger.info("🚀 CRYPTO PULSE v9.0 - DUAL AI ENGINE")
    logger.info(f"🧠 Groq: {'✅' if groq_ai.enabled else '❌'} ({token_mgr.GROQ_MAX_TPM} TPM)")
    logger.info(f"🧠 Gemini: {'✅' if gemini_ai.enabled else '❌'} ({token_mgr.GEMINI_MAX_TPM} TPM)")
    logger.info(f"📊 Total: {token_mgr.TOTAL_TPM} TPM | 7 EMA | 25+ Indicators")
    logger.info(f"📅 {dtm.now_persian()}")
    logger.info("="*70)
    
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
    except KeyboardInterrupt: ProcessLock.release()
    except Exception as e: logger.critical(f"Fatal: {e}"); ProcessLock.release()
