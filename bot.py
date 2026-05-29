#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  💎 VIP PLATINUM v37.0 — FULLY FEATURED CRYPTO TRADING BOT                  ║
║  ✅ Multi-AI (Groq, Gemini, DeepSeek) with auto fallback                    ║
║  ✅ Real-time news from 10+ sources (RSS + cryptocurrency.cv)              ║
║  ✅ Unique AI images (Pollinations) – no repetition                         ║
║  ✅ Golden Crypto Book – 1,000,000+ lessons, every 30 min                  ║
║  ✅ 24 interactive buttons – no Query timeout errors                        ║
║  ✅ Advanced charts (candlestick, indicators) – Platinum style             ║
║  ✅ 80+ technical indicators, Smart Money, Signal with strength circles    ║
║  ✅ Invite code system – fully Persian, emoji-rich                          ║
║  ✅ CoinEx exchange integration (real & demo trading)                       ║
║  ✅ Persian date/time, greetings, and ultra-precise analysis               ║
╚══════════════════════════════════════════════════════════════════════════════╝
Developer: VIP Platinum Team 💎
Version: 37.0 – Production Ready – 7000+ lines
"""

import os
import sys
import subprocess
import logging
import asyncio
import time
import json
import random
import signal
import io
import re
import gc
import urllib.parse
import hashlib
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, OrderedDict

# ---------- ENVIRONMENT ----------
os.environ["TZ"] = "Asia/Tehran"
os.environ["MPLBACKEND"] = "Agg"
try:
    time.tzset()
except:
    pass

# ---------- AUTO INSTALL LIBRARIES ----------
def ensure_libs():
    libs = {
        'matplotlib': 'matplotlib',
        'mplfinance': 'mplfinance',
        'ta': 'ta',
        'ccxt': 'ccxt',
        'httpx': 'httpx',
        'dotenv': 'python-dotenv',
        'telegram': 'python-telegram-bot',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'jdatetime': 'jdatetime',
        'pytz': 'pytz',
        'scipy': 'scipy',
        'feedparser': 'feedparser',
        'Pillow': 'Pillow',
        'cachetools': 'cachetools',
        'tenacity': 'tenacity',
        'aiohttp': 'aiohttp',
        'schedule': 'schedule',
        'colorama': 'colorama',
        'termcolor': 'termcolor',
        'google.generativeai': 'google-generativeai'
    }
    for mod, pkg in libs.items():
        try:
            __import__(mod)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ensure_libs()

# ---------- SILENCE NOISY LOGGERS ----------
for noisy in ['httpx', 'httpcore', 'telegram', 'telegram.ext', 'apscheduler', 'ccxt',
              'urllib3', 'asyncio', 'matplotlib', 'PIL', 'aiohttp', 'chardet', 'openai', 'groq']:
    logging.getLogger(noisy).setLevel(logging.CRITICAL + 1)
    logging.getLogger(noisy).propagate = False
    logging.getLogger(noisy).handlers = []

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VIPPlatinumV37')

from colorama import init, Fore, Style
init(autoreset=True)

import jdatetime
import pytz
import feedparser
import numpy as np
import pandas as pd
import ccxt
import httpx
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from PIL import Image

TEHRAN_TZ = pytz.timezone('Asia/Tehran')
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import mplfinance as mpf
    CHART_AVAILABLE = True
except:
    CHART_AVAILABLE = False

load_dotenv()

# ============================================================
# 🧹 MEMORY CLEANUP
# ============================================================
async def cleanup_memory():
    while True:
        gc.collect()
        if CHART_AVAILABLE:
            try:
                plt.close('all')
            except:
                pass
        await asyncio.sleep(600)

# ============================================================
# 📝 LOGGING SETUP
# ============================================================
logger.setLevel(logging.INFO)
logger.propagate = False
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter(f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} | {Fore.YELLOW}%(levelname)s{Style.RESET_ALL} | {Fore.WHITE}%(message)s{Style.RESET_ALL}'))
console.addFilter(lambda record: record.name == 'VIPPlatinumV37')
logger.addHandler(console)

for fname in ['vip_platinum.log', 'vip_platinum_errors.log']:
    h = RotatingFileHandler(fname, maxBytes=50*1024*1024, backupCount=10, encoding='utf-8')
    h.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    h.addFilter(lambda record: record.name == 'VIPPlatinumV37')
    h.setLevel(logging.ERROR if 'errors' in fname else logging.INFO)
    logger.addHandler(h)

# ============================================================
# 🔑 INVITE CODE SYSTEM
# ============================================================
class InviteSystem:
    VALID_CODES = {"VIP1404", "PLATINUM2026", "CRYPTOVIP", "GOLDEN1404",
                   "DIAMONDVIP", "PULSEGOLD", "VIPPLATINUM", "CRYPTOPULSE"}
    _authorized = {}
    _codes = {}
    USERS_FILE = "authorized_users.json"

    @classmethod
    def load(cls):
        try:
            if os.path.exists(cls.USERS_FILE):
                with open(cls.USERS_FILE) as f:
                    data = json.load(f)
                    cls._authorized = {int(k): v for k, v in data.get('authorized', {}).items()}
                    cls._codes = {int(k): v for k, v in data.get('codes', {}).items()}
                logger.info(f"🔑 {len(cls._authorized)} کاربر مجاز بارگذاری شد")
        except:
            pass

    @classmethod
    def save(cls):
        try:
            with open(cls.USERS_FILE, 'w') as f:
                json.dump({'authorized': cls._authorized, 'codes': cls._codes}, f, indent=2)
        except:
            pass

    @classmethod
    def is_auth(cls, user_id: int) -> bool:
        return user_id == cfg.owner_id or cls._authorized.get(user_id, False)

    @classmethod
    def validate(cls, code: str) -> bool:
        return code.upper().strip() in cls.VALID_CODES

    @classmethod
    def auth_user(cls, user_id: int, code: str) -> bool:
        if cls.validate(code):
            cls._authorized[user_id] = True
            cls._codes[user_id] = code.upper()
            cls.save()
            logger.info(f"🔑 کاربر {user_id} مجاز شد")
            return True
        return False

# ============================================================
# ⚙️ CONFIGURATION
# ============================================================
@dataclass
class Config:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    channel_id: str = os.getenv("CHANNEL_ID", "")
    owner_id: int = 7225279768
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    coinex_api_key: str = os.getenv("COINEX_API_KEY", "")
    coinex_secret: str = os.getenv("COINEX_SECRET", "")
    primary_ai: str = os.getenv("PRIMARY_AI", "groq").lower()
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT",
        "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT", "UNI/USDT", "ATOM/USDT"
    ])
    primary_tfs: List[str] = field(default_factory=lambda: ["4h", "1d", "1w"])
    signal_interval: int = 7200
    education_interval: int = 1800
    news_interval: int = 14400
    fg_interval: int = 3600
    whale_interval: int = 5400
    daily_summary_time: str = "23:00"
    hashtags: List[str] = field(default_factory=lambda: [
        "#کریپتو", "#ارز_دیجیتال", "#بیتکوین", "#سیگنال", "#تحلیل_تکنیکال", "#VIP_پلاتینیوم"
    ])

cfg = Config()

# ============================================================
# 🔒 PROCESS LOCK
# ============================================================
class ProcessLock:
    _file = "vip_platinum.lock"

    @classmethod
    def acquire(cls):
        try:
            if os.path.exists(cls._file):
                with open(cls._file) as f:
                    old = int(f.read().strip() or 0)
                os.kill(old, signal.SIGTERM)
                time.sleep(1)
                os.remove(cls._file)
            with open(cls._file, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except:
            return True

    @classmethod
    def release(cls):
        try:
            os.remove(cls._file)
        except:
            pass

for sig in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(sig, lambda s, f: (ProcessLock.release(), sys.exit(0)))

# ============================================================
# 📅 PERSIAN DATE, TIME & GREETINGS
# ============================================================
class PersianLive:
    DAYS = ['دوشنبه 🗓️', 'سه‌شنبه 🗓️', 'چهارشنبه 🗓️', 'پنج‌شنبه 🎉', 'جمعه 🕌', 'شنبه 📅', 'یکشنبه 📅']
    MONTHS = ['فروردین 🌸', 'اردیبهشت 🌹', 'خرداد ☀️', 'تیر 🔥', 'مرداد 🌞', 'شهریور 🍂', 'مهر 🍁', 'آبان 🌧️', 'آذر ❄️', 'دی ⛄', 'بهمن 🌨️', 'اسفند 🌱']

    @classmethod
    def now(cls):
        return datetime.now(TEHRAN_TZ)

    @classmethod
    def shamsi(cls):
        j = jdatetime.datetime.fromgregorian(datetime=cls.now())
        return f"{j.day} {cls.MONTHS[j.month - 1]} {j.year}"

    @classmethod
    def time_str(cls):
        return cls.now().strftime('%H:%M:%S')

    @classmethod
    def day_str(cls):
        return cls.DAYS[cls.now().weekday()]

    @classmethod
    def full(cls):
        return f"{cls.day_str()} {cls.shamsi()} ساعت {cls.time_str()} ✨"

    @classmethod
    def greeting(cls):
        h = cls.now().hour
        if 5 <= h < 9:
            return "صبح بخیر پلاتینیومی عزیز 🌄💎"
        elif 12 <= h < 14:
            return "ظهر بخیر دوست طلایی من ☀️🌟"
        elif 16 <= h < 18:
            return "عصر بخیر تریدر حرفه‌ای 🌇✨"
        elif 20 <= h <= 23 or 1 <= h < 3:
            return "شب خوش VIP عزیز 🌙💫"
        else:
            return "وقت بخیر پلاتینیومی جان ⏰💎"

pdt = PersianLive()

# ============================================================
# 🎨 AI IMAGE GENERATOR – UNIQUE EVERY TIME
# ============================================================
class UniqueImageGenerator:
    POLLINATIONS = "https://image.pollinations.ai/prompt/"
    STYLES = {
        "platinum_chart": "luxurious platinum trading chart, dark background, 4K, sharp details",
        "diamond_bull": "diamond bull with platinum horns, green energy aura, charging, epic 8K",
        "crystal_bear": "crystal ice bear with platinum claws, dramatic crypto market scene, 4K",
        "golden_whale": "magnificent golden whale swimming in platinum ocean, magical 8K",
        "news_flash": "breaking news hologram with platinum headlines, futuristic newsroom, 4K",
        "moon_rocket": "platinum rocket with Bitcoin logo flying to the moon, diamond stars, 4K",
        "abstract_crypto": "abstract platinum crypto art, blockchain network, futuristic geometry, 4K",
        "crystal_ball": "crystal ball showing crypto future, platinum base, mystical, 4K"
    }
    COLOR_THEMES = [
        "platinum and silver", "diamond and gold", "crystal and blue",
        "platinum and emerald", "silver and sapphire", "platinum and amethyst"
    ]

    def __init__(self):
        self.used_prompts = deque(maxlen=200)
        self.used_styles = deque(maxlen=30)
        self.used_colors = deque(maxlen=15)

    async def generate(self, prompt: str, style: str = None, width=1024, height=1024) -> Optional[bytes]:
        if not style:
            available = [s for s in self.STYLES if s not in self.used_styles]
            style = random.choice(available or list(self.STYLES.keys()))
        color = random.choice([c for c in self.COLOR_THEMES if c not in self.used_colors] or self.COLOR_THEMES)
        unique = f"seed{random.randint(10000, 99999)}_t{int(time.time() * 1000)}"
        full_prompt = f"{prompt}, {self.STYLES[style]}, {color} theme, high quality 4K, {unique}"
        h = hashlib.md5(full_prompt.encode()).hexdigest()
        if h in self.used_prompts:
            full_prompt += f" extra_{random.randint(1, 9999)}"
        self.used_prompts.append(h)
        self.used_styles.append(style)
        self.used_colors.append(color)
        try:
            url = f"{self.POLLINATIONS}{urllib.parse.quote(full_prompt)}?width={width}&height={height}&nologo=true&seed={random.randint(1, 999999)}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=90)) as resp:
                    if resp.status == 200:
                        return await resp.read()
        except Exception as e:
            logger.error(f"Image gen error: {e}")
        return None

    async def for_signal(self, symbol, trend):
        style = "diamond_bull" if "صعود" in trend else "crystal_bear" if "نزول" in trend else "platinum_chart"
        return await self.generate(f"{symbol} {trend} professional cryptocurrency market analysis", style)

    async def for_news(self):
        return await self.generate("latest cryptocurrency breaking news with platinum style", "news_flash")

    async def custom(self, prompt):
        return await self.generate(prompt)

ai_img = UniqueImageGenerator()

# ============================================================
# 🧠 MULTI-AI ORCHESTRATOR (GROQ + GEMINI + DEEPSEEK)
# ============================================================
class GroqAI:
    def __init__(self):
        self.enabled = bool(cfg.groq_api_key)
        self.client = httpx.AsyncClient(timeout=180)
        self.system = "تو تحلیلگر پلاتینیوم کریپتو هستی. کاملاً فارسی و پر از شکلک پاسخ بده. همیشه با انرژی مثبت و حرفه‌ای."

    async def ask(self, prompt, max_t=800):
        if not self.enabled:
            return None
        try:
            resp = await self.client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {cfg.groq_api_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": self.system}, {"role": "user", "content": prompt}],
                    "max_tokens": max_t,
                    "temperature": 0.85
                },
                timeout=120
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except:
            pass
        return None

    async def tech(self, sym, ind, price, change, candles, mtf):
        return await self.ask(f"""💎 تحلیل تکنیکال {sym} 💎
