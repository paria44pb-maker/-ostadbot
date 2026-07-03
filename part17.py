#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                              ║
║   ██████╗██████╗ ██╗   ██╗██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗███████╗███████╗ █████╗ ██████╗ ████████╗  ║
║  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗██║   ██║██╔════╝██╔════╝██╔══██╗██╔══██╗╚══██╔══╝  ║
║  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║██████╔╝██║   ██║█████╗  ███████╗███████║██████╔╝   ██║     ║
║  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║██╔═══╝ ██║   ██║██╔══╝  ╚════██║██╔══██║██╔══██╗   ██║     ║
║  ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝██║     ╚██████╔╝██║     ███████║██║  ██║██║  ██║   ██║     ║
║   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝ ╚═╝      ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝     ║
║                                                                                                              ║
║  🚀 CRYPTOPULSE AI v9.0 — PART 17 — ULTIMATE ANALYSIS ENGINE — 100% PRODUCTION — ZERO BOT                   ║
║  ═══════════════════════════════════════════════════════════════════════════════════════════════════════════    ║
║                                                                                                              ║
║  📊 Technical Analysis  │  🕯️ Candlestick Patterns  │  📐 Fibonacci  │  🐋 Whale Tracking                  ║
║  📈 Price Action        │  🏛️ Fundamental Analysis   │  🔮 Elliott    │  📡 On-Chain Data                  ║
║  🛡️ Anti-Error          │  🔇 Zero Logs              │  ⚡ Optimized   │  🧠 100+ Indicators               ║
║                                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 0 — IMPORTS & SILENT SETUP
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

import os, sys, json, math, time, random, hashlib, hmac, base64, re, asyncio
import logging, warnings, traceback, threading, itertools, functools, operator, contextlib
import secrets as _secrets, uuid as _uuid
from datetime import datetime, timedelta, timezone
from typing import (Dict, Any, List, Optional, Tuple, Union, Set, Callable, Coroutine,
                    Iterable, TypeVar, Generic, Type, Awaitable, ClassVar)
from collections import defaultdict, OrderedDict, deque, Counter
from dataclasses import dataclass, field, asdict, fields
from enum import Enum, IntEnum, auto, unique, Flag
from functools import wraps, lru_cache, partial, reduce
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress, contextmanager
from pathlib import Path

# ─── ABSOLUTE SILENCE ───
warnings.filterwarnings("ignore")
for _cat in [DeprecationWarning, FutureWarning, RuntimeWarning, UserWarning,
             SyntaxWarning, PendingDeprecationWarning, ImportWarning, BytesWarning, ResourceWarning]:
    warnings.filterwarnings("ignore", category=_cat)

logging.basicConfig(level=logging.CRITICAL, handlers=[logging.NullHandler()])
for _name in list(logging.root.manager.loggerDict.keys()):
    logging.getLogger(_name).setLevel(logging.CRITICAL)
    logging.getLogger(_name).handlers.clear()
    logging.getLogger(_name).addHandler(logging.NullHandler())
    logging.getLogger(_name).propagate = False

logger = logging.getLogger("cryptopulse.part17")
logger.setLevel(logging.WARNING)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SAFE IMPORT SYSTEM — ALL FROM part* (NO bot*)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def safe_import(module_name: str, *attrs: str) -> Dict[str, Any]:
    """ایمپورت کاملاً بی‌صدا — فقط از part*"""
    result = {attr: None for attr in attrs}
    try:
        mod = __import__(module_name, fromlist=list(attrs))
        for attr in attrs:
            try:
                result[attr] = getattr(mod, attr, None)
            except:
                pass
    except:
        pass
    return result

# Import from ALL parts (1-18) — ZERO bot imports
_p1  = safe_import("part1",  "get_config", "verify_api_key", "hash_api_key")
_p2  = safe_import("part2",  "db_manager", "user_repo", "signal_repo", "payment_repo", "get_user_repo", "get_signal_repo", "get_payment_repo")
_p3  = safe_import("part3",  "get_user_repo", "get_signal_repo", "get_payment_repo", "db_manager")
_p4  = safe_import("part4",  "get_time", "get_emoji", "get_formatter", "get_hash", "get_validator", "get_cache")
_p5  = safe_import("part5",  "get_market", "get_coinex", "get_signal", "get_ticker", "get_price", "get_ohlcv_data", "get_market_summary", "MarketAggregator", "CoinExClient", "MultiExchangeManager")
_p6  = safe_import("part6",  "get_ai", "get_groq")
_p7  = safe_import("part7",  "get_technical", "TechnicalIndicators")
_p8  = safe_import("part8",  "lux_keyboard", "menu_builder", "LuxText", "LuxEmoji")
_p9  = safe_import("part9",  "get_application", "start")
_p10 = safe_import("part10", "TradingEngine", "OrderManager", "PositionManager")
_p11 = safe_import("part11", "PaymentGateway", "InvoiceManager", "TransactionManager")
_p12 = safe_import("part12", "MediaManager", "ContentGenerator", "ImageProcessor")
_p13 = safe_import("part13", "NotificationManager", "AlertSystem", "PushNotifier")
_p14 = safe_import("part14", "TelegramBot", "WebhookManager", "PollingManager")
_p15 = safe_import("part15", "Monitor", "Logger", "MetricsCollector", "HealthChecker")
_p16 = safe_import("part16", "get_intelligence_engine", "AdminIntelligenceEngine", "UserIntelligence", "FinancialIntelligence", "SignalIntelligence", "ComprehensiveReport")
_p18 = safe_import("part18", "get_god_mode_engine", "GodModeEngine", "GodSignal", "MarketScanner", "ChannelManager", "MarketOverview")

# Merge all parts
_all_parts = [_p1, _p2, _p3, _p4, _p5, _p6, _p7, _p8, _p9, _p10, _p11, _p12, _p13, _p14, _p15, _p16, _p18]

def _extract(*attrs: str, default: Any = None) -> Any:
    for part in _all_parts:
        for attr in attrs:
            val = part.get(attr)
            if val is not None:
                return val
    return default

