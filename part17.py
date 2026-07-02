#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   📊 CryptoPulse AI - Advanced Technical & Fundamental Analysis Engine v5.0       ║
║   ─────────────────────────────────────────────────────────────────────────────    ║
║   🔬 Technical Analysis  |  📈 Price Action  |  🕯️ Candlestick Patterns         ║
║   📐 Fibonacci  |  🐋 Whale Tracking  |  🌟 Star Patterns  |  📊 Oscillators    ║
║   🏛️ Fundamental Analysis  |  🔮 Elliott Wave  |  📡 On-Chain Data             ║
║                                                                                    ║
║   ═══════════════════════════════════════════════════════════════════════════════   ║
║   📁 ۱۰۰۰۰+ خط کد  |  ⚡ فوق‌بهینه  |  🔥 حرفه‌ای  |  🛡️ ضد خطا                ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import math
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Set
from collections import defaultdict, OrderedDict, deque
from dataclasses import dataclass, field, asdict
from enum import Enum
import warnings

warnings.filterwarnings("ignore")

# ============================================================
#                    IMPORTS
# ============================================================

def safe_import(module_name: str, *attrs):
    result = {}
    try:
        module = __import__(module_name, fromlist=attrs)
        for attr in attrs:
            result[attr] = getattr(module, attr, None)
    except:
        for attr in attrs:
            result[attr] = None
    return result

_bot3 = safe_import("bot3", "get_signal_repo", "db_manager")
_bot5 = safe_import("bot5", "get_market", "get_coinex")
_bot6 = safe_import("bot6", "get_ai", "get_groq")

get_signal_repo = _bot3.get("get_signal_repo")
db_manager = _bot3.get("db_manager")
get_market = _bot5.get("get_market")
get_coinex = _bot5.get("get_coinex")
get_ai = _bot6.get("get_ai")
get_groq = _bot6.get("get_groq")

# ============================================================
#                    ENUMS
# ============================================================

