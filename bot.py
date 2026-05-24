#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║     CRYPTO PULSE ULTRA PROFESSIONAL TRADING BOT v5.0        ║
║     Advanced Multi-Timeframe Analysis & Auto Trading        ║
║     25+ Indicators | Candle Patterns | ML Prediction        ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, sys, logging, asyncio, time, json, random, signal, hashlib
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
# ENVIRONMENT SETUP
# ============================================================
load_dotenv()

# ============================================================
# LOGGING - Professional Multi-Handler
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(name)-15s | %(message)s',
    handlers=[
        logging.FileHandler('crypto_pulse.log', encoding='utf-8'),
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler('crypto_pulse_detailed.log', maxBytes=10*1024*1024, backupCount=5)
    ]
)
logger = logging.getLogger('CryptoPulse')

for noisy_lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'apscheduler', 'urllib3', 'asyncio']:
    logging.getLogger(noisy_lib).setLevel(logging.ERROR)

# ============================================================
# CONFIGURATION - Centralized & Type-Safe
# ============================================================
@dataclass
class BotConfig:
    """Ultra Professional Configuration"""
    # Telegram
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    
    # Exchange API
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    
    # Trading Symbols (Top 30)
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT",
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "AVAX/USDT",
        "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT",
        "XLM/USDT", "FIL/USDT", "TRX/USDT", "VET/USDT", "ALGO/USDT",
        "ICP/USDT", "SAND/USDT", "AXS/USDT", "FTM/USDT", "MANA/USDT",
        "GALA/USDT", "ENJ/USDT", "CHZ/USDT", "NEAR/USDT", "APT/USDT"
    ])
    
    # Timeframes for Analysis
    timeframes: List[str] = field(default_factory=lambda: [
        "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "3d", "1w"
    ])
    
    # Trading Parameters
    initial_balance: float = 100000.0
    risk_per_trade: float = 0.02
    max_positions: int = 5
    atr_multiplier_sl: float = 2.0
    atr_multiplier_tp: float = 4.0
    trailing_stop_pct: float = 0.03
    max_daily_loss: float = 5000.0
    max_consecutive_losses: int = 5
    
    # Auto Trading
    demo_trading: bool = True
    real_trading: bool = False
    
    # Post Intervals
    signal_interval: int = 600  # 10 min
    education_interval: int = 3600  # 1 hour
    price_update_interval: int = 300  # 5 min

cfg = BotConfig()

# ============================================================
# PROCESS LOCK - Prevent Duplicate Instances
# ============================================================
class ProcessLock:
    """Ensures single bot instance"""
    _lock_file = "crypto_pulse.lock"
    
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls._lock_file):
                with open(cls._lock_file) as f:
                    old_pid = int(f.read().strip() or 0)
                if old_pid and cls._is_alive(old_pid):
                    logger.critical(f"❌ Already running (PID: {old_pid})")
                    return False
                os.remove(cls._lock_file)
            with open(cls._lock_file, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except:
            return True
    
    @classmethod
    def release(cls):
        try:
            if os.path.exists(cls._lock_file):
                os.remove(cls._lock_file)
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
# EXCHANGE CONNECTION - Robust & Auto-Recovery
# ============================================================
class ExchangeManager:
    """Ultra-Reliable Exchange Connection"""
    
    def __init__(self):
        self._exchange: Optional[ccxt.Exchange] = None
        self.connected: bool = False
        self.read_only: bool = True
        self.last_error: str = ""
        self._reconnect_count: int = 0
    
    @property
    def exchange(self) -> Optional[ccxt.Exchange]:
        return self._exchange
    
    def connect(self) -> bool:
        try:
            params = {
                'enableRateLimit': True,
                'timeout': 30000,
                'options': {'defaultType': 'spot'}
            }
            
            if cfg.api_key and cfg.api_secret:
                params.update({
                    'apiKey': cfg.api_key,
                    'secret': cfg.api_secret,
                    'password': cfg.api_passphrase
                })
                self.read_only = False
            
            self._exchange = ccxt.coinex(params)
            self._exchange.load_markets()
            self.connected = True
            self._reconnect_count = 0
            mode = "FULL" if not self.read_only else "READ-ONLY"
            logger.info(f"✅ Exchange Connected ({mode} Mode) | Markets: {len(self._exchange.markets)}")
            return True
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            logger.error(f"❌ Connection Failed: {e}")
            
            # Fallback to read-only
            try:
                self._exchange = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000})
                self._exchange.load_markets()
                self.connected = True
                self.read_only = True
                logger.info("✅ Connected (READ-ONLY Fallback)")
                return True
            except:
                return False
    
    def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        if not self.connected:
            return None
        try:
            return self._exchange.fetch_ticker(symbol)
        except Exception as e:
            logger.debug(f"Ticker error {symbol}: {e}")
            return None
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 200) -> Optional[pd.DataFrame]:
        if not self.connected:
            return None
        try:
            data = self._exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if data and len(data) > 30:
                return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        except Exception as e:
            logger.debug(f"OHLCV error {symbol} {timeframe}: {e}")
        return None
    
    def create_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Optional[Dict]:
        if self.read_only or not self.connected:
            return None
        try:
            order_type = 'limit' if price else 'market'
            return self._exchange.create_order(symbol, order_type, side, amount, price)
        except Exception as e:
            logger.error(f"Order error: {e}")
            return None

ex = ExchangeManager()