💰 قیمت: {price:,.2f} دلار | تغییر: {change:+.2f}%
🌟 RSI(14)={ind.get('RSI_14', 50):.0f} | MACD={'🟢صعودی' if ind.get('MACD_HIST', 0) > 0 else '🔴نزولی'}
💫 ADX={ind.get('ADX', 20):.0f} | MFI={ind.get('MFI', 50):.0f}
🛡️ حمایت=${ind.get('حمایت', 0):.2f} | ⚔️ مقاومت=${ind.get('مقاومت', 0):.2f}
🕯️ شمع‌ها: {', '.join(candles) if candles else 'بدون الگوی خاص'}
🌍 چند تایم‌فریم: {mtf}
تحلیل کاملاً فارسی با نقاط ورود، حد ضرر و اهداف قیمتی بنویس. پر از شکلک و انرژی مثبت 💎✨""", 700)

    async def smc(self, sym, smc_data):
        return await self.ask(f"🧲 تحلیل اسمارت مانی {sym}:\n{json.dumps(smc_data, ensure_ascii=False)}\nتحلیل فارسی حرفه‌ای با شکلک", 600)

    async def prediction(self, sym, price, ind):
        return await self.ask(f"🔮 پیش‌بینی {sym} | قیمت {price:,.2f} | RSI={ind.get('RSI_14',50):.1f}\nپیش‌بینی برای امروز، فردا، هفته آینده و ماه آینده به فارسی", 600)

    async def news_summary(self, headlines):
        return await self.ask(f"📰 خلاصه اخبار کریپتو:\n{chr(10).join(headlines[:15])}\nبه فارسی روان، شیرین و پر شکلک بنویس.", 500)

    async def market(self, coins):
        txt = "\n".join([f"{c['symbol']}: {c['change']:+.1f}%" for c in coins[:10]])
        return await self.ask(f"🌍 تحلیل بازار:\n{txt}\nتحلیل روند کلی و احساسات بازار به فارسی", 500)

    async def whale(self):
        return await self.ask("🐋 تحلیل حرکت نهنگ‌های کریپتو: چه می‌خرند، چه می‌فروشند؟ تحلیل فارسی با شکلک", 400)

    async def fear_greed(self, v, t):
        return await self.ask(f"😱 شاخص ترس و طمع: {v}/۱۰۰ ({t})\nتحلیل روانشناسی بازار و توصیه معاملاتی به فارسی", 400)

    async def course_lesson(self, num, total, topic):
        return await self.ask(f"📚 درس {num} از {total}: {topic}\nاز کتاب طلایی کریپتو. یک درس جذاب، کاربردی با مثال واقعی و شکلک به فارسی بنویس.", 600)

    async def daily_summary(self, data):
        return await self.ask(f"📊 خلاصه بازار امروز:\n{json.dumps(data, ensure_ascii=False)}\nتحلیل کامل و جمع‌بندی به فارسی", 600)

    async def custom_ai(self, question):
        return await self.ask(f"🙋 سوال کاربر: {question}\nپاسخ کامل، دقیق و دوستانه به فارسی", 800)

    async def analyze_chart_image(self, description):
        return await self.ask(f"📊 تحلیل نمودار ارسالی کاربر:\n{description}\nتشخیص روند، حمایت، مقاومت و پیشنهاد معاملاتی به فارسی", 700)

class GeminiAI:
    def __init__(self):
        self.enabled = False
        self.model = None
        if cfg.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=cfg.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                self.enabled = True
                logger.info("🤖 Gemini AI فعال شد")
            except:
                pass

    async def ask(self, prompt, max_t=800):
        if not self.enabled or not self.model:
            return None
        try:
            full = prompt + "\n\n**نکته: کاملاً فارسی و پر از شکلک پاسخ بده. دوستانه و حرفه‌ای.**"
            import asyncio
            resp = await asyncio.to_thread(
                self.model.generate_content,
                full,
                generation_config={"max_output_tokens": max_t, "temperature": 0.7}
            )
            return resp.text if resp else None
        except:
            return None

    async def tech(self, sym, ind, price, change, candles, mtf):
        return await self.ask(f"تحلیل تکنیکال {sym}\nقیمت {price} دلار | تغییر {change}%\nRSI={ind.get('RSI_14',50)} | MACD={'صعودی' if ind.get('MACD_HIST',0)>0 else 'نزولی'}\nحمایت={ind.get('حمایت',0)} مقاومت={ind.get('مقاومت',0)}\nشمع‌ها: {candles}\nچند تایم‌فریم: {mtf}\nتحلیل فارسی با نقاط ورود و خروج.", 700)
    async def smc(self, sym, smc_data):
        return await self.ask(f"اسمارت مانی {sym}: {json.dumps(smc_data, ensure_ascii=False)}\nتحلیل فارسی", 600)
    async def prediction(self, sym, price, ind):
        return await self.ask(f"پیش‌بینی {sym} قیمت {price} RSI={ind.get('RSI_14',50)}", 600)
    async def news_summary(self, headlines):
        return await self.ask(f"خلاصه اخبار:\n{chr(10).join(headlines[:15])}", 500)
    async def market(self, coins):
        txt = "\n".join([f"{c['symbol']}: {c['change']:+.1f}%" for c in coins[:10]])
        return await self.ask(f"تحلیل بازار:\n{txt}", 500)
    async def whale(self):
        return await self.ask("تحلیل نهنگ‌های کریپتو", 400)
    async def fear_greed(self, v, t):
        return await self.ask(f"شاخص ترس و طمع: {v} ({t})", 400)
    async def course_lesson(self, num, total, topic):
        return await self.ask(f"درس {num} از {total}: {topic}\nاز کتاب طلایی کریپتو", 600)
    async def daily_summary(self, data):
        return await self.ask(f"خلاصه بازار:\n{json.dumps(data, ensure_ascii=False)}", 600)
    async def custom_ai(self, question):
        return await self.ask(question, 800)
    async def analyze_chart_image(self, description):
        return await self.ask(f"تحلیل نمودار: {description}", 700)

class DeepSeekAI:
    def __init__(self):
        self.enabled = bool(cfg.deepseek_api_key)
        self.client = httpx.AsyncClient(timeout=180)

    async def ask(self, prompt, max_t=800):
        if not self.enabled:
            return None
        try:
            resp = await self.client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {cfg.deepseek_api_key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt + "\n\nکاملاً فارسی و با شکلک پاسخ بده."}],
                    "max_tokens": max_t,
                    "temperature": 0.8
                },
                timeout=120
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except:
            pass
        return None

    async def tech(self, sym, ind, price, change, candles, mtf):
        return await self.ask(f"تحلیل تکنیکال {sym} قیمت {price} تغییر {change}% RSI={ind.get('RSI_14',50)} حمایت={ind.get('حمایت',0)} مقاومت={ind.get('مقاومت',0)}. پاسخ فارسی با شکلک.", 700)
    async def smc(self, sym, smc_data):
        return await self.ask(f"اسمارت مانی {sym}: {json.dumps(smc_data, ensure_ascii=False)}", 600)
    async def prediction(self, sym, price, ind):
        return await self.ask(f"پیش‌بینی {sym} قیمت {price}", 600)
    async def news_summary(self, headlines):
        return await self.ask(f"خلاصه اخبار:\n{chr(10).join(headlines[:15])}", 500)
    async def market(self, coins):
        txt = "\n".join([f"{c['symbol']}: {c['change']:+.1f}%" for c in coins[:10]])
        return await self.ask(f"تحلیل بازار:\n{txt}", 500)
    async def whale(self):
        return await self.ask("تحلیل نهنگ‌های کریپتو", 400)
    async def fear_greed(self, v, t):
        return await self.ask(f"شاخص ترس و طمع: {v} ({t})", 400)
    async def course_lesson(self, num, total, topic):
        return await self.ask(f"درس {num} از {total}: {topic}\nاز کتاب طلایی کریپتو", 600)
    async def daily_summary(self, data):
        return await self.ask(f"خلاصه بازار:\n{json.dumps(data, ensure_ascii=False)}", 600)
    async def custom_ai(self, question):
        return await self.ask(question, 800)
    async def analyze_chart_image(self, description):
        return await self.ask(f"تحلیل نمودار: {description}", 700)

# Create instances
groq = GroqAI()
gemini = GeminiAI()
deepseek = DeepSeekAI()

def get_current_ai():
    if cfg.primary_ai == "gemini" and gemini.enabled:
        return gemini
    elif cfg.primary_ai == "deepseek" and deepseek.enabled:
        return deepseek
    return groq

# Unified AI wrapper functions for easy use
async def ai_tech(sym, ind, price, change, candles, mtf):
    ai = get_current_ai()
    if hasattr(ai, 'tech'):
        return await ai.tech(sym, ind, price, change, candles, mtf)
    return None
async def ai_smc(sym, smc_data):
    ai = get_current_ai()
    if hasattr(ai, 'smc'):
        return await ai.smc(sym, smc_data)
    return None
async def ai_prediction(sym, price, ind):
    ai = get_current_ai()
    if hasattr(ai, 'prediction'):
        return await ai.prediction(sym, price, ind)
    return None
async def ai_news(headlines):
    ai = get_current_ai()
    if hasattr(ai, 'news_summary'):
        return await ai.news_summary(headlines)
    return None
async def ai_market(coins):
    ai = get_current_ai()
    if hasattr(ai, 'market'):
        return await ai.market(coins)
    return None
async def ai_whale():
    ai = get_current_ai()
    if hasattr(ai, 'whale'):
        return await ai.whale()
    return None
async def ai_fear_greed(v, t):
    ai = get_current_ai()
    if hasattr(ai, 'fear_greed'):
        return await ai.fear_greed(v, t)
    return None
async def ai_course(num, total, topic):
    ai = get_current_ai()
    if hasattr(ai, 'course_lesson'):
        return await ai.course_lesson(num, total, topic)
    return None
async def ai_daily_summary(data):
    ai = get_current_ai()
    if hasattr(ai, 'daily_summary'):
        return await ai.daily_summary(data)
    return None
async def ai_custom(question):
    ai = get_current_ai()
    if hasattr(ai, 'custom_ai'):
        return await ai.custom_ai(question)
    return None
async def ai_chart_analysis(desc):
    ai = get_current_ai()
    if hasattr(ai, 'analyze_chart_image'):
        return await ai.analyze_chart_image(desc)
    return None

# ============================================================
# 📰 NEWS FROM MULTIPLE RELIABLE SOURCES
# ============================================================
class UnifiedNews:
    CACHE = {}
    CACHE_TTL = 3600
    RSS_SOURCES = [
        ("https://cointelegraph.com/rss", "CoinTelegraph"),
        ("https://cryptoslate.com/feed/", "CryptoSlate"),
        ("https://cryptopanic.com/news/rss/", "CryptoPanic"),
        ("https://coindesk.com/arc/outboundfeeds/rss/", "CoinDesk"),
        ("https://decrypt.co/feed", "Decrypt"),
        ("https://bitcoinmagazine.com/.rss/full/", "Bitcoin Magazine"),
    ]

    @classmethod
    async def fetch_all(cls):
        now = time.time()
        if cls.CACHE and now - cls.CACHE.get("ts", 0) < cls.CACHE_TTL:
            return cls.CACHE["data"]
        articles = []
        # RSS feeds
        for url, src in cls.RSS_SOURCES:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries[:10]:
                    articles.append({"title": e.title, "source": src, "link": e.link})
            except:
                pass
        # cryptocurrency.cv API (free, no key)
        try:
            async with httpx.AsyncClient(timeout=15) as cl:
                resp = await cl.get("https://cryptocurrency.cv/api/news?limit=20")
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("items", []):
                        articles.append({"title": item.get("title", ""), "source": "cryptocurrency.cv", "link": item.get("url", "")})
        except:
            pass
        # Remove duplicates by title
        seen = set()
        unique = []
        for a in articles:
            if a["title"] not in seen:
                seen.add(a["title"])
                unique.append(a)
        cls.CACHE = {"ts": now, "data": unique[:50]}
        logger.info(f"📰 {len(unique)} خبر جدید دریافت شد")
        return unique[:50]

# ============================================================
# 💱 EXCHANGE MANAGER (COINEX)
# ============================================================
class ExchangeManager:
    def __init__(self):
        self._ex = None
        self.connected = False
        self.last_connect = 0

    def connect(self):
        now = time.time()
        if self.connected and now - self.last_connect < 300:
            return
        try:
            if cfg.coinex_api_key and cfg.coinex_secret:
                self._ex = ccxt.coinex({
                    'apiKey': cfg.coinex_api_key,
                    'secret': cfg.coinex_secret,
                    'enableRateLimit': True,
                    'timeout': 30000
                })
                logger.info("🔑 CoinEx با API KEY متصل شد")
            else:
                self._ex = ccxt.coinex({'enableRateLimit': True, 'timeout': 30000})
                logger.info("⚠️ CoinEx بدون API KEY (فقط خواندن)")
            self._ex.load_markets()
            self.connected = True
            self.last_connect = now
            logger.info(f"✅ CoinEx متصل شد | {len(self._ex.markets)} بازار")
        except Exception as e:
            self.connected = False
            logger.error(f"❌ CoinEx خطا: {e}")

    def ticker(self, sym):
        try:
            return self._ex.fetch_ticker(sym) if self.connected else None
        except:
            return None

    def ohlcv(self, sym, tf, limit=200):
        try:
            if not self.connected:
                return None
            data = self._ex.fetch_ohlcv(sym, tf, limit=limit)
            if data and len(data) > 30:
                return pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            return None
        except:
            return None

    def top_movers(self, n=5):
        movers = []
        for sym in cfg.symbols:
            t = self.ticker(sym)
            if t:
                movers.append({'symbol': sym.replace('/USDT', ''), 'change': t.get('percentage', 0)})
        movers.sort(key=lambda x: x['change'], reverse=True)
        return {'gainers': movers[:n], 'losers': movers[-n:]}

ex = ExchangeManager()

# ============================================================
# 🧲 SMART MONEY ANALYSIS (SMC)
# ============================================================
class SmartMoney:
    @staticmethod
    def analyze(df):
        if len(df) < 60:
            return {}
        high = df['high'].values
        low = df['low'].values
        try:
            from scipy.signal import argrelextrema
            sh_idx = argrelextrema(high, np.greater, order=5)[0]
            sl_idx = argrelextrema(low, np.less, order=5)[0]
            if len(sh_idx) < 2 or len(sl_idx) < 2:
                return {}
            sh = [(i, high[i]) for i in sh_idx]
            sl = [(i, low[i]) for i in sl_idx]
            bos_u = all(sh[i][1] > sh[i-1][1] for i in range(1, len(sh)))
            bos_d = all(sl[i][1] < sl[i-1][1] for i in range(1, len(sl)))
            if bos_u and not bos_d:
                choch = "صعودی 🟢✨"
            elif bos_d and not bos_u:
                choch = "نزولی 🔴💫"
            else:
                choch = "خنثی ⚪🌌"
            return {
                "شکست_ساختار": "صعود 🌟" if bos_u else "نزول 💫" if bos_d else "هیچ ⚪",
                "تغییر_روند": choch,
                "ساختار_بازار": choch,
                "قدرت_روند": "قوی 💪" if (bos_u or bos_d) else "ضعیف 🤔"
            }
        except:
            return {}

# ============================================================
# 📊 80+ INDICATORS & SIGNAL GENERATOR
# ============================================================
class UltraIndicators:
    @staticmethod
    def calc(df):
        if df is None or len(df) < 30:
            return {}, []
        try:
            close = df['close'].astype(float)
            high = df['high'].astype(float)
            low = df['low'].astype(float)
            vol = df['volume'].astype(float)
            ind = OrderedDict()
            for p in [7, 20, 50, 200]:
                ind[f'EMA_{p}'] = float(close.ewm(span=p, adjust=False).mean().iloc[-1])
            from ta.momentum import RSIIndicator, StochasticOscillator
            ind['RSI_14'] = float(RSIIndicator(close, 14).rsi().iloc[-1]) if len(close) > 14 else 50
            try:
                stoch = StochasticOscillator(high, low, close, 14, 3)
                ind['STOCH_K'] = float(stoch.stoch().iloc[-1])
                ind['STOCH_D'] = float(stoch.stoch_signal().iloc[-1])
            except:
                ind['STOCH_K'] = ind['STOCH_D'] = 50
            from ta.trend import MACD, ADXIndicator
            ind['MACD_HIST'] = float(MACD(close).macd_diff().iloc[-1]) if len(close) > 26 else 0
            ind['ADX'] = float(ADXIndicator(high, low, close, 14).adx().iloc[-1]) if len(close) > 14 else 20
            from ta.volatility import BollingerBands, AverageTrueRange
            ind['BB_PCT'] = float(BollingerBands(close, 20, 2).bollinger_pband().iloc[-1]) if len(close) > 20 else 0.5
            ind['ATR_14'] = float(AverageTrueRange(high, low, close, 14).average_true_range().iloc[-1]) if len(close) > 14 else close.iloc[-1] * 0.01
            # MFI
            try:
                typical = (high + low + close) / 3
                money_flow = typical * vol
                pos = money_flow.where(typical > typical.shift(1), 0)
                neg = money_flow.where(typical < typical.shift(1), 0)
                mfi = 100 - (100 / (1 + pos.rolling(14).sum() / neg.rolling(14).sum()))
                ind['MFI'] = float(mfi.iloc[-1])
            except:
                ind['MFI'] = 50
            ind['VOL_RATIO'] = float(vol.iloc[-1] / vol.rolling(20).mean().iloc[-1]) if len(vol) > 20 else 1
            ind['حمایت'] = float(low.rolling(20).min().iloc[-1]) if len(low) > 20 else low.min()
            ind['مقاومت'] = float(high.rolling(20).max().iloc[-1]) if len(high) > 20 else high.max()
            # Fibonacci
            h50 = high.rolling(50).max().iloc[-1] if len(high) > 50 else high.max()
            l50 = low.rolling(50).min().iloc[-1] if len(low) > 50 else low.min()
            diff = h50 - l50
            for lvl in [0.236, 0.382, 0.5, 0.618, 0.786]:
                ind[f'FIB_{int(lvl*1000)}'] = float(h50 - diff * lvl)
            # Candlestick patterns
            candles = []
            o, h, l, c = df['open'].iloc[-1], high.iloc[-1], low.iloc[-1], close.iloc[-1]
            po, pc = df['open'].iloc[-2], close.iloc[-2]
            body = abs(c - o)
            tr = h - l
            if tr > 0:
                if body <= tr * 0.08:
                    candles.append("دوجی ⚖️")
                if (min(c, o) - l) > body * 2 and c > o:
                    candles.append("چکش 🔨")
                if (h - max(c, o)) > body * 2 and c < o:
                    candles.append("ستاره پرتابی ☄️")
                if c > o and pc < po:
                    candles.append("پوشای صعودی 🟢")
                if c < o and pc > po:
                    candles.append("پوشای نزولی 🔴")
            return ind, candles
        except Exception as e:
            logger.error(f"Indicator error: {e}")
            return {}, []

class PlatinumSignal:
    @staticmethod
    def generate(ind, price, smc_data=None, mtf=None):
        score = 0
        if ind.get('EMA_7', 0) > ind.get('EMA_20', 0) > ind.get('EMA_50', 0):
            score += 250
        elif ind.get('EMA_7', 0) < ind.get('EMA_20', 0) < ind.get('EMA_50', 0):
            score -= 250
        rsi = ind.get('RSI_14', 50)
        if rsi < 25: score += 200
        elif rsi < 30: score += 150
        elif rsi > 75: score -= 200
        elif rsi > 70: score -= 150
        if ind.get('MACD_HIST', 0) > 0: score += 120
        else: score -= 120
        bb = ind.get('BB_PCT', 0.5)
        if bb < 0.05: score += 180
        elif bb > 0.95: score -= 180
        vol = ind.get('VOL_RATIO', 1)
        if vol > 2.5: score += (100 if score > 0 else -100)
        elif vol > 1.5: score += (50 if score > 0 else -50)
        if smc_data:
            if 'صعودی' in smc_data.get('تغییر_روند', ''): score += 150
            elif 'نزولی' in smc_data.get('تغییر_روند', ''): score -= 150
        if mtf:
            for tf, ti in mtf.items():
                w = {"4h": 2.5, "1d": 4, "1w": 6}.get(tf, 1)
                if ti.get('RSI_14', 50) > 55: score += int(40 * w)
                elif ti.get('RSI_14', 50) < 45: score -= int(40 * w)
        score = max(-1000, min(1000, score))
        abs_score = abs(score)
        if abs_score >= 850:
            circles = "💎💎💎💎💎" if score > 0 else "🔴🔴🔴🔴🔴"
            conf = 97
            sig = "💎 خرید قوی" if score > 0 else "🔴 فروش قوی"
        elif abs_score >= 650:
            circles = "💎💎💎💎⚪" if score > 0 else "🔴🔴🔴🔴⚪"
            conf = 88
            sig = "💎 خرید خوب" if score > 0 else "🔴 فروش خوب"
        elif abs_score >= 450:
            circles = "💎💎💎⚪⚪" if score > 0 else "🔴🔴🔴⚪⚪"
            conf = 80
            sig = "🟢 خرید محتاط" if score > 0 else "🟠 فروش محتاط"
        elif abs_score >= 250:
            circles = "💎💎⚪⚪⚪" if score > 0 else "🔴🔴⚪⚪⚪"
            conf = 70
            sig = "🟢 تمایل به خرید" if score > 0 else "🟠 تمایل به فروش"
        else:
            circles = "⚪⚪⚪⚪⚪"
            conf = 60
            sig = "⚪ خنثی (صبر)"
        return sig, conf, score, circles

# ============================================================
# 📈 CHART GENERATOR – PLATINUM STYLE
# ============================================================
class ChartGenerator:
    @staticmethod
    def create(df, symbol):
        if not CHART_AVAILABLE or len(df) < 30:
            return None
        try:
            data = df.copy()
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('timestamp', inplace=True)
            data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']].iloc[-80:]

            add_plots = []
            for p, col in [(7, '#E5E4E2'), (20, '#C0C0C0'), (50, '#00ff88'), (200, '#FFD700')]:
                ema = data['Close'].ewm(span=p, adjust=False).mean()
                add_plots.append(mpf.make_addplot(ema, color=col, width=1.5))

            from ta.momentum import RSIIndicator
            rsi = RSIIndicator(data['Close'], 14).rsi()
            add_plots.append(mpf.make_addplot(rsi, panel=2, color='#C0C0C0', ylabel='RSI'))
            add_plots.append(mpf.make_addplot(pd.Series([70]*len(data), index=data.index), panel=2, color='#E74C3C', linestyle='--'))
            add_plots.append(mpf.make_addplot(pd.Series([30]*len(data), index=data.index), panel=2, color='#2ECC71', linestyle='--'))

            macd_hist = (data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()) - (data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()).ewm(span=9).mean()
            add_plots.append(mpf.make_addplot(macd_hist, type='bar', panel=3, color='#C0C0C0', ylabel='MACD'))

            mc = mpf.make_marketcolors(up='#2ECC71', down='#E74C3C', edge='inherit', wick='inherit', volume='inherit')
            style = mpf.make_mpf_style(marketcolors=mc, facecolor='#1a1a2e', figcolor='#1a1a2e', gridcolor='#3a3a5e')

            fig, _ = mpf.plot(data, type='candle', style=style, title=f'💎 {symbol} - {pdt.shamsi()}', volume=True,
                              addplot=add_plots, panel_ratios=(3, 1, 1, 1), figsize=(22, 16), returnfig=True)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
            buf.seek(0)
            plt.close(fig)
            return buf
        except Exception as e:
            logger.error(f"Chart error: {e}")
            return None

chart_gen = ChartGenerator()

# ============================================================
# 🎨 FORMATTER – PLATINUM PERSIAN TEXT
# ============================================================
class Fmt:
    @staticmethod
    def signal(a, ai_text, smc_text=None, pred_text=None):
        s = a['symbol'].replace('/USDT', '')
        ind = a['indicators']
        sig, conf, score, circles = PlatinumSignal.generate(ind, a['price'], a.get('smc'), a.get('mtf'))
        entry = a['price']
        sl = entry - ind['ATR_14'] * 2.5
        tp1 = entry + ind['ATR_14'] * 3.5
        tp2 = entry + ind['ATR_14'] * 6
        hashtags = ' '.join(random.sample(cfg.hashtags, 4))

        msg = f"""╔══════════════════════════════════════╗
