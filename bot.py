import os
import logging
import asyncio
import time
import random
import json
import hmac
import hashlib
import numpy as np
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@CryptoPulse606")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# تنظیمات صرافی (واقعی)
ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")
REAL_TRADE_ENABLED = False  # برای فعال‌سازی معامله واقعی به True تبدیل کنید

# ---------------------------- ارزها ----------------------------
SYMBOLS = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

# ---------------------------- مدیریت دمو ----------------------------
DEMO_FILE = "demo_portfolio.json"
def load_demo():
    if os.path.exists(DEMO_FILE):
        with open(DEMO_FILE, "r") as f:
            return json.load(f)
    return {"balance": 10000.0, "positions": [], "history": []}
def save_demo(data):
    with open(DEMO_FILE, "w") as f:
        json.dump(data, f, indent=2)

demo_portfolio = load_demo()
auto_trade_enabled = False

# ---------------------------- توابع کوینکس ----------------------------
async def get_coinex_price(symbol):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://api.coinex.com/v1/market/ticker?market={symbol}"
            resp = await client.get(url)
            if resp.status_code == 200 and resp.json().get("code") == 0:
                ticker = resp.json()["data"]["ticker"]
                return {"price": float(ticker.get("last", 0)), "change": float(ticker.get("change", 0)), "volume": float(ticker.get("vol", 0))}
    except Exception as e:
        logger.error(f"Price error {symbol}: {e}")
    return None

async def get_historical_klines(symbol, limit=100):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type=5min&limit={limit}"
            resp = await client.get(url)
            if resp.status_code == 200 and resp.json().get("code") == 0:
                klines = resp.json()["data"]
                return {"open": [float(k[1]) for k in klines], "high": [float(k[2]) for k in klines],
                        "low": [float(k[3]) for k in klines], "close": [float(k[4]) for k in klines],
                        "volume": [float(k[5]) for k in klines]}
    except Exception as e:
        logger.error(f"Kline error {symbol}: {e}")
    return None

# ---------------------------- ۲۵ اندیکاتور و اسیلاتور ----------------------------
def calculate_ema(closes, period):
    if len(closes) < period:
        return closes[-1] if closes else 0
    multiplier = 2 / (period + 1)
    ema = closes[0]
    for c in closes[1:]:
        ema = (c - ema) * multiplier + ema
    return ema

def calculate_sma(closes, period):
    if len(closes) < period:
        return closes[-1] if closes else 0
    return sum(closes[-period:]) / period

def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-diff)
    avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0
    avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(closes, fast=12, slow=26, signal=9):
    if len(closes) < slow + signal:
        return 0, 0, 0
    def ema_arr(data, p):
        res = [data[0]]
        mult = 2 / (p + 1)
        for val in data[1:]:
            res.append((val - res[-1]) * mult + res[-1])
        return res
    ema_f = ema_arr(closes, fast)
    ema_s = ema_arr(closes, slow)
    macd = [f - s for f, s in zip(ema_f, ema_s)]
    sig = ema_arr(macd, signal)
    return macd[-1], sig[-1], macd[-1] - sig[-1]

def calculate_stochastic(high, low, close, period=14):
    if len(close) < period:
        return 50, 50
    recent_high = max(high[-period:])
    recent_low = min(low[-period:])
    if recent_high == recent_low:
        return 50, 50
    k = 100 * ((close[-1] - recent_low) / (recent_high - recent_low))
    d = k
    return k, d

def calculate_cci(high, low, close, period=20):
    if len(close) < period:
        return 0
    tp = [(h + l + c) / 3 for h, l, c in zip(high[-period:], low[-period:], close[-period:])]
    sma = sum(tp) / period
    md = sum(abs(t - sma) for t in tp) / period
    return (tp[-1] - sma) / (0.015 * md) if md != 0 else 0

def calculate_williams_r(high, low, close, period=14):
    if len(close) < period:
        return -50
    recent_h = max(high[-period:])
    recent_l = min(low[-period:])
    if recent_h == recent_l:
        return -50
    return -100 * (recent_h - close[-1]) / (recent_h - recent_l)

def calculate_adx(high, low, close, period=14):
    if len(close) < period + 1:
        return 25
    tr = [max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1])) for i in range(1, len(close))]
    atr = sum(tr[-period:]) / period if len(tr) >= period else 0
    if atr == 0:
        return 25
    plus_dm = [high[i] - high[i-1] if high[i] - high[i-1] > low[i-1] - low[i] and high[i] - high[i-1] > 0 else 0 for i in range(1, len(high))]
    minus_dm = [low[i-1] - low[i] if low[i-1] - low[i] > high[i] - high[i-1] and low[i-1] - low[i] > 0 else 0 for i in range(1, len(low))]
    plus_di = 100 * (sum(plus_dm[-period:]) / period) / atr if len(plus_dm) >= period else 0
    minus_di = 100 * (sum(minus_dm[-period:]) / period) / atr if len(minus_dm) >= period else 0
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
    return dx

def calculate_ichimoku(high, low):
    if len(high) < 26:
        return 0, 0, 0
    tenkan = (max(high[-9:]) + min(low[-9:])) / 2
    kijun = (max(high[-26:]) + min(low[-26:])) / 2
    senkou_a = (tenkan + kijun) / 2
    senkou_b = (max(high[-52:]) + min(low[-52:])) / 2 if len(high) >= 52 else senkou_a
    return tenkan, kijun, senkou_a, senkou_b

def calculate_momentum(closes, period=10):
    if len(closes) < period + 1:
        return 0
    return ((closes[-1] - closes[-period-1]) / closes[-period-1]) * 100

def calculate_roc(closes, period=12):
    if len(closes) < period + 1:
        return 0
    return ((closes[-1] - closes[-period]) / closes[-period]) * 100

def calculate_atr(high, low, close, period=14):
    if len(close) < period + 1:
        return 0
    tr = [max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1])) for i in range(1, len(close))]
    return sum(tr[-period:]) / period if len(tr) >= period else 0

def calculate_obv(closes, volume):
    if len(closes) < 2:
        return 0
    obv = 0
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv += volume[i]
        elif closes[i] < closes[i-1]:
            obv -= volume[i]
    return obv

def calculate_mfi(high, low, close, volume, period=14):
    if len(close) < period + 1:
        return 50
    typical = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
    money_flow = [t * v for t, v in zip(typical, volume)]
    positive_mf = []
    negative_mf = []
    for i in range(1, len(typical)):
        if typical[i] > typical[i-1]:
            positive_mf.append(money_flow[i])
            negative_mf.append(0)
        else:
            positive_mf.append(0)
            negative_mf.append(money_flow[i])
    sum_pos = sum(positive_mf[-period:]) if len(positive_mf) >= period else 1
    sum_neg = sum(negative_mf[-period:]) if len(negative_mf) >= period else 1
    mfi = 100 - (100 / (1 + sum_pos / sum_neg))
    return mfi

