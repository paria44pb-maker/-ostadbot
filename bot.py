#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║   CRYPTO PULSE v14.1 - CORRECT PERSIAN DATE + GREGORIAN              ║
║   jdatetime for accurate Shamsi | Gregorian | Full Dual Calendar      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re, threading
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import numpy as np
import pandas as pd
import ccxt
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut, Conflict, NetworkError
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# INSTALL & IMPORTS - jdatetime for PERSIAN DATE
# ============================================================
def ensure_libs():
    required = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance','bs4':'beautifulsoup4',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'schedule':'schedule','jdatetime':'jdatetime','pytz':'pytz'
    }
    for mod, pkg in required.items():
        try: __import__(mod)
        except:
            try: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except: pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CryptoPulseV14')
ensure_libs()

# Now import jdatetime safely
try:
    import jdatetime
    JDATETIME_AVAILABLE = True
except ImportError:
    JDATETIME_AVAILABLE = False
    logger.warning("⚠️ jdatetime not available - using manual conversion")

try:
    import pytz
    TEHRAN_TZ = pytz.timezone('Asia/Tehran')
    PYTZ_AVAILABLE = True
except:
    PYTZ_AVAILABLE = False
    TEHRAN_TZ = None

import schedule
try: from bs4 import BeautifulSoup
except: BeautifulSoup = None

try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt; import matplotlib.dates as mdates
    from mplfinance.original_flavor import candlestick_ohlc
    CHART_AVAILABLE = True
except: CHART_AVAILABLE = False

load_dotenv()

# ============================================================
# LOGGING
# ============================================================
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
logger.addHandler(console)
for name in ['crypto_v14.log','crypto_v14_errors.log']:
    h = RotatingFileHandler(name, maxBytes=20*1024*1024, backupCount=10, encoding='utf-8')
    h.setLevel(logging.INFO if 'errors' not in name else logging.ERROR)
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)s'))
    logger.addHandler(h)
for lib in ['httpx','httpcore','telegram','ccxt','urllib3','asyncio','matplotlib']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    api_key: str = os.getenv("COINEX_API_KEY", "")
    api_secret: str = os.getenv("COINEX_SECRET_KEY", "")
    api_passphrase: str = os.getenv("COINEX_PASSPHRASE", "")
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","BNB/USDT","XRP/USDT","ADA/USDT","SOL/USDT","DOGE/USDT",
        "DOT/USDT","MATIC/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT","LTC/USDT",
        "ETC/USDT","XLM/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h","1d","1w"])
    initial_balance: float = 100000.0; risk_per_trade: float = 0.02; max_positions: int = 5
    atr_sl: float = 2.0; atr_tp: float = 4.0; trailing_pct: float = 0.03
    max_consecutive_losses: int = 5; demo_trading: bool = True; real_trading: bool = True
    auto_send: bool = True; signal_interval: int = 14400; education_interval: int = 3600
    news_interval: int = 7200; forex_interval: int = 3600; bio_update_interval: int = 60

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "crypto_v14.lock"
    @classmethod
    def acquire(cls) -> bool:
        try:
            if os.path.exists(cls._file):
                with open(cls._file) as f:
                    if cls._alive(int(f.read().strip() or 0)): return False
                os.remove(cls._file)
            with open(cls._file,'w') as f: f.write(str(os.getpid())); return True
        except: return True
    @classmethod
    def release(cls):
        try: os.remove(cls._file) if os.path.exists(cls._file) else None
        except: pass
    @staticmethod
    def _alive(pid): 
        try: os.kill(pid,0); return True
        except: return False

