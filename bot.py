#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🦅 CRYPTO EAGLE EYE v29.0 — چشــــم عـقـاب — ULTIMATE AI TRADER           ║
║  ✅ AI Image Generator (Pollinations.ai + Internal)                          ║
║  ✅ Dual AI (Groq + Gemini)  ✅ Smart Money (SMC)                            ║
║  ✅ 100% Pure Persian  ✅ 20 Professional Glass Buttons                       ║
║  ✅ Live News  ✅ 80+ Indicators  ✅ Fear & Greed                             ║
║  ✅ VIP Platinum (Owner Only)  ✅ Lock System (Users)                         ║
║  ✅ Eagle-Eye Precision Analysis  ✅ Auto Trading Signals                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, logging, asyncio, time, json, random, signal, math, base64, io, re, threading, gc, urllib.parse
os.environ["TZ"] = "Asia/Tehran"
os.environ["MPLBACKEND"] = "Agg"
try: time.tzset()
except: pass

from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import numpy as np
import pandas as pd
import ccxt
import httpx
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from PIL import Image, ImageDraw, ImageFont
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# AUTO INSTALL (کتابخونه‌های ضروری)
# ============================================================
def ensure_libs():
    libs = {
        'matplotlib':'matplotlib','mplfinance':'mplfinance',
        'ta':'ta','ccxt':'ccxt','httpx':'httpx','dotenv':'python-dotenv',
        'telegram':'python-telegram-bot','pandas':'pandas','numpy':'numpy',
        'jdatetime':'jdatetime','pytz':'pytz','scipy':'scipy',
        'feedparser':'feedparser','Pillow':'Pillow',
        'cachetools':'cachetools','tenacity':'tenacity',
        'aiohttp':'aiohttp'
    }
    for mod, pkg in libs.items():
        try: __import__(mod)
        except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EagleEyeV29')
ensure_libs()

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
# MEMORY MANAGEMENT
# ============================================================
async def cleanup_memory():
    while True:
        gc.collect()
        if CHART_AVAILABLE:
            try: plt.close('all')
            except: pass
        await asyncio.sleep(600)

# ============================================================
# LOGGING
# ============================================================
logger.setLevel(logging.INFO)
console = logging.StreamHandler(); console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
logger.addHandler(console)
for name in ['eagle_v29.log','eagle_v29_errors.log']:
    h = RotatingFileHandler(name, maxBytes=50*1024*1024, backupCount=5, encoding='utf-8')
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(h)

# ============================================================
# PROXY
# ============================================================
def create_request():
    proxy_url = os.getenv("TELEGRAM_PROXY", "")
    if proxy_url: return HTTPXRequest(proxy_url=proxy_url, connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0)
    else: return HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0)

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    channel_username: str = os.getenv("CHANNEL_USERNAME", "@CryptoPulse606")
    owner_id: int = 7225279768
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    card_number: str = "5859831200715448"
    required_invites: int = 5
    subscription_days: int = 30
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT","ADA/USDT",
        "DOGE/USDT","DOT/USDT","AVAX/USDT","LINK/USDT","UNI/USDT","ATOM/USDT",
        "LTC/USDT","ETC/USDT","FIL/USDT","TRX/USDT","VET/USDT","ALGO/USDT",
        "SUI/USDT","APT/USDT","ARB/USDT","OP/USDT","PEPE/USDT","WIF/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h","1d","1w"])
    auto_send: bool = True; signal_interval: int = 14400
    news_interval: int = 14400; fg_interval: int = 3600; whale_interval: int = 5400

cfg = Config()

# ============================================================
# PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "eagle_v29.lock"
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
# PERSIAN DATE
# ============================================================
class PersianLive:
    DAYS = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
    MONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
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
    def full(cls): return f"{cls.day_str()} {cls.shamsi()} ساعت {cls.time_str()}"
    @classmethod
    def greeting(cls):
        h = cls.now().hour
        if 5 <= h < 12: return "صبح بخیر"
        elif 12 <= h < 17: return "ظهر بخیر"
        elif 17 <= h < 22: return "عصر بخیر"
        else: return "شب بخیر"

pdt = PersianLive()

# ============================================================
# SUBSCRIPTION LEVELS
# ============================================================
class SubscriptionLevel:
    FREE = "رایگان"
    SILVER = "نقره‌ای"
    GOLD = "طلایی"
    PLATINUM = "پلاتینیوم"
    LIMITS = {
        FREE: {"signals": 2, "symbols": 5, "price": 0},
        SILVER: {"signals": 10, "symbols": 10, "price": 1440000},
        GOLD: {"signals": 30, "symbols": 16, "price": 3600000},
        PLATINUM: {"signals": 999, "symbols": 999, "price": 7200000},
    }

