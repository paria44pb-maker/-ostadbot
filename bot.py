#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║     CRYPTO PULSE ULTIMATE AI TRADING BOT v8.0 - THE FINAL BOSS      ║
║     Groq AI | 25+ Indicators | EMA Types | Self-Learning | CoinEx    ║
║     EXACTLY 8000 TPM - FULL UTILIZATION                              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, logging, asyncio, time, json, random, signal, math
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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

# ============================================================
# PROFESSIONAL LOGGING SYSTEM
# ============================================================
logger = logging.getLogger('CryptoPulseV8')
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)

for name, level in [('crypto_v8.log', logging.INFO), ('crypto_v8_debug.log', logging.DEBUG), ('crypto_v8_errors.log', logging.ERROR)]:
    handler = RotatingFileHandler(name, maxBytes=10*1024*1024, backupCount=7, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)s | %(funcName)s | %(message)s'))
    logger.addHandler(handler)

for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'aiohttp']:
    logging.getLogger(lib).setLevel(logging.WARNING)

logger.info("="*70)
logger.info("🚀 CRYPTO PULSE ULTIMATE v8.0 - THE FINAL BOSS INITIALIZING")
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
    education_interval: int = 600  # Also 10 minutes!
    price_interval: int = 600

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v8.lock"
    
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
# GROQ TOKEN MANAGER - دقیقاً 8000 TPM
# ============================================================
class GroqTokenManager:
    """Token usage tracker for Groq EXACTLY 8000 TPM limit"""
    
    MAX_TPM: int = 8000  # EXACTLY 8000 - نه بیشتر نه کمتر
    
    def __init__(self):
        self._usage_window: deque = deque()
        self._total_tokens_today: int = 0
        self._total_requests_today: int = 0
        self._rate_limit_hits: int = 0
    
    @property
    def current_usage(self) -> int:
        """Get current TPM usage"""
        now = time.time()
        while self._usage_window and now - self._usage_window[0][0] > 60:
            self._usage_window.popleft()
        return sum(tokens for _, tokens in self._usage_window)
    
    @property
    def remaining(self) -> int:
        """Get remaining tokens - exactly to 8000"""
        return max(0, self.MAX_TPM - self.current_usage)
    
    @property
    def usage_pct(self) -> float:
        """Get usage percentage"""
        return (self.current_usage / self.MAX_TPM) * 100
    
    def can_request(self, estimated_tokens: int = 500) -> bool:
        """Check if we can make a request - exactly at 8000 limit"""
        return (self.current_usage + estimated_tokens) <= self.MAX_TPM
    
    def wait_time(self, estimated_tokens: int = 500) -> float:
        """Calculate wait time if over limit"""
        if self.can_request(estimated_tokens):
            return 0
        if self._usage_window:
            oldest_time = self._usage_window[0][0]
            return max(0, 60 - (time.time() - oldest_time) + 1)
        return 60
    
    def record(self, tokens: int):
        """Record token usage"""
        self._usage_window.append((time.time(), tokens))
        self._total_tokens_today += tokens
        self._total_requests_today += 1
    
    def record_rate_limit(self):
        """Record rate limit hit"""
        self._rate_limit_hits += 1
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            'current': self.current_usage,
            'max': self.MAX_TPM,
            'remaining': self.remaining,
            'pct': self.usage_pct,
            'today_tokens': self._total_tokens_today,
            'today_requests': self._total_requests_today,
            'rate_limits': self._rate_limit_hits
        }

# Global token manager instance
token_mgr = GroqTokenManager()