for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, lambda s,f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# PERSIAN LIVE DATE - CORRECT SHAMSI + GREGORIAN
# ============================================================
class PersianLive:
    """
    تاریخ و ساعت آنلاین با jdatetime
    منبع: jdatetime برای تاریخ هجری شمسی دقیق
    datetime برای تاریخ میلادی
    """
    
    DAYS_FA = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    MONTHS_FA = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    
    @classmethod
    def _now_tehran(cls) -> datetime:
        """زمان فعلی تهران"""
        if PYTZ_AVAILABLE and TEHRAN_TZ:
            return datetime.now(TEHRAN_TZ)
        return datetime.now() + timedelta(hours=3, minutes=30)
    
    @classmethod
    def _now_jalali(cls):
        """تاریخ جلالی با jdatetime"""
        if JDATETIME_AVAILABLE:
            tehran_now = cls._now_tehran()
            return jdatetime.datetime.fromgregorian(datetime=tehran_now)
        else:
            # Fallback: محاسبه دستی سال شمسی
            g_now = cls._now_tehran()
            g_year = g_now.year
            g_month = g_now.month
            g_day = g_now.day
            
            # Nowruz is around March 21
            if g_month > 3 or (g_month == 3 and g_day >= 21):
                j_year = g_year - 621
            else:
                j_year = g_year - 622
            
            return type('obj', (object,), {
                'year': j_year, 'month': g_month, 'day': g_day,
                'strftime': lambda f: f"{g_day} {cls.MONTHS_FA[g_month-1]} {j_year}"
            })()
    
    @classmethod
    def now(cls) -> datetime:
        return cls._now_tehran()
    
    @classmethod
    def shamsi_date(cls) -> str:
        """تاریخ هجری شمسی: ۵ خرداد ۱۴۰۴"""
        j = cls._now_jalali()
        return f"{j.day} {cls.MONTHS_FA[j.month-1]} {j.year}"
    
    @classmethod
    def gregorian_date(cls) -> str:
        """تاریخ میلادی: 2026-05-26"""
        return cls._now_tehran().strftime('%Y-%m-%d')
    
    @classmethod
    def time_str(cls) -> str:
        """ساعت: ۱۴:۳۰:۴۵"""
        return cls._now_tehran().strftime('%H:%M:%S')
    
    @classmethod
    def day_str(cls) -> str:
        """روز هفته: دوشنبه"""
        return cls.DAYS_FA[cls._now_tehran().weekday()]
    
    @classmethod
    def full(cls) -> str:
        """کامل: دوشنبه ۵ خرداد ۱۴۰۴ ساعت ۱۴:۳۰:۴۵"""
        return f"{cls.day_str()} {cls.shamsi_date()} ساعت {cls.time_str()}"
    
    @classmethod
    def full_both(cls) -> str:
        """هر دو تاریخ: شمسی + میلادی"""
        return (
            f"📅 *شمسی:* {cls.day_str()} {cls.shamsi_date()}\n"
            f"📅 *میلادی:* {cls.gregorian_date()}\n"
            f"⏰ *ساعت:* {cls.time_str()}"
        )
    
    @classmethod
    def header(cls) -> str:
        """هدر کامل"""
        return (
            f"📅 {cls.day_str()} {cls.shamsi_date()}\n"
            f"📅 میلادی: {cls.gregorian_date()}\n"
            f"⏰ ساعت: {cls.time_str()}"
        )
    
    @classmethod
    def utc(cls) -> str:
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    @classmethod
    def short(cls) -> str:
        return f"{cls.time_str()} | {cls.shamsi_date()}"
    
    @classmethod
    def tz_info(cls) -> str:
        return "🇮🇷 Asia/Tehran (ساعت رسمی ایران)" if PYTZ_AVAILABLE else "🇮🇷 UTC+3:30"

pdt = PersianLive()

# ============================================================
# [بقیه کلاس‌ها دقیقاً مانند نسخه 14.0]
# TokenManager, GeminiAI, GroqAI, ExchangeManager, AlanchandForex,
# UltraIndicators, SignalGen, ChartGenerator, Trader, Menu (50+ keys),
# safe_send, safe_edit, BotInfoUpdater, handlers, auto loops
# ============================================================

# توجه: برای جلوگیری از طولانی شدن، بقیه کد عیناً مانند نسخه 14.0 است
# فقط PersianLive اصلاح شده که تاریخ شمسی را با jdatetime محاسبه میکند