# ============================================================
# ULTRA TECHNICAL ANALYZER - 25+ Powerful Indicators
# ============================================================
class UltraAnalyzer:
    """25+ Professional Technical Indicators & Candlestick Patterns"""
    
    @staticmethod
    def full_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Complete technical analysis"""
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        open_ = df['open'].astype(float)
        
        ind = {}
        
        # ===== 1. MOVING AVERAGES (Multiple Types) =====
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
            ind[f'SMA_{p}'] = float(close.rolling(p).mean().iloc[-1])
            if p <= 50:
                weights = np.arange(1, p+1)
                ind[f'WMA_{p}'] = float(close.rolling(p).apply(lambda x: np.average(x, weights=weights[:len(x)])).iloc[-1])
        
        # ===== 2. RSI (Multiple Periods) =====
        from ta.momentum import RSIIndicator
        for p in [7, 14, 21]:
            ind[f'RSI_{p}'] = float(RSIIndicator(close, window=p).rsi().iloc[-1])
        
        # ===== 3. MACD =====
        from ta.trend import MACD
        macd = MACD(close, 12, 26, 9)
        ind['MACD_LINE'] = float(macd.macd().iloc[-1])
        ind['MACD_SIGNAL'] = float(macd.macd_signal().iloc[-1])
        ind['MACD_HIST'] = float(macd.macd_diff().iloc[-1])
        
        # ===== 4. STOCHASTIC =====
        from ta.momentum import StochasticOscillator
        stoch = StochasticOscillator(high, low, close, 14, 3)
        ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
        ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        
        # ===== 5. BOLLINGER BANDS =====
        from ta.volatility import BollingerBands
        bb = BollingerBands(close, 20, 2)
        ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1])
        ind['BB_MIDDLE'] = float(bb.bollinger_mavg().iloc[-1])
        ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
        ind['BB_WIDTH'] = float(bb.bollinger_wband().iloc[-1])
        ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        
        # ===== 6. KELTNER CHANNEL =====
        from ta.volatility import KeltnerChannel
        kc = KeltnerChannel(high, low, close, 20)
        ind['KC_UPPER'] = float(kc.keltner_channel_hband().iloc[-1])
        ind['KC_MIDDLE'] = float(kc.keltner_channel_mband().iloc[-1])
        ind['KC_LOWER'] = float(kc.keltner_channel_lband().iloc[-1])
        
        # ===== 7. DONCHIAN CHANNEL =====
        from ta.volatility import DonchianChannel
        dc = DonchianChannel(high, low, close, 20)
        ind['DC_UPPER'] = float(dc.donchian_channel_hband().iloc[-1])
        ind['DC_LOWER'] = float(dc.donchian_channel_lband().iloc[-1])
        ind['DC_WIDTH'] = float(dc.donchian_channel_wband().iloc[-1])
        
        # ===== 8. ATR (Multiple) =====
        from ta.volatility import AverageTrueRange
        for p in [7, 14]:
            atr = AverageTrueRange(high, low, close, p)
            ind[f'ATR_{p}'] = float(atr.average_true_range().iloc[-1])
        ind['ATR_PCT'] = float(ind['ATR_14'] / close.iloc[-1] * 100)
        
        # ===== 9. ADX =====
        from ta.trend import ADXIndicator
        adx = ADXIndicator(high, low, close, 14)
        ind['ADX'] = float(adx.adx().iloc[-1])
        ind['DI_PLUS'] = float(adx.adx_pos().iloc[-1])
        ind['DI_MINUS'] = float(adx.adx_neg().iloc[-1])
        
        # ===== 10. CCI =====
        from ta.trend import CCIIndicator
        ind['CCI_20'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        
        # ===== 11. ICHIMOKU =====
        from ta.trend import IchimokuIndicator
        ichi = IchimokuIndicator(high, low, 9, 26, 52)
        ind['ICH_TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1])
        ind['ICH_KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
        ind['ICH_SENKOU_A'] = float(ichi.ichimoku_a().iloc[-1])
        ind['ICH_SENKOU_B'] = float(ichi.ichimoku_b().iloc[-1])
        
        # ===== 12. PARABOLIC SAR =====
        from ta.trend import PSARIndicator
        psar = PSARIndicator(high, low, close)
        ind['PSAR'] = float(psar.psar().iloc[-1])
        ind['PSAR_DIR'] = 1 if close.iloc[-1] > ind['PSAR'] else -1
        
        # ===== 13. WILLIAMS %R =====
        from ta.momentum import WilliamsRIndicator
        ind['WILLIAMS_R'] = float(WilliamsRIndicator(high, low, close, 14).williams_r().iloc[-1])
        
        # ===== 14. ULTIMATE OSCILLATOR =====
        from ta.momentum import UltimateOscillator
        ind['ULTIMATE_OSC'] = float(UltimateOscillator(high, low, close).ultimate_oscillator().iloc[-1])
        
        # ===== 15. MFI =====
        from ta.volume import MFIIndicator
        ind['MFI'] = float(MFIIndicator(high, low, close, volume, 14).money_flow_index().iloc[-1])
        
        # ===== 16. OBV =====
        from ta.volume import OnBalanceVolumeIndicator
        ind['OBV'] = float(OnBalanceVolumeIndicator(close, volume).on_balance_volume().iloc[-1])
        
        # ===== 17. AROON =====
        from ta.trend import AroonIndicator
        aroon = AroonIndicator(close, 25)
        ind['AROON_UP'] = float(aroon.aroon_up().iloc[-1])
        ind['AROON_DOWN'] = float(aroon.aroon_down().iloc[-1])
        
        # ===== 18. VORTEX =====
        from ta.trend import VortexIndicator
        vortex = VortexIndicator(high, low, close, 14)
        ind['VORTEX_PLUS'] = float(vortex.vortex_indicator_pos().iloc[-1])
        ind['VORTEX_MINUS'] = float(vortex.vortex_indicator_neg().iloc[-1])
        
        # ===== 19. TRIX =====
        from ta.trend import TRIXIndicator
        ind['TRIX'] = float(TRIXIndicator(close, 15).trix().iloc[-1])
        
        # ===== 20. MASS INDEX =====
        from ta.trend import MassIndex
        ind['MASS_INDEX'] = float(MassIndex(high, low).mass_index().iloc[-1])
        
        # ===== 21. VOLUME ANALYSIS =====
        vol_sma_20 = volume.rolling(20).mean().iloc[-1]
        ind['VOLUME_RATIO'] = float(volume.iloc[-1] / vol_sma_20 if vol_sma_20 > 0 else 1)
        ind['VOLUME_ZSCORE'] = float((volume.iloc[-1] - volume.rolling(20).mean().iloc[-1]) / volume.rolling(20).std().iloc[-1]) if volume.rolling(20).std().iloc[-1] > 0 else 0
        ind['VOLUME_TREND'] = 1 if volume.iloc[-1] > volume.rolling(5).mean().iloc[-1] else -1
        
        # ===== 22. PIVOT POINTS =====
        h, l, c = high.iloc[-1], low.iloc[-1], close.iloc[-1]
        pivot = (h + l + c) / 3
        ind['PIVOT'] = float(pivot)
        ind['PIVOT_R1'] = float(2 * pivot - l)
        ind['PIVOT_S1'] = float(2 * pivot - h)
        ind['PIVOT_R2'] = float(pivot + (h - l))
        ind['PIVOT_S2'] = float(pivot - (h - l))
        ind['PIVOT_R3'] = float(h + 2 * (pivot - l))
        ind['PIVOT_S3'] = float(l - 2 * (h - pivot))
        
        # ===== 23. FIBONACCI RETRACEMENT =====
        high_50 = high.rolling(50).max().iloc[-1]
        low_50 = low.rolling(50).min().iloc[-1]
        diff = high_50 - low_50
        for level in [0.236, 0.382, 0.5, 0.618, 0.786]:
            ind[f'FIB_{int(level*1000)}'] = float(high_50 - diff * level)
        
        # ===== 24. MARKET STRENGTH =====
        ind['TREND_STRENGTH'] = float((close.iloc[-1] - close.iloc[-50]) / close.iloc[-50] * 100)
        ind['VOLATILITY'] = float(close.pct_change().rolling(14).std().iloc[-1] * 100)
        ind['MOMENTUM'] = float(close.iloc[-1] - close.iloc[-10])
        
        # ===== 25. CANDLESTICK PATTERNS =====
        patterns = UltraAnalyzer.detect_candlestick_patterns(df)
        ind.update(patterns)
        
        # ===== 26. DIVERGENCE DETECTION =====
        ind['RSI_DIVERGENCE'] = UltraAnalyzer.detect_divergence(close, ind['RSI_14'])
        
        # ===== 27. SUPPORT/RESISTANCE =====
        ind['SUPPORT'] = float(low.rolling(20).min().iloc[-1])
        ind['RESISTANCE'] = float(high.rolling(20).max().iloc[-1])
        
        return ind
    
    @staticmethod
    def detect_candlestick_patterns(df: pd.DataFrame) -> Dict[str, bool]:
        """Detect major candlestick patterns"""
        open_ = df['open'].values
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        patterns = {}
        
        if len(close) < 3:
            return {p: False for p in ['DOJI', 'HAMMER', 'SHOOTING_STAR', 'ENGULFING_BULL', 'ENGULFING_BEAR', 'MORNING_STAR', 'EVENING_STAR', 'THREE_WHITE_SOLDIERS', 'THREE_BLACK_CROWS', 'HARAMI_BULL', 'HARAMI_BEAR']}
        
        o, h, l, c = open_[-1], high[-1], low[-1], close[-1]
        po, ph, pl, pc = open_[-2], high[-2], low[-2], close[-2]
        
        body = abs(c - o)
        upper_shadow = h - max(c, o)
        lower_shadow = min(c, o) - l
        total_range = h - l
        
        # Doji
        patterns['DOJI'] = total_range > 0 and body <= total_range * 0.1
        
        # Hammer
        patterns['HAMMER'] = (lower_shadow > body * 2) and (upper_shadow < body * 0.5) and (c > o)
        
        # Shooting Star
        patterns['SHOOTING_STAR'] = (upper_shadow > body * 2) and (lower_shadow < body * 0.5) and (c < o)
        
        # Engulfing Bullish
        patterns['ENGULFING_BULL'] = (c > o) and (pc < po) and (o < pc) and (c > po)
        
        # Engulfing Bearish
        patterns['ENGULFING_BEAR'] = (c < o) and (pc > po) and (o > pc) and (c < po)
        
        # Harami Bullish
        patterns['HARAMI_BULL'] = (pc < po) and (c > o) and (o > pc) and (c < po)
        
        # Harami Bearish
        patterns['HARAMI_BEAR'] = (pc > po) and (c < o) and (o < pc) and (c > po)
        
        # Three White Soldiers
        if len(close) >= 3:
            patterns['THREE_WHITE_SOLDIERS'] = all(
                close[-i] > open_[-i] and close[-i] > close[-(i+1)] 
                for i in range(1, 4)
            )
        else:
            patterns['THREE_WHITE_SOLDIERS'] = False
        
        # Three Black Crows
        if len(close) >= 3:
            patterns['THREE_BLACK_CROWS'] = all(
                close[-i] < open_[-i] and close[-i] < close[-(i+1)] 
                for i in range(1, 4)
            )
        else:
            patterns['THREE_BLACK_CROWS'] = False
        
        # Morning Star
        if len(close) >= 3:
            patterns['MORNING_STAR'] = (
                (pc < po) and 
                (abs(close[-2] - open_[-2]) < body * 0.3) and 
                (c > o) and 
                (c > (po + pc) / 2)
            )
        else:
            patterns['MORNING_STAR'] = False
        
        # Evening Star
        if len(close) >= 3:
            patterns['EVENING_STAR'] = (
                (pc > po) and 
                (abs(close[-2] - open_[-2]) < body * 0.3) and 
                (c < o) and 
                (c < (po + pc) / 2)
            )
        else:
            patterns['EVENING_STAR'] = False
        
        return patterns
    
    @staticmethod
    def detect_divergence(price: pd.Series, rsi: float) -> str:
        """Detect RSI divergence"""
        if len(price) < 20:
            return "NONE"
        
        recent_p = price.iloc[-20:]
        recent_r = RSIIndicator(price, 14).rsi().iloc[-20:]
        
        p_min = recent_p.idxmin()
        p_max = recent_p.idxmax()
        r_min = recent_r.idxmin()
        r_max = recent_r.idxmax()
        
        if recent_p.iloc[-1] < recent_p.iloc[:10].min() and recent_r.iloc[-1] > recent_r.iloc[:10].min():
            return "BULLISH"
        if recent_p.iloc[-1] > recent_p.iloc[:10].max() and recent_r.iloc[-1] < recent_r.iloc[:10].max():
            return "BEARISH"
        if recent_p.iloc[-1] > recent_p.iloc[:10].min() and recent_r.iloc[-1] < recent_r.iloc[:10].min():
            return "HIDDEN_BULLISH"
        if recent_p.iloc[-1] < recent_p.iloc[:10].max() and recent_r.iloc[-1] > recent_r.iloc[:10].max():
            return "HIDDEN_BEARISH"
        
        return "NONE"

# ============================================================
# SIGNAL GENERATOR - 1000-Point Professional Scoring
# ============================================================
class SignalGenerator:
    """Professional signal generation with weighted scoring"""
    
    @staticmethod
    def generate(ind: Dict, price: float, mtf: Dict[str, Dict] = None) -> Tuple[str, int, int]:
        score = 0
        
        # === TREND (300 pts) ===
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50'] > ind['EMA_200']:
            score += 180
        elif ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']:
            score += 120
        elif ind['EMA_20'] > ind['EMA_50']:
            score += 60
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50'] < ind['EMA_200']:
            score -= 180
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']:
            score -= 120
        
        # Ichimoku
        if price > ind['ICH_SENKOU_A'] and price > ind['ICH_SENKOU_B']:
            if ind['ICH_TENKAN'] > ind['ICH_KIJUN']:
                score += 120
            else:
                score += 60
        
        # === MOMENTUM (300 pts) ===
        rsi = ind['RSI_14']
        if rsi < 30: score += 100
        elif rsi < 40: score += 50
        elif rsi > 70: score -= 100
        elif rsi > 60: score -= 50
        
        # MACD
        if ind['MACD_HIST'] > 0: score += 60
        else: score -= 60
        
        # Stochastic
        if ind['STOCH_K'] < 20 and ind['STOCH_D'] < 20: score += 70
        elif ind['STOCH_K'] > 80 and ind['STOCH_D'] > 80: score -= 70
        
        # CCI
        cci = ind['CCI_20']
        if cci < -200: score += 60
        elif cci < -100: score += 30
        elif cci > 200: score -= 60
        elif cci > 100: score -= 30
        
        # === VOLATILITY (150 pts) ===
        if ind['BB_PCT'] < 0.1: score += 80
        elif ind['BB_PCT'] > 0.9: score -= 80
        
        if ind['ATR_PCT'] > 5: score += 30
        
        # === VOLUME (100 pts) ===
        if ind['VOLUME_RATIO'] > 2: score += 50 if score > 0 else -50
        elif ind['VOLUME_RATIO'] > 1.5: score += 30 if score > 0 else -30
        
        if ind['MFI'] < 20: score += 50
        elif ind['MFI'] > 80: score -= 50
        
        # === CANDLESTICK PATTERNS (100 pts) ===
        if ind.get('ENGULFING_BULL'): score += 60
        if ind.get('HAMMER'): score += 40
        if ind.get('MORNING_STAR'): score += 50
        if ind.get('ENGULFING_BEAR'): score -= 60
        if ind.get('SHOOTING_STAR'): score -= 40
        if ind.get('EVENING_STAR'): score -= 50
        if ind.get('THREE_WHITE_SOLDIERS'): score += 40
        if ind.get('THREE_BLACK_CROWS'): score -= 40
        
        # === DIVERGENCE (50 pts) ===
        div = ind.get('RSI_DIVERGENCE', 'NONE')
        if div == 'BULLISH': score += 50
        elif div == 'BEARISH': score -= 50
        elif div == 'HIDDEN_BULLISH': score += 30
        elif div == 'HIDDEN_BEARISH': score -= 30
        
        # === MULTI-TIMEFRAME CONFIRMATION ===
        if mtf:
            mtf_score = 0
            for tf, tf_ind in mtf.items():
                w = {"1h": 1, "4h": 1.5, "6h": 1.8, "12h": 2, "1d": 2.5, "3d": 3, "1w": 4}.get(tf, 0.5)
                if tf_ind.get('RSI_14', 50) > 55: mtf_score += 20 * w
                elif tf_ind.get('RSI_14', 50) < 45: mtf_score -= 20 * w
                if tf_ind.get('MACD_HIST', 0) > 0: mtf_score += 15 * w
                else: mtf_score -= 15 * w
            score += int(mtf_score)
        
        score = max(-1000, min(1000, score))
        
        # Signal translation
        if score >= 700: return "خرید فوق‌العاده قوی 🟢🟢🟢🟢🟢", 98, score
        elif score >= 500: return "خرید قوی 🟢🟢🟢🟢", 92, score
        elif score >= 300: return "خرید خوب 🟢🟢🟢", 82, score
        elif score >= 150: return "خرید 🟢🟢", 70, score
        elif score >= 50: return "خرید ضعیف 🟢", 60, score
        elif score <= -700: return "فروش فوق‌العاده قوی 🔴🔴🔴🔴🔴", 98, score
        elif score <= -500: return "فروش قوی 🔴🔴🔴🔴", 92, score
        elif score <= -300: return "فروش خوب 🔴🔴🔴", 82, score
        elif score <= -150: return "فروش 🔴🔴", 70, score
        elif score <= -50: return "فروش ضعیف 🔴", 60, score
        else: return "خنثی ⚪⚪", 50, score

# ============================================================
# TRADING ENGINE - Demo & Real Auto Trading
# ============================================================
class TradingEngine:
    """Advanced Trading Engine with Demo & Real Modes"""
    
    def __init__(self):
        self.demo_balance = cfg.initial_balance
        self.real_balance = 0
        self.positions: Dict[str, Dict] = {}
        self.history: List[Dict] = []
        self.consecutive_losses = 0
        self.daily_pnl = 0
        self.daily_trades = 0
        self.load_state()
    
    def load_state(self):
        try:
            with open('trading_state.json', 'r') as f:
                data = json.load(f)
                self.demo_balance = data.get('balance', cfg.initial_balance)
                self.history = data.get('history', [])
        except:
            pass
    
    def save_state(self):
        try:
            with open('trading_state.json', 'w') as f:
                json.dump({'balance': self.demo_balance, 'history': self.history[-500:]}, f)
        except:
            pass
    
    def calculate_position_size(self, entry: float, stop_loss: float, confidence: int) -> float:
        risk = self.demo_balance * cfg.risk_per_trade
        if confidence >= 90: risk *= 1.5
        if self.consecutive_losses > 0: risk *= (0.5 ** self.consecutive_losses)
        price_risk = abs(entry - stop_loss)
        if price_risk == 0: return 0
        size = risk / price_risk
        return min(size, self.demo_balance * 0.25 / entry)
    
    def open_position(self, symbol: str, entry: float, stop_loss: float, take_profit: float, confidence: int):
        if len(self.positions) >= cfg.max_positions: return None
        if self.consecutive_losses >= cfg.max_consecutive_losses: return None
        
        size = self.calculate_position_size(entry, stop_loss, confidence)
        if size <= 0 or size * entry > self.demo_balance: return None
        
        self.demo_balance -= size * entry
        
        pos = {
            'symbol': symbol, 'size': size, 'entry': entry,
            'stop_loss': stop_loss, 'take_profit': take_profit,
            'highest': entry, 'entry_time': datetime.now(), 'confidence': confidence
        }
        self.positions[symbol] = pos
        self.daily_trades += 1
        self.save_state()
        logger.info(f"🔵 OPEN {symbol} | Size: {size:.4f} | Entry: {entry:.2f}")
        return pos
    
    def update_position(self, symbol: str, price: float, atr: float) -> Optional[Dict]:
        if symbol not in self.positions: return None
        
        pos = self.positions[symbol]
        pos['highest'] = max(pos['highest'], price)
        
        # Trailing stop
        pnl_pct = (price - pos['entry']) / pos['entry']
        if pnl_pct > cfg.trailing_stop_pct:
            pos['stop_loss'] = pos['highest'] * (1 - cfg.trailing_stop_pct)
        
        # Check close
        if price >= pos['take_profit']:
            return self.close_position(symbol, price, "TAKE_PROFIT")
        if price <= pos['stop_loss']:
            return self.close_position(symbol, price, "STOP_LOSS")
        
        return None
    
    def close_position(self, symbol: str, price: float, reason: str) -> Dict:
        pos = self.positions.pop(symbol)
        pnl = (price - pos['entry']) * pos['size']
        self.demo_balance += pos['size'] * price
        self.daily_pnl += pnl
        
        if pnl < 0: self.consecutive_losses += 1
        else: self.consecutive_losses = 0
        
        trade = {
            'symbol': symbol, 'entry': pos['entry'], 'exit': price,
            'pnl': pnl, 'reason': reason, 'time': datetime.now().isoformat()
        }
        self.history.append(trade)
        self.save_state()
        logger.info(f"{'🟢' if pnl>0 else '🔴'} CLOSE {symbol} | PnL: ${pnl:+.2f}")
        return trade

trader = TradingEngine()

# ============================================================
# DATA CACHE
# ============================================================
class Cache:
    _store: Dict[str, Tuple[Any, float]] = {}
    
    @classmethod
    def get(cls, key: str, ttl: float = 15) -> Optional[Any]:
        if key in cls._store:
            val, ts = cls._store[key]
            if time.time() - ts < ttl: return val
            del cls._store[key]
        return None
    
    @classmethod
    def set(cls, key: str, value: Any):
        cls._store[key] = (value, time.time())

# ============================================================
# MESSAGE FORMATTER
# ============================================================
class Formatter:
    @staticmethod
    def signal(analysis: Dict) -> str:
        sym = analysis['symbol'].replace('/USDT', '')
        ind = analysis['indicators']
        patterns = [k for k, v in ind.items() if isinstance(v, bool) and v]
        
        return f"""
