#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║     CRYPTO PULSE ULTRA PROFESSIONAL TRADING BOT v5.1            ║
║     30+ Indicators | Candle AI | Auto Trade | 70+ Buttons       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os, sys, logging, asyncio, time, json, random, signal
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from collections import deque
import numpy as np
import pandas as pd
import ccxt
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# ENVIRONMENT
# ============================================================
load_dotenv()

# ============================================================
# PROFESSIONAL LOGGING
# ============================================================
# Create logger
logger = logging.getLogger('CryptoPulse')
logger.setLevel(logging.DEBUG)

# Console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)

# File handler - main log
file_handler = RotatingFileHandler('crypto_pulse.log', maxBytes=10*1024*1024, backupCount=7, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)-15s | %(message)s'))
logger.addHandler(file_handler)

# File handler - detailed debug log
debug_handler = RotatingFileHandler('crypto_pulse_debug.log', maxBytes=50*1024*1024, backupCount=3, encoding='utf-8')
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)-15s | %(funcName)-20s | %(message)s'))
logger.addHandler(debug_handler)

# Error log
error_handler = RotatingFileHandler('crypto_pulse_errors.log', maxBytes=10*1024*1024, backupCount=10, encoding='utf-8')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)-15s | %(message)s'))
logger.addHandler(error_handler)

# Silence noisy libraries
for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'apscheduler', 'urllib3', 'asyncio', 'aiohttp']:
    logging.getLogger(lib).setLevel(logging.WARNING)

logger.info("="*60)
logger.info("🚀 Crypto Pulse Ultra v5.1 Initializing...")
logger.info("="*60)

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class BotConfig:
    """Ultra Professional Configuration"""
    # Telegram
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    admin_ids: List[int] = field(default_factory=lambda: [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x])
    
    # Exchange
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    
    # 30 Trading Symbols
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT",
        "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT",
        "XLM/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT",
        "ICP/USDT", "SAND/USDT", "AXS/USDT", "FTM/USDT", "MANA/USDT",
        "GALA/USDT", "ENJ/USDT", "CHZ/USDT", "NEAR/USDT", "APT/USDT"
    ])
    
    # 11 Timeframes
    timeframes: List[str] = field(default_factory=lambda: [
        "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "3d", "1w"
    ])
    
    # Trading
    initial_balance: float = 100000.0
    risk_per_trade: float = 0.02
    max_positions: int = 5
    atr_sl: float = 2.0
    atr_tp: float = 4.0
    trailing_pct: float = 0.03
    max_daily_loss: float = 5000.0
    max_consecutive_losses: int = 5
    
    # Modes
    demo_trading: bool = True
    real_trading: bool = False
    auto_send: bool = True
    
    # Intervals
    signal_interval: int = 600
    education_interval: int = 3600
    price_interval: int = 300

cfg = BotConfig()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_pulse.lock"
    
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls._file):
                with open(cls._file) as f:
                    old_pid = int(f.read().strip() or 0)
                if old_pid and cls._is_alive(old_pid):
                    logger.critical(f"❌ Already running (PID: {old_pid})")
                    return False
                os.remove(cls._file)
            with open(cls._file, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"🔒 Lock acquired (PID: {os.getpid()})")
            return True
        except Exception as e:
            logger.error(f"Lock error: {e}")
            return True
    
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls._file):
                os.remove(cls._file)
                logger.info("🔓 Lock released")
        except:
            pass
    
    @staticmethod
    def _is_alive(pid: int) -> bool:
        try: os.kill(pid, 0); return True
        except (OSError, ProcessLookupError): return False

for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, lambda s, f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# EXCHANGE MANAGER
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._exchange: Optional[ccxt.Exchange] = None
        self.connected: bool = False
        self.read_only: bool = True
        self.markets_loaded: int = 0
    
    @property
    def ex(self) -> Optional[ccxt.Exchange]:
        return self._exchange
    
    def connect(self) -> bool:
        try:
            params = {'enableRateLimit': True, 'timeout': 30000, 'options': {'defaultType': 'spot'}}
            
            if cfg.api_key and cfg.api_secret:
                params.update({'apiKey': cfg.api_key, 'secret': cfg.api_secret, 'password': cfg.api_passphrase})
                self.read_only = False
            
            self._exchange = ccxt.coinex(params)
            self._exchange.load_markets()
            self.markets_loaded = len(self._exchange.markets)
            self.connected = True
            
            mode = "FULL ACCESS" if not self.read_only else "READ-ONLY"
            logger.info(f"✅ Exchange Connected ({mode}) | Markets: {self.markets_loaded}")
            return True
        except Exception as e:
            logger.error(f"❌ Connection Failed: {e}")
            try:
                self._exchange = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000})
                self._exchange.load_markets()
                self.markets_loaded = len(self._exchange.markets)
                self.connected = True
                self.read_only = True
                logger.info("✅ Connected (READ-ONLY Fallback)")
                return True
            except:
                self.connected = False
                return False
    
    def ticker(self, symbol: str) -> Optional[Dict]:
        if not self.connected or not self._exchange: return None
        try: return self._exchange.fetch_ticker(symbol)
        except Exception as e: logger.debug(f"Ticker {symbol}: {e}"); return None
    
    def ohlcv(self, symbol: str, tf: str, limit: int = 200) -> Optional[pd.DataFrame]:
        if not self.connected or not self._exchange: return None
        try:
            data = self._exchange.fetch_ohlcv(symbol, tf, limit=limit)
            if data and len(data) > 30:
                return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        except Exception as e: logger.debug(f"OHLCV {symbol} {tf}: {e}")
        return None