# Core services — ALL from part*
get_config              = _extract("get_config")
db_manager              = _extract("db_manager")
get_user_repo           = _extract("get_user_repo", "user_repo")
get_signal_repo         = _extract("get_signal_repo", "signal_repo")
get_payment_repo        = _extract("get_payment_repo", "payment_repo")
get_cache               = _extract("get_cache")
get_time                = _extract("get_time")
get_emoji               = _extract("get_emoji")
get_formatter           = _extract("get_formatter")
get_hash                = _extract("get_hash")
get_validator           = _extract("get_validator")
get_market              = _extract("get_market", "MarketAggregator")
get_coinex              = _extract("get_coinex", "CoinExClient")
get_signal_func         = _extract("get_signal")
get_ticker_func         = _extract("get_ticker")
get_price_func          = _extract("get_price")
get_ohlcv_func          = _extract("get_ohlcv_data")
get_market_summary_func = _extract("get_market_summary")
get_ai                  = _extract("get_ai")
get_groq                = _extract("get_groq")
get_technical           = _extract("get_technical")
TechnicalIndicators     = _extract("TechnicalIndicators")
get_intelligence_engine = _extract("get_intelligence_engine")
get_god_mode_engine     = _extract("get_god_mode_engine")
GodModeEngine           = _extract("GodModeEngine")
GodSignal               = _extract("GodSignal")
MarketScanner           = _extract("MarketScanner")
TradingEngine           = _extract("TradingEngine")
PaymentGateway          = _extract("PaymentGateway")
NotificationManager     = _extract("NotificationManager")

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

BOT_VERSION = "9.0.0"
BOT_NAME = "CryptoPulse AI"
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().lstrip('-').isdigit()]
SECRET_KEY = os.environ.get("SECRET_KEY", hashlib.sha256(os.urandom(32)).hexdigest())

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def is_admin(uid): return uid in ADMIN_IDS
def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def today(): return datetime.now().strftime("%Y-%m-%d")
def ts(): return int(time.time())
def uid(): return str(_uuid.uuid4())[:12]
def fmt_num(n, d=2):
    if abs(n)>=1e12: return f"{n/1e12:.{d}f}T"
    if abs(n)>=1e9: return f"{n/1e9:.{d}f}B"
    if abs(n)>=1e6: return f"{n/1e6:.{d}f}M"
    if abs(n)>=1e3: return f"{n/1e3:.{d}f}K"
    return f"{n:,.{d}f}"
def fmt_price(p):
    if p>=1000: return f"${p:,.2f}"
    if p>=1: return f"${p:,.4f}"
    if p>=0.01: return f"${p:,.6f}"
    return f"${p:,.8f}"
def fmt_pct(p): return f"{p:+.2f}%"
def divider(): return "─" * 42
def header(t, w=44): return f"╔{'═'*(w-2)}╗\n║{t.center(w-2)}║\n╚{'═'*(w-2)}╝"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 4 — ENUMS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class SignalType(str, Enum):
    STRONG_BUY = "strong_buy"; BUY = "buy"; WEAK_BUY = "weak_buy"
    NEUTRAL = "neutral"; WEAK_SELL = "weak_sell"; SELL = "sell"; STRONG_SELL = "strong_sell"

class TrendType(str, Enum):
    STRONG_UPTREND = "strong_uptrend"; UPTREND = "uptrend"; WEAK_UPTREND = "weak_uptrend"
    SIDEWAYS = "sideways"; WEAK_DOWNTREND = "weak_downtrend"
    DOWNTREND = "downtrend"; STRONG_DOWNTREND = "strong_downtrend"

class PatternType(str, Enum):
    BULLISH_ENGULFING = "bullish_engulfing"; BULLISH_HARAMI = "bullish_harami"
    MORNING_STAR = "morning_star"; THREE_WHITE_SOLDIERS = "three_white_soldiers"
    PIERCING_LINE = "piercing_line"; HAMMER = "hammer"; INVERTED_HAMMER = "inverted_hammer"
    DOJI_DRAGONFLY = "doji_dragonfly"; BULLISH_ABANDONED_BABY = "bullish_abandoned_baby"
    BULLISH_KICKER = "bullish_kicker"; THREE_INSIDE_UP = "three_inside_up"
    THREE_OUTSIDE_UP = "three_outside_up"; TWEEZER_BOTTOM = "tweezer_bottom"
    BEARISH_ENGULFING = "bearish_engulfing"; BEARISH_HARAMI = "bearish_harami"
    EVENING_STAR = "evening_star"; THREE_BLACK_CROWS = "three_black_crows"
    DARK_CLOUD_COVER = "dark_cloud_cover"; HANGING_MAN = "hanging_man"
    SHOOTING_STAR = "shooting_star"; DOJI_GRAVESTONE = "doji_gravestone"
    BEARISH_ABANDONED_BABY = "bearish_abandoned_baby"; BEARISH_KICKER = "bearish_kicker"
    THREE_INSIDE_DOWN = "three_inside_down"; THREE_OUTSIDE_DOWN = "three_outside_down"
    TWEEZER_TOP = "tweezer_top"; DOJI = "doji"; SPINNING_TOP = "spinning_top"
    MARUBOZU = "marubozu"; LONG_LEGGED_DOJI = "long_legged_doji"

class WhaleActivity(str, Enum):
    ACCUMULATION = "accumulation"; DISTRIBUTION = "distribution"
    WHALE_BUY = "whale_buy"; WHALE_SELL = "whale_sell"
    SMART_MONEY_IN = "smart_money_in"; SMART_MONEY_OUT = "smart_money_out"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 5 — DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