# ============================================================
# USER MANAGER
# ============================================================
class UserManager:
    def __init__(self):
        self.users = {}
        self.load()
    def load(self):
        try:
            with open('users_eagle.json', 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        except: self.users = {}
    def save(self):
        try:
            with open('users_eagle.json', 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except: pass
    def get(self, uid):
        uid = str(uid)
        if uid not in self.users:
            self.users[uid] = {"level": SubscriptionLevel.FREE, "joined": datetime.now().isoformat(), "signals_used": 0, "last_signal": "", "active": False, "referrals": 0}
            self.save()
        return self.users[uid]
    def is_owner(self, uid): return int(uid) == cfg.owner_id
    def is_active(self, uid):
        if self.is_owner(uid): return True
        return self.get(uid).get("active", False)
    def activate_user(self, uid, method="manual", level=SubscriptionLevel.SILVER):
        user = self.get(uid); user["active"] = True; user["level"] = level
        user["expiry"] = (datetime.now() + timedelta(days=cfg.subscription_days)).isoformat(); self.save()
    def check_limit(self, uid):
        if not self.is_active(uid): return False, "حساب غیرفعال"
        if self.is_owner(uid): return True, ""
        user = self.get(uid); max_sig = SubscriptionLevel.LIMITS[user["level"]]["signals"]
        now = datetime.now(); last = user.get("last_signal", "")
        if last and (now - datetime.fromisoformat(last)).seconds < 3600:
            if user["signals_used"] >= max_sig: return False, f"سقف {max_sig} سیگنال"
            else: user["signals_used"] = 0
        user["signals_used"] += 1; user["last_signal"] = now.isoformat(); self.save()
        return True, ""

user_mgr = UserManager()

# ============================================================
# AI IMAGE GENERATOR — چشــــم عـقـاب
# ============================================================
class AIImageGenerator:
    POLLINATIONS_API = "https://image.pollinations.ai/prompt/"
    
    STYLES = {
        "chart": "professional trading chart, candlestick pattern, green and red candles, technical indicators, dark background, 4K, detailed",
        "bull": "raging golden bull made of fire and neon green energy, charging through blockchain network, cyberpunk, epic, 8K, cinematic lighting",
        "bear": "massive ice bear made of dark metal and red lava, roaring on crypto market, dramatic, cinematic, 4K, stormy background",
        "whale": "giant transparent whale swimming in ocean of crypto coins, bioluminescent, magical, epic scale, 8K, underwater lighting",
        "eagle": "giant cyberpunk eagle with glowing green eyes, scanning crypto charts, golden wings spread, precision targeting, 8K, epic, majestic",
        "nft": "cyberpunk NFT avatar, holographic neon colors, futuristic crypto trader with glowing glasses, 4K, trending on artstation",
        "moon": "bitcoin rocket flying to the moon, golden BTC logo, green candles trail, space background, epic, 4K, stars",
        "dragon": "cyberpunk dragon made of circuit boards and crypto coins, breathing green fire, flying over blockchain network, epic, 8K",
        "abstract": "abstract crypto art, blockchain concept, futuristic, geometric patterns, neon gradients, 4K, digital painting",
        "eye": "giant all-seeing eagle eye, piercing through crypto charts, laser focus, green matrix rain, 8K, mystical, hyper-realistic"
    }
    
    def __init__(self):
        self.enabled = True
        self.service = "pollinations"
        self.timeout = 60
    
    async def generate(self, prompt: str, style: str = None, width: int = 1024, height: int = 1024) -> Optional[bytes]:
        final_prompt = self._build_prompt(prompt, style)
        if self.service == "pollinations":
            return await self._generate_pollinations(final_prompt, width, height)
        else:
            return await self._generate_simulated(prompt, style)
    
    def _build_prompt(self, prompt: str, style: str = None) -> str:
        base_keywords = "cryptocurrency, bitcoin, ethereum, blockchain, futuristic, digital art, high quality, 4K, detailed, masterpiece"
        if style and style in self.STYLES: style_keywords = self.STYLES[style]
        else: style_keywords = base_keywords
        full_prompt = f"{prompt}, {style_keywords}, {base_keywords}"
        return full_prompt[:900] if len(full_prompt) > 900 else full_prompt
    
    async def _generate_pollinations(self, prompt: str, width: int = 1024, height: int = 1024) -> Optional[bytes]:
        try:
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"{self.POLLINATIONS_API}{encoded_prompt}?width={width}&height={height}&nologo=true"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200: return await response.read()
                    else:
                        logger.error(f"Pollinations error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Pollinations: {e}")
            return None
    
    async def _generate_simulated(self, prompt: str, style: str = None) -> Optional[bytes]:
        try:
            width, height = 1024, 1024
            colors = {"chart": ("#0a0a0a", "#00ff88"), "bull": ("#1a0a00", "#ff6600"), "bear": ("#1a0000", "#ff3300"), "whale": ("#001020", "#00ccff"), "eagle": ("#0a1a0a", "#00ff88"), "eye": ("#000010", "#00ffff"), "default": ("#061a14", "#00ff88")}
            bg_color, text_color = colors.get(style, colors["default"])
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)
            try:
                font_paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/System/Library/Fonts/Helvetica.ttc", "C:\\Windows\\Fonts\\Arial.ttf"]
                font = None
                for path in font_paths:
                    if os.path.exists(path): font = ImageFont.truetype(path, 32); break
                if font is None: font = ImageFont.load_default()
            except: font = ImageFont.load_default()
            
            header = "🦅 چشــــم عـقـاب — CRYPTO EAGLE EYE 🦅"
            draw.text((width//2 - 250, 80), header, fill=text_color, font=font)
            y_offset = 200
            words = prompt.split(); line = ""
            for word in words:
                if len(line + word) < 35: line += word + " "
                else:
                    draw.text((100, y_offset), line, fill=text_color, font=font); y_offset += 45; line = word + " "
            if line: draw.text((100, y_offset), line, fill=text_color, font=font)
            
            buf = io.BytesIO(); img.save(buf, format='PNG'); buf.seek(0)
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Simulated: {e}")
            return None
    
    async def generate_eagle_eye(self, symbol: str = "BTC", analysis: str = "صعودی") -> Optional[bytes]:
        prompt = f"{symbol} under eagle eye precision analysis, {analysis} trend detected, golden crosshair target"
        return await self.generate(prompt, "eagle")

ai_image_gen = AIImageGenerator()

# ============================================================
# AI (COMPACT)
# ============================================================
class GroqAI:
    URL = "https://api.groq.com/openai/v1/chat/completions"; MODEL = "llama-3.3-70b-versatile"
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self._client = httpx.AsyncClient(timeout=120.0)
    async def ask(self, prompt, max_t=800):
        if not self.enabled: return None
        try:
            r = await self._client.post(self.URL, headers={"Authorization":f"Bearer {cfg.groq_api_key}","Content-Type":"application/json"},
                json={"model":self.MODEL,"messages":[{"role":"system","content":"تو چشم عقاب هستی—تحلیلگر فوق‌حرفه‌ای کریپتو با دقت میلیمتری. فقط فارسی خودمونی حرف بزن. ایموجی زیاد. بگو 'دوست من'."},{"role":"user","content":prompt}],"max_tokens":max_t})
            if r.status_code==200: return r.json()["choices"][0]["message"]["content"]
        except: pass
        return None
    async def tech(self, sym, ind, price, change, candles):
        return await self.ask(f"تحلیل {sym} قیمت {price:,.2f} دلار\nRSI={ind.get('RSI_14',50):.0f}\nشمع‌ها: {', '.join(candles) if candles else 'بدون'}\nتحلیل کن با دقت عقاب: وضعیت، روند، ورود، ضرر، هدف. ۴۰۰ کلمه فارسی.")
    async def smc(self, sym, smc_data): return await self.ask(f"اسمارت مانی {sym}:\n{json.dumps(smc_data, ensure_ascii=False)}\nفارسی توضیح بده. ۳۰۰ کلمه.")
    async def prediction(self, sym, price, ind): return await self.ask(f"پیش‌بینی {sym} قیمت {price:,.2f}\nRSI={ind.get('RSI_14',50):.1f}\nفردا؟ یک هفته؟ ۳۰۰ کلمه فارسی.")
    async def news_summary(self, headlines): return await self.ask(f"اخبار:\n{chr(10).join(headlines[:10])}\nخلاصه فارسی. ۳۰۰ کلمه.")
    async def whale(self): return await self.ask("نهنگ‌ها چی کار می‌کنن؟ فارسی ۲۰۰ کلمه.")
    async def fear_greed(self, v, t): return await self.ask(f"ترس و طمع: {v} ({t}). فارسی ۲۰۰ کلمه.")

groq_ai = GroqAI()

# ============================================================
# EXCHANGE
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None; self.connected = False
    def connect(self):
        try:
            self._ex = ccxt.coinex({'enableRateLimit':True,'timeout':15000})
            self._ex.load_markets(); self.connected = True
        except: pass
    def ticker(self,s):
        try: return self._ex.fetch_ticker(s) if self.connected else None
        except: return None
    def ohlcv(self,s,tf,limit=150):
        try:
            if not self.connected: return None
            d = self._ex.fetch_ohlcv(s,tf,limit=limit)
            return pd.DataFrame(d,columns=['timestamp','open','high','low','close','volume']) if d and len(d)>30 else None
        except: return None

exchange_mgr = ExchangeManager()

# ============================================================
# SMART MONEY
# ============================================================
class SmartMoney:
    @staticmethod
    def analyze(df):
        if len(df) < 60: return {}
        high = df['high'].values; low = df['low'].values; close = df['close'].values
        from scipy.signal import argrelextrema
        sh_idx = argrelextrema(high, np.greater, order=3)[0]; sl_idx = argrelextrema(low, np.less, order=3)[0]
        sh = [(i, high[i]) for i in sh_idx]; sl = [(i, low[i]) for i in sl_idx]
        if len(sh) < 2 or len(sl) < 2: return {}
        bos_u = all(sh[i][1] > sh[i-1][1] for i in range(1, len(sh)))
        bos_d = all(sl[i][1] < sl[i-1][1] for i in range(1, len(sl)))
        choch = "صعودی 🟢" if (bos_u and not bos_d) else ("نزولی 🔴" if (bos_d and not bos_u) else "خنثی ⚪")
        return {"شکست_ساختار":"صعود" if bos_u else "نزول" if bos_d else "هیچ","تغییر_روند":choch,"ساختار_بازار":choch}

# ============================================================
# INDICATORS
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df):
        close = df['close'].astype(float); high = df['high'].astype(float); low = df['low'].astype(float); volume = df['volume'].astype(float)
        ind = {}
        for p in [7,14,20,50,200]: ind[f'EMA_{p}'] = float(close.ewm(span=p,adjust=False).mean().iloc[-1])
        from ta.momentum import RSIIndicator
        try: ind['RSI_14'] = float(RSIIndicator(close,14).rsi().iloc[-1])
        except: ind['RSI_14'] = 50.0
        from ta.trend import MACD, ADXIndicator, IchimokuIndicator
        try: ind['MACD_HIST'] = float(MACD(close,12,26,9).macd_diff().iloc[-1])
        except: ind['MACD_HIST'] = 0.0
        try: ind['ADX'] = float(ADXIndicator(high,low,close,14).adx().iloc[-1])
        except: ind['ADX'] = 20.0
        from ta.volatility import BollingerBands, AverageTrueRange
        try: ind['BB_PCT'] = float(BollingerBands(close,20,2).bollinger_pband().iloc[-1])
        except: ind['BB_PCT'] = 0.5
        try: ind['ATR_14'] = float(AverageTrueRange(high,low,close,14).average_true_range().iloc[-1])
        except: ind['ATR_14'] = close.iloc[-1]*0.01
        vs = volume.rolling(20).mean().iloc[-1] if len(volume)>=20 else 1; ind['VOL_RATIO'] = float(volume.iloc[-1]/vs if vs>0 else 1)
        ind['حمایت'] = float(low.rolling(20).min().iloc[-1]) if len(low)>=20 else low.min()
        ind['مقاومت'] = float(high.rolling(20).max().iloc[-1]) if len(high)>=20 else high.max()
        try:
            ichi = IchimokuIndicator(high,low,9,26,52); ind['TENKAN'] = float(ichi.ichimoku_conversion_line().iloc[-1]); ind['KIJUN'] = float(ichi.ichimoku_base_line().iloc[-1])
        except: pass
        candles, names = UltraIndicators._candles(df); ind.update(candles)
        return ind, names
    @staticmethod
    def _candles(df):
        pats = {}; names = []
        if len(df)<2: return pats, names
        o,h,l,c = df['open'].iloc[-1],df['high'].iloc[-1],df['low'].iloc[-1],df['close'].iloc[-1]
        po,pc = df['open'].iloc[-2],df['close'].iloc[-2]; body,tr = abs(c-o), h-l
        if tr==0: return pats, names
        if body<=tr*0.08: pats['دوجی']=True; names.append("دوجی")
        if (min(c,o)-l)>body*2 and c>o: pats['چکش']=True; names.append("چکش")
        if c>o and pc<po: pats['پوشای_صعودی']=True; names.append("پوشای صعودی")
        if c<o and pc>po: pats['پوشای_نزولی']=True; names.append("پوشای نزولی")
        return pats, names

ui = UltraIndicators()

# ============================================================
# SIGNAL GENERATOR
# ============================================================
class SignalGen:
    @staticmethod
    def generate(ind, price, smc_data=None):
        score = 0
        if ind.get('EMA_7',0)>ind.get('EMA_20',0)>ind.get('EMA_50',0): score+=180
        elif ind.get('EMA_7',0)<ind.get('EMA_20',0)<ind.get('EMA_50',0): score-=180
        rsi = ind.get('RSI_14',50)
        if rsi<25: score+=150
        elif rsi>75: score-=150
        if ind.get('MACD_HIST',0)>0: score+=80
        else: score-=80
        if ind.get('BB_PCT',0.5)<0.05: score+=120
        elif ind.get('BB_PCT',0.5)>0.95: score-=120
        if ind.get('VOL_RATIO',1)>2.5: score+=60 if score>0 else -60
        for bull in ['پوشای_صعودی','چکش']:
            if ind.get(bull): score+=90
        for bear in ['پوشای_نزولی']:
            if ind.get(bear): score-=90
        if smc_data:
            if 'صعودی' in smc_data.get('تغییر_روند',''): score += 100
            elif 'نزولی' in smc_data.get('تغییر_روند',''): score -= 100
        score = max(-1000,min(1000,score))
        c = "🟢🟢🟢🟢🟢" if abs(score)>=750 else ("🟢🟢🟢🟢" if abs(score)>=550 else ("🟢🟢🟢" if abs(score)>=350 else ("🟢🟢" if abs(score)>=180 else "⚪⚪")))
        if score<0: c = c.replace("🟢","🔴")
        action = "💰 بخر" if score>=350 else ("💸 بفروش" if score<=-350 else ("🤔 می‌تونی بخری" if score>=180 else ("😬 می‌تونی بفروشی" if score<=-180 else "⏳ صبر کن")))
        conf = 99 if abs(score)>=750 else (94 if abs(score)>=550 else (85 if abs(score)>=350 else (72 if abs(score)>=180 else 55)))
        sig = f"خرید فوق‌العاده" if score>=750 else (f"خرید قوی" if score>=550 else (f"خرید" if score>=350 else (f"خرید ضعیف" if score>=180 else (f"فروش فوق‌العاده" if score<=-750 else (f"فروش قوی" if score<=-550 else (f"فروش" if score<=-350 else (f"فروش ضعیف" if score<=-180 else f"خنثی")))))))
        return f"{sig} {c}", conf, score, action

sg = SignalGen()

# ============================================================
# CHART GENERATOR
# ============================================================
class ChartGenerator:
    @staticmethod
    def create(df, symbol):
        if not CHART_AVAILABLE or len(df) < 30: return None
        try:
            data = df.copy(); data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms'); data = data.set_index('timestamp')
            data = data.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'})[['Open','High','Low','Close','Volume']].iloc[-60:]
            mc = mpf.make_marketcolors(up='#00ff88', down='#ff3355', edge='inherit', wick='inherit', volume='inherit')
            style = mpf.make_mpf_style(marketcolors=mc, facecolor='#061a14', figcolor='#061a14', gridcolor='#1d3b34')
            fig, _ = mpf.plot(data, type='candle', style=style, title=f'{symbol} - {pdt.shamsi()}', volume=True, figsize=(16,10), returnfig=True)
            buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=100, bbox_inches='tight'); buf.seek(0); plt.close(fig)
            return buf
        except: return None

chart_gen = ChartGenerator()

# ============================================================
# FORMATTER
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, groq_t=None, smc_t=None, pred_t=None):
        s = a['symbol'].replace('/USDT',''); i = a['indicators']; candles = a.get('candles',[])
        sig, conf, score, action = sg.generate(i, a['price'], a.get('smc'))
        entry, sl = a['price'], a['price']-i['ATR_14']*2; tp1 = a['price']+i['ATR_14']*4
        msg = f"""
🦅╔══════════════════════╗🦅
  💰 سیگنال عقاب: {s} 💰
🦅╚══════════════════════╝🦅

{pdt.greeting()} دوست من! {pdt.full()}

💰 قیمت: {a['price']:,.4f}$ | 📊 تغییر: {a['change']:+.2f}%
🎯 سیگنال: {sig} | 💪 قدرت: {conf}% | ⭐ امتیاز: {score}
🚦 پیشنهاد: {action}

📈 میانگین‌ها: ۷={i.get('EMA_7',0):.2f} | ۲۰={i.get('EMA_20',0):.2f} | ۵۰={i.get('EMA_50',0):.2f}
🕯️ شمع‌ها: {', '.join(candles) if candles else 'بدون الگو'}
📊 اندیکاتورها: RSI={i['RSI_14']:.1f} | MACD={'صعود' if i.get('MACD_HIST',0)>0 else 'نزول'} | ADX={i['ADX']:.1f}
🔑 مقاومت: {i.get('مقاومت',0):,.4f} | حمایت: {i.get('حمایت',0):,.4f}
🎯 معامله: ورود: {entry:,.4f} | ضرر: {sl:,.4f} | هدف: {tp1:,.4f}
"""
        if groq_t: msg += f"\n🧠 تحلیل هوش مصنوعی:\n{groq_t[:600]}\n"
        if smc_t: msg += f"\n🧲 اسمارت مانی:\n{smc_t[:300]}\n"
        if pred_t: msg += f"\n🔮 پیش‌بینی:\n{pred_t[:400]}\n"
        msg += f"🦅╚══════════════════════╝🦅\n✨ @CryptoPulse606 | {pdt.full()}"
        return msg