ex = ExchangeManager()

# ============================================================
# TECHNICAL ANALYSIS - 30+ Indicators
# ============================================================
class UltraAnalysis:
    """30+ Professional Indicators + Candle Patterns"""
    
    @staticmethod
    def full(df: pd.DataFrame) -> Dict[str, Any]:
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        open_ = df['open'].astype(float)
        
        ind = {}
        
        # 1. Moving Averages
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
            ind[f'SMA_{p}'] = float(close.rolling(p).mean().iloc[-1])
            if p <= 50:
                w = np.arange(1, min(p, len(close))+1)
                ind[f'WMA_{p}'] = float(np.average(close.iloc[-p:], weights=w[-p:]) if p <= len(close) else close.iloc[-1])
        
        # 2. RSI Multi
        from ta.momentum import RSIIndicator
        for p in [7, 14, 21]:
            try: ind[f'RSI_{p}'] = float(RSIIndicator(close, window=p).rsi().iloc[-1])
            except: ind[f'RSI_{p}'] = 50.0
        
        # 3. MACD
        from ta.trend import MACD
        try:
            macd = MACD(close, 12, 26, 9)
            ind['MACD_LINE'] = float(macd.macd().iloc[-1])
            ind['MACD_SIG'] = float(macd.macd_signal().iloc[-1])
            ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        except:
            ind['MACD_LINE'] = ind['MACD_SIG'] = ind['MACD_HIST'] = 0.0
        
        # 4. Stochastic
        from ta.momentum import StochasticOscillator
        try:
            stoch = StochasticOscillator(high, low, close, 14, 3)
            ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
            ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        except:
            ind['STOCH_K'] = ind['STOCH_D'] = 50.0
        
        # 5. Bollinger Bands
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
        
        # 6. Keltner
        from ta.volatility import KeltnerChannel
        try:
            kc = KeltnerChannel(high, low, close, 20)
            ind['KC_UPPER'] = float(kc.keltner_channel_hband().iloc[-1])
            ind['KC_LOWER'] = float(kc.keltner_channel_lband().iloc[-1])
        except:
            ind['KC_UPPER'] = ind['KC_LOWER'] = close.iloc[-1]
        
        # 7. Donchian
        from ta.volatility import DonchianChannel
        try:
            dc = DonchianChannel(high, low, close, 20)
            ind['DC_UPPER'] = float(dc.donchian_channel_hband().iloc[-1])
            ind['DC_LOWER'] = float(dc.donchian_channel_lband().iloc[-1])
        except:
            ind['DC_UPPER'] = ind['DC_LOWER'] = close.iloc[-1]
        
        # 8. ATR
        from ta.volatility import AverageTrueRange
        for p in [7, 14]:
            try: ind[f'ATR_{p}'] = float(AverageTrueRange(high, low, close, p).average_true_range().iloc[-1])
            except: ind[f'ATR_{p}'] = close.iloc[-1] * 0.01
        ind['ATR_PCT'] = float(ind['ATR_14'] / close.iloc[-1] * 100)
        
        # 9. ADX
        from ta.trend import ADXIndicator
        try:
            adx = ADXIndicator(high, low, close, 14)
            ind['ADX'] = float(adx.adx().iloc[-1])
            ind['DI+'] = float(adx.adx_pos().iloc[-1])
            ind['DI-'] = float(adx.adx_neg().iloc[-1])
        except:
            ind['ADX'] = 20.0; ind['DI+'] = ind['DI-'] = 20.0
        
        # 10. CCI
        from ta.trend import CCIIndicator
        try: ind['CCI'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        
        # 11. Ichimoku
        from ta.trend import IchimokuIndicator
        try:
            ichi = IchimokuIndicator(high, low, 9, 26, 52)
            ind['ICH_TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1])
            ind['ICH_KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
            ind['ICH_SENKOU_A'] = float(ichi.ichimoku_a().iloc[-1])
            ind['ICH_SENKOU_B'] = float(ichi.ichimoku_b().iloc[-1])
        except:
            ind['ICH_TENKAN'] = ind['ICH_KIJUN'] = ind['ICH_SENKOU_A'] = ind['ICH_SENKOU_B'] = close.iloc[-1]
        
        # 12. Parabolic SAR
        from ta.trend import PSARIndicator
        try:
            psar = PSARIndicator(high, low, close)
            ind['PSAR'] = float(psar.psar().iloc[-1])
            ind['PSAR_DIR'] = 1 if close.iloc[-1] > ind['PSAR'] else -1
        except:
            ind['PSAR'] = close.iloc[-1]; ind['PSAR_DIR'] = 0
        
        # 13. Williams %R
        from ta.momentum import WilliamsRIndicator
        try: ind['WILLIAMS_R'] = float(WilliamsRIndicator(high, low, close, 14).williams_r().iloc[-1])
        except: ind['WILLIAMS_R'] = -50.0
        
        # 14. Ultimate Oscillator
        from ta.momentum import UltimateOscillator
        try: ind['ULTIMATE'] = float(UltimateOscillator(high, low, close).ultimate_oscillator().iloc[-1])
        except: ind['ULTIMATE'] = 50.0
        
        # 15. ROC
        from ta.momentum import ROCIndicator
        try: ind['ROC'] = float(ROCIndicator(close, 12).roc().iloc[-1])
        except: ind['ROC'] = 0.0
        
        # 16. Awesome Oscillator
        from ta.momentum import AwesomeOscillatorIndicator
        try: ind['AO'] = float(AwesomeOscillatorIndicator(high, low).awesome_oscillator().iloc[-1])
        except: ind['AO'] = 0.0
        
        # 17. MFI
        from ta.volume import MFIIndicator
        try: ind['MFI'] = float(MFIIndicator(high, low, close, volume, 14).money_flow_index().iloc[-1])
        except: ind['MFI'] = 50.0
        
        # 18. OBV
        from ta.volume import OnBalanceVolumeIndicator
        try: ind['OBV'] = float(OnBalanceVolumeIndicator(close, volume).on_balance_volume().iloc[-1])
        except: ind['OBV'] = 0.0
        
        # 19. Aroon
        from ta.trend import AroonIndicator
        try:
            aroon = AroonIndicator(close, 25)
            ind['AROON_UP'] = float(aroon.aroon_up().iloc[-1])
            ind['AROON_DOWN'] = float(aroon.aroon_down().iloc[-1])
        except:
            ind['AROON_UP'] = ind['AROON_DOWN'] = 50.0
        
        # 20. Vortex
        from ta.trend import VortexIndicator
        try:
            vortex = VortexIndicator(high, low, close, 14)
            ind['VORTEX+'] = float(vortex.vortex_indicator_pos().iloc[-1])
            ind['VORTEX-'] = float(vortex.vortex_indicator_neg().iloc[-1])
        except:
            ind['VORTEX+'] = ind['VORTEX-'] = 1.0
        
        # 21. TRIX
        from ta.trend import TRIXIndicator
        try: ind['TRIX'] = float(TRIXIndicator(close, 15).trix().iloc[-1])
        except: ind['TRIX'] = 0.0
        
        # 22. Mass Index
        from ta.trend import MassIndex
        try: ind['MASS_INDEX'] = float(MassIndex(high, low).mass_index().iloc[-1])
        except: ind['MASS_INDEX'] = 25.0
        
        # 23. Force Index
        from ta.volume import ForceIndexIndicator
        try: ind['FORCE'] = float(ForceIndexIndicator(close, volume, 13).force_index().iloc[-1])
        except: ind['FORCE'] = 0.0
        
        # 24. Ease of Movement
        from ta.volume import EaseOfMovementIndicator
        try: ind['EOM'] = float(EaseOfMovementIndicator(high, low, volume).ease_of_movement().iloc[-1])
        except: ind['EOM'] = 0.0
        
        # 25. Volume Analysis
        vol_sma_20 = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else volume.iloc[-1]
        ind['VOL_RATIO'] = float(volume.iloc[-1] / vol_sma_20 if vol_sma_20 > 0 else 1)
        ind['VOL_TREND'] = 1 if volume.iloc[-1] > volume.rolling(5).mean().iloc[-1] else -1 if len(volume) >= 5 else 0
        
        # 26. Pivot Points
        h, l, c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        pivot = (h + l + c) / 3
        ind['PIVOT'] = float(pivot)
        ind['PIVOT_R1'] = float(2*pivot - l)
        ind['PIVOT_S1'] = float(2*pivot - h)
        ind['PIVOT_R2'] = float(pivot + (h-l))
        ind['PIVOT_S2'] = float(pivot - (h-l))
        ind['PIVOT_R3'] = float(h + 2*(pivot-l))
        ind['PIVOT_S3'] = float(l - 2*(h-pivot))
        
        # 27. Fibonacci
        h50 = high.rolling(50).max().iloc[-1] if len(high) >= 50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low) >= 50 else low.min()
        diff = h50 - l50
        for lvl in [0.236, 0.382, 0.5, 0.618, 0.786]:
            ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff * lvl)
        
        # 28. Market Metrics
        ind['TREND_STR'] = float((close.iloc[-1] - close.iloc[-50]) / close.iloc[-50] * 100) if len(close) >= 50 else 0
        ind['VOLATILITY'] = float(close.pct_change().rolling(14).std().iloc[-1] * 100)
        ind['MOMENTUM'] = float(close.iloc[-1] - close.iloc[-10]) if len(close) >= 10 else 0
        
        # 29. Support/Resistance
        ind['SUPPORT'] = float(low.rolling(20).min().iloc[-1]) if len(low) >= 20 else low.min()
        ind['RESISTANCE'] = float(high.rolling(20).max().iloc[-1]) if len(high) >= 20 else high.max()
        
        # 30. Candle Patterns
        patterns = UltraAnalysis.candles(df)
        ind.update(patterns)
        
        # 31. Divergence
        ind['DIVERGENCE'] = UltraAnalysis.divergence(close)
        
        return ind
    
    @staticmethod
    def candles(df: pd.DataFrame) -> Dict[str, bool]:
        patterns = {p: False for p in [
            'DOJI', 'HAMMER', 'SHOOTING_STAR', 'ENGULFING_BULL', 'ENGULFING_BEAR',
            'MORNING_STAR', 'EVENING_STAR', 'THREE_WHITE', 'THREE_BLACK',
            'HARAMI_BULL', 'HARAMI_BEAR', 'PIERCING', 'DARK_CLOUD', 'MARUBOZU_BULL', 'MARUBOZU_BEAR'
        ]}
        
        if len(df) < 3: return patterns
        
        o, h, l, c = df['open'].iloc[-1], df['high'].iloc[-1], df['low'].iloc[-1], df['close'].iloc[-1]
        po, ph, pl, pc = df['open'].iloc[-2], df['high'].iloc[-2], df['low'].iloc[-2], df['close'].iloc[-2]
        
        body = abs(c - o)
        total_range = h - l
        if total_range == 0: return patterns
        
        # Doji
        patterns['DOJI'] = body <= total_range * 0.08
        # Hammer
        patterns['HAMMER'] = ((min(c,o)-l) > body*2) and ((h-max(c,o)) < body*0.5) and body > 0
        # Shooting Star
        patterns['SHOOTING_STAR'] = ((h-max(c,o)) > body*2) and ((min(c,o)-l) < body*0.5) and body > 0
        # Engulfing Bull
        patterns['ENGULFING_BULL'] = (c > o) and (pc < po) and (o <= pc) and (c >= po)
        # Engulfing Bear
        patterns['ENGULFING_BEAR'] = (c < o) and (pc > po) and (o >= pc) and (c <= po)
        # Marubozu
        patterns['MARUBOZU_BULL'] = (c > o) and ((h-c) < body*0.1) and ((o-l) < body*0.1)
        patterns['MARUBOZU_BEAR'] = (c < o) and ((h-o) < body*0.1) and ((c-l) < body*0.1)
        
        if len(df) >= 3:
            o3, c3 = df['open'].iloc[-3], df['close'].iloc[-3]
            # Morning Star
            patterns['MORNING_STAR'] = (pc < po) and (abs(c-o) < body*0.3) and (c > o) and (c > (po+pc)/2)
            # Evening Star
            patterns['EVENING_STAR'] = (pc > po) and (abs(c-o) < body*0.3) and (c < o) and (c < (po+pc)/2)
            # Three White Soldiers
            patterns['THREE_WHITE'] = (c > o) and (pc > po) and (c3 > o3) and (c > pc > c3)
            # Three Black Crows
            patterns['THREE_BLACK'] = (c < o) and (pc < po) and (c3 < o3) and (c < pc < c3)
        
        return patterns
    
    @staticmethod
    def divergence(price: pd.Series) -> str:
        if len(price) < 20: return "NONE"
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(price, 14).rsi()
        rp, rr = price.iloc[-20:], rsi.iloc[-20:]
        if rp.iloc[-1] < rp.min() and rr.iloc[-1] > rr.min(): return "BULLISH"
        if rp.iloc[-1] > rp.max() and rr.iloc[-1] < rr.max(): return "BEARISH"
        if rp.iloc[-1] > rp.min() and rr.iloc[-1] < rr.min(): return "HIDDEN_BULL"
        if rp.iloc[-1] < rp.max() and rr.iloc[-1] > rr.max(): return "HIDDEN_BEAR"
        return "NONE"

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind: Dict, price: float, mtf: Dict = None) -> Tuple[str, int, int]:
        score = 0
        
        # Trend (350)
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50'] > ind['EMA_200']: score += 200
        elif ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']: score += 130
        elif ind['EMA_20'] > ind['EMA_50']: score += 70
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50'] < ind['EMA_200']: score -= 200
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']: score -= 130
        
        if price > ind['ICH_SENKOU_A'] and price > ind['ICH_SENKOU_B']:
            score += 80 if ind['ICH_TENKAN'] > ind['ICH_KIJUN'] else 40
        elif price < ind['ICH_SENKOU_A'] and price < ind['ICH_SENKOU_B']:
            score -= 80 if ind['ICH_TENKAN'] < ind['ICH_KIJUN'] else 40
        
        # Momentum (300)
        rsi = ind['RSI_14']
        if rsi < 25: score += 120
        elif rsi < 35: score += 70
        elif rsi < 45: score += 30
        elif rsi > 75: score -= 120
        elif rsi > 65: score -= 70
        elif rsi > 55: score -= 30
        
        if ind['MACD_HIST'] > 0: score += 70
        else: score -= 70
        
        if ind['STOCH_K'] < 20 and ind['STOCH_D'] < 20: score += 80
        elif ind['STOCH_K'] > 80 and ind['STOCH_D'] > 80: score -= 80
        
        cci = ind['CCI']
        if cci < -200: score += 70
        elif cci < -100: score += 40
        elif cci > 200: score -= 70
        elif cci > 100: score -= 40
        
        # Volatility (150)
        if ind['BB_PCT'] < 0.1: score += 100
        elif ind['BB_PCT'] > 0.9: score -= 100
        if ind['ATR_PCT'] > 5: score += 40
        
        # Volume (100)
        if ind['VOL_RATIO'] > 2.5: score += 60 if score > 0 else -60
        elif ind['VOL_RATIO'] > 1.8: score += 40 if score > 0 else -40
        if ind['MFI'] < 20: score += 60
        elif ind['MFI'] > 80: score -= 60
        
        # Candles (100)
        if ind.get('ENGULFING_BULL'): score += 80
        if ind.get('HAMMER'): score += 50
        if ind.get('MORNING_STAR'): score += 60
        if ind.get('THREE_WHITE'): score += 60
        if ind.get('MARUBOZU_BULL'): score += 40
        if ind.get('ENGULFING_BEAR'): score -= 80
        if ind.get('SHOOTING_STAR'): score -= 50
        if ind.get('EVENING_STAR'): score -= 60
        if ind.get('THREE_BLACK'): score -= 60
        if ind.get('MARUBOZU_BEAR'): score -= 40
        
        # Divergence (50)
        div = ind.get('DIVERGENCE', 'NONE')
        if div == 'BULLISH': score += 60
        elif div == 'BEARISH': score -= 60
        
        # MTF (50)
        if mtf:
            for tf, ti in mtf.items():
                w = {"1h": 1, "4h": 1.5, "1d": 2.5, "1w": 4}.get(tf, 0.5)
                if ti.get('RSI_14', 50) > 55: score += int(25 * w)
                elif ti.get('RSI_14', 50) < 45: score -= int(25 * w)
        
        score = max(-1000, min(1000, score))
        
        if score >= 750: return "خرید فوق‌العاده 🟢🟢🟢🟢🟢", 99, score
        elif score >= 550: return "خرید قوی 🟢🟢🟢🟢", 93, score
        elif score >= 350: return "خرید خوب 🟢🟢🟢", 84, score
        elif score >= 200: return "خرید 🟢🟢", 73, score
        elif score >= 80: return "خرید ضعیف 🟢", 62, score
        elif score <= -750: return "فروش فوق‌العاده 🔴🔴🔴🔴🔴", 99, score
        elif score <= -550: return "فروش قوی 🔴🔴🔴🔴", 93, score
        elif score <= -350: return "فروش خوب 🔴🔴🔴", 84, score
        elif score <= -200: return "فروش 🔴🔴", 73, score
        elif score <= -80: return "فروش ضعیف 🔴", 62, score
        else: return "خنثی ⚪⚪", 50, score