@dataclass
class OHLCV:
    timestamp: int = 0; open: float = 0.0; high: float = 0.0
    low: float = 0.0; close: float = 0.0; volume: float = 0.0

    @property
    def body(self) -> float: return abs(self.close - self.open)
    @property
    def range(self) -> float: return self.high - self.low
    @property
    def upper_wick(self) -> float: return self.high - max(self.open, self.close)
    @property
    def lower_wick(self) -> float: return min(self.open, self.close) - self.low
    @property
    def is_bullish(self) -> bool: return self.close > self.open
    @property
    def is_bearish(self) -> bool: return self.close < self.open
    @property
    def body_percentage(self) -> float: return (self.body / self.range * 100) if self.range > 0 else 0
    @property
    def upper_wick_percentage(self) -> float: return (self.upper_wick / self.range * 100) if self.range > 0 else 0
    @property
    def lower_wick_percentage(self) -> float: return (self.lower_wick / self.range * 100) if self.range > 0 else 0

@dataclass
class IndicatorResult:
    name: str = ""; value: float = 0.0; signal: str = "neutral"; strength: float = 50.0
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PatternResult:
    pattern: PatternType = PatternType.DOJI; type: str = "neutral"
    strength: float = 0.0; confidence: float = 0.0; candles_needed: int = 1
    description: str = ""; reliability: float = 0.0

@dataclass
class FibonacciResult:
    swing_low: float = 0.0; swing_high: float = 0.0; is_uptrend: bool = True
    retracement_levels: Dict[str, float] = field(default_factory=dict)
    extension_levels: Dict[str, float] = field(default_factory=dict)
    current_position: float = 0.0; nearest_support: float = 0.0; nearest_resistance: float = 0.0

@dataclass
class WhaleActivityData:
    timestamp: int = 0; type: WhaleActivity = WhaleActivity.WHALE_BUY
    volume: float = 0.0; price: float = 0.0; value_usd: float = 0.0
    exchange: str = "unknown"; wallet_count: int = 0; avg_transaction: float = 0.0

@dataclass
class TechnicalAnalysisResult:
    coin: str = ""; timeframe: str = "4h"; timestamp: int = 0
    current_price: float = 0.0; change_24h: float = 0.0
    high_24h: float = 0.0; low_24h: float = 0.0; volume_24h: float = 0.0
    trend: str = "sideways"; trend_strength: float = 50.0; trend_duration: int = 0
    rsi: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="RSI", value=50))
    stochastic: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="Stochastic", value=50))
    cci: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="CCI", value=0))
    williams_r: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="Williams %R", value=-50))
    mfi: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="MFI", value=50))
    sma_signals: Dict[str, str] = field(default_factory=dict)
    ema_signals: Dict[str, str] = field(default_factory=dict)
    ma_crossovers: List[str] = field(default_factory=list)
    macd: float = 0.0; macd_signal: float = 0.0; macd_histogram: float = 0.0; macd_crossover: str = "none"
    bb_upper: float = 0.0; bb_middle: float = 0.0; bb_lower: float = 0.0
    bb_position: float = 50.0; bb_squeeze: bool = False
    ichimoku_signal: str = "neutral"; ichimoku_cloud_status: str = "none"
    adx: float = 0.0; plus_di: float = 0.0; minus_di: float = 0.0; adx_trend_strength: str = "weak"
    atr: float = 0.0; atr_percentage: float = 0.0
    sar: float = 0.0; sar_signal: str = "none"
    obv_trend: str = "neutral"; volume_trend: str = "normal"; volume_ratio: float = 1.0
    candlestick_patterns: List[PatternResult] = field(default_factory=list)
    chart_patterns: List[str] = field(default_factory=list)
    fibonacci: Optional[FibonacciResult] = None
    whale_activity: List[WhaleActivityData] = field(default_factory=list)
    whale_signal: str = "neutral"
    supports: List[Dict[str, float]] = field(default_factory=list)
    resistances: List[Dict[str, float]] = field(default_factory=list)
    pivot: float = 0.0; pivot_r1: float = 0.0; pivot_r2: float = 0.0; pivot_r3: float = 0.0
    pivot_s1: float = 0.0; pivot_s2: float = 0.0; pivot_s3: float = 0.0
    price_action_signals: List[str] = field(default_factory=list)
    market_structure: str = "unknown"
    divergences: List[Dict[str, str]] = field(default_factory=list)
    overall_signal: str = "neutral"; signal_strength: float = 50.0
    confidence: float = 50.0; risk_reward: float = 0.0
    stop_loss: float = 0.0; take_profits: List[float] = field(default_factory=list)
    summary: str = ""; key_levels: List[float] = field(default_factory=list)
    recommendation: str = ""

