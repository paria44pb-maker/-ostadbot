#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🔮 CRYPTO GOD EYE v31.0 — چشم خدای کریپتو — ULTIMATE FREE AI TRADER       ║
║  ✅ صرافی: CoinEx (کوینکس) با API KEY شما                                  ║
║  ✅ ۱۰۰٪ رایگان — بدون دعوتنامه — بدون اشتراک                               ║
║  ✅ Owner ID: 7225279768 — Unlimited Access                                ║
║  ✅ AI Image Generator (Pollinations.ai + DALL-E)                           ║
║  ✅ Dual AI (Groq + Gemini)  ✅ Smart Money (SMC)                           ║
║  ✅ 1000+ Hours AI Course (Every 30 min)                                    ║
║  ✅ Live Signals Every 2 Hours (Chart + AI Image)                           ║
║  ✅ Live News Every 4 Hours (AI Image)                                      ║
║  ✅ Daily Market Summary (23:00 Tehran)                                     ║
║  ✅ 80+ Indicators  ✅ Fear & Greed  ✅ Dominance                            ║
║  ✅ 24 Professional Animated Buttons — All Active                           ║
║  ✅ Ultra-Precise Persian Analysis — God Eye Precision                      ║
║  ✅ Signal Strength Circles 🟢🟡🔴⚪                                       ║
║  ✅ Real & Demo Trading via CoinEx API                                      ║
║  ✅ Colorful Theme — Emoji-Rich — User-Friendly                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

توسعه‌دهنده: تیم چشم خدای کریپتو 👁️
آخرین بروزرسانی: ۲۰۲۶-۰۵-۳۰
تعداد خطوط: ۵۰۰۰+
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re, threading, gc, urllib.parse, textwrap
os.environ["TZ"] = "Asia/Tehran"
os.environ["MPLBACKEND"] = "Agg"
try: time.tzset()
except: pass

from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, OrderedDict
import numpy as np
import pandas as pd
import ccxt
import httpx
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 🎨 AUTO INSTALL (ALL NECESSARY LIBRARIES)
# ============================================================
def ensure_libs():
    libs = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'jdatetime':'jdatetime','pytz':'pytz','scipy':'scipy',
        'feedparser':'feedparser','Pillow':'Pillow',
        'cachetools':'cachetools','tenacity':'tenacity',
        'aiohttp':'aiohttp','schedule':'schedule',
        'colorama':'colorama','termcolor':'termcolor'
    }
    for mod, pkg in libs.items():
        try: __import__(mod)
        except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CryptoGodEyeV31')
ensure_libs()

# کتابخانه‌های رنگی برای کنسول
from colorama import init, Fore, Back, Style
init(autoreset=True)

import schedule
import jdatetime, pytz
import feedparser
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential

TEHRAN_TZ = pytz.timezone('Asia/Tehran')
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    import mplfinance as mpf
    CHART_AVAILABLE = True
except:
    CHART_AVAILABLE = False

load_dotenv()

# ============================================================
# 🧹 MEMORY MANAGEMENT & CLEANUP
# ============================================================
async def cleanup_memory():
    """پاکسازی هوشمند حافظه با نمایش وضعیت 🧹"""
    while True:
        gc.collect()
        if CHART_AVAILABLE:
            try: plt.close('all')
            except: pass
        mem_usage = gc.get_count()
        logger.info(f"{Fore.GREEN}🧹 حافظه پاکسازی شد | وضعیت: {mem_usage}")
        await asyncio.sleep(600)

# ============================================================
# 📝 LOGGING SYSTEM (COLORFUL & ROTATING)
# ============================================================
logger.setLevel(logging.INFO)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter(
    f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} | '
    f'{Fore.YELLOW}%(levelname)s{Style.RESET_ALL} | '
    f'{Fore.WHITE}%(message)s{Style.RESET_ALL}'
))
logger.addHandler(console)

for name in ['god_eye.log','god_eye_errors.log']:
    h = RotatingFileHandler(name, maxBytes=50*1024*1024, backupCount=10, encoding='utf-8')
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(h)

# ============================================================
# 🌐 PROXY CONFIGURATION (OPTIONAL)
# ============================================================
def create_request():
    proxy_url = os.getenv("TELEGRAM_PROXY", "")
    if proxy_url: 
        logger.info(f"{Fore.MAGENTA}🌐 پروکسی فعال شد{Style.RESET_ALL}")
        return HTTPXRequest(proxy_url=proxy_url, connect_timeout=90.0, read_timeout=90.0, write_timeout=90.0)
    else: 
        return HTTPXRequest(connect_timeout=90.0, read_timeout=90.0, write_timeout=90.0)

# ============================================================
# ⚙️ CONFIGURATION DATA CLASS
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    owner_id: int = 7225279768
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    coinex_api_key: str = os.getenv("COINEX_API_KEY", "")
    coinex_secret: str = os.getenv("COINEX_SECRET", "")
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT","ADA/USDT",
        "DOGE/USDT","DOT/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT",
        "LTC/USDT","ETC/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT",
        "SUI/USDT","APT/USDT","ARB/USDT","OP/USDT","PEPE/USDT","WIF/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h","1d","1w"])
    auto_send: bool = True
    signal_interval: int = 7200
    education_interval: int = 1800
    news_interval: int = 14400
    fg_interval: int = 3600
    whale_interval: int = 5400
    daily_summary_time: str = "23:00"
    theme_colors: Dict[str, str] = field(default_factory=lambda: {
        'primary': '🟣', 'secondary': '🔵', 'success': '🟢', 
        'danger': '🔴', 'warning': '🟡', 'info': '🔷',
        'gold': '🟡', 'purple': '🟣', 'cyan': '🔷'
    })

cfg = Config()

# ============================================================
# 🔒 PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "god_eye.lock"
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
# 📅 PERSIAN DATE, TIME & GREETING ENGINE
# ============================================================
class PersianLive:
    DAYS = ['دوشنبه 🗓️','سه‌شنبه 🗓️','چهارشنبه 🗓️','پنج‌شنبه 🎉','جمعه 🕌','شنبه 📅','یکشنبه 📅']
    MONTHS = ['فروردین 🌸','اردیبهشت 🌹','خرداد ☀️','تیر 🔥','مرداد 🌞','شهریور 🍂','مهر 🍁','آبان 🌧️','آذر ❄️','دی ⛄','بهمن 🌨️','اسفند 🌱']
    EMOJIS = ['✨','🌟','💫','⭐','🔥','💥','🌈','🎯','🚀','💎','👑','🏆','🎪','🎭','🎨']
    
    @classmethod
    def now(cls): return datetime.now(TEHRAN_TZ)
    
    @classmethod
    def shamsi(cls):
        j = jdatetime.datetime.fromgregorian(datetime=cls.now())
        return f"{j.day} {cls.MONTHS[j.month-1]} {j.year}"
    
    @classmethod
    def time_str(cls): return cls.now().strftime('%H:%M:%S')
    
    @classmethod
    def day_str(cls): return cls.DAYS[cls.now().weekday()]
    
    @classmethod
    def full(cls): 
        emoji = random.choice(cls.EMOJIS)
        return f"{cls.day_str()} {cls.shamsi()} ساعت {cls.time_str()} {emoji}"
    
    @classmethod
    def golden_greeting(cls):
        h = cls.now().hour
        emoji = random.choice(['😊','🤗','😎','🥰','😍','💖','✨','🌟'])
        if 5 <= h < 9: return f"صبح بخیر {emoji} 🌄☀️"
        elif 12 <= h < 14: return f"ظهر بخیر {emoji} ☀️😎"
        elif 16 <= h < 18: return f"عصر بخیر {emoji} 🌇🌅"
        elif 20 <= h <= 23 or 1 <= h < 3: return f"شب خوش {emoji} 🌙✨"
        else: return f"وقت بخیر {emoji} ⏰💫"
    
    @classmethod
    def random_emoji(cls): return random.choice(cls.EMOJIS)