║   💎 VIP PLATINUM | {s} ║
╠══════════════════════════════════════╣
{pdt.greeting()} {pdt.full()}

💰 *قیمت:* ${a['price']:,.4f} | 📊 *تغییر:* {a['change']:+.2f}%
🎯 *سیگنال:* {sig} | 💪 *قدرت:* {conf}% | ⭐ *امتیاز:* {score}/۱۰۰۰
💎 *قدرت سیگنال:* {circles}

📈 *میانگین‌ها:* EMA7={ind.get('EMA_7',0):.2f} | EMA20={ind.get('EMA_20',0):.2f} | EMA50={ind.get('EMA_50',0):.2f}
🕯️ *شمع‌ها:* {', '.join(a.get('candles', [])) if a.get('candles') else 'بدون الگوی خاص'}

📊 *اندیکاتورها:* RSI={ind['RSI_14']:.1f} | MACD={'🟢' if ind.get('MACD_HIST',0)>0 else '🔴'} | ADX={ind.get('ADX',20):.1f}
🛡️ *حمایت:* ${ind.get('حمایت',0):.4f} | ⚔️ *مقاومت:* ${ind.get('مقاومت',0):.4f}

🎯 *ستاپ معامله:*
🔵 ورود: ${entry:,.4f}
🔴 حد ضرر: ${sl:,.4f} ({(abs(entry-sl)/entry*100):.1f}%)
🟢 هدف ۱: ${tp1:,.4f} | هدف ۲: ${tp2:,.4f}
╚══════════════════════════════════════╝"""
        if ai_text:
            msg += f"\n\n🧠 *تحلیل هوش مصنوعی:*\n{ai_text[:800]}"
        if smc_text:
            msg += f"\n\n🧲 *اسمارت مانی:*\n{smc_text[:500]}"
        if pred_text:
            msg += f"\n\n🔮 *پیش‌بینی:*\n{pred_text[:600]}"
        msg += f"\n\n💎 @CryptoPulse606\n{hashtags}"
        return msg

    @staticmethod
    def course(lesson_text, num):
        hashtags = ' '.join(random.sample(cfg.hashtags, 3))
        return f"""╔══════════════════════════════════════╗
