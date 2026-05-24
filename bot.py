#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║     CRYPTO PULSE ULTIMATE AI TRADING BOT v7.0                   ║
║     Groq AI | 25+ Indicators | Auto Signals Every 10 Min        ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os, sys, logging, asyncio, time, json, random, signal
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

load_dotenv()

# ============================================================
# PROFESSIONAL LOGGING SYSTEM
# ============================================================
logger = logging.getLogger('CryptoPulseUltimate')
logger.setLevel(logging.DEBUG)

# Console Handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)

# File Handlers
for name, level, fmt in [
    ('crypto_main.log', logging.INFO, '%(asctime)s | %(levelname)-7s | %(message)s'),
    ('crypto_debug.log', logging.DEBUG, '%(asctime)s | %(levelname)-7s | %(name)s | %(funcName)s | %(message)s'),
    ('crypto_errors.log', logging.ERROR, '%(asctime)s | %(levelname)-7s | %(message)s')
]:
    handler = RotatingFileHandler(name, maxBytes=10*1024*1024, backupCount=7, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)

# Silence noisy libraries
for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'urllib3', 'asyncio', 'aiohttp']:
    logging.getLogger(lib).setLevel(logging.WARNING)

logger.info("="*60)
logger.info("🚀 CRYPTO PULSE ULTIMATE v7.0 INITIALIZING")
logger.info("="*60)

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
    
    # 11 Timeframes for Analysis
    timeframes: Dict[str, str] = field(default_factory=lambda: {
        "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "2h": "2h", "4h": "4h",
        "6h": "6h", "12h": "12h", "1d": "1d",
        "3d": "3d", "1w": "1w"
    })
    
    # Trading Parameters
    initial_balance: float = 100000.0
    risk_per_trade: float = 0.02
    max_positions: int = 5
    atr_sl: float = 2.0
    atr_tp: float = 4.0
    trailing_pct: float = 0.03
    max_consecutive_losses: int = 5
    
    # Trading Modes
    demo_trading: bool = True
    real_trading: bool = False
    auto_send: bool = True
    
    # Intervals
    signal_interval: int = 600  # 10 دقیقه
    education_interval: int = 3600  # 1 ساعت

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_ultimate.lock"
    
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
# GROQ AI - تحلیل تکنیکال + فاندامنتال + پرایس اکشن
# ============================================================
class GroqAIEngine:
    """Ultimate AI Analysis Engine"""
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self.client = httpx.AsyncClient(timeout=45.0)
        if self.enabled:
            logger.info("🧠 Groq AI Engine Connected (Llama 3.3 70B)")
        else:
            logger.warning("⚠️ Groq AI Disabled - Set GROQ_API_KEY in .env")
    
    async def technical_analysis(self, symbol: str, indicators: Dict, price: float, 
                                  change: float, patterns: List[str], mtf_data: Dict) -> Optional[str]:
        """تحلیل تکنیکال عمیق با AI"""
        if not self.enabled:
            return None
        
        mtf_text = ""
        for tf, ind in mtf_data.items():
            mtf_text += f"{tf}: RSI={ind.get('RSI_14',50):.0f} | MACD={'Bullish' if ind.get('MACD_HIST',0)>0 else 'Bearish'} | ADX={ind.get('ADX',20):.0f}\n"
        
        prompt = f"""You are a world-class technical analyst. Analyze this cryptocurrency with precision:

SYMBOL: {symbol}
PRICE: ${price:,.4f} | 24h CHANGE: {change:+.2f}%

=== 25+ TECHNICAL INDICATORS ===
RSI(7): {indicators.get('RSI_7',50):.1f}
RSI(14): {indicators.get('RSI_14',50):.1f}
RSI(21): {indicators.get('RSI_21',50):.1f}
MACD Histogram: {indicators.get('MACD_HIST',0):.4f}
MACD Signal: {indicators.get('MACD_SIG',0):.4f}
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
Ultimate Oscillator: {indicators.get('ULTIMATE',50):.1f}
ROC(12): {indicators.get('ROC',0):.2f}
TRIX: {indicators.get('TRIX',0):.4f}
Volume Ratio: {indicators.get('VOL_RATIO',1):.2f}x
Trend Strength: {indicators.get('TREND_STR',0):.1f}%
Volatility: {indicators.get('VOLATILITY',0):.2f}%
EMA Crossover: {'Bullish' if indicators.get('EMA_7',0) > indicators.get('EMA_20',0) else 'Bearish'}
Ichimoku: {'Bullish' if price > indicators.get('ICH_SENKOU_A',0) else 'Bearish'}
Parabolic SAR: {'Bullish' if indicators.get('PSAR_DIR',0) > 0 else 'Bearish'}
Vortex: {'Bullish' if indicators.get('VORTEX+',0) > indicators.get('VORTEX-',0) else 'Bearish'}
Aroon: {'Bullish' if indicators.get('AROON_UP',0) > indicators.get('AROON_DOWN',0) else 'Bearish'}

=== CANDLESTICK PATTERNS ===
Detected: {', '.join(patterns) if patterns else 'None'}

=== DIVERGENCE ===
{indicators.get('DIVERGENCE', 'NONE')}

=== MULTI-TIMEFRAME ANALYSIS ===
{mtf_text}

=== SUPPORT/RESISTANCE ===
Resistance: ${indicators.get('RESISTANCE',0):.2f}
Pivot: ${indicators.get('PIVOT',0):.2f}
Support: ${indicators.get('SUPPORT',0):.2f}
Fibonacci 0.618: ${indicators.get('FIB_618',0):.2f}

Provide in Persian (فارسی):
1. Technical Analysis Summary (3 lines)
2. Key Support/Resistance Levels
3. Momentum & Volume Analysis
4. Candlestick Pattern Interpretation
5. Multi-Timeframe Confluence
6. SHORT-TERM Prediction (next 4-12 hours)
7. MEDIUM-TERM Prediction (next 1-3 days)
8. Entry/Exit Suggestions with Price Levels
9. Risk Level (LOW/MEDIUM/HIGH/EXTREME)
10. Confidence Score (0-100%)

Use emojis. Be specific with price levels. Max 400 words."""
        
        return await self._call_api(prompt)
    
    async def fundamental_analysis(self, symbol: str, price: float, change: float) -> Optional[str]:
        """تحلیل فاندامنتال با AI"""
        if not self.enabled:
            return None
        
        coin = symbol.replace('/USDT', '')
        
        prompt = f"""You are a crypto fundamental analyst. Analyze {coin}:

Current Price: ${price:,.4f}
24h Change: {change:+.2f}%

Provide in Persian (فارسی):
1. Market Sentiment & Overall Outlook
2. Key Fundamental Factors (adoption, development, partnerships)
3. Market Cap & Volume Analysis
4. Correlation with BTC
5. Upcoming Events/Catalysts
6. Institutional Interest
7. On-Chain Metrics (if known)
8. Long-Term Potential (3-6 months)
9. Risk Factors
10. Overall Fundamental Rating (1-10)

Use emojis. Be concise. Max 300 words."""
        
        return await self._call_api(prompt)
    
    async def price_action_analysis(self, symbol: str, indicators: Dict, price: float, patterns: List[str]) -> Optional[str]:
        """تحلیل پرایس اکشن با AI"""
        if not self.enabled:
            return None
        
        prompt = f"""You are a professional price action trader. Analyze {symbol} at ${price:,.4f}:

Candlestick Patterns: {', '.join(patterns) if patterns else 'None detected'}
BB Position: {indicators.get('BB_PCT',0.5):.2f} (0=Lower, 1=Upper)
Volume Ratio: {indicators.get('VOL_RATIO',1):.2f}x
ATR%: {indicators.get('ATR_PCT',0):.2f}%
Divergence: {indicators.get('DIVERGENCE','NONE')}

Provide in Persian (فارسی):
1. Market Structure (Trending/Ranging/Reversing)
2. Key Support/Resistance Zones
3. Supply/Demand Zones
4. Candlestick Pattern Analysis
5. Breakout/Fakeout Probability
6. Order Flow Analysis
7. Key Levels to Watch
8. Best Entry Strategy
9. Stop Loss Placement
10. Take Profit Targets

Use emojis. Be specific. Max 300 words."""
        
        return await self._call_api(prompt)
    
    async def _call_api(self, prompt: str) -> Optional[str]:
        """Call Groq API"""
        try:
            response = await self.client.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {cfg.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.MODEL,
                    "messages": [{"role": "system", "content": "You are an elite crypto analyst. Respond only in Persian (فارسی)."}, 
                                 {"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.6
                }
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            logger.error(f"Groq API Error: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Groq Error: {e}")
            return None

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
            logger.info(f"✅ Exchange: {'FULL' if not self.read_only else 'READ-ONLY'} | {len(self._ex.markets)} markets")
            return True
        except Exception as e:
            logger.error(f"❌ Exchange: {e}")
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
# 25+ TECHNICAL INDICATORS & OSCILLATORS
# ============================================================
class TechnicalIndicators:
    """Complete Technical Analysis Suite - 25+ Indicators"""
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Dict[str, Any]:
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        open_ = df['open'].astype(float)
        
        ind = {}
        
        # ===== 1-3. MOVING AVERAGES =====
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
            ind[f'SMA_{p}'] = float(close.rolling(p).mean().iloc[-1])
            if p <= 50 and p <= len(close):
                weights = np.arange(1, p+1)
                ind[f'WMA_{p}'] = float(np.average(close.iloc[-p:], weights=weights))
        
        # ===== 4-6. RSI MULTIPLE =====
        from ta.momentum import RSIIndicator
        for p in [7, 14, 21]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close, window=p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        
        # ===== 7. MACD COMPLETE =====
        from ta.trend import MACD
        try:
            macd = MACD(close, 12, 26, 9)
            ind['MACD_LINE'] = float(macd.macd().iloc[-1])
            ind['MACD_SIG'] = float(macd.macd_signal().iloc[-1])
            ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except: ind['MACD_LINE'] = ind['MACD_SIG'] = ind['MACD_HIST'] = 0.0
        
        # ===== 8. STOCHASTIC =====
        from ta.momentum import StochasticOscillator
        try:
            stoch = StochasticOscillator(high, low, close, 14, 3)
            ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
            ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        except: ind['STOCH_K'] = ind['STOCH_D'] = 50.0
        
        # ===== 9. BOLLINGER BANDS =====
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
        
        # ===== 10. KELTNER CHANNEL =====
        from ta.volatility import KeltnerChannel
        try:
            kc = KeltnerChannel(high, low, close, 20)
            ind['KC_UPPER'] = float(kc.keltner_channel_hband().iloc[-1])
            ind['KC_LOWER'] = float(kc.keltner_channel_lband().iloc[-1])
        except: ind['KC_UPPER'] = ind['KC_LOWER'] = close.iloc[-1]
        
        # ===== 11. DONCHIAN CHANNEL =====
        from ta.volatility import DonchianChannel
        try:
            dc = DonchianChannel(high, low, close, 20)
            ind['DC_UPPER'] = float(dc.donchian_channel_hband().iloc[-1])
            ind['DC_LOWER'] = float(dc.donchian_channel_lband().iloc[-1])
        except: ind['DC_UPPER'] = ind['DC_LOWER'] = close.iloc[-1]
        
        # ===== 12. ATR =====
        from ta.volatility import AverageTrueRange
        for p in [7, 14]:
            try: ind[f'ATR_{p}'] = float(AverageTrueRange(high, low, close, p).average_true_range().iloc[-1])
            except: ind[f'ATR_{p}'] = close.iloc[-1] * 0.01
        ind['ATR_PCT'] = float(ind['ATR_14'] / close.iloc[-1] * 100)
        
        # ===== 13. ADX + DI =====
        from ta.trend import ADXIndicator
        try:
            adx = ADXIndicator(high, low, close, 14)
            ind['ADX'] = float(adx.adx().iloc[-1])
            ind['DI+'] = float(adx.adx_pos().iloc[-1])
            ind['DI-'] = float(adx.adx_neg().iloc[-1])
        except: ind['ADX'] = 20.0; ind['DI+'] = ind['DI-'] = 20.0
        
        # ===== 14. CCI =====
        from ta.trend import CCIIndicator
        try: ind['CCI'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        
        # ===== 15. ICHIMOKU CLOUD =====
        from ta.trend import IchimokuIndicator
        try:
            ichi = IchimokuIndicator(high, low, 9, 26, 52)
            ind['ICH_TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1])
            ind['ICH_KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
            ind['ICH_SENKOU_A'] = float(ichi.ichimoku_a().iloc[-1])
            ind['ICH_SENKOU_B'] = float(ichi.ichimoku_b().iloc[-1])
        except:
            ind['ICH_TENKAN'] = ind['ICH_KIJUN'] = ind['ICH_SENKOU_A'] = ind['ICH_SENKOU_B'] = close.iloc[-1]
        
        # ===== 16. PARABOLIC SAR =====
        from ta.trend import PSARIndicator
        try:
            psar = PSARIndicator(high, low, close)
            ind['PSAR'] = float(psar.psar().iloc[-1])
            ind['PSAR_DIR'] = 1 if close.iloc[-1] > ind['PSAR'] else -1
        except: ind['PSAR'] = close.iloc[-1]; ind['PSAR_DIR'] = 0
        
        # ===== 17. WILLIAMS %R =====
        from ta.momentum import WilliamsRIndicator
        try: ind['WILLIAMS_R'] = float(WilliamsRIndicator(high, low, close, 14).williams_r().iloc[-1])
        except: ind['WILLIAMS_R'] = -50.0
        
        # ===== 18. ULTIMATE OSCILLATOR =====
        from ta.momentum import UltimateOscillator
        try: ind['ULTIMATE'] = float(UltimateOscillator(high, low, close).ultimate_oscillator().iloc[-1])
        except: ind['ULTIMATE'] = 50.0
        
        # ===== 19. ROC =====
        from ta.momentum import ROCIndicator
        try: ind['ROC'] = float(ROCIndicator(close, 12).roc().iloc[-1])
        except: ind['ROC'] = 0.0
        
        # ===== 20. AWESOME OSCILLATOR =====
        from ta.momentum import AwesomeOscillatorIndicator
        try: ind['AO'] = float(AwesomeOscillatorIndicator(high, low).awesome_oscillator().iloc[-1])
        except: ind['AO'] = 0.0
        
        # ===== 21. MFI =====
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high, low, close, volume, 14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        
        # ===== 22. OBV =====
        from ta.volume import OnBalanceVolumeIndicator
        try: ind['OBV'] = float(OnBalanceVolumeIndicator(close, volume).on_balance_volume().iloc[-1])
        except: ind['OBV'] = 0.0
        
        # ===== 23. AROON =====
        from ta.trend import AroonIndicator
        try:
            aroon = AroonIndicator(close, 25)
            ind['AROON_UP'] = float(aroon.aroon_up().iloc[-1])
            ind['AROON_DOWN'] = float(aroon.aroon_down().iloc[-1])
        except: ind['AROON_UP'] = ind['AROON_DOWN'] = 50.0
        
        # ===== 24. VORTEX =====
        from ta.trend import VortexIndicator
        try:
            vortex = VortexIndicator(high, low, close, 14)
            ind['VORTEX+'] = float(vortex.vortex_indicator_pos().iloc[-1])
            ind['VORTEX-'] = float(vortex.vortex_indicator_neg().iloc[-1])
        except: ind['VORTEX+'] = ind['VORTEX-'] = 1.0
        
        # ===== 25. TRIX =====
        from ta.trend import TRIXIndicator
        try: ind['TRIX'] = float(TRIXIndicator(close, 15).trix().iloc[-1])
        except: ind['TRIX'] = 0.0
        
        # ===== VOLUME ANALYSIS =====
        vol_sma = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else volume.iloc[-1]
        ind['VOL_RATIO'] = float(volume.iloc[-1] / vol_sma if vol_sma > 0 else 1)
        
        # ===== MARKET METRICS =====
        ind['TREND_STR'] = float((close.iloc[-1] - close.iloc[-50]) / close.iloc[-50] * 100) if len(close) >= 50 else 0
        ind['VOLATILITY'] = float(close.pct_change().rolling(14).std().iloc[-1] * 100)
        ind['MOMENTUM'] = float(close.iloc[-1] - close.iloc[-10]) if len(close) >= 10 else 0
        
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
        ind.update(TechnicalIndicators.detect_candles(df))
        
        # ===== DIVERGENCE =====
        ind['DIVERGENCE'] = TechnicalIndicators.detect_divergence(close)
        
        return ind
    
    @staticmethod
    def detect_candles(df: pd.DataFrame) -> Dict[str, bool]:
        patterns = {p: False for p in [
            'DOJI', 'HAMMER', 'SHOOTING_STAR', 'ENGULFING_BULL', 'ENGULFING_BEAR',
            'MORNING_STAR', 'EVENING_STAR', 'THREE_WHITE_SOLDIERS', 'THREE_BLACK_CROWS',
            'HARAMI_BULL', 'HARAMI_BEAR', 'PIERCING_LINE', 'DARK_CLOUD_COVER',
            'MARUBOZU_BULL', 'MARUBOZU_BEAR', 'SPINNING_TOP', 'HANGING_MAN',
            'INVERTED_HAMMER', 'TWEEZER_TOP', 'TWEEZER_BOTTOM'
        ]}
        
        if len(df) < 3:
            return patterns
        
        o = df['open'].iloc[-1]; h = df['high'].iloc[-1]
        l = df['low'].iloc[-1]; c = df['close'].iloc[-1]
        po = df['open'].iloc[-2]; ph = df['high'].iloc[-2]
        pl = df['low'].iloc[-2]; pc = df['close'].iloc[-2]
        
        body = abs(c - o)
        upper = h - max(c, o)
        lower = min(c, o) - l
        total_range = h - l
        
        if total_range == 0:
            return patterns
        
        # Doji
        patterns['DOJI'] = body <= total_range * 0.08
        # Spinning Top
        patterns['SPINNING_TOP'] = 0.08 < body <= total_range * 0.3 and upper > body * 0.3 and lower > body * 0.3
        # Hammer
        patterns['HAMMER'] = lower > body * 2 and upper < body * 0.5 and c > o
        # Hanging Man
        patterns['HANGING_MAN'] = lower > body * 2 and upper < body * 0.5 and c < o
        # Shooting Star
        patterns['SHOOTING_STAR'] = upper > body * 2 and lower < body * 0.5 and c < o
        # Inverted Hammer
        patterns['INVERTED_HAMMER'] = upper > body * 2 and lower < body * 0.5 and c > o
        # Engulfing
        patterns['ENGULFING_BULL'] = c > o and pc < po and o <= pc and c >= po
        patterns['ENGULFING_BEAR'] = c < o and pc > po and o >= pc and c <= po
        # Marubozu
        patterns['MARUBOZU_BULL'] = c > o and upper < body * 0.1 and lower < body * 0.1
        patterns['MARUBOZU_BEAR'] = c < o and upper < body * 0.1 and lower < body * 0.1
        # Piercing Line
        patterns['PIERCING_LINE'] = pc < po and c > o and o < pl and c > (po + pc) / 2
        # Dark Cloud Cover
        patterns['DARK_CLOUD_COVER'] = pc > po and c < o and o > ph and c < (po + pc) / 2
        
        if len(df) >= 3:
            o3 = df['open'].iloc[-3]; c3 = df['close'].iloc[-3]
            # Morning Star
            patterns['MORNING_STAR'] = pc < po and abs(df['close'].iloc[-2] - df['open'].iloc[-2]) < body * 0.3 and c > o
            # Evening Star
            patterns['EVENING_STAR'] = pc > po and abs(df['close'].iloc[-2] - df['open'].iloc[-2]) < body * 0.3 and c < o
            # Three White Soldiers
            patterns['THREE_WHITE_SOLDIERS'] = c > o and pc > po and c3 > o3 and c > pc > c3
            # Three Black Crows
            patterns['THREE_BLACK_CROWS'] = c < o and pc < po and c3 < o3 and c < pc < c3
        
        return patterns
    
    @staticmethod
    def detect_divergence(price: pd.Series) -> str:
        if len(price) < 20:
            return "NONE"
        from ta.momentum import RSIIndicator
        rsi_series = RSIIndicator(price, 14).rsi()
        rp = price.iloc[-20:]
        rr = rsi_series.iloc[-20:]
        
        if rp.iloc[-1] < rp.min() and rr.iloc[-1] > rr.min():
            return "BULLISH_DIVERGENCE"
        if rp.iloc[-1] > rp.max() and rr.iloc[-1] < rr.max():
            return "BEARISH_DIVERGENCE"
        if rp.iloc[-1] > rp.min() and rr.iloc[-1] < rr.min():
            return "HIDDEN_BULLISH"
        if rp.iloc[-1] < rp.max() and rr.iloc[-1] > rr.max():
            return "HIDDEN_BEARISH"
        return "NONE"

ti = TechnicalIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGenerator:
    @staticmethod
    def generate(ind: Dict, price: float, mtf: Dict = None) -> Tuple[str, int, int]:
        score = 0
        
        # EMA Crossover
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50'] > ind['EMA_200']: score += 200
        elif ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']: score += 130
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50'] < ind['EMA_200']: score -= 200
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']: score -= 130
        
        # Ichimoku
        if price > ind['ICH_SENKOU_A'] and price > ind['ICH_SENKOU_B']:
            score += 80 if ind['ICH_TENKAN'] > ind['ICH_KIJUN'] else 40
        elif price < ind['ICH_SENKOU_A'] and price < ind['ICH_SENKOU_B']:
            score -= 80 if ind['ICH_TENKAN'] < ind['ICH_KIJUN'] else 40
        
        # RSI
        rsi = ind['RSI_14']
        if rsi < 25: score += 120
        elif rsi < 35: score += 70
        elif rsi < 45: score += 30
        elif rsi > 75: score -= 120
        elif rsi > 65: score -= 70
        elif rsi > 55: score -= 30
        
        # MACD
        if ind['MACD_HIST'] > 0: score += 70
        else: score -= 70
        
        # Stochastic
        if ind['STOCH_K'] < 20 and ind['STOCH_D'] < 20: score += 80
        elif ind['STOCH_K'] > 80 and ind['STOCH_D'] > 80: score -= 80
        
        # CCI
        cci = ind['CCI']
        if cci < -200: score += 70
        elif cci < -100: score += 40
        elif cci > 200: score -= 70
        elif cci > 100: score -= 40
        
        # Bollinger
        if ind['BB_PCT'] < 0.1: score += 100
        elif ind['BB_PCT'] > 0.9: score -= 100
        
        # ATR Volatility
        if ind['ATR_PCT'] > 5: score += 40
        
        # Volume
        if ind['VOL_RATIO'] > 2.5: score += 60 if score > 0 else -60
        elif ind['VOL_RATIO'] > 1.5: score += 40 if score > 0 else -40
        
        # MFI
        if ind['MFI'] < 20: score += 60
        elif ind['MFI'] > 80: score -= 60
        
        # Williams %R
        if ind['WILLIAMS_R'] < -80: score += 50
        elif ind['WILLIAMS_R'] > -20: score -= 50
        
        # ADX
        if ind['ADX'] > 25 and ind['DI+'] > ind['DI-']: score += 50
        elif ind['ADX'] > 25 and ind['DI-'] > ind['DI+']: score -= 50
        
        # Candles
        if ind.get('ENGULFING_BULL'): score += 80
        if ind.get('HAMMER'): score += 50
        if ind.get('MORNING_STAR'): score += 60
        if ind.get('THREE_WHITE_SOLDIERS'): score += 60
        if ind.get('PIERCING_LINE'): score += 50
        if ind.get('MARUBOZU_BULL'): score += 40
        if ind.get('ENGULFING_BEAR'): score -= 80
        if ind.get('SHOOTING_STAR'): score -= 50
        if ind.get('EVENING_STAR'): score -= 60
        if ind.get('THREE_BLACK_CROWS'): score -= 60
        if ind.get('DARK_CLOUD_COVER'): score -= 50
        if ind.get('MARUBOZU_BEAR'): score -= 40
        
        # Divergence
        div = ind.get('DIVERGENCE', 'NONE')
        if div == 'BULLISH_DIVERGENCE': score += 70
        elif div == 'BEARISH_DIVERGENCE': score -= 70
        elif div == 'HIDDEN_BULLISH': score += 40
        elif div == 'HIDDEN_BEARISH': score -= 40
        
        # MTF
        if mtf:
            for tf, ti_data in mtf.items():
                w = {"5m": 0.3, "15m": 0.5, "30m": 0.7, "1h": 1.0, "2h": 1.2, "4h": 1.5, "6h": 1.8, "12h": 2.0, "1d": 2.5, "3d": 3.0, "1w": 4.0}.get(tf, 0.5)
                if ti_data.get('RSI_14', 50) > 55: score += int(25 * w)
                elif ti_data.get('RSI_14', 50) < 45: score -= int(25 * w)
                if ti_data.get('MACD_HIST', 0) > 0: score += int(18 * w)
                else: score -= int(18 * w)
        
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
# TRADING ENGINE
# ============================================================
class TradingEngine:
    def __init__(self):
        self.balance = cfg.initial_balance
        self.positions: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self.consecutive_losses = 0
        self.load()
    
    def load(self):
        try:
            with open('trades_v7.json', 'r') as f:
                d = json.load(f)
                self.balance = d.get('balance', cfg.initial_balance)
                self.history = d.get('history', [])
        except: pass
    
    def save(self):
        try:
            with open('trades_v7.json', 'w') as f:
                json.dump({'balance': self.balance, 'history': self.history[-500:]}, f)
        except: pass
    
    def calc_size(self, entry: float, sl: float, conf: int) -> float:
        risk = self.balance * cfg.risk_per_trade
        if conf >= 90: risk *= 1.5
        elif conf >= 80: risk *= 1.2
        elif conf < 65: risk *= 0.5
        if self.consecutive_losses > 0: risk *= (0.5 ** self.consecutive_losses)
        pr = abs(entry - sl)
        return min(risk/pr, self.balance*0.25/entry) if pr > 0 else 0
    
    def open(self, symbol: str, entry: float, sl: float, tp: float, conf: int) -> Optional[Dict]:
        if len(self.positions) >= cfg.max_positions: return None
        if self.consecutive_losses >= cfg.max_consecutive_losses: return None
        sz = self.calc_size(entry, sl, conf)
        if sz <= 0 or sz*entry > self.balance: return None
        self.balance -= sz * entry
        pos = {'symbol': symbol, 'size': sz, 'entry': entry, 'sl': sl, 'tp': tp, 'high': entry, 'time': datetime.now(), 'conf': conf}
        self.positions[symbol] = pos
        self.save()
        logger.info(f"🔵 OPEN {symbol} | {sz:.4f} @ {entry:.2f}")
        return pos
    
    def update(self, symbol: str, price: float, atr: float) -> Optional[Dict]:
        if symbol not in self.positions: return None
        p = self.positions[symbol]
        p['high'] = max(p['high'], price)
        if (price-p['entry'])/p['entry'] > cfg.trailing_pct:
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
        self.save()
        logger.info(f"{'🟢' if pnl>0 else '🔴'} CLOSE {symbol} | ${pnl:+.2f} | {reason}")
        return t

trader = TradingEngine()

# ============================================================
# CACHE
# ============================================================
class Cache:
    _d: Dict[str, Tuple[Any, float]] = {}
    @classmethod
    def get(cls, k: str, ttl: float = 15) -> Optional[Any]:
        if k in cls._d:
            v, ts = cls._d[k]
            if time.time() - ts < ttl: return v
            del cls._d[k]
        return None
    @classmethod
    def set(cls, k: str, v: Any): cls._d[k] = (v, time.time())

# ============================================================
# FORMATTER
# ============================================================
class Formatter:
    @staticmethod
    def signal_msg(analysis: Dict, ai_tech: str = None, ai_fund: str = None, ai_pa: str = None) -> str:
        s = analysis['symbol'].replace('/USDT','')
        i = analysis['indicators']
        pats = [k.replace('_',' ') for k,v in i.items() if isinstance(v,bool) and v]
        
        msg = f"""
╔══════════════════════════════════════════════╗
║       🔥 سیگنال {s} 🔥                  ║
╚══════════════════════════════════════════════╝

💰 قیمت: ${analysis['price']:,.4f}
📊 تغییر: {analysis['change']:+.2f}%

🎯 *سیگنال:* {analysis['signal']}
💪 اطمینان: {analysis['confidence']}% | امتیاز: {analysis['score']}/1000

📈 *اندیکاتورها:*
• RSI(14): {i['RSI_14']:.1f} | RSI(7): {i['RSI_7']:.1f}
• MACD: {'صعودی' if i['MACD_HIST']>0 else 'نزولی'}
• ADX: {i['ADX']:.1f} | DI+: {i['DI+']:.1f} | DI-: {i['DI-']:.1f}
• CCI: {i['CCI']:.1f} | MFI: {i['MFI']:.1f}
• Stoch K: {i['STOCH_K']:.1f} | Stoch D: {i['STOCH_D']:.1f}
• ATR: {i['ATR_14']:.4f} | Vol: {i['VOL_RATIO']:.1f}x
• BB Width: {i['BB_WIDTH']:.4f} | %B: {i['BB_PCT']:.2f}
• Williams %R: {i['WILLIAMS_R']:.1f}

🕯️ *الگوها:* {', '.join(pats) if pats else 'بدون الگو'}
🔄 *واگرایی:* {i.get('DIVERGENCE','NONE')}

🔑 *سطوح:*
• مقاومت: ${i['RESISTANCE']:,.4f} | R1: ${i['R1']:,.4f}
• پیوت: ${i['PIVOT']:,.4f}
• حمایت: ${i['SUPPORT']:,.4f} | S1: ${i['S1']:,.4f}
• Fib 0.618: ${i.get('FIB_618',0):,.4f}

⚠️ حد ضرر: ${analysis['price']-i['ATR_14']*cfg.atr_sl:,.4f}
🎯 حد سود: ${analysis['price']+i['ATR_14']*cfg.atr_tp:,.4f}
📊 ریسک/ریوارد: 1:{cfg.atr_tp/cfg.atr_sl:.1f}"""
        
        if ai_tech:
            msg += f"""

🧠 *تحلیل تکنیکال AI:*
{ai_tech[:500]}..."""
        
        if ai_pa:
            msg += f"""

📊 *تحلیل پرایس اکشن AI:*
{ai_pa[:400]}..."""
        
        if ai_fund:
            msg += f"""

📰 *تحلیل فاندامنتال AI:*
{ai_fund[:300]}..."""
        
        msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✨ @CryptoPulse606"""
        
        return msg
    
    @staticmethod
    def edu_msg() -> str:
        topics = [
            "تحلیل تکنیکال", "پرایس اکشن", "فاندامنتال",
            "مدیریت ریسک", "روانشناسی بازار", "الگوهای کندلی",
            "استراتژی معاملاتی", "ایچیموکو", "فیبوناچی",
            "بولینگر باند", "مکدی", "آراس‌آی"
        ]
        return f"""
📚 *آموزش تخصصی*

📖 {random.choice(topics)}

🔍 *اصول طلایی:*
۱. روند دوست شماست
۲. ریسک/ریوارد ≥ ۱:۲
۳. حداکثر ۲٪ ریسک
۴. حد ضرر اجباری
۵. بعد ۳ ضرر استراحت
۶. ژورنال معاملاتی
۷. صبوری = سودآوری

💡 *رمز موفقیت:*
۲۰٪ استراتژی + ۳۰٪ ریسک + ۵۰٪ روانشناسی

━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606 | {datetime.now().strftime('%H:%M')}
"""

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
             InlineKeyboardButton("⏰ مولتی‌تایم", callback_data="mtf"),
             InlineKeyboardButton("🧠 AI تحلیل", callback_data="ai_BTC/USDT")],
            [InlineKeyboardButton("📰 فاندامنتال AI", callback_data="fund_BTC/USDT"),
             InlineKeyboardButton("📊 پرایس اکشن AI", callback_data="pa_BTC/USDT"),
             InlineKeyboardButton("🔮 پیش‌بینی", callback_data="pred_BTC/USDT")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf"),
             InlineKeyboardButton("📋 تاریخچه", callback_data="hist")],
            [InlineKeyboardButton("🤖 خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("🔑 وضعیت", callback_data="status")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("🕯️ الگوها", callback_data="patt"),
             InlineKeyboardButton("⏸️ توقف", callback_data="stop")],
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="ref"),
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
        "🤖 *Crypto Pulse Ultimate AI v7.0*\n\n"
        "🧠 Groq AI (Llama 3.3 70B)\n"
        "📊 ۲۵+ اندیکاتور قدرتمند\n"
        "⏰ ۱۱ تایم‌فریم | ۳۰ ارز\n"
        "📰 تحلیل تکنیکال + فاندامنتال + پرایس اکشن\n"
        "📢 سیگنال خودکار هر ۱۰ دقیقه\n\n"
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
    
    ind = ti.calculate_all(df)
    
    # MTF
    mtf = {}
    for tf_name, tf_val in cfg.timeframes.items():
        dft = exchange_mgr.ohlcv(symbol, tf_val, 100)
        if dft is not None: mtf[tf_name] = ti.calculate_all(dft)
    
    sig, conf, score = sg.generate(ind, t['last'], mtf)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    
    # AI Analyses
    ai_tech = await ai.technical_analysis(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    ai_fund = await ai.fundamental_analysis(symbol, t['last'], t.get('percentage',0))
    ai_pa = await ai.price_action_analysis(symbol, ind, t['last'], pats)
    
    analysis = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
                'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
    
    msg = fmt.signal_msg(analysis, ai_tech, ai_fund, ai_pa)
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("🧠 AI", callback_data=f"ai_{symbol}"),
            InlineKeyboardButton("🤖 معامله", callback_data=f"trade_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def ai_tech_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🧠 تحلیل تکنیکال AI برای {symbol.replace('/USDT','')}...")
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ti.calculate_all(df)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    mtf = {}
    for tf_name, tf_val in list(cfg.timeframes.items())[:6]:
        dft = exchange_mgr.ohlcv(symbol, tf_val, 100)
        if dft is not None: mtf[tf_name] = ti.calculate_all(dft)
    
    ai_tech = await ai.technical_analysis(symbol, ind, t['last'], t.get('percentage',0), pats, mtf)
    
    if ai_tech:
        await q.edit_message_text(f"🧠 *تحلیل تکنیکال AI - {symbol.replace('/USDT','')}*\n\n{ai_tech}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄", callback_data=f"ai_{symbol}"),
                InlineKeyboardButton("📊 سیگنال", callback_data=f"s_{symbol}"),
                InlineKeyboardButton("🔙", callback_data="back")
            ]]))
    else:
        await q.edit_message_text("❌ AI فعال نیست. GROQ_API_KEY را تنظیم کنید.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def ai_fundamental_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"📰 تحلیل فاندامنتال AI...")
    
    t = exchange_mgr.ticker(symbol)
    if not t:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ai_fund = await ai.fundamental_analysis(symbol, t['last'], t.get('percentage',0))
    
    if ai_fund:
        await q.edit_message_text(f"📰 *فاندامنتال AI - {symbol.replace('/USDT','')}*\n\n{ai_fund}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄", callback_data=f"fund_{symbol}"),
                InlineKeyboardButton("🔙", callback_data="back")
            ]]))
    else:
        await q.edit_message_text("❌ AI فعال نیست.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def ai_price_action_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"📊 تحلیل پرایس اکشن AI...")
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = ti.calculate_all(df)
    pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
    ai_pa = await ai.price_action_analysis(symbol, ind, t['last'], pats)
    
    if ai_pa:
        await q.edit_message_text(f"📊 *پرایس اکشن AI - {symbol.replace('/USDT','')}*\n\n{ai_pa}\n\n━━━━━━━━━━━━━━━━━━━━━━\n✨ @CryptoPulse606",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄", callback_data=f"pa_{symbol}"),
                InlineKeyboardButton("🔙", callback_data="back")
            ]]))
    else:
        await q.edit_message_text("❌ AI فعال نیست.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def prices_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🔄 دریافت...")
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    txt = "💰 *قیمت‌ها*\n\n"
    for sym in cfg.symbols[:20]:
        t = exchange_mgr.ticker(sym)
        if t:
            e = "🟢" if t.get('percentage',0)>0 else "🔴"
            txt += f"{e} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def scan_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🔍 اسکن ۳۰ ارز...")
    if not exchange_mgr.connected: exchange_mgr.connect()
    
    res = []
    for sym in cfg.symbols:
        t = exchange_mgr.ticker(sym)
        df = exchange_mgr.ohlcv(sym, '1h', 100)
        if t and df is not None:
            ind = ti.calculate_all(df)
            sig, conf, score = sg.generate(ind, t['last'])
            res.append({'symbol': sym, 'price': t['last'], 'signal': sig, 'confidence': conf, 'score': score})
    
    res.sort(key=lambda x: abs(x['score']), reverse=True)
    
    txt = "🔍 *اسکن بازار*\n\n"
    for i, r in enumerate(res[:15], 1):
        e = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
        txt += f"{i}. {e} {r['symbol'].replace('/USDT','')}: ${r['price']:,.4f} | {r['signal'][:12]} | {r['confidence']}%\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="scan"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def trade_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str):
    q = update.callback_query
    await q.answer()
    
    t = exchange_mgr.ticker(symbol)
    df = exchange_mgr.ohlcv(symbol, '1h', 200)
    if not t or df is None: await q.answer("❌"); return
    
    ind = ti.calculate_all(df)
    sig, conf, _ = sg.generate(ind, t['last'])
    
    if conf < 60: await q.answer("⚠️ اطمینان کم"); return
    
    atr = ind['ATR_14']
    sl = t['last'] - atr * cfg.atr_sl
    tp = t['last'] + atr * cfg.atr_tp
    
    r = trader.open(symbol, t['last'], sl, tp, conf)
    if r:
        await q.edit_message_text(f"🤖 *باز شد*\n📊 {symbol}\n💰 ${t['last']:,.4f}\n🛑 ${sl:,.4f}\n🎯 ${tp:,.4f}",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
    else:
        await q.answer("⚠️ شرایط فراهم نیست", show_alert=True)

async def portfolio_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    pnl = sum(t['pnl'] for t in trader.history)
    w = len([t for t in trader.history if t['pnl'] > 0])
    total = max(1, len(trader.history))
    
    txt = f"💰 *پورتفوی*\n💵 ${trader.balance:,.2f}\n📈 PnL: ${pnl:+,.2f}\n📊 پوزیشن: {len(trader.positions)}\n📋 {total} | برد: {w} ({w/total*100:.0f}%)"
    
    if trader.positions:
        txt += "\n\n*باز:*\n"
        for s, p in trader.positions.items():
            try:
                ct = exchange_mgr.ticker(s)
                cp = ct['last']; pp = (cp-p['entry'])/p['entry']*100
                txt += f"• {s.replace('/USDT','')}: ${cp:,.4f} | {pp:+.1f}%\n"
            except:
                txt += f"• {s.replace('/USDT','')}: ${p['entry']:,.4f}\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def edu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(fmt.edu_msg(), parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def auto_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    txt = f"🤖 *خودکار*\n🎮 دمو: {'✅' if cfg.demo_trading else '❌'}\n💹 واقعی: {'✅' if cfg.real_trading else '❌'}"
    kb = [
        [InlineKeyboardButton(f"دمو: {'✅' if cfg.demo_trading else '❌'}", callback_data="td")],
        [InlineKeyboardButton(f"واقعی: {'✅' if cfg.real_trading else '❌'}", callback_data="tr")],
        [InlineKeyboardButton("🔙", callback_data="back")]
    ]
    await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def settings_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        f"⚙️ *تنظیمات*\n🔌 صرافی: {'✅' if exchange_mgr.connected else '❌'}\n🧠 AI: {'✅' if ai.enabled else '❌'}\n📢 کانال: {cfg.channel_id or '❌'}\n📊 ارز: {len(cfg.symbols)}\n⏰ TF: {len(cfg.timeframes)}",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    try:
        if d == "back": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p": await prices_handler(update, ctx)
        elif d.startswith("s_"): await full_signal_handler(update, ctx, d[2:])
        elif d.startswith("ai_"): await ai_tech_handler(update, ctx, d[3:] if len(d)>3 else "BTC/USDT")
        elif d == "ai": await ai_tech_handler(update, ctx)
        elif d.startswith("fund_"): await ai_fundamental_handler(update, ctx, d[5:] if len(d)>5 else "BTC/USDT")
        elif d.startswith("pa_"): await ai_price_action_handler(update, ctx, d[3:] if len(d)>3 else "BTC/USDT")
        elif d.startswith("pred_"): await full_signal_handler(update, ctx, d[5:] if len(d)>5 else "BTC/USDT")
        elif d == "scan": await scan_handler(update, ctx)
        elif d == "tech": await q.edit_message_text("📈 *انتخاب:*", parse_mode="Markdown", reply_markup=Menu.technical())
        elif d.startswith("trade_"): await trade_handler(update, ctx, d[6:])
        elif d == "port": await portfolio_handler(update, ctx)
        elif d in ["perf", "hist"]: await portfolio_handler(update, ctx)
        elif d == "auto": await auto_handler(update, ctx)
        elif d == "td": cfg.demo_trading = not cfg.demo_trading; await auto_handler(update, ctx)
        elif d == "tr":
            if exchange_mgr.read_only: await q.answer("❌ API نیست"); return
            cfg.real_trading = not cfg.real_trading; await auto_handler(update, ctx)
        elif d == "set": await settings_handler(update, ctx)
        elif d == "status": await settings_handler(update, ctx)
        elif d == "edu": await edu_handler(update, ctx)
        elif d == "patt": await full_signal_handler(update, ctx)
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
    if isinstance(ctx.error, Conflict):
        ProcessLock.release()
        sys.exit(1)

# ============================================================
# AUTO SIGNALS - هر ۱۰ دقیقه به کانال
# ============================================================
async def auto_signals_loop(app: Application):
    """ارسال سیگنال خودکار هر ۱۰ دقیقه"""
    await asyncio.sleep(10)
    logger.info("📢 Auto Signal Loop Started (Every 10 min)")
    
    while True:
        try:
            if not cfg.channel_id or not cfg.auto_send:
                await asyncio.sleep(60)
                continue
            
            if not exchange_mgr.connected:
                exchange_mgr.connect()
            
            # سیگنال‌های اصلی
            priority_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]
            
            for sym in priority_symbols:
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 200)
                    
                    if t and df is not None:
                        ind = ti.calculate_all(df)
                        
                        # MTF
                        mtf = {}
                        for tf_name, tf_val in list(cfg.timeframes.items())[:6]:
                            dft = exchange_mgr.ohlcv(sym, tf_val, 100)
                            if dft is not None:
                                mtf[tf_name] = ti.calculate_all(dft)
                        
                        sig, conf, score = sg.generate(ind, t['last'], mtf)
                        pats = [k for k,v in ind.items() if isinstance(v,bool) and v]
                        
                        # AI Analysis (only for BTC & ETH to save API calls)
                        ai_tech = None
                        ai_fund = None
                        ai_pa = None
                        
                        if sym in ["BTC/USDT", "ETH/USDT"] and ai.enabled:
                            ai_tech = await ai.technical_analysis(sym, ind, t['last'], t.get('percentage',0), pats, mtf)
                            ai_fund = await ai.fundamental_analysis(sym, t['last'], t.get('percentage',0))
                            ai_pa = await ai.price_action_analysis(sym, ind, t['last'], pats)
                        
                        analysis = {
                            'symbol': sym,
                            'price': t['last'],
                            'change': t.get('percentage', 0),
                            'indicators': ind,
                            'signal': sig,
                            'confidence': conf,
                            'score': score
                        }
                        
                        msg = fmt.signal_msg(analysis, ai_tech, ai_fund, ai_pa)
                        await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                        logger.info(f"📤 Signal sent: {sym}")
                        
                        await asyncio.sleep(90)  # فاصله بین پیام‌ها
                        
                except Exception as e:
                    logger.error(f"Signal error for {sym}: {e}")
                    continue
            
            # بررسی پوزیشن‌های باز
            for sym in list(trader.positions.keys()):
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 100)
                    if t and df is not None:
                        ind = ti.calculate_all(df)
                        result = trader.update(sym, t['last'], ind['ATR_14'])
                        if result:
                            emoji = "🟢" if result['pnl'] > 0 else "🔴"
                            await app.bot.send_message(
                                cfg.channel_id,
                                f"{emoji} *پوزیشن بسته شد*\n📊 {sym}\n💰 ${result['pnl']:+,.2f}\n📋 {result['reason']}",
                                parse_mode="Markdown"
                            )
                except Exception as e:
                    logger.error(f"Position check error: {e}")
            
            logger.info(f"✅ Signal cycle completed at {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Auto signal loop error: {e}")
        
        await asyncio.sleep(cfg.signal_interval)

async def auto_education_loop(app: Application):
    """ارسال محتوای آموزشی هر ۱ ساعت"""
    await asyncio.sleep(30)
    logger.info("📚 Auto Education Loop Started (Every 1 hour)")
    
    while True:
        try:
            if cfg.channel_id and cfg.auto_send:
                msg = fmt.edu_msg()
                await app.bot.send_message(cfg.channel_id, msg, parse_mode="Markdown")
                logger.info("📚 Education sent")
        except Exception as e:
            logger.error(f"Education error: {e}")
        
        await asyncio.sleep(cfg.education_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire():
        sys.exit(1)
    
    if not cfg.token:
        logger.critical("❌ TELEGRAM_BOT_TOKEN not set!")
        ProcessLock.release()
        return
    
    exchange_mgr.connect()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(error_handler)
    
    # Start background tasks
    asyncio.create_task(auto_signals_loop(app))
    asyncio.create_task(auto_education_loop(app))
    
    logger.info("="*60)
    logger.info("🚀 CRYPTO PULSE ULTIMATE AI v7.0 LAUNCHED")
    logger.info(f"🧠 Groq AI: {'✅ Llama 3.3 70B' if ai.enabled else '❌ No API Key'}")
    logger.info(f"📊 25+ Technical Indicators & Oscillators")
    logger.info(f"⏰ 11 Timeframes: {', '.join(cfg.timeframes)}")
    logger.info(f"📢 Auto Signals Every {cfg.signal_interval//60} Minutes")
    logger.info(f"📚 Auto Education Every {cfg.education_interval//3600} Hour")
    logger.info(f"💰 {len(cfg.symbols)} Cryptocurrencies")
    logger.info(f"🔌 Exchange: {'✅ Connected' if exchange_mgr.connected else '❌ Disconnected'}")
    logger.info("="*60)
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Conflict:
        logger.critical("❌ Conflict - Another instance running!")
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}")
    finally:
        try:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
        except:
            pass
        ProcessLock.release()
        logger.info("👋 Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ProcessLock.release()
        logger.info("👋 Stopped by user")
    except Exception as e:
        logger.critical(f"❌ Critical: {e}")
        ProcessLock.release()