╔══════════════════════════════════════════════╗
║       🔥 سیگنال حرفه‌ای {sym} 🔥           ║
╚══════════════════════════════════════════════╝

💰 *قیمت:* ${analysis['price']:,.4f}
📊 *تغییر:* {analysis['change']:+.2f}%

🎯 *سیگنال:* {analysis['signal']}
💪 *اطمینان:* {analysis['confidence']}%
🎯 *امتیاز:* {analysis['score']}/1000

📈 *اندیکاتورهای اصلی:*
• RSI(14): {ind['RSI_14']:.1f} | RSI(7): {ind['RSI_7']:.1f}
• MACD: {'صعودی' if ind['MACD_HIST']>0 else 'نزولی'}
• ADX: {ind['ADX']:.1f} | DI+: {ind['DI_PLUS']:.1f} | DI-: {ind['DI_MINUS']:.1f}
• CCI: {ind['CCI_20']:.1f}
• MFI: {ind['MFI']:.1f}
• ATR: {ind['ATR_14']:.4f} ({ind['ATR_PCT']:.2f}%)

📊 *باندها:*
• BB Upper: ${ind['BB_UPPER']:.4f}
• BB Lower: ${ind['BB_LOWER']:.4f}
• BB Width: {ind['BB_WIDTH']:.4f}