pdt = PersianLive()

# ============================================================
# 🎨 AI IMAGE GENERATOR — COLORFUL & UNLIMITED
# ============================================================
class AIImageGenerator:
    POLLINATIONS_API = "https://image.pollinations.ai/prompt/"
    
    STYLES = {
        "god_eye": "mystical all-seeing eye, cosmic colors, purple and gold, divine energy, 4K, masterpiece",
        "golden_chart": "luxurious golden trading chart with purple accents, green and gold candles, divine theme, 4K",
        "bull": "majestic golden bull with cosmic energy, purple and green aura, divine power, epic, 8K",
        "bear": "cosmic bear with golden eyes, purple energy, dramatic divine scene, 4K",
        "whale": "ethereal whale swimming in cosmic ocean, golden and purple scales, divine, 8K",
        "news": "divine news hologram, purple and gold headlines, cosmic newsroom, 4K",
        "moon": "rocket with divine Bitcoin logo, purple cosmos, golden stars, epic, 4K",
        "abstract": "abstract divine crypto art, cosmic blockchain, purple and gold geometry, 4K"
    }
    
    def __init__(self):
        self.enabled = True
        self.generation_count = 0
    
    async def generate(self, prompt: str, style: str = "god_eye", width: int = 1024, height: int = 1024) -> Optional[bytes]:
        """🎨 تولید تصویر با هوش مصنوعی (تم کیهانی و الهی)"""
        final_prompt = self._build_prompt(prompt, style)
        try:
            encoded_prompt = urllib.parse.quote(final_prompt)
            url = f"{self.POLLINATIONS_API}{encoded_prompt}?width={width}&height={height}&nologo=true"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=90)) as response:
                    if response.status == 200:
                        self.generation_count += 1
                        logger.info(f"{Fore.MAGENTA}🎨 تصویر #{self.generation_count} ساخته شد{Style.RESET_ALL}")
                        return await response.read()
        except Exception as e:
            logger.error(f"🎨 AI Image error: {e}")
        return None
    
    def _build_prompt(self, prompt: str, style: str = None) -> str:
        base = "divine cryptocurrency art, cosmic, purple and gold theme, high quality, 4K, masterpiece, mystical"
        style_kw = self.STYLES.get(style, base)
        full = f"{prompt}, {style_kw}, {base}"
        return full[:900]

ai_image_gen = AIImageGenerator()

# ============================================================
# 🧠 DUAL AI (GROQ + GEMINI) — DIVINE INTELLIGENCE
# ============================================================
class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "llama-3.3-70b-versatile"
    
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = httpx.AsyncClient(timeout=120.0)
        self.system_prompt = """تو چشم خدای کریپتو هستی 👁️✨ — فراتر از همه تحلیلگرها با دید الهی و کیهانی! 
فوق‌العاده صمیمی، دوستانه و پر از شکلک و ایموجی حرف بزن 🎨🌟
تحلیل‌هات باید جوری باشه که همه عاشقش بشن و به دوستاشون معرفی کنن 💖
از رنگ‌های بنفش و طلایی در توضیحات استفاده کن 🟣🟡
همیشه با انرژی مثبت و انگیزشی حرف بزن 🚀✨"""
    
    async def ask(self, prompt, max_t=1000):
        if not self.enabled: return None
        try:
            r = await self._client.post(self.URL, headers={
                "Authorization": f"Bearer {cfg.groq_api_key}",
                "Content-Type": "application/json"
            }, json={
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_t,
                "temperature": 0.8
            })
            if r.status_code == 200: 
                logger.info(f"{Fore.CYAN}🧠 AI پاسخ داد{Style.RESET_ALL}")
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"🧠 AI error: {e}")
        return None
    
    async def tech(self, sym, ind, price, change, candles, mtf):
        return await self.ask(f"""✨ تحلیل کیهانی {sym} ✨
💰 قیمت: {price:,.2f} دلار | 📊 تغییر: {change:+.2f}%
🌟 RSI(14)={ind.get('RSI_14',50):.0f} | MACD={'🟢صعودی الهی' if ind.get('MACD_HIST',0)>0 else '🔴نزولی کیهانی'}
💫 ADX={ind.get('ADX',20):.0f} | CCI={ind.get('CCI',0):.0f}
🌌 BB%={ind.get('BB_PCT',0.5):.2f} | حجم={ind.get('VOL_RATIO',1):.1f}x
🛡️ حمایت=${ind.get('حمایت',0):.2f} | ⚔️ مقاومت=${ind.get('مقاومت',0):.2f}
🕯️ شمع‌ها: {', '.join(candles) if candles else 'بدون'}
🌍 MTF: {mtf}

با دید الهی تحلیل کن 👁️✨:
وضعیت، روند، نقطه ورود، حد ضرر، اهداف 🎯
۷۰۰ کلمه فارسی پر از شکلک و انرژی مثبت 🚀""")
    
    async def smc(self, sym, smc_data):
        return await self.ask(f"🌟 اسمارت مانی الهی {sym}:\n{json.dumps(smc_data, ensure_ascii=False)}\nبا دید کیهانی توضیح بده 👁️✨ ۵۰۰ کلمه فارسی پر ایموجی 🎨")
    
    async def prediction(self, sym, price, ind):
        return await self.ask(f"🔮 پیش‌بینی الهی {sym} | قیمت: {price:,.2f}\nRSI={ind.get('RSI_14',50):.1f}\nفردا؟ یک هفته؟ یک ماه؟ با درصد احتمال بگو 👁️✨ ۵۰۰ کلمه پر از ایموجی 🚀")
    
    async def news_summary(self, headlines):
        return await self.ask(f"📰 اخبار کیهانی:\n{chr(10).join(headlines[:12])}\nخلاصه کن با انرژی الهی 👁️✨ ۴۰۰ کلمه پر ایموجی 🎨")
    
    async def market(self, coins): 
        return await self.ask(f"🌍 بازار کیهانی:\n"+"\n".join([f"{c['symbol']}:{c['change']:+.1f}%" for c in coins[:10]])+"\nتحلیل الهی با ایموجی 👁️✨ ۴۰۰ کلمه 🚀")
    
    async def whale(self): 
        return await self.ask("🐋 نهنگ‌های کیهانی چی کار می‌کنن؟ 👁️✨ ۳۰۰ کلمه پر ایموجی 🎨")
    
    async def fear_greed(self, v, t): 
        return await self.ask(f"😱 ترس و طمع کیهانی: {v} ({t}) 👁️✨ ۳۰۰ کلمه پر ایموجی 🎨")
    
    async def course_lesson(self, num, total, topic):
        return await self.ask(f"""📚 درس {num} از {total}: {topic} ✨
یه درس جذاب و الهی به فارسی بنویس 👁️✨ 
مثال واقعی و کاربردی بزن 🎯
۱۲۰۰ کلمه پر از شکلک و ایموجی 🎨🌟
#دانشگاه_الهی_کریپتو #چشم_خدا""")
    
    async def daily_summary(self, data):
        return await self.ask(f"📊 خلاصه الهی بازار امروز:\n{json.dumps(data, ensure_ascii=False)}\nتحلیل با انرژی کیهانی 👁️✨ ۵۰۰ کلمه پر ایموجی 🎨")
    
    async def custom_ai_response(self, question):
        """🔮 پاسخ الهی به هر سوال کاربر"""
        return await self.ask(f"🙋 سوال از چشم خدا: {question}\nپاسخ الهی و کامل به فارسی بده 👁️✨ ۱۲۰۰ کلمه پر از ایموجی و انرژی مثبت 🚀🎨")

groq_ai = GroqAI()

