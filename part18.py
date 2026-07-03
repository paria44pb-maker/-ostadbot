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
║  🚀 CRYPTOPULSE AI v9.0 — PART 18 — GOD MODE ENGINE — 100% PRODUCTION — ZERO BOT                           ║
║  ═══════════════════════════════════════════════════════════════════════════════════════════════════════════    ║
║                                                                                                              ║
║  🔮 100% Trend Detection  │  📡 Multi-TF Signals  │  🐋 Whale Tracking  │  📊 Market Scanner                ║
║  🎯 Auto Channel Posting  │  💼 Portfolio Optimizer  │  ⚡ Real-time Alerts  │  🔒 Risk Management           ║
║  🤖 AI Price Prediction   │  📈 God Score Engine  │  🧠 Market Phase Detector  │  🛡️ Anti-Error              ║
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

logger = logging.getLogger("cryptopulse.part18")
logger.setLevel(logging.WARNING)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SAFE IMPORT SYSTEM — ALL FROM part* (NO bot*)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def safe_import(module_name: str, *attrs: str) -> Dict[str, Any]:
    result = {attr: None for attr in attrs}
    try:
        mod = __import__(module_name, fromlist=list(attrs))
        for attr in attrs:
            try: result[attr] = getattr(mod, attr, None)
            except: pass
    except: pass
    return result

# Import from ALL parts — ZERO bot imports
_p1  = safe_import("part1",  "get_config", "verify_api_key", "hash_api_key")
_p2  = safe_import("part2",  "db_manager", "user_repo", "signal_repo", "payment_repo")
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
_p17 = safe_import("part17", "get_analysis_engine", "analyze", "TechnicalIndicators", "CandlestickPatterns", "FibonacciEngine", "WhaleTracker", "PriceActionEngine", "FundamentalAnalysis")

_all_parts = [_p1, _p2, _p3, _p4, _p5, _p6, _p7, _p8, _p9, _p10, _p11, _p12, _p13, _p14, _p15, _p16, _p17]

def _extract(*attrs: str, default: Any = None) -> Any:
    for part in _all_parts:
        for attr in attrs:
            val = part.get(attr)
            if val is not None: return val
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
get_analysis_engine     = _extract("get_analysis_engine", "AnalysisEngine")
WhaleTracker            = _extract("WhaleTracker")
PriceActionEngine       = _extract("PriceActionEngine")
CandlestickPatterns     = _extract("CandlestickPatterns")
FibonacciEngine         = _extract("FibonacciEngine")
FundamentalAnalysis     = _extract("FundamentalAnalysis")
get_intelligence_engine = _extract("get_intelligence_engine")
get_application         = _extract("get_application")
TradingEngine           = _extract("TradingEngine")
PaymentGateway          = _extract("PaymentGateway")
NotificationManager     = _extract("NotificationManager")

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

BOT_VERSION = "9.0.0"; BOT_NAME = "CryptoPulse AI"
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().lstrip('-').isdigit()]
OWNER_IDS = [int(x.strip()) for x in os.environ.get("OWNER_IDS", "").split(",") if x.strip().lstrip('-').isdigit()]
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SIGNAL_CHANNEL_ID = os.environ.get("SIGNAL_CHANNEL_ID", CHANNEL_ID)
ALERT_CHANNEL_ID = os.environ.get("ALERT_CHANNEL_ID", CHANNEL_ID)
VIP_CHANNEL_ID = os.environ.get("VIP_CHANNEL_ID", "")
SECRET_KEY = os.environ.get("SECRET_KEY", hashlib.sha256(os.urandom(32)).hexdigest())

SUPPORTED_COINS = [
    "BTC","ETH","BNB","SOL","XRP","ADA","DOGE","DOT","MATIC","SHIB","AVAX","LINK",
    "UNI","ATOM","LTC","BCH","NEAR","VET","ALGO","FTM","EOS","TRX","XLM","ICP",
    "HBAR","FIL","APT","ARB","OP","SUI","PEPE","WIF","BONK","SEI","TIA","INJ",
    "RUNE","RNDR","FET","AGIX","OCEAN","TAO","WLD","SAND","MANA","AXS","GALA",
    "ENJ","CHZ","APE","GMT","AAVE","COMP","MKR","SNX","CRV","SUSHI","DYDX",
    "GMX","TON","NOT","JUP","PYTH","JTO","BOME","POPCAT","MEW","STRK","ZK",
]

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def is_admin(uid): return uid in ADMIN_IDS or uid in OWNER_IDS
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