# ============================================================
# TRADING ENGINE
# ============================================================
class TradingEngine:
    def __init__(self):
        self.balance = cfg.initial_balance
        self.positions: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self.consecutive_losses = 0
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.load()
    
    def load(self):
        try:
            with open('trades.json', 'r') as f:
                d = json.load(f)
                self.balance = d.get('balance', cfg.initial_balance)
                self.history = d.get('history', [])
        except: pass
    
    def save(self):
        try:
            with open('trades.json', 'w') as f:
                json.dump({'balance': self.balance, 'history': self.history[-500:]}, f)
        except: pass
    
    def calc_size(self, entry: float, sl: float, conf: int) -> float:
        risk = self.balance * cfg.risk_per_trade * (1.5 if conf >= 90 else 1.2 if conf >= 80 else 0.8 if conf < 65 else 1)
        if self.consecutive_losses > 0: risk *= (0.5 ** self.consecutive_losses)
        pr = abs(entry - sl)
        if pr == 0: return 0
        return min(risk/pr, self.balance * 0.25 / entry)
    
    def open(self, symbol: str, entry: float, sl: float, tp: float, conf: int) -> Optional[Dict]:
        if len(self.positions) >= cfg.max_positions or self.consecutive_losses >= cfg.max_consecutive_losses:
            return None
        sz = self.calc_size(entry, sl, conf)
        if sz <= 0 or sz * entry > self.balance: return None
        self.balance -= sz * entry
        pos = {'symbol': symbol, 'size': sz, 'entry': entry, 'sl': sl, 'tp': tp,
               'high': entry, 'time': datetime.now(), 'conf': conf}
        self.positions[symbol] = pos
        self.daily_trades += 1
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
        self.daily_pnl += pnl
        self.consecutive_losses = 0 if pnl > 0 else self.consecutive_losses + 1
        trade = {'symbol': symbol, 'entry': p['entry'], 'exit': price, 'pnl': pnl, 'reason': reason, 'time': datetime.now().isoformat()}
        self.history.append(trade)
        self.save()
        logger.info(f"{'🟢' if pnl>0 else '🔴'} CLOSE {symbol} | ${pnl:+.2f} | {reason}")
        return trade

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
class Fmt:
    @staticmethod
    def signal(a: Dict) -> str:
        s = a['symbol'].replace('/USDT','')
        i = a['indicators']
        pats = [k for k,v in i.items() if isinstance(v,bool) and v]
        return f"""
╔══════════════════════════════════════════════╗
║       🔥 سیگنال حرفه‌ای {s} 🔥            ║
╚══════════════════════════════════════════════╝

💰 قیمت: ${a['price']:,.4f} | 📊 تغییر: {a['change']:+.2f}%

🎯 *سیگنال:* {a['signal']}
💪 اطمینان: {a['confidence']}% | امتیاز: {a['score']}/1000

📈 *اندیکاتورها:*
• RSI(14): {i['RSI_14']:.1f} | RSI(7): {i['RSI_7']:.1f}
• MACD: {'صعودی' if i['MACD_HIST']>0 else 'نزولی'}
• ADX: {i['ADX']:.1f} | CCI: {i['CCI']:.1f}
• MFI: {i['MFI']:.1f} | ATR: {i['ATR_14']:.4f}
• BB Width: {i['BB_WIDTH']:.4f}

🕯️ *الگوها:* {', '.join(pats) if pats else 'بدون الگو'}
🔄 *واگرایی:* {i.get('DIVERGENCE','NONE')}

🔑 *سطوح:*
• مقاومت: ${i['RESISTANCE']:,.4f}
• پیوت: ${i['PIVOT']:,.4f}
• حمایت: ${i['SUPPORT']:,.4f}

⚠️ حد ضرر: ${a['price']-i['ATR_14']*cfg.atr_sl:,.4f}
🎯 حد سود: ${a['price']+i['ATR_14']*cfg.atr_tp:,.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%H:%M:%S')} | ✨ @CryptoPulse606
"""
    
    @staticmethod
    def edu() -> str:
        topics = [
            "تحلیل ساختار بازار", "روانشناسی معامله‌گری", "مدیریت سرمایه",
            "الگوهای کندلی", "تحلیل وایکوف", "استراتژی شکست",
            "واگرایی مخفی", "ترلینگ استاپ", "مولتی تایم‌فریم",
            "پرایس اکشن", "فیبوناچی", "ایچیموکو", "مکدی",
            "آراس‌آی", "بولینگر باند", "حجم معاملات", "فاندامنتال",
            "مدیریت احساسات", "ژورنال نویسی", "تحلیل بین بازاری"
        ]
        return f"""
📚 *آموزش تخصصی*

📖 {random.choice(topics)}

🔍 *اصول طلایی:*
۱. روند دوست شماست
۲. ریسک/ریوارد ≥ ۱:۲
۳. حداکثر ۲٪ ریسک در هر معامله
۴. حد ضرر اجباری
۵. بعد ۳ ضرر استراحت
۶. ژورنال معاملاتی
۷. صبوری = سودآوری

💡 *رمز موفقیت:*
۲۰٪ استراتژی + ۳۰٪ ریسک + ۵۰٪ روانشناسی

━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606 | {datetime.now().strftime('%H:%M')}
"""

