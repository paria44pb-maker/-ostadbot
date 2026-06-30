#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Advanced Technical Analysis Module
ماژول تحلیل تکنیکال پیشرفته با ۳۰+ اندیکاتور
پشتیبانی از تایم‌فریم‌های مختلف و سیگنال‌دهی هوشمند
"""

import os
import sys
import json
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# ==================== تنظیمات تحلیل ====================

class TimeFrame(Enum):
    """تایم‌فریم‌های قابل پشتیبانی"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    H8 = "8h"
    H12 = "12h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"

class IndicatorType(Enum):
    """نوع اندیکاتور"""
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    OSCILLATOR = "oscillator"
    CUSTOM = "custom"

@dataclass
class IndicatorResult:
    """نتیجه اندیکاتور"""
    name: str
    value: float
    signal: str  # buy, sell, neutral
    confidence: int  # 0-100
    description: str
    type: IndicatorType

@dataclass
class SupportResistance:
    """سطوح حمایت و مقاومت"""
    support: List[float]
    resistance: List[float]
    pivot: float
    r1: float
    r2: float
    r3: float
    s1: float
    s2: float
    s3: float

@dataclass
class PatternResult:
    """نتیجه الگوی شمعی"""
    name: str
    type: str  # bullish, bearish, neutral
    strength: int  # 0-100
    description: str
    confirmation: bool

# ==================== کلاس اصلی تحلیل تکنیکال ====================

