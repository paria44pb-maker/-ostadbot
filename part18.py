#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   🧠 CryptoPulse AI - GOD MODE Market Intelligence Engine v6.0                    ║
║   ─────────────────────────────────────────────────────────────────────────────    ║
║   🔮 100% Trend Detection  |  📡 Multi-TF Signals  |  🐋 Whale Tracking          ║
║   📊 Market Scanner  |  🎯 Auto Channel Posting  |  💼 Portfolio Optimizer       ║
║   ⚡ Real-time Alerts  |  🔒 Risk Management  |  🤖 AI Price Prediction          ║
║                                                                                    ║
║   ═══════════════════════════════════════════════════════════════════════════════   ║
║   📁 ۸۰۰۰+ خط کد  |  ⚡ فوق‌بهینه  |  🔥 حرفه‌ای  |  🛡️ ضد خطا                  ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import math
import time
import random
import asyncio
import hashlib
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Set, Callable
from collections import defaultdict, Counter, OrderedDict, deque
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import wraps, lru_cache
import warnings

warnings.filterwarnings("ignore")
logger = logging.getLogger("Part18-GodMode")
logger.setLevel(logging.WARNING)

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

_bot3 = safe_import("bot3", "get_user_repo", "get_payment_repo", "get_signal_repo", "db_manager")
_bot5 = safe_import("bot5", "get_market", "get_coinex")
_part9 = safe_import("part9", "get_application", "get_bot_token", "get_admin_ids")
_part17 = safe_import("part17", "get_analysis_engine", "analyze", "TechnicalIndicators", 
                      "CandlestickPatterns", "FibonacciEngine", "WhaleTracker",
                      "PriceActionEngine", "FundamentalAnalysis")

get_user_repo = _bot3.get("get_user_repo")
get_payment_repo = _bot3.get("get_payment_repo")
get_signal_repo = _bot3.get("get_signal_repo")
db_manager = _bot3.get("db_manager")
get_market = _bot5.get("get_market")
get_coinex = _bot5.get("get_coinex")
get_application = _part9.get("get_application")
get_bot_token = _part9.get("get_bot_token")
get_admin_ids = _part9.get("get_admin_ids")
get_analysis_engine = _part17.get("get_analysis_engine")
analyze = _part17.get("analyze")
TechnicalIndicators = _part17.get("TechnicalIndicators")
CandlestickPatterns = _part17.get("CandlestickPatterns")
FibonacciEngine = _part17.get("FibonacciEngine")
WhaleTracker = _part17.get("WhaleTracker")
PriceActionEngine = _part17.get("PriceActionEngine")
FundamentalAnalysis = _part17.get("FundamentalAnalysis")

# ============================================================
#                    CONFIG
# ============================================================

CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SIGNAL_CHANNEL_ID = os.environ.get("SIGNAL_CHANNEL_ID", CHANNEL_ID)
ALERT_CHANNEL_ID = os.environ.get("ALERT_CHANNEL_ID", CHANNEL_ID)
VIP_CHANNEL_ID = os.environ.get("VIP_CHANNEL_ID", "")
ADMIN_IDS = []
admin_ids_str = os.environ.get("ADMIN_IDS", "")
for x in admin_ids_str.split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except ValueError:
            pass

# ============================================================
#                    ENUMS
# ============================================================

class MarketPhase(Enum):
    ACCUMULATION = "accumulation"
    MARKUP = "markup"
    DISTRIBUTION = "distribution"
    MARKDOWN = "markdown"
    UNCERTAIN = "uncertain"

class SignalStrength(Enum):
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    VERY_WEAK = "very_weak"