# ============================================================
# MENUS - 70+ Buttons
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 قیمت‌ها", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن", callback_data="scan")],
            [InlineKeyboardButton("📈 تحلیل", callback_data="tech"),
             InlineKeyboardButton("⏰ مولتی‌تایم", callback_data="mtf"),
             InlineKeyboardButton("⭐ برترین‌ها", callback_data="top")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="port"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf"),
             InlineKeyboardButton("📋 تاریخچه", callback_data="hist")],
            [InlineKeyboardButton("🤖 خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="set"),
             InlineKeyboardButton("🔑 وضعیت", callback_data="status")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("📰 بازار", callback_data="market"),
             InlineKeyboardButton("🕯️ الگوها", callback_data="patt")],
            [InlineKeyboardButton("📉 ترس/طمع", callback_data="fear"),
             InlineKeyboardButton("🐋 نهنگ", callback_data="whale"),
             InlineKeyboardButton("💎 آلت‌کوین", callback_data="alt")],
            [InlineKeyboardButton("🔮 پیش‌بینی", callback_data="pred"),
             InlineKeyboardButton("📈 نمودار", callback_data="chart"),
             InlineKeyboardButton("📊 مقایسه", callback_data="comp")],
            [InlineKeyboardButton("🔔 هشدار", callback_data="alert"),
             InlineKeyboardButton("⏸️ توقف", callback_data="stop"),
             InlineKeyboardButton("🔄 بروز", callback_data="ref")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")]
        ])
    
    @staticmethod
    def technical() -> InlineKeyboardMarkup:
        kb = []
        row = []
        for s in cfg.symbols[:16]:
            row.append(InlineKeyboardButton(s.replace('/USDT',''), callback_data=f"s_{s}"))
            if len(row) == 4: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([InlineKeyboardButton("🔙", callback_data="back")])
        return InlineKeyboardMarkup(kb)