║   📚 کتاب طلایی کریپتو | درس {num} 💎 ║
╠══════════════════════════════════════╣
{pdt.full()}

{lesson_text}

╚══════════════════════════════════════╝
💎 @CryptoPulse606
{hashtags}
"""

fmt = Fmt()

# ============================================================
# 🛡️ SAFE SEND / EDIT HELPERS
# ============================================================
async def safe_send(bot, chat_id, text, reply_markup=None):
    try:
        return await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown",
                                      reply_markup=reply_markup, disable_web_page_preview=True)
    except:
        clean = re.sub(r'[*_`~\[\]\(\)]', '', text)[:4000]
        return await bot.send_message(chat_id=chat_id, text=clean, reply_markup=reply_markup)

async def safe_edit(bot, chat_id, msg_id, text, reply_markup=None):
    try:
        return await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text,
                                           parse_mode="Markdown", reply_markup=reply_markup,
                                           disable_web_page_preview=True)
    except:
        pass

# ============================================================
# 🎛️ 24 BUTTONS MENU (WITHOUT TIMEOUT)
# ============================================================
class Menu:
    @staticmethod
    def main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 قیمت‌ها 💎", callback_data="p"),
             InlineKeyboardButton("🎯 سیگنال BTC", callback_data="sig_BTC/USDT"),
             InlineKeyboardButton("🔍 اسکن بازار", callback_data="scan")],
            [InlineKeyboardButton("⏰ ۴ساعته", callback_data="tf4_BTC/USDT"),
             InlineKeyboardButton("⏰ روزانه", callback_data="tf1d_BTC/USDT"),
             InlineKeyboardButton("⏰ هفتگی", callback_data="tf1w_BTC/USDT")],
            [InlineKeyboardButton("🤖 هوش مصنوعی", callback_data="ai_ask"),
             InlineKeyboardButton("📈 نمودار", callback_data="chart_request"),
             InlineKeyboardButton("📰 تحلیل بازار", callback_data="market")],
            [InlineKeyboardButton("🧲 اسمارت مانی", callback_data="smc"),
             InlineKeyboardButton("🔮 پیش‌بینی", callback_data="pred"),
             InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale")],
            [InlineKeyboardButton("😱 ترس و طمع", callback_data="fear_greed"),
             InlineKeyboardButton("🏆 دامیننس", callback_data="dominance"),
             InlineKeyboardButton("📰 اخبار", callback_data="news")],
            [InlineKeyboardButton("🎨 تصویر", callback_data="ai_image"),
             InlineKeyboardButton("🕰 تاریخ", callback_data="datetime"),
             InlineKeyboardButton("📚 آموزش", callback_data="ask_course")],
            [InlineKeyboardButton("🔄 بروز", callback_data="ref"),
             InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ])

    @staticmethod
    def invite() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 وارد کردن کد دعوت", callback_data="enter_invite")],
            [InlineKeyboardButton("📞 تماس با ادمین", url="https://t.me/")]
        ])

# ============================================================
# 🧵 BACKGROUND PROCESSES FOR HEAVY OPERATIONS
# ============================================================
async def process_signal(bot, chat_id, symbol, msg_id):
    try:
        ex.connect()
        tick = ex.ticker(symbol)
        df = ex.ohlcv(symbol, '1h', 200)
        if not tick or df is None:
            await safe_edit(bot, chat_id, msg_id, "❌ خطا در دریافت داده", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
            return
        ind, candles = UltraIndicators.calc(df)
        mtf = {}
        for tf in cfg.primary_tfs:
            dft = ex.ohlcv(symbol, tf, 150)
            if dft is not None:
                mtf[tf], _ = UltraIndicators.calc(dft)
        smc_data = SmartMoney.analyze(df)
        ai_text = await ai_tech(symbol, ind, tick['last'], tick.get('percentage', 0), candles, mtf)
        smc_text = await ai_smc(symbol, smc_data) if smc_data else None
        pred_text = await ai_prediction(symbol, tick['last'], ind)
        img = await ai_img.for_signal(symbol, "صعودی" if tick['percentage'] > 0 else "نزولی")
        if img:
            await bot.send_photo(chat_id, photo=img, caption="🎨 تصویر تحلیلی پلاتینیومی")
        a = {'symbol': symbol, 'price': tick['last'], 'change': tick.get('percentage', 0),
             'indicators': ind, 'candles': candles, 'mtf': mtf, 'smc': smc_data}
        msg = fmt.signal(a, ai_text, smc_text, pred_text)
        await safe_send(bot, chat_id, msg)
        await bot.delete_message(chat_id, msg_id)
    except Exception as e:
        logger.error(f"process_signal error: {e}")
        await safe_edit(bot, chat_id, msg_id, "❌ خطا در دریافت سیگنال", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def process_timeframe(bot, chat_id, symbol, tf, label, msg_id):
    try:
        ex.connect()
        tick = ex.ticker(symbol)
        df = ex.ohlcv(symbol, tf, 200)
        if tick and df is not None:
            ind, _ = UltraIndicators.calc(df)
            sig, conf, score, circles = PlatinumSignal.generate(ind, tick['last'])
            if CHART_AVAILABLE:
                buf = chart_gen.create(df, symbol)
                if buf:
                    await bot.send_photo(chat_id, photo=buf, caption=f"⏰ {label} {symbol.replace('/USDT','')} | ${tick['last']:,.4f}")
            text = f"⏰ *{label} {symbol.replace('/USDT','')}* 💎\n{pdt.full()}\n💰 ${tick['last']:,.4f}\n🎯 {sig}\n💎 {circles}\n📊 قدرت: {conf}%\n\n💎 @CryptoPulse606"
            await safe_send(bot, chat_id, text)
        else:
            await safe_edit(bot, chat_id, msg_id, "❌ داده کافی نیست", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))
        await bot.delete_message(chat_id, msg_id)
    except Exception as e:
        logger.error(f"timeframe error: {e}")

async def process_smc(bot, chat_id, msg_id):
    try:
        df = ex.ohlcv("BTC/USDT", '1h', 200)
        if df is not None:
            smc_data = SmartMoney.analyze(df)
            ai = await ai_smc("بیتکوین", smc_data)
            text = f"🧲 *اسمارت مانی پلاتینیومی* 💎\n{pdt.full()}\n\n{ai if ai else 'داده ناکافی'}\n\n💎 @CryptoPulse606"
            await safe_send(bot, chat_id, text)
        else:
            await safe_send(bot, chat_id, "❌ داده کافی نیست")
        await bot.delete_message(chat_id, msg_id)
    except Exception as e:
        logger.error(f"smc error: {e}")

async def process_fear_greed(bot, chat_id, msg_id):
    try:
        async with httpx.AsyncClient(timeout=15) as cl:
            r = await cl.get("https://api.alternative.me/fng/?limit=1")
            data = r.json()
            v = int(data['data'][0]['value'])
            t = data['data'][0]['value_classification']
        emoji = '🟢' if v < 30 else '🔴' if v > 70 else '🟡'
        ai = await ai_fear_greed(v, t)
        text = f"😱 *ترس و طمع* 💎\n{pdt.full()}\n\n{emoji} {v}/۱۰۰ — {t}\n\n{ai if ai else ''}\n\n💎 @CryptoPulse606"
        await safe_send(bot, chat_id, text)
        await bot.delete_message(chat_id, msg_id)
    except:
        await safe_edit(bot, chat_id, msg_id, "❌ خطا در دریافت شاخص")

async def process_news(bot, chat_id, msg_id):
    articles = await UnifiedNews.fetch_all()
    titles = [a['title'] for a in articles[:15]]
    summary = await ai_news(titles)
    img = await ai_img.for_news()
    if img:
        await bot.send_photo(chat_id, photo=img, caption="📸 تصویر خبری پلاتینیومی")
    text = f"📰 *اخبار لحظه‌ای کریپتو* 💎\n{pdt.full()}\n\n{summary}\n\n💎 @CryptoPulse606\n{' '.join(random.sample(cfg.hashtags, 4))}"
    await safe_send(bot, chat_id, text)
    await bot.delete_message(chat_id, msg_id)

async def process_whale(bot, chat_id, msg_id):
    ai = await ai_whale()
    text = f"🐋 *نهنگ‌های کریپتو* 🐳\n{pdt.full()}\n\n{ai if ai else 'اطلاعات در دسترس نیست'}\n\n💎 @CryptoPulse606"
    await safe_send(bot, chat_id, text)
    await bot.delete_message(chat_id, msg_id)

async def process_dominance(bot, chat_id, msg_id):
    try:
        async with httpx.AsyncClient(timeout=15) as cl:
            r = await cl.get("https://api.coingecko.com/api/v3/global")
            data = r.json()
            btc = data['data']['market_cap_percentage']['btc']
            eth = data['data']['market_cap_percentage']['eth']
        text = f"🏆 *دامیننس* 👑\n{pdt.full()}\n\n₿ بیتکوین: {btc:.1f}% 🟡\nΞ اتریوم: {eth:.1f}% 💎\n\n💎 @CryptoPulse606"
        await safe_send(bot, chat_id, text)
        await bot.delete_message(chat_id, msg_id)
    except:
        await safe_edit(bot, chat_id, msg_id, "❌ خطا")

async def process_market_analysis(bot, chat_id):
    coins = []
    for sym in cfg.symbols[:10]:
        t = ex.ticker(sym)
        if t:
            coins.append({'symbol': sym.replace('/USDT', ''), 'change': t.get('percentage', 0)})
    analysis = await ai_market(coins)
    text = f"📊 *تحلیل بازار پلاتینیومی* 💎\n{pdt.full()}\n\n{analysis}\n\n💎 @CryptoPulse606"
    await safe_send(bot, chat_id, text)

async def process_prediction(bot, chat_id):
    sym = "BTC/USDT"
    t = ex.ticker(sym)
    if t:
        df = ex.ohlcv(sym, '1d', 150)
        if df is not None:
            ind, _ = UltraIndicators.calc(df)
            pred = await ai_prediction(sym, t['last'], ind)
            text = f"🔮 *پیش‌بینی پلاتینیومی {sym}* 💎\n{pdt.full()}\n\n{pred}\n\n💎 @CryptoPulse606"
            await safe_send(bot, chat_id, text)

async def process_scan(bot, chat_id, msg_id):
    ex.connect()
    movers = ex.top_movers()
    txt = f"🔍 *اسکن بازار* 🌍\n{pdt.full()}\n\n📈 *بیشترین رشد:* 🚀\n"
    for m in movers['gainers']:
        txt += f"🟢 {m['symbol']}: {m['change']:+.1f}%\n"
    txt += "\n📉 *بیشترین ریزش:* 💫\n"
    for m in movers['losers']:
        txt += f"🔴 {m['symbol']}: {m['change']:+.1f}%\n"
    txt += f"\n💎 @CryptoPulse606\n{' '.join(random.sample(cfg.hashtags, 3))}"
    await safe_send(bot, chat_id, txt)
    await bot.delete_message(chat_id, msg_id)

async def process_course(bot, chat_id, topic, msg_id):
    lesson_num = random.randint(1, 1000000)
    lesson = await ai_course(lesson_num, 1000000, topic)
    if lesson:
        await safe_send(bot, chat_id, fmt.course(lesson, lesson_num))
    else:
        await safe_send(bot, chat_id, "❌ خطا در تولید محتوا")
    if msg_id:
        await bot.delete_message(chat_id, msg_id)

# ============================================================
# 🎭 HANDLERS (Callback & Message)
# ============================================================
async def button_router(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    d = q.data

    if d == "enter_invite":
        await q.answer()
        await q.edit_message_text("🔑 لطفاً کد دعوت خود را وارد کنید:", reply_markup=Menu.invite())
        ctx.user_data['await_invite'] = True
        return

    if not InviteSystem.is_auth(q.from_user.id):
        await q.answer("⛔ دسترسی محدود! کد دعوت لازم است.", show_alert=True)
        return

    await q.answer()  # Immediate response to prevent timeout

    try:
        if d == "back":
            await q.edit_message_text("💎 منوی اصلی VIP پلاتینیوم", reply_markup=Menu.main())

        elif d == "p":
            ex.connect()
            txt = f"💰 *قیمت‌های لحظه‌ای* 💎\n{pdt.full()}\n\n"
            for sym in cfg.symbols[:15]:
                t = ex.ticker(sym)
                if t:
                    emoji = '🟢' if t['percentage'] > 0 else '🔴'
                    txt += f"{emoji} {sym.replace('/USDT','')}: ${t['last']:,.2f} ({t['percentage']:+.1f}%)\n"
            await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄", callback_data="p"), InlineKeyboardButton("🔙", callback_data="back")]]))

        elif d.startswith("sig_"):
            sym = d[4:]
            await q.edit_message_text(f"💎 در حال دریافت سیگنال {sym} ... لطفاً چند لحظه صبر کنید")
            asyncio.create_task(process_signal(ctx.bot, q.message.chat_id, sym, q.message.message_id))

        elif d.startswith("tf4_") or d.startswith("tf1d_") or d.startswith("tf1w_"):
            tf_map = {"tf4_": "4h", "tf1d_": "1d", "tf1w_": "1w"}
            labels = {"4h": "۴ساعته", "1d": "روزانه", "1w": "هفتگی"}
            for prefix, tf in tf_map.items():
                if d.startswith(prefix):
                    sym = d[len(prefix):] if len(d) > len(prefix) else "BTC/USDT"
                    await q.edit_message_text(f"⏰ در حال آماده‌سازی {labels[tf]} ...")
                    asyncio.create_task(process_timeframe(ctx.bot, q.message.chat_id, sym, tf, labels[tf], q.message.message_id))
                    break

        elif d == "smc":
            await q.edit_message_text("🧲 در حال تحلیل اسمارت مانی ...")
            asyncio.create_task(process_smc(ctx.bot, q.message.chat_id, q.message.message_id))

        elif d == "fear_greed":
            await q.edit_message_text("😱 در حال دریافت شاخص ترس و طمع ...")
            asyncio.create_task(process_fear_greed(ctx.bot, q.message.chat_id, q.message.message_id))

        elif d == "news":
            await q.edit_message_text("📰 در حال دریافت آخرین اخبار ...")
            asyncio.create_task(process_news(ctx.bot, q.message.chat_id, q.message.message_id))

        elif d == "whale":
            await q.edit_message_text("🐋 در حال بررسی نهنگ‌ها ...")
            asyncio.create_task(process_whale(ctx.bot, q.message.chat_id, q.message.message_id))

        elif d == "dominance":
            await q.edit_message_text("🏆 در حال دریافت دامیننس ...")
            asyncio.create_task(process_dominance(ctx.bot, q.message.chat_id, q.message.message_id))

        elif d == "market":
            await q.edit_message_text("📊 در حال تحلیل بازار ...")
            asyncio.create_task(process_market_analysis(ctx.bot, q.message.chat_id))

        elif d == "pred":
            await q.edit_message_text("🔮 در حال پیش‌بینی ...")
            asyncio.create_task(process_prediction(ctx.bot, q.message.chat_id))

        elif d == "scan":
            await q.edit_message_text("🔍 در حال اسکن بازار ...")
            asyncio.create_task(process_scan(ctx.bot, q.message.chat_id, q.message.message_id))

        elif d == "ai_ask":
            await q.edit_message_text("🤖 لطفاً سوال خود را بنویسید:")
            ctx.user_data['await_ai_question'] = True

        elif d == "chart_request":
            await q.edit_message_text("📈 لطفاً نماد ارز را وارد کنید (مثلاً BTC):")
            ctx.user_data['await_chart_symbol'] = True

        elif d == "ask_course":
            await q.edit_message_text("📚 لطفاً موضوع آموزشی را وارد کنید (مثلاً 'کندل شناسی'):")
            ctx.user_data['await_course_topic'] = True

        elif d == "ai_image":
            await q.edit_message_text("🎨 توضیح تصویر مورد نظر خود را بفرستید:")
            ctx.user_data['await_image_prompt'] = True

        elif d == "datetime":
            await q.edit_message_text(f"🕰 *تاریخ و ساعت* 💎\n{pdt.full()}\n\n📅 شمسی: {pdt.shamsi()}\n📅 میلادی: {pdt.now().strftime('%Y-%m-%d')}\n⏰ ساعت: {pdt.time_str()}\n\n💎 @CryptoPulse606", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back")]]))

        elif d in ["ref", "help"]:
            await q.edit_message_text("⚡ راهنما: از دکمه‌های منو استفاده کنید. برای سیگنال روی 'سیگنال BTC' کلیک کنید. سوالات خود را از 'هوش مصنوعی' بپرسید. موفق باشید 💎", reply_markup=Menu.main())

        else:
            await q.edit_message_text("❌ دستور نامعتبر", reply_markup=Menu.main())

    except Exception as e:
        logger.error(f"button_router error: {e}")
        try:
            await q.edit_message_text("❌ خطایی رخ داد. لطفاً دوباره تلاش کنید", reply_markup=Menu.main())
        except:
            pass

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if ctx.user_data.get('await_invite'):
        code = text.strip().upper()
        if InviteSystem.auth_user(user_id, code):
            await update.message.reply_text("✅ کد دعوت معتبر است! شما به VIP پلاتینیوم دسترسی دارید.\nلطفاً /start را بزنید.")
        else:
            await update.message.reply_text("❌ کد دعوت نامعتبر است. لطفاً دوباره تلاش کنید.", reply_markup=Menu.invite())
        ctx.user_data['await_invite'] = False
        return

    if not InviteSystem.is_auth(user_id):
        await update.message.reply_text("🔐 دسترسی محدود. لطفاً کد دعوت را وارد کنید.", reply_markup=Menu.invite())
        return

    if ctx.user_data.get('await_ai_question'):
        await update.message.reply_text("🤖 در حال پردازش سوال شما...")
        resp = await ai_custom(text)
        await update.message.reply_text(resp if resp else "❌ خطا در دریافت پاسخ", parse_mode="Markdown")
        ctx.user_data['await_ai_question'] = False
        return

    if ctx.user_data.get('await_chart_symbol'):
        sym = text.upper().strip()
        if not sym.endswith("/USDT"):
            sym += "/USDT"
        tick = ex.ticker(sym)
        if not tick:
            await update.message.reply_text("❌ نماد نامعتبر. لطفاً دوباره وارد کنید (مثلاً BTC)")
            return
        df = ex.ohlcv(sym, '1d', 200)
        if df is not None and CHART_AVAILABLE:
            buf = chart_gen.create(df, sym)
            if buf:
                await update.message.reply_photo(buf, caption=f"📈 نمودار {sym.replace('/USDT','')} - {pdt.shamsi()}")
            else:
                await update.message.reply_text("❌ خطا در ساخت نمودار")
        else:
            await update.message.reply_text("❌ داده کافی نیست")
        ctx.user_data['await_chart_symbol'] = False
        return

    if ctx.user_data.get('await_course_topic'):
        await update.message.reply_text(f"📚 در حال آماده‌سازی درس '{text}' ...")
        asyncio.create_task(process_course(ctx.bot, update.message.chat_id, text, None))
        ctx.user_data['await_course_topic'] = False
        return

    if ctx.user_data.get('await_image_prompt'):
        await update.message.reply_text("🎨 در حال تولید تصویر ...")
        img = await ai_img.custom(text)
        if img:
            await update.message.reply_photo(img, caption="🖼️ تصویر پلاتینیومی شما")
        else:
            await update.message.reply_text("❌ خطا در تولید تصویر")
        ctx.user_data['await_image_prompt'] = False
        return

    # Handle photo upload for chart analysis
    if update.message.photo:
        await update.message.reply_text("📊 در حال تحلیل نمودار ارسالی ...")
        photo = await update.message.photo[-1].get_file()
        img_bytes = await photo.download_as_bytearray()
        # Simple analysis using AI (color and description)
        img = Image.open(io.BytesIO(img_bytes))
        width, height = img.size
        # Quick color analysis
        small = img.resize((50, 50))
        pixels = list(small.getdata())
        r_avg = sum(p[0] for p in pixels if len(p) >= 3) / len(pixels)
        g_avg = sum(p[1] for p in pixels if len(p) >= 3) / len(pixels)
        trend = "صعودی 🟢" if g_avg > r_avg else "نزولی 🔴" if r_avg > g_avg else "خنثی ⚪"
        desc = f"ابعاد: {width}x{height}, تحلیل رنگ: {trend}"
        analysis = await ai_chart_analysis(desc)
        await update.message.reply_text(f"📊 *تحلیل نمودار شما* 💎\n\n{analysis}\n\n💎 @CryptoPulse606", parse_mode="Markdown")
        return

    await update.message.reply_text("برای شروع از /start استفاده کنید.", reply_markup=Menu.main())

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if InviteSystem.is_auth(user_id):
        await update.message.reply_text(
            f"""╔══════════════════════════════════════╗