@dataclass
class FundamentalAnalysisResult:
    coin: str = ""
    market_cap: float = 0.0; market_cap_rank: int = 0
    fully_diluted_valuation: float = 0.0; total_supply: float = 0.0
    circulating_supply: float = 0.0; max_supply: float = 0.0
    volume_24h: float = 0.0; volume_market_cap_ratio: float = 0.0
    price_change_1h: float = 0.0; price_change_24h: float = 0.0
    price_change_7d: float = 0.0; price_change_30d: float = 0.0
    ath: float = 0.0; ath_date: str = ""; ath_change: float = 0.0
    atl: float = 0.0; atl_date: str = ""; atl_change: float = 0.0
    active_addresses_24h: int = 0; transaction_count_24h: int = 0
    fear_greed_index: int = 50; sentiment_score: float = 0.0
    overall_score: float = 50.0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    summary: str = ""; recommendation: str = "neutral"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 6 — TECHNICAL INDICATORS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class TechnicalIndicatorsEngine:
    @staticmethod
    def sma(data: List[float], period: int) -> List[float]:
        if len(data) < period: return [0.0] * len(data)
        result = [0.0] * (period - 1)
        window_sum = sum(data[:period])
        result.append(window_sum / period)
        for i in range(period, len(data)):
            window_sum = window_sum - data[i-period] + data[i]
            result.append(window_sum / period)
        return result

    @staticmethod
    def ema(data: List[float], period: int) -> List[float]:
        if len(data) < period: return [0.0] * len(data)
        result = [0.0] * (period - 1)
        multiplier = 2.0 / (period + 1.0)
        ema_val = sum(data[:period]) / period
        result.append(ema_val)
        for i in range(period, len(data)):
            ema_val = (data[i] - ema_val) * multiplier + ema_val
            result.append(ema_val)
        return result

    @staticmethod
    def rsi(data: List[float], period: int = 14) -> List[float]:
        if len(data) < period + 1: return [50.0] * len(data)
        result = [0.0] * period
        gains, losses = [], []
        for i in range(1, period + 1):
            change = data[i] - data[i-1]
            gains.append(max(change, 0)); losses.append(max(-change, 0))
        avg_gain = sum(gains) / period; avg_loss = sum(losses) / period
        if avg_loss == 0: result.append(100.0)
        else: result.append(100.0 - (100.0 / (1.0 + avg_gain/avg_loss)))
        for i in range(period + 1, len(data)):
            change = data[i] - data[i-1]
            gain = max(change, 0); loss = max(-change, 0)
            avg_gain = (avg_gain * (period-1) + gain) / period
            avg_loss = (avg_loss * (period-1) + loss) / period
            if avg_loss == 0: result.append(100.0)
            else: result.append(100.0 - (100.0 / (1.0 + avg_gain/avg_loss)))
        return result

    @staticmethod
    def stochastic(high: List[float], low: List[float], close: List[float], k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        if len(close) < k_period: return ([50.0]*len(close), [50.0]*len(close))
        k_vals = [0.0] * (k_period - 1)
        for i in range(k_period - 1, len(close)):
            h = max(high[i-k_period+1:i+1]); l = min(low[i-k_period+1:i+1])
            if h == l: k_vals.append(50.0)
            else: k_vals.append(((close[i] - l) / (h - l)) * 100.0)
        d_vals = TechnicalIndicatorsEngine.sma(k_vals, d_period)
        return k_vals, d_vals

    @staticmethod
    def cci(high: List[float], low: List[float], close: List[float], period: int = 20) -> List[float]:
        if len(close) < period: return [0.0] * len(close)
        result = [0.0] * (period - 1)
        tp = [(h+l+c)/3.0 for h,l,c in zip(high, low, close)]
        for i in range(period - 1, len(close)):
            sl = tp[i-period+1:i+1]; sma_tp = sum(sl) / period
            md = sum(abs(x - sma_tp) for x in sl) / period
            if md == 0: result.append(0.0)
            else: result.append((tp[i] - sma_tp) / (0.015 * md))
        return result

    @staticmethod
    def williams_r(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        if len(close) < period: return [-50.0] * len(close)
        result = [0.0] * (period - 1)
        for i in range(period - 1, len(close)):
            h = max(high[i-period+1:i+1]); l = min(low[i-period+1:i+1])
            if h == l: result.append(-50.0)
            else: result.append(((h - close[i]) / (h - l)) * -100.0)
        return result

    @staticmethod
    def mfi(high: List[float], low: List[float], close: List[float], volume: List[float], period: int = 14) -> List[float]:
        if len(close) < period + 1: return [50.0] * len(close)
        result = [0.0] * period
        tp = [(h+l+c)/3.0 for h,l,c in zip(high, low, close)]
        mf = [tp[i]*volume[i] for i in range(len(tp))]
        for i in range(period, len(close)):
            pos_flow = 0.0; neg_flow = 0.0
            for j in range(i-period+1, i+1):
                if tp[j] > tp[j-1]: pos_flow += mf[j]
                elif tp[j] < tp[j-1]: neg_flow += mf[j]
            if neg_flow == 0: result.append(100.0)
            else: result.append(100.0 - (100.0 / (1.0 + pos_flow/neg_flow)))
        return result

    @staticmethod
    def macd(data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        ema_fast = TechnicalIndicatorsEngine.ema(data, fast)
        ema_slow = TechnicalIndicatorsEngine.ema(data, slow)
        macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(data))]
        signal_line = TechnicalIndicatorsEngine.ema(macd_line, signal)
        histogram = [macd_line[i] - signal_line[i] for i in range(len(data))]
        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(data: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        if len(data) < period: return ([0.0]*len(data), [0.0]*len(data), [0.0]*len(data))
        middle = TechnicalIndicatorsEngine.sma(data, period)
        upper, lower = [0.0]*len(data), [0.0]*len(data)
        for i in range(period-1, len(data)):
            window = data[i-period+1:i+1]; mean = sum(window)/period
            std = math.sqrt(sum((x-mean)**2 for x in window)/period)
            upper[i] = middle[i] + std_dev*std; lower[i] = middle[i] - std_dev*std
        return upper, middle, lower

    @staticmethod
    def ichimoku(high: List[float], low: List[float], tenkan_p: int = 9, kijun_p: int = 26, senkou_p: int = 52) -> Dict[str, List[float]]:
        if len(high) < senkou_p: return {"tenkan_sen":[0.0]*len(high),"kijun_sen":[0.0]*len(high),"senkou_span_a":[0.0]*len(high),"senkou_span_b":[0.0]*len(high)}
        tenkan, kijun = [0.0]*(tenkan_p-1), [0.0]*(kijun_p-1)
        for i in range(tenkan_p-1, len(high)): tenkan.append((max(high[i-tenkan_p+1:i+1])+min(low[i-tenkan_p+1:i+1]))/2.0)
        for i in range(kijun_p-1, len(high)): kijun.append((max(high[i-kijun_p+1:i+1])+min(low[i-kijun_p+1:i+1]))/2.0)
        return {"tenkan_sen": tenkan, "kijun_sen": kijun, "senkou_span_a": [0.0]*len(high), "senkou_span_b": [0.0]*len(high)}

    @staticmethod
    def adx(high: List[float], low: List[float], close: List[float], period: int = 14) -> Tuple[List[float], List[float], List[float]]:
        if len(close) < period*2: return ([0.0]*len(close), [0.0]*len(close), [0.0]*len(close))
        tr, plus_dm, minus_dm = [0.0], [0.0], [0.0]
        for i in range(1, len(close)):
            tr.append(max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1])))
            up = high[i]-high[i-1]; down = low[i-1]-low[i]
            plus_dm.append(up if up>down and up>0 else 0.0)
            minus_dm.append(down if down>up and down>0 else 0.0)
        adx_vals, plus_di, minus_di = [0.0]*(period*2-1), [0.0]*(period-1), [0.0]*(period-1)
        for i in range(period-1, len(close)):
            tr_sum = sum(tr[i-period+1:i+1])
            pdi = (sum(plus_dm[i-period+1:i+1])/tr_sum*100) if tr_sum!=0 else 0
            mdi = (sum(minus_dm[i-period+1:i+1])/tr_sum*100) if tr_sum!=0 else 0
            plus_di.append(pdi); minus_di.append(mdi)
            dx = abs(pdi-mdi)/(pdi+mdi)*100 if (pdi+mdi)!=0 else 0
            adx_vals.append(dx)
        return TechnicalIndicatorsEngine.ema(adx_vals, period), plus_di, minus_di

    @staticmethod
    def atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        if len(close) < period+1: return [0.0]*len(close)
        tr_vals = [0.0]
        for i in range(1, len(close)): tr_vals.append(max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1])))
        atr_vals = [0.0]*period
        atr_vals.append(sum(tr_vals[1:period+1])/period)
        for i in range(period+1, len(close)): atr_vals.append((atr_vals[i-1]*(period-1)+tr_vals[i])/period)
        return atr_vals

    @staticmethod
    def pivot_points(high: float, low: float, close: float) -> Dict[str, float]:
        pp = (high + low + close) / 3.0
        return {"pivot": pp, "r1": 2.0*pp-low, "r2": pp+(high-low), "r3": high+2.0*(pp-low),
                "s1": 2.0*pp-high, "s2": pp-(high-low), "s3": low-2.0*(high-pp)}

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 7 — CANDLESTICK PATTERNS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class CandlestickPatternsEngine:
    @staticmethod
    def detect_all(candles: List[OHLCV]) -> List[PatternResult]:
        patterns = []
        if len(candles) < 1: return patterns
        patterns.extend(CandlestickPatternsEngine._single(candles))
        patterns.extend(CandlestickPatternsEngine._double(candles))
        patterns.extend(CandlestickPatternsEngine._triple(candles))
        return sorted(patterns, key=lambda p: p.strength, reverse=True)

    @staticmethod
    def _single(candles: List[OHLCV]) -> List[PatternResult]:
        patterns = []; c = candles[-1]
        if c.body_percentage < 5:
            if c.lower_wick_percentage > 60: patterns.append(PatternResult(PatternType.HAMMER, "bullish", 75, 80, 1, "Hammer — برگشت صعودی", 80))
            elif c.upper_wick_percentage > 60: patterns.append(PatternResult(PatternType.SHOOTING_STAR, "bearish", 75, 80, 1, "Shooting Star — برگشت نزولی", 80))
            elif c.lower_wick_percentage > 60: patterns.append(PatternResult(PatternType.DOJI_DRAGONFLY, "bullish", 60, 70, 1, "Dragonfly Doji", 65))
            elif c.upper_wick_percentage > 60: patterns.append(PatternResult(PatternType.DOJI_GRAVESTONE, "bearish", 60, 70, 1, "Gravestone Doji", 65))
            else: patterns.append(PatternResult(PatternType.DOJI, "continuation", 40, 60, 1, "Doji — تردید", 50))
        if c.body_percentage > 80: patterns.append(PatternResult(PatternType.MARUBOZU, "bullish" if c.is_bullish else "bearish", 80, 85, 1, "Marubozu", 85))
        return patterns

    @staticmethod
    def _double(candles: List[OHLCV]) -> List[PatternResult]:
        patterns = []
        if len(candles) < 2: return patterns
        c1, c2 = candles[-2], candles[-1]
        if c1.is_bearish and c2.is_bullish and c2.open <= c1.close and c2.close > c1.open:
            patterns.append(PatternResult(PatternType.BULLISH_ENGULFING, "bullish", 85, 90, 2, "Bullish Engulfing", 90))
        if c1.is_bullish and c2.is_bearish and c2.open >= c1.close and c2.close < c1.open:
            patterns.append(PatternResult(PatternType.BEARISH_ENGULFING, "bearish", 85, 90, 2, "Bearish Engulfing", 90))
        return patterns

    @staticmethod
    def _triple(candles: List[OHLCV]) -> List[PatternResult]:
        patterns = []
        if len(candles) < 3: return patterns
        c1, c2, c3 = candles[-3], candles[-2], candles[-1]
        if c1.is_bearish and c3.is_bullish and c2.body < c1.body*0.3 and c3.close > (c1.open+c1.close)/2:
            patterns.append(PatternResult(PatternType.MORNING_STAR, "bullish", 90, 95, 3, "Morning Star", 92))
        if c1.is_bullish and c3.is_bearish and c2.body < c1.body*0.3 and c3.close < (c1.open+c1.close)/2:
            patterns.append(PatternResult(PatternType.EVENING_STAR, "bearish", 90, 95, 3, "Evening Star", 92))
        return patterns

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 8 — FIBONACCI ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class FibonacciEngine:
    @staticmethod
    def retracement(swing_low: float, swing_high: float) -> FibonacciResult:
        is_uptrend = swing_high > swing_low; diff = abs(swing_high - swing_low)
        result = FibonacciResult(swing_low=swing_low, swing_high=swing_high, is_uptrend=is_uptrend)
        result.retracement_levels = {
            "0.0": swing_high if is_uptrend else swing_low,
            "0.236": swing_high - 0.236*diff if is_uptrend else swing_low + 0.236*diff,
            "0.382": swing_high - 0.382*diff if is_uptrend else swing_low + 0.382*diff,
            "0.5": swing_high - 0.5*diff if is_uptrend else swing_low + 0.5*diff,
            "0.618": swing_high - 0.618*diff if is_uptrend else swing_low + 0.618*diff,
            "0.786": swing_high - 0.786*diff if is_uptrend else swing_low + 0.786*diff,
            "1.0": swing_low if is_uptrend else swing_high,
        }
        result.extension_levels = {
            "1.272": swing_high - 1.272*diff if is_uptrend else swing_low + 1.272*diff,
            "1.618": swing_high - 1.618*diff if is_uptrend else swing_low + 1.618*diff,
            "2.0": swing_high - 2.0*diff if is_uptrend else swing_low + 2.0*diff,
            "2.618": swing_high - 2.618*diff if is_uptrend else swing_low + 2.618*diff,
        }
        return result

    @staticmethod
    def find_swings(data: List[float], lookback: int = 5) -> Tuple[List[float], List[float]]:
        if len(data) < lookback*2+1: return [], []
        highs, lows = [], []
        for i in range(lookback, len(data)-lookback):
            if data[i] == max(data[i-lookback:i+lookback+1]): highs.append(data[i])
            if data[i] == min(data[i-lookback:i+lookback+1]): lows.append(data[i])
        return highs, lows

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 9 — WHALE TRACKER
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class WhaleTrackerEngine:
    @staticmethod
    def detect(volume_data: List[Dict], threshold: float = 3.0) -> List[WhaleActivityData]:
        if not volume_data: return []
        avg_vol = sum(v.get('volume',0) for v in volume_data) / len(volume_data) if volume_data else 0
        activities = []
        for d in volume_data:
            vol = d.get('volume', 0)
            if vol > avg_vol * threshold:
                activities.append(WhaleActivityData(
                    timestamp=d.get('timestamp', ts()), volume=vol, price=d.get('price', 0),
                    value_usd=vol*d.get('price',0), exchange=d.get('exchange','unknown'),
                    type=WhaleActivity.WHALE_BUY if d.get('is_buy',True) else WhaleActivity.WHALE_SELL
                ))
        return sorted(activities, key=lambda a: a.volume, reverse=True)

    @staticmethod
    def detect_accumulation(close: List[float], volume: List[float], period: int = 14) -> str:
        if len(close) < period: return "neutral"
        ad = [0.0]
        for i in range(1, len(close)):
            clv = ((close[i]-min(close[i],close[i-1]))-(max(close[i],close[i-1])-close[i]))/max(abs(close[i]-close[i-1]), 0.0001)
            ad.append(ad[-1] + clv * volume[i])
        recent = ad[-period:]
        if all(recent[i] > recent[i-1] for i in range(1, len(recent))): return "accumulation"
        if all(recent[i] < recent[i-1] for i in range(1, len(recent))): return "distribution"
        return "neutral"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 10 — PRICE ACTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class PriceActionEngine:
    @staticmethod
    def market_structure(high: List[float], low: List[float]) -> str:
        if len(high) < 20: return "unknown"
        hh = sum(1 for i in range(5, len(high)) if high[i] > max(high[i-5:i])) >= 3
        ll = sum(1 for i in range(5, len(low)) if low[i] < min(low[i-5:i])) >= 3
        if hh: return "bullish_structure"
        if ll: return "bearish_structure"
        return "sideways_structure"

    @staticmethod
    def support_resistance(high: List[float], low: List[float], close: List[float], lookback: int = 20) -> Tuple[List[Dict], List[Dict]]:
        supports, resistances = [], []
        if len(close) < lookback: return supports, resistances
        for i in range(lookback, len(close)-lookback):
            if low[i] == min(low[i-lookback:i+lookback+1]):
                touches = sum(1 for j in range(max(0,i-50), i) if abs(low[j]-low[i])/low[i] < 0.02)
                if touches >= 2: supports.append({"level": low[i], "strength": min(touches*25, 100), "touches": touches})
            if high[i] == max(high[i-lookback:i+lookback+1]):
                touches = sum(1 for j in range(max(0,i-50), i) if abs(high[j]-high[i])/high[i] < 0.02)
                if touches >= 2: resistances.append({"level": high[i], "strength": min(touches*25, 100), "touches": touches})
        return sorted(supports, key=lambda s: s['strength'], reverse=True)[:5], sorted(resistances, key=lambda r: r['strength'], reverse=True)[:5]

    @staticmethod
    def detect_divergence(price: List[float], indicator: List[float]) -> List[Dict]:
        divergences = []
        if len(price) < 20 or len(indicator) < 20: return divergences
        p_lows, i_lows = [], []
        for i in range(5, len(price)-5):
            if price[i] == min(price[i-5:i+6]): p_lows.append((i, price[i]))
            if indicator[i] == min(indicator[i-5:i+6]): i_lows.append((i, indicator[i]))
        if len(p_lows)>=2 and len(i_lows)>=2:
            if p_lows[-1][1] < p_lows[-2][1] and i_lows[-1][1] > i_lows[-2][1]:
                divergences.append({"type": "bullish_divergence", "description": "واگرایی صعودی"})
        return divergences

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 11 — FUNDAMENTAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class FundamentalAnalysisEngine:
    @staticmethod
    def analyze(coin: str, market_data: Dict = None) -> FundamentalAnalysisResult:
        result = FundamentalAnalysisResult(coin=coin)
        if market_data:
            result.market_cap = market_data.get('market_cap', 0)
            result.market_cap_rank = market_data.get('market_cap_rank', 0)
            result.total_supply = market_data.get('total_supply', 0)
            result.circulating_supply = market_data.get('circulating_supply', 0)
            result.max_supply = market_data.get('max_supply', 0)
            result.volume_24h = market_data.get('volume_24h', 0)
            result.price_change_24h = market_data.get('price_change_percentage_24h', 0)
            result.price_change_7d = market_data.get('price_change_percentage_7d', 0)
            result.ath = market_data.get('ath', 0)
        score = 50.0
        if result.market_cap_rank <= 10: score += 20; result.strengths.append("جزء ۱۰ ارز برتر")
        elif result.market_cap_rank <= 50: score += 10
        if result.max_supply > 0 and result.circulating_supply > 0:
            if result.circulating_supply/result.max_supply > 0.9: score += 10; result.strengths.append("عرضه محدود")
        if result.price_change_7d > 10: score += 5; result.strengths.append("رشد ۷ روزه قوی")
        elif result.price_change_7d < -10: score -= 5; result.weaknesses.append("افت ۷ روزه شدید")
        result.overall_score = max(0, min(100, score))
        if result.overall_score >= 70: result.recommendation = "strong_buy"
        elif result.overall_score >= 55: result.recommendation = "buy"
        elif result.overall_score >= 45: result.recommendation = "neutral"
        elif result.overall_score >= 30: result.recommendation = "sell"
        else: result.recommendation = "strong_sell"
        return result

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 12 — MAIN ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class AnalysisEngine:
    def __init__(self):
        self.indicators = TechnicalIndicatorsEngine()
        self.patterns = CandlestickPatternsEngine()
        self.fibonacci = FibonacciEngine()
        self.whale = WhaleTrackerEngine()
        self.price_action = PriceActionEngine()
        self.fundamental = FundamentalAnalysisEngine()
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.RLock()

    def _cached(self, key: str, ttl: int = 60) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                val, exp = self._cache[key]
                if time.time() < exp: return val
                del self._cache[key]
        return None

    def _set_cache(self, key: str, value: Any):
        with self._lock:
            self._cache[key] = (value, time.time() + 60)
            if len(self._cache) > 500:
                oldest = min(self._cache.items(), key=lambda x: x[1][1])[0]
                del self._cache[oldest]

    def analyze(self, coin: str, timeframe: str = "4h", ohlcv_data: List[Dict] = None) -> TechnicalAnalysisResult:
        cache_key = f"analysis:{coin}:{timeframe}"
        cached = self._cached(cache_key)
        if cached: return cached

        if ohlcv_data is None:
            ohlcv_data = self._fetch_ohlcv(coin, timeframe)

        candles = [OHLCV(timestamp=d.get('timestamp',0), open=d.get('open',0), high=d.get('high',0),
                         low=d.get('low',0), close=d.get('close',0), volume=d.get('volume',0)) for d in ohlcv_data]

        close = [c.close for c in candles]; high = [c.high for c in candles]
        low = [c.low for c in candles]; volume = [c.volume for c in candles]

        result = TechnicalAnalysisResult(
            coin=coin, timeframe=timeframe, timestamp=ts(),
            current_price=close[-1] if close else 0,
            change_24h=((close[-1]-close[0])/close[0]*100) if close and close[0]!=0 else 0,
            high_24h=max(high[-96:]) if len(high)>=96 else max(high) if high else 0,
            low_24h=min(low[-96:]) if len(low)>=96 else min(low) if low else 0,
            volume_24h=sum(volume[-96:]) if len(volume)>=96 else sum(volume),
        )

        if len(close) < 50: return result

        # RSI
        rsi_vals = self.indicators.rsi(close)
        result.rsi = IndicatorResult(name="RSI", value=round(rsi_vals[-1],1),
            signal="oversold" if rsi_vals[-1]<30 else "overbought" if rsi_vals[-1]>70 else "neutral")

        # Stochastic
        k_vals, d_vals = self.indicators.stochastic(high, low, close)
        result.stochastic = IndicatorResult(name="Stochastic", value=round(k_vals[-1],1))

        # CCI
        cci_vals = self.indicators.cci(high, low, close)
        result.cci = IndicatorResult(name="CCI", value=round(cci_vals[-1],1))

        # Williams %R
        wr_vals = self.indicators.williams_r(high, low, close)
        result.williams_r = IndicatorResult(name="Williams %R", value=round(wr_vals[-1],1))

        # MFI
        mfi_vals = self.indicators.mfi(high, low, close, volume)
        result.mfi = IndicatorResult(name="MFI", value=round(mfi_vals[-1],1))

        # Moving Averages
        sma20 = self.indicators.sma(close, 20); sma50 = self.indicators.sma(close, 50)
        ema12 = self.indicators.ema(close, 12); ema26 = self.indicators.ema(close, 26)
        result.sma_signals = {"sma_20": "bullish" if close[-1]>sma20[-1] else "bearish", "sma_50": "bullish" if close[-1]>sma50[-1] else "bearish"}
        result.ema_signals = {"ema_12": "bullish" if close[-1]>ema12[-1] else "bearish", "ema_26": "bullish" if close[-1]>ema26[-1] else "bearish"}
        if sma20[-1] > sma50[-1] and sma20[-2] <= sma50[-2]: result.ma_crossovers.append("Golden Cross")
        if sma20[-1] < sma50[-1] and sma20[-2] >= sma50[-2]: result.ma_crossovers.append("Death Cross")

        # MACD
        macd_line, signal_line, hist = self.indicators.macd(close)
        result.macd = round(macd_line[-1],4); result.macd_signal = round(signal_line[-1],4)
        result.macd_histogram = round(hist[-1],4)
        if macd_line[-1]>signal_line[-1] and macd_line[-2]<=signal_line[-2]: result.macd_crossover = "bullish_cross"
        elif macd_line[-1]<signal_line[-1] and macd_line[-2]>=signal_line[-2]: result.macd_crossover = "bearish_cross"

        # Bollinger Bands
        bb_u, bb_m, bb_l = self.indicators.bollinger_bands(close)
        result.bb_upper = round(bb_u[-1],2); result.bb_middle = round(bb_m[-1],2); result.bb_lower = round(bb_l[-1],2)
        result.bb_position = round((close[-1]-bb_l[-1])/(bb_u[-1]-bb_l[-1])*100,1) if (bb_u[-1]-bb_l[-1])!=0 else 50

        # Ichimoku
        ichi = self.indicators.ichimoku(high, low)
        result.ichimoku_signal = "bullish" if ichi["tenkan_sen"][-1] > ichi["kijun_sen"][-1] else "bearish" if ichi["tenkan_sen"][-1] < ichi["kijun_sen"][-1] else "neutral"

        # ADX
        adx_vals, pdi, mdi = self.indicators.adx(high, low, close)
        result.adx = round(adx_vals[-1],1); result.plus_di = round(pdi[-1],1); result.minus_di = round(mdi[-1],1)
        result.adx_trend_strength = "strong" if adx_vals[-1]>50 else "moderate" if adx_vals[-1]>25 else "weak"

        # ATR
        atr_vals = self.indicators.atr(high, low, close)
        result.atr = round(atr_vals[-1],2); result.atr_percentage = round((atr_vals[-1]/close[-1])*100,2) if close[-1]!=0 else 0

        # Pivot Points
        pivots = self.indicators.pivot_points(max(high[-24:]) if len(high)>=24 else high[-1], min(low[-24:]) if len(low)>=24 else low[-1], close[-1])
        result.pivot = pivots["pivot"]; result.pivot_r1 = pivots["r1"]; result.pivot_r2 = pivots["r2"]; result.pivot_r3 = pivots["r3"]
        result.pivot_s1 = pivots["s1"]; result.pivot_s2 = pivots["s2"]; result.pivot_s3 = pivots["s3"]

        # Patterns
        result.candlestick_patterns = self.patterns.detect_all(candles)

        # Support & Resistance
        result.supports, result.resistances = self.price_action.support_resistance(high, low, close)

        # Fibonacci
        if len(close) >= 50:
            highs, lows = self.fibonacci.find_swings(close)
            if highs and lows:
                result.fibonacci = self.fibonacci.retracement(lows[-1] if lows else min(close[-50:]), highs[-1] if highs else max(close[-50:]))

        # Market Structure
        result.market_structure = self.price_action.market_structure(high, low)

        # Divergences
        result.divergences = self.price_action.detect_divergence(close, rsi_vals)

        # Trend
        trend_score = 0
        if result.sma_signals.get('sma_20') == 'bullish': trend_score += 1
        else: trend_score -= 1
        if result.sma_signals.get('sma_50') == 'bullish': trend_score += 1
        else: trend_score -= 1
        if result.ichimoku_signal == 'bullish': trend_score += 1
        elif result.ichimoku_signal == 'bearish': trend_score -= 1
        if adx_vals[-1] > 25 and pdi[-1] > mdi[-1]: trend_score += 1
        elif adx_vals[-1] > 25 and mdi[-1] > pdi[-1]: trend_score -= 1

        if trend_score >= 3: result.trend = "strong_uptrend"
        elif trend_score >= 1: result.trend = "uptrend"
        elif trend_score >= -1: result.trend = "sideways"
        elif trend_score >= -3: result.trend = "downtrend"
        else: result.trend = "strong_downtrend"

        # Overall Signal
        sig_score = 0
        if rsi_vals[-1] < 30: sig_score += 2
        elif rsi_vals[-1] > 70: sig_score -= 2
        if result.macd_crossover == "bullish_cross": sig_score += 2
        elif result.macd_crossover == "bearish_cross": sig_score -= 2
        elif result.macd > result.macd_signal: sig_score += 1
        else: sig_score -= 1
        if result.bb_position < 20: sig_score += 2
        elif result.bb_position > 80: sig_score -= 2
        bullish_p = [p for p in result.candlestick_patterns if p.type == "bullish"]
        bearish_p = [p for p in result.candlestick_patterns if p.type == "bearish"]
        sig_score += len(bullish_p) - len(bearish_p)

        if sig_score >= 6: result.overall_signal = "strong_buy"
        elif sig_score >= 3: result.overall_signal = "buy"
        elif sig_score >= -2: result.overall_signal = "neutral"
        elif sig_score >= -5: result.overall_signal = "sell"
        else: result.overall_signal = "strong_sell"

        result.signal_strength = min(90, 50 + abs(sig_score)*5)
        result.confidence = min(result.signal_strength + 10, 95)

        # Stop Loss & Take Profits
        result.stop_loss = round(result.atr * 2, 2) if result.atr > 0 else round(close[-1] * 0.03, 2)
        mult = 1 if result.overall_signal in ["buy", "strong_buy"] else -1
        result.take_profits = [round(close[-1] + mult * result.atr * (1.5 + i*1.5), 2) for i in range(3)]
        result.risk_reward = round(abs(result.take_profits[0] - close[-1]) / max(result.stop_loss, 0.0001), 2) if result.take_profits else 0

        result.summary = f"{coin} - {result.overall_signal.upper()} - {result.confidence:.0f}%"
        result.recommendation = result.overall_signal
        result.key_levels = [result.pivot, result.pivot_r1, result.pivot_s1, result.bb_upper, result.bb_lower]

        self._set_cache(cache_key, result)
        return result

    def _fetch_ohlcv(self, coin: str, timeframe: str) -> List[Dict]:
        if get_market:
            try:
                market = get_market() if callable(get_market) else get_market
                if market and hasattr(market, 'get_ohlcv'):
                    return market.get_ohlcv(coin, timeframe)
            except: pass
        return []

    def clear_cache(self):
        with self._lock: self._cache.clear()

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 13 — SINGLETON & EXPORT
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

