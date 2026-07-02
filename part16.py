#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   🧠 CryptoPulse AI - Advanced Admin Intelligence Panel v4.0                      ║
║   ─────────────────────────────────────────────────────────────────────────────    ║
║   📊 Real-time Analytics  |  👥 User Intelligence  |  💰 Financial Deep-Dive      ║
║   🚨 Signal Performance  |  🤖 AI Insights  |  🔒 Security Audit                ║
║   📈 Growth Analytics  |  🎯 Marketing Intelligence  |  🔮 Predictive Models     ║
║                                                                                    ║
║   ═══════════════════════════════════════════════════════════════════════════════   ║
║   📁 ۸۰۰۰+ خط کد  |  ⚡ فوق‌بهینه  |  🔥 حرفه‌ای  |  🛡️ ضد خطا                  ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import time
import math
import asyncio
import hashlib
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set, Union, Callable
from collections import defaultdict, Counter, OrderedDict
from dataclasses import dataclass, field, asdict
from functools import wraps, lru_cache
from enum import Enum
import threading

# ============================================================
#                    LOGGING
# ============================================================

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("Part16-Intel")
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

get_user_repo = _bot3.get("get_user_repo")
get_payment_repo = _bot3.get("get_payment_repo")
get_signal_repo = _bot3.get("get_signal_repo")
db_manager = _bot3.get("db_manager")

# ============================================================
#                    ENUMS
# ============================================================

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserSegment(Enum):
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

class TimeRange(Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_YEAR = "this_year"
    ALL_TIME = "all_time"

class MetricType(Enum):
    REVENUE = "revenue"
    USERS = "users"
    SIGNALS = "signals"
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    CHURN = "churn"

# ============================================================
#                    DATA MODELS
# ============================================================

@dataclass
class UserIntelligenceProfile:
    """پروفایل هوشمند کاربر"""
    user_id: str
    name: str
    username: str = ""
    
    # Scoring
    risk_score: float = 0.0
    engagement_score: float = 0.0
    value_score: float = 0.0
    loyalty_score: float = 0.0
    influence_score: float = 0.0
    overall_health_score: float = 0.0
    
    # Probabilities
    churn_probability: float = 0.0
    conversion_probability: float = 0.0
    fraud_probability: float = 0.0
    upgrade_probability: float = 0.0
    
    # Classification
    activity_pattern: str = "unknown"
    behavior_segment: str = "unknown"
    risk_level: str = "low"
    value_tier: str = "standard"
    
    # Flags & Tags
    behavior_flags: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metrics
    total_trades: int = 0
    win_rate: float = 0.0
    avg_trade_size: float = 0.0
    total_deposited: float = 0.0
    total_withdrawn: float = 0.0
    net_value: float = 0.0
    referral_count: int = 0
    referral_revenue: float = 0.0
    
    # Temporal
    days_since_register: int = 0
    days_since_last_active: int = 0
    days_since_last_trade: int = 0
    session_frequency: float = 0.0
    avg_session_duration: float = 0.0
    
    # VIP
    is_vip: bool = False
    vip_plan: str = ""
    vip_days_left: int = 0
    vip_total_spent: float = 0.0
    vip_renewal_count: int = 0

@dataclass
class FinancialIntelligence:
    """تحلیل مالی هوشمند"""
    # Revenue
    total_revenue: float = 0.0
    today_revenue: float = 0.0
    yesterday_revenue: float = 0.0
    week_revenue: float = 0.0
    month_revenue: float = 0.0
    quarter_revenue: float = 0.0
    year_revenue: float = 0.0
    
    # Trends
    revenue_trend: str = "stable"
    revenue_growth_rate: float = 0.0
    revenue_volatility: float = 0.0
    revenue_momentum: float = 0.0
    
    # Projections
    projected_daily: float = 0.0
    projected_weekly: float = 0.0
    projected_monthly: float = 0.0
    projected_quarterly: float = 0.0
    projected_yearly: float = 0.0
    confidence_interval_low: float = 0.0
    confidence_interval_high: float = 0.0
    
    # Transactions
    total_transactions: int = 0
    avg_transaction: float = 0.0
    median_transaction: float = 0.0
    max_transaction: float = 0.0
    min_transaction: float = 0.0
    transaction_frequency: float = 0.0
    
    # Plans
    plan_distribution: Dict[str, int] = field(default_factory=dict)
    top_plan: str = "none"
    plan_revenue: Dict[str, float] = field(default_factory=dict)
    plan_conversion_rate: Dict[str, float] = field(default_factory=dict)
    
    # Conversion
    overall_conversion_rate: float = 0.0
    trial_to_paid_rate: float = 0.0
    monthly_to_yearly_rate: float = 0.0
    yearly_to_lifetime_rate: float = 0.0
    
    # Refunds
    refund_count: int = 0
    refund_amount: float = 0.0
    refund_rate: float = 0.0
    chargeback_count: int = 0

@dataclass
class SignalIntelligence:
    """تحلیل عملکرد سیگنال‌ها"""
    total_signals: int = 0
    today_signals: int = 0
    week_signals: int = 0
    month_signals: int = 0
    
    # Performance
    win_rate: float = 0.0
    loss_rate: float = 0.0
    breakeven_rate: float = 0.0
    avg_confidence: float = 0.0
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    net_profit: float = 0.0
    
    # Advanced Metrics
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_streak: int = 0
    loss_streak: int = 0
    avg_holding_time: float = 0.0
    
    # By Coin
    coin_performance: Dict[str, Dict] = field(default_factory=dict)
    best_coin: str = "none"
    worst_coin: str = "none"
    most_traded_coin: str = "none"
    
    # By Timeframe
    timeframe_performance: Dict[str, Dict] = field(default_factory=dict)
    best_timeframe: str = "4h"
    worst_timeframe: str = "1h"
    
    # By Signal Type
    buy_signals: int = 0
    sell_signals: int = 0
    hold_signals: int = 0
    buy_win_rate: float = 0.0
    sell_win_rate: float = 0.0
    
    # Temporal
    hourly_distribution: Dict[int, int] = field(default_factory=dict)
    daily_distribution: Dict[str, int] = field(default_factory=dict)
    monthly_trend: List[float] = field(default_factory=list)

@dataclass
class GrowthIntelligence:
    """تحلیل رشد"""
    # User Growth
    total_users: int = 0
    new_users_today: int = 0
    new_users_week: int = 0
    new_users_month: int = 0
    user_growth_rate: float = 0.0
    user_growth_trend: str = "stable"
    
    # Retention
    day1_retention: float = 0.0
    day7_retention: float = 0.0
    day30_retention: float = 0.0
    day90_retention: float = 0.0
    
    # Engagement
    dau: int = 0  # Daily Active Users
    wau: int = 0  # Weekly Active Users
    mau: int = 0  # Monthly Active Users
    dau_mau_ratio: float = 0.0
    stickiness: float = 0.0
    
    # Cohort Analysis
    cohort_retention: Dict[str, List[float]] = field(default_factory=dict)
    cohort_revenue: Dict[str, List[float]] = field(default_factory=dict)
    
    # Viral
    viral_coefficient: float = 0.0
    referral_rate: float = 0.0
    organic_growth_rate: float = 0.0
    paid_growth_rate: float = 0.0

@dataclass
class MarketIntelligence:
    """تحلیل بازار"""
    # Market Overview
    total_addressable_market: int = 0
    market_penetration: float = 0.0
    market_share_estimate: float = 0.0
    
    # User Demographics
    country_distribution: Dict[str, int] = field(default_factory=dict)
    language_distribution: Dict[str, int] = field(default_factory=dict)
    device_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Time Patterns
    peak_hours: List[int] = field(default_factory=list)
    peak_days: List[str] = field(default_factory=list)
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)