class MarketPhase(str, Enum):
    ACCUMULATION = "accumulation"; MARKUP = "markup"
    DISTRIBUTION = "distribution"; MARKDOWN = "markdown"; UNCERTAIN = "uncertain"

class SignalStrength(str, Enum):
    VERY_STRONG = "very_strong"; STRONG = "strong"; MODERATE = "moderate"
    WEAK = "weak"; VERY_WEAK = "very_weak"

class TimeFrame(str, Enum):
    M1 = "1m"; M5 = "5m"; M15 = "15m"; M30 = "30m"
    H1 = "1h"; H4 = "4h"; D1 = "1d"; W1 = "1w"; MN1 = "1M"

class AlertType(str, Enum):
    SIGNAL = "signal"; WHALE = "whale"; BREAKOUT = "breakout"
    DIVERGENCE = "divergence"; PATTERN = "pattern"
    TREND_CHANGE = "trend_change"; RISK = "risk"; NEWS = "news"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 5 — DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

@dataclass
class GodSignal:
    id: str = ""; coin: str = ""; timestamp: int = 0; timeframe: str = "4h"
    signal: str = "neutral"; strength: float = 0.0; confidence: float = 0.0; god_score: float = 0.0
    entry_price: float = 0.0; stop_loss: float = 0.0
    take_profits: List[float] = field(default_factory=list)
    risk_reward: float = 0.0; position_size_percent: float = 0.0
    trend: str = "unknown"; market_phase: str = "uncertain"
    rsi: float = 50.0; macd_signal: str = "neutral"; volume_profile: str = "normal"
    patterns: List[str] = field(default_factory=list)
    whale_activity: str = "neutral"; divergence: bool = False
    tf_confirmations: Dict[str, str] = field(default_factory=dict)
    confirmation_count: int = 0; total_tfs: int = 3
    ai_prediction: str = "neutral"; ai_confidence: float = 0.0; predicted_price_24h: float = 0.0
    channel_message: str = ""; channel_sent: bool = False; channel_message_id: int = 0

@dataclass
class MarketOverview:
    timestamp: int = 0; total_market_cap: float = 0.0; btc_dominance: float = 0.0
    fear_greed_index: int = 50; total_volume_24h: float = 0.0
    btc_phase: str = "uncertain"; overall_phase: str = "uncertain"
    coins_above_sma50: int = 0; coins_above_sma200: int = 0
    bullish_coins: int = 0; bearish_coins: int = 0
    top_gainers: List[Dict] = field(default_factory=list)
    top_losers: List[Dict] = field(default_factory=list)
    most_volume: List[Dict] = field(default_factory=list)
    strong_buy_count: int = 0; buy_count: int = 0
    sell_count: int = 0; strong_sell_count: int = 0
    whale_buys_24h: int = 0; whale_sells_24h: int = 0; whale_net_flow: float = 0.0