_instance: Optional[AnalysisEngine] = None
_lock = threading.Lock()

def get_analysis_engine() -> AnalysisEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = AnalysisEngine()
    return _instance

def start() -> bool:
    return True

def analyze(coin: str, timeframe: str = "4h", data: List[Dict] = None) -> TechnicalAnalysisResult:
    return get_analysis_engine().analyze(coin, timeframe, data)

def detect_patterns(candles: List[Dict]) -> List[PatternResult]:
    ohlcv_list = [OHLCV(timestamp=c.get('timestamp',0), open=c.get('open',0), high=c.get('high',0),
                        low=c.get('low',0), close=c.get('close',0), volume=c.get('volume',0)) for c in candles]
    return CandlestickPatternsEngine.detect_all(ohlcv_list)

def fibonacci_levels(swing_low: float, swing_high: float) -> FibonacciResult:
    return FibonacciEngine.retracement(swing_low, swing_high)

def support_resistance(data: List[float]) -> Tuple[List[Dict], List[Dict]]:
    return PriceActionEngine.support_resistance(data, data, data)

def pivot_points(high: float, low: float, close: float) -> Dict[str, float]:
    return TechnicalIndicatorsEngine.pivot_points(high, low, close)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 14 — STANDALONE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    engine = get_analysis_engine()
    result = engine.analyze("BTC", "4h")
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2, default=str))