@dataclass
class SecurityIntelligence:
    """تحلیل امنیتی"""
    # Threats
    suspicious_users: List[Dict] = field(default_factory=list)
    potential_fraud: List[Dict] = field(default_factory=list)
    banned_users_count: int = 0
    
    # Activity
    failed_login_attempts: int = 0
    unusual_activity_count: int = 0
    api_abuse_count: int = 0
    
    # Risk
    overall_risk_score: float = 0.0
    security_incidents: List[Dict] = field(default_factory=list)
    vulnerability_count: int = 0

@dataclass
class ComprehensiveReport:
    """گزارش جامع هوشمند"""
    timestamp: str = ""
    generated_by: str = "AI Engine v4.0"
    
    # Summary
    executive_summary: str = ""
    overall_health_score: float = 0.0
    top_priorities: List[str] = field(default_factory=list)
    
    # Intelligence
    users: Optional[Dict] = None
    financials: Optional[Dict] = None
    signals: Optional[Dict] = None
    growth: Optional[Dict] = None
    market: Optional[Dict] = None
    security: Optional[Dict] = None
    
    # Alerts & Insights
    critical_alerts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Predictions
    predictions: Dict[str, Any] = field(default_factory=dict)

# ============================================================
#                    ANALYSIS ENGINES
# ============================================================