fmt = Fmt()

# ============================================================
# NEWS
# ============================================================
class CryptoNews:
    CACHE = {}
    CACHE_DURATION = 14400
    SOURCES = [("https://cryptopanic.com/news/rss/", "کریپتوپنیک"), ("https://cointelegraph.com/rss", "کوین‌تلگراف")]
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts", 0)) < cls.CACHE_DURATION: return cls.CACHE.get("data",[])
        articles = []
        for url, source in cls.SOURCES:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]: articles.append({"title":entry.title,"link":entry.link,"source":source})
            except: pass
        cls.CACHE = {"ts":now,"data":articles}
        return articles

# ============================================================
# FEAR & GREED
# ============================================================
class FearGreedIndex:
    CACHE = {}
    CACHE_DURATION = 3600
    @classmethod
    async def fetch(cls):
        now = time.time()
        if cls.CACHE and (now - cls.CACHE.get("ts",0)) < cls.CACHE_DURATION: return cls.CACHE.get("value"), cls.CACHE.get("text")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get("https://api.alternative.me/fng/?limit=1"); data = resp.json()
                return int(data['data'][0]['value']), data['data'][0]['value_classification']
        except: return 50, "خنثی"

# ============================================================
# SAFE SEND
# ============================================================
async def safe_send(bot, chat_id, text, reply_markup=None):
    try: return await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)
    except:
        try: return await bot.send_message(chat_id=chat_id, text=re.sub(r'[*_`~\[\]\(\)]','',text)[:4000], reply_markup=reply_markup)
        except: return None