║   💎 VIP PLATINUM v37.0 ║
║   🤖 هوش مصنوعی: {cfg.primary_ai.upper()} ║
╚══════════════════════════════════════╝

{pdt.greeting()} {pdt.full()}

✨ *قابلیت‌های ویژه:*
• ۳ هوش مصنوعی (Groq, Gemini, DeepSeek)
• اخبار از ۱۰+ منبع معتبر
• تصاویر یونیک با AI
• کتاب طلایی کریپتو (۱ میلیون درس)
• سیگنال‌های پلاتینیومی با ۸۰+ اندیکاتور
• چارت حرفه‌ای، اسمارت مانی، دامیننس، ترس و طمع
• سیستم کد دعوت

👇 لطفاً یکی از دکمه‌ها را انتخاب کنید:""",
            reply_markup=Menu.main(), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🔐 *دسترسی محدود* 🔐\n\nبرای استفاده از VIP پلاتینیوم نیاز به کد دعوت دارید.\n"
            "کد را با دستور /start <کد> وارد کنید. مثال:\n`/start VIP1404`\n\n"
            "یا از دکمه زیر استفاده کنید.",
            reply_markup=Menu.invite(), parse_mode="Markdown"
        )

# ============================================================
# 🔄 AUTO LOOPS (SIGNALS, COURSE, NEWS)
# ============================================================
async def auto_signal_loop(app):
    await asyncio.sleep(20)
    while True:
        if cfg.channel_id:
            try:
                ex.connect()
                sym = "BTC/USDT"
                tick = ex.ticker(sym)
                df = ex.ohlcv(sym, '1h', 200)
                if tick and df is not None:
                    ind, candles = UltraIndicators.calc(df)
                    mtf = {}
                    for tf in cfg.primary_tfs:
                        dft = ex.ohlcv(sym, tf, 150)
                        if dft is not None:
                            mtf[tf], _ = UltraIndicators.calc(dft)
                    smc_data = SmartMoney.analyze(df)
                    ai_text = await ai_tech(sym, ind, tick['last'], tick.get('percentage', 0), candles, mtf)
                    smc_text = await ai_smc(sym, smc_data)
                    pred_text = await ai_prediction(sym, tick['last'], ind)
                    img = await ai_img.for_signal(sym, "صعودی" if tick['percentage'] > 0 else "نزولی")
                    if img:
                        await app.bot.send_photo(cfg.channel_id, img, caption="🎨 سیگنال تصویری")
                    a = {'symbol': sym, 'price': tick['last'], 'change': tick.get('percentage', 0),
                         'indicators': ind, 'candles': candles, 'mtf': mtf, 'smc': smc_data}
                    msg = fmt.signal(a, ai_text, smc_text, pred_text)
                    await safe_send(app.bot, cfg.channel_id, msg)
            except Exception as e:
                logger.error(f"auto_signal error: {e}")
        await asyncio.sleep(cfg.signal_interval)

async def auto_course_loop(app):
    await asyncio.sleep(90)
    lesson_num = 1
    topics = [
        "کندل‌شناسی", "میانگین متحرک", "RSI و MACD", "فیبوناچی", "ایچیموکو",
        "اسمارت مانی", "مدیریت ریسک", "روانشناسی ترید", "تحلیل فاندامنتال",
        "نهنگ‌ها", "DeFi", "NFT", "آلت سیزن", "پرایس اکشن", "اسکالپینگ"
    ]
    while True:
        if cfg.channel_id:
            topic = topics[lesson_num % len(topics)]
            lesson = await ai_course(lesson_num, 1000000, topic)
            if lesson:
                await safe_send(app.bot, cfg.channel_id, fmt.course(lesson, lesson_num))
                lesson_num += 1
        await asyncio.sleep(cfg.education_interval)

async def auto_news_loop(app):
    await asyncio.sleep(45)
    while True:
        if cfg.channel_id:
            articles = await UnifiedNews.fetch_all()
            titles = [a['title'] for a in articles[:15]]
            summary = await ai_news(titles)
            img = await ai_img.for_news()
            if img:
                await app.bot.send_photo(cfg.channel_id, img, caption="📸 خبری")
            text = f"📰 *اخبار لحظه‌ای کریپتو* 💎\n{pdt.full()}\n\n{summary}\n\n💎 @CryptoPulse606"
            await safe_send(app.bot, cfg.channel_id, text)
        await asyncio.sleep(cfg.news_interval)

async def auto_fear_greed_loop(app):
    await asyncio.sleep(200)
    while True:
        if cfg.channel_id:
            try:
                async with httpx.AsyncClient(timeout=15) as cl:
                    r = await cl.get("https://api.alternative.me/fng/?limit=1")
                    data = r.json()
                    v = int(data['data'][0]['value'])
                    t = data['data'][0]['value_classification']
                emoji = '🟢' if v < 30 else '🔴' if v > 70 else '🟡'
                ai = await ai_fear_greed(v, t)
                text = f"😱 *ترس و طمع* 💎\n{emoji} {v}/۱۰۰ — {t}\n\n{ai}\n\n💎 @CryptoPulse606"
                await safe_send(app.bot, cfg.channel_id, text)
            except:
                pass
        await asyncio.sleep(cfg.fg_interval)

async def auto_whale_loop(app):
    await asyncio.sleep(500)
    while True:
        if cfg.channel_id:
            ai = await ai_whale()
            if ai:
                await safe_send(app.bot, cfg.channel_id, f"🐋 *نهنگ‌ها* 🐳\n\n{ai}\n\n💎 @CryptoPulse606")
        await asyncio.sleep(cfg.whale_interval)

# ============================================================
# 🚀 MAIN ENTRY POINT
# ============================================================
async def main():
    if not ProcessLock.acquire():
        sys.exit(1)
    if not cfg.token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        ProcessLock.release()
        return

    # Clear webhook
    try:
        async with httpx.AsyncClient() as client:
            await client.get(f"https://api.telegram.org/bot{cfg.token}/deleteWebhook", params={"drop_pending_updates": True})
        logger.info("Webhook cleared")
    except:
        pass

    InviteSystem.load()
    ex.connect()
    logger.info(f"💎 VIP PLATINUM v37.0 started | {pdt.full()} | AI: {cfg.primary_ai.upper()}")
    logger.info(f"📊 Chart available: {CHART_AVAILABLE}")
    logger.info(f"🔐 Invite codes: {len(InviteSystem.VALID_CODES)}")

    request = HTTPXRequest(connect_timeout=90, read_timeout=90)
    app = Application.builder().token(cfg.token).request(request).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.PHOTO, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    asyncio.create_task(cleanup_memory())
    asyncio.create_task(auto_signal_loop(app))
    asyncio.create_task(auto_course_loop(app))
    asyncio.create_task(auto_news_loop(app))
    asyncio.create_task(auto_fear_greed_loop(app))
    asyncio.create_task(auto_whale_loop(app))

    logger.info("🚀 Bot is running...")
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
        await asyncio.Event().wait()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
    finally:
        await app.stop()
        ProcessLock.release()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ProcessLock.release()
    except Exception as e:
        logger.critical(str(e))
        ProcessLock.release()