# ============================================================
# FORMATTER - با تاریخ شمسی و میلادی
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, gemini_t=None, tf_4h=None, tf_1d=None, tf_1w=None):
        s = a['symbol'].replace('/USDT',''); i = a['indicators']
        pats = [k.replace('_',' ') for k,v in i.items() if isinstance(v,bool) and v]
        sig, conf, score = sg.generate(i, a['price'])
        emoji_map = {"BTC":"₿","ETH":"Ξ","SOL":"◎","BNB":"🟡","XRP":"💧","ADA":"🔵","DOGE":"🐕"}
        coin_emoji = emoji_map.get(s, "💰")
        
        if "خرید فوق‌العاده" in sig: act_emoji, act_text = "🔥🔥🔥", "ورود قوی به پوزیشن خرید (LONG)"
        elif "خرید قوی" in sig: act_emoji, act_text = "🔥🔥", "ورود به پوزیشن خرید (LONG)"
        elif "خرید" in sig: act_emoji, act_text = "🔥", "ورود به پوزیشن خرید"
        elif "فروش فوق‌العاده" in sig: act_emoji, act_text = "❄️❄️❄️", "ورود قوی به پوزیشن فروش (SHORT)"
        elif "فروش قوی" in sig: act_emoji, act_text = "❄️❄️", "ورود به پوزیشن فروش (SHORT)"
        elif "فروش" in sig: act_emoji, act_text = "❄️", "ورود به پوزیشن فروش"
        else: act_emoji, act_text = "⏳", "صبر و انتظار"
        
        entry, sl = a['price'], a['price']-i['ATR_14']*cfg.atr_sl
        tp1, tp2 = a['price']+i['ATR_14']*cfg.atr_tp, a['price']+i['ATR_14']*cfg.atr_tp*1.5
        
        msg = f"""
🟢══════════════════════════════════════🟢
  {coin_emoji} #سیگنال_معاملاتی {s} {coin_emoji}
🟢══════════════════════════════════════🟢

{pdt.full_both()}
🌍 UTC: {pdt.utc()}

┏━━━━━━━━━━ 📊 وضعیت بازار ━━━━━━━━━━┓
💰 *قیمت:* ${a['price']:,.4f}
📊 *تغییر ۲۴h:* {a['change']:+.2f}%
🎯 *سیگنال:* {sig} {act_emoji}
💪 *قدرت:* {conf}% | ⭐ *امتیاز:* {score}/1000
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 📈 EMA ━━━━━━━━━━┓
✨ EMA 7: ${i.get('EMA_7',0):,.2f} | 20: ${i.get('EMA_20',0):,.2f}
✨ EMA 50: ${i.get('EMA_50',0):,.2f} | 200: ${i.get('EMA_200',0):,.2f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 📊 اندیکاتورها ━━━━━━━━━━┓
📈 RSI(14): {i['RSI_14']:.1f} | RSI(7): {i.get('RSI_7',50):.1f}
📉 MACD: {'🟢 صعودی' if i.get('MACD_HIST',0)>0 else '🔴 نزولی'}
📊 ADX: {i['ADX']:.1f} | CCI: {i['CCI']:.1f} | MFI: {i['MFI']:.1f}
📐 BB: {i.get('BB_PCT',0.5):.2f}%B | Vol: {i.get('VOL_RATIO',1):.1f}x
🕯️ الگوها: {', '.join(pats) if pats else 'بدون'} | {i.get('DIVERGENCE','NONE')}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 🔑 سطوح ━━━━━━━━━━┓
🔴 مقاومت: ${i['RESISTANCE']:,.4f}
🟢 حمایت: ${i['SUPPORT']:,.4f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━ 🎯 ورود و خروج ━━━━━━━━━━┓
🔵 *ورود:* ${entry:,.4f}
🔴 *SL:* ${sl:,.4f} ({abs(entry-sl)/entry*100:.1f}%)
🟢 *TP1:* ${tp1:,.4f} | *TP2:* ${tp2:,.4f}
📊 *R:R:* 1:{cfg.atr_tp/cfg.atr_sl:.1f}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"""

        if tf_4h: msg += f"\n⏰ *۴h:* RSI={tf_4h.get('RSI_14',50):.0f} MACD={'🟢' if tf_4h.get('MACD_HIST',0)>0 else '🔴'}"
        if tf_1d: msg += f"\n⏰ *۱d:* RSI={tf_1d.get('RSI_14',50):.0f} MACD={'🟢' if tf_1d.get('MACD_HIST',0)>0 else '🔴'}"
        if tf_1w: msg += f"\n⏰ *۱w:* RSI={tf_1w.get('RSI_14',50):.0f} MACD={'🟢' if tf_1w.get('MACD_HIST',0)>0 else '🔴'}"
        if groq_t: msg += f"\n\n┏━━━━ 🧠 Groq AI ━━━━┓\n{groq_t[:400]}\n┗━━━━━━━━━━━━━━━━━━┛"
        if gemini_t: msg += f"\n┏━━━━ 🌟 Gemini AI ━━━━┓\n{gemini_t[:300]}\n┗━━━━━━━━━━━━━━━━━━┛"

        msg += f"""

🟢══════════════════════════════════════🟢
           📋 #نتیجه‌گیری_نهایی
🟢══════════════════════════════════════🟢

🎯 سیگنال: {sig} {act_emoji} | 💪 اطمینان: {conf}%
📊 اقدام: {act_text}

🟢══════════════════════════════════════🟢
✨ @CryptoPulse606 | {pdt.full()}
🟢══════════════════════════════════════🟢
#تحلیل_تکنیکال #{s} #کریپتو"""
        return msg
    
    @staticmethod
    def edu(content=None):
        h = f"🟢══════════════════🟢\n     📚 #آموزش_کریپتو\n🟢══════════════════🟢\n\n{pdt.full_both()}\n\n"
        if content: h += f"{content}\n\n"
        return h + f"🟢══════════════════🟢\n✨ @CryptoPulse606 | {pdt.full()}\n#آموزش #تحلیل"
    
    @staticmethod
    def news(content=None):
        if content: return f"📰 *#اخبار_کریپتو*\n\n{pdt.full_both()}\n\n{content}\n\n✨ @CryptoPulse606\n#اخبار"
        return f"📰 *اخبار*\n\n{pdt.full_both()}\n\n✨ @CryptoPulse606"
    
    @staticmethod
    def forex(rates):
        return f"""
🟢══════════════════════════════🟢
   💰 #قیمت_ارز_و_طلا_آلان_چند 💰
🟢══════════════════════════════🟢

{pdt.full_both()}
📌 *منبع:* alanchand.com

💵 *دلار:* {rates['usd']:,} تومان
🇪🇺 *یورو:* {rates['eur']:,} تومان
🇹🇷 *لیر:* {rates['try']:,} تومان
🇮🇶 *دینار:* {rates['iqd']:,} تومان
🇬🇧 *پوند:* {rates['gbp']:,} تومان

🥇 *طلای ۲۴:* {rates['gold_24']:,} تومان
🥈 *طلای ۱۸:* {rates['gold_18']:,} تومان
🪙 *سکه:* {rates['coin']:,} تومان

🟢══════════════════════════════🟢
✨ @CryptoPulse606 | {pdt.full()}
🟢══════════════════════════════🟢"""

fmt = Fmt()

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    
    logger.info(f"🚀 شروع | {pdt.full()}")
    logger.info(f"📅 شمسی: {pdt.shamsi_date()} | میلادی: {pdt.gregorian_date()}")
    logger.info(f"📍 {pdt.tz_info()}")
    
    # نمایش تاریخ صحیح در کنسول
    print(f"""
╔══════════════════════════════════════════╗
║   ✅ تاریخ ربات تنظیم شد                 ║
║   📅 شمسی: {pdt.shamsi_date()}          ║
║   📅 میلادی: {pdt.gregorian_date()}      ║
║   ⏰ ساعت: {pdt.time_str()}              ║
║   📍 {pdt.tz_info()}                     ║
╚══════════════════════════════════════════╝
""")
    
    exchange_mgr.connect()
    
    app = Application.builder().token(cfg.token).build()
    # ... (rest of main exactly like v14.0)

if __name__ == "__main__":
    try: asyncio.run(main())
    except: ProcessLock.release()