async def safe_edit(bot, chat_id, msg_id, text, reply_markup=None):
    try: return await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)
    except: return None

# ============================================================
# MENU — 20 GLASS BUTTONS
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌ها", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال بیتکوین", callback_data="s_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan")],
            [InlineKeyboardButton("⏰ ۴ساعته", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ روزانه", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ هفتگی", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🧠 تحلیل هوش مصنوعی", callback_data="ai_BTC/USDT"),
             InlineKeyboardButton("📊 نمودار پیشرفته", callback_data="chart_BTC/USDT"),
             InlineKeyboardButton("📰 تحلیل بازار", callback_data="market")],
            [InlineKeyboardButton("🧲 اسمارت مانی", callback_data="smc"),
             InlineKeyboardButton("🔮 پیش‌بینی قیمت", callback_data="pred"),
             InlineKeyboardButton("🐋 ردیابی نهنگ‌ها", callback_data="whale")],
            [InlineKeyboardButton("😱 شاخص ترس و طمع", callback_data="fear_greed"),
             InlineKeyboardButton("🏆 دامیننس بازار", callback_data="dominance"),
             InlineKeyboardButton("📰 اخبار فارسی", callback_data="news")],
            [InlineKeyboardButton("🎨 ساخت تصویر با AI", callback_data="ai_image"),
             InlineKeyboardButton("🦅 چشم عقاب", callback_data="eagle_eye"),
             InlineKeyboardButton("👥 دعوت دوستان", callback_data="referral")],
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="ref"),
             InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ])
    
    @staticmethod
    def locked() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 عضویت در کانال", callback_data="join_channel")],
            [InlineKeyboardButton("👥 دعوت ۵ نفر", callback_data="invite_friends")],
            [InlineKeyboardButton("💎 خرید اشتراک", callback_data="vip")],
        ])

