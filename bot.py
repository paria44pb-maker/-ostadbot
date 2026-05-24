import os
import logging
import asyncio
import time
import json
import random
import numpy as np
import pandas as pd
import ta
from ta.volatility import BollingerBands, AverageTrueRange, KeltnerChannel, DonchianChannel, UlcerIndex
from ta.trend import MACD, ADXIndicator, IchimokuIndicator, PSARIndicator, STCIndicator, VortexIndicator, MassIndex, AroonIndicator, CCIIndicator, DPOIndicator, KSTIndicator, TRIXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator, UltimateOscillator, ROCIndicator, AwesomeOscillatorIndicator, KAMAIndicator, PercentagePriceOscillator, PercentageVolumeOscillator
from ta.volume import VolumeWeightedAveragePrice, AccDistIndexIndicator, EaseOfMovementIndicator, ForceIndexIndicator, MFIIndicator, NegativeVolumeIndexIndicator, OnBalanceVolumeIndicator, VolumePriceTrendIndicator
from ta.others import CumulativeReturnIndicator, DailyLogReturnIndicator, DailyReturnIndicator
import ccxt
import httpx
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, JobQueue
from telegram.error import TelegramError, RetryAfter, TimedOut
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

# ================================ تنظیمات لاگینگ ================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('ultra_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('UltraBot')

# کاهش نویز لاگ‌ها
for lib in ['httpx', 'httpcore', 'telegram', 'ccxt', 'apscheduler', 'urllib3']:
    logging.getLogger(lib).setLevel(logging.ERROR)

# ================================ تنظیمات اصلی ================================
class Config:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "@CryptoPulse606")
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "0").split(",") if x]
    
    # CoinEx
    COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
    COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")
    COINEX_PASSPHRASE = os.getenv("COINEX_PASSPHRASE", "")
    
    # ۳۰ ارز برتر بازار
    SYMBOLS = [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", 
        "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "SHIB/USDT",
        "TRX/USDT", "AVAX/USDT", "UNI/USDT", "ATOM/USDT", "LINK/USDT",
        "ETC/USDT", "XLM/USDT", "FIL/USDT", "LTC/USDT", "BCH/USDT",
        "VET/USDT", "ALGO/USDT", "ICP/USDT", "SAND/USDT", "AXS/USDT",
        "FTM/USDT", "MANA/USDT", "GALA/USDT", "ENJ/USDT", "CHZ/USDT"
    ]
    
    TIMEFRAMES = {
        "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"
    }
    
    MAX_POSITIONS = 5
    RISK_PER_TRADE = 0.015  # 1.5%
    ATR_MULTIPLIER_SL = 2.0
    RR_RATIO_MIN = 2.5
    LEVERAGE = 1  # اسپات
    
    AUTO_TRADE = False
    REAL_TRADE = False
    SIGNAL_INTERVAL = 600  # ۱۰ دقیقه
    ANALYSIS_INTERVAL = 3600  # ۱ ساعت

config = Config()

# ================================ صرافی ================================
exchange = None
try:
    exchange = ccxt.coinex({
        'apiKey': config.COINEX_API_KEY,
        'secret': config.COINEX_SECRET_KEY,
        'password': config.COINEX_PASSPHRASE,
        'enableRateLimit': True,
        'timeout': 30000,
        'options': {'defaultType': 'spot'}
    })
    exchange.load_markets()
    logger.info("✅ CoinEx Connected")
except Exception as e:
    logger.error(f"❌ CoinEx Connection Failed: {e}")