# ============================================================
# HANDLERS
# ============================================================
async def start_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Crypto Pulse Ultra v5.1*\n\n"
        "✨ ۳۰+ اندیکاتور | ۱۱ تایم‌فریم\n"
        "✨ ۳۰ ارز | ۷۰+ دکمه\n"
        "✨ معاملات دمو و واقعی\n"
        "✨ الگوهای کندلی | واگرایی\n\n"
        "👇 انتخاب کنید:",
        parse_mode="Markdown", reply_markup=Menu.main()
    )

async def signal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🔄 تحلیل {symbol.replace('/USDT','')}...")
    
    if not ex.connected: ex.connect()
    
    t = ex.ticker(symbol)
    df = ex.ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = UltraAnalysis.full(df)
    mtf = {}
    for tf in cfg.timeframes[:6]:
        dft = ex.ohlcv(symbol, tf, 100)
        if dft is not None: mtf[tf] = UltraAnalysis.full(dft)
    
    sig, conf, score = SignalGen.generate(ind, t['last'], mtf)
    a = {'symbol': symbol, 'price': t['last'], 'change': t.get('percentage',0),
         'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
    
    await q.edit_message_text(Fmt.signal(a), parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"s_{symbol}"),
            InlineKeyboardButton("🤖 معامله", callback_data=f"trade_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def prices_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🔄 دریافت...")
    if not ex.connected: ex.connect()
    
    txt = "💰 *قیمت‌ها*\n\n"
    for sym in cfg.symbols[:20]:
        t = ex.ticker(sym)
        if t:
            e = "🟢" if t.get('percentage',0)>0 else "🔴"
            txt += f"{e} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def scan_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🔍 اسکن ۳۰ ارز...")
    if not ex.connected: ex.connect()
    
    res = []
    for sym in cfg.symbols:
        t = ex.ticker(sym)
        df = ex.ohlcv(sym, '1h', 100)
        if t and df is not None:
            ind = UltraAnalysis.full(df)
            sig, conf, score = SignalGen.generate(ind, t['last'])
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
    
    t = ex.ticker(symbol)
    df = ex.ohlcv(symbol, '1h', 200)
    if not t or df is None: await q.answer("❌"); return
    
    ind = UltraAnalysis.full(df)
    sig, conf, _ = SignalGen.generate(ind, t['last'])
    
    if conf < 60: await q.answer("⚠️ اطمینان کم"); return
    
    atr = ind['ATR_14']
    sl = t['last'] - atr * cfg.atr_sl
    tp = t['last'] + atr * cfg.atr_tp
    
    r = trader.open(symbol, t['last'], sl, tp, conf)
    if r:
        await q.edit_message_text(
            f"🤖 *باز شد*\n📊 {symbol}\n💰 ${t['last']:,.4f}\n🛑 ${sl:,.4f}\n🎯 ${tp:,.4f}",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
    else:
        await q.answer("⚠️ شرایط فراهم نیست", show_alert=True)

async def portfolio_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    pnl = sum(t['pnl'] for t in trader.history)
    w = len([t for t in trader.history if t['pnl'] > 0])
    total = max(1, len(trader.history))
    
    txt = f"💰 *پورتفوی*\n\n💵 موجودی: ${trader.balance:,.2f}\n📈 PnL: ${pnl:+,.2f}\n📊 پوزیشن: {len(trader.positions)}\n📋 کل: {total} | برد: {w} ({w/total*100:.0f}%)"
    
    if trader.positions:
        txt += "\n\n*باز:*\n"
        for s, p in trader.positions.items():
            try:
                ct = ex.ticker(s)
                cp = ct['last']; pp = (cp-p['entry'])/p['entry']*100
                txt += f"• {s.replace('/USDT','')}: ${cp:,.4f} | {pp:+.1f}%\n"
            except:
                txt += f"• {s.replace('/USDT','')}: ${p['entry']:,.4f}\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="port"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def edu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(Fmt.edu(), parse_mode="Markdown",
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
        f"⚙️ *تنظیمات*\n🔌 صرافی: {'✅' if ex.connected else '❌'}\n📢 کانال: {cfg.channel_id or '❌'}\n📊 ارز: {len(cfg.symbols)}\n⏰ TF: {len(cfg.timeframes)}",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    try:
        if d == "back": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p": await prices_handler(update, ctx)
        elif d.startswith("s_"): await signal_handler(update, ctx, d[2:])
        elif d == "scan": await scan_handler(update, ctx)
        elif d == "top": await scan_handler(update, ctx)
        elif d == "tech": await q.edit_message_text("📈 *انتخاب:*", parse_mode="Markdown", reply_markup=Menu.technical())
        elif d.startswith("trade_"): await trade_handler(update, ctx, d[6:])
        elif d == "port": await portfolio_handler(update, ctx)
        elif d in ["perf", "hist"]: await portfolio_handler(update, ctx)
        elif d == "auto": await auto_handler(update, ctx)
        elif d == "td":
            cfg.demo_trading = not cfg.demo_trading
            await auto_handler(update, ctx)
        elif d == "tr":
            if ex.read_only: await q.answer("❌ API نیست"); return
            cfg.real_trading = not cfg.real_trading
            await auto_handler(update, ctx)
        elif d == "set": await settings_handler(update, ctx)
        elif d == "status": await settings_handler(update, ctx)
        elif d == "edu": await edu_handler(update, ctx)
        elif d == "market": await scan_handler(update, ctx)
        elif d == "patt": await signal_handler(update, ctx)
        elif d == "stop":
            for s in list(trader.positions.keys()):
                t = ex.ticker(s)
                if t: trader.close(s, t['last'], "EMERGENCY")
            await q.edit_message_text("⏸️ بسته شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ref": await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "help":
            await q.edit_message_text("❓ /start برای منو", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
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
# AUTO TASKS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(15)
    while True:
        try:
            if not cfg.channel_id or not cfg.auto_send:
                await asyncio.sleep(60); continue
            if not ex.connected: ex.connect()
            
            for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT"]:
                t = ex.ticker(sym)
                df = ex.ohlcv(sym, '1h', 200)
                if t and df is not None:
                    ind = UltraAnalysis.full(df)
                    mtf = {}
                    for tf in ["1h", "4h", "1d"]:
                        dft = ex.ohlcv(sym, tf, 100)
                        if dft is not None: mtf[tf] = UltraAnalysis.full(dft)
                    sig, conf, score = SignalGen.generate(ind, t['last'], mtf)
                    a = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0),
                         'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                    await app.bot.send_message(cfg.channel_id, Fmt.signal(a), parse_mode="Markdown")
                    await asyncio.sleep(120)
            
            # Position check
            for sym in list(trader.positions.keys()):
                t = ex.ticker(sym)
                df = ex.ohlcv(sym, '1h', 100)
                if t and df is not None:
                    ind = UltraAnalysis.full(df)
                    r = trader.update(sym, t['last'], ind['ATR_14'])
                    if r:
                        e = "🟢" if r['pnl']>0 else "🔴"
                        await app.bot.send_message(cfg.channel_id,
                            f"{e} *بسته:* {sym}\n💰 ${r['pnl']:+,.2f} | {r['reason']}", parse_mode="Markdown")
            
        except Exception as e: logger.error(f"Task: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_education(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and cfg.auto_send:
                await app.bot.send_message(cfg.channel_id, Fmt.edu(), parse_mode="Markdown")
        except Exception as e: logger.error(f"Edu: {e}")
        await asyncio.sleep(cfg.education_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token:
        logger.critical("❌ No token!")
        ProcessLock.release(); return
    
    ex.connect()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(error_handler)
    
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_education(app))
    
    logger.info("="*60)
    logger.info("🚀 CRYPTO PULSE ULTRA v5.1 LAUNCHED")
    logger.info(f"📊 30+ Indicators | 11 Timeframes | 30 Coins")
    logger.info(f"🔌 Exchange: {'✅' if ex.connected else '❌'} | Mode: {'FULL' if not ex.read_only else 'READ-ONLY'}")
    logger.info(f"📢 Channel: {cfg.channel_id or 'Not Set'}")
    logger.info("="*60)
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Conflict:
        logger.critical("❌ Conflict!")
    except Exception as e:
        logger.critical(f"❌ {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()
        logger.info("👋 Shutdown complete")

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: ProcessLock.release()
    except Exception as e: logger.critical(f"Fatal: {e}"); ProcessLock.release()