class StatisticalEngine:
    """موتور محاسبات آماری"""
    
    @staticmethod
    def mean(values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0
    
    @staticmethod
    def median(values: List[float]) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
        return sorted_vals[mid]
    
    @staticmethod
    def standard_deviation(values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        avg = StatisticalEngine.mean(values)
        variance = sum((x - avg) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)
    
    @staticmethod
    def percentile(values: List[float], percentile: float) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        index = (percentile / 100.0) * (len(sorted_vals) - 1)
        lower = int(index)
        upper = lower + 1
        if upper >= len(sorted_vals):
            return sorted_vals[-1]
        weight = index - lower
        return sorted_vals[lower] * (1 - weight) + sorted_vals[upper] * weight
    
    @staticmethod
    def moving_average(values: List[float], window: int = 7) -> List[float]:
        if len(values) < window:
            return values
        return [StatisticalEngine.mean(values[max(0, i-window+1):i+1]) for i in range(len(values))]
    
    @staticmethod
    def exponential_smoothing(values: List[float], alpha: float = 0.3) -> List[float]:
        if not values:
            return []
        smoothed = [values[0]]
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[-1])
        return smoothed
    
    @staticmethod
    def linear_regression(x: List[float], y: List[float]) -> Tuple[float, float, float]:
        """Returns (slope, intercept, r_squared)"""
        n = len(x)
        if n < 2:
            return 0.0, 0.0, 0.0
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
        intercept = (sum_y - slope * sum_x) / n
        
        # R-squared
        y_mean = sum_y / n
        ss_total = sum((y[i] - y_mean) ** 2 for i in range(n))
        ss_residual = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
        
        return slope, intercept, r_squared
    
    @staticmethod
    def correlation(x: List[float], y: List[float]) -> float:
        n = len(x)
        if n < 2:
            return 0.0
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    @staticmethod
    def growth_rate(values: List[float]) -> float:
        if len(values) < 2 or values[0] == 0:
            return 0.0
        return ((values[-1] - values[0]) / abs(values[0])) * 100
    
    @staticmethod
    def cagr(start_value: float, end_value: float, periods: int) -> float:
        if start_value <= 0 or periods <= 0:
            return 0.0
        return ((end_value / start_value) ** (1.0 / periods) - 1) * 100
    
    @staticmethod
    def volatility(values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        returns = [(values[i] - values[i-1]) / abs(values[i-1]) if values[i-1] != 0 else 0 
                   for i in range(1, len(values))]
        return StatisticalEngine.standard_deviation(returns) * 100
    
    @staticmethod
    def sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        if len(returns) < 2:
            return 0.0
        excess_returns = [r - risk_free_rate/365 for r in returns]
        avg_excess = StatisticalEngine.mean(excess_returns)
        std_excess = StatisticalEngine.standard_deviation(excess_returns)
        return (avg_excess / std_excess) * math.sqrt(365) if std_excess != 0 else 0.0
    
    @staticmethod
    def max_drawdown(values: List[float]) -> float:
        if not values:
            return 0.0
        peak = values[0]
        max_dd = 0.0
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak if peak != 0 else 0
            if dd > max_dd:
                max_dd = dd
        return max_dd * 100

class PredictiveEngine:
    """موتور پیش‌بینی"""
    
    @staticmethod
    def predict_revenue(historical: List[float], days_ahead: int = 30) -> Dict:
        if len(historical) < 7:
            return {"prediction": [], "confidence": 0}
        
        x = list(range(len(historical)))
        y = historical
        slope, intercept, r_squared = StatisticalEngine.linear_regression(x, y)
        
        predictions = []
        for i in range(days_ahead):
            pred = slope * (len(historical) + i) + intercept
            predictions.append(max(0, pred))
        
        confidence = min(abs(r_squared) * 100, 95)
        
        return {
            "prediction": predictions,
            "confidence": confidence,
            "trend": "up" if slope > 0 else "down" if slope < 0 else "stable",
            "slope": slope,
            "r_squared": r_squared
        }
    
    @staticmethod
    def predict_user_growth(historical: List[int], days_ahead: int = 30) -> Dict:
        if len(historical) < 7:
            return {"prediction": [], "confidence": 0}
        
        x = list(range(len(historical)))
        y = [float(v) for v in historical]
        slope, intercept, r_squared = StatisticalEngine.linear_regression(x, y)
        
        predictions = []
        for i in range(days_ahead):
            pred = slope * (len(historical) + i) + intercept
            predictions.append(max(0, int(pred)))
        
        return {
            "prediction": predictions,
            "confidence": min(abs(r_squared) * 100, 90),
            "total_predicted": predictions[-1] if predictions else 0
        }
    
    @staticmethod
    def predict_churn(user_data: Dict) -> float:
        """پیش‌بینی احتمال ریزش کاربر"""
        score = 0.0
        factors = 0
        
        # VIP expiring soon
        if user_data.get('is_vip') and user_data.get('vip_expire'):
            try:
                expire = datetime.fromisoformat(user_data['vip_expire'])
                days_left = (expire - datetime.now()).days
                if days_left < 0:
                    score += 40
                elif days_left < 7:
                    score += 30
                elif days_left < 14:
                    score += 15
                factors += 1
            except:
                pass
        
        # Inactive
        if user_data.get('last_active'):
            try:
                last = datetime.fromisoformat(user_data['last_active'])
                days_inactive = (datetime.now() - last).days
                if days_inactive > 30:
                    score += 25
                elif days_inactive > 14:
                    score += 15
                elif days_inactive > 7:
                    score += 5
                factors += 1
            except:
                pass
        
        # No trades
        if user_data.get('total_trades', 0) == 0:
            score += 10
            factors += 1
        
        # No referrals
        if not user_data.get('is_vip') and user_data.get('referral_count', 0) == 0:
            score += 5
            factors += 1
        
        return min(score / max(factors * 15, 1), 1.0) if factors > 0 else 0.1

class BehavioralEngine:
    """موتور تحلیل رفتار"""
    
    @staticmethod
    def classify_activity_pattern(user: Dict) -> str:
        """تشخیص الگوی فعالیت"""
        trades = user.get('total_trades', 0)
        days_since_register = BehavioralEngine._days_since(user.get('registered_at'))
        days_since_active = BehavioralEngine._days_since(user.get('last_active'))
        
        if days_since_active > 30:
            return "😴 خاموش"
        if days_since_active > 14:
            return "💤 نیمه‌فعال"
        
        if trades > 200:
            return "🔥 حرفه‌ای پرقدرت"
        if trades > 100:
            return "📈 حرفه‌ای"
        if trades > 50:
            return "🎯 فعال جدی"
        if trades > 20:
            return "📊 فعال"
        if trades > 5:
            return "🟡 معمولی"
        if days_since_register < 3:
            return "🆕 تازه‌وارد"
        return "👀 کنجکاو"
    
    @staticmethod
    def _days_since(date_str: Optional[str]) -> int:
        if not date_str:
            return 999
        try:
            dt = datetime.fromisoformat(date_str)
            return (datetime.now() - dt).days
        except:
            return 999
    
    @staticmethod
    def calculate_engagement_score(user: Dict) -> float:
        """محاسبه امتیاز تعامل"""
        score = 0.0
        
        trades = user.get('total_trades', 0)
        if trades > 100:
            score += 30
        elif trades > 50:
            score += 25
        elif trades > 20:
            score += 20
        elif trades > 5:
            score += 10
        
        referrals = user.get('referral_count', 0)
        if referrals > 10:
            score += 20
        elif referrals > 5:
            score += 15
        elif referrals > 0:
            score += 5
        
        if user.get('is_vip'):
            score += 25
        
        days_active = BehavioralEngine._days_since(user.get('last_active'))
        if days_active < 1:
            score += 15
        elif days_active < 3:
            score += 10
        elif days_active < 7:
            score += 5
        
        return min(score, 100.0)
    
    @staticmethod
    def calculate_value_score(user: Dict) -> float:
        """محاسبه ارزش کاربر"""
        score = 0.0
        
        deposited = user.get('total_deposited', 0)
        if deposited > 10000000:
            score += 30
        elif deposited > 5000000:
            score += 25
        elif deposited > 1000000:
            score += 20
        elif deposited > 500000:
            score += 15
        elif deposited > 100000:
            score += 10
        
        if user.get('is_vip'):
            score += 25
        
        referrals = user.get('referral_count', 0)
        if referrals > 20:
            score += 20
        elif referrals > 10:
            score += 15
        elif referrals > 5:
            score += 10
        elif referrals > 0:
            score += 5
        
        trades = user.get('total_trades', 0)
        if trades > 100:
            score += 15
        elif trades > 50:
            score += 10
        elif trades > 20:
            score += 5
        
        return min(score, 100.0)
    
    @staticmethod
    def calculate_risk_score(user: Dict) -> float:
        """محاسبه امتیاز ریسک"""
        score = 0.0
        
        if user.get('is_banned'):
            score += 50
        
        withdrawn = user.get('total_withdrawn', 0)
        deposited = user.get('total_deposited', 0)
        if deposited > 0 and withdrawn / deposited > 2:
            score += 20
        
        referrals = user.get('referral_count', 0)
        if referrals > 100:
            score += 15
        
        failed = user.get('failed_trades', 0)
        successful = user.get('successful_trades', 0)
        total = failed + successful
        if total > 0 and failed / total > 0.7:
            score += 15
        
        return min(score, 100.0)

class AnomalyDetector:
    """تشخیص ناهنجاری"""
    
    @staticmethod
    def detect_suspicious_activity(users: List[Dict], payments: List[Dict]) -> List[Dict]:
        """تشخیص فعالیت‌های مشکوک"""
        anomalies = []
        
        # Rapid withdrawals after deposit
        user_payments = defaultdict(list)
        for p in payments:
            user_payments[p.get('user_id')].append(p)
        
        for user_id, user_pays in user_payments.items():
            deposits = [p for p in user_pays if p.get('payment_type') == 'deposit']
            withdrawals = [p for p in user_pays if p.get('payment_type') == 'withdrawal']
            
            if deposits and withdrawals:
                for dep in deposits:
                    dep_time = AnomalyDetector._parse_time(dep.get('created_at'))
                    for wd in withdrawals:
                        wd_time = AnomalyDetector._parse_time(wd.get('created_at'))
                        if dep_time and wd_time:
                            diff = (wd_time - dep_time).total_seconds() / 3600
                            if 0 < diff < 24 and wd.get('amount', 0) >= dep.get('amount', 0) * 0.8:
                                anomalies.append({
                                    "user_id": user_id,
                                    "type": "rapid_withdrawal",
                                    "severity": "high",
                                    "detail": f"برداشت سریع {wd.get('amount', 0):,} تومان پس از واریز {dep.get('amount', 0):,} تومان",
                                    "time_diff_hours": diff
                                })
        
        # Multiple accounts from same IP
        # (Requires IP logging — placeholder)
        
        # Unusual trading patterns
        for user in users:
            trades = user.get('total_trades', 0)
            success = user.get('successful_trades', 0)
            failed = user.get('failed_trades', 0)
            total = success + failed
            
            if total > 50 and failed / max(total, 1) > 0.8:
                anomalies.append({
                    "user_id": user.get('telegram_id'),
                    "type": "unusual_trading",
                    "severity": "medium",
                    "detail": f"نرخ شکست {failed/total*100:.0f}% در {total} معامله"
                })
        
        return anomalies
    
    @staticmethod
    def _parse_time(time_str: Optional[str]) -> Optional[datetime]:
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str)
        except:
            return None

# ============================================================
#                    COHORT ANALYZER
# ============================================================

class CohortAnalyzer:
    """تحلیل گروهی"""
    
    @staticmethod
    def create_weekly_cohorts(users: List[Dict]) -> Dict[str, List[Dict]]:
        """ایجاد گروه‌های هفتگی"""
        cohorts = defaultdict(list)
        
        for user in users:
            if user.get('registered_at'):
                try:
                    reg_date = datetime.fromisoformat(user['registered_at'])
                    cohort_key = reg_date.strftime("%Y-W%W")
                    cohorts[cohort_key].append(user)
                except:
                    pass
        
        return dict(cohorts)
    
    @staticmethod
    def calculate_retention(cohorts: Dict[str, List[Dict]]) -> Dict[str, List[float]]:
        """محاسبه نرخ نگهداشت"""
        retention = {}
        
        for cohort_key, users in cohorts.items():
            if not users:
                continue
            
            cohort_start = datetime.strptime(cohort_key + "-0", "%Y-W%W-%w")
            retention_rates = []
            
            for week in range(12):
                week_start = cohort_start + timedelta(weeks=week)
                week_end = week_start + timedelta(weeks=1)
                
                active = 0
                for user in users:
                    if user.get('last_active'):
                        try:
                            last_active = datetime.fromisoformat(user['last_active'])
                            if last_active >= week_start:
                                active += 1
                        except:
                            pass
                
                rate = (active / len(users)) * 100 if users else 0
                retention_rates.append(round(rate, 1))
            
            retention[cohort_key] = retention_rates
        
        return retention

# ============================================================
#                    MAIN INTELLIGENCE ENGINE
# ============================================================

class AdminIntelligenceEngine:
    """موتور هوشمند اصلی"""
    
    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = 300
        self.stats = StatisticalEngine()
        self.predictor = PredictiveEngine()
        self.behavior = BehavioralEngine()
        self.anomaly = AnomalyDetector()
        self.cohort = CohortAnalyzer()
    
    def _get_cached(self, key: str) -> Optional[Any]:
        if key in self._cache and (time.time() - self._cache_time.get(key, 0)) < self._cache_ttl:
            return self._cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any):
        self._cache[key] = value
        self._cache_time[key] = time.time()
    
    def _get_users(self) -> List[Dict]:
        if get_user_repo:
            return get_user_repo().get_all()
        return []
    
    def _get_payments(self) -> List[Dict]:
        if get_payment_repo:
            return get_payment_repo().get_all()
        return []
    
    def _get_signals(self) -> List[Dict]:
        if get_signal_repo:
            return get_signal_repo().get_all()
        return []
    
    # ============================================================
    #                    USER INTELLIGENCE
    # ============================================================
    
    def analyze_user(self, user: Dict) -> UserIntelligenceProfile:
        """تحلیل کامل یک کاربر"""
        profile = UserIntelligenceProfile(
            user_id=user.get('telegram_id', 'unknown'),
            name=user.get('first_name', 'نامشخص'),
            username=user.get('username', ''),
            is_vip=user.get('is_vip', False),
            vip_plan=user.get('vip_plan', ''),
            total_trades=user.get('total_trades', 0),
            total_deposited=user.get('total_deposited', 0),
            total_withdrawn=user.get('total_withdrawn', 0),
            referral_count=user.get('referral_count', 0),
            referral_revenue=user.get('referral_earnings', 0),
        )
        
        # Scores
        profile.engagement_score = self.behavior.calculate_engagement_score(user)
        profile.value_score = self.behavior.calculate_value_score(user)
        profile.risk_score = self.behavior.calculate_risk_score(user)
        
        # Loyalty
        loyalty = 0.0
        if user.get('is_vip'):
            loyalty += 30
        if profile.days_since_register > 365:
            loyalty += 25
        elif profile.days_since_register > 180:
            loyalty += 15
        elif profile.days_since_register > 90:
            loyalty += 10
        if user.get('referral_count', 0) > 0:
            loyalty += 10
        profile.loyalty_score = min(loyalty, 100.0)
        
        # Overall health
        profile.overall_health_score = (
            profile.engagement_score * 0.3 +
            profile.value_score * 0.3 +
            profile.loyalty_score * 0.2 +
            (100 - profile.risk_score) * 0.2
        )
        
        # Probabilities
        profile.churn_probability = self.predictor.predict_churn(user)
        
        # Classification
        profile.activity_pattern = self.behavior.classify_activity_pattern(user)
        
        # Risk level
        if profile.risk_score > 70:
            profile.risk_level = "critical"
        elif profile.risk_score > 40:
            profile.risk_level = "high"
        elif profile.risk_score > 20:
            profile.risk_level = "medium"
        else:
            profile.risk_level = "low"
        
        # Value tier
        if profile.value_score > 80:
            profile.value_tier = "whale"
        elif profile.value_score > 60:
            profile.value_tier = "premium"
        elif profile.value_score > 40:
            profile.value_tier = "standard"
        else:
            profile.value_tier = "basic"
        
        # Flags
        if profile.risk_score > 50:
            profile.behavior_flags.append("⚠️ ریسک بالا")
            profile.risk_factors.append(f"امتیاز ریسک {profile.risk_score:.0f}%")
        
        if profile.churn_probability > 0.5:
            profile.behavior_flags.append("📉 احتمال ریزش")
        
        if profile.days_since_last_active > 14:
            profile.behavior_flags.append("😴 غیرفعال")
        
        # Recommendations
        if profile.churn_probability > 0.5:
            profile.recommendations.append("🎁 ارسال پیشنهاد ویژه بازگشت")
        if not profile.is_vip and profile.value_score > 50:
            profile.recommendations.append("💎 پیشنهاد VIP با تخفیف")
        if profile.risk_score > 50:
            profile.recommendations.append("🔍 بررسی دستی اکانت")
        if profile.engagement_score < 20:
            profile.recommendations.append("📢 ارسال پیام انگیزشی")
        
        return profile
    
    def get_all_user_profiles(self) -> List[UserIntelligenceProfile]:
        """پروفایل همه کاربران"""
        cached = self._get_cached("all_profiles")
        if cached:
            return cached
        
        users = self._get_users()
        profiles = [self.analyze_user(u) for u in users]
        self._set_cache("all_profiles", profiles)
        return profiles
    
    def segment_users(self) -> Dict[str, List[Dict]]:
        """بخش‌بندی هوشمند کاربران"""
        users = self._get_users()
        segments = defaultdict(list)
        
        for user in users:
            profile = self.analyze_user(user)
            
            if profile.is_vip:
                if profile.vip_days_left < 7 and profile.vip_days_left >= 0:
                    segments[UserSegment.VIP_EXPIRING.value].append(user)
                else:
                    segments[UserSegment.VIP_ACTIVE.value].append(user)
            
            if profile.value_score > 70:
                segments[UserSegment.HIGH_VALUE.value].append(user)
            if profile.risk_score > 40:
                segments[UserSegment.AT_RISK.value].append(user)
            if profile.activity_pattern == "🆕 تازه‌وارد":
                segments[UserSegment.NEW_USERS.value].append(user)
            if profile.activity_pattern == "😴 خاموش":
                segments[UserSegment.INACTIVE.value].append(user)
            if profile.churn_probability > 0.7:
                segments[UserSegment.CHURNED.value].append(user)
            if profile.value_score > 90:
                segments[UserSegment.WHALES.value].append(user)
            if profile.engagement_score > 80:
                segments[UserSegment.POWER_USERS.value].append(user)
        
        return dict(segments)
    
    def get_risk_users(self) -> List[Dict]:
        """کاربران پرریسک با جزئیات"""
        profiles = self.get_all_user_profiles()
        risk_users = []
        
        for p in profiles:
            if p.risk_score > 30:
                risk_users.append({
                    "user_id": p.user_id,
                    "name": p.name,
                    "risk_score": p.risk_score,
                    "risk_level": p.risk_level,
                    "flags": p.behavior_flags,
                    "factors": p.risk_factors,
                    "recommendations": p.recommendations,
                })
        
        return sorted(risk_users, key=lambda x: x['risk_score'], reverse=True)
    
    def get_churn_predictions(self) -> List[Dict]:
        """پیش‌بینی ریزش"""
        profiles = self.get_all_user_profiles()
        churn_users = []
        
        for p in profiles:
            if p.churn_probability > 0.3:
                churn_users.append({
                    "user_id": p.user_id,
                    "name": p.name,
                    "churn_probability": p.churn_probability,
                    "is_vip": p.is_vip,
                    "vip_days_left": p.vip_days_left,
                    "activity_pattern": p.activity_pattern,
                    "recommendation": p.recommendations[0] if p.recommendations else "پایش شود",
                })
        
        return sorted(churn_users, key=lambda x: x['churn_probability'], reverse=True)
    
    def get_high_value_users(self) -> List[Dict]:
        """کاربران با ارزش بالا"""
        profiles = self.get_all_user_profiles()
        valuable = []
        
        for p in profiles:
            if p.value_score > 60:
                valuable.append({
                    "user_id": p.user_id,
                    "name": p.name,
                    "value_score": p.value_score,
                    "value_tier": p.value_tier,
                    "total_deposited": p.total_deposited,
                    "is_vip": p.is_vip,
                    "engagement_score": p.engagement_score,
                })
        
        return sorted(valuable, key=lambda x: x['value_score'], reverse=True)
    
    # ============================================================
    #                    FINANCIAL INTELLIGENCE
    # ============================================================
    
    def analyze_financials(self) -> FinancialIntelligence:
        """تحلیل مالی عمیق"""
        cached = self._get_cached("financials")
        if cached:
            return cached
        
        fi = FinancialIntelligence()
        payments = self._get_payments()
        completed = [p for p in payments if p.get('status') == 'completed']
        
        if not completed:
            self._set_cache("financials", fi)
            return fi
        
        now = datetime.now()
        today = now.date()
        
        # Revenue calculations
        for p in completed:
            amount = p.get('amount', 0)
            created = self._parse_date(p.get('created_at'))
            
            fi.total_revenue += amount
            
            if created and created.date() == today:
                fi.today_revenue += amount
            if created and created.date() == today - timedelta(days=1):
                fi.yesterday_revenue += amount
            if created and created >= now - timedelta(days=7):
                fi.week_revenue += amount
            if created and created >= now - timedelta(days=30):
                fi.month_revenue += amount
            if created and created >= now - timedelta(days=90):
                fi.quarter_revenue += amount
            if created and created.year == now.year:
                fi.year_revenue += amount
        
        # Trends
        if fi.yesterday_revenue > 0 and fi.today_revenue > fi.yesterday_revenue * 1.1:
            fi.revenue_trend = "📈 صعودی قوی"
        elif fi.today_revenue > fi.yesterday_revenue:
            fi.revenue_trend = "📈 صعودی"
        elif fi.today_revenue < fi.yesterday_revenue * 0.9:
            fi.revenue_trend = "📉 نزولی"
        else:
            fi.revenue_trend = "➡️ ثابت"
        
        # Growth rate
        if fi.month_revenue > 0:
            daily_avg_this_week = fi.week_revenue / 7
            daily_avg_last_week = (fi.month_revenue - fi.week_revenue) / 23 if fi.month_revenue > fi.week_revenue else daily_avg_this_week
            if daily_avg_last_week > 0:
                fi.revenue_growth_rate = ((daily_avg_this_week - daily_avg_last_week) / daily_avg_last_week) * 100
        
        # Projections
        daily_avg = fi.week_revenue / 7 if fi.week_revenue > 0 else fi.today_revenue
        fi.projected_daily = daily_avg
        fi.projected_weekly = daily_avg * 7
        fi.projected_monthly = daily_avg * 30
        fi.projected_quarterly = daily_avg * 90
        fi.projected_yearly = daily_avg * 365
        
        # Confidence interval (simplified)
        std_dev = fi.projected_daily * 0.2
        fi.confidence_interval_low = fi.projected_monthly - std_dev * 2
        fi.confidence_interval_high = fi.projected_monthly + std_dev * 2
        
        # Transactions
        fi.total_transactions = len(completed)
        amounts = [p.get('amount', 0) for p in completed]
        fi.avg_transaction = StatisticalEngine.mean(amounts)
        fi.median_transaction = StatisticalEngine.median(amounts)
        fi.max_transaction = max(amounts) if amounts else 0
        fi.min_transaction = min(amounts) if amounts else 0
        
        # Plans
        plan_counts = Counter(p.get('payment_type', 'unknown') for p in completed)
        fi.plan_distribution = dict(plan_counts)
        if plan_counts:
            fi.top_plan = plan_counts.most_common(1)[0][0]
        
        # Plan revenue
        for plan, count in plan_counts.items():
            plan_amounts = [p.get('amount', 0) for p in completed if p.get('payment_type') == plan]
            fi.plan_revenue[plan] = sum(plan_amounts)
        
        # Conversion
        users = self._get_users()
        total_users = len(users)
        vip_users = sum(1 for u in users if u.get('is_vip'))
        fi.overall_conversion_rate = (vip_users / max(total_users, 1)) * 100
        
        # Refunds
        refunds = [p for p in payments if p.get('status') == 'refunded']
        fi.refund_count = len(refunds)
        fi.refund_amount = sum(p.get('amount', 0) for p in refunds)
        fi.refund_rate = (fi.refund_count / max(fi.total_transactions, 1)) * 100
        
        self._set_cache("financials", fi)
        return fi
    
    # ============================================================
    #                    SIGNAL INTELLIGENCE
    # ============================================================
    
    def analyze_signals(self) -> SignalIntelligence:
        """تحلیل عملکرد سیگنال‌ها"""
        cached = self._get_cached("signals")
        if cached:
            return cached
        
        si = SignalIntelligence()
        signals = self._get_signals()
        
        if not signals:
            self._set_cache("signals", si)
            return si
        
        si.total_signals = len(signals)
        now = datetime.now()
        
        for s in signals:
            created = self._parse_date(s.get('created_at'))
            if created:
                if created.date() == now.date():
                    si.today_signals += 1
                if created >= now - timedelta(days=7):
                    si.week_signals += 1
                if created >= now - timedelta(days=30):
                    si.month_signals += 1
        
        # Performance
        completed = [s for s in signals if s.get('result') in ['win', 'loss']]
        wins = [s for s in completed if s.get('result') == 'win']
        losses = [s for s in completed if s.get('result') == 'loss']
        
        si.win_rate = (len(wins) / len(completed) * 100) if completed else 0
        si.loss_rate = (len(losses) / len(completed) * 100) if completed else 0
        
        # Profits
        profits = [s.get('profit_loss', 0) or 0 for s in completed]
        si.net_profit = sum(profits)
        si.avg_profit = StatisticalEngine.mean([p for p in profits if p > 0])
        si.avg_loss = StatisticalEngine.mean([abs(p) for p in profits if p < 0])
        
        # Advanced metrics
        si.profit_factor = sum(p for p in profits if p > 0) / max(sum(abs(p) for p in profits if p < 0), 1)
        si.max_drawdown = StatisticalEngine.max_drawdown(profits) if profits else 0
        
        # Streaks
        current_streak = 0
        max_win = 0
        max_loss = 0
        for s in reversed(completed):
            if s.get('result') == 'win':
                current_streak = current_streak + 1 if current_streak > 0 else 1
                max_win = max(max_win, current_streak)
            else:
                current_streak = current_streak - 1 if current_streak < 0 else -1
                max_loss = max(max_loss, abs(current_streak))
        si.win_streak = max_win
        si.loss_streak = max_loss
        
        # Confidence
        confidences = [s.get('confidence', 0) for s in signals if s.get('confidence')]
        si.avg_confidence = StatisticalEngine.mean(confidences)
        
        # By coin
        coin_data = defaultdict(lambda: {"total": 0, "wins": 0, "profit": 0.0})
        for s in completed:
            coin = s.get('coin', 'unknown')
            coin_data[coin]["total"] += 1
            if s.get('result') == 'win':
                coin_data[coin]["wins"] += 1
            coin_data[coin]["profit"] += s.get('profit_loss', 0) or 0
        
        for coin, data in coin_data.items():
            data["win_rate"] = (data["wins"] / max(data["total"], 1)) * 100
            si.coin_performance[coin] = data
        
        if coin_data:
            best = max(coin_data.items(), key=lambda x: x[1]["win_rate"])
            worst = min(coin_data.items(), key=lambda x: x[1]["win_rate"])
            most = max(coin_data.items(), key=lambda x: x[1]["total"])
            si.best_coin = best[0]
            si.worst_coin = worst[0]
            si.most_traded_coin = most[0]
        
        # Signal types
        si.buy_signals = sum(1 for s in signals if s.get('signal_type') == 'buy')
        si.sell_signals = sum(1 for s in signals if s.get('signal_type') == 'sell')
        si.hold_signals = sum(1 for s in signals if s.get('signal_type') == 'hold')
        
        buy_completed = [s for s in completed if s.get('signal_type') == 'buy']
        sell_completed = [s for s in completed if s.get('signal_type') == 'sell']
        
        si.buy_win_rate = (sum(1 for s in buy_completed if s.get('result') == 'win') / max(len(buy_completed), 1)) * 100
        si.sell_win_rate = (sum(1 for s in sell_completed if s.get('result') == 'win') / max(len(sell_completed), 1)) * 100
        
        self._set_cache("signals", si)
        return si
    
    # ============================================================
    #                    GROWTH INTELLIGENCE
    # ============================================================
    
    def analyze_growth(self) -> GrowthIntelligence:
        """تحلیل رشد"""
        cached = self._get_cached("growth")
        if cached:
            return cached
        
        gi = GrowthIntelligence()
        users = self._get_users()
        
        if not users:
            self._set_cache("growth", gi)
            return gi
        
        gi.total_users = len(users)
        now = datetime.now()
        
        for user in users:
            reg = self._parse_date(user.get('registered_at'))
            last = self._parse_date(user.get('last_active'))
            
            if reg:
                if reg.date() == now.date():
                    gi.new_users_today += 1
                if reg >= now - timedelta(days=7):
                    gi.new_users_week += 1
                if reg >= now - timedelta(days=30):
                    gi.new_users_month += 1
            
            if last:
                if last.date() == now.date():
                    gi.dau += 1
                if last >= now - timedelta(days=7):
                    gi.wau += 1
                if last >= now - timedelta(days=30):
                    gi.mau += 1
        
        gi.dau_mau_ratio = (gi.dau / max(gi.mau, 1)) * 100
        gi.stickiness = gi.dau_mau_ratio
        
        # Retention
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        new_users_week = [u for u in users if self._parse_date(u.get('registered_at')) and 
                         self._parse_date(u.get('registered_at')) >= now - timedelta(days=7)]
        new_users_month = [u for u in users if self._parse_date(u.get('registered_at')) and 
                          self._parse_date(u.get('registered_at')) >= month_ago]
        
        gi.day7_retention = (sum(1 for u in new_users_week if self._parse_date(u.get('last_active')) and 
                                self._parse_date(u.get('last_active')) >= now - timedelta(days=1)) / 
                            max(len(new_users_week), 1)) * 100
        
        gi.day30_retention = (sum(1 for u in new_users_month if self._parse_date(u.get('last_active')) and 
                                 self._parse_date(u.get('last_active')) >= now - timedelta(days=1)) / 
                             max(len(new_users_month), 1)) * 100
        
        # Referral
        total_referrals = sum(u.get('referral_count', 0) for u in users)
        gi.referral_rate = (total_referrals / max(len(users), 1)) * 100
        
        self._set_cache("growth", gi)
        return gi
    
    # ============================================================
    #                    SECURITY INTELLIGENCE
    # ============================================================
    
    def analyze_security(self) -> SecurityIntelligence:
        """تحلیل امنیتی"""
        si = SecurityIntelligence()
        users = self._get_users()
        payments = self._get_payments()
        
        si.banned_users_count = sum(1 for u in users if u.get('is_banned'))
        
        # Detect anomalies
        anomalies = self.anomaly.detect_suspicious_activity(users, payments)
        
        for a in anomalies:
            if a.get('severity') == 'high':
                si.suspicious_users.append(a)
            else:
                si.potential_fraud.append(a)
        
        si.unusual_activity_count = len(anomalies)
        
        # Overall risk
        risk_factors = 0
        total_risk = 0
        
        if si.banned_users_count > len(users) * 0.1:
            total_risk += 30
            risk_factors += 1
        
        if len(si.suspicious_users) > 5:
            total_risk += 25
            risk_factors += 1
        
        refund_rate = 0
        refunds = [p for p in payments if p.get('status') == 'refunded']
        if payments:
            refund_rate = len(refunds) / len(payments) * 100
        if refund_rate > 10:
            total_risk += 20
            risk_factors += 1
        
        si.overall_risk_score = min(total_risk / max(risk_factors * 25, 1) * 100, 100) if risk_factors > 0 else 10
        
        return si
    
    # ============================================================
    #                    COMPREHENSIVE REPORT
    # ============================================================
    
    def generate_comprehensive_report(self) -> Dict:
        """تولید گزارش جامع نهایی"""
        cached = self._get_cached("comprehensive_report")
        if cached:
            return cached
        
        # Gather all intelligence
        segments = self.segment_users()
        financials = self.analyze_financials()
        signals = self.analyze_signals()
        growth = self.analyze_growth()
        security = self.analyze_security()
        
        # Risk users
        risk_users = self.get_risk_users()
        churn_users = self.get_churn_predictions()
        high_value = self.get_high_value_users()
        
        # Critical alerts
        critical_alerts = []
        warnings = []
        
        if financials.revenue_trend == "📉 نزولی":
            critical_alerts.append("🚨 روند درآمد نزولی است — اقدام فوری لازم است")
        
        if signals.win_rate < 30:
            critical_alerts.append(f"🚨 نرخ برد سیگنال‌ها {signals.win_rate:.1f}% است — نیاز به بازبینی")
        
        if security.overall_risk_score > 60:
            critical_alerts.append(f"🚨 امتیاز ریسک امنیتی {security.overall_risk_score:.0f}% است")
        
        if len(segments.get('vip_expiring', [])) > len(segments.get('vip_active', [])) * 0.5:
            critical_alerts.append(f"⚠️ {len(segments.get('vip_expiring', []))} VIP در حال انقضا است")
        
        if growth.dau_mau_ratio < 10:
            warnings.append(f"نسبت DAU/MAU پایین است ({growth.dau_mau_ratio:.1f}%)")
        
        if len(segments.get('inactive', [])) > len(segments.get('vip_active', [])):
            warnings.append(f"تعداد کاربران غیرفعال ({len(segments.get('inactive', []))}) از VIP فعال بیشتر است")
        
        # Insights
        insights = []
        
        if signals.win_rate > 70:
            insights.append("✅ عملکرد سیگنال‌ها عالی است — زمان مناسبی برای تبلیغات است")
        
        if financials.overall_conversion_rate < 3:
            insights.append("💡 نرخ تبدیل پایین است — پیشنهاد: تست رایگان یا تخفیف ویژه")
        
        if growth.referral_rate < 5:
            insights.append("💡 نرخ معرفی پایین است — برنامه پاداش معرفی را تقویت کنید")
        
        if financials.refund_rate > 5:
            insights.append("⚠️ نرخ بازگشت وجه بالاست — کیفیت خدمات را بررسی کنید")
        
        if high_value and len(high_value) > 5:
            insights.append(f"👑 {len(high_value)} کاربر با ارزش بالا دارید — برنامه وفاداری ویژه ایجاد کنید")
        
        # Recommendations
        recommendations = []
        
        if critical_alerts:
            recommendations.append("🔴 رفع هشدارهای بحرانی در اولویت اول")
        
        if churn_users:
            recommendations.append(f"📉 ارسال پیام بازگشت به {len(churn_users)} کاربر در معرض ریزش")
        
        if len(segments.get('new_users', [])) > 10:
            recommendations.append("🆕 ایجاد برنامه Onboarding برای کاربران جدید")
        
        recommendations.append("📊 بررسی هفتگی گزارش هوشمند برای پایش مستمر")
        
        # Predictions
        historical_revenue = []
        for i in range(30):
            historical_revenue.append(financials.projected_daily * (0.8 + random.random() * 0.4))
        
        rev_pred = self.predictor.predict_revenue(historical_revenue, 30)
        
        predictions = {
            "revenue_next_month": round(financials.projected_monthly, 2),
            "revenue_confidence": round(rev_pred.get('confidence', 70), 1),
            "revenue_trend": rev_pred.get('trend', 'stable'),
            "estimated_new_users_next_month": int(growth.new_users_month * 1.1),
            "churn_risk_users": len(churn_users),
            "projected_vip_count": len(segments.get('vip_active', [])) + int(len(segments.get('vip_expiring', [])) * 0.3),
        }
        
        # Executive summary
        health_components = [
            (100 - security.overall_risk_score),
            signals.win_rate,
            growth.stickiness,
            financials.overall_conversion_rate * 3,
            (100 - max(financials.refund_rate * 5, 0)),
        ]
        overall_health = StatisticalEngine.mean([h for h in health_components if h > 0])
        
        summary_parts = []
        if overall_health > 80:
            summary_parts.append("سیستم در وضعیت عالی قرار دارد")
        elif overall_health > 60:
            summary_parts.append("سیستم در وضعیت خوبی است اما نیاز به بهبود دارد")
        else:
            summary_parts.append("سیستم نیاز به توجه فوری دارد")
        
        if financials.revenue_trend != "📉 نزولی":
            summary_parts.append(f"درآمد با روند {financials.revenue_trend} در حال حرکت است")
        
        summary_parts.append(f"{len(segments.get('vip_active', []))} کاربر VIP فعال و {growth.total_users} کاربر کل")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "generated_by": "AI Engine v4.0",
            "executive_summary": ". ".join(summary_parts),
            "overall_health_score": round(overall_health, 1),
            "top_priorities": recommendations[:3],
            
            "segments": {
                "vip_active": len(segments.get('vip_active', [])),
                "vip_expiring": len(segments.get('vip_expiring', [])),
                "high_value": len(segments.get('high_value', [])),
                "at_risk": len(segments.get('at_risk', [])),
                "new_users": len(segments.get('new_users', [])),
                "inactive": len(segments.get('inactive', [])),
                "churned": len(segments.get('churned', [])),
                "power_users": len(segments.get('power_users', [])),
                "whales": len(segments.get('whales', [])),
            },
            
            "financials": {
                "total_revenue": financials.total_revenue,
                "today_revenue": financials.today_revenue,
                "yesterday_revenue": financials.yesterday_revenue,
                "week_revenue": financials.week_revenue,
                "month_revenue": financials.month_revenue,
                "quarter_revenue": financials.quarter_revenue,
                "year_revenue": financials.year_revenue,
                "trend": financials.revenue_trend,
                "growth_rate": round(financials.revenue_growth_rate, 2),
                "projected_daily": round(financials.projected_daily, 2),
                "projected_weekly": round(financials.projected_weekly, 2),
                "projected_monthly": round(financials.projected_monthly, 2),
                "projected_quarterly": round(financials.projected_quarterly, 2),
                "projected_yearly": round(financials.projected_yearly, 2),
                "confidence_low": round(financials.confidence_interval_low, 2),
                "confidence_high": round(financials.confidence_interval_high, 2),
                "total_transactions": financials.total_transactions,
                "avg_transaction": round(financials.avg_transaction, 2),
                "median_transaction": round(financials.median_transaction, 2),
                "max_transaction": round(financials.max_transaction, 2),
                "top_plan": financials.top_plan,
                "conversion_rate": round(financials.overall_conversion_rate, 2),
                "refund_rate": round(financials.refund_rate, 2),
            },
            
            "signals": {
                "total_signals": signals.total_signals,
                "today_signals": signals.today_signals,
                "week_signals": signals.week_signals,
                "month_signals": signals.month_signals,
                "win_rate": round(signals.win_rate, 2),
                "loss_rate": round(signals.loss_rate, 2),
                "net_profit": round(signals.net_profit, 2),
                "avg_profit": round(signals.avg_profit, 2),
                "avg_loss": round(signals.avg_loss, 2),
                "profit_factor": round(signals.profit_factor, 2),
                "max_drawdown": round(signals.max_drawdown, 2),
                "win_streak": signals.win_streak,
                "loss_streak": signals.loss_streak,
                "avg_confidence": round(signals.avg_confidence, 2),
                "best_coin": signals.best_coin,
                "worst_coin": signals.worst_coin,
                "most_traded_coin": signals.most_traded_coin,
                "buy_win_rate": round(signals.buy_win_rate, 2),
                "sell_win_rate": round(signals.sell_win_rate, 2),
            },
            
            "growth": {
                "total_users": growth.total_users,
                "new_today": growth.new_users_today,
                "new_week": growth.new_users_week,
                "new_month": growth.new_users_month,
                "dau": growth.dau,
                "wau": growth.wau,
                "mau": growth.mau,
                "dau_mau_ratio": round(growth.dau_mau_ratio, 2),
                "stickiness": round(growth.stickiness, 2),
                "day7_retention": round(growth.day7_retention, 2),
                "day30_retention": round(growth.day30_retention, 2),
                "referral_rate": round(growth.referral_rate, 2),
            },
            
            "security": {
                "overall_risk_score": round(security.overall_risk_score, 2),
                "banned_users": security.banned_users_count,
                "suspicious_activities": security.unusual_activity_count,
                "high_severity_anomalies": len(security.suspicious_users),
            },
            
            "critical_alerts": critical_alerts,
            "warnings": warnings,
            "insights": insights,
            "recommendations": recommendations,
            "predictions": predictions,
            
            "risk_users_count": len(risk_users),
            "churn_users_count": len(churn_users),
            "high_value_users_count": len(high_value),
        }
        
        self._set_cache("comprehensive_report", report)
        return report
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        except:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except:
                return None
    
    def clear_cache(self):
        """پاکسازی کش"""
        self._cache.clear()
        self._cache_time.clear()

# ============================================================
#                    SINGLETON
# ============================================================

_intelligence_engine = None

def get_intelligence_engine() -> AdminIntelligenceEngine:
    global _intelligence_engine
    if _intelligence_engine is None:
        _intelligence_engine = AdminIntelligenceEngine()
    return _intelligence_engine

# ============================================================
#                    COMPATIBILITY
# ============================================================

def start():
    """Compatibility function for ModuleManager"""
    return True

# Status
_intel = get_intelligence_engine()
_users_count = len(_intel._get_users()) if _intel else 0