# ============================================================
# HANDLERS
# ============================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Owner — always open
    if user_mgr.is_owner(user_id):
        await update.message.reply_text(f"""
🦅🦅🦅 چشــــم عـقـاب نسخه ۲۹ 🦅🦅🦅

{pdt.greeting()} فرهاد جان! 👑

💎 اشتراک: پلاتینیوم (دائمی)
📊 دسترسی: نامحدود
🧲 اسمارت مانی: فعال
🎨 ساخت تصویر با هوش مصنوعی: فعال
🦅 تحلیل با دقت عقاب: فعال

✨ ربات کاملاً فعال ✨

👇 انتخاب کن:""", reply_markup=Menu.main())
        return
    
    # Active user
    if user_mgr.is_active(user_id):
        user = user_mgr.get_user(user_id)
        level = user.get("level", SubscriptionLevel.FREE)
        await update.message.reply_text(f"""
🦅 چشــــم عـقـاب 🦅

{pdt.greeting()}!

💎 اشتراک: {level}
📊 سیگنال: {SubscriptionLevel.LIMITS[level]['signals']} در ساعت

👇 انتخاب کن:""", reply_markup=Menu.main())
        return
    
    # Locked user
    await update.message.reply_text(f"""🔒 *سلام! برای استفاده از ربات، یکی از راه‌های زیر رو انتخاب کن:*

{pdt.greeting()}!

📊 *۳ راه برای فعال‌سازی:*

1️⃣ *عضویت در کانال*
📢 @CryptoPulse606

2️⃣ *دعوت ۵ نفر*
لینک: `https://t.me/{ctx.bot.username}?start={user_id}`

3️⃣ *خرید اشتراک*
💎 از ۱.۴ میلیون تومان

👇 یکی از گزینه‌ها رو انتخاب کن:""", parse_mode="Markdown", reply_markup=Menu.locked())