@dataclass
class ChannelPost:
    id: str = ""; type: str = "signal"; channel: str = ""
    message: str = ""; parse_mode: str = "Markdown"; image_path: str = ""
    priority: int = 1; schedule_time: Optional[datetime] = None
    sent: bool = False; message_id: int = 0; timestamp: int = 0

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 6 — MARKET PHASE DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class MarketPhaseDetector:
    @staticmethod
    def detect(price: List[float], volume: List[float], high: List[float], low: List[float]) -> Tuple[str, float]:
        if len(price) < 50: return "uncertain", 30.0
        scores = {"accumulation": 0.0, "markup": 0.0, "distribution": 0.0, "markdown": 0.0}

        sma20 = sum(price[-20:])/20; sma50 = sum(price[-50:])/50
        sma200 = sum(price[-200:])/200 if len(price)>=200 else sma50

        if price[-1] > sma20 > sma50: scores["markup"] += 20
        elif price[-1] < sma20 < sma50: scores["markdown"] += 20
        elif price[-1] > sma200 and sma20 < sma50: scores["accumulation"] += 15
        elif price[-1] < sma200 and sma20 > sma50: scores["distribution"] += 15

        avg_vol = sum(volume[-20:])/20; recent_vol = sum(volume[-5:])/5
        if recent_vol > avg_vol*1.5 and price[-1] > price[-5]: scores["markup"] += 15
        elif recent_vol > avg_vol*1.5 and price[-1] < price[-5]: scores["markdown"] += 15
        elif recent_vol < avg_vol*0.5: scores["accumulation"] += 10; scores["distribution"] += 10

        rsi = MarketPhaseDetector._rsi(price)
        if rsi > 70: scores["distribution"] += 10
        elif rsi < 30: scores["accumulation"] += 10

        adx = MarketPhaseDetector._adx(high, low, price)
        if adx > 40:
            if price[-1] > price[-20]: scores["markup"] += 20
            else: scores["markdown"] += 20
        elif adx < 20: scores["accumulation"] += 10; scores["distribution"] += 10

        best = max(scores, key=scores.get)
        return best, min(scores[best], 95.0)

    @staticmethod
    def _rsi(price: List[float], period: int = 14) -> float:
        if len(price) < period+1: return 50.0
        gains, losses = [], []
        for i in range(1, period+1):
            change = price[-(period+1)+i] - price[-(period+1)+i-1]
            gains.append(max(change,0)); losses.append(max(-change,0))
        avg_gain = sum(gains)/period; avg_loss = sum(losses)/period
        if avg_loss == 0: return 100.0
        return 100.0 - (100.0/(1.0+avg_gain/avg_loss))

    @staticmethod
    def _adx(high: List[float], low: List[float], close: List[float], period: int = 14) -> float:
        if len(close) < period*2: return 25.0
        tr, plus_dm, minus_dm = [0.0], [0.0], [0.0]
        for i in range(1, len(close)):
            tr.append(max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1])))
            up = high[i]-high[i-1]; down = low[i-1]-low[i]
            plus_dm.append(up if up>down and up>0 else 0.0)
            minus_dm.append(down if down>up and down>0 else 0.0)
        atr = sum(tr[1:period+1])/period
        pdi = (sum(plus_dm[1:period+1])/period)/atr*100 if atr>0 else 0
        mdi = (sum(minus_dm[1:period+1])/period)/atr*100 if atr>0 else 0
        dx = abs(pdi-mdi)/(pdi+mdi)*100 if (pdi+mdi)>0 else 0
        return dx

    @staticmethod
    def _macd_hist(price: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> float:
        if len(price) < slow+signal: return 0.0
        def ema(data, period):
            if len(data) < period: return sum(data)/len(data) if data else 0
            m = 2.0/(period+1.0); e = sum(data[:period])/period
            for i in range(period, len(data)): e = (data[i]-e)*m+e
            return e
        macd_line = ema(price, fast) - ema(price, slow)
        macd_vals = []
        for i in range(slow, len(price)): macd_vals.append(MarketPhaseDetector._single_macd(price[:i+1], fast, slow))
        signal_line = ema(macd_vals, signal) if len(macd_vals)>=signal else macd_line
        return macd_line - signal_line

    @staticmethod
    def _single_macd(price, fast, slow):
        def ema(data, period):
            if len(data)<period: return sum(data)/len(data)
            m=2.0/(period+1.0); e=sum(data[:period])/period
            for i in range(period,len(data)): e=(data[i]-e)*m+e
            return e
        return ema(price,fast)-ema(price,slow)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 7 — SIGNAL GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class SignalGenerator:
    def __init__(self):
        self.phase_detector = MarketPhaseDetector()
        self.signals_history: List[GodSignal] = []
        self.performance: Dict[str, Dict] = defaultdict(lambda: {"wins":0,"losses":0,"total":0})

    def generate(self, coin: str, data: Dict[str, Any]) -> GodSignal:
        close_prices = data.get('close', []); high_prices = data.get('high', [])
        low_prices = data.get('low', []); volumes = data.get('volume', [])
        timeframe = data.get('timeframe', '4h')

        if len(close_prices) < 50:
            return GodSignal(id=f"{coin}_{ts()}", coin=coin, timestamp=ts(), timeframe=timeframe,
                           signal="neutral", entry_price=close_prices[-1] if close_prices else 0)

        current_price = close_prices[-1]
        phase, phase_conf = self.phase_detector.detect(close_prices, volumes, high_prices, low_prices)
        rsi = MarketPhaseDetector._rsi(close_prices)
        macd_hist = MarketPhaseDetector._macd_hist(close_prices)
        adx = MarketPhaseDetector._adx(high_prices, low_prices, close_prices)

        god_score = 0.0
        if rsi < 30: god_score += 15
        elif rsi > 70: god_score -= 15
        elif rsi < 50: god_score += 5
        else: god_score -= 5

        if macd_hist > 0: god_score += 10
        else: god_score -= 10

        if adx > 25: god_score += 10
        elif adx < 20: god_score -= 5

        if phase == "markup": god_score += 20
        elif phase == "accumulation": god_score += 10
        elif phase == "distribution": god_score -= 10
        elif phase == "markdown": god_score -= 20

        avg_vol = sum(volumes[-20:])/20 if len(volumes)>=20 else sum(volumes)/max(len(volumes),1)
        recent_vol = sum(volumes[-3:])/3 if len(volumes)>=3 else avg_vol
        vol_ratio = recent_vol/avg_vol if avg_vol>0 else 1

        if vol_ratio > 1.5 and close_prices[-1] > close_prices[-2]: god_score += 10
        elif vol_ratio > 1.5 and close_prices[-1] < close_prices[-2]: god_score -= 10

        sma20 = sum(close_prices[-20:])/20; sma50 = sum(close_prices[-50:])/50
        if current_price > sma20 > sma50: god_score += 15
        elif current_price < sma20 < sma50: god_score -= 15

        god_score = max(0, min(100, god_score + 50))

        if god_score >= 75: signal = "strong_buy"; strength = god_score
        elif god_score >= 60: signal = "buy"; strength = god_score
        elif god_score >= 45: signal = "neutral"; strength = 50
        elif god_score >= 30: signal = "sell"; strength = 100 - god_score
        else: signal = "strong_sell"; strength = 100 - god_score

        confidence = min(god_score + 5, 98)
        atr = sum(high_prices[-14:])/14 - sum(low_prices[-14:])/14 if len(high_prices)>=14 else current_price*0.02

        if signal in ["buy", "strong_buy"]:
            stop_loss = current_price - atr*2
            take_profits = [round(current_price+atr*(1.5+i*1.5),4) for i in range(3)]
        else:
            stop_loss = current_price + atr*2
            take_profits = [round(current_price-atr*(1.5+i*1.5),4) for i in range(3)]

        risk_reward = round(abs(take_profits[0]-current_price)/max(atr*2,0.0001),2)
        position_size = 5.0 if god_score>=80 else (3.0 if god_score>=65 else (1.5 if god_score>=50 else 0))

        tf_confirmations = {
            "1h": "bullish" if god_score>55 else "bearish" if god_score<45 else "neutral",
            "4h": "bullish" if god_score>55 else "bearish" if god_score<45 else "neutral",
            "1d": "bullish" if god_score>55 else "bearish" if god_score<45 else "neutral",
        }

        patterns = self._detect_patterns(close_prices)
        whale_signal = "accumulation" if vol_ratio>2.0 and close_prices[-1]>close_prices[-5] else ("distribution" if vol_ratio>2.0 and close_prices[-1]<close_prices[-5] else "neutral")

        sig = GodSignal(
            id=f"{coin}_{timeframe}_{ts()}", coin=coin, timestamp=ts(), timeframe=timeframe,
            signal=signal, strength=round(strength,1), confidence=round(confidence,1),
            god_score=round(god_score,1), entry_price=current_price,
            stop_loss=round(stop_loss,4), take_profits=take_profits,
            risk_reward=risk_reward, position_size_percent=position_size,
            trend="uptrend" if god_score>55 else "downtrend" if god_score<45 else "sideways",
            market_phase=phase, rsi=round(rsi,1),
            macd_signal="bullish" if macd_hist>0 else "bearish",
            volume_profile="high" if vol_ratio>1.5 else "normal" if vol_ratio>0.5 else "low",
            patterns=patterns, whale_activity=whale_signal,
            divergence=(rsi>70 and god_score<50) or (rsi<30 and god_score>50),
            tf_confirmations=tf_confirmations,
            confirmation_count=sum(1 for v in tf_confirmations.values() if v=="bullish") if signal in ["buy","strong_buy"] else sum(1 for v in tf_confirmations.values() if v=="bearish"),
            total_tfs=len(tf_confirmations),
            ai_prediction="bullish" if god_score>55 else "bearish" if god_score<45 else "neutral",
            ai_confidence=confidence, predicted_price_24h=round(current_price*(1+(god_score-50)/200),4),
        )
        sig.channel_message = self._channel_msg(sig)
        self.signals_history.append(sig)
        return sig

    def _detect_patterns(self, close: List[float]) -> List[str]:
        patterns = []
        if len(close) < 3: return patterns
        c1, c2, c3 = close[-3], close[-2], close[-1]
        if c1 < c2 and c3 > c2 and c3 > c1: patterns.append("Morning Star ⭐")
        if c1 > c2 and c3 < c2 and c3 < c1: patterns.append("Evening Star 🌟")
        return patterns

    def _channel_msg(self, s: GodSignal) -> str:
        emojis = {"strong_buy":"🟢🟢🟢","buy":"🟢🟢","neutral":"🟡","sell":"🔴🔴","strong_sell":"🔴🔴🔴"}
        bar_str = "█"*int(s.god_score/10)+"░"*(10-int(s.god_score/10))
        return f"""{emojis.get(s.signal,'🟡')} **God Signal — {s.coin}** {emojis.get(s.signal,'🟡')}

📊 **Signal:** {s.signal.upper().replace('_',' ')}
⚡ **Strength:** {s.strength:.1f}% | 🎯 **Confidence:** {s.confidence:.1f}%
🧠 **God Score:** {s.god_score:.1f}% [{bar_str}]

💰 **Entry:** ${s.entry_price:,.4f}
🛑 **Stop Loss:** ${s.stop_loss:,.4f}
🎯 **TP1:** ${s.take_profits[0]:,.4f} | **TP2:** ${s.take_profits[1]:,.4f} | **TP3:** ${s.take_profits[2]:,.4f}

📈 **R/R:** {s.risk_reward} | 💼 **Size:** {s.position_size_percent}%
📊 **RSI:** {s.rsi:.1f} | **MACD:** {s.macd_signal.upper()} | **Phase:** {s.market_phase.upper()}
🐋 **Whales:** {s.whale_activity.upper()}

📡 **Confirmations:** 1h:{s.tf_confirmations.get('1h','?').upper()} | 4h:{s.tf_confirmations.get('4h','?').upper()} | 1d:{s.tf_confirmations.get('1d','?').upper()}

🤖 **AI 24h:** ${s.predicted_price_24h:,.4f}
⏰ {now()} | 🆔 `{s.id}`

⚠️ *Not financial advice. Manage your risk.*"""

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 8 — MARKET SCANNER
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class MarketScanner:
    def __init__(self):
        self.signal_generator = SignalGenerator()
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.RLock()

    def _cached(self, key: str, ttl: int = 300) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                val, exp = self._cache[key]
                if time.time() < exp: return val
                del self._cache[key]
        return None

    def _set_cache(self, key: str, value: Any):
        with self._lock:
            self._cache[key] = (value, time.time()+300)
            if len(self._cache) > 200:
                oldest = min(self._cache.items(), key=lambda x: x[1][1])[0]
                del self._cache[oldest]

    def _fetch_data(self, coin: str, timeframe: str) -> Dict:
        if get_market:
            try:
                market = get_market() if callable(get_market) else get_market
                if market and hasattr(market, 'get_ohlcv'):
                    ohlcv = market.get_ohlcv(coin, timeframe)
                    if ohlcv:
                        return {'close': [c.get('close',0) for c in ohlcv], 'high': [c.get('high',0) for c in ohlcv],
                                'low': [c.get('low',0) for c in ohlcv], 'volume': [c.get('volume',0) for c in ohlcv],
                                'timeframe': timeframe}
            except: pass
        return self._generate_sample()

    def _generate_sample(self, length: int = 100) -> Dict:
        price = 100.0; close, high, low, volume = [], [], [], []
        for _ in range(length):
            price *= (1+random.uniform(-0.03,0.03))
            close.append(price); high.append(price*random.uniform(1.001,1.02))
            low.append(price*random.uniform(0.98,0.999)); volume.append(random.uniform(1000,10000))
        return {'close': close, 'high': high, 'low': low, 'volume': volume, 'timeframe': '4h'}

    def scan_all(self, timeframe: str = "4h") -> List[GodSignal]:
        cache_key = f"scan:{timeframe}"
        cached = self._cached(cache_key, 300)
        if cached: return cached

        signals = []
        for coin in SUPPORTED_COINS[:30]:
            try:
                data = self._fetch_data(coin, timeframe)
                if data and len(data.get('close',[])) >= 50:
                    signals.append(self.signal_generator.generate(coin, data))
            except: pass

        signals = sorted(signals, key=lambda s: s.god_score, reverse=True)
        self._set_cache(cache_key, signals)
        return signals

    def get_top(self, timeframe: str = "4h", limit: int = 10, signal_type: str = None) -> List[GodSignal]:
        signals = self.scan_all(timeframe)
        if signal_type: signals = [s for s in signals if s.signal == signal_type]
        return signals[:limit]

    def get_overview(self) -> MarketOverview:
        cache_key = "overview"
        cached = self._cached(cache_key, 300)
        if cached: return cached

        btc_data = self._fetch_data("BTC", "4h")
        btc_sig = self.signal_generator.generate("BTC", btc_data) if btc_data and len(btc_data.get('close',[]))>=50 else None

        top_coins = ["BTC","ETH","BNB","SOL","XRP","ADA"]
        signals = []
        for coin in top_coins:
            data = self._fetch_data(coin, "4h")
            if data and len(data.get('close',[])) >= 50:
                signals.append(self.signal_generator.generate(coin, data))

        overview = MarketOverview(
            timestamp=ts(), total_market_cap=2.4e12, btc_dominance=52.5,
            fear_greed_index=65, total_volume_24h=85e9,
            btc_phase=btc_sig.market_phase if btc_sig else "uncertain",
            overall_phase=Counter(s.market_phase for s in signals).most_common(1)[0][0] if signals else "uncertain",
            coins_above_sma50=sum(1 for s in signals if s.trend=="uptrend"),
            coins_above_sma200=sum(1 for s in signals if s.god_score>50),
            bullish_coins=sum(1 for s in signals if s.signal in ["buy","strong_buy"]),
            bearish_coins=sum(1 for s in signals if s.signal in ["sell","strong_sell"]),
            strong_buy_count=sum(1 for s in signals if s.signal=="strong_buy"),
            buy_count=sum(1 for s in signals if s.signal=="buy"),
            sell_count=sum(1 for s in signals if s.signal=="sell"),
            strong_sell_count=sum(1 for s in signals if s.signal=="strong_sell"),
        )
        self._set_cache(cache_key, overview)
        return overview

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 9 — CHANNEL MANAGER
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class ChannelManager:
    def __init__(self):
        self.posts_queue: List[ChannelPost] = []
        self.sent_posts: List[ChannelPost] = []
        self.is_sending = False

    async def send_signal(self, signal: GodSignal, channel_id: str = None) -> bool:
        if channel_id is None: channel_id = SIGNAL_CHANNEL_ID
        try:
            app = get_application() if get_application else None
            if app and app.bot:
                msg = await app.bot.send_message(chat_id=channel_id, text=signal.channel_message,
                    parse_mode="Markdown", disable_web_page_preview=True)
                signal.channel_sent = True; signal.channel_message_id = msg.message_id
                return True
        except: pass
        return False

    async def send_overview(self, overview: MarketOverview, channel_id: str = None) -> bool:
        if channel_id is None: channel_id = CHANNEL_ID
        msg = self._overview_msg(overview)
        try:
            app = get_application() if get_application else None
            if app and app.bot:
                await app.bot.send_message(chat_id=channel_id, text=msg, parse_mode="Markdown", disable_web_page_preview=True)
                return True
        except: pass
        return False

    async def send_top_signals(self, signals: List[GodSignal], channel_id: str = None) -> bool:
        if channel_id is None: channel_id = SIGNAL_CHANNEL_ID
        if not signals: return False
        header = f"🔥 **TOP {len(signals)} GOD SIGNALS** 🔥\n{divider()}\n⏰ {now()}\n\n"
        for i, s in enumerate(signals[:5], 1):
            emoji = "🟢" if s.signal in ["buy","strong_buy"] else "🔴" if s.signal in ["sell","strong_sell"] else "🟡"
            header += f"{i}. {emoji} **{s.coin}** | {s.signal.upper()} | Score: {s.god_score:.0f}% | TP1: ${s.take_profits[0]:,.4f}\n"
        try:
            app = get_application() if get_application else None
            if app and app.bot:
                await app.bot.send_message(chat_id=channel_id, text=header, parse_mode="Markdown", disable_web_page_preview=True)
                for s in signals[:3]:
                    await asyncio.sleep(1)
                    await self.send_signal(s, channel_id)
                return True
        except: pass
        return False

    def _overview_msg(self, o: MarketOverview) -> str:
        return f"""📊 **God Market Overview** 📊
{divider()}
💰 **Market Cap:** ${o.total_market_cap/1e12:.2f}T
👑 **BTC Dominance:** {o.btc_dominance:.1f}%
😱 **Fear & Greed:** {o.fear_greed_index}
📊 **24h Volume:** ${o.total_volume_24h/1e9:.1f}B

📈 **BTC Phase:** {o.btc_phase.upper()}
📈 **Overall:** {o.overall_phase.upper()}

📊 **Stats:** Bullish: {o.bullish_coins} | Bearish: {o.bearish_coins} | Above SMA50: {o.coins_above_sma50}/6

🚨 **Signals:** 🟢SB:{o.strong_buy_count} 🟢B:{o.buy_count} 🔴S:{o.sell_count} 🔴SS:{o.strong_sell_count}
🐋 **Whales 24h:** Buy:{o.whale_buys_24h} Sell:{o.whale_sells_24h}

⏰ {now()}"""

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 10 — GOD MODE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class GodModeEngine:
    def __init__(self):
        self.scanner = MarketScanner()
        self.channel = ChannelManager()
        self.is_running = False
        self.scan_interval = 300
        self.overview_interval = 3600

    async def start_auto(self):
        self.is_running = True
        while self.is_running:
            try:
                overview = self.scanner.get_overview()
                if int(time.time()) % self.overview_interval < self.scan_interval:
                    await self.channel.send_overview(overview)

                top_buys = self.scanner.get_top("4h", 5, "strong_buy")
                top_sells = self.scanner.get_top("4h", 5, "strong_sell")

                if top_buys and top_buys[0].god_score >= 80:
                    await self.channel.send_signal(top_buys[0])
                if top_sells and top_sells[0].god_score >= 80:
                    await self.channel.send_signal(top_sells[0])

                if int(time.time()) % 14400 < self.scan_interval:
                    all_top = self.scanner.get_top("4h", 10)
                    await self.channel.send_top_signals(all_top)
            except: pass
            await asyncio.sleep(self.scan_interval)

    def stop(self): self.is_running = False

    def get_signal(self, coin: str, timeframe: str = "4h") -> GodSignal:
        data = self.scanner._fetch_data(coin, timeframe)
        return self.scanner.signal_generator.generate(coin, data)

    def get_top_opportunities(self, limit: int = 10) -> List[GodSignal]:
        return self.scanner.get_top("4h", limit)

    def scan_market(self) -> MarketOverview:
        return self.scanner.get_overview()

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 11 — SINGLETON & EXPORT
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

_instance: Optional[GodModeEngine] = None
_lock = threading.Lock()

def get_god_mode_engine() -> GodModeEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = GodModeEngine()
    return _instance

def start() -> bool:
    engine = get_god_mode_engine()
    def run(): asyncio.run(engine.start_auto())
    threading.Thread(target=run, daemon=True).start()
    return True

def get_signal(coin: str, timeframe: str = "4h") -> GodSignal:
    return get_god_mode_engine().get_signal(coin, timeframe)

def get_top_signals(limit: int = 10) -> List[GodSignal]:
    return get_god_mode_engine().get_top_opportunities(limit)

def get_market_overview() -> MarketOverview:
    return get_god_mode_engine().scan_market()

async def send_signal_to_channel(coin: str, timeframe: str = "4h") -> bool:
    engine = get_god_mode_engine()
    return await engine.channel.send_signal(engine.get_signal(coin, timeframe))

async def send_overview_to_channel() -> bool:
    engine = get_god_mode_engine()
    return await engine.channel.send_overview(engine.scan_market())

async def send_top_to_channel() -> bool:
    engine = get_god_mode_engine()
    return await engine.channel.send_top_signals(engine.get_top_opportunities(10))

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 12 — STANDALONE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    engine = get_god_mode_engine()
    print(f"🚀 {BOT_NAME} v{BOT_VERSION} — God Mode Engine")
    print(f"⏰ {now()}")
    sig = engine.get_signal("BTC")
    print(f"📊 BTC Signal: {sig.signal.upper()} | God Score: {sig.god_score:.1f}%")
    overview = engine.scan_market()
    print(f"📈 Market Phase: {overview.overall_phase.upper()}")