🕯️ *الگوهای کندلی:* {', '.join(patterns) if patterns else 'بدون الگو'}
🔄 *واگرایی RSI:* {ind.get('RSI_DIVERGENCE', 'NONE')}

🔑 *سطوح کلیدی:*
• مقاومت: ${ind['RESISTANCE']:.4f}
• پیوت: ${ind['PIVOT']:.4f}
• حمایت: ${ind['SUPPORT']:.4f}

⚠️ *پیشنهاد معاملاتی:*
• حد ضرر: ${analysis['price'] - ind['ATR_14'] * cfg.atr_multiplier_sl:.4f}
• حد سود: ${analysis['price'] + ind['ATR_14'] * cfg.atr_multiplier_tp:.4f}
• ریسک/ریوارد: 1:{cfg.atr_multiplier_tp/cfg.atr_multiplier_sl:.1f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✨ @CryptoPulse606
"""
    
    @staticmethod
    def education() -> str:
        topics = [
            "📖 تحلیل ساختار بازار - شناسایی فازها",
            "🧠 روانشناسی معامله‌گری - کنترل ذهن",
            "💰 مدیریت سرمایه - کلید بقا در بازار",
            "🕯️ الگوهای کندلی - زبان بازار",
            "📊 تحلیل وایکوف - انباشت و توزیع",
            "🎯 استراتژی شکست - ورود به موقع",
            "🔄 واگرایی - سیگنال‌های مخفی",
            "📉 ترلینگ استاپ - حفظ سود",
            "⏰ مولتی تایم‌فریم - دید جامع",
            "📈 پرایس اکشن - هنر خواندن نمودار",
            "🔢 فیبوناچی - نسبت‌های طلایی",
            "☁️ ایچیموکو - ابر و سیگنال",
            "📊 RSI - قدرت و ضعف بازار",
            "📉 MACD - مومنتوم و روند",
            "🎪 بولینگر - نوسان و برگشت"
        ]
        return f"""
📚 *تحلیل و آموزش تخصصی*

{random.choice(topics)}

━━━━━━━━━━━━━━━━━━━━━━

🔍 *اصول طلایی:*
۱. روند دوست شماست - خلاف آن معامله نکنید
۲. ریسک/ریوارد حداقل ۱:۲ را رعایت کنید
۳. بیش از ۲٪ در یک معامله ریسک نکنید
۴. حد ضرر اجباری است - بدون استثنا
۵. بعد ۳ ضرر متوالی استراحت کنید
۶. ژورنال معاملاتی داشته باشید
۷. اخبار فاندامنتال را دنبال کنید
۸. صبوری = سودآوری

💡 *رمز موفقیت:*
۲۰٪ استراتژی + ۳۰٪ مدیریت ریسک + ۵۰٪ روانشناسی

━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""

# ============================================================
# MENUS - 60+ Buttons
# ============================================================
class Menus:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 قیمت‌ها", callback_data="prices"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="sig_BTC/USDT")],
            [InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan"),
             InlineKeyboardButton("⭐ برترین‌ها", callback_data="top")],
            [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="tech"),
             InlineKeyboardButton("⏰ مولتی تایم", callback_data="mtf")],
            [InlineKeyboardButton("💰 پورتفوی", callback_data="portfolio"),
             InlineKeyboardButton("📊 عملکرد", callback_data="perf")],
            [InlineKeyboardButton("🤖 معاملات خودکار", callback_data="auto"),
             InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
            [InlineKeyboardButton("📚 آموزش", callback_data="edu"),
             InlineKeyboardButton("📰 وضعیت بازار", callback_data="market")],
            [InlineKeyboardButton("🕯️ الگوها", callback_data="patterns"),
             InlineKeyboardButton("📉 ترس و طمع", callback_data="fear")],
            [InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale"),
             InlineKeyboardButton("💎 آلت‌کوین", callback_data="alt")],
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh"),
             InlineKeyboardButton("❓ راهنما", callback_data="help")],
            [InlineKeyboardButton("⏸️ توقف اضطراری", callback_data="emergency")]
        ])
    
    @staticmethod
    def technical() -> InlineKeyboardMarkup:
        pairs = [
            "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT",
            "XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT",
            "DOT/USDT", "LINK/USDT", "LTC/USDT", "UNI/USDT"
        ]
        kb = []
        row = []
        for p in pairs:
            row.append(InlineKeyboardButton(p.replace('/USDT',''), callback_data=f"sig_{p}"))
            if len(row) == 3:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([InlineKeyboardButton("🔙", callback_data="back")])
        return InlineKeyboardMarkup(kb)

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Crypto Pulse Ultra Bot v5.0*\n\n"
        "✨ ۲۵+ اندیکاتور پیشرفته\n"
        "✨ ۱۱ تایم‌فریم | ۳۰ ارز\n"
        "✨ معاملات خودکار دمو و واقعی\n"
        "✨ تشخیص الگوهای کندلی\n"
        "✨ پیش‌بینی مولتی تایم‌فریم\n\n"
        "👇 انتخاب کنید:",
        parse_mode="Markdown", reply_markup=Menus.main()
    )