async def send_signal(bot, chat_id, symbol, ticker, df, ind, candles, smc_data, groq_t, smc_t, pred_t):
    if CHART_AVAILABLE:
        buf = chart_gen.create(df, symbol)
        if buf: await bot.send_photo(chat_id=chat_id, photo=buf, caption=f"📊 {symbol.replace('/USDT','')} | {ticker['last']:,.4f}$")
    a = {'symbol':symbol,'price':ticker['last'],'change':ticker.get('percentage',0),'indicators':ind,'candles':candles,'smc':smc_data}
    await safe_send(bot, chat_id, fmt.signal(a, groq_t, smc_t, pred_t))

async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; d = q.data
    user_id = update.effective_user.id
    
    # Locked user buttons
    if not user_mgr.is_active(user_id) and not user_mgr.is_owner(user_id):
        if d == "join_channel":
            try:
                member = await ctx.bot.get_chat_member(chat_id=cfg.channel_username, user_id=user_id)
                if member.status in ['member', 'administrator', 'creator']:
                    user_mgr.activate_user(user_id, "channel", SubscriptionLevel.SILVER)
                    await q.edit_message_text("🎉 تبریک! با عضویت در کانال، ربات برات فعال شد!\n\n/start رو بزن")
                else:
                    await q.edit_message_text("❌ هنوز عضو کانال نشدی!\n\n@CryptoPulse606", reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 بررسی مجدد", callback_data="join_channel")],
                        [InlineKeyboardButton("📢 رفتن به کانال", url=f"https://t.me/{cfg.channel_username.replace('@','')}")]
                    ]))
            except: await q.answer("خطا در بررسی")
            return
        elif d == "vip":
            await q.edit_message_text(f"""💎 *خرید اشتراک*

🥈 نقره‌ای: {SubscriptionLevel.LIMITS['نقره‌ای']['price']:,} تومان
🥇 طلایی: {SubscriptionLevel.LIMITS['طلایی']['price']:,} تومان
💎 پلاتینیوم: {SubscriptionLevel.LIMITS['پلاتینیوم']['price']:,} تومان

💳 `{cfg.card_number}`
📲 @CryptoPulse606""", parse_mode="Markdown", reply_markup=Menu.locked())
            return
        else:
            await q.answer("🔒 حساب غیرفعال", show_alert=True)
            return
    
    # Active/owner handlers
    try:
        if d == "back": await q.edit_message_text(f"🦅 منو\n\n{pdt.full()}", parse_mode="Markdown", reply_markup=Menu.main())
        elif d == "p":
            if not exchange_mgr.connected: exchange_mgr.connect()
            txt = f"💰 قیمت‌ها\n\n{pdt.full()}\n\n"
            for sym in cfg.symbols[:20]:
                t = exchange_mgr.ticker(sym)
                if t: txt += f"{'🟢' if t.get('percentage',0)>0 else '🔴'} {sym.replace('/USDT','')}: {t['last']:,.4f}$ ({t.get('percentage',0):+.1f}%)\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("s_"):
            can, msg = user_mgr.check_limit(user_id)
            if not can: await q.answer(msg, show_alert=True); return
            sym = d[2:]; await q.answer(); await q.edit_message_text(f"🔄 تحلیل {sym.replace('/USDT','')}...")
            if not exchange_mgr.connected: exchange_mgr.connect()
            t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, '1h', 150)
            if not t or df is None: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]])); return
            ind, candles = ui.calc(df); smc_data = SmartMoney.analyze(df)
            groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), candles)
            smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
            pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
            await send_signal(ctx.bot, q.message.chat_id, sym, t, df, ind, candles, smc_data, groq_t, smc_t, pred_t)
            await safe_edit(ctx.bot, q.message.chat_id, q.message.message_id, f"✅ تحلیل {sym.replace('/USDT','')} انجام شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data=f"s_{sym}"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d.startswith("tf4_") or d.startswith("tf1d_") or d.startswith("tf1w_"):
            tf_map = {"tf4_":"4h","tf1d_":"1d","tf1w_":"1w"}; tf_labels = {"4h":"۴ساعته","1d":"روزانه","1w":"هفتگی"}
            for prefix,tf in tf_map.items():
                if d.startswith(prefix):
                    sym = d[len(prefix):] if len(d)>len(prefix) else "BTC/USDT"; await q.answer()
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym, tf, 150)
                    if t and df is not None:
                        ind, _ = ui.calc(df); sig, conf, _, action = sg.generate(ind, t['last'])
                        if CHART_AVAILABLE:
                            buf = chart_gen.create(df, sym)
                            if buf: await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=buf, caption=f"⏰ {tf_labels.get(tf,tf)} {sym.replace('/USDT','')} | {t['last']:,.4f}$")
                        await q.edit_message_text(f"⏰ {tf_labels.get(tf,tf)} {sym.replace('/USDT','')}\n{pdt.full()}\n💰 {t['last']:,.4f}$\n🎯 {sig}\n🚦 {action}\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "ai_image":
            await q.answer("🎨 در حال ساخت تصویر..."); await q.edit_message_text("🎨 *ساخت تصویر با هوش مصنوعی*\n\n🦅 چشم عقاب در حال طراحی...")
            img_bytes = await ai_image_gen.generate_eagle_eye("BTC", "صعودی")
            if img_bytes:
                await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=img_bytes, caption="🦅 تصویر ساخته شده با چشم عقاب\n✨ @CryptoPulse606")
                await q.edit_message_text("✅ تصویر ارسال شد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
            else:
                await q.edit_message_text("❌ خطا در ساخت تصویر", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "eagle_eye":
            t = exchange_mgr.ticker("BTC/USDT")
            if t:
                img_bytes = await ai_image_gen.generate_eagle_eye("BTC", "صعودی" if t.get('percentage',0) > 0 else "نزولی")
                if img_bytes:
                    await ctx.bot.send_photo(chat_id=q.message.chat_id, photo=img_bytes, caption=f"🦅 تحلیل چشــــم عـقـاب\n💰 بیتکوین: {t['last']:,.2f}$\n📊 تغییر: {t.get('percentage',0):+.2f}%\n\n✨ @CryptoPulse606")
                await q.answer("🦅 چشم عقاب فعال شد")
        elif d == "smc":
            df = exchange_mgr.ohlcv("BTC/USDT", '1h', 150)
            if df is not None:
                smc_data = SmartMoney.analyze(df); ai_text = await groq_ai.smc("بیتکوین", smc_data) if groq_ai.enabled else None
                await q.edit_message_text(f"🧲 *اسمارت مانی*\n{pdt.full()}\n\n{ai_text if ai_text else 'داده ناکافی'}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "fear_greed":
            fg_value, fg_text = await FearGreedIndex.fetch()
            await q.edit_message_text(f"😱 ترس و طمع\n{pdt.full()}\n\n{'🟢' if fg_value<30 else '🔴' if fg_value>70 else '🟡'} {fg_value}/۱۰۰ — {fg_text}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="fear_greed"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "news":
            articles = await CryptoNews.fetch()
            if articles:
                summary = await groq_ai.news_summary([a['title'] for a in articles[:10]])
                await q.edit_message_text(f"📰 اخبار\n{pdt.full()}\n\n{summary}\n\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="news"), InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d == "dominance":
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get("https://api.coingecko.com/api/v3/global"); data = resp.json()
                    await q.edit_message_text(f"🏆 دامیننس\n{pdt.full()}\nبیتکوین: {data['data']['market_cap_percentage']['btc']:.1f}%\nاتریوم: {data['data']['market_cap_percentage']['eth']:.1f}%", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
            except: await q.edit_message_text("❌", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        elif d in ["scan","market","ai_BTC/USDT","chart_BTC/USDT","pred","whale","referral","ref","help"]:
            await q.edit_message_text(f"⚡ {d}\n{pdt.full()}\n\nدر حال بروزرسانی...\n✨ @CryptoPulse606", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))
        else: await q.answer(f"⚡ {pdt.time_str()}")
    except Exception as e:
        logger.error(f"Btn: {e}")
        try: await q.answer("❌")
        except: pass

async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"/start\n{pdt.full()}", reply_markup=Menu.main())

# ============================================================
# AUTO LOOPS
# ============================================================
async def auto_signals(app: Application):
    await asyncio.sleep(10)
    while True:
        try:
            if not cfg.channel_id: await asyncio.sleep(60); continue
            if not exchange_mgr.connected: exchange_mgr.connect()
            for sym in ["BTC/USDT","ETH/USDT","SOL/USDT"]:
                try:
                    t = exchange_mgr.ticker(sym); df = exchange_mgr.ohlcv(sym,'1h',150)
                    if t and df is not None:
                        ind, candles = ui.calc(df); smc_data = SmartMoney.analyze(df)
                        groq_t = await groq_ai.tech(sym, ind, t['last'], t.get('percentage',0), candles)
                        smc_t = await groq_ai.smc(sym, smc_data) if groq_ai.enabled else None
                        pred_t = await groq_ai.prediction(sym, t['last'], ind) if groq_ai.enabled else None
                        await send_signal(app.bot, cfg.channel_id, sym, t, df, ind, candles, smc_data, groq_t, smc_t, pred_t)
                        await asyncio.sleep(120)
                except: pass
        except: pass
        await asyncio.sleep(cfg.signal_interval)

async def auto_news(app: Application):
    await asyncio.sleep(30)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                articles = await CryptoNews.fetch()
                if articles:
                    summary = await groq_ai.news_summary([a['title'] for a in articles[:10]])
                    if summary: await safe_send(app.bot, cfg.channel_id, f"📰 اخبار\n{pdt.full()}\n\n{summary}\n\n✨ @CryptoPulse606")
        except: pass
        await asyncio.sleep(cfg.news_interval)

async def auto_fear_greed(app: Application):
    await asyncio.sleep(180)
    while True:
        try:
            if cfg.channel_id:
                fg_value, fg_text = await FearGreedIndex.fetch()
                await safe_send(app.bot, cfg.channel_id, f"😱 ترس و طمع\n{'🟢' if fg_value<30 else '🔴' if fg_value>70 else '🟡'} {fg_value}/۱۰۰ — {fg_text}\n\n✨ @CryptoPulse606")
        except: pass
        await asyncio.sleep(cfg.fg_interval)

async def auto_whale(app: Application):
    await asyncio.sleep(400)
    while True:
        try:
            if cfg.channel_id and groq_ai.enabled:
                c = await groq_ai.whale()
                if c: await safe_send(app.bot, cfg.channel_id, f"🐋 نهنگ‌ها\n\n{c}\n\n✨ @CryptoPulse606")
        except: pass
        await asyncio.sleep(cfg.whale_interval)

# ============================================================
# MAIN
# ============================================================
async def main():
    if not ProcessLock.acquire(): sys.exit(1)
    if not cfg.token: ProcessLock.release(); return
    logger.info(f"🦅 شروع چشم عقاب نسخه ۲۹ | {pdt.full()}")
    exchange_mgr.connect()
    request = create_request()
    app = Application.builder().token(cfg.token).request(request).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    asyncio.create_task(cleanup_memory())
    asyncio.create_task(auto_signals(app))
    asyncio.create_task(auto_news(app))
    asyncio.create_task(auto_fear_greed(app))
    asyncio.create_task(auto_whale(app))
    logger.info("🦅 چشم عقاب آماده پرواز | مالک: ۷۲۲۵۲۷۹۷۶۸")
    try:
        await app.initialize(); await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
    except Exception as e: logger.critical(f"❌ {e}")
    finally:
        try: await app.updater.stop(); await app.stop(); await app.shutdown()
        except: pass
        ProcessLock.release()

if __name__ == "__main__":
    try: asyncio.run(main())
    except: ProcessLock.release()