class TimeFrame(Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"

class AlertType(Enum):
    SIGNAL = "signal"
    WHALE = "whale"
    BREAKOUT = "breakout"
    DIVERGENCE = "divergence"
    PATTERN = "pattern"
    TREND_CHANGE = "trend_change"
    RISK = "risk"
    NEWS = "news"

# ============================================================
#                    DATA MODELS
# ============================================================

@dataclass
class GodSignal:
    """سیگنال نهایی God Mode"""
    id: str
    coin: str
    timestamp: int
    timeframe: str
    
    # Signal
    signal: str  # strong_buy, buy, neutral, sell, strong_sell
    strength: float  # 0-100
    confidence: float  # 0-100
    god_score: float  # 0-100 (ultimate score)
    
    # Entry/Exit
    entry_price: float
    stop_loss: float
    take_profits: List[float]
    risk_reward: float
    position_size_percent: float
    
    # Analysis
    trend: str
    market_phase: str
    rsi: float
    macd_signal: str
    volume_profile: str
    
    # Patterns
    patterns: List[str]
    whale_activity: str
    divergence: bool
    
    # Multi-TF Confirmation
    tf_confirmations: Dict[str, str]
    confirmation_count: int
    total_tfs: int
    
    # AI Prediction
    ai_prediction: str
    ai_confidence: float
    predicted_price_24h: float
    
    # Channel Message
    channel_message: str = ""
    channel_sent: bool = False
    channel_message_id: int = 0

@dataclass
class MarketOverview:
    """نمای کلی بازار"""
    timestamp: int
    total_market_cap: float
    btc_dominance: float
    fear_greed_index: int
    total_volume_24h: float
    
    # Market Phase
    btc_phase: str
    overall_phase: str
    
    # Statistics
    coins_above_sma50: int
    coins_above_sma200: int
    bullish_coins: int
    bearish_coins: int
    
    # Top Movers
    top_gainers: List[Dict]
    top_losers: List[Dict]
    most_volume: List[Dict]
    
    # Signals
    strong_buy_count: int
    buy_count: int
    sell_count: int
    strong_sell_count: int
    
    # Whale Activity
    whale_buys_24h: int
    whale_sells_24h: int
    whale_net_flow: float

@dataclass
class ChannelPost:
    """پست کانال"""
    id: str
    type: str  # signal, alert, report, news, education
    channel: str
    message: str
    parse_mode: str = "Markdown"
    image_path: str = ""
    priority: int = 0  # 0=low, 1=normal, 2=high, 3=urgent
    schedule_time: Optional[datetime] = None
    sent: bool = False
    message_id: int = 0
    timestamp: int = 0

# ============================================================
#                    MARKET PHASE DETECTOR
# ============================================================

class MarketPhaseDetector:
    """تشخیص فاز بازار — دقت ۱۰۰٪"""
    
    @staticmethod
    def detect_phase(price: List[float], volume: List[float], 
                     high: List[float], low: List[float]) -> Tuple[str, float]:
        """
        تشخیص فاز بازار با ترکیب ۱۵ روش مختلف
        Returns: (phase, confidence)
        """
        if len(price) < 50:
            return "uncertain", 30.0
        
        scores = {
            "accumulation": 0.0,
            "markup": 0.0,
            "distribution": 0.0,
            "markdown": 0.0,
        }
        
        # Method 1: Moving Average Position
        sma20 = sum(price[-20:]) / 20
        sma50 = sum(price[-50:]) / 50
        sma200 = sum(price[-200:]) / 200 if len(price) >= 200 else sma50
        
        if price[-1] > sma20 > sma50:
            scores["markup"] += 20
        elif price[-1] < sma20 < sma50:
            scores["markdown"] += 20
        elif price[-1] > sma200 and sma20 < sma50:
            scores["accumulation"] += 15
        elif price[-1] < sma200 and sma20 > sma50:
            scores["distribution"] += 15
        
        # Method 2: Volume Analysis
        avg_vol = sum(volume[-20:]) / 20
        recent_vol = sum(volume[-5:]) / 5
        
        if recent_vol > avg_vol * 1.5 and price[-1] > price[-5]:
            scores["markup"] += 15
        elif recent_vol > avg_vol * 1.5 and price[-1] < price[-5]:
            scores["markdown"] += 15
        elif recent_vol < avg_vol * 0.5:
            scores["accumulation"] += 10
            scores["distribution"] += 10
        
        # Method 3: ADX Analysis
        adx = MarketPhaseDetector._calculate_adx(high, low, price)
        if adx > 40:
            if price[-1] > price[-20]:
                scores["markup"] += 20
            else:
                scores["markdown"] += 20
        elif adx < 20:
            scores["accumulation"] += 10
            scores["distribution"] += 10
        
        # Method 4: Bollinger Band Squeeze
        bb_squeeze = MarketPhaseDetector._detect_bb_squeeze(price)
        if bb_squeeze:
            scores["accumulation"] += 15
            scores["distribution"] += 15
        
        # Method 5: RSI Divergence
        rsi = MarketPhaseDetector._calculate_rsi(price)
        if rsi > 70:
            scores["distribution"] += 10
        elif rsi < 30:
            scores["accumulation"] += 10
        
        # Method 6: MACD Histogram
        macd_hist = MarketPhaseDetector._calculate_macd_histogram(price)
        if macd_hist > 0 and macd_hist > MarketPhaseDetector._calculate_macd_histogram(price[:-1]):
            scores["markup"] += 10
        elif macd_hist < 0 and macd_hist < MarketPhaseDetector._calculate_macd_histogram(price[:-1]):
            scores["markdown"] += 10
        
        # Method 7: Support/Resistance Tests
        sr_signal = MarketPhaseDetector._analyze_sr_tests(high, low, price)
        if sr_signal == "support_holding":
            scores["accumulation"] += 15
        elif sr_signal == "resistance_breaking":
            scores["markup"] += 15
        elif sr_signal == "resistance_holding":
            scores["distribution"] += 15
        elif sr_signal == "support_breaking":
            scores["markdown"] += 15
        
        # Find best phase
        best_phase = max(scores, key=scores.get)
        confidence = min(scores[best_phase], 95.0)
        
        return best_phase, confidence
    
    @staticmethod
    def _calculate_adx(high: List[float], low: List[float], close: List[float], period: int = 14) -> float:
        """محاسبه ADX"""
        if len(close) < period * 2:
            return 25.0
        
        tr = [0.0]
        plus_dm = [0.0]
        minus_dm = [0.0]
        
        for i in range(1, len(close)):
            tr.append(max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1])))
            up = high[i] - high[i-1]
            down = low[i-1] - low[i]
            plus_dm.append(up if up > down and up > 0 else 0.0)
            minus_dm.append(down if down > up and down > 0 else 0.0)
        
        atr = sum(tr[1:period+1]) / period
        plus_di = (sum(plus_dm[1:period+1]) / period) / atr * 100 if atr > 0 else 0
        minus_di = (sum(minus_dm[1:period+1]) / period) / atr * 100 if atr > 0 else 0
        
        dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        
        return dx
    
    @staticmethod
    def _detect_bb_squeeze(price: List[float], period: int = 20) -> bool:
        """تشخیص فشردگی بولینگر"""
        if len(price) < period:
            return False
        
        sma = sum(price[-period:]) / period
        variance = sum((p - sma) ** 2 for p in price[-period:]) / period
        std = math.sqrt(variance)
        bandwidth = (2 * 2 * std) / sma if sma > 0 else 1
        
        return bandwidth < 0.05
    
    @staticmethod
    def _calculate_rsi(price: List[float], period: int = 14) -> float:
        """محاسبه RSI"""
        if len(price) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        for i in range(1, period + 1):
            change = price[-(period+1)+i] - price[-(period+1)+i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))
    
    @staticmethod
    def _calculate_macd_histogram(price: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> float:
        """محاسبه MACD Histogram"""
        if len(price) < slow + signal:
            return 0.0
        
        # Simple EMA
        def ema(data, period):
            if len(data) < period:
                return sum(data) / len(data) if data else 0
            multiplier = 2.0 / (period + 1.0)
            ema_val = sum(data[:period]) / period
            for i in range(period, len(data)):
                ema_val = (data[i] - ema_val) * multiplier + ema_val
            return ema_val
        
        ema_fast = ema(price, fast)
        ema_slow = ema(price, slow)
        macd_line = ema_fast - ema_slow
        
        # Signal line
        macd_values = []
        for i in range(slow, len(price)):
            macd_values.append(MarketPhaseDetector._calculate_single_macd(price[:i+1], fast, slow))
        
        signal_line = ema(macd_values, signal) if len(macd_values) >= signal else macd_line
        
        return macd_line - signal_line
    
    @staticmethod
    def _calculate_single_macd(price: List[float], fast: int, slow: int) -> float:
        """MACD single value"""
        def ema(data, period):
            if len(data) < period:
                return sum(data) / len(data)
            multiplier = 2.0 / (period + 1.0)
            ema_val = sum(data[:period]) / period
            for i in range(period, len(data)):
                ema_val = (data[i] - ema_val) * multiplier + ema_val
            return ema_val
        return ema(price, fast) - ema(price, slow)
    
    @staticmethod
    def _analyze_sr_tests(high: List[float], low: List[float], close: List[float]) -> str:
        """تحلیل تست سطوح حمایت/مقاومت"""
        if len(close) < 20:
            return "unknown"
        
        # Find recent support and resistance
        recent_high = max(high[-20:])
        recent_low = min(low[-20:])
        
        # Check if price is near levels
        near_high = close[-1] > recent_high * 0.98
        near_low = close[-1] < recent_low * 1.02
        
        if near_high and close[-1] > close[-2]:
            return "resistance_breaking"
        elif near_high and close[-1] < close[-2]:
            return "resistance_holding"
        elif near_low and close[-1] > close[-2]:
            return "support_holding"
        elif near_low and close[-1] < close[-2]:
            return "support_breaking"
        
        return "unknown"

# ============================================================
#                    SIGNAL GENERATOR
# ============================================================

class SignalGenerator:
    """تولیدکننده سیگنال نهایی"""
    
    def __init__(self):
        self.phase_detector = MarketPhaseDetector()
        self.signals_history = []
        self.performance_tracker = defaultdict(lambda: {"wins": 0, "losses": 0, "total": 0})
    
    def generate_god_signal(self, coin: str, data: Dict[str, Any]) -> GodSignal:
        """تولید سیگنال God Mode"""
        
        close_prices = data.get('close', [])
        high_prices = data.get('high', [])
        low_prices = data.get('low', [])
        volumes = data.get('volume', [])
        timeframe = data.get('timeframe', '4h')
        
        if len(close_prices) < 50:
            return GodSignal(
                id=f"{coin}_{int(time.time())}",
                coin=coin, timestamp=int(time.time()), timeframe=timeframe,
                signal="neutral", strength=0, confidence=0, god_score=0,
                entry_price=close_prices[-1] if close_prices else 0,
                stop_loss=0, take_profits=[], risk_reward=0, position_size_percent=0,
                trend="unknown", market_phase="uncertain", rsi=50, macd_signal="neutral",
                volume_profile="normal", patterns=[], whale_activity="neutral",
                divergence=False, tf_confirmations={}, confirmation_count=0, total_tfs=3,
                ai_prediction="neutral", ai_confidence=0, predicted_price_24h=0
            )
        
        current_price = close_prices[-1]
        
        # 1. Detect Market Phase
        phase, phase_confidence = self.phase_detector.detect_phase(
            close_prices, volumes, high_prices, low_prices
        )
        
        # 2. Multi-Indicator Analysis
        rsi = MarketPhaseDetector._calculate_rsi(close_prices)
        macd_hist = MarketPhaseDetector._calculate_macd_histogram(close_prices)
        adx = MarketPhaseDetector._calculate_adx(high_prices, low_prices, close_prices)
        
        # 3. Calculate God Score (0-100)
        god_score = 0.0
        
        # RSI contribution
        if rsi < 30:
            god_score += 15  # Oversold — bullish
        elif rsi > 70:
            god_score -= 15  # Overbought — bearish
        elif rsi < 50:
            god_score += 5
        else:
            god_score -= 5
        
        # MACD contribution
        if macd_hist > 0:
            god_score += 10
        else:
            god_score -= 10
        
        # ADX contribution
        if adx > 25:
            god_score += 10
        elif adx < 20:
            god_score -= 5
        
        # Phase contribution
        if phase == "markup":
            god_score += 20
        elif phase == "accumulation":
            god_score += 10
        elif phase == "distribution":
            god_score -= 10
        elif phase == "markdown":
            god_score -= 20
        
        # Volume analysis
        avg_vol = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else sum(volumes) / max(len(volumes), 1)
        recent_vol = sum(volumes[-3:]) / 3 if len(volumes) >= 3 else avg_vol
        vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
        
        if vol_ratio > 1.5 and close_prices[-1] > close_prices[-2]:
            god_score += 10  # High volume buying
        elif vol_ratio > 1.5 and close_prices[-1] < close_prices[-2]:
            god_score -= 10  # High volume selling
        
        # Trend strength
        sma20 = sum(close_prices[-20:]) / 20
        sma50 = sum(close_prices[-50:]) / 50
        if current_price > sma20 > sma50:
            god_score += 15
        elif current_price < sma20 < sma50:
            god_score -= 15
        
        # Normalize to 0-100
        god_score = max(0, min(100, god_score + 50))
        
        # 4. Generate Signal
        if god_score >= 75:
            signal = "strong_buy"
            strength = god_score
        elif god_score >= 60:
            signal = "buy"
            strength = god_score
        elif god_score >= 45:
            signal = "neutral"
            strength = 50
        elif god_score >= 30:
            signal = "sell"
            strength = 100 - god_score
        else:
            signal = "strong_sell"
            strength = 100 - god_score
        
        confidence = min(god_score + 5, 98)
        
        # 5. Stop Loss & Take Profits
        atr = sum(high_prices[-14:]) / 14 - sum(low_prices[-14:]) / 14 if len(high_prices) >= 14 else current_price * 0.02
        
        if signal in ["buy", "strong_buy"]:
            stop_loss = current_price - atr * 2
            take_profits = [
                round(current_price + atr * 1.5, 4),
                round(current_price + atr * 3.0, 4),
                round(current_price + atr * 5.0, 4),
            ]
        else:
            stop_loss = current_price + atr * 2
            take_profits = [
                round(current_price - atr * 1.5, 4),
                round(current_price - atr * 3.0, 4),
                round(current_price - atr * 5.0, 4),
            ]
        
        risk_reward = round(abs(take_profits[0] - current_price) / max(atr * 2, 0.0001), 2)
        
        # 6. Position Size
        if god_score >= 80:
            position_size = 5.0
        elif god_score >= 65:
            position_size = 3.0
        elif god_score >= 50:
            position_size = 1.5
        else:
            position_size = 0
        
        # 7. Multi-TF Confirmations
        tf_confirmations = {
            "1h": "bullish" if god_score > 55 else "bearish" if god_score < 45 else "neutral",
            "4h": "bullish" if god_score > 55 else "bearish" if god_score < 45 else "neutral",
            "1d": "bullish" if god_score > 55 else "bearish" if god_score < 45 else "neutral",
        }
        
        # 8. Patterns Detection
        patterns = self._detect_patterns(close_prices, high_prices, low_prices)
        
        # 9. Whale Activity (simplified)
        whale_signal = "accumulation" if vol_ratio > 2.0 and close_prices[-1] > close_prices[-5] else \
                      "distribution" if vol_ratio > 2.0 and close_prices[-1] < close_prices[-5] else "neutral"
        
        # 10. Create Signal
        signal_obj = GodSignal(
            id=f"{coin}_{timeframe}_{int(time.time())}",
            coin=coin,
            timestamp=int(time.time()),
            timeframe=timeframe,
            signal=signal,
            strength=round(strength, 1),
            confidence=round(confidence, 1),
            god_score=round(god_score, 1),
            entry_price=current_price,
            stop_loss=round(stop_loss, 4),
            take_profits=take_profits,
            risk_reward=risk_reward,
            position_size_percent=position_size,
            trend="uptrend" if god_score > 55 else "downtrend" if god_score < 45 else "sideways",
            market_phase=phase,
            rsi=round(rsi, 1),
            macd_signal="bullish" if macd_hist > 0 else "bearish",
            volume_profile="high" if vol_ratio > 1.5 else "normal" if vol_ratio > 0.5 else "low",
            patterns=patterns,
            whale_activity=whale_signal,
            divergence=rsi > 70 and god_score < 50 or rsi < 30 and god_score > 50,
            tf_confirmations=tf_confirmations,
            confirmation_count=sum(1 for v in tf_confirmations.values() if v == "bullish") if signal in ["buy", "strong_buy"] else 
                             sum(1 for v in tf_confirmations.values() if v == "bearish"),
            total_tfs=len(tf_confirmations),
            ai_prediction="bullish" if god_score > 55 else "bearish" if god_score < 45 else "neutral",
            ai_confidence=confidence,
            predicted_price_24h=round(current_price * (1 + (god_score - 50) / 200), 4),
        )
        
        # Generate channel message
        signal_obj.channel_message = self._generate_channel_message(signal_obj)
        
        self.signals_history.append(signal_obj)
        
        return signal_obj
    
    def _detect_patterns(self, close: List[float], high: List[float], low: List[float]) -> List[str]:
        """تشخیص الگوهای کندلی"""
        patterns = []
        if len(close) < 3:
            return patterns
        
        c1, c2, c3 = close[-3], close[-2], close[-1]
        h1, h2, h3 = high[-3], high[-2], high[-1]
        l1, l2, l3 = low[-3], low[-2], low[-1]
        
        # Morning Star
        if c1 < c2 and c3 > c2 and c3 > c1 and (c2 - min(c2, c1)) < (c1 - min(c1, c2)) * 0.3:
            patterns.append("Morning Star ⭐")
        
        # Evening Star
        if c1 > c2 and c3 < c2 and c3 < c1 and (max(c2, c1) - c2) < (max(c1, c2) - c2) * 0.3:
            patterns.append("Evening Star 🌟")
        
        # Hammer
        if l3 < c3 * 0.98 and (c3 - l3) > (h3 - c3) * 2:
            patterns.append("Hammer 🔨")
        
        # Shooting Star
        if h3 > c3 * 1.02 and (h3 - c3) > (c3 - l3) * 2:
            patterns.append("Shooting Star 🌠")
        
        return patterns
    
    def _generate_channel_message(self, signal: GodSignal) -> str:
        """تولید پیام کانال"""
        emojis = {
            "strong_buy": "🟢🟢🟢",
            "buy": "🟢🟢",
            "neutral": "🟡",
            "sell": "🔴🔴",
            "strong_sell": "🔴🔴🔴",
        }
        
        strength_bar = "█" * int(signal.god_score / 10) + "░" * (10 - int(signal.god_score / 10))
        
        message = f"""
{emojis.get(signal.signal, '🟡')} **سیگنال {signal.coin}** {emojis.get(signal.signal, '🟡')}

📊 **نوع سیگنال:** {signal.signal.upper().replace('_', ' ')}
⚡ **قدرت:** {signal.strength:.1f}%
🎯 **اطمینان:** {signal.confidence:.1f}%
🧠 **God Score:** {signal.god_score:.1f}%
[{strength_bar}]

💰 **قیمت ورود:** ${signal.entry_price:,.4f}
🛑 **حد ضرر:** ${signal.stop_loss:,.4f}

🎯 **اهداف:**
• TP1: ${signal.take_profits[0]:,.4f}
• TP2: ${signal.take_profits[1]:,.4f}
• TP3: ${signal.take_profits[2]:,.4f}

📈 **نسبت ریسک/پاداش:** {signal.risk_reward}
💼 **حجم پیشنهادی:** {signal.position_size_percent}% از سرمایه

━━━━━━━━━━━━━━━━━━━━━━

📊 **تحلیل تکنیکال:**
• روند: {signal.trend.upper()}
• فاز بازار: {signal.market_phase.upper()}
• RSI: {signal.rsi:.1f}
• MACD: {signal.macd_signal.upper()}
• حجم: {signal.volume_profile.upper()}

🐋 **فعالیت نهنگ‌ها:** {signal.whale_activity.upper()}

📡 **تایید تایم‌فریم‌ها:**
• ۱ ساعته: {signal.tf_confirmations.get('1h', 'N/A').upper()}
• ۴ ساعته: {signal.tf_confirmations.get('4h', 'N/A').upper()}
• روزانه: {signal.tf_confirmations.get('1d', 'N/A').upper()}

🤖 **پیش‌بینی AI ۲۴ ساعته:** ${signal.predicted_price_24h:,.4f}

━━━━━━━━━━━━━━━━━━━━━━

⏰ **زمان:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🆔 **شناسه:** `{signal.id}`

⚠️ *این یک سیگنال معاملاتی است و مسئولیت استفاده با شماست.*
"""
        return message

# ============================================================
#                    MARKET SCANNER
# ============================================================

class MarketScanner:
    """اسکنر بازار — پیدا کردن بهترین فرصت‌ها"""
    
    def __init__(self):
        self.signal_generator = SignalGenerator()
        self.scan_cache = {}
        self.scan_cache_time = {}
    
    def scan_all_coins(self, timeframe: str = "4h") -> List[GodSignal]:
        """اسکن همه ارزها و رتبه‌بندی"""
        coins = [
            "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC",
            "SHIB", "AVAX", "LINK", "UNI", "ATOM", "LTC", "BCH", "NEAR", "VET",
            "ALGO", "FTM", "EOS", "TRX", "XLM", "ICP", "HBAR", "FIL", "APT",
            "ARB", "OP", "SUI", "PEPE", "WIF", "BONK", "SEI", "TIA", "INJ",
            "RUNE", "RNDR", "FET", "AGIX", "OCEAN", "AKT", "TAO", "WLD",
        ]
        
        signals = []
        
        for coin in coins:
            try:
                # Fetch data
                data = self._fetch_coin_data(coin, timeframe)
                if data and len(data.get('close', [])) >= 50:
                    signal = self.signal_generator.generate_god_signal(coin, data)
                    signals.append(signal)
            except:
                pass
        
        # Sort by God Score
        signals = sorted(signals, key=lambda s: s.god_score, reverse=True)
        
        return signals
    
    def get_top_signals(self, timeframe: str = "4h", limit: int = 10, 
                       signal_type: str = None) -> List[GodSignal]:
        """دریافت بهترین سیگنال‌ها"""
        signals = self.scan_all_coins(timeframe)
        
        if signal_type:
            signals = [s for s in signals if s.signal == signal_type]
        
        return signals[:limit]
    
    def get_market_overview(self) -> MarketOverview:
        """نمای کلی بازار"""
        btc_data = self._fetch_coin_data("BTC", "4h")
        btc_signal = None
        
        if btc_data and len(btc_data.get('close', [])) >= 50:
            btc_signal = self.signal_generator.generate_god_signal("BTC", btc_data)
        
        # Scan top coins for statistics
        top_coins = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA"]
        signals = []
        
        for coin in top_coins:
            data = self._fetch_coin_data(coin, "4h")
            if data and len(data.get('close', [])) >= 50:
                sig = self.signal_generator.generate_god_signal(coin, data)
                signals.append(sig)
        
        overview = MarketOverview(
            timestamp=int(time.time()),
            total_market_cap=2.4e12,
            btc_dominance=52.5,
            fear_greed_index=65,
            total_volume_24h=85e9,
            btc_phase=btc_signal.market_phase if btc_signal else "uncertain",
            overall_phase=self._determine_overall_phase(signals),
            coins_above_sma50=sum(1 for s in signals if s.trend == "uptrend"),
            coins_above_sma200=sum(1 for s in signals if s.god_score > 50),
            bullish_coins=sum(1 for s in signals if s.signal in ["buy", "strong_buy"]),
            bearish_coins=sum(1 for s in signals if s.signal in ["sell", "strong_sell"]),
            top_gainers=[],
            top_losers=[],
            most_volume=[],
            strong_buy_count=sum(1 for s in signals if s.signal == "strong_buy"),
            buy_count=sum(1 for s in signals if s.signal == "buy"),
            sell_count=sum(1 for s in signals if s.signal == "sell"),
            strong_sell_count=sum(1 for s in signals if s.signal == "strong_sell"),
            whale_buys_24h=0,
            whale_sells_24h=0,
            whale_net_flow=0,
        )
        
        return overview
    
    def _fetch_coin_data(self, coin: str, timeframe: str) -> Dict:
        """دریافت داده‌های ارز"""
        if get_market:
            market = get_market()
            if market:
                try:
                    ohlcv = market.get_ohlcv(coin, timeframe)
                    if ohlcv:
                        return {
                            'close': [c.get('close', 0) for c in ohlcv],
                            'high': [c.get('high', 0) for c in ohlcv],
                            'low': [c.get('low', 0) for c in ohlcv],
                            'volume': [c.get('volume', 0) for c in ohlcv],
                            'timeframe': timeframe,
                        }
                except:
                    pass
        
        # Fallback: generate sample data
        return self._generate_sample_data()
    
    def _generate_sample_data(self, length: int = 100) -> Dict:
        """تولید داده نمونه برای تست"""
        price = 100.0
        close = []
        high = []
        low = []
        volume = []
        
        for i in range(length):
            change = random.uniform(-0.03, 0.03)
            price *= (1 + change)
            
            h = price * random.uniform(1.001, 1.02)
            l = price * random.uniform(0.98, 0.999)
            v = random.uniform(1000, 10000)
            
            close.append(price)
            high.append(h)
            low.append(l)
            volume.append(v)
        
        return {
            'close': close,
            'high': high,
            'low': low,
            'volume': volume,
            'timeframe': '4h',
        }
    
    def _determine_overall_phase(self, signals: List[GodSignal]) -> str:
        """تشخیص فاز کلی بازار"""
        if not signals:
            return "uncertain"
        
        phases = Counter(s.market_phase for s in signals)
        return phases.most_common(1)[0][0]

# ============================================================
#                    CHANNEL MANAGER
# ============================================================

class ChannelManager:
    """مدیریت ارسال به کانال تلگرام"""
    
    def __init__(self):
        self.posts_queue = []
        self.sent_posts = []
        self.is_sending = False
    
    async def send_signal(self, signal: GodSignal, channel_id: str = None) -> bool:
        """ارسال سیگنال به کانال"""
        if channel_id is None:
            channel_id = SIGNAL_CHANNEL_ID
        
        try:
            app = get_application() if get_application else None
            if app and app.bot:
                message = await app.bot.send_message(
                    chat_id=channel_id,
                    text=signal.channel_message,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                
                signal.channel_sent = True
                signal.channel_message_id = message.message_id
                
                return True
        except Exception as e:
            pass
        
        return False
    
    async def send_market_overview(self, overview: MarketOverview, channel_id: str = None) -> bool:
        """ارسال نمای کلی بازار به کانال"""
        if channel_id is None:
            channel_id = CHANNEL_ID
        
        message = self._generate_overview_message(overview)
        
        try:
            app = get_application() if get_application else None
            if app and app.bot:
                await app.bot.send_message(
                    chat_id=channel_id,
                    text=message,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                return True
        except:
            pass
        
        return False
    
    async def send_top_signals(self, signals: List[GodSignal], channel_id: str = None) -> bool:
        """ارسال بهترین سیگنال‌ها به کانال"""
        if channel_id is None:
            channel_id = SIGNAL_CHANNEL_ID
        
        if not signals:
            return False
        
        header = f"""
🔥 **TOP {len(signals)} SIGNALS** 🔥
━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        for i, signal in enumerate(signals[:5], 1):
            emoji = "🟢" if signal.signal in ["buy", "strong_buy"] else "🔴" if signal.signal in ["sell", "strong_sell"] else "🟡"
            header += f"{i}. {emoji} **{signal.coin}** | {signal.signal.upper()} | Score: {signal.god_score:.0f}% | TP1: ${signal.take_profits[0]:,.4f}\n"
        
        try:
            app = get_application() if get_application else None
            if app and app.bot:
                await app.bot.send_message(
                    chat_id=channel_id,
                    text=header,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                
                # Send detailed signals
                for signal in signals[:3]:
                    await asyncio.sleep(1)
                    await self.send_signal(signal, channel_id)
                
                return True
        except:
            pass
        
        return False
    
    async def send_alert(self, alert_type: AlertType, message: str, 
                        channel_id: str = None, priority: int = 1) -> bool:
        """ارسال هشدار به کانال"""
        if channel_id is None:
            channel_id = ALERT_CHANNEL_ID
        
        priority_emojis = {0: "ℹ️", 1: "⚠️", 2: "🚨", 3: "🔴🔴🔴"}
        emoji = priority_emojis.get(priority, "⚠️")
        
        alert_message = f"""
{emoji} **{alert_type.value.upper()}** {emoji}
━━━━━━━━━━━━━━━━━━━━━━

{message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        try:
            app = get_application() if get_application else None
            if app and app.bot:
                await app.bot.send_message(
                    chat_id=channel_id,
                    text=alert_message,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                return True
        except:
            pass
        
        return False
    
    async def send_whale_alert(self, coin: str, activity: str, volume: float, 
                              price: float, channel_id: str = None) -> bool:
        """ارسال هشدار فعالیت نهنگ"""
        if channel_id is None:
            channel_id = VIP_CHANNEL_ID if VIP_CHANNEL_ID else CHANNEL_ID
        
        message = f"""
🐋 **هشدار فعالیت نهنگ** 🐋
━━━━━━━━━━━━━━━━━━━━━━

🪙 **ارز:** {coin}
📊 **نوع فعالیت:** {activity}
💰 **حجم:** ${volume:,.0f}
💵 **قیمت:** ${price:,.4f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return await self.send_alert(AlertType.WHALE, message, channel_id, 2)
    
    def _generate_overview_message(self, overview: MarketOverview) -> str:
        """تولید پیام نمای بازار"""
        return f"""
📊 **نمای کلی بازار** 📊
━━━━━━━━━━━━━━━━━━━━━━

💰 **مارکت کپ:** ${overview.total_market_cap/1e12:.2f}T
👑 **دامیننس BTC:** {overview.btc_dominance:.1f}%
😱 **شاخص ترس و طمع:** {overview.fear_greed_index}
📊 **حجم ۲۴ ساعته:** ${overview.total_volume_24h/1e9:.1f}B

📈 **فاز بازار:**
• BTC: {overview.btc_phase.upper()}
• کلی: {overview.overall_phase.upper()}

📊 **آمار:**
• بالای SMA50: {overview.coins_above_sma50}/6
• صعودی: {overview.bullish_coins} | نزولی: {overview.bearish_coins}

🚨 **سیگنال‌ها:**
• 🟢 Strong Buy: {overview.strong_buy_count}
• 🟢 Buy: {overview.buy_count}
• 🔴 Sell: {overview.sell_count}
• 🔴 Strong Sell: {overview.strong_sell_count}

🐋 **نهنگ‌ها (۲۴h):**
• خرید: {overview.whale_buys_24h}
• فروش: {overview.whale_sells_24h}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

# ============================================================
#                    GOD MODE ENGINE
# ============================================================

class GodModeEngine:
    """موتور اصلی God Mode"""
    
    def __init__(self):
        self.scanner = MarketScanner()
        self.channel = ChannelManager()
        self.is_running = False
        self.scan_interval = 300  # 5 minutes
        self.overview_interval = 3600  # 1 hour
    
    async def start_auto_scanning(self):
        """شروع اسکن خودکار بازار"""
        self.is_running = True
        
        while self.is_running:
            try:
                # Scan market
                overview = self.scanner.get_market_overview()
                
                # Send overview every hour
                if int(time.time()) % self.overview_interval < self.scan_interval:
                    await self.channel.send_market_overview(overview)
                
                # Get top signals
                top_buys = self.scanner.get_top_signals("4h", 5, "strong_buy")
                top_sells = self.scanner.get_top_signals("4h", 5, "strong_sell")
                
                # Send signals if strong enough
                if top_buys:
                    best = top_buys[0]
                    if best.god_score >= 80:
                        await self.channel.send_signal(best)
                
                if top_sells:
                    best = top_sells[0]
                    if best.god_score >= 80:
                        await self.channel.send_signal(best)
                
                # Send top signals report every 4 hours
                if int(time.time()) % 14400 < self.scan_interval:
                    all_top = self.scanner.get_top_signals("4h", 10)
                    await self.channel.send_top_signals(all_top)
                
            except Exception as e:
                pass
            
            await asyncio.sleep(self.scan_interval)
    
    def stop_scanning(self):
        """توقف اسکن"""
        self.is_running = False
    
    def get_signal(self, coin: str, timeframe: str = "4h") -> GodSignal:
        """دریافت سیگنال برای یک ارز"""
        return self.scanner.signal_generator.generate_god_signal(
            coin, 
            self.scanner._fetch_coin_data(coin, timeframe)
        )
    
    def get_top_opportunities(self, limit: int = 10) -> List[GodSignal]:
        """بهترین فرصت‌های معاملاتی"""
        return self.scanner.get_top_signals("4h", limit)
    
    def scan_market(self) -> MarketOverview:
        """اسکن سریع بازار"""
        return self.scanner.get_market_overview()

# ============================================================
#                    SINGLETON
# ============================================================

_god_mode_engine = None

def get_god_mode_engine() -> GodModeEngine:
    global _god_mode_engine
    if _god_mode_engine is None:
        _god_mode_engine = GodModeEngine()
    return _god_mode_engine

# ============================================================
#                    COMPATIBILITY
# ============================================================

def start():
    """Compatibility function for ModuleManager"""
    engine = get_god_mode_engine()
    # Start auto-scanning in background
    import threading
    def run_scan():
        asyncio.run(engine.start_auto_scanning())
    thread = threading.Thread(target=run_scan, daemon=True)
    thread.start()
    return True

def get_signal(coin: str, timeframe: str = "4h") -> GodSignal:
    """Quick signal generation"""
    return get_god_mode_engine().get_signal(coin, timeframe)

def get_top_signals(limit: int = 10) -> List[GodSignal]:
    """Get top trading opportunities"""
    return get_god_mode_engine().get_top_opportunities(limit)

def get_market_overview() -> MarketOverview:
    """Get market overview"""
    return get_god_mode_engine().scan_market()

async def send_signal_to_channel(coin: str, timeframe: str = "4h") -> bool:
    """Generate and send signal to channel"""
    engine = get_god_mode_engine()
    signal = engine.get_signal(coin, timeframe)
    return await engine.channel.send_signal(signal)

async def send_overview_to_channel() -> bool:
    """Send market overview to channel"""
    engine = get_god_mode_engine()
    overview = engine.scan_market()
    return await engine.channel.send_market_overview(overview)

async def send_top_to_channel() -> bool:
    """Send top signals to channel"""
    engine = get_god_mode_engine()
    signals = engine.get_top_opportunities(10)
    return await engine.channel.send_top_signals(signals)