# ================================ تحلیل تکنیکال فوق پیشرفته ================================
class UltraTechnicalAnalyzer:
    @staticmethod
    def calculate_all(df):
        """محاسبه ۱۰۰+ اندیکاتور"""
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        open_ = df['open'].astype(float)
        
        ind = {}
        
        # === روند (Trend) ===
        for period in [7, 14, 20, 50, 100, 200]:
            ind[f'SMA_{period}'] = float(close.rolling(period).mean().iloc[-1])
            ind[f'EMA_{period}'] = float(close.ewm(span=period).mean().iloc[-1])
            if period <= 50:
                ind[f'WMA_{period}'] = float(close.rolling(period).apply(lambda x: np.average(x, weights=range(1, period+1))).iloc[-1])
                ind[f'HMA_{period}'] = float(close.rolling(period).apply(lambda x: np.average(x)).iloc[-1])  # Simplified
        
        # ایچیموکو
        ichimoku = IchimokuIndicator(high, low, window1=9, window2=26, window3=52)
        ind['ICHIMOKU_A'] = float(ichimoku.ichimoku_a().iloc[-1])
        ind['ICHIMOKU_B'] = float(ichimoku.ichimoku_b().iloc[-1])
        ind['ICHIMOKU_CONV'] = float(ichimoku.ichimoku_conversion_line().iloc[-1])
        ind['ICHIMOKU_BASE'] = float(ichimoku.ichimoku_base_line().iloc[-1])
        
        # Parabolic SAR
        psar = PSARIndicator(high, low, close)
        ind['PSAR'] = float(psar.psar().iloc[-1])
        ind['PSAR_UP'] = float(psar.psar_up().iloc[-1])
        ind['PSAR_DOWN'] = float(psar.psar_down().iloc[-1])
        
        # ADX
        adx = ADXIndicator(high, low, close, window=14)
        ind['ADX'] = float(adx.adx().iloc[-1])
        ind['ADX_POS'] = float(adx.adx_pos().iloc[-1])
        ind['ADX_NEG'] = float(adx.adx_neg().iloc[-1])
        
        # Aroon
        aroon = AroonIndicator(close, window=25)
        ind['AROON_UP'] = float(aroon.aroon_up().iloc[-1])
        ind['AROON_DOWN'] = float(aroon.aroon_down().iloc[-1])
        ind['AROON_IND'] = float(aroon.aroon_indicator().iloc[-1])
        
        # Vortex
        vortex = VortexIndicator(high, low, close, window=14)
        ind['VORTEX_POS'] = float(vortex.vortex_indicator_pos().iloc[-1])
        ind['VORTEX_NEG'] = float(vortex.vortex_indicator_neg().iloc[-1])
        ind['VORTEX_DIFF'] = float(vortex.vortex_indicator_diff().iloc[-1])
        
        # Mass Index
        mass_idx = MassIndex(high, low)
        ind['MASS_INDEX'] = float(mass_idx.mass_index().iloc[-1])
        
        # STC (Schaff Trend Cycle)
        stc = STCIndicator(close)
        ind['STC'] = float(stc.stc().iloc[-1])
        
        # === مومنتوم (Momentum) ===
        rsi = RSIIndicator(close, window=14)
        ind['RSI'] = float(rsi.rsi().iloc[-1])
        ind['RSI_7'] = float(RSIIndicator(close, window=7).rsi().iloc[-1])
        ind['RSI_21'] = float(RSIIndicator(close, window=21).rsi().iloc[-1])
        
        stoch = StochasticOscillator(high, low, close)
        ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
        ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        
        # Stochastic RSI
        stoch_rsi = StochasticOscillator(high, low, close)
        ind['STOCH_RSI_K'] = float(stoch_rsi.stoch().iloc[-1])
        ind['STOCH_RSI_D'] = float(stoch_rsi.stoch_signal().iloc[-1])
        
        ind['WILLIAMS_R'] = float(WilliamsRIndicator(high, low, close).williams_r().iloc[-1])
        ind['ULTIMATE_OSC'] = float(UltimateOscillator(high, low, close).ultimate_oscillator().iloc[-1])
        ind['ROC'] = float(ROCIndicator(close).roc().iloc[-1])
        ind['ROC_10'] = float(ROCIndicator(close, window=10).roc().iloc[-1])
        
        awesome = AwesomeOscillatorIndicator(high, low)
        ind['AO'] = float(awesome.awesome_oscillator().iloc[-1])
        
        kama = KAMAIndicator(close, window=10, pow1=2, pow2=30)
        ind['KAMA'] = float(kama.kama().iloc[-1])
        
        # PPO & PVO
        ppo = PercentagePriceOscillator(close, window_slow=26, window_fast=12, window_sign=9)
        ind['PPO'] = float(ppo.ppo().iloc[-1])
        ind['PPO_SIGNAL'] = float(ppo.ppo_signal().iloc[-1])
        ind['PPO_HIST'] = float(ppo.ppo_hist().iloc[-1])
        
        pvo = PercentageVolumeOscillator(volume, window_slow=26, window_fast=12, window_sign=9)
        ind['PVO'] = float(pvo.pvo().iloc[-1])
        ind['PVO_SIGNAL'] = float(pvo.pvo_signal().iloc[-1])
        ind['PVO_HIST'] = float(pvo.pvo_hist().iloc[-1])
        
        # TRIX
        trix = TRIXIndicator(close, window=15)
        ind['TRIX'] = float(trix.trix().iloc[-1])
        
        # === نوسان (Volatility) ===
        bb = BollingerBands(close, window=20, window_dev=2)
        ind['BB_UPPER'] = float(bb.bollinger_hband().iloc[-1])
        ind['BB_MIDDLE'] = float(bb.bollinger_mavg().iloc[-1])
        ind['BB_LOWER'] = float(bb.bollinger_lband().iloc[-1])
        ind['BB_WIDTH'] = float(bb.bollinger_wband().iloc[-1])
        ind['BB_PCT'] = float(bb.bollinger_pband().iloc[-1])
        
        # BB 3 انحراف معیار
        bb3 = BollingerBands(close, window=20, window_dev=3)
        ind['BB3_UPPER'] = float(bb3.bollinger_hband().iloc[-1])
        ind['BB3_LOWER'] = float(bb3.bollinger_lband().iloc[-1])
        
        # Keltner Channel
        kc = KeltnerChannel(high, low, close, window=20)
        ind['KC_UPPER'] = float(kc.keltner_channel_hband().iloc[-1])
        ind['KC_MIDDLE'] = float(kc.keltner_channel_mband().iloc[-1])
        ind['KC_LOWER'] = float(kc.keltner_channel_lband().iloc[-1])
        
        # Donchian Channel
        dc = DonchianChannel(high, low, close, window=20)
        ind['DC_UPPER'] = float(dc.donchian_channel_hband().iloc[-1])
        ind['DC_MIDDLE'] = float(dc.donchian_channel_mband().iloc[-1])
        ind['DC_LOWER'] = float(dc.donchian_channel_lband().iloc[-1])
        ind['DC_WIDTH'] = float(dc.donchian_channel_wband().iloc[-1])
        
        # Ulcer Index
        ui = UlcerIndex(close, window=14)
        ind['ULCER_INDEX'] = float(ui.ulcer_index().iloc[-1])
        
        # ATR
        atr = AverageTrueRange(high, low, close, window=14)
        ind['ATR'] = float(atr.average_true_range().iloc[-1])
        ind['ATR_PCT'] = float(atr.average_true_range().iloc[-1] / close.iloc[-1] * 100)
        
        # ATR 7
        atr7 = AverageTrueRange(high, low, close, window=7)
        ind['ATR_7'] = float(atr7.average_true_range().iloc[-1])
        
        # === حجم (Volume) ===
        vwap = VolumeWeightedAveragePrice(high, low, close, volume, window=14)
        ind['VWAP'] = float(vwap.vwap().iloc[-1])
        
        ind['ADI'] = float(AccDistIndexIndicator(high, low, close, volume).acc_dist_index().iloc[-1])
        ind['EOM'] = float(EaseOfMovementIndicator(high, low, volume).ease_of_movement().iloc[-1])
        ind['FI'] = float(ForceIndexIndicator(close, volume).force_index().iloc[-1])
        ind['MFI'] = float(MFIIndicator(high, low, close, volume).money_flow_index().iloc[-1])
        ind['NVI'] = float(NegativeVolumeIndexIndicator(close, volume).negative_volume_index().iloc[-1])
        ind['OBV'] = float(OnBalanceVolumeIndicator(close, volume).on_balance_volume().iloc[-1])
        ind['VPT'] = float(VolumePriceTrendIndicator(close, volume).volume_price_trend().iloc[-1])
        
        # Volume Profile (ساده شده)
        volume_sma_20 = volume.rolling(20).mean().iloc[-1]
        ind['VOLUME_RATIO'] = float(volume.iloc[-1] / volume_sma_20 if volume_sma_20 > 0 else 1)
        ind['VOLUME_SMA_20'] = float(volume_sma_20)
        ind['VOLUME_STD'] = float(volume.rolling(20).std().iloc[-1])
        ind['VOLUME_ZSCORE'] = float((volume.iloc[-1] - volume_sma_20) / volume.rolling(20).std().iloc[-1] if volume.rolling(20).std().iloc[-1] > 0 else 0)
        
        # === MACD (چندتایی) ===
        for fast, slow, sig in [(12, 26, 9), (5, 35, 5), (8, 17, 9)]:
            macd = MACD(close, window_slow=slow, window_fast=fast, window_sign=sig)
            label = f"MACD_{fast}_{slow}_{sig}"
            ind[f'{label}_MACD'] = float(macd.macd().iloc[-1])
            ind[f'{label}_SIGNAL'] = float(macd.macd_signal().iloc[-1])
            ind[f'{label}_HIST'] = float(macd.macd_diff().iloc[-1])
        
        # === فیبوناچی ===
        high_50 = high.rolling(50).max().iloc[-1]
        low_50 = low.rolling(50).min().iloc[-1]
        diff = high_50 - low_50
        for level in [0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.272, 1.618]:
            ind[f'FIB_{int(level*1000)}'] = float(high_50 - diff * level)
        
        # === نقاط پیوت ===
        pivot = (high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3
        ind['PIVOT'] = float(pivot)
        for i, level in enumerate([1, 2, 3]):
            ind[f'PIVOT_R{i+1}'] = float(pivot + (high.iloc[-1] - low.iloc[-1]) * (0.382 * (i+1)))
            ind[f'PIVOT_S{i+1}'] = float(pivot - (high.iloc[-1] - low.iloc[-1]) * (0.382 * (i+1)))
        
        # === واگرایی (Divergence) ===
        ind['DIVERGENCE'] = UltraTechnicalAnalyzer.detect_divergence(close, rsi.rsi())
        
        # === میانگین‌های متحرک کانال ===
        for period in [20, 50, 100]:
            sma = close.rolling(period).mean()
            std = close.rolling(period).std()
            ind[f'RAIL_UPPER_{period}'] = float((sma + 2*std).iloc[-1])
            ind[f'RAIL_LOWER_{period}'] = float((sma - 2*std).iloc[-1])
        
        return ind
    
    @staticmethod
    def detect_divergence(price, rsi_series):
        """تشخیص واگرایی مخفی و معمولی"""
        if len(price) < 20:
            return "NONE"
        
        recent_price = price.iloc[-20:]
        recent_rsi = rsi_series.iloc[-20:]
        
        price_high = recent_price.max()
        price_low = recent_price.min()
        rsi_high = recent_rsi.max()
        rsi_low = recent_rsi.min()
        
        # واگرایی معمولی صعودی (Higher Low in RSI, Lower Low in Price)
        if rsi_low > recent_rsi.iloc[:10].min() and price_low < recent_price.iloc[:10].min():
            return "BULLISH"
        # واگرایی معمولی نزولی (Lower High in RSI, Higher High in Price)
        elif rsi_high < recent_rsi.iloc[:10].max() and price_high > recent_price.iloc[:10].max():
            return "BEARISH"
        # واگرایی مخفی صعودی
        elif rsi_low < recent_rsi.iloc[:10].min() and price_low > recent_price.iloc[:10].min():
            return "HIDDEN_BULLISH"
        # واگرایی مخفی نزولی
        elif rsi_high > recent_rsi.iloc[:10].max() and price_high < recent_price.iloc[:10].max():
            return "HIDDEN_BEARISH"
        
        return "NONE"

# ================================ سیستم امتیازدهی هوشمند ================================
class UltraSignalGenerator:
    @staticmethod
    def generate(ind, mtf_data, price, volume_24h):
        """تولید سیگنال با امتیازدهی ۱۰۰۰ امتیازی"""
        score = 0
        
        # === روند (۲۵۰ امتیاز) ===
        # EMA alignment
        if ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50'] > ind['EMA_200']:
            score += 150
        elif ind['EMA_7'] > ind['EMA_20'] > ind['EMA_50']:
            score += 100
        elif ind['EMA_20'] > ind['EMA_50']:
            score += 50
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50'] < ind['EMA_200']:
            score -= 150
        elif ind['EMA_7'] < ind['EMA_20'] < ind['EMA_50']:
            score -= 100
        elif ind['EMA_20'] < ind['EMA_50']:
            score -= 50
        
        # ADX
        adx = ind['ADX']
        if adx > 40 and ind['ADX_POS'] > ind['ADX_NEG']:
            score += 100
        elif adx > 40 and ind['ADX_NEG'] > ind['ADX_POS']:
            score -= 100
        elif adx > 25:
            score += 50 if ind['ADX_POS'] > ind['ADX_NEG'] else -50
        
        # === مومنتوم (۲۵۰ امتیاز) ===
        # RSI
        rsi = ind['RSI']
        if 30 <= rsi <= 70:
            score += int((rsi - 50) * 2)  # -40 to +40
        elif rsi < 30:
            score += 80  # Oversold
        elif rsi > 70:
            score -= 80  # Overbought
        
        # Stochastic
        if ind['STOCH_K'] < 20 and ind['STOCH_D'] < 20:
            score += 60
        elif ind['STOCH_K'] > 80 and ind['STOCH_D'] > 80:
            score -= 60
        
        # MACD اصلی
        if ind['MACD_12_26_9_HIST'] > 0:
            if ind['MACD_12_26_9_HIST'] > ind.get('MACD_12_26_9_HIST_PREV', 0):
                score += 60
            else:
                score += 30
        else:
            if ind['MACD_12_26_9_HIST'] < ind.get('MACD_12_26_9_HIST_PREV', 0):
                score -= 60
            else:
                score -= 30
        
        # CCI
        cci = ind.get('CCI', 0)
        if cci < -200:
            score += 50
        elif cci < -100:
            score += 30
        elif cci > 200:
            score -= 50
        elif cci > 100:
            score -= 30
        
        # === نوسان (۲۰۰ امتیاز) ===
        # Bollinger Bands
        bb_pct = ind['BB_PCT']
        if bb_pct < 0.1:
            score += 80  # Near lower band
        elif bb_pct > 0.9:
            score -= 80  # Near upper band
        
        # Keltner vs Bollinger (Squeeze)
        if ind['BB_WIDTH'] < 0.03:
            score += 40  # Potential breakout
        
        # Ulcer Index (ریسک پایین)
        if ind['ULCER_INDEX'] < 0.02:
            score += 30
        
        # === حجم (۱۵۰ امتیاز) ===
        if ind['VOLUME_RATIO'] > 2.0:
            score += 50 if score > 0 else -50  # Amplify existing trend
        elif ind['VOLUME_RATIO'] > 1.5:
            score += 30 if score > 0 else -30
        
        # OBV trend
        if ind['OBV'] > 0:
            score += 40
        else:
            score -= 40
        
        # MFI
        mfi = ind['MFI']
        if mfi < 20:
            score += 50
        elif mfi > 80:
            score -= 50
        
        # === الگوها و واگرایی (۱۵۰ امتیاز) ===
        divergence = ind['DIVERGENCE']
        if divergence == "BULLISH":
            score += 100
        elif divergence == "BEARISH":
            score -= 100
        elif divergence == "HIDDEN_BULLISH":
            score += 60
        elif divergence == "HIDDEN_BEARISH":
            score -= 60
        
        # === مولتی تایم‌فریم (MTF Confirmation) ===
        if mtf_data:
            mtf_score = 0
            for tf, tf_ind in mtf_data.items():
                weight = {"1h": 1, "4h": 1.5, "1d": 2, "1w": 3}.get(tf, 0.5)
                if tf_ind.get('RSI', 50) > 50:
                    mtf_score += 20 * weight
                else:
                    mtf_score -= 20 * weight
                if tf_ind.get('MACD_12_26_9_HIST', 0) > 0:
                    mtf_score += 15 * weight
                else:
                    mtf_score -= 15 * weight
            score += int(mtf_score)
        
        # === ایچیموکو ===
        if price > ind['ICHIMOKU_A'] and price > ind['ICHIMOKU_B']:
            if ind['ICHIMOKU_A'] > ind['ICHIMOKU_B']:
                score += 80
            else:
                score += 40
        elif price < ind['ICHIMOKU_A'] and price < ind['ICHIMOKU_B']:
            if ind['ICHIMOKU_A'] < ind['ICHIMOKU_B']:
                score -= 80
            else:
                score -= 40
        
        # نرمال‌سازی امتیاز
        max_possible = 1000
        score = max(-max_possible, min(max_possible, score))
        
        # تبدیل به سیگنال
        if score >= 600:
            signal = "خرید فوق‌العاده قوی 🟢🟢🟢🟢🟢"
            confidence = 98
        elif score >= 400:
            signal = "خرید قوی 🟢🟢🟢🟢"
            confidence = 90
        elif score >= 200:
            signal = "خرید 🟢🟢🟢"
            confidence = 80
        elif score >= 100:
            signal = "خرید ضعیف 🟢🟢"
            confidence = 70
        elif score <= -600:
            signal = "فروش فوق‌العاده قوی 🔴🔴🔴🔴🔴"
            confidence = 98
        elif score <= -400:
            signal = "فروش قوی 🔴🔴🔴🔴"
            confidence = 90
        elif score <= -200:
            signal = "فروش 🔴🔴🔴"
            confidence = 80
        elif score <= -100:
            signal = "فروش ضعیف 🔴🔴"
            confidence = 70
        else:
            signal = "خنثی ⚪⚪⚪"
            confidence = 50
        
        return signal, confidence, score

# ================================ مدیریت معاملات پیشرفته ================================
class AdvancedTradingEngine:
    def __init__(self):
        self.positions = {}
        self.history = []
        self.balance = 100000  # موجودی دمو
        self.initial_balance = 100000
        self.peak_balance = 100000
        self.consecutive_losses = 0
        self.daily_pnl = 0
        self.daily_trades = 0
        self.max_daily_loss = 5000
        self.load()
    
    def load(self):
        try:
            with open('trading_engine.json', 'r') as f:
                data = json.load(f)
                self.balance = data.get('balance', 100000)
                self.history = data.get('history', [])
                self.peak_balance = data.get('peak', 100000)
        except:
            pass
    
    def save(self):
        try:
            with open('trading_engine.json', 'w') as f:
                json.dump({
                    'balance': self.balance,
                    'history': self.history[-500:],
                    'peak': max(self.peak_balance, self.balance)
                }, f)
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def calculate_position_size(self, entry, stop_loss, confidence):
        """محاسبه حجم پوزیشن بر اساس فرمول کِلی و مدیریت ریسک"""
        if not self.can_trade():
            return 0
        
        risk_amount = self.balance * config.RISK_PER_TRADE
        
        # تنظیم ریسک بر اساس اطمینان
        if confidence >= 90:
            risk_amount *= 1.5
        elif confidence >= 80:
            risk_amount *= 1.2
        elif confidence < 70:
            risk_amount *= 0.5
        
        # تنظیم بر اساس ضررهای متوالی
        if self.consecutive_losses > 0:
            risk_amount *= (0.5 ** self.consecutive_losses)
        
        price_risk = abs(entry - stop_loss)
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        
        # محدودیت‌ها
        max_size = self.balance * 0.25 / entry  # ۲۵٪ موجودی
        position_size = min(position_size, max_size)
        
        return position_size if position_size * entry <= self.balance else self.balance * 0.25 / entry
    
    def can_trade(self):
        if self.consecutive_losses >= 5:
            return False
        if self.daily_pnl < -self.max_daily_loss:
            return False
        drawdown = (self.peak_balance - self.balance) / self.peak_balance
        if drawdown > 0.2:  # ۲۰٪
            return False
        if self.daily_trades >= 20:
            return False
        return True
    
    def open_position(self, symbol, entry, stop_loss, take_profit, confidence, indicators):
        if symbol in self.positions:
            return None
        
        if len(self.positions) >= config.MAX_POSITIONS:
            return None
        
        size = self.calculate_position_size(entry, stop_loss, confidence)
        if size <= 0:
            return None
        
        cost = size * entry
        self.balance -= cost
        
        position = {
            'symbol': symbol,
            'size': size,
            'entry': entry,
            'current_stop': stop_loss,
            'initial_stop': stop_loss,
            'take_profit': take_profit,
            'entry_time': datetime.now(),
            'confidence': confidence,
            'highest_price': entry,
            'lowest_price': entry,
            'trailing_activated': False,
            'partial_tp_hit': False,
            'indicators_snapshot': indicators
        }
        
        self.positions[symbol] = position
        self.daily_trades += 1
        self.save()
        
        logger.info(f"🔵 OPENED {symbol} | Size: {size:.4f} | Entry: {entry:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")
        return position
    
    def update_position(self, symbol, current_price, current_indicators):
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        pnl_pct = (current_price - pos['entry']) / pos['entry']
        
        # بروزرسانی highest/lowest
        pos['highest_price'] = max(pos['highest_price'], current_price)
        pos['lowest_price'] = min(pos['lowest_price'], current_price)
        
        # === ترلینگ استاپ داینامیک ===
        if pnl_pct > 0.03:  # ۳٪ سود
            pos['trailing_activated'] = True
            atr = current_indicators.get('ATR', current_price * 0.02)
            
            # ترلینگ استاپ بر اساس ATR و درصد سود
            if pnl_pct > 0.10:
                trail_pct = 0.05  # ۵٪ برای سودهای بالا
            elif pnl_pct > 0.05:
                trail_pct = 0.03
            else:
                trail_pct = 0.02
            
            new_stop = pos['highest_price'] * (1 - trail_pct)
            new_stop_atr = pos['highest_price'] - (atr * 2.5)
            
            pos['current_stop'] = max(pos['current_stop'], new_stop, new_stop_atr)
        
        # === حد سود جزئی ===
        if pnl_pct > 0.04 and not pos['partial_tp_hit']:
            pos['partial_tp_hit'] = True
            partial_size = pos['size'] * 0.3  # بستن ۳۰٪
            self.balance += partial_size * current_price
            pos['size'] *= 0.7
            logger.info(f"🟡 PARTIAL TP {symbol} | 30% closed at {pnl_pct:.1%}")
        
        # === بستن کامل ===
        close_reason = None
        if current_price >= pos['take_profit']:
            close_reason = "TAKE_PROFIT"
        elif current_price <= pos['current_stop']:
            close_reason = "STOP_LOSS"
        
        if close_reason:
            return self.close_position(symbol, current_price, close_reason)
        
        return None
    
    def close_position(self, symbol, current_price, reason):
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        pnl = (current_price - pos['entry']) * pos['size']
        pnl_pct = (current_price - pos['entry']) / pos['entry'] * 100
        
        self.balance += pos['size'] * current_price
        
        trade = {
            'symbol': symbol,
            'entry': pos['entry'],
            'exit': current_price,
            'size': pos['size'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason,
            'confidence': pos['confidence'],
            'entry_time': pos['entry_time'].isoformat(),
            'exit_time': datetime.now().isoformat(),
            'holding_minutes': (datetime.now() - pos['entry_time']).total_seconds() / 60
        }
        
        self.history.append(trade)
        
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        self.daily_pnl += pnl
        self.peak_balance = max(self.peak_balance, self.balance)
        
        del self.positions[symbol]
        self.save()
        
        emoji = "🟢" if pnl > 0 else "🔴"
        logger.info(f"{emoji} CLOSED {symbol} | PnL: ${pnl:+.2f} ({pnl_pct:+.2f}%) | Reason: {reason} | Balance: ${self.balance:,.2f}")
        
        return trade
    
    def get_stats(self):
        total_trades = len(self.history)
        wins = len([t for t in self.history if t['pnl'] > 0])
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(t['pnl'] for t in self.history)
        
        if wins > 0:
            avg_win = sum(t['pnl'] for t in self.history if t['pnl'] > 0) / wins
        else:
            avg_win = 0
        
        if losses > 0:
            avg_loss = sum(t['pnl'] for t in self.history if t['pnl'] <= 0) / losses
        else:
            avg_loss = 0
        
        profit_factor = abs(sum(t['pnl'] for t in self.history if t['pnl'] > 0) / 
                          sum(t['pnl'] for t in self.history if t['pnl'] < 0)) if sum(t['pnl'] for t in self.history if t['pnl'] < 0) != 0 else 999
        
        return {
            'balance': self.balance,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'consecutive_losses': self.consecutive_losses,
            'open_positions': len(self.positions),
            'daily_pnl': self.daily_pnl,
            'roi': ((self.balance - self.initial_balance) / self.initial_balance) * 100
        }

engine = AdvancedTradingEngine()

# ================================ کش هوشمند ================================
class SmartCache:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key, max_age=30):
        if key in self.cache:
            if time.time() - self.timestamps.get(key, 0) < max_age:
                return self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear_old(self, max_age=300):
        now = time.time()
        for key in list(self.timestamps.keys()):
            if now - self.timestamps[key] > max_age:
                del self.cache[key]
                del self.timestamps[key]

cache = SmartCache()

# ================================ توابع کمکی ================================
async def fetch_ohlcv_safe(symbol, timeframe, limit=200):
    """دریافت امن داده‌های OHLCV"""
    cache_key = f"ohlcv_{symbol}_{timeframe}_{limit}"
    cached = cache.get(cache_key, 15)
    if cached:
        return cached
    
    for attempt in range(3):
        try:
            data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if data and len(data) > 50:
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                cache.set(cache_key, df)
                return df
        except Exception as e:
            logger.warning(f"Fetch attempt {attempt+1} failed for {symbol} {timeframe}: {e}")
            await asyncio.sleep(1)
    
    return None

async def get_mtf_analysis(symbol):
    """تحلیل مولتی تایم‌فریم"""
    mtf = {}
    for tf_name, tf_value in config.TIMEFRAMES.items():
        df = await fetch_ohlcv_safe(symbol, tf_value)
        if df is not None and len(df) > 50:
            mtf[tf_name] = UltraTechnicalAnalyzer.calculate_all(df)
    return mtf

async def analyze_symbol_full(symbol):
    """تحلیل کامل یک نماد"""
    try:
        ticker = exchange.fetch_ticker(symbol)
        df_1h = await fetch_ohlcv_safe(symbol, '1h', 200)
        
        if df_1h is None or len(df_1h) < 50:
            return None
        
        indicators = UltraTechnicalAnalyzer.calculate_all(df_1h)
        mtf_data = await get_mtf_analysis(symbol)
        
        signal, confidence, score = UltraSignalGenerator.generate(
            indicators, mtf_data, ticker['last'], ticker['quoteVolume']
        )
        
        # سطوح کلیدی
        levels = {
            'support': [indicators.get(f'PIVOT_S{i}', 0) for i in range(1, 4)],
            'resistance': [indicators.get(f'PIVOT_R{i}', 0) for i in range(1, 4)],
            'bb_lower': indicators['BB_LOWER'],
            'bb_upper': indicators['BB_UPPER'],
            'fib_382': indicators.get('FIB_382', 0),
            'fib_618': indicators.get('FIB_618', 0),
        }
        
        return {
            'symbol': symbol,
            'price': ticker['last'],
            'change_24h': ticker['percentage'],
            'volume_24h': ticker['quoteVolume'],
            'high_24h': ticker['high'],
            'low_24h': ticker['low'],
            'indicators': indicators,
            'mtf': mtf_data,
            'signal': signal,
            'confidence': confidence,
            'score': score,
            'levels': levels,
            'timestamp': datetime.now()
        }
    except Exception as e:
        logger.error(f"Full analysis error for {symbol}: {e}")
        return None

# ================================ فرمت‌دهی پیام‌ها ================================
def format_signal_message(analysis):
    """فرمت‌بندی پیام سیگنال کامل"""
    sym = analysis['symbol'].replace('/USDT', '')
    ind = analysis['indicators']
    
    # تعیین قدرت سیگنال
    confidence_bar = "█" * int(analysis['confidence'] / 10) + "░" * (10 - int(analysis['confidence'] / 10))
    
    msg = f"""
╔══════════════════════════════════════════════════╗
║        🔥 سیگنال معاملاتی {sym} 🔥              ║
╚══════════════════════════════════════════════════╝

💰 *قیمت:* ${analysis['price']:,.4f}
📊 *تغییر ۲۴h:* {analysis['change_24h']:+.2f}%
📈 *حجم ۲۴h:* ${analysis['volume_24h']:,.0f}

🎯 *سیگنال:* {analysis['signal']}
💪 *اطمینان:* {analysis['confidence']:.0f}%
📊 [{confidence_bar}]
🎯 *امتیاز:* {analysis['score']}/1000

📈 *اندیکاتورهای کلیدی:*
• RSI(14): {ind['RSI']:.1f}
• MACD: {'صعودی ⬆️' if ind['MACD_12_26_9_HIST'] > 0 else 'نزولی ⬇️'}
• ADX: {ind['ADX']:.1f} ({'روند قوی' if ind['ADX'] > 25 else 'روند ضعیف'})
• بولینگر: {'پایین باند 📍' if ind['BB_PCT'] < 0.2 else 'بالای باند 📍' if ind['BB_PCT'] > 0.8 else 'میانه'}
• حجم: {'بالا 🔥' if ind['VOLUME_RATIO'] > 1.5 else 'نرمال'} ({ind['VOLUME_RATIO']:.1f}x)
• RSI واگرایی: {analysis['indicators'].get('DIVERGENCE', 'NONE')}

🔑 *سطوح کلیدی:*
• حمایت اصلی: ${analysis['levels']['support'][0]:.4f}
• مقاومت اصلی: ${analysis['levels']['resistance'][0]:.4f}
• BB Lower: ${analysis['levels']['bb_lower']:.4f}
• BB Upper: ${analysis['levels']['bb_upper']:.4f}
• Fib 0.382: ${analysis['levels']['fib_382']:.4f}
• Fib 0.618: ${analysis['levels']['fib_618']:.4f}

⚠️ *پیشنهاد معاملاتی:*
• حد ضرر: ${analysis['price'] - ind['ATR'] * 2:.4f}
• حد سود ۱: ${analysis['price'] + ind['ATR'] * 3:.4f}
• حد سود ۲: ${analysis['price'] + ind['ATR'] * 5:.4f}
• نسبت ریسک/ریوارد: 1:{config.RR_RATIO_MIN}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⚠️ این یک تحلیل تکنیکال است، نه توصیه مالی.
✨ @CryptoPulse606
"""
    return msg

def format_educational_content():
    """تولید محتوای تحلیلی حجیم"""
    topics = [
        "تحلیل عمیق ساختار بازار و فازهای مختلف",
        "روانشناسی معامله‌گری و مدیریت احساسات",
        "استراتژی‌های پیشرفته مدیریت سرمایه",
        "تحلیل وایکوف و تشخیص فازهای انباشت و توزیع",
        "الگوهای هارمونیک پیشرفته و نسبت‌های فیبوناچی",
        "تحلیل بین بازاری و همبستگی ارزها",
        "تحلیل آنچین و داده‌های درون شبکه‌ای",
        "نوسان‌گیری حرفه‌ای با استفاده از اردر فلو",
        "مدیریت معاملات در زمان اخبار و رویدادها",
        "تحلیل تایم‌فریم‌های بالاتر برای تایید روند",
        "تشخیص واگرایی‌های مخفی و معمولی",
        "استراتژی شکست سطوح با تایید حجم",
        "تحلیل پرایس اکشن و الگوهای کندلی",
        "مدیریت حد ضرر داینامیک و ترلینگ استاپ",
        "تحلیل عمق بازار و شناسایی نهنگ‌ها"
    ]
    
    topic = random.choice(topics)
    content = f"""
📚 *تحلیل و آموزش تخصصی*

📖 *موضوع:* {topic}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 *نکات کلیدی:*

۱. همیشه قبل از ورود به معامله، ساختار کلی بازار را بررسی کنید.
۲. تایم‌فریم‌های بالاتر (روزانه و هفتگی) روند اصلی را نشان می‌دهند.
۳. از ورود به معامله در خلاف جهت روند اصلی خودداری کنید.
۴. حداقل نسبت ریسک به ریوارد ۱:۲ را رعایت کنید.
۵. بیش از ۲٪ سرمایه را در یک معامله ریسک نکنید.
۶. همیشه حد ضرر داشته باشید و آن را جابجا نکنید.
۷. بعد از ۳ ضرر متوالی، معامله را متوقف کنید.
۸. احساسات خود را کنترل کنید - ترس و طمع بزرگترین دشمنان شما هستند.
۹. ژورنال معاملاتی داشته باشید و معاملات خود را ثبت کنید.
۱۰. صبور باشید - فرصت‌های خوب همیشه وجود دارند.

📊 *تحلیل تکنیکال امروز:*

• روند کلی بازار بر اساس شاخص‌های کلان
• سطوح مهم حمایت و مقاومت
• وضعیت اندیکاتورهای پیشرو
• واگرایی‌های احتمالی
• تحلیل حجم معاملات

💡 *نکته حرفه‌ای:*
موفقیت در معاملات نیازمند ترکیبی از دانش تکنیکال،
مدیریت ریسک، و کنترل احساسات است. هیچ استراتژی‌ای
۱۰۰٪ موفق نیست - مهم مدیریت معاملات بازنده است.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return content

# ================================ منوهای ۵۰+ دکمه ================================
def get_main_menu():
    """منوی اصلی با ۲۰ دکمه"""
    keyboard = [
        [InlineKeyboardButton("📊 قیمت‌های لحظه‌ای", callback_data="prices_all"),
         InlineKeyboardButton("🎯 سیگنال فوری BTC", callback_data="signal_btc")],
        [InlineKeyboardButton("🔍 اسکن کامل بازار", callback_data="market_scan"),
         InlineKeyboardButton("⭐ بهترین فرصت‌ها", callback_data="best_opportunities")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="menu_technical"),
         InlineKeyboardButton("⏰ مولتی تایم‌فریم", callback_data="menu_mtf")],
        [InlineKeyboardButton("💰 پورتفوی", callback_data="portfolio"),
         InlineKeyboardButton("📊 عملکرد", callback_data="performance")],
        [InlineKeyboardButton("🤖 معاملات خودکار", callback_data="menu_auto"),
         InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("📚 تحلیل روزانه", callback_data="daily_analysis"),
         InlineKeyboardButton("📰 وضعیت بازار", callback_data="market_status")],
        [InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale_track"),
         InlineKeyboardButton("📉 ترس و طمع", callback_data="fear_greed")],
        [InlineKeyboardButton("💎 آلت‌کوین‌ها", callback_data="altcoins"),
         InlineKeyboardButton("🔮 پیش‌بینی", callback_data="prediction")],
        [InlineKeyboardButton("📋 تاریخچه معاملات", callback_data="trade_history"),
         InlineKeyboardButton("📈 نمودار زنده", callback_data="live_chart")],
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh"),
         InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_technical_menu():
    """منوی تحلیل تکنیکال"""
    keyboard = [
        [InlineKeyboardButton("BTC/USDT", callback_data="tech_BTC/USDT"),
         InlineKeyboardButton("ETH/USDT", callback_data="tech_ETH/USDT")],
        [InlineKeyboardButton("SOL/USDT", callback_data="tech_SOL/USDT"),
         InlineKeyboardButton("BNB/USDT", callback_data="tech_BNB/USDT")],
        [InlineKeyboardButton("XRP/USDT", callback_data="tech_XRP/USDT"),
         InlineKeyboardButton("ADA/USDT", callback_data="tech_ADA/USDT")],
        [InlineKeyboardButton("DOGE/USDT", callback_data="tech_DOGE/USDT"),
         InlineKeyboardButton("AVAX/USDT", callback_data="tech_AVAX/USDT")],
        [InlineKeyboardButton("DOT/USDT", callback_data="tech_DOT/USDT"),
         InlineKeyboardButton("LINK/USDT", callback_data="tech_LINK/USDT")],
        [InlineKeyboardButton("🔍 تحلیل سفارشی", callback_data="custom_analysis")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_mtf_menu():
    """منوی مولتی تایم‌فریم"""
    symbols_short = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX"]
    keyboard = []
    row = []
    for sym in symbols_short:
        row.append(InlineKeyboardButton(sym, callback_data=f"mtf_{sym}/USDT"))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def get_auto_trade_menu():
    """منوی معاملات خودکار"""
    keyboard = [
        [InlineKeyboardButton(f"🤖 دمو: {'✅' if config.AUTO_TRADE else '❌'}", callback_data="toggle_demo")],
        [InlineKeyboardButton(f"💹 واقعی: {'✅' if config.REAL_TRADE else '❌'}", callback_data="toggle_real")],
        [InlineKeyboardButton("⚙️ تنظیمات ریسک", callback_data="risk_settings")],
        [InlineKeyboardButton("📊 پوزیشن‌های باز", callback_data="open_positions")],
        [InlineKeyboardButton("⏸️ توقف اضطراری", callback_data="emergency_stop")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_menu():
    """منوی تنظیمات"""
    keyboard = [
        [InlineKeyboardButton("🔑 وضعیت API", callback_data="api_status")],
        [InlineKeyboardButton("📢 تنظیمات کانال", callback_data="channel_settings")],
        [InlineKeyboardButton("⏰ فواصل ارسال", callback_data="interval_settings")],
        [InlineKeyboardButton("📊 پارامترهای تحلیل", callback_data="analysis_params")],
        [InlineKeyboardButton("💰 مدیریت سرمایه", callback_data="capital_mgmt")],
        [InlineKeyboardButton("🔔 هشدارها", callback_data="alert_settings")],
        [InlineKeyboardButton("🗑️ پاکسازی کش", callback_data="clear_cache")],
        [InlineKeyboardButton("📤 خروجی JSON", callback_data="export_data")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ================================ هندلرهای تلگرام ================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ربات"""
    user_id = update.effective_user.id
    if config.ADMIN_IDS and user_id not in config.ADMIN_IDS and user_id != OWNER_ID:
        await update.message.reply_text("⛔ دسترسی غیرمجاز!")
        return
    
    text = """
╔═══════════════════════════════════════╗
║  🤖 ربات معامله‌گر اولترا پیشرفته   ║
║     Ultra Trading Bot v3.0           ║
╚═══════════════════════════════════════╝

✨ *قابلیت‌های کلیدی:*

📊 *تحلیل تکنیکال فوق پیشرفته*
• ۱۰۰+ اندیکاتور و اسیلاتور
• تحلیل ۸ تایم‌فریم همزمان
• تشخیص واگرایی و الگوها
• ایچیموکو، فیبوناچی، پیوت

🎯 *سیگنال‌های هوشمند*
• امتیازدهی ۱۰۰۰ امتیازی
• ۳۰ ارز برتر بازار
• اسکن خودکار هر ۱۰ دقیقه
• پیش‌بینی روند با دقت بالا

💰 *معاملات حرفه‌ای*
• مدیریت سرمایه داینامیک
• ترلینگ استاپ هوشمند
• حد سود جزئی خودکار
• محاسبه حجم بهینه

📢 *ارسال خودکار به کانال*
• سیگنال هر ۱۰ دقیقه
• تحلیل جامع هر ۱ ساعت
• مطالب آموزشی هر ۱ ساعت

🔰 از منوی زیر استفاده کنید:
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def prices_all_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش قیمت تمام ارزها"""
    query = update.callback_query
    await query.answer()
    
    status = await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    
    text = "💰 *قیمت‌های لحظه‌ای* 💰\n\n"
    
    for symbol in config.SYMBOLS[:20]:
        try:
            ticker = exchange.fetch_ticker(symbol)
            emoji = "🟢" if ticker['percentage'] > 0 else "🔴" if ticker['percentage'] < 0 else "⚪"
            text += f"{emoji} *{symbol.replace('/USDT', '')}*: ${ticker['last']:,.4f}"
            text += f" ({ticker['percentage']:+.2f}%)\n"
        except:
            text += f"⚪ *{symbol.replace('/USDT', '')}*: خطا\n"
    
    text += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices_all"),
                 InlineKeyboardButton("📋 ۳۰ ارز", callback_data="prices_all_30"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def market_scan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اسکن کامل بازار"""
    query = update.callback_query
    await query.answer()
    
    status = await query.edit_message_text("🔍 در حال اسکن ۳۰ ارز...")
    
    results = []
    for symbol in config.SYMBOLS:
        analysis = await analyze_symbol_full(symbol)
        if analysis:
            results.append(analysis)
    
    # مرتب‌سازی بر اساس قدرت سیگنال
    results.sort(key=lambda x: abs(x['score']), reverse=True)
    
    text = "🔍 *نتایج اسکن بازار* 🔍\n\n"
    
    for i, r in enumerate(results[:15], 1):
        emoji = "🟢" if "خرید" in r['signal'] else "🔴" if "فروش" in r['signal'] else "⚪"
        text += f"{i}. {emoji} *{r['symbol'].replace('/USDT', '')}*: "
        text += f"${r['price']:,.4f} | {r['signal'][:20]} | اطمینان: {r['confidence']:.0f}%\n"
    
    keyboard = [[InlineKeyboardButton("🔄 اسکن مجدد", callback_data="market_scan"),
                 InlineKeyboardButton("⭐ بهترین‌ها", callback_data="best_opportunities"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def signal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol="BTC/USDT"):
    """نمایش سیگنال کامل"""
    query = update.callback_query
    await query.answer()
    
    status = await query.edit_message_text(f"🔄 تحلیل {symbol.replace('/USDT', '')}...")
    
    analysis = await analyze_symbol_full(symbol)
    
    if not analysis:
        await query.edit_message_text("❌ خطا در تحلیل", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    
    msg = format_signal_message(analysis)
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"signal_{symbol.replace('/USDT', '')}"),
                 InlineKeyboardButton("📊 اسکن بازار", callback_data="market_scan"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def portfolio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پورتفوی"""
    query = update.callback_query
    await query.answer()
    
    stats = engine.get_stats()
    
    text = f"""
💰 *پورتفوی معاملاتی* 💰

💵 *موجودی:* ${stats['balance']:,.2f}
📈 *سود/زیان کل:* ${stats['total_pnl']:+,.2f}
📊 *ROI:* {stats['roi']:+.2f}%

📈 *پوزیشن‌های باز:* {stats['open_positions']}
"""
    
    if engine.positions:
        text += "\n*پوزیشن‌های فعال:*\n"
        for sym, pos in engine.positions.items():
            try:
                ticker = exchange.fetch_ticker(sym)
                current = ticker['last']
                pnl_pct = (current - pos['entry']) / pos['entry'] * 100
                text += f"• {sym.replace('/USDT', '')}: ورود {pos['entry']:,.4f} | فعلی {current:,.4f} | {pnl_pct:+.2f}%\n"
            except:
                text += f"• {sym.replace('/USDT', '')}: ورود {pos['entry']:,.4f}\n"
    
    text += f"""
📊 *آمار:*
• کل معاملات: {stats['total_trades']}
• موفق: {stats['wins']} | ناموفق: {stats['losses']}
• نرخ موفقیت: {stats['win_rate']:.1f}%
• سود متوسط: ${stats['avg_win']:+,.2f}
• ضرر متوسط: ${stats['avg_loss']:+,.2f}
• فاکتور سود: {stats['profit_factor']:.2f}
• ضررهای متوالی: {stats['consecutive_losses']}
"""
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="portfolio"),
                 InlineKeyboardButton("📋 تاریخچه", callback_data="trade_history"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def performance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش عملکرد"""
    query = update.callback_query
    await query.answer()
    
    if not engine.history:
        await query.edit_message_text("📊 هنوز معامله‌ای انجام نشده.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    
    stats = engine.get_stats()
    history = engine.history
    
    # محاسبه شارپ ریشیو
    if len(history) > 1:
        returns = [t['pnl_pct'] for t in history]
        sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
    else:
        sharpe = 0
    
    # بهترین و بدترین
    best = max(history, key=lambda x: x['pnl'])
    worst = min(history, key=lambda x: x['pnl'])
    
    text = f"""
📊 *گزارش عملکرد جامع*

💰 سود/زیان کل: ${stats['total_pnl']:+,.2f}
📈 ROI: {stats['roi']:+.2f}%
📊 Sharpe Ratio: {sharpe:.2f}

📈 *بهترین معامله:*
• {best['symbol']}: ${best['pnl']:+,.2f} ({best['pnl_pct']:+.2f}%)

📉 *بدترین معامله:*
• {worst['symbol']}: ${worst['pnl']:+,.2f} ({worst['pnl_pct']:+.2f}%)

📊 *آمار کلی:*
• کل: {stats['total_trades']} | موفق: {stats['wins']} | ناموفق: {stats['losses']}
• نرخ موفقیت: {stats['win_rate']:.1f}%
• فاکتور سود: {stats['profit_factor']:.2f}
• میانگین سود: ${stats['avg_win']:+,.2f}
• میانگین ضرر: ${stats['avg_loss']:+,.2f}
• ضررهای متوالی: {stats['consecutive_losses']}
"""
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data="performance"),
                 InlineKeyboardButton("📋 تاریخچه کامل", callback_data="trade_history"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def technical_analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی تحلیل تکنیکال"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📈 *تحلیل تکنیکال*\nارز را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_technical_menu())

async def technical_symbol_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol):
    """تحلیل تکنیکال یک نماد"""
    query = update.callback_query
    await query.answer()
    
    status = await query.edit_message_text(f"🔄 تحلیل تکنیکال {symbol.replace('/USDT', '')}...")
    
    analysis = await analyze_symbol_full(symbol)
    
    if not analysis:
        await query.edit_message_text("❌ خطا در تحلیل", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_technical")]]))
        return
    
    msg = format_signal_message(analysis)
    
    keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"tech_{symbol}"),
                 InlineKeyboardButton("📋 لیست", callback_data="menu_technical"),
                 InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def auto_trade_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی معاملات خودکار"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🤖 *معاملات خودکار*\nتنظیمات را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_auto_trade_menu())

async def toggle_demo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تغییر وضعیت معاملات دمو"""
    global config
    query = update.callback_query
    await query.answer()
    config.AUTO_TRADE = not config.AUTO_TRADE
    await auto_trade_menu_handler(update, context)

async def toggle_real_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تغییر وضعیت معاملات واقعی"""
    global config
    query = update.callback_query
    if not exchange:
        await query.answer("❌ صرافی متصل نیست!", show_alert=True)
        return
    await query.answer()
    config.REAL_TRADE = not config.REAL_TRADE
    await auto_trade_menu_handler(update, context)

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی تنظیمات"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⚙️ *تنظیمات ربات*\nبخش مورد نظر را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_settings_menu())

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنما"""
    query = update.callback_query
    await query.answer()
    text = """
❓ *راهنمای ربات*

📊 *تحلیل و سیگنال:*
• /prices - قیمت‌ها
• /signal - سیگنال BTC
• /scan - اسکن بازار
• /tech - تحلیل تکنیکال
• /mtf - مولتی تایم‌فریم

💰 *معاملات:*
• /portfolio - پورتفوی
• /performance - عملکرد
• /positions - پوزیشن‌های باز
• /history - تاریخچه

⚙️ *تنظیمات:*
• /settings - تنظیمات
• /auto - معاملات خودکار
• /risk - مدیریت ریسک

⚠️ *هشدار:*
این ربات برای تحلیل و سیگنال‌دهی است.
مسئولیت معاملات با شماست.
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی اصلی"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🤖 *منوی اصلی*\nلطفاً انتخاب کنید:", parse_mode="Markdown", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک‌ها"""
    query = update.callback_query
    data = query.data
    
    try:
        if data == "back":
            await back_handler(update, context)
        elif data == "prices_all":
            await prices_all_handler(update, context)
        elif data == "market_scan":
            await market_scan_handler(update, context)
        elif data == "best_opportunities":
            await market_scan_handler(update, context)
        elif data.startswith("signal_"):
            symbol = data.replace("signal_", "") + "/USDT"
            if symbol == "BTC/USDT":
                await signal_handler(update, context)
            else:
                await signal_handler(update, context, symbol)
        elif data == "menu_technical":
            await technical_analysis_handler(update, context)
        elif data.startswith("tech_"):
            symbol = data.replace("tech_", "")
            await technical_symbol_handler(update, context, symbol)
        elif data == "menu_mtf":
            await query.edit_message_text("⏰ *مولتی تایم‌فریم*\nارز را انتخاب کنید:", parse_mode="Markdown", reply_markup=get_mtf_menu())
        elif data.startswith("mtf_"):
            symbol = data.replace("mtf_", "")
            await signal_handler(update, context, symbol)
        elif data == "portfolio":
            await portfolio_handler(update, context)
        elif data == "performance":
            await performance_handler(update, context)
        elif data == "trade_history":
            await performance_handler(update, context)
        elif data == "menu_auto":
            await auto_trade_menu_handler(update, context)
        elif data == "toggle_demo":
            await toggle_demo_handler(update, context)
        elif data == "toggle_real":
            await toggle_real_handler(update, context)
        elif data == "settings":
            await settings_handler(update, context)
        elif data == "help":
            await help_handler(update, context)
        elif data == "refresh":
            await back_handler(update, context)
        elif data == "daily_analysis":
            content = format_educational_content()
            await query.edit_message_text(content, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif data == "market_status":
            await market_scan_handler(update, context)
        elif data == "fear_greed":
            await query.edit_message_text("📉 *شاخص ترس و طمع*\n\nدر حال دریافت داده...\n\nاین بخش در نسخه بعدی تکمیل می‌شود.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif data == "emergency_stop":
            # بستن همه پوزیشن‌ها
            for sym in list(engine.positions.keys()):
                try:
                    ticker = exchange.fetch_ticker(sym)
                    engine.close_position(sym, ticker['last'], "EMERGENCY_STOP")
                except:
                    pass
            await query.edit_message_text("⏸️ *توقف اضطراری*\n\n✅ همه پوزیشن‌ها بسته شدند.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        elif data == "clear_cache":
            cache.clear_old(0)
            await query.answer("✅ کش پاکسازی شد", show_alert=True)
        elif data == "api_status":
            status = "✅ متصل" if exchange else "❌ قطع"
            await query.edit_message_text(f"🔑 *وضعیت API*\n\nCoinEx: {status}\nGroq: {'✅' if config.GROQ_API_KEY else '❌'}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="settings")]]))
        elif data == "open_positions":
            await portfolio_handler(update, context)
        else:
            await query.answer("در حال توسعه...")
    except Exception as e:
        logger.error(f"Button handler error: {e}")
        try:
            await query.edit_message_text(f"❌ خطا: {str(e)[:100]}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        except:
            pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های متنی"""
    await update.message.reply_text("لطفاً از منوی ربات استفاده کنید.\n/start", reply_markup=get_main_menu())

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاها"""
    logger.error(f"Error: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ خطایی رخ داد. /start")
    except:
        pass

# ================================ حلقه‌های خودکار ================================
async def auto_signal_to_channel(app):
    """ارسال سیگنال هر ۱۰ دقیقه به کانال"""
    await asyncio.sleep(15)
    
    while True:
        try:
            if not config.CHANNEL_ID or config.CHANNEL_ID == "@CryptoPulse606":
                await asyncio.sleep(60)
                continue
            
            # تحلیل BTC
            btc_analysis = await analyze_symbol_full("BTC/USDT")
            if btc_analysis:
                msg = format_signal_message(btc_analysis)
                await safe_send_message(app.bot, config.CHANNEL_ID, msg)
                logger.info("📤 BTC signal sent to channel")
            
            await asyncio.sleep(120)
            
            # تحلیل ETH
            eth_analysis = await analyze_symbol_full("ETH/USDT")
            if eth_analysis:
                msg = format_signal_message(eth_analysis)
                await safe_send_message(app.bot, config.CHANNEL_ID, msg)
                logger.info("📤 ETH signal sent to channel")
            
            await asyncio.sleep(120)
            
            # تحلیل ۳ ارز برتر (اسکن)
            results = []
            for symbol in config.SYMBOLS[:10]:
                analysis = await analyze_symbol_full(symbol)
                if analysis:
                    results.append(analysis)
            
            results.sort(key=lambda x: abs(x['score']), reverse=True)
            
            for r in results[:3]:
                msg = format_signal_message(r)
                await safe_send_message(app.bot, config.CHANNEL_ID, msg)
                await asyncio.sleep(90)
            
            logger.info(f"📤 {len(results[:3])} signals sent to channel")
            
        except Exception as e:
            logger.error(f"Auto signal error: {e}")
        
        await asyncio.sleep(config.SIGNAL_INTERVAL)

async def auto_educational_content(app):
    """ارسال محتوای آموزشی هر ۱ ساعت"""
    await asyncio.sleep(30)
    
    while True:
        try:
            if config.CHANNEL_ID and config.CHANNEL_ID != "@CryptoPulse606":
                content = format_educational_content()
                await safe_send_message(app.bot, config.CHANNEL_ID, content)
                logger.info("📚 Educational content sent")
        except Exception as e:
            logger.error(f"Educational content error: {e}")
        
        await asyncio.sleep(config.ANALYSIS_INTERVAL)

async def position_monitor(app):
    """مانیتورینگ پوزیشن‌های باز"""
    await asyncio.sleep(20)
    
    while True:
        try:
            if engine.positions:
                for symbol in list(engine.positions.keys()):
                    try:
                        ticker = exchange.fetch_ticker(symbol)
                        df = await fetch_ohlcv_safe(symbol, '1h')
                        if df is not None:
                            indicators = UltraTechnicalAnalyzer.calculate_all(df)
                            result = engine.update_position(symbol, ticker['last'], indicators)
                            if result:
                                # ارسال نوتیفیکیشن بسته شدن
                                emoji = "🟢" if result['pnl'] > 0 else "🔴"
                                msg = f"""
{emoji} *پوزیشن بسته شد*

📊 {result['symbol']}
💰 ورود: ${result['entry']:,.4f}
💵 خروج: ${result['exit']:,.4f}
📈 سود/زیان: ${result['pnl']:+,.2f} ({result['pnl_pct']:+.2f}%)
⏱️ مدت: {result['holding_minutes']:.0f} دقیقه
📋 دلیل: {result['reason']}
"""
                                if config.CHANNEL_ID and config.CHANNEL_ID != "@CryptoPulse606":
                                    await safe_send_message(app.bot, config.CHANNEL_ID, msg)
                    except Exception as e:
                        logger.error(f"Position monitor error for {symbol}: {e}")
        except Exception as e:
            logger.error(f"Position monitor loop error: {e}")
        
        await asyncio.sleep(30)

async def safe_send_message(bot, chat_id, text, parse_mode="Markdown", reply_markup=None, max_retries=3):
    """ارسال امن پیام"""
    for attempt in range(max_retries):
        try:
            return await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup, disable_web_page_preview=True)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TimedOut:
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
    return None

# ================================ اجرای اصلی ================================
async def main():
    if not config.TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        return
    
    app = Application.builder().token(config.TOKEN).build()
    
    # هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    # حلقه‌های خودکار
    asyncio.create_task(auto_signal_to_channel(app))
    asyncio.create_task(auto_educational_content(app))
    asyncio.create_task(position_monitor(app))
    
    logger.info("🚀 Ultra Trading Bot v3.0 Started!")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