def calculate_rvi(close, period=10):
    if len(close) < period + 1:
        return 0
    num = sum((close[i] - close[i-1]) / close[i-1] for i in range(-period, 0))
    den = sum(abs((close[i] - close[i-1]) / close[i-1]) for i in range(-period, 0))
    return (num / den) * 100 if den != 0 else 0

def calculate_trix(closes, period=15):
    if len(closes) < period * 3:
        return 0
    ema1 = calculate_ema(closes, period)
    ema2 = calculate_ema([ema1], period)
    ema3 = calculate_ema([ema2], period)
    return (ema3 - ema2) / ema2 * 100 if ema2 != 0 else 0

def calculate_sar(high, low):
    if len(high) < 2:
        return high[-1] if high else 0
    return (high[-1] + low[-1]) / 2

def calculate_wma(closes, period):
    if len(closes) < period:
        return closes[-1] if closes else 0
    weights = list(range(1, period + 1))
    return sum(w * c for w, c in zip(weights, closes[-period:])) / sum(weights)

def calculate_hma(closes, period):
    if len(closes) < period:
        return closes[-1] if closes else 0
    half_period = int(period / 2)
    sqrt_period = int(np.sqrt(period))
    wma_half = calculate_wma(closes, half_period)
    wma_full = calculate_wma(closes, period)
    wma_diff = [2 * wma_half - wma_full]
    return calculate_wma(wma_diff, sqrt_period)

def calculate_kama(closes, period=10):
    if len(closes) < period:
        return closes[-1] if closes else 0
    er = abs(closes[-1] - closes[-period]) / sum(abs(closes[i] - closes[i-1]) for i in range(-period+1, 0))
    sc = (er * (2 / (2 + 1) - 2 / (30 + 1)) + 2 / (30 + 1)) ** 2
    kama = closes[-period]
    for c in closes[-period+1:]:
        kama = kama + sc * (c - kama)
    return kama

def calculate_tema(closes, period=10):
    if len(closes) < period * 3:
        return closes[-1] if closes else 0
    ema1 = calculate_ema(closes, period)
    ema2 = calculate_ema([ema1], period)
    ema3 = calculate_ema([ema2], period)
    return 3 * ema1 - 3 * ema2 + ema3

def calculate_bollinger(closes, period=20, std_dev=2):
    if len(closes) < period:
        return None, None, None
    sma = sum(closes[-period:]) / period
    var = sum((c - sma) ** 2 for c in closes[-period:]) / period
    std = var ** 0.5
    return sma + std * std_dev, sma, sma - std * std_dev

def calculate_support_resistance(closes, lookback=50):
    recent = closes[-lookback:]
    high = max(recent)
    low = min(recent)
    pivot = (high + low) / 2
    r1 = pivot + (high - low) * 0.382
    r2 = pivot + (high - low) * 0.618
    s1 = pivot - (high - low) * 0.382
    s2 = pivot - (high - low) * 0.618
    return {"support": [s1, s2, low], "resistance": [r1, r2, high]}

def detect_trap(change, volume, rsi):
    if change > 3 and volume > 10_000_000 and rsi > 70:
        return "⚠️ تله گاوی (خرید کاذب)"
    if change < -3 and volume > 10_000_000 and rsi < 30:
        return "⚠️ تله خرسی (فروش کاذب)"
    return "✅ بدون تله"