class TechnicalAnalysis:
    """تحلیل تکنیکال پیشرفته با تمام اندیکاتورها"""
    
    def __init__(self):
        self.indicators = {}
        self.patterns = {}
        self._cache = {}
        self._cache_ttl = 60
        
        # تنظیمات پیش‌فرض
        self.default_periods = {
            'sma': 20,
            'ema': 20,
            'rsi': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2,
            'stoch_k': 14,
            'stoch_d': 3,
            'adx': 14,
            'atr': 14,
            'mfi': 14,
            'cci': 20,
            'williams_r': 14,
            'roc': 10,
            'momentum': 10,
            'ichimoku_tenkan': 9,
            'ichimoku_kijun': 26,
            'ichimoku_senkou': 52
        }
    
    # ==================== اندیکاتورهای روند ====================
    
    def calculate_sma(self, data: pd.Series, period: int = 20) -> pd.Series:
        """محاسبه میانگین متحرک ساده (SMA)"""
        return data.rolling(window=period).mean()
    
    def calculate_ema(self, data: pd.Series, period: int = 20) -> pd.Series:
        """محاسبه میانگین متحرک نمایی (EMA)"""
        return data.ewm(span=period, adjust=False).mean()
    
    def calculate_wma(self, data: pd.Series, period: int = 20) -> pd.Series:
        """محاسبه میانگین متحرک وزنی (WMA)"""
        weights = np.arange(1, period + 1)
        return data.rolling(period).apply(
            lambda x: np.sum(weights * x) / np.sum(weights)
        )
    
    def calculate_hma(self, data: pd.Series, period: int = 20) -> pd.Series:
        """محاسبه میانگین متحرک هال (HMA)"""
        half_period = int(period / 2)
        sqrt_period = int(np.sqrt(period))
        
        wma_half = self.calculate_wma(data, half_period)
        wma_full = self.calculate_wma(data, period)
        hma_raw = 2 * wma_half - wma_full
        return self.calculate_wma(hma_raw, sqrt_period)
    
    def calculate_ichimoku(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """محاسبه ابر ایچیموکو"""
        tenkan_period = self.default_periods['ichimoku_tenkan']
        kijun_period = self.default_periods['ichimoku_kijun']
        senkou_period = self.default_periods['ichimoku_senkou']
        
        tenkan_sen = (df['high'].rolling(tenkan_period).max() + 
                     df['low'].rolling(tenkan_period).min()) / 2
        
        kijun_sen = (df['high'].rolling(kijun_period).max() + 
                     df['low'].rolling(kijun_period).min()) / 2
        
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun_period)
        
        senkou_span_b = ((df['high'].rolling(senkou_period).max() + 
                         df['low'].rolling(senkou_period).min()) / 2).shift(kijun_period)
        
        chikou_span = df['close'].shift(-kijun_period)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    # ==================== اندیکاتورهای نوسان‌سنج ====================
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """محاسبه شاخص قدرت نسبی (RSI)"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data: pd.Series) -> Dict[str, pd.Series]:
        """محاسبه MACD"""
        fast = self.default_periods['macd_fast']
        slow = self.default_periods['macd_slow']
        signal = self.default_periods['macd_signal']
        
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_stochastic(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """محاسبه استوکاستیک"""
        k_period = self.default_periods['stoch_k']
        d_period = self.default_periods['stoch_d']
        
        low_min = df['low'].rolling(k_period).min()
        high_max = df['high'].rolling(k_period).max()
        
        stoch_k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        stoch_d = stoch_k.rolling(d_period).mean()
        
        return {
            'k': stoch_k,
            'd': stoch_d
        }
    
    def calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """محاسبه ویلیامز %R"""
        low_min = df['low'].rolling(period).min()
        high_max = df['high'].rolling(period).max()
        return -100 * ((high_max - df['close']) / (high_max - low_min))
    
    def calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """محاسبه شاخص کانال کالا (CCI)"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        return (tp - sma_tp) / (0.015 * mad)
    
    def calculate_mfi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """محاسبه شاخص جریان پول (MFI)"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)
        
        positive_sum = positive_flow.rolling(period).sum()
        negative_sum = negative_flow.rolling(period).sum()
        
        mfi = 100 - (100 / (1 + (positive_sum / negative_sum)))
        return mfi
    
    # ==================== اندیکاتورهای نوسان ====================
    
    def calculate_bollinger_bands(self, data: pd.Series) -> Dict[str, pd.Series]:
        """محاسبه باند بولینگر"""
        period = self.default_periods['bb_period']
        std_dev = self.default_periods['bb_std']
        
        middle = data.rolling(period).mean()
        std = data.rolling(period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'width': upper - lower,
            'position': (data - lower) / (upper - lower)
        }
    
    def calculate_keltner_channels(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """محاسبه کانال کلتنر"""
        period = 20
        atr = self.calculate_atr(df, period)
        
        ema = df['close'].ewm(span=period, adjust=False).mean()
        
        return {
            'upper': ema + (atr * 1.5),
            'middle': ema,
            'lower': ema - (atr * 1.5)
        }
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """محاسبه میانگین محدوده واقعی (ATR)"""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(period).mean()
    
    # ==================== اندیکاتورهای حجم ====================
    
    def calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """محاسبه تعادل حجم (OBV)"""
        return (df['volume'] * np.where(df['close'] > df['close'].shift(), 1, 
                                       -1 if df['close'] < df['close'].shift() else 0)).cumsum()
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """محاسبه میانگین وزنی قیمت حجم (VWAP)"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        return (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    
    def calculate_money_flow(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """محاسبه جریان پول"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        positive = money_flow.where(typical_price > typical_price.shift(), 0)
        negative = money_flow.where(typical_price < typical_price.shift(), 0)
        
        return {
            'positive': positive,
            'negative': negative,
            'net': positive - negative
        }
    
    # ==================== اندیکاتورهای پیشرفته ====================
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """محاسبه شاخص جهت‌دار میانگین (ADX)"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = abs(minus_dm)
        
        tr = self.calculate_atr(df, period)
        
        plus_di = 100 * (plus_dm.rolling(period).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / tr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        return dx.rolling(period).mean()
    
    def calculate_roc(self, data: pd.Series, period: int = 10) -> pd.Series:
        """محاسبه نرخ تغییر (ROC)"""
        return ((data - data.shift(period)) / data.shift(period)) * 100
    
    def calculate_momentum(self, data: pd.Series, period: int = 10) -> pd.Series:
        """محاسبه مومنتوم"""
        return data - data.shift(period)
    
    def calculate_chandelier_exit(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """محاسبه خروج شاندلیر"""
        atr = self.calculate_atr(df, 22)
        
        return {
            'long': df['high'].rolling(22).max() - (atr * 3),
            'short': df['low'].rolling(22).min() + (atr * 3)
        }
    
    # ==================== الگوهای شمعی ====================
    
    def detect_doji(self, df: pd.DataFrame) -> pd.Series:
        """تشخیص الگوی دوجی"""
        body = abs(df['close'] - df['open'])
        range_high_low = df['high'] - df['low']
        return body <= (range_high_low * 0.1)
    
    def detect_hammer(self, df: pd.DataFrame) -> pd.Series:
        """تشخیص الگوی چکش"""
        body = abs(df['close'] - df['open'])
        lower_wick = df['low'].where(df['close'] > df['open'], df['open']) - df['low']
        upper_wick = df['high'] - df['high'].where(df['close'] > df['open'], df['close'])
        
        return (lower_wick > body * 2) & (upper_wick < body * 0.5) & (body > 0)
    
    def detect_shooting_star(self, df: pd.DataFrame) -> pd.Series:
        """تشخیص الگوی ستاره دنباله‌دار"""
        body = abs(df['close'] - df['open'])
        upper_wick = df['high'] - df['high'].where(df['close'] > df['open'], df['close'])
        lower_wick = df['low'].where(df['close'] > df['open'], df['open']) - df['low']
        
        return (upper_wick > body * 2) & (lower_wick < body * 0.5) & (body > 0)
    
    def detect_engulfing(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """تشخیص الگوی پوشایی"""
        bullish_engulfing = (
            (df['close'] > df['open']) &
            (df['close'].shift() < df['open'].shift()) &
            (df['close'] > df['open'].shift()) &
            (df['open'] < df['close'].shift())
        )
        
        bearish_engulfing = (
            (df['close'] < df['open']) &
            (df['close'].shift() > df['open'].shift()) &
            (df['close'] < df['open'].shift()) &
            (df['open'] > df['close'].shift())
        )
        
        return {
            'bullish': bullish_engulfing,
            'bearish': bearish_engulfing
        }
    
    def detect_harami(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """تشخیص الگوی هارامی"""
        body1 = abs(df['close'].shift() - df['open'].shift())
        body2 = abs(df['close'] - df['open'])
        
        bullish_harami = (
            (df['close'].shift() < df['open'].shift()) &
            (df['close'] > df['open']) &
            (body2 < body1 * 0.5) &
            (df['close'] < df['open'].shift()) &
            (df['open'] > df['close'].shift())
        )
        
        bearish_harami = (
            (df['close'].shift() > df['open'].shift()) &
            (df['close'] < df['open']) &
            (body2 < body1 * 0.5) &
            (df['close'] > df['open'].shift()) &
            (df['open'] < df['close'].shift())
        )
        
        return {
            'bullish': bullish_harami,
            'bearish': bearish_harami
        }
    
    def detect_three_white_soldiers(self, df: pd.DataFrame) -> pd.Series:
        """تشخیص الگوی سه سرباز سفید"""
        return (
            (df['close'] > df['open']) &
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['close'].shift(2) > df['open'].shift(2)) &
            (df['close'] > df['close'].shift(1)) &
            (df['close'].shift(1) > df['close'].shift(2)) &
            (df['open'] > df['open'].shift(1)) &
            (df['open'].shift(1) > df['open'].shift(2))
        )
    
    def detect_three_black_crows(self, df: pd.DataFrame) -> pd.Series:
        """تشخیص الگوی سه کلاغ سیاه"""
        return (
            (df['close'] < df['open']) &
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'].shift(2) < df['open'].shift(2)) &
            (df['close'] < df['close'].shift(1)) &
            (df['close'].shift(1) < df['close'].shift(2)) &
            (df['open'] < df['open'].shift(1)) &
            (df['open'].shift(1) < df['open'].shift(2))
        )
    
    # ==================== سطوح حمایت و مقاومت ====================
    
    def calculate_support_resistance(self, df: pd.DataFrame) -> SupportResistance:
        """محاسبه سطوح حمایت و مقاومت"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # نقاط محوری
        pivot = (high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3
        
        r1 = (2 * pivot) - low.iloc[-1]
        r2 = pivot + (high.iloc[-1] - low.iloc[-1])
        r3 = r1 + (high.iloc[-1] - low.iloc[-1])
        
        s1 = (2 * pivot) - high.iloc[-1]
        s2 = pivot - (high.iloc[-1] - low.iloc[-1])
        s3 = s1 - (high.iloc[-1] - low.iloc[-1])
        
        # حمایت و مقاومت پویا
        supports = [s1, s2, s3]
        resistances = [r1, r2, r3]
        
        # اضافه کردن SMAها به عنوان سطوح
        sma_50 = df['close'].rolling(50).mean().iloc[-1]
        sma_200 = df['close'].rolling(200).mean().iloc[-1]
        
        if not np.isnan(sma_50):
            if sma_50 < close.iloc[-1]:
                supports.append(sma_50)
            else:
                resistances.append(sma_50)
        
        if not np.isnan(sma_200):
            if sma_200 < close.iloc[-1]:
                supports.append(sma_200)
            else:
                resistances.append(sma_200)
        
        return SupportResistance(
            support=supports,
            resistance=resistances,
            pivot=pivot,
            r1=r1, r2=r2, r3=r3,
            s1=s1, s2=s2, s3=s3
        )
    
    # ==================== تحلیل کامل ====================
    
    def analyze_full(self, df: pd.DataFrame) -> Dict[str, Any]:
        """تحلیل کامل تکنیکال با تمام اندیکاتورها"""
        if df.empty or len(df) < 50:
            return {
                'error': 'داده‌های کافی نیست',
                'signal': 'hold',
                'confidence': 0
            }
        
        # محاسبه همه اندیکاتورها
        df = self.calculate_all_indicators(df)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # جمع‌آوری سیگنال‌ها
        signals = {
            'buy': 0,
            'sell': 0,
            'neutral': 0
        }
        
        results = []
        
        # RSI
        rsi_signal = self._analyze_rsi(latest['rsi'])
        results.append(rsi_signal)
        signals[rsi_signal['signal']] += 1
        
        # MACD
        macd_signal = self._analyze_macd(latest['macd'], latest['macd_signal'])
        results.append(macd_signal)
        signals[macd_signal['signal']] += 1
        
        # باند بولینگر
        bb_signal = self._analyze_bollinger_bands(
            latest['close'],
            latest['bb_upper'],
            latest['bb_lower'],
            latest['bb_position']
        )
        results.append(bb_signal)
        signals[bb_signal['signal']] += 1
        
        # استوکاستیک
        stoch_signal = self._analyze_stochastic(latest['stoch_k'], latest['stoch_d'])
        results.append(stoch_signal)
        signals[stoch_signal['signal']] += 1
        
        # ADX
        adx_signal = self._analyze_adx(latest['adx'])
        results.append(adx_signal)
        signals[adx_signal['signal']] += 1
        
        # MFI
        mfi_signal = self._analyze_mfi(latest['mfi'])
        results.append(mfi_signal)
        signals[mfi_signal['signal']] += 1
        
        # CCI
        cci_signal = self._analyze_cci(latest['cci'])
        results.append(cci_signal)
        signals[cci_signal['signal']] += 1
        
        # ویلیامز %R
        williams_signal = self._analyze_williams_r(latest['williams_r'])
        results.append(williams_signal)
        signals[williams_signal['signal']] += 1
        
        # میانگین متحرک
        sma_signal = self._analyze_sma(latest['sma_7'], latest['sma_25'], latest['sma_50'])
        results.append(sma_signal)
        signals[sma_signal['signal']] += 1
        
        # تصمیم نهایی
        if signals['buy'] > signals['sell']:
            final_signal = 'buy'
        elif signals['sell'] > signals['buy']:
            final_signal = 'sell'
        else:
            final_signal = 'neutral'
        
        # محاسبه اطمینان
        total = signals['buy'] + signals['sell'] + signals['neutral']
        if total > 0:
            confidence = int((max(signals['buy'], signals['sell']) / total) * 100)
        else:
            confidence = 50
        
        # سطوح حمایت و مقاومت
        sr = self.calculate_support_resistance(df)
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'signals': results,
            'support_resistance': sr,
            'latest': latest.to_dict(),
            'buy_count': signals['buy'],
            'sell_count': signals['sell'],
            'neutral_count': signals['neutral'],
            'total_indicators': len(results)
        }
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """محاسبه همه اندیکاتورها روی دیتافریم"""
        # میانگین متحرک
        df['sma_7'] = self.calculate_sma(df['close'], 7)
        df['sma_25'] = self.calculate_sma(df['close'], 25)
        df['sma_50'] = self.calculate_sma(df['close'], 50)
        df['sma_99'] = self.calculate_sma(df['close'], 99)
        df['sma_200'] = self.calculate_sma(df['close'], 200)
        
        df['ema_9'] = self.calculate_ema(df['close'], 9)
        df['ema_12'] = self.calculate_ema(df['close'], 12)
        df['ema_21'] = self.calculate_ema(df['close'], 21)
        df['ema_26'] = self.calculate_ema(df['close'], 26)
        df['ema_50'] = self.calculate_ema(df['close'], 50)
        
        # RSI
        df['rsi'] = self.calculate_rsi(df['close'])
        df['rsi_7'] = self.calculate_rsi(df['close'], 7)
        df['rsi_21'] = self.calculate_rsi(df['close'], 21)
        
        # MACD
        macd = self.calculate_macd(df['close'])
        df['macd'] = macd['macd']
        df['macd_signal'] = macd['signal']
        df['macd_histogram'] = macd['histogram']
        
        # بولینگر
        bb = self.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb['upper']
        df['bb_middle'] = bb['middle']
        df['bb_lower'] = bb['lower']
        df['bb_width'] = bb['width']
        df['bb_position'] = bb['position']
        
        # استوکاستیک
        stoch = self.calculate_stochastic(df)
        df['stoch_k'] = stoch['k']
        df['stoch_d'] = stoch['d']
        
        # ADX
        df['adx'] = self.calculate_adx(df)
        
        # ATR
        df['atr'] = self.calculate_atr(df)
        
        # MFI
        df['mfi'] = self.calculate_mfi(df)
        
        # CCI
        df['cci'] = self.calculate_cci(df)
        
        # ویلیامز %R
        df['williams_r'] = self.calculate_williams_r(df)
        
        # ROC
        df['roc'] = self.calculate_roc(df['close'])
        
        # مومنتوم
        df['momentum'] = self.calculate_momentum(df['close'])
        
        # OBV
        df['obv'] = self.calculate_obv(df)
        
        # VWAP
        df['vwap'] = self.calculate_vwap(df)
        
        # ایچیموکو
        ichimoku = self.calculate_ichimoku(df)
        df['tenkan_sen'] = ichimoku['tenkan_sen']
        df['kijun_sen'] = ichimoku['kijun_sen']
        df['senkou_span_a'] = ichimoku['senkou_span_a']
        df['senkou_span_b'] = ichimoku['senkou_span_b']
        df['chikou_span'] = ichimoku['chikou_span']
        
        # کلتنر
        keltner = self.calculate_keltner_channels(df)
        df['kc_upper'] = keltner['upper']
        df['kc_middle'] = keltner['middle']
        df['kc_lower'] = keltner['lower']
        
        return df
    
    # ==================== تحلیل‌های سیگنال ====================
    
    def _analyze_rsi(self, rsi: float) -> IndicatorResult:
        """تحلیل سیگنال RSI"""
        if rsi < 30:
            return IndicatorResult(
                name='RSI',
                value=rsi,
                signal='buy',
                confidence=90,
                description='اشباع فروش - سیگنال خرید قوی',
                type=IndicatorType.OSCILLATOR
            )
        elif rsi < 40:
            return IndicatorResult(
                name='RSI',
                value=rsi,
                signal='buy',
                confidence=70,
                description='نزدیک اشباع فروش - سیگنال خرید',
                type=IndicatorType.OSCILLATOR
            )
        elif rsi > 70:
            return IndicatorResult(
                name='RSI',
                value=rsi,
                signal='sell',
                confidence=90,
                description='اشباع خرید - سیگنال فروش قوی',
                type=IndicatorType.OSCILLATOR
            )
        elif rsi > 60:
            return IndicatorResult(
                name='RSI',
                value=rsi,
                signal='sell',
                confidence=70,
                description='نزدیک اشباع خرید - سیگنال فروش',
                type=IndicatorType.OSCILLATOR
            )
        else:
            return IndicatorResult(
                name='RSI',
                value=rsi,
                signal='neutral',
                confidence=50,
                description='منطقه خنثی',
                type=IndicatorType.OSCILLATOR
            )
    
    def _analyze_macd(self, macd: float, signal: float) -> IndicatorResult:
        """تحلیل سیگنال MACD"""
        if macd > signal:
            return IndicatorResult(
                name='MACD',
                value=macd - signal,
                signal='buy',
                confidence=75,
                description='MACD بالای سیگنال - سیگنال خرید',
                type=IndicatorType.MOMENTUM
            )
        else:
            return IndicatorResult(
                name='MACD',
                value=macd - signal,
                signal='sell',
                confidence=75,
                description='MACD پایین‌تر از سیگنال - سیگنال فروش',
                type=IndicatorType.MOMENTUM
            )
    
    def _analyze_bollinger_bands(
        self,
        price: float,
        upper: float,
        lower: float,
        position: float
    ) -> IndicatorResult:
        """تحلیل سیگنال باند بولینگر"""
        if position < 0.1:
            return IndicatorResult(
                name='Bollinger Bands',
                value=position,
                signal='buy',
                confidence=85,
                description='قیمت پایین‌تر از باند پایین - فرصت خرید عالی',
                type=IndicatorType.VOLATILITY
            )
        elif position < 0.3:
            return IndicatorResult(
                name='Bollinger Bands',
                value=position,
                signal='buy',
                confidence=65,
                description='قیمت نزدیک باند پایین - منطقه خرید',
                type=IndicatorType.VOLATILITY
            )
        elif position > 0.9:
            return IndicatorResult(
                name='Bollinger Bands',
                value=position,
                signal='sell',
                confidence=85,
                description='قیمت بالاتر از باند بالا - منطقه فروش',
                type=IndicatorType.VOLATILITY
            )
        elif position > 0.7:
            return IndicatorResult(
                name='Bollinger Bands',
                value=position,
                signal='sell',
                confidence=65,
                description='قیمت نزدیک باند بالا - منطقه فروش',
                type=IndicatorType.VOLATILITY
            )
        else:
            return IndicatorResult(
                name='Bollinger Bands',
                value=position,
                signal='neutral',
                confidence=50,
                description='قیمت در محدوده میانی باند',
                type=IndicatorType.VOLATILITY
            )
    
    def _analyze_stochastic(self, k: float, d: float) -> IndicatorResult:
        """تحلیل سیگنال استوکاستیک"""
        if k < 20 and k > d:
            return IndicatorResult(
                name='Stochastic',
                value=k,
                signal='buy',
                confidence=80,
                description='اشباع فروش و در حال افزایش - خرید',
                type=IndicatorType.OSCILLATOR
            )
        elif k > 80 and k < d:
            return IndicatorResult(
                name='Stochastic',
                value=k,
                signal='sell',
                confidence=80,
                description='اشباع خرید و در حال کاهش - فروش',
                type=IndicatorType.OSCILLATOR
            )
        else:
            return IndicatorResult(
                name='Stochastic',
                value=k,
                signal='neutral',
                confidence=50,
                description='منطقه خنثی',
                type=IndicatorType.OSCILLATOR
            )
    
    def _analyze_adx(self, adx: float) -> IndicatorResult:
        """تحلیل سیگنال ADX"""
        if adx > 40:
            return IndicatorResult(
                name='ADX',
                value=adx,
                signal='buy',
                confidence=80,
                description='روند بسیار قوی - مناسب برای معامله',
                type=IndicatorType.TREND
            )
        elif adx > 25:
            return IndicatorResult(
                name='ADX',
                value=adx,
                signal='neutral',
                confidence=60,
                description='روند قوی - قابل معامله',
                type=IndicatorType.TREND
            )
        else:
            return IndicatorResult(
                name='ADX',
                value=adx,
                signal='neutral',
                confidence=40,
                description='روند ضعیف - احتیاط',
                type=IndicatorType.TREND
            )
    
    def _analyze_mfi(self, mfi: float) -> IndicatorResult:
        """تحلیل سیگنال MFI"""
        if mfi < 20:
            return IndicatorResult(
                name='MFI',
                value=mfi,
                signal='buy',
                confidence=85,
                description='اشباع فروش - سیگنال خرید',
                type=IndicatorType.VOLUME
            )
        elif mfi > 80:
            return IndicatorResult(
                name='MFI',
                value=mfi,
                signal='sell',
                confidence=85,
                description='اشباع خرید - سیگنال فروش',
                type=IndicatorType.VOLUME
            )
        else:
            return IndicatorResult(
                name='MFI',
                value=mfi,
                signal='neutral',
                confidence=50,
                description='منطقه خنثی',
                type=IndicatorType.VOLUME
            )
    
    def _analyze_cci(self, cci: float) -> IndicatorResult:
        """تحلیل سیگنال CCI"""
        if cci < -100:
            return IndicatorResult(
                name='CCI',
                value=cci,
                signal='buy',
                confidence=80,
                description='اشباع فروش - سیگنال خرید',
                type=IndicatorType.OSCILLATOR
            )
        elif cci > 100:
            return IndicatorResult(
                name='CCI',
                value=cci,
                signal='sell',
                confidence=80,
                description='اشباع خرید - سیگنال فروش',
                type=IndicatorType.OSCILLATOR
            )
        else:
            return IndicatorResult(
                name='CCI',
                value=cci,
                signal='neutral',
                confidence=50,
                description='منطقه خنثی',
                type=IndicatorType.OSCILLATOR
            )
    
    def _analyze_williams_r(self, williams_r: float) -> IndicatorResult:
        """تحلیل سیگنال ویلیامز %R"""
        if williams_r < -80:
            return IndicatorResult(
                name='Williams %R',
                value=williams_r,
                signal='buy',
                confidence=80,
                description='اشباع فروش - سیگنال خرید',
                type=IndicatorType.OSCILLATOR
            )
        elif williams_r > -20:
            return IndicatorResult(
                name='Williams %R',
                value=williams_r,
                signal='sell',
                confidence=80,
                description='اشباع خرید - سیگنال فروش',
                type=IndicatorType.OSCILLATOR
            )
        else:
            return IndicatorResult(
                name='Williams %R',
                value=williams_r,
                signal='neutral',
                confidence=50,
                description='منطقه خنثی',
                type=IndicatorType.OSCILLATOR
            )
    
    def _analyze_sma(self, sma_7: float, sma_25: float, sma_50: float) -> IndicatorResult:
        """تحلیل سیگنال میانگین متحرک"""
        if sma_7 > sma_25 > sma_50:
            return IndicatorResult(
                name='SMA',
                value=sma_7,
                signal='buy',
                confidence=70,
                description='روند صعودی قوی - سیگنال خرید',
                type=IndicatorType.TREND
            )
        elif sma_7 < sma_25 < sma_50:
            return IndicatorResult(
                name='SMA',
                value=sma_7,
                signal='sell',
                confidence=70,
                description='روند نزولی قوی - سیگنال فروش',
                type=IndicatorType.TREND
            )
        elif sma_7 > sma_25:
            return IndicatorResult(
                name='SMA',
                value=sma_7,
                signal='buy',
                confidence=55,
                description='روند صعودی کوتاه‌مدت',
                type=IndicatorType.TREND
            )
        elif sma_7 < sma_25:
            return IndicatorResult(
                name='SMA',
                value=sma_7,
                signal='sell',
                confidence=55,
                description='روند نزولی کوتاه‌مدت',
                type=IndicatorType.TREND
            )
        else:
            return IndicatorResult(
                name='SMA',
                value=sma_7,
                signal='neutral',
                confidence=50,
                description='روند خنثی',
                type=IndicatorType.TREND
            )

# ==================== Export ====================

technical_analysis = TechnicalAnalysis()

def get_technical() -> TechnicalAnalysis:
    return technical_analysis
