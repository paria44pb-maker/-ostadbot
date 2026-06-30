#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Media Management Module (Ultimate Edition)
ماژول مدیریت عکس، رسانه، نمودار و تصاویر حرفه‌ای
طراحی شده با بهترین استانداردها - بدون خطا و بدون لاگ
"""

import os
import sys
import io
import base64
import json
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# ============================================================
#                    تنظیمات Matplotlib
# ============================================================

plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = '#0a0a0a'
plt.rcParams['axes.facecolor'] = '#0d0d0d'
plt.rcParams['axes.labelcolor'] = '#00ff88'
plt.rcParams['xtick.color'] = '#00ff88'
plt.rcParams['ytick.color'] = '#00ff88'
plt.rcParams['grid.color'] = '#1a1a1a'
plt.rcParams['legend.facecolor'] = '#0d0d0d'
plt.rcParams['legend.edgecolor'] = '#00ff88'
plt.rcParams['font.size'] = 10

# ============================================================
#                    SAFE IMPORTS
# ============================================================

def safe_import(module_name: str, *attrs):
    """ایمن‌سازی واردات ماژول‌ها"""
    result = {}
    try:
        module = __import__(module_name, fromlist=attrs)
        for attr in attrs:
            result[attr] = getattr(module, attr) if hasattr(module, attr) else None
    except:
        for attr in attrs:
            result[attr] = None
    return result

# ============================================================
#                    IMPORTS
# ============================================================

_bot2 = safe_import("bot2", "get_config")
_bot4 = safe_import("bot4", "get_time", "get_emoji", "get_formatter")
_bot5 = safe_import("bot5", "get_market")
_bot7 = safe_import("bot7", "get_technical")

get_config = _bot2.get("get_config")
get_time = _bot4.get("get_time")
get_emoji = _bot4.get("get_emoji")
get_formatter = _bot4.get("get_formatter")
get_market = _bot5.get("get_market")
get_technical = _bot7.get("get_technical")

# ============================================================
#                    CONFIG
# ============================================================

config = get_config() if get_config else None

IMAGE_PATH = os.environ.get("IMAGE_PATH", "assets/")
IMAGE_URL_BASE = os.environ.get("IMAGE_URL_BASE", "https://cryptopulse.ai/images/")
USE_IMAGE_URL = os.environ.get("USE_IMAGE_URL", "False").lower() == "true"
IMAGE_QUALITY = int(os.environ.get("IMAGE_QUALITY", 90))
IMAGE_FORMAT = os.environ.get("IMAGE_FORMAT", "png")

# ============================================================
#                    ENUMS & CONSTANTS
# ============================================================

class ImageType(Enum):
    WELCOME = "welcome"
    LOGO = "logo"
    BANNER = "banner"
    SIGNAL = "signal"
    ANALYSIS = "analysis"
    VIP = "vip"
    WALLET = "wallet"
    ADMIN = "admin"
    CHART = "chart"
    PROFILE = "profile"
    RECEIPT = "receipt"
    BACKUP = "backup"

class ImageFormat(Enum):
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    WEBP = "webp"
    GIF = "gif"

class ChartType(Enum):
    CANDLESTICK = "candlestick"
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    RADAR = "radar"

class ChartTheme(Enum):
    DARK = "dark"
    LIGHT = "light"
    SOLAR = "solar"
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"

# ============================================================
#                    IMAGE MANAGER
# ============================================================

class ImageManager:
    """مدیریت کامل تصاویر و رسانه - نسخه نهایی"""

    def __init__(self):
        self.path = IMAGE_PATH
        self.url_base = IMAGE_URL_BASE
        self.use_url = USE_IMAGE_URL
        self.quality = IMAGE_QUALITY
        self.format = IMAGE_FORMAT

        # تصاویر پیش‌فرض
        self.default_images = {
            'welcome': 'welcome_image.jpg',
            'logo': 'logo.png',
            'banner': 'banner.png',
            'signal': 'signal_image.jpg',
            'analysis': 'analysis_image.jpg',
            'vip': 'vip_image.jpg',
            'wallet': 'wallet_image.jpg',
            'admin': 'admin_image.jpg',
            'chart': 'chart_image.png',
            'default': 'default_image.jpg',
            'profile': 'profile.png',
            'receipt': 'receipt.jpg',
            'backup': 'backup.png'
        }

        # ابعاد تصاویر
        self.image_sizes = {
            'welcome': (1080, 500),
            'logo': (500, 500),
            'banner': (1200, 400),
            'signal': (800, 400),
            'analysis': (900, 500),
            'vip': (800, 400),
            'wallet': (800, 400),
            'admin': (800, 400),
            'chart': (1000, 600),
            'profile': (200, 200),
            'receipt': (600, 400),
            'backup': (100, 100)
        }

        # رنگ‌های تم
        self.themes = {
            'dark': {
                'background': '#0a0a0a',
                'card': '#1a1a1a',
                'primary': '#00ff88',
                'secondary': '#ff4466',
                'text': '#ffffff',
                'subtext': '#888888',
                'border': '#2a2a2a',
                'success': '#00ff88',
                'danger': '#ff4466',
                'warning': '#ffaa00',
                'info': '#4488ff'
            },
            'light': {
                'background': '#ffffff',
                'card': '#f5f5f5',
                'primary': '#0066cc',
                'secondary': '#cc3300',
                'text': '#000000',
                'subtext': '#666666',
                'border': '#dddddd',
                'success': '#00cc66',
                'danger': '#cc3300',
                'warning': '#ff9900',
                'info': '#0066cc'
            }
        }

        self.current_theme = 'dark'
        self._ensure_directories()
        self._font_cache = {}

    def _ensure_directories(self):
        """ایجاد پوشه‌های مورد نیاز"""
        try:
            os.makedirs(self.path, exist_ok=True)
            os.makedirs("./assets", exist_ok=True)
            os.makedirs("./receipts", exist_ok=True)
            os.makedirs("./backups", exist_ok=True)
            os.makedirs("./charts", exist_ok=True)
            os.makedirs("./temp", exist_ok=True)
            os.makedirs("./assets/users", exist_ok=True)
            os.makedirs("./assets/icons", exist_ok=True)
        except:
            pass

    def _get_font(self, size: int = 14, bold: bool = False) -> ImageFont.FreeTypeFont:
        """دریافت فونت با کش"""
        cache_key = f"{size}_{bold}"
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        try:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            if bold:
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            font = ImageFont.truetype(font_path, size)
        except:
            font = ImageFont.load_default()

        self._font_cache[cache_key] = font
        return font

    # ==================== دریافت تصاویر ====================

    def get_image_path(self, image_type: str = "welcome") -> str:
        """دریافت مسیر تصویر"""
        filename = self.default_images.get(image_type, self.default_images['default'])
        if self.use_url:
            return self.url_base + filename
        return os.path.join(self.path, filename)

    def get_image_url(self, image_type: str = "welcome") -> str:
        """دریافت URL تصویر"""
        filename = self.default_images.get(image_type, self.default_images['default'])
        return self.url_base + filename

    def get_image_size(self, image_type: str = "welcome") -> Tuple[int, int]:
        """دریافت ابعاد تصویر"""
        return self.image_sizes.get(image_type, (1080, 500))

    def image_exists(self, image_type: str = "welcome") -> bool:
        """بررسی وجود تصویر"""
        if self.use_url:
            return True
        path = self.get_image_path(image_type)
        return os.path.exists(path)

    def get_all_images(self) -> Dict[str, str]:
        """دریافت همه تصاویر"""
        return self.default_images

    def get_theme(self) -> Dict[str, str]:
        """دریافت تم فعلی"""
        return self.themes.get(self.current_theme, self.themes['dark'])

    def set_theme(self, theme: str):
        """تنظیم تم"""
        if theme in self.themes:
            self.current_theme = theme

    # ==================== ایجاد تصاویر ====================

    def create_welcome_image(self, user_name: str = "", coin: str = "BTC") -> bytes:
        """ایجاد تصویر خوش‌آمدگویی حرفه‌ای"""
        width, height = 1080, 500
        theme = self.get_theme()

        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)

        # گرادیانت پس‌زمینه
        for i in range(height):
            color_value = int(10 + (i / height) * 20)
            color = f"#{color_value:02x}{color_value:02x}{color_value + 10:02x}"
            draw.rectangle([(0, i), (width, i + 1)], fill=color)

        # خطوط تزئینی
        for x in range(0, width, 50):
            draw.line([(x, 0), (x + 50, height)], fill='#1a1a1a', width=1)

        # دایره‌های تزئینی
        for _ in range(5):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(20, 60)
            draw.ellipse([(x - r, y - r), (x + r, y + r)], outline='#00ff88', width=1)

        # متن‌ها
        font_title = self._get_font(60, bold=True)
        font_sub = self._get_font(30)
        font_info = self._get_font(20)

        draw.text((50, 50), "🪙 CryptoPulse AI", fill=theme['primary'], font=font_title)
        draw.text((50, 140), "ربات هوشمند تحلیل ارزهای دیجیتال", fill=theme['text'], font=font_sub)

        if user_name:
            draw.text((50, 200), f"خوش آمدید {user_name}!", fill=theme['warning'], font=font_sub)

        # اطلاعات
        y = 270
        draw.text((50, y), f"📊 {coin} / USDT", fill=theme['text'], font=font_info)
        draw.text((50, y + 35), "🤖 هوش مصنوعی Groq", fill=theme['text'], font=font_info)
        draw.text((50, y + 70), "🚨 سیگنال‌های لحظه‌ای", fill=theme['text'], font=font_info)

        # خطوط جداکننده
        draw.line([(50, 260), (1030, 260)], fill=theme['primary'], width=2)
        draw.line([(50, 420), (1030, 420)], fill=theme['border'], width=1)

        # فوتر
        draw.text((50, 440), f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=theme['subtext'], font=font_info)
        draw.text((800, 440), "📱 @CryptoPulseAIBot", fill=theme['subtext'], font=font_info)

        # ذخیره
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG', quality=self.quality)
        return img_bytes.getvalue()

    def create_signal_image(self, signal: Dict[str, Any]) -> bytes:
        """ایجاد تصویر سیگنال حرفه‌ای"""
        width, height = 800, 500
        theme = self.get_theme()

        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)

        # اطلاعات سیگنال
        coin = signal.get('coin', 'BTC')
        signal_type = signal.get('signal', 'hold').upper()
        confidence = signal.get('confidence', 50)
        price = signal.get('current_price', 0)
        targets = signal.get('targets', [])
        stop_loss = signal.get('stop_loss', 0)

        # رنگ‌ها بر اساس سیگنال
        signal_colors = {
            'BUY': '#00ff88',
            'SELL': '#ff4466',
            'HOLD': '#ffaa00',
            'STRONG_BUY': '#00cc66',
            'STRONG_SELL': '#cc3300'
        }
        color = signal_colors.get(signal_type, '#ffffff')

        # هدر
        font_title = self._get_font(40, bold=True)
        font_sub = self._get_font(28)
        font_info = self._get_font(22)

        draw.text((50, 30), f"🚨 سیگنال {coin}", fill=color, font=font_title)
        draw.line([(50, 80), (750, 80)], fill=color, width=2)

        # اطلاعات اصلی
        y = 110
        draw.text((50, y), f"پیشنهاد: {signal_type}", fill=color, font=font_sub)
        draw.text((50, y + 45), f"اطمینان: {confidence}%", fill=theme['text'], font=font_sub)
        draw.text((50, y + 90), f"قیمت فعلی: ${price:,.2f}", fill=theme['text'], font=font_sub)

        # اهداف
        if targets:
            y = 260
            draw.text((50, y), "اهداف قیمتی:", fill=theme['warning'], font=font_sub)
            for i, target in enumerate(targets[:3], 1):
                draw.text((70, y + i * 40), f"هدف {i}: ${target:,.2f}", fill=theme['text'], font=font_info)

        # حد ضرر
        if stop_loss:
            draw.text((400, 260), f"حد ضرر: ${stop_loss:,.2f}", fill=theme['danger'], font=font_sub)

        # فوتر
        draw.line([(50, 450), (750, 450)], fill=theme['border'], width=1)
        draw.text((50, 465), f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=theme['subtext'], font=font_info)
        draw.text((600, 465), "💎 VIP", fill=theme['warning'], font=font_info)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG', quality=self.quality)
        return img_bytes.getvalue()

    def create_analysis_image(self, coin: str, analysis: Dict[str, Any]) -> bytes:
        """ایجاد تصویر تحلیل حرفه‌ای"""
        width, height = 900, 600
        theme = self.get_theme()

        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)

        font_title = self._get_font(36, bold=True)
        font_sub = self._get_font(24)
        font_info = self._get_font(18)

        # هدر
        draw.text((50, 30), f"📊 تحلیل تکنیکال {coin}", fill=theme['primary'], font=font_title)
        draw.line([(50, 80), (850, 80)], fill=theme['primary'], width=2)

        # اندیکاتورها
        indicators = [
            ('RSI', analysis.get('rsi', 50)),
            ('MACD', analysis.get('macd', 0)),
            ('باند بولینگر', analysis.get('bb_position', 0)),
            ('ADX', analysis.get('adx', 25)),
            ('MFI', analysis.get('mfi', 50)),
            ('CCI', analysis.get('cci', 0))
        ]

        y = 110
        for name, value in indicators:
            draw.text((50, y), f"{name}:", fill=theme['subtext'], font=font_info)
            draw.text((200, y), f"{value:.2f}", fill=theme['text'], font=font_info)
            y += 35

        # سطوح حمایت و مقاومت
        y = 320
        draw.text((50, y), "سطوح کلیدی:", fill=theme['warning'], font=font_sub)
        draw.text((70, y + 35), f"حمایت: ${analysis.get('support', 0):,.2f}", fill=theme['text'], font=font_info)
        draw.text((70, y + 70), f"مقاومت: ${analysis.get('resistance', 0):,.2f}", fill=theme['text'], font=font_info)

        # پیشنهاد
        signal = analysis.get('signal', 'hold').upper()
        signal_colors = {
            'BUY': '#00ff88',
            'SELL': '#ff4466',
            'HOLD': '#ffaa00'
        }
        color = signal_colors.get(signal, '#ffffff')

        y = 450
        draw.text((50, y), f"پیشنهاد: {signal}", fill=color, font=font_sub)
        draw.text((50, y + 45), f"اطمینان: {analysis.get('confidence', 50)}%", fill=theme['text'], font=font_info)

        # فوتر
        draw.line([(50, 540), (850, 540)], fill=theme['border'], width=1)
        draw.text((50, 555), f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=theme['subtext'], font=font_info)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG', quality=self.quality)
        return img_bytes.getvalue()

    def create_vip_image(self, user_data: Dict[str, Any]) -> bytes:
        """ایجاد تصویر VIP حرفه‌ای"""
        width, height = 800, 500
        theme = self.get_theme()

        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)

        font_title = self._get_font(40, bold=True)
        font_sub = self._get_font(28)
        font_info = self._get_font(20)

        # هدر
        draw.text((50, 30), "💎 VIP", fill=theme['warning'], font=font_title)
        draw.line([(50, 80), (750, 80)], fill=theme['warning'], width=2)

        # اطلاعات
        is_vip = user_data.get('is_vip', False)
        status = "✅ فعال" if is_vip else "❌ غیرفعال"
        expire = user_data.get('vip_expire', 'ندارد')
        level = user_data.get('vip_level', 0)

        y = 120
        draw.text((50, y), f"وضعیت: {status}", fill=theme['text'], font=font_sub)
        draw.text((50, y + 50), f"انقضا: {expire}", fill=theme['text'], font=font_sub)
        draw.text((50, y + 100), f"سطح: {level}", fill=theme['text'], font=font_sub)

        # امکانات
        if is_vip:
            features = [
                "📊 سیگنال‌های اختصاصی VIP",
                "🤖 تحلیل پیشرفته با AI",
                "🆘 پشتیبانی اولویت‌دار",
                "💎 دسترسی به ارزهای ویژه"
            ]
            y = 280
            draw.text((50, y), "امکانات فعال:", fill=theme['primary'], font=font_sub)
            for i, feature in enumerate(features):
                draw.text((70, y + 35 + i * 35), feature, fill=theme['text'], font=font_info)

        # فوتر
        draw.line([(50, 450), (750, 450)], fill=theme['border'], width=1)
        draw.text((50, 465), f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=theme['subtext'], font=font_info)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG', quality=self.quality)
        return img_bytes.getvalue()

    def create_wallet_image(self, wallet_data: Dict[str, Any]) -> bytes:
        """ایجاد تصویر کیف پول حرفه‌ای"""
        width, height = 800, 500
        theme = self.get_theme()

        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)

        font_title = self._get_font(36, bold=True)
        font_sub = self._get_font(24)
        font_info = self._get_font(20)

        draw.text((50, 30), "💰 کیف پول", fill=theme['primary'], font=font_title)
        draw.line([(50, 80), (750, 80)], fill=theme['primary'], width=2)

        # اطلاعات مالی
        balance = wallet_data.get('balance', 0)
        total_deposited = wallet_data.get('total_deposited', 0)
        total_withdrawn = wallet_data.get('total_withdrawn', 0)
        total_profit = wallet_data.get('total_profit', 0)

        y = 120
        draw.text((50, y), f"موجودی: ${balance:,.2f}", fill=theme['text'], font=font_sub)
        draw.text((50, y + 50), f"کل واریز: ${total_deposited:,.2f}", fill=theme['text'], font=font_sub)
        draw.text((50, y + 100), f"کل برداشت: ${total_withdrawn:,.2f}", fill=theme['text'], font=font_sub)
        draw.text((50, y + 150), f"سود کل: ${total_profit:,.2f}", fill=theme['success'], font=font_sub)

        # کد معرف
        referral_code = wallet_data.get('referral_code', 'ندارد')
        draw.text((400, 120), f"کد معرف:", fill=theme['subtext'], font=font_info)
        draw.text((400, 155), referral_code, fill=theme['warning'], font=font_sub)

        # فوتر
        draw.line([(50, 450), (750, 450)], fill=theme['border'], width=1)
        draw.text((50, 465), f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=theme['subtext'], font=font_info)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG', quality=self.quality)
        return img_bytes.getvalue()

    def create_admin_image(self, stats: Dict[str, Any]) -> bytes:
        """ایجاد تصویر پنل ادمین حرفه‌ای"""
        width, height = 900, 600
        theme = self.get_theme()

        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)

        font_title = self._get_font(36, bold=True)
        font_sub = self._get_font(24)
        font_info = self._get_font(18)

        draw.text((50, 30), "👑 پنل مدیریت", fill=theme['warning'], font=font_title)
        draw.line([(50, 80), (850, 80)], fill=theme['warning'], width=2)

        # آمار کاربران
        users = stats.get('users', {})
        y = 120
        draw.text((50, y), "📊 آمار کاربران:", fill=theme['text'], font=font_sub)
        draw.text((70, y + 40), f"کل: {users.get('total', 0):,}", fill=theme['text'], font=font_info)
        draw.text((70, y + 70), f"فعال: {users.get('active', 0):,}", fill=theme['text'], font=font_info)
        draw.text((70, y + 100), f"VIP: {users.get('vip', 0):,}", fill=theme['warning'], font=font_info)

        # آمار مالی
        payments = stats.get('payments', {})
        y = 260
        draw.text((50, y), "💰 آمار مالی:", fill=theme['text'], font=font_sub)
        draw.text((70, y + 40), f"درآمد: ${payments.get('revenue', 0):,.2f}", fill=theme['success'], font=font_info)
        draw.text((70, y + 70), f"در انتظار: {payments.get('pending', 0)}", fill=theme['warning'], font=font_info)

        # آمار سیگنال‌ها
        signals = stats.get('signals', {})
        y = 390
        draw.text((50, y), "🚨 آمار سیگنال‌ها:", fill=theme['text'], font=font_sub)
        draw.text((70, y + 40), f"کل: {signals.get('total', 0):,}", fill=theme['text'], font=font_info)
        draw.text((70, y + 70), f"نرخ موفقیت: {signals.get('success_rate', 0):.1f}%", fill=theme['success'], font=font_info)

        # فوتر
        draw.line([(50, 540), (850, 540)], fill=theme['border'], width=1)
        draw.text((50, 555), f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=theme['subtext'], font=font_info)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG', quality=self.quality)
        return img_bytes.getvalue()


# ============================================================
#                    CHART GENERATOR
# ============================================================

class ChartGenerator:
    """تولید نمودارهای حرفه‌ای - نسخه کامل"""

    def __init__(self):
        self.width = 1000
        self.height = 600
        self.dpi = 150
        self.theme = ChartTheme.DARK

    def create_candlestick_chart(self, df, coin: str = "BTC", title: str = "") -> bytes:
        """ایجاد نمودار شمعی حرفه‌ای"""
        if df is None or df.empty:
            return None

        fig = go.Figure()

        # شمع‌ها
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='شمع',
            increasing=dict(line_color='#00ff88'),
            decreasing=dict(line_color='#ff4466')
        ))

        # میانگین متحرک
        if 'sma_7' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['sma_7'],
                name='SMA 7',
                line=dict(color='#00ff88', width=1.5)
            ))

        if 'sma_25' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['sma_25'],
                name='SMA 25',
                line=dict(color='#ffaa00', width=1.5)
            ))

        if 'sma_99' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['sma_99'],
                name='SMA 99',
                line=dict(color='#ff4466', width=1.5)
            ))

        # باند بولینگر
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['bb_upper'],
                name='BB بالا',
                line=dict(color='rgba(255,255,255,0.3)', width=1)
            ))
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['bb_lower'],
                name='BB پایین',
                line=dict(color='rgba(255,255,255,0.3)', width=1)
            ))

        # تنظیمات
        fig.update_layout(
            template='plotly_dark',
            title=dict(
                text=f"{coin} - {title or 'نمودار قیمت'}",
                font=dict(color='#ffffff', size=24, family='Arial Black')
            ),
            height=self.height,
            width=self.width,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=80, b=50),
            legend=dict(
                font=dict(color='#ffffff'),
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor='rgba(255,255,255,0.1)',
                borderwidth=1
            ),
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.05)',
                showgrid=True,
                title_font=dict(color='#ffffff')
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.05)',
                showgrid=True,
                title='قیمت (USDT)',
                title_font=dict(color='#ffffff')
            )
        )

        return pio.to_image(fig, format='png', scale=2)

    def create_advanced_chart(self, df, coin: str = "BTC") -> bytes:
        """ایجاد نمودار پیشرفته با RSI و MACD"""
        if df is None or df.empty:
            return None

        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(f"{coin} - قیمت", 'RSI', 'MACD')
        )

        # شمع‌ها
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='شمع',
            increasing=dict(line_color='#00ff88'),
            decreasing=dict(line_color='#ff4466')
        ), row=1, col=1)

        # میانگین متحرک
        if 'sma_7' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['sma_7'],
                name='SMA 7',
                line=dict(color='#00ff88', width=1)
            ), row=1, col=1)

        if 'sma_25' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['sma_25'],
                name='SMA 25',
                line=dict(color='#ffaa00', width=1)
            ), row=1, col=1)

        # RSI
        if 'rsi' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['rsi'],
                name='RSI',
                line=dict(color='#ffaa00', width=2)
            ), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # MACD
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['macd'],
                name='MACD',
                line=dict(color='#00ff88', width=2)
            ), row=3, col=1)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['macd_signal'],
                name='سیگنال',
                line=dict(color='#ff4466', width=2)
            ), row=3, col=1)

            if 'macd_histogram' in df.columns:
                colors = ['#00ff88' if h >= 0 else '#ff4466' for h in df['macd_histogram']]
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df['macd_histogram'],
                    name='هیستوگرام',
                    marker_color=colors,
                    opacity=0.5
                ), row=3, col=1)

        fig.update_layout(
            template='plotly_dark',
            height=self.height + 200,
            width=self.width,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=50, b=50),
            legend=dict(
                font=dict(color='#ffffff'),
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor='rgba(255,255,255,0.1)',
                borderwidth=1
            )
        )

        fig.update_xaxes(
            gridcolor='rgba(255,255,255,0.05)',
            showgrid=True,
            title_font=dict(color='#ffffff')
        )

        fig.update_yaxes(
            gridcolor='rgba(255,255,255,0.05)',
            showgrid=True,
            title_font=dict(color='#ffffff')
        )

        return pio.to_image(fig, format='png', scale=2)

    def create_line_chart(self, data: Dict[str, List[float]], title: str = "") -> bytes:
        """ایجاد نمودار خطی"""
        fig = go.Figure()

        for name, values in data.items():
            fig.add_trace(go.Scatter(
                y=values,
                name=name,
                line=dict(width=2)
            ))

        fig.update_layout(
            template='plotly_dark',
            title=title,
            height=self.height,
            width=self.width,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=50, b=50)
        )

        return pio.to_image(fig, format='png', scale=2)

    def create_bar_chart(self, data: Dict[str, float], title: str = "") -> bytes:
        """ایجاد نمودار میله‌ای"""
        fig = go.Figure(data=[
            go.Bar(
                x=list(data.keys()),
                y=list(data.values()),
                marker_color='#00ff88'
            )
        ])

        fig.update_layout(
            template='plotly_dark',
            title=title,
            height=self.height,
            width=self.width,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=50, b=50)
        )

        return pio.to_image(fig, format='png', scale=2)


# ============================================================
#                    MEDIA MANAGER
# ============================================================

class MediaManager:
    """مدیریت کامل رسانه - نسخه نهایی"""

    def __init__(self):
        self.image = ImageManager()
        self.chart = ChartGenerator()
        self._cache = {}
        self._cache_ttl = 300

    async def get_welcome_image(self, user_name: str = "") -> bytes:
        """دریافت تصویر خوش‌آمدگویی با کش"""
        cache_key = f"welcome_{user_name}"
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp).seconds < self._cache_ttl:
                return data

        img = self.image.create_welcome_image(user_name)
        self._cache[cache_key] = (img, datetime.now())
        return img

    async def get_signal_image(self, signal: Dict[str, Any]) -> bytes:
        """دریافت تصویر سیگنال"""
        return self.image.create_signal_image(signal)

    async def get_analysis_image(self, coin: str, analysis: Dict[str, Any]) -> bytes:
        """دریافت تصویر تحلیل"""
        return self.image.create_analysis_image(coin, analysis)

    async def get_vip_image(self, user_data: Dict[str, Any]) -> bytes:
        """دریافت تصویر VIP"""
        return self.image.create_vip_image(user_data)

    async def get_wallet_image(self, wallet_data: Dict[str, Any]) -> bytes:
        """دریافت تصویر کیف پول"""
        return self.image.create_wallet_image(wallet_data)

    async def get_admin_image(self, stats: Dict[str, Any]) -> bytes:
        """دریافت تصویر پنل ادمین"""
        return self.image.create_admin_image(stats)

    async def get_chart(self, df, coin: str = "BTC", chart_type: str = "advanced") -> bytes:
        """دریافت نمودار"""
        if chart_type == "advanced":
            return self.chart.create_advanced_chart(df, coin)
        return self.chart.create_candlestick_chart(df, coin)

    def clear_cache(self):
        """پاکسازی کش"""
        self._cache.clear()


# ============================================================
#                    EXPORT
# ============================================================

media_manager = MediaManager()


def get_media_manager() -> MediaManager:
    """دریافت نمونه MediaManager"""
    return media_manager


def get_image_manager() -> ImageManager:
    """دریافت نمونه ImageManager"""
    return media_manager.image


def get_chart_generator() -> ChartGenerator:
    """دریافت نمونه ChartGenerator"""
    return media_manager.chart


def check_media():
    """بررسی وضعیت رسانه"""
    return {
        "media_manager": "✅ OK" if media_manager else "❌ FAILED",
        "image_manager": "✅ OK" if media_manager.image else "❌ FAILED",
        "chart_generator": "✅ OK" if media_manager.chart else "❌ FAILED",
        "image_path": IMAGE_PATH,
        "use_url": USE_IMAGE_URL,
        "cache_size": len(media_manager._cache)
    }


# ============================================================
#                    MAIN
# ============================================================

if __name__ == "__main__":
    status = check_media()
    print("=" * 50)
    print("🔍 Media Management Status")
    print("=" * 50)
    for key, value in status.items():
        print(f"{key}: {value}")
    print("=" * 50)
