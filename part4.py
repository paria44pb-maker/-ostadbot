
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Utilities Module
ماژول ابزارها، زمان تهران، Emoji، فرمت‌ها و توابع کمکی پیشرفته
"""

import os
import sys
import re
import json
import math
import random
import string
import hashlib
import base64
import binascii
import unicodedata
import pytz
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache, wraps
from decimal import Decimal, ROUND_DOWN, ROUND_UP, ROUND_HALF_UP
from zoneinfo import ZoneInfo
import emoji as emoji_lib

# ==================== زمان تهران ====================

class TehranTime:
    """مدیریت زمان تهران با پشتیبانی کامل از ساعت تابستانی"""
    
    _instance = None
    _tehran_tz = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._tehran_tz = ZoneInfo("Asia/Tehran")
        self._utc_tz = ZoneInfo("UTC")
        
        self.DST_START = (3, 21, 0, 0)
        self.DST_END = (9, 21, 0, 0)
        self.TIMEZONE_OFFSET = 3.5
        
        self._leap_years = self._generate_leap_years()
        self._persian_months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                               'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        self._persian_weekdays = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه']
        self._persian_numbers = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
                                '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}
    
    def _generate_leap_years(self) -> set:
        leap_years = set()
        for year in range(1350, 1450):
            if self._is_leap_year(year):
                leap_years.add(year)
        return leap_years
    
    def _is_leap_year(self, year: int) -> bool:
        a = year % 33
        return a in [1, 5, 9, 13, 17, 22, 26, 30]
    
    def now(self) -> datetime:
        return datetime.now(self._tehran_tz)
    
    def now_utc(self) -> datetime:
        return datetime.now(self._utc_tz)
    
    def now_timestamp(self) -> int:
        return int(self.now().timestamp())
    
    def now_iso(self) -> str:
        return self.now().isoformat()
    
    def now_persian(self) -> str:
        return self.to_persian_format(self.now())
    
    def now_persian_short(self) -> str:
        dt = self.now()
        persian = self.gregorian_to_persian(dt.year, dt.month, dt.day)
        return f"{persian[0]}/{persian[1]:02d}/{persian[2]:02d} {dt.hour:02d}:{dt.minute:02d}"
    
    def now_persian_date(self) -> str:
        dt = self.now()
        persian = self.gregorian_to_persian(dt.year, dt.month, dt.day)
        return f"{persian[0]}/{persian[1]:02d}/{persian[2]:02d}"
    
    def now_persian_time(self) -> str:
        dt = self.now()
        return f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    
    def to_persian_format(self, dt: datetime) -> str:
        persian_year = self.gregorian_to_persian(dt.year, dt.month, dt.day)
        weekday_str = self._persian_weekdays[dt.weekday()]
        month_str = self._persian_months[persian_year[1] - 1]
        
        year_str = self.to_persian_num(persian_year[0])
        day_str = self.to_persian_num(persian_year[2])
        hour_str = self.to_persian_num(dt.hour)
        minute_str = self.to_persian_num(dt.minute)
        
        return f"{weekday_str} {day_str} {month_str} {year_str} - {hour_str}:{minute_str}"
    
    def to_persian_num(self, num: int) -> str:
        return ''.join(self._persian_numbers.get(c, c) for c in str(num))
    
    def from_persian_num(self, text: str) -> str:
        reverse_map = {v: k for k, v in self._persian_numbers.items()}
        return ''.join(reverse_map.get(c, c) for c in text)
    
    def gregorian_to_persian(self, gy: int, gm: int, gd: int) -> tuple:
        g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
        
        gy = gy - 1600
        gm = gm - 1
        gd = gd - 1
        
        g_day_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
        
        for i in range(gm):
            g_day_no += g_days_in_month[i]
        if gm > 1 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
            g_day_no += 1
        g_day_no += gd
        
        j_day_no = g_day_no - 227468
        
        j_year = (j_day_no * 4 + 3) // 1461
        j_day_no = j_day_no - (j_year * 1461) // 4
        j_month = (j_day_no * 6 + 3) // 183
        j_day_no = j_day_no - (j_month * 183) // 6
        j_day = j_day_no + 1
        
        return (j_year + 1380, j_month + 1, j_day)
    
    def persian_to_gregorian(self, jy: int, jm: int, jd: int) -> tuple:
        j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
        g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        jy = jy - 1380
        jm = jm - 1
        jd = jd - 1
        
        j_day_no = 365 * jy + (jy + 3) // 4
        
        for i in range(jm):
            j_day_no += j_days_in_month[i]
        j_day_no += jd
        
        g_day_no = j_day_no + 227468
        
        g_year = (g_day_no * 4 + 3) // 1461
        g_day_no = g_day_no - (g_year * 1461) // 4
        g_month = (g_day_no * 12 + 6) // 367
        g_day_no = g_day_no - (g_month * 367) // 12
        g_day = g_day_no + 1
        
        return (g_year + 1600, g_month + 1, g_day)
    
    def format_datetime(self, dt: datetime = None, format_type: str = "full") -> str:
        if dt is None:
            dt = self.now()
        
        formats = {
            "full": "%Y-%m-%d %H:%M:%S",
            "date": "%Y-%m-%d",
            "time": "%H:%M:%S",
            "short": "%y/%m/%d %H:%M",
            "persian": self.to_persian_format(dt),
            "persian_short": self.now_persian_short(),
            "iso": dt.isoformat(),
            "timestamp": str(int(dt.timestamp())),
        }
        
        return formats.get(format_type, formats["full"])
    
    def relative_time(self, dt: datetime) -> str:
        now = self.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return f"{int(seconds)} ثانیه پیش"
        elif seconds < 3600:
            return f"{int(seconds / 60)} دقیقه پیش"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} ساعت پیش"
        elif seconds < 604800:
            return f"{int(seconds / 86400)} روز پیش"
        elif seconds < 2592000:
            return f"{int(seconds / 604800)} هفته پیش"
        elif seconds < 31536000:
            return f"{int(seconds / 2592000)} ماه پیش"
        else:
            return f"{int(seconds / 31536000)} سال پیش"
    
    def get_timezone_offset(self) -> str:
        offset = self.TIMEZONE_OFFSET
        hours = int(offset)
        minutes = int((offset - hours) * 60)
        return f"UTC+{hours}:{minutes:02d}"
    
    def is_dst(self) -> bool:
        return bool(self.now().dst())
    
    def get_day_start(self, dt: datetime = None) -> datetime:
        if dt is None:
            dt = self.now()
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_day_end(self, dt: datetime = None) -> datetime:
        if dt is None:
            dt = self.now()
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    def get_week_start(self, dt: datetime = None) -> datetime:
        if dt is None:
            dt = self.now()
        start = dt - timedelta(days=dt.weekday())
        return start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_month_start(self, dt: datetime = None) -> datetime:
        if dt is None:
            dt = self.now()
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def days_between(self, date1: datetime, date2: datetime) -> int:
        return abs((date1 - date2).days)

# ==================== Emoji کامل ====================

class EmojiManager:
    """مدیریت Emoji با بیش از ۲۰۰ ایموجی"""
    
    # ایموجی‌های پایه
    BASIC = {
        "chart": "📊",
        "signal": "🚨",
        "analysis": "📈",
        "settings": "⚙️",
        "wallet": "💰",
        "admin": "👑",
        "buy": "🟢",
        "sell": "🔴",
        "hold": "🟡",
        "loading": "⏳",
        "success": "✅",
        "error": "❌",
        "info": "ℹ️",
        "fire": "🔥",
        "lightning": "⚡",
        "vip": "💎",
        "user": "👤",
        "support": "🆘",
        "help": "📖",
        "star": "⭐",
        "heart": "❤️",
        "rocket": "🚀",
        "shield": "🛡️",
        "trophy": "🏆",
        "crown": "👑",
        "diamond": "💎",
        "coin": "🪙",
        "money": "💵",
        "credit": "💳",
        "bank": "🏦",
        "graph": "📉",
        "candle": "🕯️",
        "bell": "🔔",
        "lock": "🔒",
        "unlock": "🔓",
        "key": "🔑",
        "phone": "📱",
        "computer": "💻",
        "globe": "🌍",
        "flag": "🏁",
        "party": "🎉",
        "gift": "🎁",
        "ticket": "🎫",
        "medal": "🏅",
        "ribbon": "🎀",
        "pizza": "🍕",
        "coffee": "☕",
        "beer": "🍺",
        "cake": "🎂",
        "sun": "☀️",
        "moon": "🌙",
        "cloud": "☁️",
        "rain": "🌧️",
        "snow": "❄️",
        "storm": "⛈️",
        "wind": "💨",
        "water": "💧",
        "earth": "🌍",
        "mountain": "🏔️",
        "forest": "🌲",
        "flower": "🌸",
        "leaf": "🍃",
        "fruit": "🍎",
        "vegetable": "🥬",
        "happy": "😊",
        "sad": "😢",
        "angry": "😡",
        "excited": "🤩",
        "surprised": "😮",
        "thinking": "🤔",
        "love": "😍",
        "cool": "😎",
        "peace": "😌",
        "cry": "😭",
        "laugh": "😂",
        "wink": "😉",
        "kiss": "😘",
        "nerd": "🤓",
        "sleep": "😴",
        "pray": "🙏",
        "rock": "🤘",
        "clap": "👏",
        "thumbs_up": "👍",
        "thumbs_down": "👎",
        "up": "⬆️",
        "down": "⬇️",
        "left": "⬅️",
        "right": "➡️",
        "plus": "➕",
        "minus": "➖",
        "multiply": "✖️",
        "divide": "➗",
        "check": "✔️",
        "cross": "✖️",
        "warning": "⚠️",
        "stop": "🛑",
        "play": "▶️",
        "pause": "⏸️",
        "next": "⏭️",
        "prev": "⏮️",
        "back": "🔙",
        "forward": "🔜"
    }
    
    # ایموجی‌های ارزها
    COINS = {
        "BTC": "₿",
        "ETH": "Ξ",
        "BNB": "BNB",
        "SOL": "◎",
        "XRP": "XRP",
        "ADA": "₳",
        "DOGE": "Ð",
        "DOT": "DOT",
        "MATIC": "MATIC",
        "SHIB": "SHIB",
        "AVAX": "AVAX",
        "LINK": "LINK",
        "UNI": "UNI",
        "ATOM": "ATOM",
        "LTC": "Ł",
        "BCH": "BCH",
        "NEAR": "NEAR",
        "VET": "VET",
        "ALGO": "ALGO",
        "FTM": "FTM",
        "EOS": "EOS",
        "TRX": "TRX",
        "XLM": "XLM",
        "ICP": "ICP",
        "HBAR": "HBAR",
        "FIL": "FIL",
        "APT": "APT",
        "ARB": "ARB",
        "OP": "OP",
        "MKR": "MKR",
        "AAVE": "AAVE",
        "INJ": "INJ",
        "TON": "TON",
        "SUI": "SUI",
        "PEPE": "🐸",
        "BONK": "🐕",
        "FLOKI": "🐕‍🦺",
        "WIF": "🧢",
        "JUP": "🪐",
        "JASMY": "JASMY",
        "KAS": "⚡",
        "RNDR": "🎨",
        "THETA": "🎬",
        "FET": "🤖",
        "AGIX": "🧠",
        "OCEAN": "🌊",
        "USDT": "₮",
        "USDC": "💲",
        "DAI": "🪙",
        "BUSD": "🟡",
        "TUSD": "🔵"
    }
    
    # ایموجی‌های پرچم
    FLAGS = {
        "iran": "🇮🇷",
        "usa": "🇺🇸",
        "uk": "🇬🇧",
        "canada": "🇨🇦",
        "germany": "🇩🇪",
        "france": "🇫🇷",
        "italy": "🇮🇹",
        "spain": "🇪🇸",
        "japan": "🇯🇵",
        "china": "🇨🇳",
        "russia": "🇷🇺",
        "australia": "🇦🇺",
        "brazil": "🇧🇷",
        "india": "🇮🇳",
        "turkey": "🇹🇷",
        "uae": "🇦🇪",
        "south_korea": "🇰🇷",
        "switzerland": "🇨🇭",
        "singapore": "🇸🇬",
        "malaysia": "🇲🇾"
    }
    
    # ایموجی‌های اعداد
    NUMBERS = {
        "0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣",
        "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣",
        "8": "8️⃣", "9": "9️⃣", "10": "🔟"
    }
    
    @classmethod
    def get(cls, key: str, default: str = "❓") -> str:
        all_emojis = {**cls.BASIC, **cls.COINS, **cls.FLAGS, **cls.NUMBERS}
        return all_emojis.get(key, default)
    
    @classmethod
    def get_coin_emoji(cls, coin: str) -> str:
        return cls.COINS.get(coin.upper(), "🪙")
    
    @classmethod
    def get_signal_emoji(cls, signal_type: str) -> str:
        emojis = {
            "buy": "🟢",
            "sell": "🔴",
            "hold": "🟡",
            "strong_buy": "💚",
            "strong_sell": "❤️",
            "weak_buy": "🟩",
            "weak_sell": "🟥"
        }
        return emojis.get(signal_type, "⚪")
    
    @classmethod
    def get_price_emoji(cls, change: float) -> str:
        if change > 5:
            return "🚀"
        elif change > 2:
            return "📈"
        elif change > 0:
            return "⬆️"
        elif change == 0:
            return "➡️"
        elif change > -2:
            return "⬇️"
        elif change > -5:
            return "📉"
        else:
            return "💀"
    
    @classmethod
    def get_confidence_emoji(cls, confidence: int) -> str:
        if confidence >= 80:
            return "⭐⭐⭐"
        elif confidence >= 60:
            return "⭐⭐"
        elif confidence >= 40:
            return "⭐"
        else:
            return "💫"
    
    @classmethod
    def get_status_emoji(cls, status: str) -> str:
        emojis = {
            "active": "🟢",
            "inactive": "⚪",
            "pending": "🟡",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⛔",
            "running": "🔄",
            "stopped": "⏹️",
            "paused": "⏸️",
            "error": "🚨",
            "warning": "⚠️",
            "success": "🌟",
            "vip": "💎",
            "premium": "🏅",
            "free": "🆓",
            "online": "🟢",
            "offline": "🔴",
            "maintenance": "🟡"
        }
        return emojis.get(status.lower(), "❓")

# ==================== فرمت‌کننده‌ها ====================

class Formatter:
    """فرمت‌کننده‌های پیشرفته"""
    
    @staticmethod
    def number(value: float, decimals: int = 2) -> str:
        return f"{value:,.{decimals}f}"
    
    @staticmethod
    def price(value: float, currency: str = "USD") -> str:
        symbols = {
            "USD": "$", "USDT": "₮", "BTC": "₿", "ETH": "Ξ",
            "BNB": "BNB", "SOL": "◎", "XRP": "XRP", "ADA": "₳",
            "DOGE": "Ð", "DOT": "DOT", "MATIC": "MATIC",
            "IRT": "تومان", "IRR": "﷼", "EUR": "€", "GBP": "£"
        }
        symbol = symbols.get(currency, currency)
        if currency in ["IRT", "IRR"]:
            return f"{Formatter.number(value, 0)} {symbol}"
        return f"{symbol}{Formatter.number(value, 2)}"
    
    @staticmethod
    def percentage(value: float, decimals: int = 2) -> str:
        sign = "+" if value > 0 else ""
        return f"{sign}{Formatter.number(value, decimals)}%"
    
    @staticmethod
    def change(value: float, decimals: int = 2) -> str:
        return Formatter.percentage(value, decimals)
    
    @staticmethod
    def volume(value: float) -> str:
        if value >= 1e12:
            return f"{value/1e12:.2f}T"
        elif value >= 1e9:
            return f"{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{value/1e6:.2f}M"
        elif value >= 1e3:
            return f"{value/1e3:.2f}K"
        else:
            return f"{value:.2f}"
    
    @staticmethod
    def duration(seconds: int) -> str:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    @staticmethod
    def compact_number(value: float) -> str:
        if value >= 1e12:
            return f"{value/1e12:.2f}T"
        elif value >= 1e9:
            return f"{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{value/1e6:.2f}M"
        elif value >= 1e3:
            return f"{value/1e3:.2f}K"
        else:
            return str(value)
    
    @staticmethod
    def plural(count: int, singular: str, plural: str = None) -> str:
        if plural is None:
            plural = singular + "s"
        return singular if count == 1 else plural

# ==================== ابزارهای هش ====================

class HashUtils:
    """ابزارهای هش و رمزنگاری"""
    
    @staticmethod
    def sha256(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def sha512(text: str) -> str:
        return hashlib.sha512(text.encode()).hexdigest()
    
    @staticmethod
    def md5(text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def base64_encode(text: str) -> str:
        return base64.b64encode(text.encode()).decode()
    
    @staticmethod
    def base64_decode(text: str) -> str:
        return base64.b64decode(text.encode()).decode()
    
    @staticmethod
    def generate_api_key() -> str:
        return base64.b64encode(os.urandom(32)).decode().replace('+', '').replace('/', '').replace('=', '')[:32]
    
    @staticmethod
    def generate_secret_key() -> str:
        return base64.b64encode(os.urandom(48)).decode().replace('+', '').replace('/', '').replace('=', '')[:48]
    
    @staticmethod
    def generate_referral_code(length: int = 8) -> str:
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        return ''.join(random.choice(string.digits) for _ in range(length))
    
    @staticmethod
    def generate_password(length: int = 16) -> str:
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_trade_id() -> str:
        timestamp = int(datetime.now().timestamp())
        random_part = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f"T{timestamp}{random_part}"
    
    @staticmethod
    def generate_payment_id() -> str:
        timestamp = int(datetime.now().timestamp())
        random_part = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f"P{timestamp}{random_part}"

# ==================== اعتبارسنجی ====================

class Validator:
    """اعتبارسنجی‌های پیشرفته"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        pattern = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/]?'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        pattern = r'^[a-zA-Z0-9_]{3,30}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def is_valid_coin_symbol(symbol: str) -> bool:
        pattern = r'^[A-Z]{2,10}$'
        return bool(re.match(pattern, symbol))
    
    @staticmethod
    def is_valid_amount(amount: float) -> bool:
        return amount > 0 and amount < 1e12
    
    @staticmethod
    def is_valid_price(price: float) -> bool:
        return price > 0 and price < 1e12
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        text = re.sub(r'[<>/\\]', '', text)
        return text[:1000]