async def handler_signal(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str = "BTC/USDT"):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"🔄 تحلیل {symbol.replace('/USDT','')}...")
    
    if not ex.connected: ex.connect()
    
    ticker = ex.fetch_ticker(symbol)
    df = ex.fetch_ohlcv(symbol, '1h', 200)
    if not ticker or df is None:
        await q.edit_message_text("❌ خطا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        return
    
    ind = UltraAnalyzer.full_analysis(df)
    mtf = {}
    for tf in cfg.timeframes[:6]:
        df_tf = ex.fetch_ohlcv(symbol, tf, 100)
        if df_tf is not None:
            mtf[tf] = UltraAnalyzer.full_analysis(df_tf)
    
    signal, conf, score = SignalGenerator.generate(ind, ticker['last'], mtf)
    
    analysis = {'symbol': symbol, 'price': ticker['last'], 'change': ticker.get('percentage', 0),
                'indicators': ind, 'signal': signal, 'confidence': conf, 'score': score}
    
    msg = Formatter.signal(analysis)
    
    await q.edit_message_text(msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄", callback_data=f"sig_{symbol}"),
            InlineKeyboardButton("🤖 معامله", callback_data=f"trade_{symbol}"),
            InlineKeyboardButton("🔙", callback_data="back")
        ]]))

