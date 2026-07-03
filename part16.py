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
║  🚀 CRYPTOPULSE AI v9.0 — PART 16 — ULTIMATE INTELLIGENCE ENGINE — 100% PRODUCTION — ZERO BOT               ║
║  ═══════════════════════════════════════════════════════════════════════════════════════════════════════════    ║
║                                                                                                              ║
║  🧠 Admin Intelligence  │  👥 User Analytics  │  💰 Financial Deep-Dive  │  📊 Signal Performance           ║
║  📈 Growth Analytics    │  🎯 Market Intel     │  🔒 Security Audit       │  🔮 Predictive Models            ║
║  🤖 AI Insights         │  📋 Comprehensive    │  ⚡ Real-time             │  🛡️ Anti-Error                  ║
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

# ─── SILENCE ALL NOISE ───
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

logger = logging.getLogger("cryptopulse.part16")
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
_p17 = safe_import("part17", "get_analysis_engine", "AnalysisEngine", "TechnicalIndicators", "CandlestickPatterns", "FibonacciEngine", "WhaleTracker", "PriceActionEngine", "FundamentalAnalysis")
_p18 = safe_import("part18", "get_god_mode_engine", "GodModeEngine", "GodSignal", "MarketScanner", "ChannelManager", "MarketOverview")

# Merge all parts for attribute extraction
_all_parts = [_p1, _p2, _p3, _p4, _p5, _p6, _p7, _p8, _p9, _p10, _p11, _p12, _p13, _p14, _p15, _p17, _p18]

def _extract(*attrs: str, default: Any = None) -> Any:
    """Extract attribute from all parts with priority fallback"""
    for part in _all_parts:
        for attr in attrs:
            val = part.get(attr)
            if val is not None:
                return val
    return default

# Core service extraction — all from part*, not bot*
get_config              = _extract("get_config")
verify_api_key          = _extract("verify_api_key")
hash_api_key            = _extract("hash_api_key")
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
get_god_mode_engine     = _extract("get_god_mode_engine")
GodModeEngine           = _extract("GodModeEngine")
GodSignal               = _extract("GodSignal")
MarketScanner           = _extract("MarketScanner")
TradingEngine           = _extract("TradingEngine")
PaymentGateway          = _extract("PaymentGateway")
NotificationManager     = _extract("NotificationManager")
MediaManager            = _extract("MediaManager")
Monitor                 = _extract("Monitor", "HealthChecker")

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

BOT_VERSION = "9.0.0"
BOT_NAME = "CryptoPulse AI"
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().lstrip('-').isdigit()]
OWNER_IDS = [int(x.strip()) for x in os.environ.get("OWNER_IDS", "").split(",") if x.strip().lstrip('-').isdigit()]
SECRET_KEY = os.environ.get("SECRET_KEY", hashlib.sha256(os.urandom(32)).hexdigest())

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
def fmt_pct(p): return f"{p:+.2f}%"
def fmt_irt(a): return f"{a:,.0f} تومان"
def divider(): return "─" * 42
def header(t, w=44): return f"╔{'═'*(w-2)}╗\n║{t.center(w-2)}║\n╚{'═'*(w-2)}╝"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 4 — ENUMS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserSegment(str, Enum):
    VIP_ACTIVE = "vip_active"
    VIP_EXPIRING = "vip_expiring"
    HIGH_VALUE = "high_value"
    AT_RISK = "at_risk"
    NEW_USERS = "new_users"
    INACTIVE = "inactive"
    CHURNED = "churned"
    POWER_USERS = "power_users"
    CASUAL = "casual"
    WHALES = "whales"