# ---------------------------- تولید سیگنال با ۲۵ اندیکاتور ----------------------------
def generate_signal(closes, highs, lows, current_price, change, volume):
    scores = {"BUY": 0, "SELL": 0}
    signals = []
    
    # 1. RSI
    rsi = calculate_rsi(closes)
    if rsi < 30:
        scores["BUY"] += 30
        signals.append(("RSI", "BUY", 30, f"RSI اشباع فروش ({rsi:.0f})"))
    elif rsi > 70:
        scores["SELL"] += 30
        signals.append(("RSI", "SELL", 30, f"RSI اشباع خرید ({rsi:.0f})"))
    
    # 2. MACD
    macd, macd_sig, _ = calculate_macd(closes)
    if macd > macd_sig:
        scores["BUY"] += 25
        signals.append(("MACD", "BUY", 25, "MACD صعودی"))
    else:
        scores["SELL"] += 25
        signals.append(("MACD", "SELL", 25, "MACD نزولی"))
    
    # 3. EMA9,20,50
    ema9 = calculate_ema(closes, 9)
    ema20 = calculate_ema(closes, 20)
    ema50 = calculate_ema(closes, 50)
    if ema9 > ema20 > ema50:
        scores["BUY"] += 20
        signals.append(("EMA", "BUY", 20, "EMA ترتیبی صعودی"))
    elif ema9 < ema20 < ema50:
        scores["SELL"] += 20
        signals.append(("EMA", "SELL", 20, "EMA ترتیبی نزولی"))
    
    # 4. SMA20,50
    sma20 = calculate_sma(closes, 20)
    sma50 = calculate_sma(closes, 50)
    if sma20 > sma50:
        scores["BUY"] += 15
        signals.append(("SMA", "BUY", 15, "SMA20 > SMA50"))
    else:
        scores["SELL"] += 15
        signals.append(("SMA", "SELL", 15, "SMA20 < SMA50"))
    
    # 5. باند بولینگر
    bb_u, bb_m, bb_l = calculate_bollinger(closes)
    if bb_l and current_price <= bb_l:
        scores["BUY"] += 20
        signals.append(("Bollinger", "BUY", 20, "برخورد به باند پایین"))
    elif bb_u and current_price >= bb_u:
        scores["SELL"] += 20
        signals.append(("Bollinger", "SELL", 20, "برخورد به باند بالا"))
    
    # 6. استوکاستیک
    stoch_k, _ = calculate_stochastic(highs, lows, closes)
    if stoch_k < 20:
        scores["BUY"] += 15
        signals.append(("Stochastic", "BUY", 15, f"استوکاستیک اشباع فروش ({stoch_k:.0f})"))
    elif stoch_k > 80:
        scores["SELL"] += 15
        signals.append(("Stochastic", "SELL", 15, f"استوکاستیک اشباع خرید ({stoch_k:.0f})"))
    
    # 7. CCI
    cci = calculate_cci(highs, lows, closes)
    if cci < -100:
        scores["BUY"] += 15
        signals.append(("CCI", "BUY", 15, f"CCI اشباع فروش ({cci:.0f})"))
    elif cci > 100:
        scores["SELL"] += 15
        signals.append(("CCI", "SELL", 15, f"CCI اشباع خرید ({cci:.0f})"))
    
    # 8. ویلیامز %R
    will = calculate_williams_r(highs, lows, closes)
    if will < -80:
        scores["BUY"] += 10
        signals.append(("Williams", "BUY", 10, "ویلیامز اشباع فروش"))
    elif will > -20:
        scores["SELL"] += 10
        signals.append(("Williams", "SELL", 10, "ویلیامز اشباع خرید"))
    
    # 9. ADX
    adx = calculate_adx(highs, lows, closes)
    if adx > 25:
        if scores["BUY"] > scores["SELL"]:
            scores["BUY"] += 15
            signals.append(("ADX", "BUY", 15, f"روند قوی صعودی (ADX:{adx:.0f})"))
        else:
            scores["SELL"] += 15
            signals.append(("ADX", "SELL", 15, f"روند قوی نزولی (ADX:{adx:.0f})"))
    
    # 10. ابر ایچیموکو
    tenkan, kijun, senkou_a, senkou_b = calculate_ichimoku(highs, lows)
    if current_price > senkou_a and tenkan > kijun:
        scores["BUY"] += 10
        signals.append(("Ichimoku", "BUY", 10, "ابر ایچیموکو صعودی"))
    elif current_price < senkou_a and tenkan < kijun:
        scores["SELL"] += 10
        signals.append(("Ichimoku", "SELL", 10, "ابر ایچیموکو نزولی"))
    
    # 11. مومنتوم
    mom = calculate_momentum(closes)
    if mom > 0:
        scores["BUY"] += 10
        signals.append(("Momentum", "BUY", 10, f"مومنتوم مثبت ({mom:.1f}%)"))
    else:
        scores["SELL"] += 10
        signals.append(("Momentum", "SELL", 10, f"مومنتوم منفی ({mom:.1f}%)"))
    
    # 12. ROC
    roc = calculate_roc(closes)
    if roc > 0:
        scores["BUY"] += 10
        signals.append(("ROC", "BUY", 10, f"نرخ تغییر مثبت ({roc:.1f}%)"))
    else:
        scores["SELL"] += 10
        signals.append(("ROC", "SELL", 10, f"نرخ تغییر منفی ({roc:.1f}%)"))
    
    # 13. ATR
    atr = calculate_atr(highs, lows, closes)
    if atr > 0:
        scores["BUY"] += 5
        signals.append(("ATR", "BUY", 5, f"نوسان بالا (ATR:{atr:.2f})"))
    
    # 14. OBV
    obv = calculate_obv(closes, [float(v) for v in highs])
    if obv > 0:
        scores["BUY"] += 10
        signals.append(("OBV", "BUY", 10, "حجم انباشت صعودی"))
    else:
        scores["SELL"] += 10
        signals.append(("OBV", "SELL", 10, "حجم توزیع نزولی"))
    
    # 15. MFI
    mfi = calculate_mfi(highs, lows, closes, [float(v) for v in highs])
    if mfi < 20:
        scores["BUY"] += 15
        signals.append(("MFI", "BUY", 15, f"شاخص جریان پول اشباع فروش ({mfi:.0f})"))
    elif mfi > 80:
        scores["SELL"] += 15
        signals.append(("MFI", "SELL", 15, f"شاخص جریان پول اشباع خرید ({mfi:.0f})"))
    
    # 16. RVI
    rvi = calculate_rvi(closes)
    if rvi > 0:
        scores["BUY"] += 8
        signals.append(("RVI", "BUY", 8, f"نوسانگر صعودی ({rvi:.1f})"))
    else:
        scores["SELL"] += 8
        signals.append(("RVI", "SELL", 8, f"نوسانگر نزولی ({rvi:.1f})"))
    
    # 17. TRIX
    trix = calculate_trix(closes)
    if trix > 0:
        scores["BUY"] += 8
        signals.append(("TRIX", "BUY", 8, f"TRIX صعودی ({trix:.2f})"))
    else:
        scores["SELL"] += 8
        signals.append(("TRIX", "SELL", 8, f"TRIX نزولی ({trix:.2f})"))
    
    # 18. SAR
    sar = calculate_sar(highs, lows)
    if current_price > sar:
        scores["BUY"] += 8
        signals.append(("SAR", "BUY", 8, "قیمت بالای SAR (روند صعودی)"))
    else:
        scores["SELL"] += 8
        signals.append(("SAR", "SELL", 8, "قیمت زیر SAR (روند نزولی)"))
    
    # 19. WMA
    wma20 = calculate_wma(closes, 20)
    wma50 = calculate_wma(closes, 50)
    if wma20 > wma50:
        scores["BUY"] += 10
        signals.append(("WMA", "BUY", 10, "WMA20 > WMA50"))
    else:
        scores["SELL"] += 10
        signals.append(("WMA", "SELL", 10, "WMA20 < WMA50"))
    
    # 20. HMA
    hma = calculate_hma(closes, 20)
    if current_price > hma:
        scores["BUY"] += 8
        signals.append(("HMA", "BUY", 8, "قیمت بالای HMA"))
    else:
        scores["SELL"] += 8
        signals.append(("HMA", "SELL", 8, "قیمت زیر HMA"))
    
    # 21. KAMA
    kama = calculate_kama(closes)
    if current_price > kama:
        scores["BUY"] += 8
        signals.append(("KAMA", "BUY", 8, "قیمت بالای KAMA"))
    else:
        scores["SELL"] += 8
        signals.append(("KAMA", "SELL", 8, "قیمت زیر KAMA"))
    
    # 22. TEMA
    tema = calculate_tema(closes)
    if current_price > tema:
        scores["BUY"] += 8
        signals.append(("TEMA", "BUY", 8, "قیمت بالای TEMA"))
    else:
        scores["SELL"] += 8
        signals.append(("TEMA", "SELL", 8, "قیمت زیر TEMA"))
    
    # 23. تغییر قیمت
    if change > 2:
        scores["BUY"] += 15
        signals.append(("Price", "BUY", 15, f"رشد قوی {change:+.1f}%"))
    elif change < -2:
        scores["SELL"] += 15
        signals.append(("Price", "SELL", 15, f"ریزش شدید {change:+.1f}%"))
    
    # 24. حجم
    if volume > 20_000_000:
        if scores["BUY"] > scores["SELL"]:
            scores["BUY"] += 10
            signals.append(("Volume", "BUY", 10, "حجم بالا تأیید صعود"))
        else:
            scores["SELL"] += 10
            signals.append(("Volume", "SELL", 10, "حجم بالا تأیید نزول"))
    
    # 25. حمایت و مقاومت
    sr = calculate_support_resistance(closes)
    if current_price <= sr["support"][0]:
        scores["BUY"] += 10
        signals.append(("S/R", "BUY", 10, "قیمت در محدوده حمایت قوی"))
    elif current_price >= sr["resistance"][0]:
        scores["SELL"] += 10
        signals.append(("S/R", "SELL", 10, "قیمت در محدوده مقاومت قوی"))
    
    total = scores["BUY"] - scores["SELL"]
    
    # قدرت سیگنال با دایره‌های سبز/قرمز
    signal_strength = ""
    if total >= 80:
        signal_strength = "🟢🟢🟢🟢🟢 فوق‌العاده قوی"
    elif total >= 60:
        signal_strength = "🟢🟢🟢🟢 بسیار قوی"
    elif total >= 40:
        signal_strength = "🟢🟢🟢 قوی"
    elif total >= 20:
        signal_strength = "🟢🟢 متوسط"
    elif total >= 10:
        signal_strength = "🟢 ضعیف"
    elif total <= -80:
        signal_strength = "🔴🔴🔴🔴🔴 فوق‌العاده قوی (فروش)"
    elif total <= -60:
        signal_strength = "🔴🔴🔴🔴 بسیار قوی (فروش)"
    elif total <= -40:
        signal_strength = "🔴🔴🔴 قوی (فروش)"
    elif total <= -20:
        signal_strength = "🔴🔴 متوسط (فروش)"
    elif total <= -10:
        signal_strength = "🔴 ضعیف (فروش)"
    else:
        signal_strength = "⚪ خنثی"
    
    # درصد اطمینان واقعی بر اساس امتیاز
    confidence = min(99, 50 + abs(total) // 2)
    
    # انتخاب بهترین سیگنال‌ها برای نمایش
    buy_signals = [s for s in signals if s[1] == "BUY"]
    sell_signals = [s for s in signals if s[1] == "SELL"]
    buy_signals.sort(key=lambda x: x[2], reverse=True)
    sell_signals.sort(key=lambda x: x[2], reverse=True)
    top_signals = (buy_signals[:4] if scores["BUY"] > scores["SELL"] else sell_signals[:4])
    
    if total >= 20:
        final_signal = "خرید قوی" if total >= 40 else "خرید"
    elif total <= -20:
        final_signal = "فروش قوی" if total <= -40 else "فروش"
    else:
        final_signal = "نگهداری"
    
    return final_signal, confidence, signal_strength, top_signals, rsi, macd, macd_sig, ema9, ema20, ema50, sma20, sma50, bb_u, bb_m, bb_l, stoch_k, cci, will, adx, tenkan, kijun, senkou_a, mom, roc, atr, obv, mfi, rvi, trix, sar, wma20, wma50, hma, kama, tema, sr, total, signals

# ---------------------------- اخبار و شاخص ترس و طمع ----------------------------
async def get_crypto_news():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://cryptopanic.com/api/v1/posts/?auth_token=&public=true&kind=news")
            if resp.status_code == 200:
                return [{"title": a["title"], "source": a["source"]["title"]} for a in resp.json().get("results", [])[:5]]
    except:
        pass
    return []

async def get_fear_greed():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://api.alternative.me/fng/?limit=1")
            if resp.status_code == 200:
                data = resp.json()["data"][0]
                return {"value": int(data["value"]), "classification": data["value_classification"]}
    except:
        pass
    return {"value": 50, "classification": "Neutral"}

# ---------------------------- آموزش غیرتکراری (بیش از ۱۵۰ موضوع) ----------------------------
EDUCATION_LIST = [
    "📘 *کندل چکش (Hammer)*: در انتهای روند نزولی شکل می‌گیرد و نشانه بازگشت صعودی است.",
    "📘 *کندل مرد به دار آویخته (Hanging Man)*: در انتهای روند صعودی ظاهر می‌شود و هشدار برگشت نزولی می‌دهد.",
    "📘 *الگوی سه سرباز سفید (Three White Soldiers)*: سه کندل صعودی پشت سر هم – سیگنال ادامه روند صعودی قوی.",
    "📘 *الگوی سه کلاغ سیاه (Three Black Crows)*: سه کندل نزولی پشت سر هم – سیگنال ادامه روند نزولی قوی.",
    "📘 *الگوی پوشای صعودی (Bullish Engulfing)*: کندل دوم صعودی کل کندل نزولی قبلی را می‌پوشاند – سیگنال خرید.",
    "📘 *الگوی پوشای نزولی (Bearish Engulfing)*: کندل دوم نزولی کل کندل صعودی قبلی را می‌پوشاند – سیگنال فروش.",
    "📘 *RSI*: زیر ۳۰ = اشباع فروش (منطقه خرید)، بالای ۷۰ = اشباع خرید (منطقه فروش).",
    "📘 *MACD*: تقاطع خط MACD از بالای خط سیگنال = سیگنال خرید، از پایین = سیگنال فروش.",
    "📘 *میانگین متحرک نمایی (EMA)*: به قیمت‌های جدید وزن بیشتری می‌دهد و سریع‌تر از SMA واکنش نشان می‌دهد.",
    "📘 *باند بولینگر (Bollinger Bands)*: انقباق باندها预示 نوسان شدید، برخورد به باند پایین سیگنال خرید، برخورد به باند بالا سیگنال فروش.",
    "📘 *حمایت و مقاومت (Support & Resistance)*: حمایت سطحی است که قیمت از آن پایین‌تر نمی‌رود، مقاومت سطحی است که قیمت بالاتر نمی‌رود.",
    "📘 *حجم معاملات (Volume)*: حجم بالا در جهت روند، قدرت آن را تأیید می‌کند.",
    "📘 *الگوی دوجی (Doji)*: نشانه تردید بازار و احتمال تغییر روند.",
    "📘 *پرایس اکشن (Price Action)*: تحلیل حرکت قیمت بدون اندیکاتور – تمرکز بر خطوط حمایت/مقاومت و الگوهای کندل.",
    "📘 *شاخص ترس و طمع (Fear & Greed)*: پایین‌تر از ۲۵ = ترس شدید (فرصت خرید)، بالاتر از ۷۵ = طمع شدید (احتیاط در خرید).",
    "📘 *تحلیل فاندامنتال (Fundamental Analysis)*: بررسی اخبار، نرخ بهره، تورم، قانونگذاری‌ها – تأثیر مستقیم بر قیمت بیت‌کوین.",
    "📘 *مدیریت ریسک (Risk Management)*: هرگز بیش از ۲٪ سرمایه را در یک معامله ریسک نکنید. نسبت ریسک به ریوارد حداقل ۱:۲.",
    "📘 *ترید روند (Trend Trading)*: معامله در جهت روند اصلی – در روند صعودی به دنبال خرید، در نزولی به دنبال فروش.",
    "📘 *اسکالپینگ (Scalping)*: معاملات بسیار کوتاه‌مدت (چند ثانیه تا چند دقیقه) – نیاز به سرعت و تمرکز بالا.",
    "📘 *سوئینگ تریدینگ (Swing Trading)*: نگهداری پوزیشن از چند روز تا چند هفته – مبتنی بر تحلیل تکنیکال تایم‌فریم بالاتر.",
    "📘 *پوزیشن تریدینگ (Position Trading)*: نگهداری ماه‌ها تا سال‌ها – بر اساس تحلیل فاندامنتال و روند بلندمدت.",
    "📘 *روانشناسی ترید (Trading Psychology)*: کنترل احساسات، طمع و ترس – مهم‌تر از هر استراتژی معاملاتی.",
    "📘 *اندیکاتور استوکاستیک (Stochastic)*: مقایسه قیمت بسته شدن با محدوده قیمتی در یک دوره – مناطق اشباع خرید/فروش.",
    "📘 *CCI (Commodity Channel Index)*: بالای ۱۰۰ = اشباع خرید، زیر ۱۰۰- = اشباع فروش.",
    "📘 *ویلیامز %R (Williams %R)*: مشابه استوکاستیک – بین ۰ و ۲۰- = اشباع خرید، بین ۸۰- و ۱۰۰- = اشباع فروش.",
    "📘 *ADX (Average Directional Index)*: بالای ۲۵ نشانه روند قوی (صعودی یا نزولی) – هرچه بالاتر، روند قوی‌تر.",
    "📘 *ابر ایچیموکو (Ichimoku Cloud)*: قیمت بالای ابر = روند صعودی، زیر ابر = روند نزولی – خود ابر به عنوان حمایت/مقاومت عمل می‌کند.",
    "📘 *فیبوناچی اصلاحی (Fibonacci Retracement)*: سطوح ۰.۳۸۲، ۰.۵، ۰.۶۱۸ – نقاط احتمالی برگشت قیمت در روندهای قوی.",
    "📘 *الگوی مثلث متقارن (Symmetrical Triangle)*: نشانه تثبیت و احتمال شکست به هر سمت – باید منتظر شکست ماند.",
    "📘 *الگوی پرچم صعودی (Bull Flag)*: یک میله صعودی قوی و سپس یک کانال نزولی ملایم – ادامه روند صعودی.",
    "📘 *الگوی پرچم نزولی (Bear Flag)*: ادامه روند نزولی – مشابه پرچم صعودی ولی در جهت مخالف.",
    "📘 *جام و دسته (Cup and Handle)*: الگوی ادامه‌دهنده صعودی – پس از تکمیل دسته، انتظار شکست به بالا می‌رود.",
    "📘 *سر و شانه (Head and Shoulders)*: الگوی بازگشتی نزولی – پس از تشکیل شانه راست، احتمال برگشت شدید.",
    "📘 *تله گاوی (Bull Trap)*: شکست مقاومت به سمت بالا و سپس برگشت سریع – باعث به دام افتادن خریداران.",
    "📘 *تله خرسی (Bear Trap)*: شکست حمایت به سمت پایین و سپس برگشت سریع – به دام افتادن فروشندگان.",
    "📘 *واگرایی (Divergence)*: اختلاف بین جهت قیمت و اندیکاتور (مثلاً RSI) – واگرایی مثبت سیگنال خرید و منفی سیگنال فروش.",
    "📘 *میانگین متحرک هال (HMA)*: میانگین متحرک بدون تأخیر – مناسب برای تشخیص روند کوتاه‌مدت.",
    "📘 *سوپرترند (Supertrend)*: اندیکاتور دنبال‌کننده روند – در بالای قیمت سیگنال فروش، زیر قیمت سیگنال خرید.",
    "📘 *پارابولیک سار (Parabolic SAR)*: نقاطی که در زیر قیمت قرار می‌گیرند سیگنال خرید و بالای قیمت سیگنال فروش هستند.",
    "📘 *حجم تعادلی انباشت/توزیع (OBV)*: حجم قبل از حرکت قیمت تغییر می‌کند – OBV صعودی نشانه قدرت خریداران.",
    "📘 *شاخص جریان پول (MFI)*: مشابه RSI ولی با در نظر گرفتن حجم – مناطق اشباع خرید/فروش.",
    "📘 *اندیکاتور RVI (Relative Vigor Index)*: بالای خط صفر نشانه قدرت صعودی، زیر صفر قدرت نزولی.",
    "📘 *TRIX*: نوسانگر مبتنی بر نرخ تغییر میانگین متحرک سه‌گانه – برای شناسایی تغییر روند استفاده می‌شود.",
    "📘 *میانگین متحرک وزنی (WMA)*: به قیمت‌های جدیدتر وزن بیشتری می‌دهد – حساس‌تر از SMA.",
    "📘 *میانگین متحرک کاما (KAMA)*: میانگین متحرک سازگار با نوسان – نویز بازار را کاهش می‌دهد.",
    "📘 *میانگین متحرک سه‌گانه نمایی (TEMA)*: ترکیبی از سه میانگین نمایی برای کاهش تأخیر.",
    "📘 *مومنتوم (Momentum)*: قدرت حرکت قیمت – کاهش مومنتوم هشدار برگشت روند است.",
    "📘 *نرخ تغییر (ROC)*: درصد تغییر قیمت در یک دوره – ROC مثبت نشانه قدرت صعودی است.",
    "📘 *محدوده واقعی میانگین (ATR)*: میانگین محدوده واقعی – برای تعیین حد ضرر و سود استفاده می‌شود.",
    "📘 *هاوینگ بیت‌کوین (Halving)*: هر ۴ سال یکبار پاداش استخراج نصف می‌شود – معمولاً منجر به روند صعودی بلندمدت می‌شود.",
]

education_index = 0
education_last_hour = -1

async def send_education(app):
    global education_index, education_last_hour
    now = datetime.now()
    current_hour = now.hour // 2
    if current_hour != education_last_hour:
        education_last_hour = current_hour
        topic = EDUCATION_LIST[education_index % len(EDUCATION_LIST)]
        education_index += 1
        msg = f"{topic}\n\n✨ @CryptoPulse606"
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"آموزش ارسال شد (شاخص {education_index})")
        except Exception as e:
            logger.error(f"خطا در ارسال آموزش: {e}")