# ============================================================
# GROQ AI - EXACTLY 8000 TPM UTILIZATION
# ============================================================
class GroqAIEngine:
    """AI Engine - دقیقاً 8000 TPM با استفاده کامل از سقف"""
    API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    MODEL: str = "llama-3.3-70b-versatile"
    
    # Token allocation per request type - دقیقاً برای 8000 TPM
    TOKENS = {
        'technical': 650,      # تحلیل تکنیکال - کامل و جامع
        'market': 500,         # تحلیل بازار
        'education': 1000,     # محتوای آموزشی - حجیم و پرمحتوا
        'prediction': 450,     # پیش‌بینی
        'strategy': 500,       # استراتژی
        'sentiment': 350,      # احساسات بازار
        'fundamental': 500,    # تحلیل فاندامنتال
        'price_action': 500,   # پرایس اکشن
    }
    
    def __init__(self):
        self.enabled: bool = bool(cfg.groq_api_key)
        self.client: httpx.AsyncClient = httpx.AsyncClient(timeout=60.0)
        if self.enabled:
            logger.info(f"🧠 Groq AI Ready (EXACTLY {token_mgr.MAX_TPM} TPM Limit)")
        else:
            logger.warning("⚠️ Groq AI Disabled - Set GROQ_API_KEY in .env")
    
    async def _call_api(self, prompt: str, max_tokens: int = 650) -> Optional[str]:
        """Call Groq API with EXACT TPM limit check"""
        if not self.enabled:
            return None
        
        # Check TPM limit - exactly at 8000
        if not token_mgr.can_request(max_tokens):
            wait = token_mgr.wait_time(max_tokens)
            if wait > 30:
                logger.warning(f"⏳ TPM at limit ({token_mgr.current_usage}/{token_mgr.MAX_TPM}), skipping")
                token_mgr.record_rate_limit()
                return None
            logger.info(f"⏳ Waiting {wait:.0f}s for TPM reset...")
            await asyncio.sleep(wait)
        
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
                        {"role": "system", "content": "You are an elite crypto analyst. Respond only in Persian (فارسی). Use emojis. Be detailed and professional."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 429:
                token_mgr.record_rate_limit()
                logger.warning("⚠️ Groq 429 - Rate Limited")
                return None
            
            if response.status_code == 200:
                data = response.json()
                actual_tokens = data.get('usage', {}).get('total_tokens', max_tokens)
                token_mgr.record(actual_tokens)
                return data["choices"][0]["message"]["content"]
            
            logger.error(f"Groq API Error: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Groq Exception: {e}")
            return None
    
    async def technical_analysis(self, symbol: str, indicators: Dict, price: float, 
                                  change: float, patterns: List[str], mtf_data: Dict) -> Optional[str]:
        """تحلیل تکنیکال عمیق - 650 tokens"""
        if not self.enabled: return None
        
        mtf_text = ""
        for tf, ind in mtf_data.items():
            mtf_text += f"{tf}: RSI={ind.get('RSI_14',50):.0f} | MACD={'Bullish' if ind.get('MACD_HIST',0)>0 else 'Bearish'} | ADX={ind.get('ADX',20):.0f}\n"
        
        prompt = f"""You are a world-class technical analyst. Analyze this cryptocurrency with precision:

SYMBOL: {symbol}
PRICE: ${price:,.4f} | 24h CHANGE: {change:+.2f}%
DATE: {dtm.now_persian()}

=== 25+ TECHNICAL INDICATORS ===
RSI(7): {indicators.get('RSI_7',50):.1f}
RSI(14): {indicators.get('RSI_14',50):.1f}
RSI(21): {indicators.get('RSI_21',50):.1f}
MACD Histogram: {indicators.get('MACD_HIST',0):.4f}
Stochastic K: {indicators.get('STOCH_K',50):.1f}
Stochastic D: {indicators.get('STOCH_D',50):.1f}
ADX: {indicators.get('ADX',20):.1f}
DI+: {indicators.get('DI+',20):.1f}
DI-: {indicators.get('DI-',20):.1f}
CCI(20): {indicators.get('CCI',0):.1f}
MFI(14): {indicators.get('MFI',50):.1f}
Bollinger %B: {indicators.get('BB_PCT',0.5):.3f}
Bollinger Width: {indicators.get('BB_WIDTH',0):.4f}
ATR(14): {indicators.get('ATR_14',0):.4f}
ATR%: {indicators.get('ATR_PCT',0):.2f}%
Williams %R: {indicators.get('WILLIAMS_R',-50):.1f}
Volume Ratio: {indicators.get('VOL_RATIO',1):.2f}x
Trend Strength: {indicators.get('TREND_STR',0):.1f}%

=== EMA TYPES ===
EMA_7: {indicators.get('EMA_7',0):.2f}
EMA_14: {indicators.get('EMA_14',0):.2f}
EMA_20: {indicators.get('EMA_20',0):.2f}
EMA_50: {indicators.get('EMA_50',0):.2f}
EMA_100: {indicators.get('EMA_100',0):.2f}
EMA_200: {indicators.get('EMA_200',0):.2f}
DEMA_20: {indicators.get('DEMA_20',0):.2f}
TEMA_20: {indicators.get('TEMA_20',0):.2f}
KAMA: {indicators.get('KAMA',0):.2f}
HMA_20: {indicators.get('HMA_20',0):.2f}
FRAMA_20: {indicators.get('FRAMA_20',0):.2f}
JMA_20: {indicators.get('JMA_20',0):.2f}

=== CANDLESTICK PATTERNS ===
Detected: {', '.join(patterns) if patterns else 'None'}

=== DIVERGENCE ===
{indicators.get('DIVERGENCE', 'NONE')}

=== MULTI-TIMEFRAME ===
{mtf_text}

=== SUPPORT/RESISTANCE ===
Resistance: ${indicators.get('RESISTANCE',0):.2f}
Pivot: ${indicators.get('PIVOT',0):.2f}
Support: ${indicators.get('SUPPORT',0):.2f}

Provide in Persian (فارسی):
1. Technical Analysis Summary
2. Key Support/Resistance with exact prices
3. EMA Alignment & Crossover Analysis
4. Momentum & Volume Analysis
5. Multi-Timeframe Confluence
6. SHORT-TERM Prediction (4-12 hours)
7. MEDIUM-TERM Prediction (1-3 days)
8. Entry/Exit Suggestions with Price Levels
9. Risk Level (LOW/MEDIUM/HIGH/EXTREME)
10. Confidence Score (0-100%)

Use emojis. Be specific. Max 400 words."""
        
        return await self._call_api(prompt, self.TOKENS['technical'])
    
    async def market_overview(self, top_coins: List[Dict]) -> Optional[str]:
        """تحلیل کلی بازار - 500 tokens"""
        if not self.enabled: return None
        
        coins_text = "\n".join([f"{c['symbol']}: ${c['price']:,.2f} ({c['change']:+.2f}%)" for c in top_coins[:10]])
        
        prompt = f"""You are a crypto market strategist. Provide a comprehensive market overview in Persian (فارسی):

DATE: {dtm.now_persian()}

TOP 10 COINS:
{coins_text}

Provide:
1. Overall Market Sentiment
2. Bitcoin Dominance Analysis
3. Altcoin Season Assessment
4. Fear & Greed Analysis
5. Key Market Drivers Today
6. Upcoming Events to Watch
7. Sector Rotation Analysis
8. Institutional Flow Analysis
9. Risk Assessment for New Entries
10. Best & Worst Performers Analysis

Use emojis. Be comprehensive. Max 500 words."""
        
        return await self._call_api(prompt, self.TOKENS['market'])
    
    async def trading_strategy(self, symbol: str, indicators: Dict, price: float) -> Optional[str]:
        """استراتژی معاملاتی - 500 tokens"""
        if not self.enabled: return None
        
        prompt = f"""You are a professional trading strategist. Create a detailed trading strategy for {symbol} at ${price:,.2f} in Persian (فارسی):

RSI(14): {indicators.get('RSI_14',50):.1f}
ADX: {indicators.get('ADX',20):.1f}
ATR%: {indicators.get('ATR_PCT',0):.2f}%
BB Position: {indicators.get('BB_PCT',0.5):.2f}

Provide:
1. Optimal Entry Strategy (Limit/Market/Scale-in)
2. Position Sizing Recommendation
3. Stop Loss Placement (Multiple Levels)
4. Take Profit Targets (Short/Medium/Long)
5. Trailing Stop Strategy
6. Risk Management Rules
7. Exit Strategy (When to take profits/cut losses)
8. Maximum Drawdown Allowance
9. Correlation Hedge Suggestions
10. Time-Based Exit Rules

Use emojis. Be practical. Max 400 words."""
        
        return await self._call_api(prompt, self.TOKENS['strategy'])
    
    async def educational_content(self, topic: str = None) -> Optional[str]:
        """محتوای آموزشی حجیم - 1000 tokens"""
        if not self.enabled: return None
        
        topics = [
            "تحلیل تکنیکال پیشرفته با EMA و فیبوناچی",
            "روانشناسی معامله‌گری و کنترل احساسات در بازار",
            "مدیریت سرمایه و ریسک پیشرفته در کریپتو",
            "الگوهای کندلی و پرایس اکشن حرفه‌ای",
            "تحلیل وایکوف و فازهای انباشت و توزیع",
            "استراتژی‌های معاملاتی در بازارهای نوسانی",
            "تحلیل آنچین و داده‌های درون شبکه‌ای",
            "مدیریت حد ضرر و ترلینگ استاپ حرفه‌ای",
            "تحلیل مولتی تایم‌فریم و همروندی",
            "فاندامنتال و تاثیر اخبار بر بازار کریپتو",
            "ایچیموکو و استراتژی‌های ابر کومو",
            "باندهای بولینگر و استراتژی فشردگی",
            "مکدی و واگرایی‌های مخفی",
            "آراس‌آی و تشخیص اشباع خرید و فروش",
            "تحلیل حجم معاملات و ردپای نهنگ‌ها",
            "فیبوناچی و نسبت‌های طلایی در معامله",
            "الگوهای هارمونیک و نقاط بازگشتی",
            "مدیریت سبد سرمایه در بازار کریپتو",
            "تحلیل تایم‌فریم‌های بالا برای معاملات روزانه",
            "روش‌های نوین تحلیل بازار با هوش مصنوعی"
        ]
        
        if not topic:
            topic = random.choice(topics)
        
        prompt = f"""You are a crypto trading professor. Write an EXTENSIVE, DETAILED educational post in Persian (فارسی) about:

TOPIC: {topic}
DATE: {dtm.now_persian()}

Requirements:
- AT LEAST 500 words
- Practical examples with real scenarios
- Step-by-step guides
- Pro tips and common mistakes
- Advanced techniques
- Include specific numbers and calculations
- Use emojis extensively
- Make it engaging and professional
- Add a "Golden Nugget" section at the end
- Include actionable takeaways

Make this the BEST content about this topic on Telegram!"""
        
        return await self._call_api(prompt, self.TOKENS['education'])
    
    async def market_prediction(self, symbol: str, indicators: Dict, price: float) -> Optional[str]:
        """پیش‌بینی بازار - 450 tokens"""
        if not self.enabled: return None
        
        prompt = f"""You are a crypto market forecaster. Predict the future of {symbol} at ${price:,.2f} in Persian (فارسی):

DATE: {dtm.now_persian()}
RSI: {indicators.get('RSI_14',50):.1f}
MACD: {'Bullish' if indicators.get('MACD_HIST',0)>0 else 'Bearish'}
ADX: {indicators.get('ADX',20):.1f}
BB Position: {indicators.get('BB_PCT',0.5):.2f}

Provide predictions for:
1. Next 4 Hours (with price target)
2. Next 24 Hours
3. Next 7 Days
4. Next 30 Days
5. Best Case Scenario
6. Worst Case Scenario
7. Most Likely Scenario
8. Key Levels to Watch
9. Reversal Probability
10. Confidence Level for Each Prediction

Use emojis. Be bold with specific numbers! Max 500 words."""
        
        return await self._call_api(prompt, self.TOKENS['prediction'])
    
    async def sentiment_analysis(self, symbol: str, price: float, change: float) -> Optional[str]:
        """تحلیل احساسات بازار - 350 tokens"""
        if not self.enabled: return None
        
        prompt = f"""You are a market sentiment analyst. Analyze {symbol} sentiment in Persian (فارسی):

Price: ${price:,.2f}
24h Change: {change:+.2f}%
Date: {dtm.now_persian()}

Provide:
1. Current Market Sentiment (Fear/Greed/Neutral)
2. Social Media Sentiment
3. Institutional Sentiment
4. Retail Sentiment
5. Whale Activity Assessment
6. Contrarian Indicators
7. Sentiment Divergence Analysis
8. Historical Sentiment Comparison
9. Sentiment-Based Trading Strategy
10. Sentiment Reversal Signals

Use emojis extensively. Max 400 words."""
        
        return await self._call_api(prompt, self.TOKENS['sentiment'])
    
    async def fundamental_analysis(self, symbol: str, price: float, change: float) -> Optional[str]:
        """تحلیل فاندامنتال - 500 tokens"""
        if not self.enabled: return None
        
        coin = symbol.replace('/USDT', '')
        
        prompt = f"""You are a crypto fundamental analyst. Analyze {coin} fundamentally in Persian (فارسی):

Price: ${price:,.2f} | 24h Change: {change:+.2f}%
Date: {dtm.now_persian()}

Provide:
1. Project Overview & Technology
2. Team & Development Activity
3. Adoption & Partnerships
4. Tokenomics & Supply
5. Competition Analysis
6. Upcoming Catalysts
7. Institutional Interest
8. On-Chain Metrics
9. Risk Factors
10. Long-Term Outlook (6-12 months)

Use emojis. Be thorough. Max 400 words."""
        
        return await self._call_api(prompt, self.TOKENS['fundamental'])
    
    async def price_action_analysis(self, symbol: str, indicators: Dict, price: float, patterns: List[str]) -> Optional[str]:
        """تحلیل پرایس اکشن - 500 tokens"""
        if not self.enabled: return None
        
        prompt = f"""You are a price action expert. Analyze {symbol} at ${price:,.2f} in Persian (فارسی):

Patterns: {', '.join(patterns) if patterns else 'None'}
BB Position: {indicators.get('BB_PCT',0.5):.2f}
Volume Ratio: {indicators.get('VOL_RATIO',1):.2f}x
ATR%: {indicators.get('ATR_PCT',0):.2f}%

Provide:
1. Market Structure Analysis
2. Key Support/Resistance Zones
3. Supply/Demand Analysis
4. Candlestick Pattern Interpretation
5. Breakout/Fakeout Assessment
6. Order Flow Insights
7. Optimal Entry/Exit Points
8. Stop Loss Placement
9. Take Profit Targets
10. Risk/Reward Assessment

Use emojis. Be specific with levels. Max 400 words."""
        
        return await self._call_api(prompt, self.TOKENS['price_action'])

ai = GroqAIEngine()

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
    
    def order_book(self, symbol: str) -> Optional[Dict]:
        """دریافت عمق بازار"""
        if not self.connected: return None
        try: return self._ex.fetch_order_book(symbol, 10)
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
        
        # ===== 7 TYPES OF EMA =====
        # 1. Standard EMA
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
            ind[f'SMA_{p}'] = float(close.rolling(p).mean().iloc[-1])
        
        # 2. DEMA (Double EMA)
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema20_2 = ema20.ewm(span=20, adjust=False).mean()
        ind['DEMA_20'] = float((2 * ema20.iloc[-1] - ema20_2.iloc[-1]))
        
        # 3. TEMA (Triple EMA)
        ema20_3 = ema20_2.ewm(span=20, adjust=False).mean()
        ind['TEMA_20'] = float((3 * ema20.iloc[-1] - 3 * ema20_2.iloc[-1] + ema20_3.iloc[-1]))
        
        # 4. KAMA (Kaufman Adaptive Moving Average)
        from ta.momentum import KAMAIndicator
        try: ind['KAMA'] = float(KAMAIndicator(close, 20, 2, 30).kama().iloc[-1])
        except: ind['KAMA'] = ind['EMA_20']
        
        # 5. HMA (Hull Moving Average)
        if len(close) >= 20:
            wma_half = 2 * close.rolling(10).apply(lambda x: np.average(x, weights=range(1,11))).iloc[-1]
            wma_full = close.rolling(20).apply(lambda x: np.average(x, weights=range(1,21))).iloc[-1]
            diff = wma_half - wma_full
            ind['HMA_20'] = float(diff if not np.isnan(diff) else ind['EMA_20'])
        else:
            ind['HMA_20'] = ind['EMA_20']
        
        # 6. FRAMA (Fractal Adaptive Moving Average)
        if len(close) >= 20:
            n1 = (high.rolling(10).max().iloc[-1] - low.rolling(10).min().iloc[-1]) / 10
            n2 = (high.rolling(20).max().iloc[-1] - low.rolling(20).min().iloc[-1]) / 20
            n3 = (high.rolling(40).max().iloc[-1] - low.rolling(40).min().iloc[-1]) / 40 if len(close) >= 40 else n2
            dim = (np.log(n1 + n2) - np.log(n3)) / np.log(2) if n3 > 0 else 1
            alpha = np.exp(-4.6 * (dim - 1))
            alpha = max(0.01, min(1, alpha))
            frama = close.iloc[-1] * alpha + ind['EMA_20'] * (1 - alpha)
            ind['FRAMA_20'] = float(frama)
        else:
            ind['FRAMA_20'] = ind['EMA_20']
        
        # 7. JMA (Jurik Moving Average) - Simplified
        if len(close) >= 20:
            jma = close.iloc[-5:].mean() * 0.5 + ind['EMA_20'] * 0.3 + close.iloc[-1] * 0.2
            ind['JMA_20'] = float(jma)
        else:
            ind['JMA_20'] = ind['EMA_20']
        
        # ===== RSI MULTIPLE =====
        from ta.momentum import RSIIndicator
        for p in [7, 14, 21]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close, window=p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        
        # ===== MACD =====
        from ta.trend import MACD
        try:
            macd = MACD(close, 12, 26, 9)
            ind['MACD_LINE'] = float(macd.macd().iloc[-1])
            ind['MACD_SIG'] = float(macd.macd_signal().iloc[-1])
            ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_LINE'] = ind['MACD_SIG'] = ind['MACD_HIST'] = 0.0
        
        # ===== STOCHASTIC =====
        from ta.momentum import StochasticOscillator
        try:
            stoch = StochasticOscillator(high, low, close, 14, 3)
            ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
            ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        except: ind['STOCH_K'] = ind['STOCH_D'] = 50.0
        
        # ===== BOLLINGER BANDS =====
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
        
        # ===== ATR =====
        from ta.volatility import AverageTrueRange
        for p in [7, 14]:
            try: ind[f'ATR_{p}'] = float(AverageTrueRange(high, low, close, p).average_true_range().iloc[-1])
            except: ind[f'ATR_{p}'] = close.iloc[-1] * 0.01
        ind['ATR_PCT'] = float(ind['ATR_14'] / close.iloc[-1] * 100)
        
        # ===== ADX =====
        from ta.trend import ADXIndicator
        try:
            adx = ADXIndicator(high, low, close, 14)
            ind['ADX'] = float(adx.adx().iloc[-1])
            ind['DI+'] = float(adx.adx_pos().iloc[-1])
            ind['DI-'] = float(adx.adx_neg().iloc[-1])
        except: ind['ADX'] = 20.0; ind['DI+'] = ind['DI-'] = 20.0
        
        # ===== CCI =====
        from ta.trend import CCIIndicator
        try: ind['CCI'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        
        # ===== ICHIMOKU =====
        from ta.trend import IchimokuIndicator
        try:
            ichi = IchimokuIndicator(high, low, 9, 26, 52)
            ind['ICH_TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1])
            ind['ICH_KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
            ind['ICH_SENKOU_A'] = float(ichi.ichimoku_a().iloc[-1])
            ind['ICH_SENKOU_B'] = float(ichi.ichimoku_b().iloc[-1])
        except:
            ind['ICH_TENKAN'] = ind['ICH_KIJUN'] = ind['ICH_SENKOU_A'] = ind['ICH_SENKOU_B'] = close.iloc[-1]
        
        # ===== WILLIAMS %R =====
        from ta.momentum import WilliamsRIndicator
        try: ind['WILLIAMS_R'] = float(WilliamsRIndicator(high, low, close, 14).williams_r().iloc[-1])
        except: ind['WILLIAMS_R'] = -50.0
        
        # ===== MFI =====
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high, low, close, volume, 14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        
        # ===== VOLUME =====
        vol_sma = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else volume.iloc[-1]
        ind['VOL_RATIO'] = float(volume.iloc[-1] / vol_sma if vol_sma > 0 else 1)
        
        # ===== TREND STRENGTH =====
        ind['TREND_STR'] = float((close.iloc[-1] - close.iloc[-50]) / close.iloc[-50] * 100) if len(close) >= 50 else 0
        
        # ===== PIVOT POINTS =====
        h, l, c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        pivot = (h + l + c) / 3
        ind['PIVOT'] = float(pivot)
        ind['R1'] = float(2*pivot - l)
        ind['S1'] = float(2*pivot - h)
        ind['R2'] = float(pivot + (h-l))
        ind['S2'] = float(pivot - (h-l))
        
        # ===== FIBONACCI =====
        h50 = high.rolling(50).max().iloc[-1] if len(high) >= 50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low) >= 50 else low.min()
        diff = h50 - l50
        for level in [0.236, 0.382, 0.5, 0.618, 0.786]:
            ind[f'FIB_{int(level*1000)}'] = float(h50 - diff * level)
        
        # ===== SUPPORT/RESISTANCE =====
        ind['SUPPORT'] = float(low.rolling(20).min().iloc[-1]) if len(low) >= 20 else low.min()
        ind['RESISTANCE'] = float(high.rolling(20).max().iloc[-1]) if len(high) >= 20 else high.max()
        
        # ===== CANDLESTICK PATTERNS =====
        ind.update(UltimateIndicators.detect_candles(df))
        
        # ===== DIVERGENCE =====
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
        upper = h - max(c, o)
        lower = min(c, o) - l
        tr = h - l
        if tr == 0: return patterns
        
        patterns['DOJI'] = body <= tr * 0.08
        patterns['HAMMER'] = lower > body * 2 and upper < body * 0.5 and c > o
        patterns['SHOOTING_STAR'] = upper > body * 2 and lower < body * 0.5 and c < o
        patterns['ENGULFING_BULL'] = c > o and pc < po and o <= pc and c >= po
        patterns['ENGULFING_BEAR'] = c < o and pc > po and o >= pc and c <= po
        patterns['MARUBOZU_BULL'] = c > o and upper < body * 0.1 and lower < body * 0.1
        patterns['MARUBOZU_BEAR'] = c < o and upper < body * 0.1 and lower < body * 0.1
        
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
# SIGNAL GENERATOR WITH EMA TYPES
# ============================================================
class SignalGenerator:
    @staticmethod
    def generate(ind: Dict, price: float, mtf: Dict = None) -> Tuple[str, int, int]:
        score = 0
        
        # EMA Crossovers (with all 7 types)
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']: score += 150
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']: score -= 150
        
        if ind['DEMA_20'] > ind['EMA_20']: score += 40
        if ind['TEMA_20'] > ind['EMA_20']: score += 30
        if ind['HMA_20'] > ind['EMA_20']: score += 30
        if ind['FRAMA_20'] > ind['EMA_20']: score += 20
        if ind['JMA_20'] > ind['EMA_20']: score += 20
        
        # RSI
        rsi = ind['RSI_14']
        if rsi < 30: score += 120
        elif rsi < 40: score += 60
        elif rsi > 70: score -= 120
        elif rsi > 60: score -= 60
        
        # MACD
        if ind['MACD_HIST'] > 0: score += 70
        else: score -= 70
        
        # Stochastic
        if ind['STOCH_K'] < 20: score += 70
        elif ind['STOCH_K'] > 80: score -= 70
        
        # CCI
        cci = ind['CCI']
        if cci < -200: score += 70
        elif cci > 200: score -= 70
        
        # Bollinger
        if ind['BB_PCT'] < 0.1: score += 100
        elif ind['BB_PCT'] > 0.9: score -= 100
        
        # Volume
        if ind['VOL_RATIO'] > 2: score += 50 if score > 0 else -50
        
        # MFI
        if ind['MFI'] < 20: score += 60
        elif ind['MFI'] > 80: score -= 60
        
        # Candles
        if ind.get('ENGULFING_BULL'): score += 80
        if ind.get('HAMMER'): score += 50
        if ind.get('ENGULFING_BEAR'): score -= 80
        if ind.get('SHOOTING_STAR'): score -= 50
        if ind.get('THREE_WHITE_SOLDIERS'): score += 60
        if ind.get('THREE_BLACK_CROWS'): score -= 60
        
        # Divergence
        if ind.get('DIVERGENCE') == 'BULLISH_DIVERGENCE': score += 70
        elif ind.get('DIVERGENCE') == 'BEARISH_DIVERGENCE': score -= 70
        
        # MTF
        if mtf:
            for tf, ti_data in mtf.items():
                w = {"5m": 0.3, "15m": 0.5, "30m": 0.7, "1h": 1.0, "2h": 1.2, "4h": 1.5, "6h": 1.8, "12h": 2.0, "1d": 2.5, "3d": 3.0, "1w": 4.0}.get(tf, 0.5)
                if ti_data.get('RSI_14', 50) > 55: score += int(25 * w)
                elif ti_data.get('RSI_14', 50) < 45: score -= int(25 * w)
        
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
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'best_hour': None,
            'worst_hour': None,
            'best_symbol': None,
            'worst_symbol': None,
            'symbol_performance': {},
            'hour_performance': {},
            'confidence_threshold': 70,
            'risk_multiplier': 1.0,
            'learned_patterns': []
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
                json.dump({
                    'balance': self.balance,
                    'history': self.history[-1000:],
                    'experience': self.experience
                }, f)
        except: pass
    
    def learn_from_history(self):
        """Learn from past trades to improve"""
        if len(self.history) < 10:
            return
        
        wins = [t for t in self.history if t['pnl'] > 0]
        losses = [t for t in self.history if t['pnl'] <= 0]
        
        self.experience['total_trades'] = len(self.history)
        self.experience['wins'] = len(wins)
        self.experience['losses'] = len(losses)
        
        if wins:
            self.experience['best_trade'] = max(t['pnl'] for t in wins)
            self.experience['avg_win'] = sum(t['pnl'] for t in wins) / len(wins)
        
        if losses:
            self.experience['worst_trade'] = min(t['pnl'] for t in losses)
            self.experience['avg_loss'] = sum(t['pnl'] for t in losses) / len(losses)
        
        # Adjust confidence threshold based on win rate
        win_rate = len(wins) / len(self.history) * 100
        if win_rate > 70:
            self.experience['confidence_threshold'] = 60
            self.experience['risk_multiplier'] = 1.3
        elif win_rate > 60:
            self.experience['confidence_threshold'] = 65
            self.experience['risk_multiplier'] = 1.1
        elif win_rate < 40:
            self.experience['confidence_threshold'] = 80
            self.experience['risk_multiplier'] = 0.7
        
        self.save()
    
    def should_trade(self, symbol: str, confidence: int, score: int) -> Tuple[bool, str]:
        """Decide whether to trade based on experience"""
        if confidence < self.experience['confidence_threshold']:
            return False, f"اطمینان {confidence}% کمتر از حد نیاز {self.experience['confidence_threshold']}%"
        
        if len(self.positions) >= cfg.max_positions:
            return False, "حداکثر پوزیشن باز"
        
        if self.consecutive_losses >= cfg.max_consecutive_losses:
            return False, f"{cfg.max_consecutive_losses} ضرر متوالی"
        
        # Check symbol performance
        sym_perf = self.experience.get('symbol_performance', {}).get(symbol, 0)
        if sym_perf < -500:
            return False, f"عملکرد ضعیف {symbol} در گذشته"
        
        return True, "آماده معامله"
    
    def open(self, symbol: str, entry: float, sl: float, tp: float, conf: int) -> Optional[Dict]:
        can_trade, reason = self.should_trade(symbol, conf, conf)
        if not can_trade:
            logger.info(f"⚠️ Trade rejected for {symbol}: {reason}")
            return None
        
        risk = self.balance * cfg.risk_per_trade * self.experience['risk_multiplier']
        if self.consecutive_losses > 0:
            risk *= (0.5 ** self.consecutive_losses)
        
        pr = abs(entry - sl)
        sz = min(risk/pr, self.balance*0.25/entry) if pr > 0 else 0
        
        if sz <= 0 or sz*entry > self.balance:
            return None
        
        self.balance -= sz * entry
        pos = {
            'symbol': symbol, 'size': sz, 'entry': entry,
            'sl': sl, 'tp': tp, 'high': entry,
            'time': datetime.now(), 'conf': conf
        }
        self.positions[symbol] = pos
        self.save()
        logger.info(f"🔵 OPEN {symbol} | {sz:.4f} @ {entry:.2f} | Risk: {self.experience['risk_multiplier']:.1f}x")
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
        
        t = {
            'symbol': symbol, 'entry': p['entry'], 'exit': price,
            'pnl': pnl, 'reason': reason, 'time': datetime.now().isoformat(),
            'hour': datetime.now().hour
        }
        self.history.append(t)
        
        # Update experience
        sym_perf = self.experience.get('symbol_performance', {})
        sym_perf[symbol] = sym_perf.get(symbol, 0) + pnl
        self.experience['symbol_performance'] = sym_perf
        
        self.learn_from_history()
        self.save()
        
        logger.info(f"{'🟢' if pnl>0 else '🔴'} CLOSE {symbol} | ${pnl:+.2f} | {reason}")
        return t
    
    def get_stats(self) -> Dict:
        total = max(1, len(self.history))
        wins = len([t for t in self.history if t['pnl'] > 0])
        return {
            'balance': self.balance,
            'pnl': sum(t['pnl'] for t in self.history),
            'total': total,
            'wins': wins,
            'win_rate': wins/total*100,
            'experience': self.experience
        }

trader = SelfLearningTrader()

# ============================================================
# FORMATTER WITH DATE/TIME
# ============================================================
class Formatter:
    @staticmethod
    def header() -> str:
        return dtm.timestamp_header()
    
    @staticmethod
    def signal_msg(analysis: Dict, ai_analyses: Dict = None) -> str:
        s = analysis['symbol'].replace('/USDT','')
        i = analysis['indicators']
        pats = [k for k,v in i.items() if isinstance(v,bool) and v]
        
        msg = f"""
{Formatter.header()}
╔══════════════════════════════════════════════╗
║       🔥 سیگنال {s} 🔥                  ║
╚══════════════════════════════════════════════╝

💰 قیمت: ${analysis['price']:,.4f}
📊 تغییر: {analysis['change']:+.2f}%

🎯 *سیگنال:* {analysis['signal']}
💪 اطمینان: {analysis['confidence']}% | امتیاز: {analysis['score']}/1000

📈 *انواع EMA:*
• EMA_7: ${i.get('EMA_7',0):,.2f} | EMA_20: ${i.get('EMA_20',0):,.2f}
• EMA_50: ${i.get('EMA_50',0):,.2f} | EMA_200: ${i.get('EMA_200',0):,.2f}
• DEMA_20: ${i.get('DEMA_20',0):,.2f} | TEMA_20: ${i.get('TEMA_20',0):,.2f}
• HMA_20: ${i.get('HMA_20',0):,.2f} | KAMA: ${i.get('KAMA',0):,.2f}
• FRAMA_20: ${i.get('FRAMA_20',0):,.2f} | JMA_20: ${i.get('JMA_20',0):,.2f}

📊 *اندیکاتورها:*
• RSI(14): {i['RSI_14']:.1f} | MACD: {'صعودی' if i['MACD_HIST']>0 else 'نزولی'}
• ADX: {i['ADX']:.1f} | CCI: {i['CCI']:.1f} | MFI: {i['MFI']:.1f}
• BB Width: {i['BB_WIDTH']:.4f} | Vol: {i['VOL_RATIO']:.1f}x

🕯️ *الگوها:* {', '.join(pats) if pats else 'بدون الگو'}
🔄 *واگرایی:* {i.get('DIVERGENCE','NONE')}

🔑 *سطوح:*
• مقاومت: ${i['RESISTANCE']:,.4f}
• حمایت: ${i['SUPPORT']:,.4f}
• Fib 0.618: ${i.get('FIB_618',0):,.4f}

⚠️ حد ضرر: ${analysis['price']-i['ATR_14']*cfg.atr_sl:,.4f}
🎯 حد سود: ${analysis['price']+i['ATR_14']*cfg.atr_tp:,.4f}"""
        
        if ai_analyses:
            if ai_analyses.get('tech'):
                msg += f"\n\n🧠 *تحلیل تکنیکال AI:*\n{ai_analyses['tech'][:600]}..."
            if ai_analyses.get('prediction'):
                msg += f"\n\n🔮 *پیش‌بینی AI:*\n{ai_analyses['prediction'][:400]}..."
        
        msg += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606 | {dtm.now_str()}"
        return msg
    
    @staticmethod
    def education_msg(ai_content: str = None) -> str:
        if ai_content:
            return f"""
{Formatter.header()}
🧠 *آموزش تخصصی هوش مصنوعی*

{ai_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606 | {dtm.now_str()}"""
        
        return f"""
{Formatter.header()}
📚 *آموزش تخصصی*

📖 درس امروز: تحلیل حرفه‌ای بازار

🔍 نکات کلیدی:
• روند دوست شماست
• ریسک/ریوارد ≥ ۱:۲
• حد ضرر اجباری

━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606 | {dtm.now_str()}"""

fmt = Formatter()

# ============================================================
# MENUS
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 قیمت‌ها", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن", callback_data="scan")],
            [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="tech"),
             InlineKeyboardButton("🧠 AI کامل", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("🔮 پیش‌بینی", callback_data="pred_BTC/USDT")],
            [InlineKeyboardButton("📰 بازار AI", callback_data="market_ai"),
             InlineKeyboardButton("📊 استراتژی", callback_data="strat_BTC/USDT"),
             InlineKeyboardButton("💭 احساسات", callback_data="sent_BTC/USDT")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf"),
             InlineKeyboardButton("🧠 تجربه", callback_data="exp")],
            [InlineKeyboardButton("🤖 خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("⏸️ توقف", callback_data="stop")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("🔄 بروز", callback_data="ref"),
             InlineKeyboardButton("❓ راهنما", callback_data="help")]
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
        "🤖 *Crypto Pulse Ultimate v8.0*\n\n"
        "🧠 Groq AI (Llama 3.3 70B) | 8000 TPM\n"
        "📊 ۷ نوع EMA | ۲۵+ اندیکاتور\n"
        "⏰ ۱۱ تایم‌فریم | ۳۰ ارز\n"
        "🎓 یادگیری از تجربه معاملات\n"
        "📢 سیگنال + آموزش هر ۱۰ دقیقه\n\n"
        "👇 انتخاب کنید:",
        parse_mode="Markdown", reply_markup=Menu.main()
    )

async def full_signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🔄 تحلیل کامل {symbol.replace('/USDT','')}...")
    
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calculate_all(df)
    
    mtf = {}
    for tf_name, tf_val in cfg.timeframes.items():
        dft = exchange_mgr.ohlcv(symbol, tf_val, 100)
        if dft is not None: mtf[tf_name] = ui.calculate_all(dft)
    
    sig, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    ai_analyses = {}
    if ai.enabled:
        ai_analyses['tech'] = await ai.technical_analysis(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
        ai_analyses['prediction'] = await ai.market_prediction(symbol, ind, t['last'])
    
    analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
                'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
    
    msg = fmt.signal_msg(analysis, ai_analyses)
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("🧠 AI", callback_data=f"ai_{symbol}"),
            InlineKeyboardButton("🤖 معامله", callback_data=f"trade_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def market_ai_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("📰 تحلیل بازار با AI...")
    
    top = []
    for sym in cfg.symbols[:15]:
        t = exchange_mgr.ticker(sym)
        if t:
            top.append({'symbol': sym.replace('/USDT',''), 'price': t['last'], 'change': t.get('percentage',0)})
    
    ai_overview = await ai.market_overview(top)
    
    if ai_overview:
        await q.edit_message_text(f"{fmt.header()}📰 *تحلیل جامع بازار*\n\n{ai_overview}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="market_ai"), InlineKeyboardButton("🔙", callback_data="back")]]))
    else:
        await q.edit_message_text("❌ AI فعال نیست", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def strategy_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("📊 استراتژی معاملاتی با AI...")
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ui.calculate_all(df)
    ai_strat = await ai.trading_strategy(symbol, ind, t['last'])
    
    if ai_strat:
        await q.edit_message_text(f"{fmt.header()}📊 *استراتژی {symbol.replace('/USDT','')}*\n\n{ai_strat}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data=f"strat_{symbol}"), InlineKeyboardButton("🔙", callback_data="back")]]))
    else:
        await q.edit_message_text("❌ AI فعال نیست", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def experience_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    exp = trader.experience
    txt = f"""
{fmt.header()}
🧠 *تجربه و یادگیری ربات*

📊 *آمار معاملات:*
• کل: {exp['total_trades']} | برد: {exp['wins']} | باخت: {exp['losses']}
• بهترین: ${exp['best_trade']:+,.2f}
• بدترین: ${exp['worst_trade']:+,.2f}
• میانگین برد: ${exp['avg_win']:+,.2f}
• میانگین باخت: ${exp['avg_loss']:+,.2f}

⚙️ *تنظیمات خودکار:*
• آستانه اطمینان: {exp['confidence_threshold']}%
• ضریب ریسک: {exp['risk_multiplier']:.1f}x

💡 *یادگیری:*
ربات از {exp['total_trades']} معامله قبلی تجربه کسب کرده
و پارامترهای معاملاتی را بهینه کرده است.

━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606 | {dtm.now_str()}"""
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="exp"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def trade_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str):
    q = update.callback_query
    await q.answer()
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None: await q.answer("❌"); return
    
    ind = ui.calculate_all(df)
    sig, conf, _ = sg.generate(ind, t['last'])
    
    atr = ind['ATR_14']
    sl = t['last'] - atr * cfg.atr_sl
    tp = t['last'] + atr * cfg.atr_tp
    
    r = trader.open(symbol, t['last'], sl, tp, conf)
    if r:
        await q.edit_message_text(
            f"{fmt.header()}🤖 *باز شد*\n📊 {symbol}\n💰 ${t['last']:,.4f}\n🛑 ${sl:,.4f}\n🎯 ${tp:,.4f}\n🧠 تجربه: {trader.experience['confidence_threshold']}% آستانه",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
    else:
        await q.answer("⚠️ شرایط فراهم نیست", show_alert=True)

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
        elif d.startswith("s_"): await full_signal_handler(update, ctx, d[2:])
        elif d.startswith("ai_"): await full_signal_handler(update, ctx, d[3:] if len(d)>3 else "BTC/USDT")
        elif d == "market_ai": await market_ai_handler(update, ctx)
        elif d.startswith("strat_"): await strategy_handler(update, ctx, d[6:] if len(d)>6 else "BTC/USDT")
        elif d.startswith("pred_"): await full_signal_handler(update, ctx, d[5:] if len(d)>5 else "BTC/USDT")
        elif d.startswith("sent_"): await full_signal_handler(update, ctx, d[5:] if len(d)>5 else "BTC/USDT")
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
            for i, r in enumerate(res[:15], 1):
                e = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
                txt += f"{i}. {e} {r['symbol'].replace('/USDT','')}: ${r['price']:,.4f} | {r['signal'][:12]} | {r['confidence']}%\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="scan"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "tech": await q.edit_message_text("📈 *انتخاب:*", parse_mode="Markdown", reply_markup=Menu.technical())
        elif d.startswith("trade_"): await trade_handler(update, ctx, d[6:])
        elif d == "port":
            stats = trader.get_stats()
            txt = f"{fmt.header()}💰 *پورتفوی*\n💵 ${stats['balance']:,.2f}\n📈 PnL: ${stats['pnl']:+,.2f}\n📊 پوزیشن: {len(trader.positions)}\n📋 {stats['total']} | برد: {stats['wins']} ({stats['win_rate']:.0f}%)"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "exp": await experience_handler(update, ctx)
        elif d == "perf":
            stats = trader.get_stats()
            await q.edit_message_text(f"{fmt.header()}📊 *عملکرد*\n💰 ${stats['balance']:,.2f}\n📈 PnL: ${stats['pnl']:+,.2f}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "auto":
            await q.edit_message_text(f"🤖 *خودکار*\n🎮 دمو: {'✅' if cfg.demo_trading else '❌'}\n💹 واقعی: {'✅' if cfg.real_trading else '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"دمو: {'✅' if cfg.demo_trading else '❌'}", callback_data="td"), InlineKeyboardButton(f"واقعی: {'✅' if cfg.real_trading else '❌'}", callback_data="tr"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "td": cfg.demo_trading = not cfg.demo_trading
        elif d == "tr":
            if exchange_mgr.read_only: await q.answer("❌ API نیست"); return
            cfg.real_trading = not cfg.real_trading
        elif d == "set":
            await q.edit_message_text(f"{fmt.header()}⚙️ *تنظیمات*\n🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'}\n🧠 AI: {'✅' if ai.enabled else '❌'}\n📢 کانال: {cfg.channel_id or '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "edu":
            ai_content = await ai.educational_content()
            await q.edit_message_text(fmt.education_msg(ai_content), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = exchange_mgr.ticker(s)
                if t: trader.close(s, t['last'], "EMERGENCY")
            await q.edit_message_text("⏸️ بسته شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "help": await q.edit_message_text("❓ /start", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        else: await q.answer("⚡")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start", reply_markup=Menu.main())

async def error_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {ctx.error}")
    if isinstance(ctx.error, Conflict): ProcessLock.release(); sys.exit(1)

# ============================================================
# AUTO TASKS - دقیقاً هر ۱۰ دقیقه با مصرف 8000 TPM
# ============================================================
async def auto_signals_loop(app: Application):
    """
    چرخه ۱۰ دقیقه‌ای با مصرف دقیق 8000 TPM:
    - 7 سیگنال (BTC,ETH,SOL,BNB,XRP,ADA,DOGE) = 7 × 650 = 4,550
    - 2 پیش‌بینی (BTC,ETH) = 2 × 450 = 900
    - 1 تحلیل بازار = 500
    - 1 استراتژی (BTC) = 500
    - 1 احساسات (BTC) = 350
    - 1 فاندامنتال (BTC) = 500
    - 1 پرایس اکشن (BTC) = 500
    مجموع: 4,550 + 900 + 500 + 500 + 350 + 500 + 500 = 7,800 TPM
    """
    await asyncio.sleep(10)
    logger.info(f"📢 Auto Signal Loop Started (Every 10 min, Target: {token_mgr.MAX_TPM} TPM)")
    
    while True:
        try:
            if not cfg.channel_id or not cfg.auto_send:
                await asyncio.sleep(60); continue
            
            if not exchange_mgr.connected: exchange_mgr.connect()
            
            # ===== 7 سیگنال اصلی =====
            priority_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"]
            
            for sym in priority_symbols:
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 200)
                    if t and df is not None:
                        ind = ui.calculate_all(df)
                        mtf = {}
                        for tf_name, tf_val in list(cfg.timeframes.items())[:6]:
                            dft = exchange_mgr.ohlcv(sym, tf_val, 100)
                            if dft is not None: mtf[tf_name] = ui.calculate_all(dft)
                        
                        sig, conf, score = sg.generate(ind, t['last'], mtf)
                        pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                        
                        # AI برای همه ۷ ارز
                        ai_analyses = {}
                        if ai.enabled:
                            ai_analyses['tech'] = await ai.technical_analysis(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
                            if sym in ["BTC/USDT", "ETH/USDT"]:
                                ai_analyses['prediction'] = await ai.market_prediction(sym, ind, t['last'])
                        
                        analysis = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0),
                                   'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                        
                        msg = fmt.signal_msg(analysis, ai_analyses)
                        await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                        logger.info(f"📤 Signal sent: {sym}")
                        await asyncio.sleep(45)
                except Exception as e:
                    logger.error(f"Signal error for {sym}: {e}")
                    continue
            
            # ===== تحلیل‌های اضافی برای BTC =====
            if ai.enabled:
                try:
                    # استراتژی BTC
                    btc_t = exchange_mgr.ticker("BTC/USDT")
                    btc_df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
                    if btc_t and btc_df is not None:
                        btc_ind = ui.calculate_all(btc_df)
                        
                        # استراتژی
                        strat = await ai.trading_strategy("BTC/USDT", btc_ind, btc_t['last'])
                        if strat:
                            await app.bot.send_message(cfg.channel_id,
                                f"{fmt.header()}📊 *استراتژی BTC*\n\n{strat}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                                parse_mode="Markdown")
                            await asyncio.sleep(30)
                        
                        # احساسات
                        sentiment = await ai.sentiment_analysis("BTC/USDT", btc_t['last'], btc_t.get('percentage',0))
                        if sentiment:
                            await app.bot.send_message(cfg.channel_id,
                                f"{fmt.header()}💭 *احساسات بازار BTC*\n\n{sentiment}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                                parse_mode="Markdown")
                            await asyncio.sleep(30)
                        
                        # فاندامنتال
                        fundamental = await ai.fundamental_analysis("BTC/USDT", btc_t['last'], btc_t.get('percentage',0))
                        if fundamental:
                            await app.bot.send_message(cfg.channel_id,
                                f"{fmt.header()}📰 *فاندامنتال BTC*\n\n{fundamental}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                                parse_mode="Markdown")
                            await asyncio.sleep(30)
                        
                        # پرایس اکشن
                        btc_pats = [k for k,v in btc_ind.items() if isinstance(v,bool) and v]
                        pa = await ai.price_action_analysis("BTC/USDT", btc_ind, btc_t['last'], btc_pats)
                        if pa:
                            await app.bot.send_message(cfg.channel_id,
                                f"{fmt.header()}📊 *پرایس اکشن BTC*\n\n{pa}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                                parse_mode="Markdown")
                            await asyncio.sleep(30)
                except Exception as e:
                    logger.error(f"BTC extra analysis error: {e}")
            
            # ===== تحلیل بازار =====
            if ai.enabled:
                try:
                    top = []
                    for sym in cfg.symbols[:15]:
                        t = exchange_mgr.ticker(sym)
                        if t: top.append({'symbol': sym.replace('/USDT',''), 'price': t['last'], 'change': t.get('percentage',0)})
                    
                    market = await ai.market_overview(top)
                    if market:
                        await app.bot.send_message(cfg.channel_id,
                            f"{fmt.header()}📰 *تحلیل بازار*\n\n{market}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
                            parse_mode="Markdown")
                except Exception as e:
                    logger.error(f"Market overview error: {e}")
            
            # بررسی پوزیشن‌ها
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
                except Exception as e:
                    logger.error(f"Position check error: {e}")
            
            # گزارش مصرف TPM
            stats = token_mgr.get_stats()
            logger.info(f"✅ Cycle done | TPM: {stats['current']}/{stats['max']} ({stats['pct']:.0f}%) | Requests: {stats['today_requests']}")
            
        except Exception as e:
            logger.error(f"Auto signal loop error: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education_loop(app: Application):
    """ارسال محتوای آموزشی هر ۱۰ دقیقه"""
    await asyncio.sleep(30)
    logger.info("📚 Auto Education Loop Started (Every 10 minutes)")
    
    while True:
        try:
            if cfg.channel_id and cfg.auto_send and ai.enabled:
                ai_content = await ai.educational_content()
                if ai_content:
                    msg = fmt.education_msg(ai_content)
                    await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                    logger.info("📚 Educational content sent")
        except Exception as e:
            logger.error(f"Education error: {e}")
        await asyncio.sleep(cfg.education_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token:
        logger.critical("❌ No token!"); ProcessLock.release(); return
    
    exchange_mgr.connect()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(error_handler)
    
    asyncio.create_task(auto_signals_loop(app))
    asyncio.create_task(auto_education_loop(app))
    
    logger.info("="*70)
    logger.info("🚀 CRYPTO PULSE ULTIMATE v8.0 - THE FINAL BOSS")
    logger.info(f"🧠 Groq AI: {'✅ Llama 3.3 70B' if ai.enabled else '❌'} | EXACTLY {token_mgr.MAX_TPM} TPM")
    logger.info(f"📊 7 EMA Types + 25+ Indicators")
    logger.info(f"⏰ 11 Timeframes | 30 Coins")
    logger.info(f"📢 Auto Signals + Education Every 10 Minutes")
    logger.info(f"🎓 Self-Learning Engine Active")
    logger.info(f"📅 {dtm.now_persian()}")
    logger.info("="*70)
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Conflict: logger.critical("❌ Conflict!")
    except Exception as e: logger.critical(f"❌ {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: ProcessLock.release()
    except Exception as e: logger.critical(f"Fatal: {e}"); ProcessLock.release()