class SignalType(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    WEAK_BUY = "weak_buy"
    NEUTRAL = "neutral"
    WEAK_SELL = "weak_sell"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

class TrendType(Enum):
    STRONG_UPTREND = "strong_uptrend"
    UPTREND = "uptrend"
    WEAK_UPTREND = "weak_uptrend"
    SIDEWAYS = "sideways"
    WEAK_DOWNTREND = "weak_downtrend"
    DOWNTREND = "downtrend"
    STRONG_DOWNTREND = "strong_downtrend"

class PatternType(Enum):
    # Bullish Patterns
    BULLISH_ENGULFING = "bullish_engulfing"
    BULLISH_HARAMI = "bullish_harami"
    MORNING_STAR = "morning_star"
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    PIERCING_LINE = "piercing_line"
    HAMMER = "hammer"
    INVERTED_HAMMER = "inverted_hammer"
    DOJI_DRAGONFLY = "doji_dragonfly"
    BULLISH_ABANDONED_BABY = "bullish_abandoned_baby"
    BULLISH_KICKER = "bullish_kicker"
    THREE_INSIDE_UP = "three_inside_up"
    THREE_OUTSIDE_UP = "three_outside_up"
    TWEEZER_BOTTOM = "tweezer_bottom"
    
    # Bearish Patterns
    BEARISH_ENGULFING = "bearish_engulfing"
    BEARISH_HARAMI = "bearish_harami"
    EVENING_STAR = "evening_star"
    THREE_BLACK_CROWS = "three_black_crows"
    DARK_CLOUD_COVER = "dark_cloud_cover"
    HANGING_MAN = "hanging_man"
    SHOOTING_STAR = "shooting_star"
    DOJI_GRAVESTONE = "doji_gravestone"
    BEARISH_ABANDONED_BABY = "bearish_abandoned_baby"
    BEARISH_KICKER = "bearish_kicker"
    THREE_INSIDE_DOWN = "three_inside_down"
    THREE_OUTSIDE_DOWN = "three_outside_down"
    TWEEZER_TOP = "tweezer_top"
    
    # Continuation Patterns
    DOJI = "doji"
    SPINNING_TOP = "spinning_top"
    MARUBOZU = "marubozu"
    LONG_LEGGED_DOJI = "long_legged_doji"

class FibonacciLevel(Enum):
    LEVEL_0 = 0.0
    LEVEL_236 = 0.236
    LEVEL_382 = 0.382
    LEVEL_500 = 0.5
    LEVEL_618 = 0.618
    LEVEL_786 = 0.786
    LEVEL_100 = 1.0
    LEVEL_1272 = 1.272
    LEVEL_1414 = 1.414
    LEVEL_1618 = 1.618
    LEVEL_2000 = 2.0
    LEVEL_2618 = 2.618
    LEVEL_3618 = 3.618
    LEVEL_4236 = 4.236

class WhaleActivity(Enum):
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    WHALE_BUY = "whale_buy"
    WHALE_SELL = "whale_sell"
    SMART_MONEY_IN = "smart_money_in"
    SMART_MONEY_OUT = "smart_money_out"

# ============================================================
#                    DATA MODELS
# ============================================================

@dataclass
class OHLCV:
    """مدل داده کندل"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @property
    def body(self) -> float:
        return abs(self.close - self.open)
    
    @property
    def range(self) -> float:
        return self.high - self.low
    
    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)
    
    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low
    
    @property
    def is_bullish(self) -> bool:
        return self.close > self.open
    
    @property
    def is_bearish(self) -> bool:
        return self.close < self.open
    
    @property
    def body_percentage(self) -> float:
        return (self.body / self.range * 100) if self.range > 0 else 0
    
    @property
    def upper_wick_percentage(self) -> float:
        return (self.upper_wick / self.range * 100) if self.range > 0 else 0
    
    @property
    def lower_wick_percentage(self) -> float:
        return (self.lower_wick / self.range * 100) if self.range > 0 else 0

@dataclass
class IndicatorResult:
    """نتیجه محاسبه اندیکاتور"""
    name: str
    value: float
    signal: str = "neutral"
    strength: float = 50.0
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PatternResult:
    """نتیجه تشخیص الگو"""
    pattern: PatternType
    type: str  # bullish, bearish, continuation
    strength: float  # 0-100
    confidence: float  # 0-100
    candles_needed: int
    description: str = ""
    reliability: float = 0.0

@dataclass
class FibonacciResult:
    """نتیجه محاسبه فیبوناچی"""
    swing_low: float
    swing_high: float
    is_uptrend: bool
    retracement_levels: Dict[str, float] = field(default_factory=dict)
    extension_levels: Dict[str, float] = field(default_factory=dict)
    current_position: float = 0.0
    nearest_support: float = 0.0
    nearest_resistance: float = 0.0

@dataclass
class WhaleActivityData:
    """داده فعالیت نهنگ"""
    timestamp: int
    type: WhaleActivity
    volume: float
    price: float
    value_usd: float = 0.0
    exchange: str = "unknown"
    wallet_count: int = 0
    avg_transaction: float = 0.0

@dataclass
class TechnicalAnalysisResult:
    """نتیجه کامل تحلیل تکنیکال"""
    coin: str
    timeframe: str
    timestamp: int
    
    # Price
    current_price: float
    change_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    
    # Trend
    trend: str
    trend_strength: float
    trend_duration: int
    
    # Oscillators
    rsi: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="RSI", value=50))
    stochastic: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="Stochastic", value=50))
    cci: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="CCI", value=0))
    williams_r: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="Williams %R", value=-50))
    mfi: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="MFI", value=50))
    ultimate_oscillator: IndicatorResult = field(default_factory=lambda: IndicatorResult(name="Ultimate Oscillator", value=50))
    
    # Moving Averages
    sma_signals: Dict[str, str] = field(default_factory=dict)
    ema_signals: Dict[str, str] = field(default_factory=dict)
    ma_crossovers: List[str] = field(default_factory=list)
    
    # MACD
    macd: float = 0.0
    macd_signal: float = 0.0
    macd_histogram: float = 0.0
    macd_crossover: str = "none"
    
    # Bollinger Bands
    bb_upper: float = 0.0
    bb_middle: float = 0.0
    bb_lower: float = 0.0
    bb_position: float = 0.0
    bb_squeeze: bool = False
    
    # Ichimoku
    ichimoku_signal: str = "neutral"
    ichimoku_cloud_status: str = "none"
    
    # ADX / DMI
    adx: float = 0.0
    plus_di: float = 0.0
    minus_di: float = 0.0
    adx_trend_strength: str = "weak"
    
    # ATR
    atr: float = 0.0
    atr_percentage: float = 0.0
    
    # Parabolic SAR
    sar: float = 0.0
    sar_signal: str = "none"
    
    # Volume
    obv_trend: str = "neutral"
    volume_trend: str = "normal"
    volume_ratio: float = 1.0
    
    # Patterns
    candlestick_patterns: List[PatternResult] = field(default_factory=list)
    chart_patterns: List[str] = field(default_factory=list)
    
    # Fibonacci
    fibonacci: Optional[FibonacciResult] = None
    
    # Whale Activity
    whale_activity: List[WhaleActivityData] = field(default_factory=list)
    whale_signal: str = "neutral"
    
    # Support & Resistance
    supports: List[Dict[str, float]] = field(default_factory=list)
    resistances: List[Dict[str, float]] = field(default_factory=list)
    
    # Pivot Points
    pivot: float = 0.0
    pivot_r1: float = 0.0
    pivot_r2: float = 0.0
    pivot_r3: float = 0.0
    pivot_s1: float = 0.0
    pivot_s2: float = 0.0
    pivot_s3: float = 0.0
    
    # Price Action
    price_action_signals: List[str] = field(default_factory=list)
    market_structure: str = "unknown"
    
    # Divergences
    divergences: List[Dict[str, str]] = field(default_factory=list)
    
    # Final Signal
    overall_signal: str = "neutral"
    signal_strength: float = 50.0
    confidence: float = 50.0
    risk_reward: float = 0.0
    stop_loss: float = 0.0
    take_profits: List[float] = field(default_factory=list)
    
    # Summary
    summary: str = ""
    key_levels: List[float] = field(default_factory=list)
    recommendation: str = ""

@dataclass
class FundamentalAnalysisResult:
    """نتیجه تحلیل فاندامنتال"""
    coin: str
    
    # Market Metrics
    market_cap: float = 0.0
    market_cap_rank: int = 0
    fully_diluted_valuation: float = 0.0
    total_supply: float = 0.0
    circulating_supply: float = 0.0
    max_supply: float = 0.0
    
    # Volume
    volume_24h: float = 0.0
    volume_market_cap_ratio: float = 0.0
    volume_change_24h: float = 0.0
    
    # Price Changes
    price_change_1h: float = 0.0
    price_change_24h: float = 0.0
    price_change_7d: float = 0.0
    price_change_30d: float = 0.0
    price_change_1y: float = 0.0
    ath: float = 0.0
    ath_date: str = ""
    ath_change: float = 0.0
    atl: float = 0.0
    atl_date: str = ""
    atl_change: float = 0.0
    
    # On-Chain Metrics (if available)
    active_addresses_24h: int = 0
    transaction_count_24h: int = 0
    average_transaction_value: float = 0.0
    hash_rate: float = 0.0
    difficulty: float = 0.0
    network_value_to_transactions: float = 0.0
    mvrv_ratio: float = 0.0  # Market Value to Realized Value
    puell_multiple: float = 0.0
    stock_to_flow: float = 0.0
    
    # Sentiment
    fear_greed_index: int = 50
    social_volume: int = 0
    social_engagement: int = 0
    sentiment_score: float = 0.0
    news_sentiment: str = "neutral"
    
    # Development
    github_commits_30d: int = 0
    github_contributors: int = 0
    developer_score: float = 0.0
    
    # Community
    twitter_followers: int = 0
    reddit_subscribers: int = 0
    telegram_members: int = 0
    community_score: float = 0.0
    
    # Institutional
    institutional_interest: str = "unknown"
    etf_flow: float = 0.0
    grayscale_premium: float = 0.0
    
    # Summary
    overall_score: float = 50.0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    summary: str = ""
    recommendation: str = "neutral"

@dataclass
class StarPlanetData:
    """داده‌های ستاره‌شناسی مالی (Financial Astrology)"""
    date: str
    mercury_retrograde: bool = False
    venus_retrograde: bool = False
    mars_retrograde: bool = False
    jupiter_aspect: str = "none"
    saturn_aspect: str = "none"
    moon_phase: str = "new_moon"
    solar_eclipse: bool = False
    lunar_eclipse: bool = False
    market_sentiment_forecast: str = "neutral"
    historical_correlation: float = 0.0

# ============================================================
#                    TECHNICAL INDICATORS ENGINE
# ============================================================

class TechnicalIndicators:
    """موتور محاسبه اندیکاتورهای تکنیکال"""
    
    # ============================================================
    #                    MOVING AVERAGES
    # ============================================================
    
    @staticmethod
    def sma(data: List[float], period: int) -> List[float]:
        """Simple Moving Average"""
        if len(data) < period:
            return [0.0] * len(data)
        result = [0.0] * (period - 1)
        window = data[:period]
        window_sum = sum(window)
        result.append(window_sum / period)
        for i in range(period, len(data)):
            window_sum = window_sum - data[i - period] + data[i]
            result.append(window_sum / period)
        return result
    
    @staticmethod
    def ema(data: List[float], period: int) -> List[float]:
        """Exponential Moving Average"""
        if len(data) < period:
            return [0.0] * len(data)
        result = [0.0] * (period - 1)
        multiplier = 2.0 / (period + 1.0)
        ema_value = sum(data[:period]) / period
        result.append(ema_value)
        for i in range(period, len(data)):
            ema_value = (data[i] - ema_value) * multiplier + ema_value
            result.append(ema_value)
        return result
    
    @staticmethod
    def wma(data: List[float], period: int) -> List[float]:
        """Weighted Moving Average"""
        if len(data) < period:
            return [0.0] * len(data)
        result = [0.0] * (period - 1)
        weights = list(range(1, period + 1))
        weight_sum = sum(weights)
        for i in range(period - 1, len(data)):
            wma_value = sum(w * data[i - period + 1 + j] for j, w in enumerate(weights)) / weight_sum
            result.append(wma_value)
        return result
    
    @staticmethod
    def hull_ma(data: List[float], period: int) -> List[float]:
        """Hull Moving Average"""
        if len(data) < period:
            return [0.0] * len(data)
        half_period = int(period / 2)
        sqrt_period = int(math.sqrt(period))
        
        wma_half = TechnicalIndicators.wma(data, half_period)
        wma_full = TechnicalIndicators.wma(data, period)
        
        raw_hma = [2.0 * wma_half[i] - wma_full[i] for i in range(len(data))]
        result = TechnicalIndicators.wma(raw_hma, sqrt_period)
        
        return result
    
    # ============================================================
    #                    OSCILLATORS
    # ============================================================
    
    @staticmethod
    def rsi(data: List[float], period: int = 14) -> List[float]:
        """Relative Strength Index"""
        if len(data) < period + 1:
            return [50.0] * len(data)
        
        result = [0.0] * (period)
        gains = []
        losses = []
        
        for i in range(1, period + 1):
            change = data[i] - data[i - 1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100.0 - (100.0 / (1.0 + rs)))
        
        for i in range(period + 1, len(data)):
            change = data[i] - data[i - 1]
            gain = max(change, 0)
            loss = max(-change, 0)
            
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            if avg_loss == 0:
                result.append(100.0)
            else:
                rs = avg_gain / avg_loss
                result.append(100.0 - (100.0 / (1.0 + rs)))
        
        return result
    
    @staticmethod
    def stochastic(high: List[float], low: List[float], close: List[float], 
                   k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Stochastic Oscillator (%K and %D)"""
        if len(close) < k_period:
            return ([50.0] * len(close), [50.0] * len(close))
        
        k_values = [0.0] * (k_period - 1)
        
        for i in range(k_period - 1, len(close)):
            highest = max(high[i - k_period + 1:i + 1])
            lowest = min(low[i - k_period + 1:i + 1])
            
            if highest == lowest:
                k_values.append(50.0)
            else:
                k_values.append(((close[i] - lowest) / (highest - lowest)) * 100.0)
        
        d_values = TechnicalIndicators.sma(k_values, d_period)
        
        return k_values, d_values
    
    @staticmethod
    def cci(high: List[float], low: List[float], close: List[float], period: int = 20) -> List[float]:
        """Commodity Channel Index"""
        if len(close) < period:
            return [0.0] * len(close)
        
        result = [0.0] * (period - 1)
        typical_prices = [(h + l + c) / 3.0 for h, l, c in zip(high, low, close)]
        
        for i in range(period - 1, len(close)):
            tp_slice = typical_prices[i - period + 1:i + 1]
            sma_tp = sum(tp_slice) / period
            mean_deviation = sum(abs(tp - sma_tp) for tp in tp_slice) / period
            
            if mean_deviation == 0:
                result.append(0.0)
            else:
                result.append((typical_prices[i] - sma_tp) / (0.015 * mean_deviation))
        
        return result
    
    @staticmethod
    def williams_r(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        """Williams %R"""
        if len(close) < period:
            return [-50.0] * len(close)
        
        result = [0.0] * (period - 1)
        
        for i in range(period - 1, len(close)):
            highest = max(high[i - period + 1:i + 1])
            lowest = min(low[i - period + 1:i + 1])
            
            if highest == lowest:
                result.append(-50.0)
            else:
                result.append(((highest - close[i]) / (highest - lowest)) * -100.0)
        
        return result
    
    @staticmethod
    def mfi(high: List[float], low: List[float], close: List[float], volume: List[float], period: int = 14) -> List[float]:
        """Money Flow Index"""
        if len(close) < period + 1:
            return [50.0] * len(close)
        
        result = [0.0] * (period)
        typical_prices = [(h + l + c) / 3.0 for h, l, c in zip(high, low, close)]
        money_flows = [tp * v for tp, v in zip(typical_prices, volume)]
        
        for i in range(period, len(close)):
            pos_flow = 0.0
            neg_flow = 0.0
            
            for j in range(i - period + 1, i + 1):
                if typical_prices[j] > typical_prices[j - 1]:
                    pos_flow += money_flows[j]
                elif typical_prices[j] < typical_prices[j - 1]:
                    neg_flow += money_flows[j]
            
            if neg_flow == 0:
                result.append(100.0)
            else:
                money_ratio = pos_flow / neg_flow
                result.append(100.0 - (100.0 / (1.0 + money_ratio)))
        
        return result
    
    @staticmethod
    def ultimate_oscillator(high: List[float], low: List[float], close: List[float],
                           period1: int = 7, period2: int = 14, period3: int = 28) -> List[float]:
        """Ultimate Oscillator"""
        max_period = max(period1, period2, period3)
        if len(close) < max_period + 1:
            return [50.0] * len(close)
        
        result = [0.0] * (max_period)
        
        for i in range(max_period, len(close)):
            bp = close[i] - min(low[i], close[i - 1])
            tr = max(high[i], close[i - 1]) - min(low[i], close[i - 1])
            
            if tr == 0:
                result.append(50.0)
                continue
            
            avg1 = sum(bp for _ in range(i - period1 + 1, i + 1)) / sum(
                tr for _ in range(i - period1 + 1, i + 1)) if sum(
                tr for _ in range(i - period1 + 1, i + 1)) != 0 else 0
            
            avg2 = sum(bp for _ in range(i - period2 + 1, i + 1)) / sum(
                tr for _ in range(i - period2 + 1, i + 1)) if sum(
                tr for _ in range(i - period2 + 1, i + 1)) != 0 else 0
            
            avg3 = sum(bp for _ in range(i - period3 + 1, i + 1)) / sum(
                tr for _ in range(i - period3 + 1, i + 1)) if sum(
                tr for _ in range(i - period3 + 1, i + 1)) != 0 else 0
            
            result.append(((4.0 * avg1 + 2.0 * avg2 + avg3) / 7.0) * 100.0)
        
        return result
    
    @staticmethod
    def awesome_oscillator(high: List[float], low: List[float]) -> List[float]:
        """Awesome Oscillator"""
        if len(high) < 34:
            return [0.0] * len(high)
        
        median_prices = [(h + l) / 2.0 for h, l in zip(high, low)]
        sma5 = TechnicalIndicators.sma(median_prices, 5)
        sma34 = TechnicalIndicators.sma(median_prices, 34)
        
        return [sma5[i] - sma34[i] for i in range(len(median_prices))]
    
    # ============================================================
    #                    MACD
    # ============================================================
    
    @staticmethod
    def macd(data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """MACD Line, Signal Line, Histogram"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        
        macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(data))]
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = [macd_line[i] - signal_line[i] for i in range(len(data))]
        
        return macd_line, signal_line, histogram
    
    # ============================================================
    #                    BOLLINGER BANDS
    # ============================================================
    
    @staticmethod
    def bollinger_bands(data: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """Bollinger Bands (Upper, Middle, Lower)"""
        if len(data) < period:
            return ([0.0] * len(data), [0.0] * len(data), [0.0] * len(data))
        
        middle = TechnicalIndicators.sma(data, period)
        upper = [0.0] * len(data)
        lower = [0.0] * len(data)
        
        for i in range(period - 1, len(data)):
            window = data[i - period + 1:i + 1]
            mean = sum(window) / period
            variance = sum((x - mean) ** 2 for x in window) / period
            std = math.sqrt(variance)
            
            upper[i] = middle[i] + std_dev * std
            lower[i] = middle[i] - std_dev * std
        
        return upper, middle, lower
    
    @staticmethod
    def bandwidth(upper: List[float], middle: List[float], lower: List[float]) -> List[float]:
        """Bollinger Bandwidth"""
        return [(u - l) / m if m != 0 else 0.0 for u, m, l in zip(upper, middle, lower)]
    
    @staticmethod
    def bb_percent(close: List[float], upper: List[float], lower: List[float]) -> List[float]:
        """%B Indicator"""
        return [(c - l) / (u - l) if (u - l) != 0 else 0.5 for c, u, l in zip(close, upper, lower)]
    
    # ============================================================
    #                    ICHIMOKU CLOUD
    # ============================================================
    
    @staticmethod
    def ichimoku(high: List[float], low: List[float], close: List[float],
                tenkan_period: int = 9, kijun_period: int = 26, senkou_b_period: int = 52) -> Dict[str, List[float]]:
        """Ichimoku Cloud"""
        if len(close) < senkou_b_period:
            return {
                "tenkan_sen": [0.0] * len(close),
                "kijun_sen": [0.0] * len(close),
                "senkou_span_a": [0.0] * len(close),
                "senkou_span_b": [0.0] * len(close),
                "chikou_span": [0.0] * len(close),
            }
        
        tenkan_sen = [0.0] * (tenkan_period - 1)
        kijun_sen = [0.0] * (kijun_period - 1)
        senkou_span_a = [0.0] * (kijun_period + 25)
        senkou_span_b = [0.0] * (senkou_b_period + 25)
        chikou_span = [0.0] * 26 + close[26:]
        
        for i in range(tenkan_period - 1, len(close)):
            tenkan_sen.append((max(high[i - tenkan_period + 1:i + 1]) + min(low[i - tenkan_period + 1:i + 1])) / 2.0)
        
        for i in range(kijun_period - 1, len(close)):
            kijun_sen.append((max(high[i - kijun_period + 1:i + 1]) + min(low[i - kijun_period + 1:i + 1])) / 2.0)
        
        for i in range(kijun_period - 1, len(close) - 26):
            senkou_span_a.append((tenkan_sen[i] + kijun_sen[i]) / 2.0)
        
        for i in range(senkou_b_period - 1, len(close) - 26):
            senkou_span_b.append((max(high[i - senkou_b_period + 1:i + 1]) + min(low[i - senkou_b_period + 1:i + 1])) / 2.0)
        
        while len(senkou_span_a) < len(close):
            senkou_span_a.append(0.0)
            senkou_span_b.append(0.0)
        
        return {
            "tenkan_sen": tenkan_sen,
            "kijun_sen": kijun_sen,
            "senkou_span_a": senkou_span_a,
            "senkou_span_b": senkou_span_b,
            "chikou_span": chikou_span,
        }
    
    # ============================================================
    #                    ADX / DMI
    # ============================================================
    
    @staticmethod
    def adx(high: List[float], low: List[float], close: List[float], period: int = 14) -> Tuple[List[float], List[float], List[float]]:
        """ADX, +DI, -DI"""
        if len(close) < period * 2:
            return ([0.0] * len(close), [0.0] * len(close), [0.0] * len(close))
        
        adx_values = [0.0] * (period * 2 - 1)
        plus_di = [0.0] * (period - 1)
        minus_di = [0.0] * (period - 1)
        
        tr = [0.0]
        plus_dm = [0.0]
        minus_dm = [0.0]
        
        for i in range(1, len(close)):
            tr.append(max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])))
            
            up_move = high[i] - high[i - 1]
            down_move = low[i - 1] - low[i]
            
            plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
            minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)
        
        for i in range(period - 1, len(close)):
            tr_sum = sum(tr[i - period + 1:i + 1])
            plus_dm_sum = sum(plus_dm[i - period + 1:i + 1])
            minus_dm_sum = sum(minus_dm[i - period + 1:i + 1])
            
            plus_di_val = (plus_dm_sum / tr_sum * 100.0) if tr_sum != 0 else 0.0
            minus_di_val = (minus_dm_sum / tr_sum * 100.0) if tr_sum != 0 else 0.0
            
            plus_di.append(plus_di_val)
            minus_di.append(minus_di_val)
            
            dx = abs(plus_di_val - minus_di_val) / (plus_di_val + minus_di_val) * 100.0 if (plus_di_val + minus_di_val) != 0 else 0.0
            adx_values.append(dx)
        
        # Smooth ADX
        smoothed_adx = TechnicalIndicators.ema(adx_values, period)
        
        return smoothed_adx, plus_di, minus_di
    
    # ============================================================
    #                    ATR
    # ============================================================
    
    @staticmethod
    def atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> List[float]:
        """Average True Range"""
        if len(close) < period + 1:
            return [0.0] * len(close)
        
        tr_values = [0.0]
        for i in range(1, len(close)):
            tr = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
            tr_values.append(tr)
        
        atr_values = [0.0] * period
        atr_values.append(sum(tr_values[1:period + 1]) / period)
        
        for i in range(period + 1, len(close)):
            atr_values.append((atr_values[i - 1] * (period - 1) + tr_values[i]) / period)
        
        return atr_values
    
    # ============================================================
    #                    PARABOLIC SAR
    # ============================================================
    
    @staticmethod
    def parabolic_sar(high: List[float], low: List[float], 
                      acceleration: float = 0.02, maximum: float = 0.2) -> List[float]:
        """Parabolic SAR"""
        if len(high) < 2:
            return [0.0] * len(high)
        
        sar_values = [0.0] * len(high)
        
        # Initial values
        is_uptrend = True
        sar = low[0]
        ep = high[0]  # Extreme Point
        af = acceleration
        
        for i in range(1, len(high)):
            if is_uptrend:
                sar = sar + af * (ep - sar)
                
                if sar > low[i]:
                    is_uptrend = False
                    sar = ep
                    ep = low[i]
                    af = acceleration
                else:
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + acceleration, maximum)
                    
                    if i > 0:
                        sar = min(sar, low[i - 1])
            else:
                sar = sar + af * (ep - sar)
                
                if sar < high[i]:
                    is_uptrend = True
                    sar = ep
                    ep = high[i]
                    af = acceleration
                else:
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + acceleration, maximum)
                    
                    if i > 0:
                        sar = max(sar, high[i - 1])
            
            sar_values[i] = sar
        
        return sar_values
    
    # ============================================================
    #                    VOLUME INDICATORS
    # ============================================================
    
    @staticmethod
    def obv(close: List[float], volume: List[float]) -> List[float]:
        """On-Balance Volume"""
        if len(close) < 1:
            return [0.0] * len(close)
        
        obv_values = [0.0]
        for i in range(1, len(close)):
            if close[i] > close[i - 1]:
                obv_values.append(obv_values[-1] + volume[i])
            elif close[i] < close[i - 1]:
                obv_values.append(obv_values[-1] - volume[i])
            else:
                obv_values.append(obv_values[-1])
        
        return obv_values
    
    @staticmethod
    def volume_profile(high: List[float], low: List[float], close: List[float], 
                       volume: List[float], bins: int = 20) -> Dict[str, Any]:
        """Volume Profile"""
        if not high:
            return {}
        
        all_prices = [h for h in high] + [l for l in low] + [c for c in close]
        min_price = min(all_prices)
        max_price = max(all_prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            return {}
        
        bin_size = price_range / bins
        profile = defaultdict(float)
        
        for i in range(len(close)):
            bin_index = int((close[i] - min_price) / bin_size)
            bin_index = min(bin_index, bins - 1)
            profile[round(min_price + bin_index * bin_size, 2)] += volume[i]
        
        # POC (Point of Control)
        poc_price = max(profile, key=profile.get) if profile else 0.0
        poc_volume = profile.get(poc_price, 0)
        
        # Value Area (70%)
        total_volume = sum(profile.values())
        target_volume = total_volume * 0.7
        sorted_prices = sorted(profile.keys(), key=lambda p: profile[p], reverse=True)
        accumulated = 0.0
        vah = 0.0
        val = 0.0
        
        for price in sorted_prices:
            accumulated += profile[price]
            if accumulated >= target_volume and vah == 0.0:
                vah = price
            val = price
        
        return {
            "poc": poc_price,
            "poc_volume": poc_volume,
            "vah": max(vah, val),  # Value Area High
            "val": min(vah, val),  # Value Area Low
            "profile": dict(sorted(profile.items())),
        }
    
    # ============================================================
    #                    VWAP
    # ============================================================
    
    @staticmethod
    def vwap(high: List[float], low: List[float], close: List[float], volume: List[float]) -> List[float]:
        """Volume Weighted Average Price"""
        if len(close) < 1:
            return [0.0] * len(close)
        
        typical_prices = [(h + l + c) / 3.0 for h, l, c in zip(high, low, close)]
        vwap_values = []
        cumulative_tp_volume = 0.0
        cumulative_volume = 0.0
        
        for i in range(len(close)):
            cumulative_tp_volume += typical_prices[i] * volume[i]
            cumulative_volume += volume[i]
            
            if cumulative_volume > 0:
                vwap_values.append(cumulative_tp_volume / cumulative_volume)
            else:
                vwap_values.append(0.0)
        
        return vwap_values
    
    # ============================================================
    #                    PIVOT POINTS
    # ============================================================
    
    @staticmethod
    def pivot_points(high: float, low: float, close: float, pivot_type: str = "standard") -> Dict[str, float]:
        """Pivot Points (Standard, Fibonacci, Woodie, Camarilla)"""
        result = {}
        
        if pivot_type == "standard":
            pp = (high + low + close) / 3.0
            result = {
                "pivot": pp,
                "r1": 2.0 * pp - low,
                "r2": pp + (high - low),
                "r3": high + 2.0 * (pp - low),
                "s1": 2.0 * pp - high,
                "s2": pp - (high - low),
                "s3": low - 2.0 * (high - pp),
            }
        elif pivot_type == "fibonacci":
            pp = (high + low + close) / 3.0
            range_hl = high - low
            result = {
                "pivot": pp,
                "r1": pp + 0.382 * range_hl,
                "r2": pp + 0.618 * range_hl,
                "r3": pp + 1.0 * range_hl,
                "s1": pp - 0.382 * range_hl,
                "s2": pp - 0.618 * range_hl,
                "s3": pp - 1.0 * range_hl,
            }
        elif pivot_type == "camarilla":
            range_hl = high - low
            result = {
                "pivot": (high + low + close) / 3.0,
                "r1": close + range_hl * 1.1 / 12.0,
                "r2": close + range_hl * 1.1 / 6.0,
                "r3": close + range_hl * 1.1 / 4.0,
                "r4": close + range_hl * 1.1 / 2.0,
                "s1": close - range_hl * 1.1 / 12.0,
                "s2": close - range_hl * 1.1 / 6.0,
                "s3": close - range_hl * 1.1 / 4.0,
                "s4": close - range_hl * 1.1 / 2.0,
            }
        elif pivot_type == "woodie":
            pp = (high + low + 2.0 * close) / 4.0
            result = {
                "pivot": pp,
                "r1": 2.0 * pp - low,
                "r2": pp + (high - low),
                "r3": high + 2.0 * (pp - low),
                "s1": 2.0 * pp - high,
                "s2": pp - (high - low),
                "s3": low - 2.0 * (high - pp),
            }
        
        return result

# ============================================================
#                    CANDLESTICK PATTERNS ENGINE
# ============================================================

class CandlestickPatterns:
    """موتور تشخیص الگوهای شمعی"""
    
    @staticmethod
    def detect_all_patterns(candles: List[OHLCV]) -> List[PatternResult]:
        """تشخیص تمام الگوهای شمعی"""
        patterns = []
        
        if len(candles) < 1:
            return patterns
        
        # Single candle patterns
        patterns.extend(CandlestickPatterns._detect_single_candle_patterns(candles))
        
        # Two candle patterns
        patterns.extend(CandlestickPatterns._detect_two_candle_patterns(candles))
        
        # Three candle patterns
        patterns.extend(CandlestickPatterns._detect_three_candle_patterns(candles))
        
        return sorted(patterns, key=lambda p: p.strength, reverse=True)
    
    @staticmethod
    def _detect_single_candle_patterns(candles: List[OHLCV]) -> List[PatternResult]:
        """تشخیص الگوهای تک کندلی"""
        patterns = []
        c = candles[-1]  # Latest candle
        
        # Doji
        if c.body_percentage < 5:
            if c.upper_wick_percentage > 60:
                patterns.append(PatternResult(
                    PatternType.DOJI_GRAVESTONE, "bearish", 60, 70, 1,
                    "Gravestone Doji — نشانه برگشت نزولی", 65
                ))
            elif c.lower_wick_percentage > 60:
                patterns.append(PatternResult(
                    PatternType.DOJI_DRAGONFLY, "bullish", 60, 70, 1,
                    "Dragonfly Doji — نشانه برگشت صعودی", 65
                ))
            else:
                patterns.append(PatternResult(
                    PatternType.DOJI, "continuation", 40, 60, 1,
                    "Doji — تردید در بازار", 50
                ))
        
        # Long-Legged Doji
        if c.body_percentage < 5 and c.upper_wick_percentage > 30 and c.lower_wick_percentage > 30:
            patterns.append(PatternResult(
                PatternType.LONG_LEGGED_DOJI, "continuation", 50, 60, 1,
                "Long-Legged Doji — تردید شدید", 55
            ))
        
        # Hammer
        if c.lower_wick_percentage > 60 and c.body_percentage < 30 and c.lower_wick > c.body * 2:
            patterns.append(PatternResult(
                PatternType.HAMMER, "bullish", 75, 80, 1,
                "Hammer — احتمال برگشت صعودی", 80
            ))
        
        # Hanging Man
        if c.lower_wick_percentage > 60 and c.body_percentage < 30 and c.range > 0:
            if candles[-2].close > c.close if len(candles) > 1 else True:
                patterns.append(PatternResult(
                    PatternType.HANGING_MAN, "bearish", 70, 75, 1,
                    "Hanging Man — هشدار برگشت نزولی", 75
                ))
        
        # Shooting Star
        if c.upper_wick_percentage > 60 and c.body_percentage < 30 and c.upper_wick > c.body * 2:
            patterns.append(PatternResult(
                PatternType.SHOOTING_STAR, "bearish", 75, 80, 1,
                "Shooting Star — احتمال برگشت نزولی", 80
            ))
        
        # Inverted Hammer
        if c.upper_wick_percentage > 60 and c.body_percentage < 30:
            if len(candles) > 1 and candles[-2].close > c.close:
                patterns.append(PatternResult(
                    PatternType.INVERTED_HAMMER, "bullish", 65, 70, 1,
                    "Inverted Hammer — احتمال برگشت صعودی", 70
                ))
        
        # Marubozu
        if c.body_percentage > 80 and c.upper_wick_percentage < 10 and c.lower_wick_percentage < 10:
            if c.is_bullish:
                patterns.append(PatternResult(
                    PatternType.MARUBOZU, "bullish", 80, 85, 1,
                    "Bullish Marubozu — قدرت خریداران", 85
                ))
            else:
                patterns.append(PatternResult(
                    PatternType.MARUBOZU, "bearish", 80, 85, 1,
                    "Bearish Marubozu — قدرت فروشندگان", 85
                ))
        
        # Spinning Top
        if c.body_percentage < 30 and c.upper_wick_percentage > 20 and c.lower_wick_percentage > 20:
            patterns.append(PatternResult(
                PatternType.SPINNING_TOP, "continuation", 30, 50, 1,
                "Spinning Top — عدم قطعیت", 45
            ))
        
        return patterns
    
    @staticmethod
    def _detect_two_candle_patterns(candles: List[OHLCV]) -> List[PatternResult]:
        """تشخیص الگوهای دو کندلی"""
        patterns = []
        
        if len(candles) < 2:
            return patterns
        
        c1 = candles[-2]  # Previous
        c2 = candles[-1]  # Current
        
        # Bullish Engulfing
        if c1.is_bearish and c2.is_bullish and c2.open <= c1.close and c2.close > c1.open:
            patterns.append(PatternResult(
                PatternType.BULLISH_ENGULFING, "bullish", 85, 90, 2,
                "Bullish Engulfing — سیگنال قوی صعودی", 90
            ))
        
        # Bearish Engulfing
        if c1.is_bullish and c2.is_bearish and c2.open >= c1.close and c2.close < c1.open:
            patterns.append(PatternResult(
                PatternType.BEARISH_ENGULFING, "bearish", 85, 90, 2,
                "Bearish Engulfing — سیگنال قوی نزولی", 90
            ))
        
        # Piercing Line
        if c1.is_bearish and c2.is_bullish:
            if c2.open <= c1.close and c2.close > (c1.open + c1.close) / 2 and c2.close < c1.open:
                patterns.append(PatternResult(
                    PatternType.PIERCING_LINE, "bullish", 75, 80, 2,
                    "Piercing Line — برگشت صعودی", 80
                ))
        
        # Dark Cloud Cover
        if c1.is_bullish and c2.is_bearish:
            if c2.open > c1.close and c2.close < (c1.open + c1.close) / 2:
                patterns.append(PatternResult(
                    PatternType.DARK_CLOUD_COVER, "bearish", 75, 80, 2,
                    "Dark Cloud Cover — برگشت نزولی", 80
                ))
        
        # Bullish Harami
        if c1.is_bearish and c2.is_bullish and c2.body < c1.body * 0.5 and c2.open > c1.close and c2.close < c1.open:
            patterns.append(PatternResult(
                PatternType.BULLISH_HARAMI, "bullish", 65, 75, 2,
                "Bullish Harami — احتمال برگشت صعودی", 70
            ))
        
        # Bearish Harami
        if c1.is_bullish and c2.is_bearish and c2.body < c1.body * 0.5 and c2.open < c1.close and c2.close > c1.open:
            patterns.append(PatternResult(
                PatternType.BEARISH_HARAMI, "bearish", 65, 75, 2,
                "Bearish Harami — احتمال برگشت نزولی", 70
            ))
        
        # Tweezer Bottom
        if abs(c1.low - c2.low) / max(c1.range, c2.range, 0.001) < 0.05:
            if c1.is_bearish and c2.is_bullish:
                patterns.append(PatternResult(
                    PatternType.TWEEZER_BOTTOM, "bullish", 70, 75, 2,
                    "Tweezer Bottom — حمایت قوی", 75
                ))
        
        # Tweezer Top
        if abs(c1.high - c2.high) / max(c1.range, c2.range, 0.001) < 0.05:
            if c1.is_bullish and c2.is_bearish:
                patterns.append(PatternResult(
                    PatternType.TWEEZER_TOP, "bearish", 70, 75, 2,
                    "Tweezer Top — مقاومت قوی", 75
                ))
        
        return patterns
    
    @staticmethod
    def _detect_three_candle_patterns(candles: List[OHLCV]) -> List[PatternResult]:
        """تشخیص الگوهای سه کندلی"""
        patterns = []
        
        if len(candles) < 3:
            return patterns
        
        c1 = candles[-3]
        c2 = candles[-2]
        c3 = candles[-1]
        
        # Morning Star
        if c1.is_bearish and c3.is_bullish:
            if c2.body < c1.body * 0.3 and c2.body < c3.body * 0.3:
                if c3.close > (c1.open + c1.close) / 2:
                    patterns.append(PatternResult(
                        PatternType.MORNING_STAR, "bullish", 90, 95, 3,
                        "Morning Star — سیگنال بسیار قوی صعودی", 92
                    ))
        
        # Evening Star
        if c1.is_bullish and c3.is_bearish:
            if c2.body < c1.body * 0.3 and c2.body < c3.body * 0.3:
                if c3.close < (c1.open + c1.close) / 2:
                    patterns.append(PatternResult(
                        PatternType.EVENING_STAR, "bearish", 90, 95, 3,
                        "Evening Star — سیگنال بسیار قوی نزولی", 92
                    ))
        
        # Three White Soldiers
        if all(c.is_bullish for c in [c1, c2, c3]):
            if all(c.close > c.open for c in [c1, c2, c3]):
                if c2.open < c1.close and c2.close > c1.close:
                    if c3.open < c2.close and c3.close > c2.close:
                        patterns.append(PatternResult(
                            PatternType.THREE_WHITE_SOLDIERS, "bullish", 85, 90, 3,
                            "Three White Soldiers — تداوم صعودی قوی", 88
                        ))
        
        # Three Black Crows
        if all(c.is_bearish for c in [c1, c2, c3]):
            if all(c.open > c.close for c in [c1, c2, c3]):
                if c2.open > c1.close and c2.close < c1.close:
                    if c3.open > c2.close and c3.close < c2.close:
                        patterns.append(PatternResult(
                            PatternType.THREE_BLACK_CROWS, "bearish", 85, 90, 3,
                            "Three Black Crows — تداوم نزولی قوی", 88
                        ))
        
        # Three Inside Up
        if c1.is_bearish and c2.is_bullish and c3.is_bullish:
            if c2.body < c1.body * 0.5 and c2.open > c1.close and c2.close < c1.open:
                if c3.close > c1.open:
                    patterns.append(PatternResult(
                        PatternType.THREE_INSIDE_UP, "bullish", 80, 85, 3,
                        "Three Inside Up — تایید برگشت صعودی", 83
                    ))
        
        # Three Inside Down
        if c1.is_bullish and c2.is_bearish and c3.is_bearish:
            if c2.body < c1.body * 0.5 and c2.open < c1.close and c2.close > c1.open:
                if c3.close < c1.open:
                    patterns.append(PatternResult(
                        PatternType.THREE_INSIDE_DOWN, "bearish", 80, 85, 3,
                        "Three Inside Down — تایید برگشت نزولی", 83
                    ))
        
        return patterns

# ============================================================
#                    FIBONACCI ENGINE
# ============================================================

class FibonacciEngine:
    """موتور محاسبات فیبوناچی"""
    
    @staticmethod
    def fibonacci_retracement(swing_low: float, swing_high: float) -> FibonacciResult:
        """محاسبه سطوح فیبوناچی Retracement"""
        is_uptrend = swing_high > swing_low
        diff = abs(swing_high - swing_low)
        
        result = FibonacciResult(
            swing_low=swing_low,
            swing_high=swing_high,
            is_uptrend=is_uptrend,
            current_position=0.5,  # Will be updated
        )
        
        retracement_levels = {
            "0.0": swing_high if is_uptrend else swing_low,
            "0.236": swing_high - 0.236 * diff if is_uptrend else swing_low + 0.236 * diff,
            "0.382": swing_high - 0.382 * diff if is_uptrend else swing_low + 0.382 * diff,
            "0.500": swing_high - 0.5 * diff if is_uptrend else swing_low + 0.5 * diff,
            "0.618": swing_high - 0.618 * diff if is_uptrend else swing_low + 0.618 * diff,
            "0.786": swing_high - 0.786 * diff if is_uptrend else swing_low + 0.786 * diff,
            "1.0": swing_low if is_uptrend else swing_high,
        }
        
        extension_levels = {
            "1.272": swing_high - 1.272 * diff if is_uptrend else swing_low + 1.272 * diff,
            "1.414": swing_high - 1.414 * diff if is_uptrend else swing_low + 1.414 * diff,
            "1.618": swing_high - 1.618 * diff if is_uptrend else swing_low + 1.618 * diff,
            "2.0": swing_high - 2.0 * diff if is_uptrend else swing_low + 2.0 * diff,
            "2.618": swing_high - 2.618 * diff if is_uptrend else swing_low + 2.618 * diff,
            "3.618": swing_high - 3.618 * diff if is_uptrend else swing_low + 3.618 * diff,
            "4.236": swing_high - 4.236 * diff if is_uptrend else swing_low + 4.236 * diff,
        }
        
        result.retracement_levels = retracement_levels
        result.extension_levels = extension_levels
        
        return result
    
    @staticmethod
    def find_swing_points(data: List[float], lookback: int = 5) -> Tuple[List[float], List[float]]:
        """پیدا کردن نقاط چرخش"""
        if len(data) < lookback * 2 + 1:
            return [], []
        
        swing_highs = []
        swing_lows = []
        
        for i in range(lookback, len(data) - lookback):
            # Swing High
            if data[i] == max(data[i - lookback:i + lookback + 1]):
                if len(swing_highs) == 0 or data[i] != swing_highs[-1]:
                    swing_highs.append(data[i])
            
            # Swing Low
            if data[i] == min(data[i - lookback:i + lookback + 1]):
                if len(swing_lows) == 0 or data[i] != swing_lows[-1]:
                    swing_lows.append(data[i])
        
        return swing_highs, swing_lows
    
    @staticmethod
    def fibonacci_time_zones(start_index: int, length: int) -> List[int]:
        """مناطق زمانی فیبوناچی"""
        fib_numbers = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        return [start_index + f * length for f in fib_numbers]
    
    @staticmethod
    def fibonacci_fan(start_price: float, end_price: float, start_idx: int, end_idx: int) -> Dict[str, List[Tuple[float, float]]]:
        """فن فیبوناچی"""
        diff = end_price - start_price
        x_diff = end_idx - start_idx
        
        levels = {
            "0.382": [],
            "0.500": [],
            "0.618": [],
        }
        
        for ratio_str, ratio in [("0.382", 0.382), ("0.500", 0.5), ("0.618", 0.618)]:
            for i in range(start_idx, end_idx + 1):
                t = (i - start_idx) / x_diff if x_diff > 0 else 0
                price = start_price + diff * t * ratio
                levels[ratio_str].append((i, price))
        
        return levels

# ============================================================
#                    WHALE TRACKING ENGINE
# ============================================================

class WhaleTracker:
    """موتور ردیابی نهنگ‌ها"""
    
    @staticmethod
    def detect_whale_activity(volume_data: List[Dict], threshold_multiplier: float = 3.0) -> List[WhaleActivityData]:
        """تشخیص فعالیت نهنگ‌ها"""
        if not volume_data:
            return []
        
        activities = []
        avg_volume = sum(v.get('volume', 0) for v in volume_data) / len(volume_data) if volume_data else 0
        
        for data in volume_data:
            vol = data.get('volume', 0)
            
            if vol > avg_volume * threshold_multiplier:
                # Large transaction detected
                activity_type = WhaleActivity.WHALE_BUY if data.get('is_buy', True) else WhaleActivity.WHALE_SELL
                
                activities.append(WhaleActivityData(
                    timestamp=data.get('timestamp', int(time.time())),
                    type=activity_type,
                    volume=vol,
                    price=data.get('price', 0),
                    value_usd=vol * data.get('price', 0),
                    exchange=data.get('exchange', 'unknown'),
                    wallet_count=data.get('wallet_count', 1),
                    avg_transaction=vol / max(data.get('transaction_count', 1), 1),
                ))
        
        return sorted(activities, key=lambda a: a.volume, reverse=True)
    
    @staticmethod
    def detect_accumulation_distribution(close: List[float], volume: List[float], period: int = 14) -> str:
        """تشخیص انباشت یا توزیع"""
        if len(close) < period:
            return "neutral"
        
        ad_values = [0.0]
        
        for i in range(1, len(close)):
            if close[i] == close[i - 1]:
                clv = 0
            elif close[i] > close[i - 1]:
                clv = ((close[i] - min(close[i], close[i - 1])) - 
                       (max(close[i], close[i - 1]) - close[i])) / (max(close[i], close[i - 1]) - min(close[i], close[i - 1]))
            else:
                clv = ((close[i] - min(close[i], close[i - 1])) - 
                       (max(close[i], close[i - 1]) - close[i])) / (max(close[i], close[i - 1]) - min(close[i], close[i - 1]))
            
            ad = ad_values[-1] + clv * volume[i]
            ad_values.append(ad)
        
        # Check recent trend
        recent = ad_values[-period:]
        if all(recent[i] > recent[i - 1] for i in range(1, len(recent))):
            return "accumulation"
        elif all(recent[i] < recent[i - 1] for i in range(1, len(recent))):
            return "distribution"
        
        return "neutral"
    
    @staticmethod
    def detect_smart_money(price_data: List[float], volume_data: List[float]) -> str:
        """تشخیص پول هوشمند"""
        if len(price_data) < 20:
            return "neutral"
        
        # Divergence between price and volume
        recent_price = price_data[-5:]
        recent_volume = volume_data[-5:]
        
        price_trend = "up" if recent_price[-1] > recent_price[0] else "down"
        volume_trend = "up" if sum(recent_volume) > sum(volume_data[-10:-5]) else "down"
        
        if price_trend == "down" and volume_trend == "up":
            return "smart_money_accumulating"
        elif price_trend == "up" and volume_trend == "down":
            return "smart_money_distributing"
        
        return "neutral"

# ============================================================
#                    PRICE ACTION ENGINE
# ============================================================

class PriceActionEngine:
    """موتور تحلیل پرایس اکشن"""
    
    @staticmethod
    def market_structure(high: List[float], low: List[float], close: List[float]) -> str:
        """تشخیص ساختار بازار"""
        if len(close) < 20:
            return "unknown"
        
        # Higher Highs and Higher Lows = Uptrend
        # Lower Highs and Lower Lows = Downtrend
        
        highs = high[-20:]
        lows = low[-20:]
        
        higher_highs = sum(1 for i in range(5, len(highs)) if highs[i] > max(highs[i-5:i]))
        lower_lows = sum(1 for i in range(5, len(lows)) if lows[i] < min(lows[i-5:i]))
        
        if higher_highs >= 3:
            return "bullish_structure"
        elif lower_lows >= 3:
            return "bearish_structure"
        
        return "sideways_structure"
    
    @staticmethod
    def detect_support_resistance(high: List[float], low: List[float], close: List[float], 
                                  lookback: int = 20, min_touches: int = 2) -> Tuple[List[Dict], List[Dict]]:
        """تشخیص سطوح حمایت و مقاومت"""
        supports = []
        resistances = []
        
        if len(close) < lookback:
            return supports, resistances
        
        # Find local minima for support
        for i in range(lookback, len(close) - lookback):
            if low[i] == min(low[i - lookback:i + lookback + 1]):
                # Check if this level has been touched multiple times
                touches = sum(1 for j in range(max(0, i - 50), i) if abs(low[j] - low[i]) / low[i] < 0.02)
                if touches >= min_touches:
                    supports.append({
                        "level": low[i],
                        "strength": min(touches * 25, 100),
                        "touches": touches,
                        "recent": True,
                    })
        
        # Find local maxima for resistance
        for i in range(lookback, len(close) - lookback):
            if high[i] == max(high[i - lookback:i + lookback + 1]):
                touches = sum(1 for j in range(max(0, i - 50), i) if abs(high[j] - high[i]) / high[i] < 0.02)
                if touches >= min_touches:
                    resistances.append({
                        "level": high[i],
                        "strength": min(touches * 25, 100),
                        "touches": touches,
                        "recent": True,
                    })
        
        # Sort by strength
        supports = sorted(supports, key=lambda s: s['strength'], reverse=True)[:5]
        resistances = sorted(resistances, key=lambda r: r['strength'], reverse=True)[:5]
        
        return supports, resistances
    
    @staticmethod
    def detect_breakout(high: List[float], low: List[float], close: List[float], 
                        level: float, direction: str = "resistance") -> bool:
        """تشخیص شکست"""
        if len(close) < 3:
            return False
        
        if direction == "resistance":
            # Price closes above resistance
            return close[-1] > level and close[-2] > level
        else:
            # Price closes below support
            return close[-1] < level and close[-2] < level
    
    @staticmethod
    def detect_divergence(price: List[float], indicator: List[float], 
                         lookback: int = 20) -> List[Dict]:
        """تشخیص واگرایی"""
        divergences = []
        
        if len(price) < lookback or len(indicator) < lookback:
            return divergences
        
        recent_price = price[-lookback:]
        recent_ind = indicator[-lookback:]
        
        # Bullish Divergence: Price makes lower low, Indicator makes higher low
        price_lows = []
        ind_lows = []
        
        for i in range(5, len(recent_price) - 5):
            if recent_price[i] == min(recent_price[i-5:i+6]):
                price_lows.append((i, recent_price[i]))
            if recent_ind[i] == min(recent_ind[i-5:i+6]):
                ind_lows.append((i, recent_ind[i]))
        
        if len(price_lows) >= 2 and len(ind_lows) >= 2:
            if price_lows[-1][1] < price_lows[-2][1] and ind_lows[-1][1] > ind_lows[-2][1]:
                divergences.append({
                    "type": "bullish_divergence",
                    "strength": "strong",
                    "description": "واگرایی صعودی — نشانه برگشت به سمت بالا"
                })
        
        # Bearish Divergence: Price makes higher high, Indicator makes lower high
        price_highs = []
        ind_highs = []
        
        for i in range(5, len(recent_price) - 5):
            if recent_price[i] == max(recent_price[i-5:i+6]):
                price_highs.append((i, recent_price[i]))
            if recent_ind[i] == max(recent_ind[i-5:i+6]):
                ind_highs.append((i, recent_ind[i]))
        
        if len(price_highs) >= 2 and len(ind_highs) >= 2:
            if price_highs[-1][1] > price_highs[-2][1] and ind_highs[-1][1] < ind_highs[-2][1]:
                divergences.append({
                    "type": "bearish_divergence",
                    "strength": "strong",
                    "description": "واگرایی نزولی — نشانه برگشت به سمت پایین"
                })
        
        return divergences
    
    @staticmethod
    def detect_order_blocks(high: List[float], low: List[float]) -> List[Dict]:
        """تشخیص Order Blocks"""
        if len(high) < 10:
            return []
        
        order_blocks = []
        
        # Look for large moves followed by consolidation
        for i in range(10, len(high)):
            range_i = high[i] - low[i]
            avg_range = sum(high[j] - low[j] for j in range(i-5, i)) / 5
            
            if range_i > avg_range * 2:
                order_blocks.append({
                    "index": i,
                    "type": "demand" if high[i] > high[i-1] else "supply",
                    "zone_high": high[i],
                    "zone_low": low[i],
                    "strength": round(range_i / avg_range, 1),
                })
        
        return order_blocks

# ============================================================
#                    FUNDAMENTAL ANALYSIS ENGINE
# ============================================================

class FundamentalAnalysis:
    """موتور تحلیل فاندامنتال"""
    
    @staticmethod
    def analyze_coin_fundamentals(coin: str, market_data: Dict = None) -> FundamentalAnalysisResult:
        """تحلیل فاندامنتال یک ارز"""
        result = FundamentalAnalysisResult(coin=coin)
        
        if market_data:
            result.market_cap = market_data.get('market_cap', 0)
            result.market_cap_rank = market_data.get('market_cap_rank', 0)
            result.total_supply = market_data.get('total_supply', 0)
            result.circulating_supply = market_data.get('circulating_supply', 0)
            result.max_supply = market_data.get('max_supply', 0)
            result.volume_24h = market_data.get('volume_24h', 0)
            result.price_change_1h = market_data.get('price_change_percentage_1h', 0)
            result.price_change_24h = market_data.get('price_change_percentage_24h', 0)
            result.price_change_7d = market_data.get('price_change_percentage_7d', 0)
            result.ath = market_data.get('ath', 0)
            result.ath_change = market_data.get('ath_change_percentage', 0)
        
        # Calculate ratios
        if result.volume_24h > 0 and result.market_cap > 0:
            result.volume_market_cap_ratio = (result.volume_24h / result.market_cap) * 100
        
        # Scoring
        score = 50.0
        
        # Market cap score
        if result.market_cap_rank <= 10:
            score += 20
            result.strengths.append("جزء ۱۰ ارز برتر بازار")
        elif result.market_cap_rank <= 50:
            score += 10
        
        # Volume score
        if result.volume_market_cap_ratio > 10:
            score += 10
            result.strengths.append("حجم معاملات بالا نسبت به ارزش بازار")
        
        # Supply score
        if result.max_supply > 0 and result.circulating_supply > 0:
            ratio = result.circulating_supply / result.max_supply
            if ratio > 0.9:
                score += 10
                result.strengths.append("عرضه در گردش نزدیک به حداکثر — کمبود عرضه")
        
        # Price performance
        if result.price_change_7d > 10:
            score += 5
            result.strengths.append("عملکرد قیمتی قوی در ۷ روز گذشته")
        elif result.price_change_7d < -10:
            score -= 5
            result.weaknesses.append("افت قیمتی شدید در ۷ روز گذشته")
        
        result.overall_score = min(max(score, 0), 100)
        
        # Recommendation
        if result.overall_score >= 70:
            result.recommendation = "strong_buy"
        elif result.overall_score >= 55:
            result.recommendation = "buy"
        elif result.overall_score >= 45:
            result.recommendation = "neutral"
        elif result.overall_score >= 30:
            result.recommendation = "sell"
        else:
            result.recommendation = "strong_sell"
        
        return result

# ============================================================
#                    MAIN ANALYSIS ENGINE
# ============================================================

class AnalysisEngine:
    """موتور اصلی تحلیل"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.patterns = CandlestickPatterns()
        self.fibonacci = FibonacciEngine()
        self.whale = WhaleTracker()
        self.price_action = PriceActionEngine()
        self.fundamental = FundamentalAnalysis()
        
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = 60
    
    def analyze(self, coin: str, timeframe: str = "4h", 
                ohlcv_data: List[Dict] = None) -> TechnicalAnalysisResult:
        """تحلیل کامل تکنیکال"""
        
        if ohlcv_data is None:
            ohlcv_data = self._fetch_ohlcv(coin, timeframe)
        
        candles = [OHLCV(
            timestamp=d.get('timestamp', 0),
            open=d.get('open', 0),
            high=d.get('high', 0),
            low=d.get('low', 0),
            close=d.get('close', 0),
            volume=d.get('volume', 0),
        ) for d in ohlcv_data]
        
        close = [c.close for c in candles]
        high = [c.high for c in candles]
        low = [c.low for c in candles]
        volume = [c.volume for c in candles]
        
        result = TechnicalAnalysisResult(
            coin=coin,
            timeframe=timeframe,
            timestamp=int(time.time()),
            current_price=close[-1] if close else 0,
            change_24h=((close[-1] - close[0]) / close[0] * 100) if close and close[0] != 0 else 0,
            high_24h=max(high[-96:]) if len(high) >= 96 else max(high) if high else 0,
            low_24h=min(low[-96:]) if len(low) >= 96 else min(low) if low else 0,
            volume_24h=sum(volume[-96:]) if len(volume) >= 96 else sum(volume),
        )
        
        if len(close) < 50:
            return result
        
        # ====== OSCILLATORS ======
        rsi_values = self.indicators.rsi(close)
        result.rsi = IndicatorResult(
            name="RSI", value=round(rsi_values[-1], 1),
            signal="oversold" if rsi_values[-1] < 30 else "overbought" if rsi_values[-1] > 70 else "neutral",
            strength=abs(rsi_values[-1] - 50) * 2,
        )
        
        k_values, d_values = self.indicators.stochastic(high, low, close)
        result.stochastic = IndicatorResult(
            name="Stochastic", value=round(k_values[-1], 1),
            signal="oversold" if k_values[-1] < 20 else "overbought" if k_values[-1] > 80 else "neutral",
        )
        
        cci_values = self.indicators.cci(high, low, close)
        result.cci = IndicatorResult(
            name="CCI", value=round(cci_values[-1], 1),
            signal="oversold" if cci_values[-1] < -100 else "overbought" if cci_values[-1] > 100 else "neutral",
        )
        
        wr_values = self.indicators.williams_r(high, low, close)
        result.williams_r = IndicatorResult(
            name="Williams %R", value=round(wr_values[-1], 1),
            signal="oversold" if wr_values[-1] < -80 else "overbought" if wr_values[-1] > -20 else "neutral",
        )
        
        mfi_values = self.indicators.mfi(high, low, close, volume)
        result.mfi = IndicatorResult(
            name="MFI", value=round(mfi_values[-1], 1),
            signal="oversold" if mfi_values[-1] < 20 else "overbought" if mfi_values[-1] > 80 else "neutral",
        )
        
        # ====== MOVING AVERAGES ======
        sma_20 = self.indicators.sma(close, 20)
        sma_50 = self.indicators.sma(close, 50)
        sma_200 = self.indicators.sma(close, 200)
        ema_12 = self.indicators.ema(close, 12)
        ema_26 = self.indicators.ema(close, 26)
        
        result.sma_signals = {
            "sma_20": "bullish" if close[-1] > sma_20[-1] else "bearish",
            "sma_50": "bullish" if close[-1] > sma_50[-1] else "bearish",
            "sma_200": "bullish" if close[-1] > sma_200[-1] else "bearish",
        }
        
        result.ema_signals = {
            "ema_12": "bullish" if close[-1] > ema_12[-1] else "bearish",
            "ema_26": "bullish" if close[-1] > ema_26[-1] else "bearish",
        }
        
        # Crossovers
        if sma_20[-1] > sma_50[-1] and sma_20[-2] <= sma_50[-2]:
            result.ma_crossovers.append("Golden Cross (SMA 20/50)")
        if sma_20[-1] < sma_50[-1] and sma_20[-2] >= sma_50[-2]:
            result.ma_crossovers.append("Death Cross (SMA 20/50)")
        
        # ====== MACD ======
        macd_line, signal_line, histogram = self.indicators.macd(close)
        result.macd = round(macd_line[-1], 4)
        result.macd_signal = round(signal_line[-1], 4)
        result.macd_histogram = round(histogram[-1], 4)
        
        if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
            result.macd_crossover = "bullish_cross"
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
            result.macd_crossover = "bearish_cross"
        
        # ====== BOLLINGER BANDS ======
        bb_upper, bb_middle, bb_lower = self.indicators.bollinger_bands(close)
        result.bb_upper = round(bb_upper[-1], 2)
        result.bb_middle = round(bb_middle[-1], 2)
        result.bb_lower = round(bb_lower[-1], 2)
        result.bb_position = round((close[-1] - bb_lower[-1]) / (bb_upper[-1] - bb_lower[-1]) * 100, 1) if (bb_upper[-1] - bb_lower[-1]) != 0 else 50
        
        # Squeeze detection
        bandwidth = self.indicators.bandwidth(bb_upper, bb_middle, bb_lower)
        if bandwidth[-1] < 0.05:
            result.bb_squeeze = True
        
        # ====== ICHIMOKU ======
        ichimoku = self.indicators.ichimoku(high, low, close)
        tenkan = ichimoku["tenkan_sen"][-1]
        kijun = ichimoku["kijun_sen"][-1]
        
        if tenkan > kijun:
            result.ichimoku_signal = "bullish"
        elif tenkan < kijun:
            result.ichimoku_signal = "bearish"
        else:
            result.ichimoku_signal = "neutral"
        
        # Cloud status
        senkou_a = ichimoku["senkou_span_a"][-1]
        senkou_b = ichimoku["senkou_span_b"][-1]
        if close[-1] > senkou_a and close[-1] > senkou_b:
            result.ichimoku_cloud_status = "above_cloud"
        elif close[-1] < senkou_a and close[-1] < senkou_b:
            result.ichimoku_cloud_status = "below_cloud"
        else:
            result.ichimoku_cloud_status = "inside_cloud"
        
        # ====== ADX ======
        adx, plus_di, minus_di = self.indicators.adx(high, low, close)
        result.adx = round(adx[-1], 1)
        result.plus_di = round(plus_di[-1], 1)
        result.minus_di = round(minus_di[-1], 1)
        
        if adx[-1] > 25:
            result.adx_trend_strength = "strong" if adx[-1] > 50 else "moderate"
        else:
            result.adx_trend_strength = "weak"
        
        # ====== ATR ======
        atr_values = self.indicators.atr(high, low, close)
        result.atr = round(atr_values[-1], 2)
        result.atr_percentage = round((atr_values[-1] / close[-1]) * 100, 2) if close[-1] != 0 else 0
        
        # ====== PARABOLIC SAR ======
        sar_values = self.indicators.parabolic_sar(high, low)
        result.sar = round(sar_values[-1], 2)
        result.sar_signal = "buy" if sar_values[-1] < close[-1] else "sell"
        
        # ====== VOLUME ======
        obv_values = self.indicators.obv(close, volume)
        if len(obv_values) > 20:
            obv_trend = "up" if obv_values[-1] > obv_values[-20] else "down"
            result.obv_trend = obv_trend
        
        avg_vol = sum(volume[-20:]) / 20 if len(volume) >= 20 else sum(volume) / max(len(volume), 1)
        result.volume_ratio = volume[-1] / avg_vol if avg_vol > 0 else 1.0
        result.volume_trend = "high" if result.volume_ratio > 1.5 else "low" if result.volume_ratio < 0.5 else "normal"
        
        # ====== CANDLESTICK PATTERNS ======
        result.candlestick_patterns = self.patterns.detect_all_patterns(candles)
        
        # ====== SUPPORT & RESISTANCE ======
        supports, resistances = self.price_action.detect_support_resistance(high, low, close)
        result.supports = supports[:5]
        result.resistances = resistances[:5]
        
        # ====== PIVOT POINTS ======
        pivots = self.indicators.pivot_points(
            max(high[-24:]) if len(high) >= 24 else high[-1],
            min(low[-24:]) if len(low) >= 24 else low[-1],
            close[-1]
        )
        result.pivot = pivots.get("pivot", 0)
        result.pivot_r1 = pivots.get("r1", 0)
        result.pivot_r2 = pivots.get("r2", 0)
        result.pivot_r3 = pivots.get("r3", 0)
        result.pivot_s1 = pivots.get("s1", 0)
        result.pivot_s2 = pivots.get("s2", 0)
        result.pivot_s3 = pivots.get("s3", 0)
        
        # ====== FIBONACCI ======
        if len(close) >= 50:
            swing_highs, swing_lows = self.fibonacci.find_swing_points(close)
            if swing_highs and swing_lows:
                swing_low = swing_lows[-1] if swing_lows else min(close[-50:])
                swing_high = swing_highs[-1] if swing_highs else max(close[-50:])
                result.fibonacci = self.fibonacci.fibonacci_retracement(swing_low, swing_high)
        
        # ====== DIVERGENCES ======
        result.divergences = self.price_action.detect_divergence(close, rsi_values)
        
        # ====== MARKET STRUCTURE ======
        result.market_structure = self.price_action.market_structure(high, low, close)
        
        # ====== TREND ======
        trend_signals = []
        if result.sma_signals.get('sma_20') == 'bullish':
            trend_signals.append(1)
        else:
            trend_signals.append(-1)
        if result.sma_signals.get('sma_50') == 'bullish':
            trend_signals.append(1)
        else:
            trend_signals.append(-1)
        if result.ichimoku_signal == 'bullish':
            trend_signals.append(1)
        elif result.ichimoku_signal == 'bearish':
            trend_signals.append(-1)
        if adx[-1] > 25 and plus_di[-1] > minus_di[-1]:
            trend_signals.append(1)
        elif adx[-1] > 25 and minus_di[-1] > plus_di[-1]:
            trend_signals.append(-1)
        
        trend_score = sum(trend_signals)
        if trend_score >= 3:
            result.trend = "strong_uptrend"
            result.trend_strength = 85
        elif trend_score >= 1:
            result.trend = "uptrend"
            result.trend_strength = 65
        elif trend_score >= -1:
            result.trend = "sideways"
            result.trend_strength = 35
        elif trend_score >= -3:
            result.trend = "downtrend"
            result.trend_strength = 65
        else:
            result.trend = "strong_downtrend"
            result.trend_strength = 85
        
        # ====== OVERALL SIGNAL ======
        signal_score = 0
        
        # RSI
        if rsi_values[-1] < 30:
            signal_score += 2
        elif rsi_values[-1] > 70:
            signal_score -= 2
        elif rsi_values[-1] < 50:
            signal_score += 1
        else:
            signal_score -= 1
        
        # MACD
        if result.macd_crossover == "bullish_cross":
            signal_score += 2
        elif result.macd_crossover == "bearish_cross":
            signal_score -= 2
        elif result.macd > result.macd_signal:
            signal_score += 1
        else:
            signal_score -= 1
        
        # Bollinger Bands
        if result.bb_position < 20:
            signal_score += 2
        elif result.bb_position > 80:
            signal_score -= 2
        
        # Stochastic
        if k_values[-1] < 20:
            signal_score += 1
        elif k_values[-1] > 80:
            signal_score -= 1
        
        # ADX
        if adx[-1] > 25 and plus_di[-1] > minus_di[-1]:
            signal_score += 1
        elif adx[-1] > 25 and minus_di[-1] > plus_di[-1]:
            signal_score -= 1
        
        # Ichimoku
        if result.ichimoku_cloud_status == "above_cloud":
            signal_score += 1
        elif result.ichimoku_cloud_status == "below_cloud":
            signal_score -= 1
        
        # Patterns
        bullish_patterns = [p for p in result.candlestick_patterns if p.type == "bullish"]
        bearish_patterns = [p for p in result.candlestick_patterns if p.type == "bearish"]
        
        if bullish_patterns:
            signal_score += len(bullish_patterns)
        if bearish_patterns:
            signal_score -= len(bearish_patterns)
        
        # Final signal
        if signal_score >= 6:
            result.overall_signal = "strong_buy"
            result.signal_strength = min(90, 60 + signal_score * 3)
        elif signal_score >= 3:
            result.overall_signal = "buy"
            result.signal_strength = min(70, 50 + signal_score * 3)
        elif signal_score >= -2:
            result.overall_signal = "neutral"
            result.signal_strength = 50
        elif signal_score >= -5:
            result.overall_signal = "sell"
            result.signal_strength = min(70, 50 + abs(signal_score) * 3)
        else:
            result.overall_signal = "strong_sell"
            result.signal_strength = min(90, 60 + abs(signal_score) * 3)
        
        # Confidence
        result.confidence = min(result.signal_strength + 10, 95)
        
        # Stop Loss & Take Profits
        result.stop_loss = round(result.atr * 2, 2) if result.atr > 0 else round(close[-1] * 0.03, 2)
        
        if result.overall_signal in ["buy", "strong_buy"]:
            result.take_profits = [
                round(close[-1] + result.atr * 1.5, 2),
                round(close[-1] + result.atr * 3.0, 2),
                round(close[-1] + result.atr * 5.0, 2),
            ]
        else:
            result.take_profits = [
                round(close[-1] - result.atr * 1.5, 2),
                round(close[-1] - result.atr * 3.0, 2),
                round(close[-1] - result.atr * 5.0, 2),
            ]
        
        # Risk/Reward
        tp = result.take_profits[0] if result.take_profits else close[-1]
        result.risk_reward = round(abs(tp - close[-1]) / max(result.stop_loss, 0.0001), 2)
        
        # Key levels
        result.key_levels = [
            result.pivot,
            result.pivot_r1, result.pivot_s1,
            result.bb_upper, result.bb_lower,
        ]
        
        # Summary
        result.summary = f"{coin} - {result.overall_signal.upper()} - Confidence: {result.confidence:.0f}%"
        result.recommendation = result.overall_signal
        
        return result
    
    def _fetch_ohlcv(self, coin: str, timeframe: str) -> List[Dict]:
        """دریافت داده‌های OHLCV"""
        if get_market:
            market = get_market()
            if market:
                return market.get_ohlcv(coin, timeframe)
        return []

    def clear_cache(self):
        """پاکسازی کش"""
        self._cache.clear()
        self._cache_time.clear()

# ============================================================
#                    SINGLETON
# ============================================================

_analysis_engine = None

def get_analysis_engine() -> AnalysisEngine:
    global _analysis_engine
    if _analysis_engine is None:
        _analysis_engine = AnalysisEngine()
    return _analysis_engine

# ============================================================
#                    COMPATIBILITY
# ============================================================

def start():
    return True

def analyze(coin: str, timeframe: str = "4h", data: List[Dict] = None) -> TechnicalAnalysisResult:
    """Quick analysis function"""
    engine = get_analysis_engine()
    return engine.analyze(coin, timeframe, data)

def analyze_fundamentals(coin: str, data: Dict = None) -> FundamentalAnalysisResult:
    """Quick fundamental analysis"""
    return FundamentalAnalysis.analyze_coin_fundamentals(coin, data)

def detect_patterns(candles: List[Dict]) -> List[PatternResult]:
    """Quick pattern detection"""
    ohlcv_list = [OHLCV(
        timestamp=c.get('timestamp', 0),
        open=c.get('open', 0),
        high=c.get('high', 0),
        low=c.get('low', 0),
        close=c.get('close', 0),
        volume=c.get('volume', 0),
    ) for c in candles]
    return CandlestickPatterns.detect_all_patterns(ohlcv_list)

def fibonacci_levels(swing_low: float, swing_high: float) -> FibonacciResult:
    """Quick Fibonacci calculation"""
    return FibonacciEngine.fibonacci_retracement(swing_low, swing_high)

def pivot_points(high: float, low: float, close: float, pivot_type: str = "standard") -> Dict[str, float]:
    """Quick pivot points calculation"""
    return TechnicalIndicators.pivot_points(high, low, close, pivot_type)

def support_resistance(data: List[float]) -> Tuple[List[Dict], List[Dict]]:
    """Quick S/R detection"""
    return PriceActionEngine.detect_support_resistance(data, data, data)