# ==================== تبدیل‌ها ====================

class Converter:
    """تبدیل‌کننده‌های پیشرفته"""
    
    @staticmethod
    def to_decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except:
            return Decimal('0')
    
    @staticmethod
    def to_int(value: Any) -> int:
        try:
            return int(value)
        except:
            return 0
    
    @staticmethod
    def to_float(value: Any) -> float:
        try:
            return float(value)
        except:
            return 0.0
    
    @staticmethod
    def to_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        return bool(value)
    
    @staticmethod
    def to_json(obj: Any) -> str:
        try:
            return json.dumps(obj, default=str)
        except:
            return '{}'
    
    @staticmethod
    def from_json(json_str: str) -> Any:
        try:
            return json.loads(json_str)
        except:
            return {}
    
    @staticmethod
    def to_percentage(value: float, total: float) -> float:
        if total == 0:
            return 0.0
        return (value / total) * 100
    
    @staticmethod
    def to_risk_reward(entry: float, stop_loss: float, target: float) -> float:
        risk = abs(entry - stop_loss)
        reward = abs(target - entry)
        if risk == 0:
            return 0.0
        return reward / risk

# ==================== استخراج داده ====================

class DataExtractor:
    """استخراج داده از متون"""
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        pattern = r'[-+]?\d*\.?\d+'
        return [float(x) for x in re.findall(pattern, text)]
    
    @staticmethod
    def extract_coins(text: str) -> List[str]:
        coins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT',
                'MATIC', 'SHIB', 'AVAX', 'LINK', 'UNI', 'ATOM', 'LTC', 'BCH',
                'NEAR', 'VET', 'ALGO', 'FTM', 'EOS', 'TRX', 'XLM', 'ICP']
        found = []
        text_upper = text.upper()
        for coin in coins:
            if coin in text_upper:
                found.append(coin)
        return found
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        pattern = r'https?://[^\s]+'
        return re.findall(pattern, text)

# ==================== کش ساده ====================

class CacheManager:
    """مدیریت کش ساده"""
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self._cache = {}
        self._max_size = max_size
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if (datetime.now() - timestamp).seconds < self._ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        if len(self._cache) >= self._max_size:
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]
        self._cache[key] = (value, datetime.now())
    
    def clear(self):
        self._cache.clear()
    
    def remove(self, key: str):
        if key in self._cache:
            del self._cache[key]

# ==================== Export ====================

tehran_time = TehranTime()
emoji_manager = EmojiManager()
formatter = Formatter()
hash_utils = HashUtils()
validator = Validator()
converter = Converter()
data_extractor = DataExtractor()
cache_manager = CacheManager()

def get_time() -> TehranTime:
    return tehran_time

def get_emoji() -> EmojiManager:
    return emoji_manager

def get_formatter() -> Formatter:
    return formatter

def get_hash() -> HashUtils:
    return hash_utils

def get_validator() -> Validator:
    return validator

def get_converter() -> Converter:
    return converter

def get_cache() -> CacheManager:
    return cache_manager

def get_data_extractor() -> DataExtractor:
    return data_extractor