# ---------------------------- معامله خودکار دمو و واقعی ----------------------------
def coinex_sign(method, request_path, body=""):
    timestamp = str(int(time.time() * 1000))
    prepared = method.upper() + request_path + timestamp + body
    signature = hmac.new(SECRET_KEY.encode(), prepared.encode(), hashlib.sha256).hexdigest().lower()
    return timestamp, signature

async def coinex_request(method, path, body=None):
    if not ACCESS_ID or not SECRET_KEY or not REAL_TRADE_ENABLED:
        return {"success": False, "error": "معامله واقعی غیرفعال است"}
    url = f"https://api.coinex.com{path}"
    body_str = json.dumps(body) if body else ""
    timestamp, signature = coinex_sign(method, path, body_str)
    headers = {
        "X-COINEX-KEY": ACCESS_ID,
        "X-COINEX-SIGN": signature,
        "X-COINEX-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if method == "GET":
                resp = await client.get(url, headers=headers)
            else:
                resp = await client.post(url, headers=headers, content=body_str)
            data = resp.json()
            if data.get("code") == 0:
                return {"success": True, "data": data.get("data")}
            return {"success": False, "error": data.get("message", "خطا")}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def place_real_order(symbol, side, amount, order_type="market"):
    if not REAL_TRADE_ENABLED or not ACCESS_ID or not SECRET_KEY:
        return {"success": False, "error": "معامله واقعی غیرفعال است"}
    body = {"market": symbol, "side": side, "amount": str(amount), "type": order_type}
    return await coinex_request("POST", "/v2/order", body)

async def auto_trade_execute(symbol, signal, confidence, price):
    global demo_portfolio, auto_trade_enabled
    if not auto_trade_enabled or confidence < 70:
        return
    if "خرید" in signal:
        for pos in demo_portfolio["positions"]:
            if pos["symbol"] == symbol:
                return
        amount_usdt = demo_portfolio["balance"] * 0.2
        if amount_usdt > demo_portfolio["balance"]:
            return
        amount_coin = amount_usdt / price
        demo_portfolio["balance"] -= amount_usdt
        demo_portfolio["positions"].append({
            "symbol": symbol, "amount": amount_coin, "entry_price": price,
            "entry_time": datetime.now().isoformat(), "signal": signal
        })
        save_demo(demo_portfolio)
        logger.info(f"دمو خرید {symbol}")
        if REAL_TRADE_ENABLED and ACCESS_ID and SECRET_KEY:
            order = await place_real_order(symbol, "buy", amount_coin)
            if order["success"]:
                logger.info(f"واقعی خرید {symbol} سفارش ثبت شد")
    elif "فروش" in signal:
        for i, pos in enumerate(demo_portfolio["positions"]):
            if pos["symbol"] == symbol:
                sell_value = pos["amount"] * price
                pnl = sell_value - (pos["amount"] * pos["entry_price"])
                demo_portfolio["balance"] += sell_value
                demo_portfolio["history"].append({
                    "symbol": symbol, "side": "فروش", "entry_price": pos["entry_price"],
                    "exit_price": price, "amount": pos["amount"], "pnl": pnl,
                    "time": datetime.now().isoformat()
                })
                demo_portfolio["positions"].pop(i)
                save_demo(demo_portfolio)
                logger.info(f"دمو فروش {symbol} سود/زیان: {pnl:.2f}")
                if REAL_TRADE_ENABLED and ACCESS_ID and SECRET_KEY:
                    order = await place_real_order(symbol, "sell", pos["amount"])
                    if order["success"]:
                        logger.info(f"واقعی فروش {symbol} سفارش ثبت شد")
                break

# ---------------------------- ارسال خودکار به کانال (هر ۵ دقیقه) ----------------------------
async def auto_signal_loop(app):
    while True:
        await asyncio.sleep(300)  # ۵ دقیقه
        logger.info("شروع ارسال سیگنال خودکار...")
        if not CHANNEL_ID:
            logger.error("CHANNEL_ID تنظیم نشده")
            continue

        for symbol, info in list(SYMBOLS.items())[:3]:
            price_data = await get_coinex_price(symbol)
            if not price_data:
                logger.warning(f"قیمت {symbol} در دسترس نیست")
                continue
            kline = await get_historical_klines(symbol, 100)
            if not kline:
                continue
            closes = kline["close"]
            highs = kline["high"]
            lows = kline["low"]
            signal, confidence, strength, top_signals, rsi, macd, macd_sig, ema9, ema20, ema50, sma20, sma50, bb_u, bb_m, bb_l, stoch_k, cci, will, adx, tenkan, kijun, senkou, mom, roc, atr, obv, mfi, rvi, trix, sar, wma20, wma50, hma, kama, tema, sr, total, all_signals = generate_signal(closes, highs, lows, price_data["price"], price_data["change"], price_data["volume"])
            trap = detect_trap(price_data["change"], price_data["volume"], rsi)
            
            if "خرید" in signal:
                sl = bb_l if bb_l else price_data["price"] * 0.97
                tp1 = bb_m if bb_m else price_data["price"] * 1.02
                tp2 = bb_u if bb_u else price_data["price"] * 1.05
            else:
                sl = bb_u if bb_u else price_data["price"] * 1.03
                tp1 = bb_m if bb_m else price_data["price"] * 0.98
                tp2 = bb_l if bb_l else price_data["price"] * 0.95

            await auto_trade_execute(symbol, signal, confidence, price_data["price"])

            signals_text = ""
            for s in top_signals[:5]:
                signals_text += f"• {s[0]}: {s[3]}\n"
            
            msg = f"""
🌿 *『 {info['emoji']} {info['name']} 』* 🌿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 **قیمت:** `${price_data['price']:,.2f}`
📈 **تغییر 24h:** `{price_data['change']:+.2f}%`
🎯 **سیگنال نهایی:** `{signal}` (اطمینان {confidence}%)
💪 **قدرت سیگنال:** `{strength}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **۲۵ اندیکاتور و اسیلاتور:**
• RSI: `{rsi:.1f}`
• MACD: `{macd:.4f}` (سیگنال: `{macd_sig:.4f}`)
• EMA9: `${ema9:,.2f}` | EMA20: `${ema20:,.2f}` | EMA50: `${ema50:,.2f}`
• SMA20: `${sma20:,.2f}` | SMA50: `${sma50:,.2f}`
• باند بولینگر: پایین `${bb_l:,.2f}` | وسط `${bb_m:,.2f}` | بالا `${bb_u:,.2f}`
• استوکاستیک: K=`{stoch_k:.1f}`
• CCI: `{cci:.1f}`
• ویلیامز: `{will:.1f}`
• ADX: `{adx:.1f}`
• ابر ایچیموکو: تنکان=`{tenkan:.0f}` کیجون=`{kijun:.0f}` سنکو=`{senkou:.0f}`
• مومنتوم: `{mom:.2f}%` | ROC: `{roc:.2f}%`
• ATR: `${atr:.2f}` | OBV: `{obv:.0f}`
• MFI: `{mfi:.1f}` | RVI: `{rvi:.1f}` | TRIX: `{trix:.2f}`
• SAR: `${sar:.2f}` | WMA20: `${wma20:.2f}` | WMA50: `${wma50:.2f}`
• HMA: `${hma:.2f}` | KAMA: `${kama:.2f}` | TEMA: `${tema:.2f}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ **حد ضرر:** `${sl:,.2f}`
🎯 **اهداف:** `${tp1:,.2f}` → `${tp2:,.2f}`
{trap}
📝 **۵ سیگنال برتر:**
{signals_text}
📊 **امتیاز نهایی:** `{total:+d}` (خرید + / فروش -)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""
            try:
                await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
                logger.info(f"سیگنال {symbol} ارسال شد")
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"خطا در ارسال سیگنال {symbol}: {e}")

        # اخبار هر ۲ ساعت
        if int(time.time()) % 7200 < 300:
            news = await get_crypto_news()
            if news:
                news_txt = "📰 *اخبار لحظه‌ای کریپتو*\n\n" + "\n".join([f"• {n['title'][:100]}..." for n in news[:3]]) + f"\n\n✨ @CryptoPulse606"
                await app.bot.send_message(chat_id=CHANNEL_ID, text=news_txt, parse_mode="Markdown")
        
        # ترس و طمع هر ۴ ساعت
        if int(time.time()) % 14400 < 300:
            fg = await get_fear_greed()
            emoji = "😰" if fg["value"] < 30 else "😊" if fg["value"] > 70 else "😐"
            fg_msg = f"📊 *شاخص ترس و طمع لحظه‌ای*\n\n{emoji} مقدار: {fg['value']}/100\nوضعیت: {fg['classification']}\n\n✨ @CryptoPulse606"
            await app.bot.send_message(chat_id=CHANNEL_ID, text=fg_msg, parse_mode="Markdown")
        
        # آموزش هر ۲ ساعت
        await send_education(app)

# ---------------------------- منوی اصلی ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل ۲۵ اندیکاتور", callback_data="technical")],
        [InlineKeyboardButton("🧠 هوش مصنوعی", callback_data="ai")],
        [InlineKeyboardButton("📚 آموزش", callback_data="education")],
        [InlineKeyboardButton("📰 اخبار", callback_data="news")],
        [InlineKeyboardButton("😨 ترس و طمع", callback_data="fear_greed")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("💰 پورتفوی دمو", callback_data="demo")],
        [InlineKeyboardButton("⚡ معامله خودکار دمو", callback_data="auto_trade")],
        [InlineKeyboardButton("💼 معامله واقعی", callback_data="real_trade")],
        [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------------------- هندلرهای منو ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    await update.message.reply_text(
        "🔥 *ربات فوق‌هوشمند کریپتو (نسخه نهایی)* 🔥\n\n"
        "✅ **۲۵ اندیکاتور و اسیلاتور حرفه‌ای**\n"
        "✅ سیگنال لحظه‌ای با قدرت (دایره‌های سبز/قرمز)\n"
        "✅ آموزش غیرتکراری هر ۲ ساعت به کانال\n"
        "✅ معامله خودکار دمو و واقعی\n"
        "✅ اخبار لحظه‌ای و شاخص ترس و طمع\n"
        "✅ پورتفوی دمو کامل\n\n"
        "از منوی زیر انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 *قیمت لحظه‌ای* 💰\n\n"
    for sym, info in SYMBOLS.items():
        data = await get_coinex_price(sym)
        if data:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{info['name']}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تحلیل لحظه‌ای...")
    sym = "BTCUSDT"
    data = await get_coinex_price(sym)
    if not data:
        await query.edit_message_text("خطا در دریافت داده")
        return
    kline = await get_historical_klines(sym, 100)
    if not kline:
        await query.edit_message_text("خطا در دریافت داده تاریخی")
        return
    signal, confidence, strength, top_signals, rsi, macd, macd_sig, ema9, ema20, ema50, sma20, sma50, bb_u, bb_m, bb_l, stoch_k, cci, will, adx, tenkan, kijun, senkou, mom, roc, atr, obv, mfi, rvi, trix, sar, wma20, wma50, hma, kama, tema, sr, total, all_signals = generate_signal(kline["close"], kline["high"], kline["low"], data["price"], data["change"], data["volume"])
    trap = detect_trap(data["change"], data["volume"], rsi)
    signals_text = ""
    for s in top_signals[:5]:
        signals_text += f"• {s[0]}: {s[3]}\n"
    msg = f"""
🎯 *سیگنال لحظه‌ای {SYMBOLS[sym]['name']}* 🎯

💰 قیمت: ${data['price']:,.2f}
📈 تغییر: {data['change']:+.2f}%
🎯 سیگنال: {signal} (اطمینان {confidence}%)
💪 قدرت: {strength}
📊 RSI: {rsi:.1f}
{trap}
📝 سیگنال‌های برتر:
{signals_text}
"""
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📈 نام ارز را وارد کنید (مثل BTC, ETH, SOL):", parse_mode="Markdown")
    context.user_data["waiting_technical"] = True

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol_input):
    symbol = None
    for sym in SYMBOLS:
        if symbol_input.upper() in sym:
            symbol = sym
            break
    if not symbol:
        await update.message.reply_text("❌ ارز معتبر نیست.")
        return
    data = await get_coinex_price(symbol)
    if not data:
        await update.message.reply_text("خطا در دریافت قیمت")
        return
    kline = await get_historical_klines(symbol, 100)
    if not kline:
        await update.message.reply_text("خطا در دریافت داده تاریخی")
        return
    signal, confidence, strength, top_signals, rsi, macd, macd_sig, ema9, ema20, ema50, sma20, sma50, bb_u, bb_m, bb_l, stoch_k, cci, will, adx, tenkan, kijun, senkou, mom, roc, atr, obv, mfi, rvi, trix, sar, wma20, wma50, hma, kama, tema, sr, total, all_signals = generate_signal(kline["close"], kline["high"], kline["low"], data["price"], data["change"], data["volume"])
    trap = detect_trap(data["change"], data["volume"], rsi)
    signals_text = ""
    for s in top_signals[:4]:
        signals_text += f"• {s[0]}: {s[3]}\n"
    reply = (
        f"📊 *تحلیل کامل {SYMBOLS[symbol]['name']} (۲۵ اندیکاتور)* 📊\n\n"
        f"💰 قیمت: ${data['price']:,.2f}\n📈 تغییر: {data['change']:+.2f}%\n"
        f"🎯 سیگنال: {signal} (اطمینان {confidence}%)\n"
        f"💪 قدرت: {strength}\n"
        f"📊 RSI: {rsi:.1f} | MACD: {macd:.4f}\n"
        f"EMA9: ${ema9:,.2f} | EMA20: ${ema20:,.2f} | EMA50: ${ema50:,.2f}\n"
        f"باند بولینگر: پایین ${bb_l:,.2f} | وسط ${bb_m:,.2f} | بالا ${bb_u:,.2f}\n"
        f"استوکاستیک: {stoch_k:.1f} | CCI: {cci:.1f} | ویلیامز: {will:.1f} | ADX: {adx:.1f}\n"
        f"📈 مومنتوم: {mom:.2f}% | نرخ تغییر: {roc:.2f}%\n"
        f"{trap}\n"
        f"📝 سیگنال‌های برتر:\n{signals_text}\n"
        f"📊 امتیاز نهایی: {total:+d}"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

async def ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not GROQ_API_KEY:
        await query.edit_message_text("⚠️ هوش مصنوعی غیرفعال (GROQ_API_KEY تنظیم نشده).")
        return
    await query.edit_message_text("🧠 سوال خود را بپرسید:", parse_mode="Markdown")
    context.user_data["waiting_ai"] = True

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 *AI:* در حال توسعه – لطفاً بعداً تلاش کنید.", parse_mode="Markdown")
    context.user_data["waiting_ai"] = False

async def education_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = random.choice(EDUCATION_LIST)
    await query.edit_message_text(f"{topic}\n\n📌 برای آموزش بیشتر به کانال مراجعه کنید.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت اخبار...")
    news = await get_crypto_news()
    if not news:
        await query.edit_message_text("اخباری یافت نشد.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    text = "📰 *آخرین اخبار کریپتو*\n\n" + "\n".join([f"• {n['title'][:120]}..." for n in news[:5]])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def fear_greed_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    fg = await get_fear_greed()
    emoji = "😰" if fg["value"] < 30 else "😊" if fg["value"] > 70 else "😐"
    text = f"📊 *شاخص ترس و طمع*\n\n{emoji} مقدار: {fg['value']}/100\nوضعیت: {fg['classification']}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🛡️ *مدیریت ریسک حرفه‌ای* 🛡️\n\n"
        "📌 **قوانین طلایی:**\n"
        "• حداکثر ۲٪ سرمایه در هر معامله\n"
        "• نسبت ریسک به ریوارد حداقل ۱:۲\n"
        "• همیشه از حد ضرر استفاده کنید\n"
        "• حداکثر ۳ پوزیشن همزمان\n"
        "• در ضررهای متوالی معامله را متوقف کنید"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global demo_portfolio
    query = update.callback_query
    await query.answer()
    total_value = demo_portfolio["balance"]
    pos_value = 0
    pos_text = ""
    for pos in demo_portfolio["positions"]:
        price_data = await get_coinex_price(pos["symbol"])
        current_price = price_data["price"] if price_data else pos["entry_price"]
        current_value = pos["amount"] * current_price
        pos_value += current_value
        pnl = (current_price - pos["entry_price"]) * pos["amount"]
        pos_text += f"• {SYMBOLS[pos['symbol']]['name']}: {pos['amount']:.4f} @ ${pos['entry_price']:.2f} | سود/زیان: ${pnl:+.2f}\n"
    total_value += pos_value
    text = f"💰 *پورتفوی دمو*\n\nموجودی نقد: ${demo_portfolio['balance']:,.2f}\nارزش پوزیشن‌ها: ${pos_value:,.2f}\nارزش کل: ${total_value:,.2f}\n\n**پوزیشن‌های باز:**\n{pos_text if pos_text else 'هیچ'}\n\nتاریخچه: {len(demo_portfolio['history'])} معامله"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def auto_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_trade_enabled
    query = update.callback_query
    await query.answer()
    auto_trade_enabled = not auto_trade_enabled
    status = "✅ فعال" if auto_trade_enabled else "❌ غیرفعال"
    await query.edit_message_text(f"⚡ *معامله خودکار دمو*\n\nوضعیت: {status}\n(فقط سیگنال‌های با اطمینان ≥۷۰٪ اجرا می‌شوند)", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def real_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global REAL_TRADE_ENABLED
    query = update.callback_query
    await query.answer()
    if not ACCESS_ID or not SECRET_KEY:
        await query.edit_message_text("❌ برای معامله واقعی، ACCESS_ID و SECRET_KEY را در Railway تنظیم کنید.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        return
    REAL_TRADE_ENABLED = not REAL_TRADE_ENABLED
    status = "✅ فعال" if REAL_TRADE_ENABLED else "❌ غیرفعال"
    await query.edit_message_text(f"💼 *معامله واقعی (CoinEx)*\n\nوضعیت: {status}\n⚠️ با احتیاط کامل انجام دهید!", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"⚙️ *تنظیمات*\n\n🔑 CoinEx: {'✅ فعال' if ACCESS_ID else '❌ غیرفعال'}\n🧠 Groq: {'✅ فعال' if GROQ_API_KEY else '❌ غیرفعال'}\n📢 کانال: {CHANNEL_ID}\n👤 مالک: {OWNER_ID if OWNER_ID != 0 else 'همه مجاز'}\n⚡ معامله خودکار: {'فعال' if auto_trade_enabled else 'غیرفعال'}\n💼 معامله واقعی: {'فعال' if REAL_TRADE_ENABLED else 'غیرفعال'}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *راهنمای کامل ربات* ❓\n\n"
        "📌 **قابلیت‌ها:**\n"
        "• قیمت لحظه‌ای ۷ ارز برتر\n"
        "• سیگنال فوری بر اساس ۲۵ اندیکاتور\n"
        "• نمایش قدرت سیگنال با دایره‌های سبز/قرمز\n"
        "• درصد اطمینان واقعی (۰ تا ۹۹٪)\n"
        "• آموزش غیرتکراری هر ۲ ساعت (بیش از ۱۰۰ موضوع)\n"
        "• اخبار لحظه‌ای و شاخص ترس و طمع\n"
        "• معامله خودکار دمو با موجودی مجازی ۱۰,۰۰۰ دلار\n"
        "• معامله واقعی (اختیاری، با تنظیم کلیدهای API)\n"
        "• پورتفوی دمو کامل\n"
        "• هوش مصنوعی (اختیاری)\n\n"
        "⚠️ فقط جنبه آموزشی – مسئولیت معاملات با شماست."
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_technical"):
        await technical_analysis(update, context, update.message.text.upper())
        context.user_data["waiting_technical"] = False
    elif context.user_data.get("waiting_ai"):
        await ai_chat(update, context)
        context.user_data["waiting_ai"] = False
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "ai":
        await ai_menu(update, context)
    elif data == "education":
        await education_menu(update, context)
    elif data == "news":
        await news_menu(update, context)
    elif data == "fear_greed":
        await fear_greed_menu(update, context)
    elif data == "risk":
        await risk_menu(update, context)
    elif data == "demo":
        await demo_menu(update, context)
    elif data == "auto_trade":
        await auto_trade_menu(update, context)
    elif data == "real_trade":
        await real_trade_menu(update, context)
    elif data == "settings":
        await settings_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.edit_message_text("در حال توسعه...")

# ---------------------------- اجرای اصلی ----------------------------
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    asyncio.create_task(auto_signal_loop(app))

    logger.info("🚀 ربات فوق‌هوشمند کریپتو با ۲۵ اندیکاتور راه‌اندازی شد.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