class TimeRange(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_YEAR = "this_year"
    ALL_TIME = "all_time"

class MetricType(str, Enum):
    REVENUE = "revenue"
    USERS = "users"
    SIGNALS = "signals"
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    CHURN = "churn"

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 5 — DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

@dataclass
class UserIntelligenceProfile:
    user_id: str; name: str; username: str = ""
    risk_score: float = 0.0; engagement_score: float = 0.0
    value_score: float = 0.0; loyalty_score: float = 0.0
    influence_score: float = 0.0; overall_health_score: float = 0.0
    churn_probability: float = 0.0; conversion_probability: float = 0.0
    fraud_probability: float = 0.0; upgrade_probability: float = 0.0
    activity_pattern: str = "unknown"; behavior_segment: str = "unknown"
    risk_level: str = "low"; value_tier: str = "standard"
    behavior_flags: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    total_trades: int = 0; win_rate: float = 0.0
    avg_trade_size: float = 0.0; total_deposited: float = 0.0
    total_withdrawn: float = 0.0; net_value: float = 0.0
    referral_count: int = 0; referral_revenue: float = 0.0
    days_since_register: int = 0; days_since_last_active: int = 0
    days_since_last_trade: int = 0; session_frequency: float = 0.0
    avg_session_duration: float = 0.0
    is_vip: bool = False; vip_plan: str = ""
    vip_days_left: int = 0; vip_total_spent: float = 0.0
    vip_renewal_count: int = 0

@dataclass
class FinancialIntelligence:
    total_revenue: float = 0.0; today_revenue: float = 0.0
    yesterday_revenue: float = 0.0; week_revenue: float = 0.0
    month_revenue: float = 0.0; quarter_revenue: float = 0.0
    year_revenue: float = 0.0
    revenue_trend: str = "stable"; revenue_growth_rate: float = 0.0
    revenue_volatility: float = 0.0; revenue_momentum: float = 0.0
    projected_daily: float = 0.0; projected_weekly: float = 0.0
    projected_monthly: float = 0.0; projected_quarterly: float = 0.0
    projected_yearly: float = 0.0
    confidence_interval_low: float = 0.0; confidence_interval_high: float = 0.0
    total_transactions: int = 0; avg_transaction: float = 0.0
    median_transaction: float = 0.0; max_transaction: float = 0.0
    min_transaction: float = 0.0; transaction_frequency: float = 0.0
    plan_distribution: Dict[str, int] = field(default_factory=dict)
    top_plan: str = "none"; plan_revenue: Dict[str, float] = field(default_factory=dict)
    plan_conversion_rate: Dict[str, float] = field(default_factory=dict)
    overall_conversion_rate: float = 0.0; trial_to_paid_rate: float = 0.0
    monthly_to_yearly_rate: float = 0.0; yearly_to_lifetime_rate: float = 0.0
    refund_count: int = 0; refund_amount: float = 0.0
    refund_rate: float = 0.0; chargeback_count: int = 0

@dataclass
class SignalIntelligence:
    total_signals: int = 0; today_signals: int = 0
    week_signals: int = 0; month_signals: int = 0
    win_rate: float = 0.0; loss_rate: float = 0.0
    breakeven_rate: float = 0.0; avg_confidence: float = 0.0
    avg_profit: float = 0.0; avg_loss: float = 0.0
    net_profit: float = 0.0
    profit_factor: float = 0.0; sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0; max_drawdown: float = 0.0
    win_streak: int = 0; loss_streak: int = 0
    avg_holding_time: float = 0.0
    coin_performance: Dict[str, Dict] = field(default_factory=dict)
    best_coin: str = "none"; worst_coin: str = "none"
    most_traded_coin: str = "none"
    timeframe_performance: Dict[str, Dict] = field(default_factory=dict)
    best_timeframe: str = "4h"; worst_timeframe: str = "1h"
    buy_signals: int = 0; sell_signals: int = 0; hold_signals: int = 0
    buy_win_rate: float = 0.0; sell_win_rate: float = 0.0
    hourly_distribution: Dict[int, int] = field(default_factory=dict)
    daily_distribution: Dict[str, int] = field(default_factory=dict)
    monthly_trend: List[float] = field(default_factory=list)

@dataclass
class GrowthIntelligence:
    total_users: int = 0; new_users_today: int = 0
    new_users_week: int = 0; new_users_month: int = 0
    user_growth_rate: float = 0.0; user_growth_trend: str = "stable"
    day1_retention: float = 0.0; day7_retention: float = 0.0
    day30_retention: float = 0.0; day90_retention: float = 0.0
    dau: int = 0; wau: int = 0; mau: int = 0
    dau_mau_ratio: float = 0.0; stickiness: float = 0.0
    cohort_retention: Dict[str, List[float]] = field(default_factory=dict)
    cohort_revenue: Dict[str, List[float]] = field(default_factory=dict)
    viral_coefficient: float = 0.0; referral_rate: float = 0.0
    organic_growth_rate: float = 0.0; paid_growth_rate: float = 0.0

@dataclass
class MarketIntelligence:
    total_addressable_market: int = 0; market_penetration: float = 0.0
    market_share_estimate: float = 0.0
    country_distribution: Dict[str, int] = field(default_factory=dict)
    language_distribution: Dict[str, int] = field(default_factory=dict)
    device_distribution: Dict[str, int] = field(default_factory=dict)
    peak_hours: List[int] = field(default_factory=list)
    peak_days: List[str] = field(default_factory=list)
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)