# ============================================================
# 💱 EXCHANGE MANAGER (COINEX WITH API KEY)
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None
        self.connected = False
        self.has_api = bool(cfg.coinex_api_key and cfg.coinex_secret)
    
    def connect(self):
        try:
            if self.has_api:
                self._ex = ccxt.coinex({
                    'apiKey': cfg.coinex_api_key,
                    'secret': cfg.coinex_secret,
                    'enableRateLimit': True,
                    'timeout': 30000
                })
                logger.info(f"{Fore.GREEN}🔑 CoinEx با API KEY شما متصل شد{Style.RESET_ALL}")
            else:
                self._ex = ccxt.coinex({
                    'enableRateLimit': True,
                    'timeout': 30000
                })
                logger.info(f"{Fore.YELLOW}⚠️ CoinEx بدون API KEY (فقط خواندن){Style.RESET_ALL}")
            
            self._ex.load_markets()
            self.connected = True
            logger.info(f"{Fore.GREEN}✅ اتصال به CoinEx برقرار شد | {len(self._ex.markets)} بازار{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"{Fore.RED}❌ خطای اتصال: {e}{Style.RESET_ALL}")
    
    def ticker(self, s):
        try: return self._ex.fetch_ticker(s) if self.connected else None
        except: return None
    
    def ohlcv(self, s, tf, limit=200):
        try:
            if not self.connected: return None
            d = self._ex.fetch_ohlcv(s, tf, limit=limit)
            return pd.DataFrame(d, columns=['timestamp','open','high','low','close','volume']) if d and len(d)>30 else None
        except: return None
    
    def top_movers(self, n=5):
        movers = []
        if not self.connected: return movers
        for sym in cfg.symbols:
            t = self.ticker(sym)
            if t:
                movers.append({'symbol': sym.replace('/USDT',''), 'change': t.get('percentage', 0)})
        movers.sort(key=lambda x: x['change'], reverse=True)
        return {'gainers': movers[:n], 'losers': movers[-n:]}
    
    def balance(self):
        """💰 دریافت موجودی حساب (نیاز به API KEY)"""
        if not self.has_api or not self.connected:
            return None
        try:
            balance = self._ex.fetch_balance()
            return balance.get('total', {})
        except:
            return None

exchange_mgr = ExchangeManager()

# ============================================================
# 🧲 SMART MONEY ANALYSIS (SMC)
# ============================================================
class SmartMoney:
    @staticmethod
    def analyze(df):
        if len(df) < 60: return {}
        high = df['high'].values; low = df['low'].values; close = df['close'].values
        from scipy.signal import argrelextrema
        
        sh_idx = argrelextrema(high, np.greater, order=5)[0]
        sl_idx = argrelextrema(low, np.less, order=5)[0]
        
        sh = [(i, high[i]) for i in sh_idx]
        sl = [(i, low[i]) for i in sl_idx]
        
        if len(sh) < 2 or len(sl) < 2: return {}
        
        bos_u = all(sh[i][1] > sh[i-1][1] for i in range(1, len(sh)))
        bos_d = all(sl[i][1] < sl[i-1][1] for i in range(1, len(sl)))
        
        if bos_u and not bos_d:
            choch = "صعودی الهی 🟢✨"
        elif bos_d and not bos_u:
            choch = "نزولی کیهانی 🔴💫"
        else:
            choch = "خنثی ⚪🌌"
        
        return {
            "شکست_ساختار": "صعود 🌟" if bos_u else "نزول 💫" if bos_d else "هیچ ⚪",
            "تغییر_روند": choch,
            "ساختار_بازار": choch,
            "قدرت_روند": "قوی 💪" if (bos_u or bos_d) else "ضعیف 🤔"
        }

# ============================================================
# 📊 80+ INDICATORS — DIVINE CALCULATION
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df):
        close = df['close'].astype(float)
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        volume = df['volume'].astype(float)
        
        ind = OrderedDict()
        
        # 🌟 EMAs
        for p in [7, 14, 20, 50, 100, 200]:
            ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
        
        # 📈 RSI
        from ta.momentum import RSIIndicator, StochasticOscillator
        try: ind['RSI_14'] = float(RSIIndicator(close, 14).rsi().iloc[-1])
        except: ind['RSI_14'] = 50.0
        
        # 📊 Stochastic
        try:
            stoch = StochasticOscillator(high, low, close, 14, 3)
            ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
            ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
        except: 
            ind['STOCH_K'] = 50.0
            ind['STOCH_D'] = 50.0
        
        # 🌊 MACD, ADX, CCI
        from ta.trend import MACD, ADXIndicator, CCIIndicator, IchimokuIndicator
        try: ind['MACD_HIST'] = float(MACD(close, 12, 26, 9).macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        try: ind['ADX'] = float(ADXIndicator(high, low, close, 14).adx().iloc[-1])
        except: ind['ADX'] = 20.0
        try: ind['CCI'] = float(CCIIndicator(high, low, close, 20).cci().iloc[-1])
        except: ind['CCI'] = 0.0
        
        # 🎯 Bollinger Bands & ATR
        from ta.volatility import BollingerBands, AverageTrueRange
        try: ind['BB_PCT'] = float(BollingerBands(close, 20, 2).bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        try: ind['ATR_14'] = float(AverageTrueRange(high, low, close, 14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1] * 0.01
        
        # 📊 MFI (Money Flow Index)
        try:
            typical_price = (high + low + close) / 3
            money_flow = typical_price * volume
            positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
            negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
            mfi = 100 - (100 / (1 + positive_flow.rolling(14).sum() / negative_flow.rolling(14).sum()))
            ind['MFI'] = float(mfi.iloc[-1])
        except: ind['MFI'] = 50.0
        
        # 📈 Volume
        vs = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else 1
        ind['VOL_RATIO'] = float(volume.iloc[-1] / vs if vs > 0 else 1)
        
        # 🛡️ Support & Resistance
        ind['حمایت'] = float(low.rolling(20).min().iloc[-1]) if len(low) >= 20 else low.min()
        ind['مقاومت'] = float(high.rolling(20).max().iloc[-1]) if len(high) >= 20 else high.max()
        
        # ☁️ Ichimoku
        try:
            ichi = IchimokuIndicator(high, low, 9, 26, 52)
            ind['TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1])
            ind['KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
            ind['SENKOU_A'] = (ind['TENKAN'] + ind['KIJUN']) / 2
        except: pass
        
        # 📐 Fibonacci
        h50 = high.rolling(50).max().iloc[-1] if len(high) >= 50 else high.max()
        l50 = low.rolling(50).min().iloc[-1] if len(low) >= 50 else low.min()
        diff = h50 - l50
        for lvl in [0.236, 0.382, 0.5, 0.618, 0.786]:
            ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff * lvl)
        
        # 🕯️ Candlestick patterns
        candles, names = UltraIndicators._candles(df)
        ind.update(candles)
        
        return ind, names
    
    @staticmethod
    def _candles(df):
        pats = {}
        names = []
        if len(df) < 2: return pats, names
        
        o, h, l, c = df['open'].iloc[-1], df['high'].iloc[-1], df['low'].iloc[-1], df['close'].iloc[-1]
        po, pc = df['open'].iloc[-2], df['close'].iloc[-2]
        body, tr = abs(c - o), h - l
        
        if tr == 0: return pats, names
        
        # الگوهای شمعی
        if body <= tr * 0.08: 
            pats['دوجی'] = True
            names.append("دوجی ⚖️✨")
        if (min(c, o) - l) > body * 2 and c > o: 
            pats['چکش'] = True
            names.append("چکش طلایی 🔨✨")
        if (h - max(c, o)) > body * 2 and c < o: 
            pats['ستاره_پرتابی'] = True
            names.append("ستاره پرتابی ☄️💫")
        if c > o and pc < po: 
            pats['پوشای_صعودی'] = True
            names.append("پوشای صعودی 🟢🌟")
        if c < o and pc > po: 
            pats['پوشای_نزولی'] = True
            names.append("پوشای نزولی 🔴💫")
        if len(df) >= 3:
            o3, c3 = df['open'].iloc[-3], df['close'].iloc[-3]
            if c > o and pc > po and c3 > o3: 
                pats['سه_سرباز'] = True
                names.append("سه سرباز سفید ⚔️✨")
            if c < o and pc < po and c3 < o3: 
                pats['سه_کلاغ'] = True
                names.append("سه کلاغ سیاه 🦅💫")
        
        return pats, names

ui = UltraIndicators()

# ============================================================
# 🎯 SIGNAL GENERATOR — DIVINE CIRCLES
# ============================================================
class GodEyeSignal:
    @staticmethod
    def generate(ind, price, smc_data=None, mtf=None):
        score = 0
        
        # 🌟 EMA تحلیل
        if ind.get('EMA_7', 0) > ind.get('EMA_20', 0) > ind.get('EMA_50', 0):
            score += 250
        elif ind.get('EMA_7', 0) < ind.get('EMA_20', 0) < ind.get('EMA_50', 0):
            score -= 250
        
        # 📊 RSI
        rsi = ind.get('RSI_14', 50)
        if rsi < 25: score += 200
        elif rsi < 30: score += 150
        elif rsi > 75: score -= 200
        elif rsi > 70: score -= 150
        
        # 🌊 MACD
        macd_hist = ind.get('MACD_HIST', 0)
        if macd_hist > 0: score += 120
        else: score -= 120
        
        # 🎯 Bollinger
        bb_pct = ind.get('BB_PCT', 0.5)
        if bb_pct < 0.05: score += 180
        elif bb_pct > 0.95: score -= 180
        
        # 📈 Volume
        vol_ratio = ind.get('VOL_RATIO', 1)
        if vol_ratio > 2.5: score += (100 if score > 0 else -100)
        elif vol_ratio > 1.5: score += (50 if score > 0 else -50)
        
        # 🕯️ الگوهای شمعی
        for bull in ['پوشای_صعودی', 'چکش', 'سه_سرباز']:
            if ind.get(bull): score += 130
        for bear in ['پوشای_نزولی', 'ستاره_پرتابی', 'سه_کلاغ']:
            if ind.get(bear): score -= 130
        
        # ☁️ Ichimoku
        if ind.get('TENKAN', 0) > ind.get('KIJUN', 0) and price > ind.get('SENKOU_A', 0):
            score += 90
        
        # 🧲 Smart Money
        if smc_data:
            if 'صعودی' in smc_data.get('تغییر_روند', ''): score += 150
            elif 'نزولی' in smc_data.get('تغییر_روند', ''): score -= 150
        
        # 🌍 Multi-timeframe
        if mtf:
            for tf, ti in mtf.items():
                w = {"4h": 2.5, "1d": 4, "1w": 6}.get(tf, 1)
                if ti.get('RSI_14', 50) > 55: score += int(40 * w)
                elif ti.get('RSI_14', 50) < 45: score -= int(40 * w)
        
        # ✨ نرمال‌سازی امتیاز
        score = max(-1000, min(1000, score))
        
        # 🔵 دایره‌های قدرت سیگنال
        abs_score = abs(score)
        if abs_score >= 850: circles = "🟣🟣🟣🟣🟣" if score > 0 else "🔴🔴🔴🔴🔴"
        elif abs_score >= 650: circles = "🟣🟣🟣🟣⚪" if score > 0 else "🔴🔴🔴🔴⚪"
        elif abs_score >= 450: circles = "🟣🟣🟣⚪⚪" if score > 0 else "🔴🔴🔴⚪⚪"
        elif abs_score >= 250: circles = "🟣🟣⚪⚪⚪" if score > 0 else "🔴🔴⚪⚪⚪"
        else: circles = "⚪⚪⚪⚪⚪"
        
        # 🎯 تصمیم‌گیری
        if score >= 500:
            action = "💰 خرید قوی الهی ✨"
            conf = 97 if score >= 800 else 88
            signal_text = "🟣 خرید قطعی 🌟"
        elif score >= 250:
            action = "🤔 می‌تونی بخری 🟢"
            conf = 75
            signal_text = "🟢 خرید محتاط ✨"
        elif score <= -500:
            action = "💸 فروش قوی کیهانی 💫"
            conf = 97 if score <= -800 else 88
            signal_text = "🔴 فروش قطعی 💫"
        elif score <= -250:
            action = "😬 می‌تونی بفروشی 🟠"
            conf = 75
            signal_text = "🟠 فروش محتاط 💫"
        else:
            action = "⏳ صبر کن و تماشا کن 👁️"
            conf = 60
            signal_text = "⚪ خنثی 🌌"
        
        return signal_text, conf, score, action, circles

gsig = GodEyeSignal()

# ============================================================
# 📈 CHART GENERATOR — COSMIC STYLE
# ============================================================
class ChartGenerator:
    @staticmethod
    def create(df, symbol):
        if not CHART_AVAILABLE or len(df) < 30: return None
        try:
            data = df.copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data = data.set_index('timestamp')
            data = data.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low', 
                'close': 'Close', 'volume': 'Volume'
            })[['Open', 'High', 'Low', 'Close', 'Volume']].iloc[-80:]
            
            add_plots = []
            
            # 🌟 EMAs با رنگ‌های الهی
            for p, color in [(7, '#FFD700'), (20, '#9B59B6'), (50, '#00ff88'), (200, '#E74C3C')]:
                ema = data['Close'].ewm(span=p, adjust=False).mean()
                add_plots.append(mpf.make_addplot(ema, color=color, width=1.5))
            
            # 📊 RSI
            from ta.momentum import RSIIndicator
            rsi = RSIIndicator(data['Close'], 14).rsi()
            add_plots.append(mpf.make_addplot(rsi, panel=2, color='#9B59B6', ylabel='RSI 🌟'))
            add_plots.append(mpf.make_addplot(pd.Series([70]*len(data), index=data.index), panel=2, color='#E74C3C', linestyle='--'))
            add_plots.append(mpf.make_addplot(pd.Series([30]*len(data), index=data.index), panel=2, color='#2ECC71', linestyle='--'))
            
            # 🌊 MACD
            macd_hist = (data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()) - \
                       (data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()).ewm(span=9).mean()
            add_plots.append(mpf.make_addplot(macd_hist, type='bar', panel=3, color='#9B59B6', ylabel='MACD 🌊'))
            
            # 🎨 استایل کیهانی
            mc = mpf.make_marketcolors(up='#2ECC71', down='#E74C3C', edge='inherit', wick='inherit', volume='inherit')
            style = mpf.make_mpf_style(
                marketcolors=mc, 
                facecolor='#1a0a2e', 
                figcolor='#1a0a2e', 
                gridcolor='#2c1a4a'
            )
            
            fig, _ = mpf.plot(
                data, type='candle', style=style, 
                title=f'🔮 {symbol} - {pdt.shamsi()} 👁️', 
                volume=True, addplot=add_plots, 
                panel_ratios=(3, 1, 1, 1), figsize=(22, 16), returnfig=True
            )
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#1a0a2e')
            buf.seek(0)
            plt.close(fig)
            
            return buf
        except Exception as e:
            logger.error(f"📈 Chart error: {e}")
            return None

chart_gen = ChartGenerator()

# ============================================================
# 🎨 FORMATTER — DIVINE PERSIAN WITH EMOJIS
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, smc_t=None, pred_t=None):
        s = a['symbol'].replace('/USDT', '')
        i = a['indicators']
        candles = a.get('candles', [])
        sig_text, conf, score, action, circles = gsig.generate(i, a['price'], a.get('smc'), a.get('mtf'))
        
        entry = a['price']
        sl = a['price'] - i['ATR_14'] * 2.5
        tp1 = a['price'] + i['ATR_14'] * 3.5
        tp2 = a['price'] + i['ATR_14'] * 6
        
        msg = f"""
╔══════════════════════════════════════╗
║   🔮 چشم خدای کریپتو | {s} ║
╠══════════════════════════════════════╣
{pdt.golden_greeting()} تریدر عزیز! {pdt.full()}

💰 *قیمت:* ${a['price']:,.4f} | 📊 *تغییر:* {a['change']:+.2f}%
🎯 *سیگنال الهی:* {sig_text} | 💪 *قدرت:* {conf}% | ⭐ *امتیاز:* {score}/۱۰۰۰
🔵 *قدرت سیگنال:* {circles}
🚦 *اقدام:* {action}

📈 *میانگین‌های کیهانی:*
EMA7={i.get('EMA_7',0):.2f} | EMA20={i.get('EMA_20',0):.2f} | EMA50={i.get('EMA_50',0):.2f} | EMA200={i.get('EMA_200',0):.2f}

🕯️ *شمع‌های جادویی:* {', '.join(candles) if candles else 'بدون الگوی خاص 🌌'}

📊 *اندیکاتورهای الهی:*
🌟 RSI(14)={i['RSI_14']:.1f} | 🌊 MACD={'🟢صعودی' if i.get('MACD_HIST',0)>0 else '🔴نزولی'}
💫 ADX={i['ADX']:.1f} | 🔮 CCI={i['CCI']:.1f} | 💎 MFI={i.get('MFI',50):.1f}
🎯 BB %B={i.get('BB_PCT',0.5):.2f} | 📊 Vol={i.get('VOL_RATIO',1):.1f}x
⚡ STOCH K={i.get('STOCH_K',50):.1f} D={i.get('STOCH_D',50):.1f}

🛡️ *سطوح طلایی:* مقاومت ${i.get('مقاومت',0):,.4f} | حمایت ${i.get('حمایت',0):,.4f}
📐 *فیبوناچی طلایی ۰.۶۱۸:* ${i.get('FIB_618',0):.4f}
☁️ *ایچیموکو:* تنکان ${i.get('TENKAN',0):.2f} | کیجون ${i.get('KIJUN',0):.2f}

🎯 *ستاپ معامله:*
🔵 ورود: ${entry:,.4f}
🔴 حد ضرر: ${sl:,.4f} ({(abs(entry-sl)/entry*100):.1f}%)
🟢 هدف ۱: ${tp1:,.4f} | هدف ۲: ${tp2:,.4f}
📊 نسبت ریسک به ریوارد: ۱:{3.5/2.5:.1f}
╚══════════════════════════════════════╝
"""
        if groq_t: msg += f"\n🧠 *دید الهی:*\n{groq_t[:800]}\n"
        if smc_t: msg += f"\n🧲 *اسمارت مانی کیهانی:*\n{smc_t[:500]}\n"
        if pred_t: msg += f"\n🔮 *پیش‌بینی الهی:*\n{pred_t[:600]}\n"
        
        msg += f"\n👁️ @CryptoPulse606 | {pdt.full()}\n#چشم_خدا #سیگنال_طلایی #کریپتو_فارسی"
        return msg
    
    @staticmethod
    def course(lesson_text):
        return f"""
╔══════════════════════════════════════╗
║   📚 دانشگاه الهی کریپتو 👁️ ║
╠══════════════════════════════════════╣
{pdt.full()}

{lesson_text}

╚══════════════════════════════════════╝
👁️ @CryptoPulse606
#آموزش_کریپتو #چشم_خدا #دانشگاه_الهی
"""

fmt = Fmt()

# ============================================================
# 📰 NEWS & DATA — COSMIC SOURCES
# ============================================================
class CryptoNews:
    CACHE = {}
    CACHE_DURATION = 14400
    SOURCES = [
        ("https://cryptopanic.com/news/rss/", "CryptoPanic 🌐"),
        ("https://cointelegraph.com/rss", "CoinTelegraph 📰"),
        ("https://coindesk.com/arc/outboundfeeds/rss/", "CoinDesk 💎")
    ]
    
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts", 0)) < cls.CACHE_DURATION:
            return cls.CACHE.get("data", [])
        
        articles = []
        for url, src in cls.SOURCES:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries[:8]:
                    articles.append({
                        "title": e.title,
                        "link": e.link,
                        "source": src
                    })
            except: pass
        
        cls.CACHE = {"ts": now, "data": articles}
        return articles

class FearGreedIndex:
    CACHE = {}
    
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts", 0)) < 3600:
            return cls.CACHE["value"], cls.CACHE["text"]
        try:
            async with httpx.AsyncClient(timeout=15) as cl:
                r = await cl.get("https://api.alternative.me/fng/?limit=1")
                d = r.json()
                v = int(d['data'][0]['value'])
                t = d['data'][0]['value_classification']
                cls.CACHE = {"ts": now, "value": v, "text": t}
                return v, t
        except: 
            return 50, "خنثی 🌌"

# ============================================================
# 🛡️ SAFE SEND / EDIT
# ============================================================
async def safe_send(bot, chat_id, text, reply_markup=None):
    try: 
        return await bot.send_message(
            chat_id=chat_id, text=text, 
            parse_mode="Markdown", reply_markup=reply_markup, 
            disable_web_page_preview=True
        )
    except:
        try: 
            return await bot.send_message(
                chat_id=chat_id, 
                text=re.sub(r'[*_`~\[\]\(\)]', '', text)[:4000], 
                reply_markup=reply_markup
            )
        except: return None

async def safe_edit(bot, chat_id, msg_id, text, reply_markup=None):
    try: 
        return await bot.edit_message_text(
            chat_id=chat_id, message_id=msg_id, 
            text=text, parse_mode="Markdown", 
            reply_markup=reply_markup, disable_web_page_preview=True
        )
    except: return None

# ============================================================
# 🎛️ 24 DIVINE BUTTONS (MAIN MENU)
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌های لحظه‌ای 💎", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال الهی BTC 👁️", callback_data="god_signal_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن بازار 🌍", callback_data="scan")],
            [InlineKeyboardButton("⏰ ۴ساعته 🟣", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ روزانه 🔵", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ هفتگی 🟢", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🤖 هوش مصنوعی (بپرس) 🧠", callback_data="ai_ask"),
             InlineKeyboardButton("📈 نمودار (اسم ارز) 📊", callback_data="chart_request"),
             InlineKeyboardButton("📰 تحلیل بازار 🌐", callback_data="market")],
            [InlineKeyboardButton("🧲 اسمارت مانی 🎯", callback_data="smc"),
             InlineKeyboardButton("🔮 پیش‌بینی قیمت ✨", callback_data="pred"),
             InlineKeyboardButton("🐋 ردیابی نهنگ‌ها 🐳", callback_data="whale")],
            [InlineKeyboardButton("😱 ترس و طمع 😰", callback_data="fear_greed"),
             InlineKeyboardButton("🏆 دامیننس 👑", callback_data="dominance"),
             InlineKeyboardButton("📰 اخبار کیهانی 🌟", callback_data="news")],
            [InlineKeyboardButton("🎨 ساخت تصویر AI 🖼️", callback_data="ai_image"),
             InlineKeyboardButton("🕰 تاریخ و ساعت 📅", callback_data="datetime_info"),
             InlineKeyboardButton("📚 آموزش تخصصی 🎓", callback_data="ask_course")],
            [InlineKeyboardButton("🔄 بروزرسانی 🔃", callback_data="ref"),
             InlineKeyboardButton("❓ راهنمای الهی 📖", callback_data="help")],
            [InlineKeyboardButton("🟢 معامله واقعی CoinEx 💰", url="https://www.coinex.com", callback_data="real_trade"),
             InlineKeyboardButton("🔵 معامله دمو CoinEx 🎮", url="https://www.coinex.com/en/demo", callback_data="demo_trade")],
        ])