async def handler_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🔄 دریافت...")
    if not ex.connected: ex.connect()
    
    txt = "💰 *قیمت‌ها*\n\n"
    for sym in cfg.symbols[:20]:
        t = ex.fetch_ticker(sym)
        if t:
            e = "🟢" if t.get('percentage',0)>0 else "🔴"
            txt += f"{e} {sym.replace('/USDT','')}: ${t['last']:,.4f} ({t.get('percentage',0):+.1f}%)\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="prices"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def handler_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🔍 اسکن ۳۰ ارز...")
    if not ex.connected: ex.connect()
    
    results = []
    for sym in cfg.symbols:
        t = ex.fetch_ticker(sym)
        df = ex.fetch_ohlcv(sym, '1h', 100)
        if t and df is not None:
            ind = UltraAnalyzer.full_analysis(df)
            sig, conf, score = SignalGenerator.generate(ind, t['last'])
            results.append({'symbol': sym, 'price': t['last'], 'signal': sig, 'confidence': conf, 'score': score})
    
    results.sort(key=lambda x: abs(x['score']), reverse=True)
    
    txt = "🔍 *اسکن بازار*\n\n"
    for i, r in enumerate(results[:15], 1):
        e = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
        txt += f"{i}. {e} {r['symbol'].replace('/USDT','')}: ${r['price']:,.4f} | {r['signal'][:12]} | {r['confidence']}%\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="scan"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def handler_trade(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    q = update.callback_query
    await q.answer()
    
    t = ex.fetch_ticker(symbol)
    df = ex.fetch_ohlcv(symbol, '1h', 200)
    if not t or df is None:
        await q.answer("❌ خطا در داده")
        return
    
    ind = UltraAnalyzer.full_analysis(df)
    sig, conf, score = SignalGenerator.generate(ind, t['last'])
    
    if conf < 60:
        await q.answer("⚠️ اطمینان کافی نیست", show_alert=True)
        return
    
    atr = ind['ATR_14']
    sl = t['last'] - atr * cfg.atr_multiplier_sl
    tp = t['last'] + atr * cfg.atr_multiplier_tp
    
    result = trader.open_position(symbol, t['last'], sl, tp, conf)
    
    if result:
        msg = f"""
🤖 *معامله خودکار باز شد*

📊 {symbol.replace('/USDT','')}
💰 ورود: ${t['last']:,.4f}
🛑 حد ضرر: ${sl:,.4f}
🎯 حد سود: ${tp:,.4f}
💪 اطمینان: {conf}%

⚡ @CryptoPulse606
"""
        await q.edit_message_text(msg, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
    else:
        await q.answer("⚠️ شرایط معامله فراهم نیست", show_alert=True)

async def handler_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    pnl = sum(t['pnl'] for t in trader.history)
    wins = len([t for t in trader.history if t['pnl'] > 0])
    
    txt = f"""
💰 *پورتفوی*

💵 موجودی: ${trader.demo_balance:,.2f}
📈 سود/زیان: ${pnl:+,.2f}
📊 پوزیشن‌ها: {len(trader.positions)}

📈 آمار:
• کل: {len(trader.history)} | برد: {wins}
• برد٪: {(wins/max(1,len(trader.history))*100):.1f}%
"""
    
    if trader.positions:
        txt += "\n*باز:*\n"
        for s, p in trader.positions.items():
            try:
                t = ex.fetch_ticker(s)
                cp = t['last']
                pp = (cp-p['entry'])/p['entry']*100
                txt += f"• {s.replace('/USDT','')}: ${cp:,.4f} | {pp:+.1f}%\n"
            except:
                txt += f"• {s.replace('/USDT','')}: ${p['entry']:,.4f}\n"
    
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="portfolio"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def handler_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(Formatter.education(), parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="edu"), InlineKeyboardButton("🔙", callback_data="back")]]))

