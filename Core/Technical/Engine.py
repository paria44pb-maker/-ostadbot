import pandas as pd
import pandas_ta as ta
import numpy as np
from config.settings import TIMEFRAMES

class TechnicalEngine:
    def __init__(self, df):
        self.df = df.copy()
        self.scores = {'BUY': 0, 'SELL': 0}
        self.signals = []

    def calculate_all_indicators(self):
        # روند (Trend)
        self.df['EMA20'] = ta.ema(self.df['close'], length=20)
        self.df['EMA50'] = ta.ema(self.df['close'], length=50)
        self.df['EMA200'] = ta.ema(self.df['close'], length=200)
        self.df['SMA50'] = ta.sma(self.df['close'], length=50)
        self.df['SMA200'] = ta.sma(self.df['close'], length=200)
        self.df['ADX'] = ta.adx(self.df['high'], self.df['low'], self.df['close'])[f'ADX_14']
        self.df['ICHIMOKU_A'] = ta.ichimoku(self.df['high'], self.df['low'])[0]['ISA_9']
        self.df['SUPERTREND'] = ta.supertrend(self.df['high'], self.df['low'], self.df['close'])[f'SUPERT_7_3']
        
        # اسیلاتورها (Oscillators)
        self.df['RSI'] = ta.rsi(self.df['close'], length=14)
        self.df['STOCH_RSI_K'] = ta.stochrsi(self.df['close'])[f'STOCHRSIk_14_14_3_3']
        self.df['CCI'] = ta.cci(self.df['high'], self.df['low'], self.df['close'], length=20)
        self.df['MACD'] = ta.macd(self.df['close'])[f'MACD_12_26_9']
        self.df['MACD_SIGNAL'] = ta.macd(self.df['close'])[f'MACDs_12_26_9']
        self.df['WILLIAMS_R'] = ta.willr(self.df['high'], self.df['low'], self.df['close'], length=14)
        self.df['MFI'] = ta.mfi(self.df['high'], self.df['low'], self.df['close'], self.df['volume'], length=14)
        
        # حجم (Volume)
        self.df['OBV'] = ta.obv(self.df['close'], self.df['volume'])
        self.df['CMF'] = ta.cmf(self.df['high'], self.df['low'], self.df['close'], self.df['volume'], length=20)
        self.df['VWAP'] = ta.vwap(self.df['high'], self.df['low'], self.df['close'], self.df['volume'])
        
        # نوسان (Volatility)
        self.df['BB_UPPER'], self.df['BB_MIDDLE'], self.df['BB_LOWER'] = ta.bbands(self.df['close'], length=20, std=2)
        self.df['ATR'] = ta.atr(self.df['high'], self.df['low'], self.df['close'], length=14)
        
        # دیگر اندیکاتورها
        self.df['KELTNER_UPPER'], self.df['KELTNER_MIDDLE'], self.df['KELTNER_LOWER'] = ta.kc(self.df['high'], self.df['low'], self.df['close'], length=20)
        self.df['DONCHIAN_HIGH'] = ta.donchian(self.df['high'], lower_length=20, upper_length=20)['DCHIGH_20_20']
        self.df['DONCHIAN_LOW'] = ta.donchian(self.df['low'], lower_length=20, upper_length=20)['DCLOW_20_20']
        self.df['PIVOT'] = (self.df['high'].rolling(20).max() + self.df['low'].rolling(20).min()) / 2
        
        return self.df

    def score_indicators(self):
        last = self.df.iloc[-1]
        
        # RSI
        if last['RSI'] < 30:
            self.scores['BUY'] += 30
            self.signals.append(("RSI", "BUY", 30, f"RSI oversold ({last['RSI']:.0f})"))
        elif last['RSI'] > 70:
            self.scores['SELL'] += 30
            self.signals.append(("RSI", "SELL", 30, f"RSI overbought ({last['RSI']:.0f})"))
        
        # MACD
        if last['MACD'] > last['MACD_SIGNAL']:
            self.scores['BUY'] += 25
            self.signals.append(("MACD", "BUY", 25, "MACD bullish crossover"))
        else:
            self.scores['SELL'] += 25
            self.signals.append(("MACD", "SELL", 25, "MACD bearish crossover"))
        
        # EMA ترتیبی
        if last['EMA20'] > last['EMA50'] > last['EMA200']:
            self.scores['BUY'] += 20
            self.signals.append(("EMA", "BUY", 20, "Golden order (EMA20>EMA50>EMA200)"))
        elif last['EMA20'] < last['EMA50'] < last['EMA200']:
            self.scores['SELL'] += 20
            self.signals.append(("EMA", "SELL", 20, "Death order (EMA20<EMA50<EMA200)"))
        
        # باند بولینگر
        if last['close'] <= last['BB_LOWER']:
            self.scores['BUY'] += 20
            self.signals.append(("Bollinger", "BUY", 20, "Price at lower band"))
        elif last['close'] >= last['BB_UPPER']:
            self.scores['SELL'] += 20
            self.signals.append(("Bollinger", "SELL", 20, "Price at upper band"))
        
        # استوکاستیک RSI
        if last['STOCH_RSI_K'] < 20:
            self.scores['BUY'] += 15
            self.signals.append(("StochRSI", "BUY", 15, "Oversold"))
        elif last['STOCH_RSI_K'] > 80:
            self.scores['SELL'] += 15
            self.signals.append(("StochRSI", "SELL", 15, "Overbought"))
        
        # CCI
        if last['CCI'] < -100:
            self.scores['BUY'] += 15
            self.signals.append(("CCI", "BUY", 15, "Oversold"))
        elif last['CCI'] > 100:
            self.scores['SELL'] += 15
            self.signals.append(("CCI", "SELL", 15, "Overbought"))
        
        # ویلیامز %R
        if last['WILLIAMS_R'] < -80:
            self.scores['BUY'] += 10
            self.signals.append(("Williams", "BUY", 10, "Oversold"))
        elif last['WILLIAMS_R'] > -20:
            self.scores['SELL'] += 10
            self.signals.append(("Williams", "SELL", 10, "Overbought"))
        
        # ADX (قدرت روند)
        if last['ADX'] > 25:
            if self.scores['BUY'] > self.scores['SELL']:
                self.scores['BUY'] += 15
                self.signals.append(("ADX", "BUY", 15, f"Strong uptrend (ADX:{last['ADX']:.0f})"))
            else:
                self.scores['SELL'] += 15
                self.signals.append(("ADX", "SELL", 15, f"Strong downtrend (ADX:{last['ADX']:.0f})"))
        
        # MFI
        if last['MFI'] < 20:
            self.scores['BUY'] += 15
            self.signals.append(("MFI", "BUY", 15, "Money flow oversold"))
        elif last['MFI'] > 80:
            self.scores['SELL'] += 15
            self.signals.append(("MFI", "SELL", 15, "Money flow overbought"))
        
        # OBV
        if len(self.df) > 1 and self.df['OBV'].iloc[-1] > self.df['OBV'].iloc[-2]:
            self.scores['BUY'] += 10
            self.signals.append(("OBV", "BUY", 10, "Accumulation"))
        else:
            self.scores['SELL'] += 10
            self.signals.append(("OBV", "SELL", 10, "Distribution"))
        
        # تغییر قیمت
        change = (last['close'] - self.df['close'].iloc[-2]) / self.df['close'].iloc[-2] * 100
        if change > 2:
            self.scores['BUY'] += 15
            self.signals.append(("Price", "BUY", 15, f"Strong pump {change:+.1f}%"))
        elif change < -2:
            self.scores['SELL'] += 15
            self.signals.append(("Price", "SELL", 15, f"Strong dump {change:+.1f}%"))
        
        # حجم
        volume_ma = self.df['volume'].rolling(20).mean().iloc[-1]
        if self.df['volume'].iloc[-1] > volume_ma * 1.5:
            if self.scores['BUY'] > self.scores['SELL']:
                self.scores['BUY'] += 10
                self.signals.append(("Volume", "BUY", 10, "High volume confirming uptrend"))
            else:
                self.scores['SELL'] += 10
                self.signals.append(("Volume", "SELL", 10, "High volume confirming downtrend"))
        
        # ابر ایچیموکو
        if last['close'] > last['ICHIMOKU_A']:
            self.scores['BUY'] += 10
            self.signals.append(("Ichimoku", "BUY", 10, "Price above cloud"))
        else:
            self.scores['SELL'] += 10
            self.signals.append(("Ichimoku", "SELL", 10, "Price below cloud"))
        
        # سوپرترند
        if last['SUPERTREND'] < last['close']:
            self.scores['BUY'] += 10
            self.signals.append(("Supertrend", "BUY", 10, "Bullish"))
        else:
            self.scores['SELL'] += 10
            self.signals.append(("Supertrend", "SELL", 10, "Bearish"))
        
        total = self.scores['BUY'] - self.scores['SELL']
        return total, self.scores, self.signals