@dataclass
class SecurityIntelligence:
    suspicious_users: List[Dict] = field(default_factory=list)
    potential_fraud: List[Dict] = field(default_factory=list)
    banned_users_count: int = 0
    failed_login_attempts: int = 0; unusual_activity_count: int = 0
    api_abuse_count: int = 0; overall_risk_score: float = 0.0
    security_incidents: List[Dict] = field(default_factory=list)
    vulnerability_count: int = 0

@dataclass
class ComprehensiveReport:
    timestamp: str = ""; generated_by: str = "AI Engine v9.0"
    executive_summary: str = ""; overall_health_score: float = 0.0
    top_priorities: List[str] = field(default_factory=list)
    users: Optional[Dict] = None; financials: Optional[Dict] = None
    signals: Optional[Dict] = None; growth: Optional[Dict] = None
    market: Optional[Dict] = None; security: Optional[Dict] = None
    critical_alerts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    predictions: Dict[str, Any] = field(default_factory=dict)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 6 — STATISTICAL ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class StatisticalEngine:
    @staticmethod
    def mean(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    @staticmethod
    def median(values: List[float]) -> float:
        if not values: return 0.0
        s = sorted(values); n = len(s); m = n // 2
        return (s[m-1] + s[m]) / 2 if n % 2 == 0 else s[m]

    @staticmethod
    def std(values: List[float]) -> float:
        if len(values) < 2: return 0.0
        avg = StatisticalEngine.mean(values)
        return math.sqrt(sum((x-avg)**2 for x in values) / (len(values)-1))

    @staticmethod
    def percentile(values: List[float], p: float) -> float:
        if not values: return 0.0
        s = sorted(values); idx = (p/100) * (len(s)-1)
        lo, hi = int(idx), min(int(idx)+1, len(s)-1)
        w = idx - lo
        return s[lo] * (1-w) + s[hi] * w

    @staticmethod
    def moving_average(values: List[float], window: int = 7) -> List[float]:
        if len(values) < window: return values
        return [StatisticalEngine.mean(values[max(0,i-window+1):i+1]) for i in range(len(values))]

    @staticmethod
    def linear_regression(x: List[float], y: List[float]) -> Tuple[float, float, float]:
        n = len(x)
        if n < 2: return 0.0, 0.0, 0.0
        sx, sy = sum(x), sum(y)
        sxy = sum(x[i]*y[i] for i in range(n))
        sx2 = sum(v**2 for v in x)
        slope = (n*sxy - sx*sy) / (n*sx2 - sx**2) if (n*sx2 - sx**2) != 0 else 0
        intercept = (sy - slope*sx) / n
        ym = sy / n
        ss_tot = sum((y[i]-ym)**2 for i in range(n))
        ss_res = sum((y[i]-(slope*x[i]+intercept))**2 for i in range(n))
        r2 = 1 - (ss_res/ss_tot) if ss_tot != 0 else 0
        return slope, intercept, r2

    @staticmethod
    def growth_rate(values: List[float]) -> float:
        if len(values) < 2 or values[0] == 0: return 0.0
        return ((values[-1] - values[0]) / abs(values[0])) * 100

    @staticmethod
    def volatility(values: List[float]) -> float:
        if len(values) < 2: return 0.0
        returns = [(values[i]-values[i-1])/abs(values[i-1]) if values[i-1]!=0 else 0 for i in range(1,len(values))]
        return StatisticalEngine.std(returns) * 100

    @staticmethod
    def max_drawdown(values: List[float]) -> float:
        if not values: return 0.0
        peak = values[0]; max_dd = 0.0
        for v in values:
            if v > peak: peak = v
            dd = (peak - v) / peak if peak != 0 else 0
            if dd > max_dd: max_dd = dd
        return max_dd * 100

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 7 — PREDICTIVE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class PredictiveEngine:
    @staticmethod
    def predict_revenue(historical: List[float], days_ahead: int = 30) -> Dict:
        if len(historical) < 7: return {"prediction": [], "confidence": 0}
        x = list(range(len(historical)))
        slope, intercept, r2 = StatisticalEngine.linear_regression(x, historical)
        predictions = [max(0, slope*(len(historical)+i)+intercept) for i in range(days_ahead)]
        return {"prediction": predictions, "confidence": min(abs(r2)*100, 95), "trend": "up" if slope>0 else "down" if slope<0 else "stable", "slope": slope, "r_squared": r2}

    @staticmethod
    def predict_user_growth(historical: List[int], days_ahead: int = 30) -> Dict:
        if len(historical) < 7: return {"prediction": [], "confidence": 0}
        x = list(range(len(historical)))
        y = [float(v) for v in historical]
        slope, intercept, r2 = StatisticalEngine.linear_regression(x, y)
        predictions = [max(0, int(slope*(len(historical)+i)+intercept)) for i in range(days_ahead)]
        return {"prediction": predictions, "confidence": min(abs(r2)*100, 90), "total_predicted": predictions[-1] if predictions else 0}

    @staticmethod
    def predict_churn(user_data: Dict) -> float:
        score = 0.0; factors = 0
        if user_data.get('is_vip') and user_data.get('vip_expiry'):
            try:
                expire = datetime.fromisoformat(str(user_data['vip_expiry']).replace('Z','+00:00'))
                days_left = (expire.replace(tzinfo=None) - datetime.now()).days
                if days_left < 0: score += 40
                elif days_left < 7: score += 30
                elif days_left < 14: score += 15
                factors += 1
            except: pass
        if user_data.get('last_active'):
            try:
                last = datetime.fromisoformat(str(user_data['last_active']).replace('Z','+00:00'))
                days_inactive = (datetime.now() - last.replace(tzinfo=None)).days
                if days_inactive > 30: score += 25
                elif days_inactive > 14: score += 15
                elif days_inactive > 7: score += 5
                factors += 1
            except: pass
        if user_data.get('total_trades', 0) == 0: score += 10; factors += 1
        if not user_data.get('is_vip') and user_data.get('referral_count', 0) == 0: score += 5; factors += 1
        return min(score / max(factors * 15, 1), 1.0) if factors > 0 else 0.1

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 8 — BEHAVIORAL ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class BehavioralEngine:
    @staticmethod
    def _days_since(date_str) -> int:
        if not date_str: return 999
        try:
            dt = datetime.fromisoformat(str(date_str).replace('Z','+00:00'))
            return (datetime.now() - dt.replace(tzinfo=None)).days
        except: return 999

    @staticmethod
    def classify_activity(user: Dict) -> str:
        trades = user.get('total_trades', 0)
        days_active = BehavioralEngine._days_since(user.get('last_active'))
        if days_active > 30: return "خاموش"
        if days_active > 14: return "نیمه‌فعال"
        if trades > 200: return "حرفه‌ای پرقدرت"
        if trades > 50: return "فعال"
        if trades > 10: return "معمولی"
        return "تازه‌کار"

    @staticmethod
    def classify_behavior(user: Dict) -> str:
        trades = user.get('total_trades', 0)
        is_vip = user.get('is_vip', False)
        balance = user.get('balance', 0)
        if is_vip and trades > 100 and balance > 10000000: return "نهنگ"
        if is_vip and trades > 50: return "VIP فعال"
        if is_vip: return "VIP"
        if trades > 100: return "معامله‌گر حرفه‌ای"
        if trades > 10: return "معامله‌گر"
        if balance > 1000000: return "سرمایه‌گذار"
        return "کاربر عادی"

    @staticmethod
    def calculate_risk(user: Dict) -> Tuple[float, List[str]]:
        score = 0.0; factors = []
        if user.get('is_banned'): score += 80; factors.append("مسدود شده")
        if BehavioralEngine._days_since(user.get('last_active')) > 60: score += 20; factors.append("غیرفعال طولانی")
        if user.get('total_trades', 0) == 0 and BehavioralEngine._days_since(user.get('registered_at')) > 30: score += 15; factors.append("بدون معامله")
        if user.get('vip_expiry'):
            try:
                expire = datetime.fromisoformat(str(user['vip_expiry']).replace('Z','+00:00'))
                if (expire.replace(tzinfo=None) - datetime.now()).days < 3: score += 10; factors.append("VIP در حال انقضا")
            except: pass
        return min(score, 100), factors

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 9 — IN-MEMORY DATA PROVIDER (FALLBACK)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class InMemoryDataProvider:
    _users: Dict[str, Dict] = {}
    _payments: List[Dict] = []
    _signals: List[Dict] = []
    _lock = threading.RLock()

    @classmethod
    def get_users(cls) -> List[Dict]: return list(cls._users.values())
    @classmethod
    def get_payments(cls) -> List[Dict]: return cls._payments
    @classmethod
    def get_signals(cls) -> List[Dict]: return cls._signals
    @classmethod
    def add_user(cls, data): cls._users[str(data.get('telegram_id', uid()))] = data
    @classmethod
    def add_payment(cls, data): cls._payments.append(data)
    @classmethod
    def add_signal(cls, data): cls._signals.append(data)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 10 — DATA PROVIDER (REAL + FALLBACK)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class DataProvider:
    @staticmethod
    def get_users() -> List[Dict]:
        if get_user_repo:
            try:
                repo = get_user_repo() if callable(get_user_repo) else get_user_repo
                if hasattr(repo, 'get_all'): return repo.get_all()
                if hasattr(repo, 'get_all_users'): return repo.get_all_users()
            except: pass
        if db_manager:
            try:
                dm = db_manager() if callable(db_manager) else db_manager
                if hasattr(dm, 'get_all_users'): return dm.get_all_users()
            except: pass
        return InMemoryDataProvider.get_users()

    @staticmethod
    def get_payments() -> List[Dict]:
        if get_payment_repo:
            try:
                repo = get_payment_repo() if callable(get_payment_repo) else get_payment_repo
                if hasattr(repo, 'get_all'): return repo.get_all()
                if hasattr(repo, 'get_all_payments'): return repo.get_all_payments()
            except: pass
        return InMemoryDataProvider.get_payments()

    @staticmethod
    def get_signals() -> List[Dict]:
        if get_signal_repo:
            try:
                repo = get_signal_repo() if callable(get_signal_repo) else get_signal_repo
                if hasattr(repo, 'get_all'): return repo.get_all()
                if hasattr(repo, 'get_signals'): return repo.get_signals(limit=10000)
            except: pass
        return InMemoryDataProvider.get_signals()

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 11 — INTELLIGENCE ENGINES
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class UserIntelligenceEngine:
    @staticmethod
    def analyze(users: List[Dict]) -> Dict:
        if not users: return {"total": 0, "segments": {}, "risk_distribution": {}, "top_users": [], "avg_health": 0}
        segments = defaultdict(int)
        risks = defaultdict(int)
        profiles = []
        for u in users:
            risk_score, risk_factors = BehavioralEngine.calculate_risk(u)
            churn = PredictiveEngine.predict_churn(u)
            behavior = BehavioralEngine.classify_behavior(u)
            segments[behavior] += 1
            rl = "high" if risk_score > 60 else ("medium" if risk_score > 30 else "low")
            risks[rl] += 1
            profiles.append({
                "user_id": u.get('telegram_id', '?'),
                "name": u.get('first_name', 'N/A'),
                "risk_score": round(risk_score, 1),
                "churn_probability": round(churn * 100, 1),
                "behavior": behavior,
                "risk_level": rl,
                "risk_factors": risk_factors,
                "is_vip": u.get('is_vip', False),
                "balance": u.get('balance', 0),
                "total_trades": u.get('total_trades', 0),
            })
        profiles.sort(key=lambda x: x['risk_score'], reverse=True)
        avg_health = 100 - StatisticalEngine.mean([p['risk_score'] for p in profiles])
        return {
            "total": len(users),
            "segments": dict(segments),
            "risk_distribution": dict(risks),
            "top_risk_users": profiles[:10],
            "avg_health_score": round(avg_health, 1),
            "vip_count": sum(1 for u in users if u.get('is_vip')),
            "active_count": sum(1 for u in users if BehavioralEngine._days_since(u.get('last_active')) <= 7),
        }

class FinancialIntelligenceEngine:
    @staticmethod
    def analyze(payments: List[Dict]) -> Dict:
        if not payments: return {"total_revenue": 0, "total_transactions": 0, "avg_transaction": 0}
        approved = [p for p in payments if p.get('status') == 'approved' and p.get('amount', 0) > 0]
        total = sum(p.get('amount', 0) for p in approved)
        amounts = [p.get('amount', 0) for p in approved]
        today_str = today()
        today_rev = sum(p.get('amount', 0) for p in approved if p.get('created_at', '').startswith(today_str))
        plan_dist = defaultdict(int)
        plan_rev = defaultdict(float)
        for p in approved:
            plan = p.get('plan', p.get('type', 'unknown'))
            plan_dist[plan] += 1
            plan_rev[plan] += p.get('amount', 0)
        return {
            "total_revenue": round(total, 2),
            "today_revenue": round(today_rev, 2),
            "total_transactions": len(approved),
            "avg_transaction": round(StatisticalEngine.mean(amounts), 2),
            "median_transaction": round(StatisticalEngine.median(amounts), 2),
            "max_transaction": round(max(amounts) if amounts else 0, 2),
            "plan_distribution": dict(plan_dist),
            "plan_revenue": {k: round(v, 2) for k, v in plan_rev.items()},
            "top_plan": max(plan_dist, key=plan_dist.get) if plan_dist else "none",
        }

class SignalIntelligenceEngine:
    @staticmethod
    def analyze(signals: List[Dict]) -> Dict:
        if not signals: return {"total": 0, "win_rate": 0, "avg_confidence": 0}
        total = len(signals)
        closed = [s for s in signals if s.get('status') == 'closed']
        won = [s for s in closed if s.get('hit_target')]
        lost = [s for s in closed if s.get('hit_stop')]
        win_rate = (len(won) / len(closed) * 100) if closed else 0
        confidences = [s.get('confidence', 50) for s in signals]
        profits = [s.get('profit_percent', 0) or 0 for s in closed]
        by_coin = defaultdict(lambda: {"total": 0, "won": 0, "lost": 0})
        for s in signals:
            c = s.get('coin', '?')
            by_coin[c]["total"] += 1
            if s.get('hit_target'): by_coin[c]["won"] += 1
            if s.get('hit_stop'): by_coin[c]["lost"] += 1
        coin_perf = {}
        for c, d in by_coin.items():
            rate = (d['won'] / d['total'] * 100) if d['total'] > 0 else 0
            coin_perf[c] = {"total": d['total'], "won": d['won'], "lost": d['lost'], "win_rate": round(rate, 1)}
        return {
            "total": total,
            "closed": len(closed),
            "active": len([s for s in signals if s.get('status') == 'active']),
            "win_rate": round(win_rate, 1),
            "avg_confidence": round(StatisticalEngine.mean(confidences), 1),
            "avg_profit": round(StatisticalEngine.mean([p for p in profits if p > 0]), 2),
            "avg_loss": round(abs(StatisticalEngine.mean([p for p in profits if p < 0])), 2),
            "net_profit": round(sum(profits), 2),
            "max_drawdown": round(StatisticalEngine.max_drawdown(profits), 2),
            "coin_performance": coin_perf,
            "best_coin": max(coin_perf, key=lambda x: coin_perf[x]['win_rate']) if coin_perf else "none",
            "worst_coin": min(coin_perf, key=lambda x: coin_perf[x]['win_rate']) if coin_perf else "none",
        }

class GrowthIntelligenceEngine:
    @staticmethod
    def analyze(users: List[Dict]) -> Dict:
        if not users: return {"total": 0, "new_today": 0}
        today_str = today()
        new_today = sum(1 for u in users if u.get('created_at', '').startswith(today_str))
        active_7d = sum(1 for u in users if BehavioralEngine._days_since(u.get('last_active')) <= 7)
        active_30d = sum(1 for u in users if BehavioralEngine._days_since(u.get('last_active')) <= 30)
        return {
            "total": len(users),
            "new_today": new_today,
            "active_7d": active_7d,
            "active_30d": active_30d,
            "vip_count": sum(1 for u in users if u.get('is_vip')),
            "trial_count": sum(1 for u in users if u.get('is_trial')),
            "referral_users": sum(1 for u in users if u.get('referrals', 0) > 0),
        }

class SecurityIntelligenceEngine:
    @staticmethod
    def analyze(users: List[Dict]) -> Dict:
        if not users: return {"banned": 0, "suspicious": 0, "overall_risk": 0}
        banned = [u for u in users if u.get('is_banned')]
        suspicious = []
        for u in users:
            risk, factors = BehavioralEngine.calculate_risk(u)
            if risk > 60:
                suspicious.append({"user_id": u.get('telegram_id'), "name": u.get('first_name'), "risk": risk, "factors": factors})
        suspicious.sort(key=lambda x: x['risk'], reverse=True)
        return {
            "total_users": len(users),
            "banned": len(banned),
            "suspicious": len(suspicious),
            "top_suspicious": suspicious[:10],
            "overall_risk": round(StatisticalEngine.mean([s['risk'] for s in suspicious]) if suspicious else 0, 1),
        }

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 12 — ADMIN INTELLIGENCE ENGINE (FACADE)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class AdminIntelligenceEngine:
    """Main Intelligence Engine — Facade for all sub-engines"""

    def __init__(self):
        self.users = DataProvider.get_users()
        self.payments = DataProvider.get_payments()
        self.signals = DataProvider.get_signals()

    def refresh(self):
        self.users = DataProvider.get_users()
        self.payments = DataProvider.get_payments()
        self.signals = DataProvider.get_signals()

    def get_user_intelligence(self) -> Dict:
        return UserIntelligenceEngine.analyze(self.users)

    def get_financial_intelligence(self) -> Dict:
        return FinancialIntelligenceEngine.analyze(self.payments)

    def get_signal_intelligence(self) -> Dict:
        return SignalIntelligenceEngine.analyze(self.signals)

    def get_growth_intelligence(self) -> Dict:
        return GrowthIntelligenceEngine.analyze(self.users)

    def get_security_intelligence(self) -> Dict:
        return SecurityIntelligenceEngine.analyze(self.users)

    def get_full_dashboard(self) -> Dict:
        self.refresh()
        user_intel = self.get_user_intelligence()
        fin_intel = self.get_financial_intelligence()
        sig_intel = self.get_signal_intelligence()
        growth_intel = self.get_growth_intelligence()
        sec_intel = self.get_security_intelligence()

        alerts = []
        if fin_intel.get('today_revenue', 0) == 0: alerts.append("⚠️ درآمد امروز صفر است")
        if sig_intel.get('win_rate', 100) < 40: alerts.append("🚨 نرخ برد سیگنال‌ها زیر ۴۰٪")
        if sec_intel.get('suspicious', 0) > 5: alerts.append("🔴 تعداد کاربران مشکوک بالاست")
        if user_intel.get('active_count', 0) < user_intel.get('total', 1) * 0.1: alerts.append("⚠️ نرخ فعالیت کاربران پایین است")

        return {
            "timestamp": now(),
            "generated_by": f"AdminIntelligenceEngine v{BOT_VERSION}",
            "user_intelligence": user_intel,
            "financial_intelligence": fin_intel,
            "signal_intelligence": sig_intel,
            "growth_intelligence": growth_intel,
            "security_intelligence": sec_intel,
            "alerts": alerts,
            "overall_health": round(
                (user_intel.get('avg_health_score', 50) +
                 (100 - sec_intel.get('overall_risk', 50)) +
                 min(sig_intel.get('win_rate', 0) * 1.5, 100)) / 3, 1
            ),
        }

    def generate_comprehensive_report(self) -> Dict:
        dashboard = self.get_full_dashboard()
        insights = []
        recommendations = []

        if dashboard['financial_intelligence'].get('total_revenue', 0) > 0:
            insights.append(f"💰 درآمد کل: {fmt_irt(dashboard['financial_intelligence']['total_revenue'])}")
        if dashboard['user_intelligence'].get('vip_count', 0) > 0:
            insights.append(f"💎 تعداد کاربران VIP: {dashboard['user_intelligence']['vip_count']}")
        if dashboard['signal_intelligence'].get('win_rate', 0) > 0:
            insights.append(f"📈 نرخ برد سیگنال‌ها: {dashboard['signal_intelligence']['win_rate']}%")

        if dashboard['signal_intelligence'].get('win_rate', 100) < 50:
            recommendations.append("بهبود کیفیت سیگنال‌ها با بررسی الگوریتم تحلیل")
        if dashboard['user_intelligence'].get('active_count', 0) < dashboard['user_intelligence'].get('total', 1) * 0.2:
            recommendations.append("ارسال نوتیفیکیشن برای کاربران غیرفعال")
        if dashboard['financial_intelligence'].get('today_revenue', 0) < 100000:
            recommendations.append("برگزاری کمپین تخفیف VIP برای افزایش درآمد")

        return {
            **dashboard,
            "insights": insights,
            "recommendations": recommendations,
            "critical_alerts": dashboard['alerts'],
        }

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 13 — EXPORT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

_instance: Optional[AdminIntelligenceEngine] = None
_lock = threading.Lock()

def get_intelligence_engine() -> AdminIntelligenceEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = AdminIntelligenceEngine()
    return _instance

def start() -> bool:
    return True

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 14 — STANDALONE
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    engine = get_intelligence_engine()
    report = engine.generate_comprehensive_report()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