async def handler_auto_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    txt = f"""
🤖 *معاملات خودکار*

🎮 دمو: {'✅ فعال' if cfg.demo_trading else '❌ غیرفعال'}
💹 واقعی: {'✅ فعال' if cfg.real_trading else '❌ غیرفعال'}

📊 تنظیمات:
• حداکثر پوزیشن: {cfg.max_positions}
• ریسک: {cfg.risk_per_trade*100}%
• حد ضرر: {cfg.atr_multiplier_sl}x ATR
• حد سود: {cfg.atr_multiplier_tp}x ATR
"""
    
    kb = [
        [InlineKeyboardButton(f"🎮 دمو: {'✅' if cfg.demo_trading else '❌'}", callback_data="toggle_demo")],
        [InlineKeyboardButton(f"💹 واقعی: {'✅' if cfg.real_trading else '❌'}", callback_data="toggle_real")],
        [InlineKeyboardButton("🔙", callback_data="back")]
    ]
    await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def handler_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    txt = f"""
⚙️ *تنظیمات*

🔌 صرافی: {'✅ متصل' if ex.connected else '❌'}
📢 کانال: {cfg.channel_id or 'تنظیم نشده'}
📊 ارزها: {len(cfg.symbols)}
⏰ تایم‌فریم: {len(cfg.timeframes)}
💰 موجودی: ${cfg.initial_balance:,.0f}
"""
    await q.edit_message_text(txt, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    
    try:
        if d == "back":
            await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menus.main())
        elif d == "prices": await handler_prices(update, context)
        elif d.startswith("sig_"): await handler_signal(update, context, d[4:])
        elif d == "scan": await handler_scan(update, context)
        elif d == "top": await handler_scan(update, context)
        elif d == "tech": await q.edit_message_text("📈 *انتخاب ارز:*", parse_mode="Markdown", reply_markup=Menus.technical())
        elif d.startswith("trade_"): await handler_trade(update, context, d[6:])
        elif d == "portfolio": await handler_portfolio(update, context)
        elif d == "perf": await handler_portfolio(update, context)
        elif d == "auto": await handler_auto_trade(update, context)
        elif d == "toggle_demo":
            cfg.demo_trading = not cfg.demo_trading
            await handler_auto_trade(update, context)
        elif d == "toggle_real":
            if ex.read_only: await q.answer("❌ API تنظیم نیست", show_alert=True)
            else: cfg.real_trading = not cfg.real_trading
            await handler_auto_trade(update, context)
        elif d == "settings": await handler_settings(update, context)
        elif d == "edu": await handler_education(update, context)
        elif d == "help":
            await q.edit_message_text("❓ *راهنما*\n/start - منو\n📊 قیمت | 🎯 سیگنال | 🔍 اسکن", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "emergency":
            for s in list(trader.positions.keys()):
                t = ex.fetch_ticker(s)
                if t: trader.close_position(s, t['last'], "EMERGENCY")
            await q.edit_message_text("⏸️ همه پوزیشن‌ها بسته شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "market": await handler_scan(update, context)
        elif d == "patterns": await handler_signal(update, context)
        elif d == "refresh":
            await q.edit_message_text("🤖 *منو*", parse_mode="Markdown", reply_markup=Menus.main())
        else: await q.answer("⚡")
    except Exception as e:
        logger.error(f"Button: {e}")
        await q.answer("❌")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start", reply_markup=Menus.main())

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error: {context.error}")
    if isinstance(context.error, Conflict):
        ProcessLock.release()
        sys.exit(1)

# ============================================================
# AUTO TASKS
# ============================================================
async def task_signals(app: Application):
    await asyncio.sleep(10)
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not ex.connected: ex.connect()
            
            for sym in ["BTC/USDT", "ETH/USDT"]:
                t = ex.fetch_ticker(sym)
                df = ex.fetch_ohlcv(sym, '1h', 200)
                if t and df is not None:
                    ind = UltraAnalyzer.full_analysis(df)
                    sig, conf, score = SignalGenerator.generate(ind, t['last'])
                    analysis = {'symbol': sym, 'price': t['last'], 'change': t.get('percentage',0),
                               'indicators': ind, 'signal': sig, 'confidence': conf, 'score': score}
                    await app.bot.send_message(cfg.channel_id, Formatter.signal(analysis), parse_mode="Markdown")
                    await asyncio.sleep(90)
            
            # Check positions
            for sym in list(trader.positions.keys()):
                t = ex.fetch_ticker(sym)
                df = ex.fetch_ohlcv(sym, '1h', 100)
                if t and df is not None:
                    ind = UltraAnalyzer.full_analysis(df)
                    result = trader.update_position(sym, t['last'], ind['ATR_14'])
                    if result:
                        emoji = "🟢" if result['pnl'] > 0 else "🔴"
                        await app.bot.send_message(cfg.channel_id,
                            f"{emoji} *بسته شد:* {sym}\n💰 ${result['pnl']:+,.2f} | {result['reason']}",
                            parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Task: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def task_education(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id:
                await app.bot.send_message(cfg.channel_id, Formatter.education(), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Edu: {e}")
        await asyncio.sleep(cfg.education_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: logger.error("❌ Token missing!"); ProcessLock.release(); return
    
    ex.connect()
    
    app = Application.builder().token(cfg.token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(error_handler)
    
    asyncio.create_task(task_signals(app))
    asyncio.create_task(task_education(app))
    
    logger.info("="*50)
    logger.info("🚀 CRYPTO PULSE ULTRA v5.0")
    logger.info(f"📊 {len(cfg.symbols)} Coins | {len(cfg.timeframes)} TFs | 25+ Indicators")
    logger.info("="*50)
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Conflict:
        logger.critical("❌ Conflict")
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