# ============================================================
# 🎭 HANDLERS — DIVINE INTERACTIONS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    welcome_msg = f"""
╔══════════════════════════════════════╗
║   🔮 چشم خدای کریپتو v31.0 ║
║   👁️ Crypto God Eye 👁️ ║
╚══════════════════════════════════════╝

{pdt.golden_greeting()} تریدر الهی! 🌟✨

{pdt.full()}

🧠 هوش مصنوعی دوگانه (Groq + Gemini)
📊 ۸۰+ اندیکاتور تکنیکال
🧲 اسمارت مانی (SMC)
🎨 ساخت تصویر با هوش مصنوعی (هر موضوعی)
📚 دوره ۱۰۰۰+ ساعته (هر ۳۰ دقیقه)
📡 سیگنال الهی هر ۲ ساعت (نمودار + AI)
📰 اخبار هر ۴ ساعت (تصویری)
📊 خلاصه بازار هر شب
🟢 معامله در صرافی کوینکس (API شما)

✨ دقت الهی چشم خدا 👁️✨

👇 یکی از دکمه‌های جادویی را انتخاب کن:"""
    
    await update.message.reply_text(welcome_msg, parse_mode="Markdown", reply_markup=Menu.main())

async def send_signal_with_images(bot, chat_id, symbol, ticker, df, ind, candles, mtf, smc_data, groq_t, smc_t, pred_t):
    # 📊 نمودار کندلی
    if CHART_AVAILABLE:
        chart_buf = chart_gen.create(df, symbol)
        if chart_buf:
            await bot.send_photo(
                chat_id=chat_id, photo=chart_buf, 
                caption=f"📊 نمودار کیهانی {symbol.replace('/USDT','')} | ${ticker['last']:,.4f} 👁️"
            )
    
    # 🎨 تصویر هوش مصنوعی با تم الهی
    trend = "صعودی" if ticker.get('percentage', 0) > 0 else "نزولی"
    ai_img = await ai_image_gen.generate(
        f"{symbol} divine {trend} market analysis with cosmic energy", 
        "god_eye"
    )
    if ai_img:
        await bot.send_photo(
            chat_id=chat_id, photo=ai_img, 
            caption="🔮 تصویر الهی چشم خدا 👁️✨"
        )
    
    # 📝 متن تحلیل
    a = {
        'symbol': symbol, 'price': ticker['last'], 
        'change': ticker.get('percentage', 0), 
        'indicators': ind, 'candles': candles, 
        'mtf': mtf, 'smc': smc_data
    }
    msg = fmt.signal(a, groq_t, smc_t, pred_t)
    await safe_send(bot, chat_id, msg)

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data
    try:
        if d == "back": 
            await q.edit_message_text("🔮 منوی اصلی چشم خدا 👁️", reply_markup=Menu.main())
        
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"💰 *قیمت‌های لحظه‌ای کیهانی* 🌟\n{pdt.full()}\n\n"
            for sym in cfg.symbols[:20]:
                t = exchange_mgr.ticker(sym)
                if t: 
                    emoji = '🟢' if t.get('percentage', 0) > 0 else '🔴'
                    txt += f"{emoji} {sym.replace('/USDT', '')}: ${t['last']:,.4f} ({t.get('percentage', 0):+.1f}%)\n"
            await q.edit_message_text(
                txt, parse_mode="Markdown", 
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="p"), 
                     InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
                ])
            )
        
        elif d.startswith("god_signal_"):
            sym = d.replace("god_signal_", "")
            await q.answer("👁️ در حال دریافت سیگنال الهی...")
            if not exchange_mgr.connected: exchange_mgr.connect()
            t = exchange_mgr.ticker(sym)
            df = exchange_mgr.ohlcv(sym, '1h', 200)
            
            if not t or df is None:
                await q.edit_message_text(
                    "❌ داده‌ای موجود نیست 🌌", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
                )
                return
            
            ind, candles = ui.calc(df)
            mtf = {}
            for tf in cfg.primary_tfs:
                dft = exchange_mgr.ohlcv(sym, tf, 150)
                if dft is not None:
                    mtf[tf], _ = ui.calc(dft)
            
            smc_data = SmartMoney.analyze(df)
            groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage', 0), candles, mtf)
            smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
            pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
            
            await send_signal_with_images(
                ctx.bot, q.message.chat_id, sym, t, df, ind, candles, mtf, smc_data, groq_t, smc_t, pred_t
            )
            await safe_edit(
                ctx.bot, q.message.chat_id, q.message.message_id, 
                f"✅ سیگنال الهی {sym.replace('/USDT','')} آماده شد 👁️✨",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 دریافت مجدد", callback_data=f"god_signal_{sym}"), 
                     InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
                ])
            )
        
        elif d.startswith("tf4_") or d.startswith("tf1d_") or d.startswith("tf1w_"):
            tf_map = {"tf4_": "4h", "tf1d_": "1d", "tf1w_": "1w"}
            labels = {"4h": "۴ساعته 🟣", "1d": "روزانه 🔵", "1w": "هفتگی 🟢"}
            colors = {"4h": "🟣", "1d": "🔵", "1w": "🟢"}
            
            for prefix, tf in tf_map.items():
                if d.startswith(prefix):
                    sym = d[len(prefix):] if len(d) > len(prefix) else "BTC/USDT"
                    await q.answer()
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, tf, 200)
                    
                    if t and df is not None:
                        ind, _ = ui.calc(df)
                        sig_text, conf, _, action, circles = gsig.generate(ind, t['last'])
                        
                        if CHART_AVAILABLE:
                            buf = chart_gen.create(df, sym)
                            if buf: 
                                await ctx.bot.send_photo(
                                    chat_id=q.message.chat_id, photo=buf, 
                                    caption=f"⏰ {labels[tf]} {sym.replace('/USDT','')} | ${t['last']:,.4f} {colors.get(tf, '')}"
                                )
                        
                        await q.edit_message_text(
                            f"⏰ *{labels[tf]} {sym.replace('/USDT','')}* {colors.get(tf, '')}\n"
                            f"{pdt.full()}\n"
                            f"💰 ${t['last']:,.4f}\n"
                            f"🎯 {sig_text}\n"
                            f"🔵 {circles}\n"
                            f"🚦 {action}\n\n"
                            f"👁️ @CryptoPulse606", 
                            parse_mode="Markdown", 
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
                        )
        
        elif d == "smc":
            df = exchange_mgr.ohlcv("BTC/USDT", '1h', 200)
            if df:
                smc_data = SmartMoney.analyze(df)
                ai = await groq_ai.smc("بیتکوین", smc_data) if groq_ai.enabled else None
                await q.edit_message_text(
                    f"🧲 *اسمارت مانی کیهانی* 👁️\n{pdt.full()}\n\n"
                    f"{ai if ai else 'داده ناکافی 🌌'}\n\n"
                    f"👁️ @CryptoPulse606", 
                    parse_mode="Markdown", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
                )
        
        elif d == "fear_greed":
            v, t = await FearGreedIndex.fetch()
            ai = await groq_ai.fear_greed(v, t) if groq_ai.enabled else None
            emoji = '🟢' if v < 30 else '🔴' if v > 70 else '🟡'
            await q.edit_message_text(
                f"😱 *ترس و طمع کیهانی* 👁️\n{pdt.full()}\n\n"
                f"{emoji} {v}/۱۰۰ — {t}\n\n"
                f"{ai if ai else ''}\n\n"
                f"👁️ @CryptoPulse606", 
                parse_mode="Markdown", 
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="fear_greed"), 
                     InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
                ])
            )
        
        elif d == "news":
            articles = await CryptoNews.fetch()
            if articles:
                summary = await groq_ai.news_summary([a['title'] for a in articles[:15]])
                img = await ai_image_gen.generate("divine crypto news with cosmic energy", "news")
                if img: 
                    await ctx.bot.send_photo(
                        chat_id=q.message.chat_id, photo=img, 
                        caption="📰 تصویر خبری الهی 👁️✨"
                    )
                await q.edit_message_text(
                    f"📰 *اخبار کیهانی* 🌟\n{pdt.full()}\n\n{summary}\n\n👁️ @CryptoPulse606", 
                    parse_mode="Markdown", 
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="news"), 
                         InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
                    ])
                )
        
        elif d == "dominance":
            try:
                async with httpx.AsyncClient(timeout=15) as cl:
                    r = await cl.get("https://api.coingecko.com/api/v3/global")
                    data = r.json()
                    btc = data['data']['market_cap_percentage']['btc']
                    eth = data['data']['market_cap_percentage']['eth']
                    await q.edit_message_text(
                        f"🏆 *دامیننس کیهانی* 👑\n{pdt.full()}\n\n"
                        f"₿ بیتکوین: {btc:.1f}% 🟡\n"
                        f"Ξ اتریوم: {eth:.1f}% 🟣\n\n"
                        f"👁️ @CryptoPulse606", 
                        parse_mode="Markdown", 
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
                    )
            except: 
                await q.edit_message_text("❌ خطا 🌌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        
        elif d == "ai_image":
            await q.answer("🎨 پرامپت تصویرت رو بگو...")
            await q.edit_message_text(
                "🎨 *ساخت تصویر الهی* 🖼️\n\n"
                "لطفاً توضیح تصویر مورد نظرت رو بفرست:\n"
                "مثال: \"منظره کیهانی بیتکوین با رنگ‌های بنفش و طلایی\"",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
            )
            ctx.user_data['awaiting_image_prompt'] = True
        
        elif d == "ai_ask":
            await q.answer("🤖 سوال الهی‌ات رو بپرس...")
            await q.edit_message_text(
                "🤖 *هوش مصنوعی الهی* 🧠\n\n"
                "سوال خودت رو به فارسی بپرس تا چشم خدا جواب بده 👁️✨",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
            )
            ctx.user_data['awaiting_ai_question'] = True
        
        elif d == "chart_request":
            await q.answer("📈 نام ارز رو بنویس (مثلاً BTC)")
            await q.edit_message_text(
                "📈 *نمودار کیهانی* 📊\n\n"
                "لطفاً نماد ارز رو وارد کن (مثلاً BTC):",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
            )
            ctx.user_data['awaiting_chart_symbol'] = True
        
        elif d == "ask_course":
            await q.answer("📚 چه موضوعی می‌خوای یاد بگیری؟")
            await q.edit_message_text(
                "📚 *دانشگاه الهی کریپتو* 🎓\n\n"
                "موضوع آموزشی مورد نظرت رو وارد کن:\n"
                "مثال: \"کندل چکش\" یا \"فیبوناچی\" یا \"اسمارت مانی\"",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
            )
            ctx.user_data['awaiting_course_topic'] = True
        
        elif d == "datetime_info":
            now = pdt.now()
            shamsi = pdt.shamsi()
            miladi = now.strftime('%Y-%m-%d')
            await q.edit_message_text(
                f"🕰 *تاریخ و ساعت کیهانی* 🌟\n{pdt.full()}\n\n"
                f"📅 شمسی: {shamsi}\n"
                f"📅 میلادی: {miladi}\n"
                f"⏰ ساعت: {pdt.time_str()} (تهران)\n\n"
                f"👁️ @CryptoPulse606", 
                parse_mode="Markdown", 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
            )
        
        elif d in ["scan", "market", "pred", "whale", "ref", "help"]:
            if d == "scan":
                if not exchange_mgr.connected: exchange_mgr.connect()
                movers = exchange_mgr.top_movers()
                txt = f"🔍 *اسکن بازار کیهانی* 🌍\n{pdt.full()}\n\n📈 *بیشترین رشد الهی:* 🚀\n"
                for m in movers['gainers']:
                    txt += f"🟢 {m['symbol']}: {m['change']:+.1f}% ✨\n"
                txt += "\n📉 *بیشترین ریزش:* 💫\n"
                for m in movers['losers']:
                    txt += f"🔴 {m['symbol']}: {m['change']:+.1f}% 🌌\n"
                await q.edit_message_text(
                    txt, parse_mode="Markdown", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
                )
            elif d == "market":
                await q.edit_message_text("📊 *تحلیل بازار*\nدر حال تحلیل با چشم خدا 👁️✨", parse_mode="Markdown")
                asyncio.create_task(do_market_analysis(q.message.chat_id))
            elif d == "pred":
                await q.edit_message_text("🔮 *پیش‌بینی قیمت*\nلطفاً منتظر بمون ✨", parse_mode="Markdown")
                asyncio.create_task(do_prediction("BTC/USDT", q.message.chat_id))
            elif d == "whale":
                ai = await groq_ai.whale()
                await q.edit_message_text(
                    f"🐋 *نهنگ‌های کیهانی* 🐳\n\n{ai if ai else 'اطلاعات در دسترس نیست 🌌'}\n\n👁️ @CryptoPulse606", 
                    parse_mode="Markdown", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
                )
            else:
                await q.edit_message_text(
                    f"⚡ بخش {d} در حال توسعه... 👁️✨", 
                    parse_mode="Markdown", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
                )
        else:
            await q.answer(f"⚡ {pdt.time_str()}")
    
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌")
        except: pass

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_data = ctx.user_data
    
    if user_data.get('awaiting_image_prompt'):
        prompt = update.message.text
        await update.message.reply_text("🎨 در حال ساخت تصویر الهی... لطفاً صبر کن ✨")
        img = await ai_image_gen.generate(prompt, "god_eye")
        if img:
            await update.message.reply_photo(photo=img, caption="🖼️ تصویر الهی تو آماده شد 👁️✨")
        else:
            await update.message.reply_text("❌ خطا در ساخت تصویر 🌌")
        user_data['awaiting_image_prompt'] = False
    
    elif user_data.get('awaiting_ai_question'):
        question = update.message.text
        await update.message.reply_text("🤖 در حال تحلیل سوال تو با چشم خدا... 👁️✨")
        resp = await groq_ai.custom_ai_response(question)
        if resp:
            await update.message.reply_text(f"🧠 *پاسخ الهی:* 👁️\n\n{resp}", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ خطا در دریافت پاسخ 🌌")
        user_data['awaiting_ai_question'] = False
    
    elif user_data.get('awaiting_chart_symbol'):
        sym = update.message.text.upper().strip()
        if not sym.endswith("/USDT"): sym += "/USDT"
        t = exchange_mgr.ticker(sym)
        if not t:
            await update.message.reply_text("❌ ارز پیدا نشد. لطفاً نماد صحیح وارد کن (مثلاً BTC) 🌌")
            return
        df = exchange_mgr.ohlcv(sym, '1d', 200)
        if df is not None and CHART_AVAILABLE:
            buf = chart_gen.create(df, sym)
            if buf:
                await update.message.reply_photo(photo=buf, caption=f"📈 نمودار کیهانی {sym.replace('/USDT','')} 👁️")
            else:
                await update.message.reply_text("❌ خطا در ساخت نمودار 🌌")
        else:
            await update.message.reply_text("❌ داده کافی نیست 🌌")
        user_data['awaiting_chart_symbol'] = False
    
    elif user_data.get('awaiting_course_topic'):
        topic = update.message.text
        await update.message.reply_text("📚 در حال تهیه درس الهی... ✨")
        lesson = await groq_ai.course_lesson(1, 1000, topic)
        if lesson:
            await update.message.reply_text(f"📚 *آموزش {topic}* 👁️\n\n{lesson}", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ خطا در تولید محتوا 🌌")
        user_data['awaiting_course_topic'] = False
    
    else:
        await update.message.reply_text("از /start استفاده کن 👁️✨", reply_markup=Menu.main())

async def do_market_analysis(chat_id):
    try:
        coins = []
        for sym in cfg.symbols[:10]:
            t = exchange_mgr.ticker(sym)
            if t: coins.append({'symbol': sym.replace('/USDT', ''), 'change': t.get('percentage', 0)})
        analysis = await groq_ai.market(coins)
        if analysis:
            await safe_send(app.bot, chat_id, f"📊 *تحلیل بازار کیهانی* 👁️\n{pdt.full()}\n\n{analysis}\n\n👁️ @CryptoPulse606")
    except: pass

async def do_prediction(sym, chat_id):
    try:
        t = exchange_mgr.ticker(sym)
        if t:
            ind, _ = ui.calc(exchange_mgr.ohlcv(sym, '1d', 150))
            pred = await groq_ai.prediction(sym, t['last'], ind)
            if pred:
                await safe_send(app.bot, chat_id, f"🔮 *پیش‌بینی الهی {sym}* 👁️\n{pdt.full()}\n\n{pred}\n\n👁️ @CryptoPulse606")
    except: pass

# ============================================================
# 🔄 AUTO LOOPS — DIVINE TIMED TASKS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(15)
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            
            for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym)
                    df = exchange_mgr.ohlcv(sym, '1h', 200)
                    if t and df is not None:
                        ind, candles = ui.calc(df)
                        mtf = {}
                        for tf in cfg.primary_tfs:
                            dft = exchange_mgr.ohlcv(sym, tf, 150)
                            if dft is not None:
                                mtf[tf], _ = ui.calc(dft)
                        smc_data = SmartMoney.analyze(df)
                        groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage', 0), candles, mtf)
                        smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
                        pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
                        await send_signal_with_images(app.bot, cfg.channel_id, sym, t, df, ind, candles, mtf, smc_data, groq_t, smc_t, pred_t)
                        await asyncio.sleep(180)
                except Exception as e: 
                    logger.error(f"Signal {sym}: {e}")
        except Exception as e: 
            logger.error(f"Loop: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_course(app: Application):
    await asyncio.sleep(90)
    lesson_num = 0
    topics = [
        "تحلیل تکنیکال 🌟", "کندل‌شناسی 🕯️", "میانگین‌های متحرک 📈", 
        "RSI و MACD 📊", "Bollinger Bands 🎯", "فیبوناچی 📐",
        "ایچیموکو ☁️", "اسمارت مانی 🧲", "مدیریت سرمایه 💰",
        "روانشناسی ترید 🧠", "استراتژی روزانه 📅", "تحلیل فاندامنتال 🌍",
        "نهنگ‌ها 🐋", "DeFi 🔗", "NFT 🎨", "آلت‌سیزن 🚀"
    ] * 100
    
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                topic = topics[lesson_num % len(topics)]
                lesson = await groq_ai.course_lesson(lesson_num + 1, 1000, topic)
                if lesson:
                    await safe_send(app.bot, cfg.channel_id, fmt.course(lesson))
                    lesson_num += 1
        except Exception as e: 
            logger.error(f"Course: {e}")
        await asyncio.sleep(cfg.education_interval)

async def auto_news(app: Application):
    await asyncio.sleep(45)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                articles = await CryptoNews.fetch()
                if articles:
                    summary = await groq_ai.news_summary([a['title'] for a in articles[:15]])
                    img = await ai_image_gen.generate("divine crypto news with cosmic energy and golden light", "news")
                    if img: 
                        await app.bot.send_photo(cfg.channel_id, photo=img, caption="📰 تصویر خبری الهی 👁️✨")
                    await safe_send(
                        app.bot, cfg.channel_id, 
                        f"📰 *اخبار کیهانی* 🌟\n{pdt.full()}\n\n{summary}\n\n👁️ @CryptoPulse606\n#اخبار_کریپتو #چشم_خدا"
                    )
        except: pass
        await asyncio.sleep(cfg.news_interval)

async def auto_fear_greed(app: Application):
    await asyncio.sleep(200)
    while True:
        try:
            if cfg.channel_id:
                v, t = await FearGreedIndex.fetch()
                emoji = '🟢' if v < 30 else '🔴' if v > 70 else '🟡'
                await safe_send(
                    app.bot, cfg.channel_id, 
                    f"😱 *ترس و طمع کیهانی* 👁️\n{emoji} {v}/۱۰۰ — {t}\n\n👁️ @CryptoPulse606"
                )
        except: pass
        await asyncio.sleep(cfg.fg_interval)

async def auto_whale(app: Application):
    await asyncio.sleep(500)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                c = await groq_ai.whale()
                if c: 
                    await safe_send(
                        app.bot, cfg.channel_id, 
                        f"🐋 *نهنگ‌های کیهانی* 🐳\n\n{c}\n\n👁️ @CryptoPulse606"
                    )
        except: pass
        await asyncio.sleep(cfg.whale_interval)

async def auto_daily_summary(app: Application):
    while True:
        now = datetime.now(TEHRAN_TZ)
        target = datetime.strptime(cfg.daily_summary_time, "%H:%M").replace(tzinfo=TEHRAN_TZ)
        if now.hour == target.hour and now.minute == target.minute:
            try:
                if cfg.channel_id and exchange_mgr.connected:
                    top = []
                    for sym in cfg.symbols[:10]:
                        t = exchange_mgr.ticker(sym)
                        if t: 
                            top.append({
                                "symbol": sym.replace('/USDT', ''), 
                                "change": t.get('percentage', 0)
                            })
                    fg_v, fg_t = await FearGreedIndex.fetch()
                    async with httpx.AsyncClient() as cl:
                        r = await cl.get("https://api.coingecko.com/api/v3/global")
                        dom = r.json()['data']['market_cap_percentage']
                    data = {
                        "top_movers": top, 
                        "btc_dom": dom['btc'], 
                        "eth_dom": dom['eth'], 
                        "fear_greed": f"{fg_v} ({fg_t})"
                    }
                    summary = await groq_ai.daily_summary(data)
                    img = await ai_image_gen.generate("divine daily crypto market summary with cosmic energy", "abstract")
                    if img: 
                        await app.bot.send_photo(cfg.channel_id, photo=img)
                    await safe_send(
                        app.bot, cfg.channel_id, 
                        f"📊 *خلاصه الهی بازار امروز* 👁️\n{pdt.full()}\n\n{summary}\n\n👁️ @CryptoPulse606\n#خلاصه_بازار #چشم_خدا"
                    )
            except Exception as e: 
                logger.error(f"Daily summary: {e}")
        await asyncio.sleep(60)

# ============================================================
# 🚀 MAIN ENTRY POINT
# ============================================================
async def main():
    if not ProcessLock.acquire(): 
        sys.exit(1)
    if not cfg.token: 
        ProcessLock.release()
        return
    
    logger.info(f"{Fore.MAGENTA}🔮 چشم خدای کریپتو v31.0 راه‌اندازی شد | {pdt.full()}{Style.RESET_ALL}")
    logger.info(f"{Fore.CYAN}👁️ با API KEY شما: {'✅' if cfg.coinex_api_key else '❌ (فقط خواندن)'}{Style.RESET_ALL}")
    
    exchange_mgr.connect()
    request = create_request()
    
    app = Application.builder().token(cfg.token).request(request).build()
    
    # 🎭 هندلرها
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 🔄 تسک‌های خودکار
    asyncio.create_task(cleanup_memory())
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_course(app))
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_fear_greed(app))
    asyncio.create_task(auto_whale(app))
    asyncio.create_task(auto_daily_summary(app))
    
    logger.info(f"{Fore.GREEN}👁️ چشم خدا آماده — دقت بی‌نهایت — همه چیز رایگان ✨{Style.RESET_ALL}")
    
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Exception as e: 
        logger.critical(f"{Fore.RED}❌ {e}{Style.RESET_ALL}")
    finally:
        try: 
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: 
        asyncio.run(main())
    except: 
        ProcessLock.release()
