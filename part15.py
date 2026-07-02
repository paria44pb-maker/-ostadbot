#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Media Management Module (Ultimate Edition)
ماژول مدیریت عکس، رسانه، نمودار و تصاویر حرفه‌ای
طراحی شده با بهترین استانداردها - نسخه ارتقاء یافته
"""

import os
import sys
import io
import base64
import json
import hashlib
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# تنظیم لاگر
logger = logging.getLogger(__name__)

# ============================================================
# SAFE IMPORTS - مدیریت ایمن واردات ماژول‌ها
# ============================================================

def safe_import_module(module_name: str):
    """وارد کردن ایمن یک ماژول"""
    try:
        return __import__(module_name)
    except ImportError as e:
        logger.warning(f"Could not import {module_name}: {e}")
        return None

def safe_import_attr(module_name: str, *attrs):
    """ایمن‌سازی واردات ماژول‌ها با دریافت ویژگی‌های خاص"""
    result = {}
    try:
        module = __import__(module_name, fromlist=list(attrs))
        for attr in attrs:
            try:
                result[attr] = getattr(module, attr)
            except AttributeError:
                logger.warning(f"Attribute {attr} not found in {module_name}")
                result[attr] = None
    except ImportError as e:
        logger.warning(f"Could not import {module_name}: {e}")
        for attr in attrs:
            result[attr] = None
    return result

# وارد کردن کتابخانه‌های ضروری
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    logger.error("PIL/Pillow is not installed")
    PIL_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # استفاده از بک‌اند غیرتعاملی
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    logger.error("Matplotlib is not installed")
    MATPLOTLIB_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    logger.error("NumPy is not installed")
    NUMPY_AVAILABLE = False

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    logger.error("Plotly is not installed")
    PLOTLY_AVAILABLE = False

# ============================================================
# تنظیمات Matplotlib
# ============================================================

if MATPLOTLIB_AVAILABLE:
    try:
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
    except Exception as e:
        logger.error(f"Error setting matplotlib style: {e}")

# ============================================================
# IMPORTS - واردات ماژول‌های ربات
# ============================================================

_bot2 = safe_import_attr("bot2", "get_config")
_bot4 = safe_import_attr("bot4", "get_time", "get_emoji", "get_formatter")
_bot5 = safe_import_attr("bot5", "get_market")
_bot7 = safe_import_attr("bot7", "get_technical")

get_config = _bot2.get("get_config")
get_time = _bot4.get("get_time")
get_emoji = _bot4.get("get_emoji")
get_formatter = _bot4.get("get_formatter")
get_market = _bot5.get("get_market")
get_technical = _bot7.get("get_technical")

# ============================================================
# CONFIG - تنظیمات
# ============================================================

def get_safe_config():
    """دریافت ایمن کانفیگ"""
    if get_config and callable(get_config):
        try:
            return get_config()
        except Exception as e:
            logger.error(f"Error getting config: {e}")
    return {}

config = get_safe_config()

# تنظیمات از متغیرهای محیطی با مقادیر پیش‌فرض
IMAGE_PATH = os.environ.get("IMAGE_PATH", "assets/")
IMAGE_URL_BASE = os.environ.get("IMAGE_URL_BASE", "https://cryptopulse.ai/images/")
USE_IMAGE_URL = os.environ.get("USE_IMAGE_URL", "False").lower() in ["true", "1", "yes"]
IMAGE_QUALITY = int(os.environ.get("IMAGE_QUALITY", "90"))
IMAGE_FORMAT = os.environ.get("IMAGE_FORMAT", "PNG").upper()

# ============================================================
# ENUMS & CONSTANTS
# ============================================================

class ImageType(Enum):
    """انواع تصاویر"""
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
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"

class ImageFormat(Enum):
    """فرمت‌های معتبر تصویر"""
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    WEBP = "webp"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"

    @classmethod
    def is_valid(cls, format_str: str) -> bool:
        """بررسی معتبر بودن فرمت"""
        try:
            cls(format_str.lower())
            return True
        except ValueError:
            return False

class ChartType(Enum):
    """انواع نمودار"""
    CANDLESTICK = "candlestick"
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    RADAR = "radar"
    HISTOGRAM = "histogram"
    BOX = "box"

class ChartTheme(Enum):
    """تم‌های نمودار"""
    DARK = "dark"
    LIGHT = "light"
    SOLAR = "solar"
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"

class ImageSize(Enum):
    """ابعاد استاندارد تصاویر"""
    WELCOME = (1080, 500)
    LOGO = (500, 500)
    BANNER = (1200, 400)
    SIGNAL = (800, 500)
    ANALYSIS = (900, 600)
    VIP = (800, 500)
    WALLET = (800, 500)
    ADMIN = (900, 600)
    CHART = (1000, 600)
    PROFILE = (200, 200)
    RECEIPT = (600, 400)
    BACKUP = (100, 100)
    DEFAULT = (800, 400)

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class ImageConfig:
    """تنظیمات تصویر"""
    width: int = 800
    height: int = 400
    quality: int = 90
    format: str = "PNG"
    theme: str = "dark"
    font_size_title: int = 36
    font_size_subtitle: int = 24
    font_size_text: int = 18

@dataclass
class ChartConfig:
    """تنظیمات نمودار"""
    chart_type: ChartType = ChartType.LINE
    theme: ChartTheme = ChartTheme.DARK
    width: int = 1000
    height: int = 600
    show_grid: bool = True
    interactive: bool = False

# ============================================================
# FONT MANAGER
# ============================================================

class FontManager:
    """مدیریت فونت‌ها با کش و fallback"""
    
    def __init__(self):
        self._font_cache = {}
        self._find_system_fonts()
    
    def _find_system_fonts(self):
        """پیدا کردن فونت‌های سیستمی"""
        self.font_paths = [
            # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            # Windows
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ]
    
    def get_font(self, size: int = 14, bold: bool = False) -> ImageFont.FreeTypeFont:
        """دریافت فونت با کش و fallback"""
        cache_key = f"{size}_{bold}"
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # تلاش برای بارگذاری فونت
        font = self._load_font(size, bold)
        
        self._font_cache[cache_key] = font
        return font
    
    def _load_font(self, size: int, bold: bool) -> ImageFont.FreeTypeFont:
        """بارگذاری فونت با اولویت‌بندی"""
        # اولویت با فونت‌های DejaVu
        try:
            if bold:
                for path in self.font_paths:
                    if 'Bold' in path or 'bold' in path:
                        if os.path.exists(path):
                            return ImageFont.truetype(path, size)
            else:
                for path in self.font_paths:
                    if 'Regular' in path or 'DejaVuSans.ttf' in path:
                        if os.path.exists(path):
                            return ImageFont.truetype(path, size)
        except Exception:
            pass
        
        # Fallback به فونت پیش‌فرض
        try:
            return ImageFont.load_default()
        except Exception:
            # آخرین راه‌حل
            return ImageFont.ImageFont()

# ============================================================
# IMAGE MANAGER - نسخه ارتقاء یافته
# ============================================================

class ImageManager:
    """مدیریت کامل تصاویر و رسانه - نسخه نهایی ارتقاء یافته"""

    def __init__(self):
        self.path = IMAGE_PATH
        self.url_base = IMAGE_URL_BASE
        self.use_url = USE_IMAGE_URL
        self.quality = IMAGE_QUALITY
        
        # اعتبارسنجی فرمت
        if ImageFormat.is_valid(IMAGE_FORMAT):
            self.format = IMAGE_FORMAT.lower()
        else:
            logger.warning(f"Invalid image format: {IMAGE_FORMAT}, using PNG")
            self.format = "png"
        
        # راه‌اندازی مدیریت فونت
        self.font_manager = FontManager()
        
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
            'backup': 'backup.png',
            'error': 'error.png',
            'success': 'success.png',
            'warning': 'warning.png',
            'info': 'info.png'
        }
        
        # ابعاد تصاویر
        self.image_sizes = {
            'welcome': (1080, 500),
            'logo': (500, 500),
            'banner': (1200, 400),
            'signal': (800, 500),
            'analysis': (900, 600),
            'vip': (800, 500),
            'wallet': (800, 500),
            'admin': (900, 600),
            'chart': (1000, 600),
            'profile': (200, 200),
            'receipt': (600, 400),
            'backup': (100, 100),
            'default': (800, 400),
            'error': (800, 400),
            'success': (800, 400),
            'warning': (800, 400),
            'info': (800, 400)
        }
        
        # تم‌های رنگی
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
                'info': '#4488ff',
                'accent': '#9944ff'
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
                'info': '#0066cc',
                'accent': '#6633cc'
            },
            'cyber': {
                'background': '#0a0014',
                'card': '#15002e',
                'primary': '#00ffff',
                'secondary': '#ff00ff',
                'text': '#ffffff',
                'subtext': '#8a8aff',
                'border': '#2a0a4a',
                'success': '#00ffcc',
                'danger': '#ff0044',
                'warning': '#ffcc00',
                'info': '#4488ff',
                'accent': '#8844ff'
            }
        }
        
        self.current_theme = 'dark'
        self._ensure_directories()
        self._load_custom_fonts()
    
    def _ensure_directories(self):
        """ایجاد پوشه‌های مورد نیاز"""
        directories = [
            self.path,
            "./assets",
            "./assets/users",
            "./assets/icons",
            "./assets/temp",
            "./receipts",
            "./backups",
            "./charts",
            "./temp",
            "./logs"
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {e}")
    
    def _load_custom_fonts(self):
        """بارگذاری فونت‌های سفارشی"""
        self.custom_fonts = {}
        custom_font_dir = "./assets/fonts"
        
        if os.path.exists(custom_font_dir):
            for font_file in os.listdir(custom_font_dir):
                if font_file.endswith(('.ttf', '.otf')):
                    font_name = os.path.splitext(font_file)[0]
                    font_path = os.path.join(custom_font_dir, font_file)
                    self.custom_fonts[font_name] = font_path
    
    def _get_font(self, size: int = 14, bold: bool = False, font_name: str = None) -> ImageFont.FreeTypeFont:
        """دریافت فونت (با کش و مدیریت سفارشی)"""
        if font_name and font_name in self.custom_fonts:
            cache_key = f"custom_{font_name}_{size}_{bold}"
            if hasattr(self, '_custom_font_cache') and cache_key in self._custom_font_cache:
                return self._custom_font_cache[cache_key]
            
            try:
                font = ImageFont.truetype(self.custom_fonts[font_name], size)
                if not hasattr(self, '_custom_font_cache'):
                    self._custom_font_cache = {}
                self._custom_font_cache[cache_key] = font
                return font
            except Exception:
                pass
        
        return self.font_manager.get_font(size, bold)
    
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
        return self.image_sizes.get(image_type, self.image_sizes['default'])
    
    def image_exists(self, image_type: str = "welcome") -> bool:
        """بررسی وجود تصویر"""
        if self.use_url:
            return True
        
        path = self.get_image_path(image_type)
        return os.path.exists(path)
    
    def get_all_images(self) -> Dict[str, str]:
        """دریافت همه تصاویر"""
        return self.default_images.copy()
    
    def get_theme(self) -> Dict[str, str]:
        """دریافت تم فعلی"""
        return self.themes.get(self.current_theme, self.themes['dark']).copy()
    
    def set_theme(self, theme: str):
        """تنظیم تم"""
        if theme in self.themes:
            self.current_theme = theme
            logger.info(f"Theme changed to: {theme}")
        else:
            logger.warning(f"Theme '{theme}' not found, using current theme")
    
    def add_theme(self, name: str, colors: Dict[str, str]):
        """افزودن تم جدید"""
        self.themes[name] = colors
        logger.info(f"New theme added: {name}")
    
    # ==================== ابزارهای ترسیم ====================
    
    def _create_gradient_background(self, draw: ImageDraw.ImageDraw, 
                                   width: int, height: int, 
                                   color1: str, color2: str):
        """ایجاد پس‌زمینه گرادیانت"""
        for i in range(height):
            ratio = i / height
            r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
            g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
            b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            draw.rectangle([(0, i), (width, i + 1)], fill=color)
    
    def _draw_decorative_elements(self, draw: ImageDraw.ImageDraw, 
                                 width: int, height: int, theme: dict):
        """ترسیم عناصر تزئینی"""
        # خطوط مورب
        for x in range(0, width, 80):
            draw.line([(x, 0), (x + 100, height)], fill=theme['border'], width=1)
        
        # نقاط تزئینی
        for _ in range(10):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(2, 5)
            draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=theme['primary'])
    
    def _draw_header(self, draw: ImageDraw.ImageDraw, title: str, 
                    theme: dict, y_offset: int = 20):
        """ترسیم هدر استاندارد"""
        font_title = self._get_font(36, bold=True)
        draw.text((50, y_offset), title, fill=theme['primary'], font=font_title)
        draw.line([(50, y_offset + 60), (750, y_offset + 60)], fill=theme['primary'], width=2)
    
    def _draw_footer(self, draw: ImageDraw.ImageDraw, width: int, height: int, 
                    theme: dict, additional_text: str = ""):
        """ترسیم فوتر استاندارد"""
        font_info = self._get_font(16)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        draw.line([(50, height - 50), (width - 50, height - 50)], fill=theme['border'], width=1)
        draw.text((50, height - 35), f"⏰ {timestamp}", fill=theme['subtext'], font=font_info)
        
        if additional_text:
            draw.text((width - 250, height - 35), additional_text, fill=theme['subtext'], font=font_info)
        else:
            draw.text((width - 250, height - 35), "📱 @CryptoPulseAIBot", fill=theme['subtext'], font=font_info)
    
    def _add_watermark(self, img: Image.Image, text: str = "CryptoPulse AI"):
        """افزودن واترمارک به تصویر"""
        try:
            watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            font = self._get_font(20)
            text_width, text_height = draw.textsize(text, font=font)
            
            x = img.size[0] - text_width - 10
            y = img.size[1] - text_height - 10
            
            draw.text((x, y), text, fill=(255, 255, 255, 50), font=font)
            
            return Image.alpha_composite(img.convert('RGBA'), watermark)
        except Exception:
            return img
    
    # ==================== ایجاد تصاویر ====================
    
    def create_welcome_image(self, user_name: str = "", coin: str = "BTC") -> bytes:
        """ایجاد تصویر خوش‌آمدگویی حرفه‌ای"""
        width, height = self.get_image_size('welcome')
        theme = self.get_theme()
        
        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)
        
        # پس‌زمینه گرادیانت
        self._create_gradient_background(draw, width, height, '#0a0a12', '#1a1a2e')
        
        # عناصر تزئینی
        self._draw_decorative_elements(draw, width, height, theme)
        
        # متن‌ها
        font_title = self._get_font(60, bold=True)
        font_sub = self._get_font(30)
        font_info = self._get_font(20)
        
        # عنوان اصلی
        draw.text((50, 50), "🪙 CryptoPulse AI", fill=theme['primary'], font=font_title)
        draw.text((50, 140), "ربات هوشمند تحلیل ارزهای دیجیتال", fill=theme['text'], font=font_sub)
        
        if user_name:
            draw.text((50, 200), f"خوش آمدید {user_name}!", fill=theme['warning'], font=font_sub)
        
        # اطلاعات
        y = 270
        info_items = [
            f"📊 تحلیل {coin} / USDT",
            "🤖 هوش مصنوعی پیشرفته",
            "🚨 سیگنال‌های لحظه‌ای",
            "💎 تحلیل VIP اختصاصی",
            "📈 نمودارهای حرفه‌ای"
        ]
        
        for item in info_items:
            draw.text((50, y), item, fill=theme['text'], font=font_info)
            y += 35
        
        # خطوط جداکننده
        draw.line([(50, 260), (width - 50, 260)], fill=theme['primary'], width=2)
        draw.line([(50, height - 80), (width - 50, height - 80)], fill=theme['border'], width=1)
        
        # فوتر
        self._draw_footer(draw, width, height, theme)
        
        # واترمارک
        img = self._add_watermark(img)
        
        # ذخیره
        return self._image_to_bytes(img)
    
    def create_signal_image(self, signal: Dict[str, Any]) -> bytes:
        """ایجاد تصویر سیگنال حرفه‌ای"""
        width, height = self.get_image_size('signal')
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
            'BUY': theme['success'],
            'SELL': theme['danger'],
            'HOLD': theme['warning'],
            'STRONG_BUY': '#00cc66',
            'STRONG_SELL': '#cc3300'
        }
        color = signal_colors.get(signal_type, theme['text'])
        
        # هدر
        self._draw_header(draw, f"🚨 سیگنال {coin}", theme)
        
        # مستطیل رنگی پس‌زمینه
        draw.rectangle([(30, 90), (width - 30, 160)], fill=color, outline=color)
        
        # اطلاعات اصلی
        font_sub = self._get_font(28)
        font_info = self._get_font(22)
        
        y = 180
        draw.text((50, y), f"پیشنهاد: {signal_type}", fill=color, font=font_sub)
        draw.text((50, y + 45), f"اطمینان: {confidence}%", fill=theme['text'], font=font_sub)
        draw.text((50, y + 90), f"قیمت فعلی: ${price:,.2f}", fill=theme['text'], font=font_sub)
        
        # اهداف
        if targets:
            y = 340
            draw.text((50, y), "🎯 اهداف قیمتی:", fill=theme['warning'], font=font_sub)
            for i, target in enumerate(targets[:5], 1):
                color_idx = theme['success'] if i <= 3 else theme['warning']
                draw.text((70, y + i * 35), f"هدف {i}: ${target:,.2f}", fill=color_idx, font=font_info)
        
        # حد ضرر
        if stop_loss:
            draw.rectangle([(400, 260), (width - 50, 320)], outline=theme['danger'], width=2)
            draw.text((420, 275), f"حد ضرر: ${stop_loss:,.2f}", fill=theme['danger'], font=font_sub)
        
        # فوتر
        self._draw_footer(draw, width, height, theme, "💎 VIP Signal")
        
        img = self._add_watermark(img)
        return self._image_to_bytes(img)
    
    def create_analysis_image(self, coin: str, analysis: Dict[str, Any]) -> bytes:
        """ایجاد تصویر تحلیل حرفه‌ای"""
        width, height = self.get_image_size('analysis')
        theme = self.get_theme()
        
        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)
        
        # هدر
        self._draw_header(draw, f"📊 تحلیل تکنیکال {coin}", theme)
        
        font_info = self._get_font(18)
        font_sub = self._get_font(24)
        
        # اندیکاتورها
        indicators = [
            ('RSI', analysis.get('rsi', 50), 'info'),
            ('MACD', analysis.get('macd', 0), 'accent'),
            ('باند بولینگر', analysis.get('bb_position', 0), 'primary'),
            ('ADX', analysis.get('adx', 25), 'warning'),
            ('MFI', analysis.get('mfi', 50), 'success'),
            ('CCI', analysis.get('cci', 0), 'danger'),
            ('ATR', analysis.get('atr', 0), 'accent'),
            ('Stochastic', analysis.get('stochastic', 50), 'info')
        ]
        
        y = 110
        for name, value, color_key in indicators:
            color = theme.get(color_key, theme['text'])
            draw.text((50, y), f"{name}:", fill=theme['subtext'], font=font_info)
            
            # نمایش گرافیکی مقدار
            bar_width = min(abs(value) * 2, 300)
            if value < 0:
                draw.rectangle([(200, y + 5), (200 + bar_width, y + 25)], fill=theme['danger'])
            else:
                draw.rectangle([(200, y + 5), (200 + bar_width, y + 25)], fill=theme['success'])
            
            draw.text((510, y), f"{value:.2f}", fill=color, font=font_info)
            y += 40
        
        # سطوح حمایت و مقاومت
        y = 430
        draw.text((50, y), "📈 سطوح کلیدی:", fill=theme['warning'], font=font_sub)
        draw.text((70, y + 40), f"حمایت: ${analysis.get('support', 0):,.2f}", fill=theme['success'], font=font_info)
        draw.text((70, y + 70), f"مقاومت: ${analysis.get('resistance', 0):,.2f}", fill=theme['danger'], font=font_info)
        
        # پیشنهاد
        signal = analysis.get('signal', 'hold').upper()
        signal_colors = {
            'BUY': theme['success'],
            'SELL': theme['danger'],
            'HOLD': theme['warning']
        }
        color = signal_colors.get(signal, theme['text'])
        
        draw.text((400, y), f"پیشنهاد: {signal}", fill=color, font=font_sub)
        draw.text((400, y + 40), f"اطمینان: {analysis.get('confidence', 50)}%", fill=theme['text'], font=font_info)
        
        # فوتر
        self._draw_footer(draw, width, height, theme)
        
        img = self._add_watermark(img)
        return self._image_to_bytes(img)
    
    def create_vip_image(self, user_data: Dict[str, Any]) -> bytes:
        """ایجاد تصویر VIP حرفه‌ای"""
        width, height = self.get_image_size('vip')
        theme = self.get_theme()
        
        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)
        
        # پس‌زمینه ویژه VIP
        self._create_gradient_background(draw, width, height, '#1a0a00', '#2a1a0a')
        
        # الماس‌های تزئینی
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.text((x, y), "💎", fill=theme['warning'], font=self._get_font(random.randint(10, 30)))
        
        # هدر
        font_title = self._get_font(48, bold=True)
        draw.text((50, 30), "💎 VIP MEMBER", fill=theme['warning'], font=font_title)
        draw.line([(50, 90), (width - 50, 90)], fill=theme['warning'], width=3)
        
        # اطلاعات
        is_vip = user_data.get('is_vip', False)
        status = "✅ فعال" if is_vip else "❌ غیرفعال"
        expire = user_data.get('vip_expire', 'ندارد')
        level = user_data.get('vip_level', 0)
        
        font_sub = self._get_font(28)
        font_info = self._get_font(22)
        
        y = 130
        draw.text((50, y), f"وضعیت: {status}", fill=theme['text'], font=font_sub)
        draw.text((50, y + 50), f"تاریخ انقضا: {expire}", fill=theme['text'], font=font_sub)
        draw.text((50, y + 100), f"سطح: {level}", fill=theme['warning'], font=font_sub)
        
        # امکانات
        if is_vip:
            features = [
                ("📊", "سیگنال‌های VIP اختصاصی"),
                ("🤖", "تحلیل پیشرفته با هوش مصنوعی"),
                ("🆘", "پشتیبانی 24/7 اولویت‌دار"),
                ("💎", "دسترسی به ارزهای ویژه"),
                ("🎯", "دقت سیگنال بالای 90%"),
                ("💰", "کیف پول اختصاصی با سود بیشتر"),
                ("📈", "نمودارهای پیشرفته و اختصاصی"),
                ("🔔", "نوتیفیکیشن‌های لحظه‌ای")
            ]
            
            y = 310
            draw.text((50, y), "امکانات ویژه:", fill=theme['primary'], font=font_sub)
            
            for i, (emoji, feature) in enumerate(features):
                if i < 4:
                    x = 70
                    y_pos = y + 40 + i * 35
                else:
                    x = 400
                    y_pos = y + 40 + (i - 4) * 35
                
                draw.text((x, y_pos), f"{emoji} {feature}", fill=theme['text'], font=font_info)
        
        # فوتر
        self._draw_footer(draw, width, height, theme, "💎 VIP Account")
        
        return self._image_to_bytes(img)
    
    def create_wallet_image(self, wallet_data: Dict[str, Any]) -> bytes:
        """ایجاد تصویر کیف پول حرفه‌ای"""
        width, height = self.get_image_size('wallet')
        theme = self.get_theme()
        
        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)
        
        self._draw_header(draw, "💰 کیف پول", theme)
        
        font_sub = self._get_font(28)
        font_info = self._get_font(20)
        
        # اطلاعات مالی
        balance = wallet_data.get('balance', 0)
        total_deposited = wallet_data.get('total_deposited', 0)
        total_withdrawn = wallet_data.get('total_withdrawn', 0)
        total_profit = wallet_data.get('total_profit', 0)
        pending = wallet_data.get('pending', 0)
        
        y = 130
        financial_info = [
            ("موجودی:", f"${balance:,.2f}", theme['primary']),
            ("کل واریز:", f"${total_deposited:,.2f}", theme['text']),
            ("کل برداشت:", f"${total_withdrawn:,.2f}", theme['text']),
            ("سود کل:", f"${total_profit:,.2f}", theme['success']),
            ("در انتظار:", f"${pending:,.2f}", theme['warning'])
        ]
        
        for label, value, color in financial_info:
            draw.text((50, y), label, fill=theme['subtext'], font=font_sub)
            draw.text((250, y), value, fill=color, font=font_sub)
            y += 50
        
        # کد معرف
        referral_code = wallet_data.get('referral_code', 'ندارد')
        draw.text((450, 130), "کد معرف:", fill=theme['subtext'], font=font_info)
        draw.rectangle([(450, 165), (650, 200)], outline=theme['warning'], width=2)
        draw.text((460, 172), referral_code, fill=theme['warning'], font=font_sub)
        
        # وضعیت کیف پول
        wallet_status = wallet_data.get('status', 'active')
        status_colors = {
            'active': theme['success'],
            'frozen': theme['warning'],
            'blocked': theme['danger']
        }
        status_color = status_colors.get(wallet_status, theme['text'])
        
        draw.text((450, 250), f"وضعیت: {wallet_status.upper()}", fill=status_color, font=font_sub)
        
        # نمودار سود (ساده)
        profit_data = wallet_data.get('profit_history', [])
        if profit_data and len(profit_data) > 1:
            chart_y = 350
            max_val = max(profit_data)
            min_val = min(profit_data)
            
            if max_val > min_val:
                for i in range(len(profit_data) - 1):
                    x1 = 50 + i * 50
                    y1 = chart_y - ((profit_data[i] - min_val) / (max_val - min_val)) * 100
                    x2 = 50 + (i + 1) * 50
                    y2 = chart_y - ((profit_data[i + 1] - min_val) / (max_val - min_val)) * 100
                    draw.line([(x1, y1), (x2, y2)], fill=theme['primary'], width=2)
        
        # فوتر
        self._draw_footer(draw, width, height, theme)
        
        return self._image_to_bytes(img)
    
    def create_admin_image(self, stats: Dict[str, Any]) -> bytes:
        """ایجاد تصویر پنل ادمین حرفه‌ای (تکمیل شده)"""
        width, height = self.get_image_size('admin')
        theme = self.get_theme()
        
        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)
        
        # پس‌زمینه ویژه ادمین
        self._create_gradient_background(draw, width, height, '#0a0014', '#150028')
        
        # هدر
        font_title = self._get_font(42, bold=True)
        draw.text((50, 30), "🔐 Admin Panel", fill=theme['danger'], font=font_title)
        draw.line([(50, 85), (width - 50, 85)], fill=theme['danger'], width=2)
        
        font_sub = self._get_font(24)
        font_info = self._get_font(18)
        
        # آمار کلی
        y = 110
        total_users = stats.get('total_users', 0)
        total_vip = stats.get('total_vip', 0)
        total_signals = stats.get('total_signals', 0)
        total_transactions = stats.get('total_transactions', 0)
        total_volume = stats.get('total_volume', 0)
        
        stats_items = [
            ("👥 کاربران:", total_users),
            ("💎 VIP:", total_vip),
            ("📊 سیگنال‌ها:", total_signals),
            ("💳 تراکنش‌ها:", total_transactions),
            ("💰 حجم معاملات:", f"${total_volume:,.2f}")
        ]
        
        for label, value in stats_items:
            draw.text((50, y), label, fill=theme['subtext'], font=font_sub)
            draw.text((300, y), str(value), fill=theme['text'], font=font_sub)
            y += 45
        
        # وضعیت سیستم
        y = 350
        draw.text((50, y), "System Status:", fill=theme['primary'], font=font_sub)
        
        system_status = stats.get('system_status', {})
        cpu = system_status.get('cpu', 0)
        memory = system_status.get('memory', 0)
        disk = system_status.get('disk', 0)
        
        # نمایش گرافیکی وضعیت
        for i, (label, value, color_key) in enumerate([
            ("CPU", cpu, 'success' if cpu < 70 else 'warning' if cpu < 90 else 'danger'),
            ("Memory", memory, 'success' if memory < 70 else 'warning' if memory < 90 else 'danger'),
            ("Disk", disk, 'success' if disk < 70 else 'warning' if disk < 90 else 'danger')
        ]):
            y_pos = y + 35 + i * 40
            color = theme.get(color_key, theme['text'])
            draw.text((70, y_pos), f"{label}:", fill=theme['subtext'], font=font_info)
            draw.rectangle([(170, y_pos + 5), (470, y_pos + 25)], outline=theme['border'], width=1)
            bar_width = int((value / 100) * 300)
            draw.rectangle([(170, y_pos + 5), (170 + bar_width, y_pos + 25)], fill=color)
            draw.text((480, y_pos), f"{value}%", fill=color, font=font_info)
        
        # لاگ‌های اخیر
        y = 490
        draw.text((50, y), "Recent Logs:", fill=theme['warning'], font=font_sub)
        
        recent_logs = stats.get('recent_logs', [])
        for i, log in enumerate(recent_logs[:3]):
            log_color = theme['danger'] if 'error' in log.lower() else theme['text']
            draw.text((70, y + 30 + i * 25), f"• {log[:60]}...", fill=log_color, font=font_info)
        
        # فوتر
        draw.line([(50, height - 40), (width - 50, height - 40)], fill=theme['border'], width=1)
        draw.text((50, height - 30), f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=theme['subtext'], font=font_info)
        draw.text((width - 250, height - 30), "🔐 Admin Access", fill=theme['danger'], font=font_info)
        
        return self._image_to_bytes(img)
    
    def create_chart_image(self, chart_data: Dict[str, Any], chart_config: ChartConfig = None) -> bytes:
        """ایجاد تصویر نمودار حرفه‌ای"""
        if chart_config is None:
            chart_config = ChartConfig()
        
        if not MATPLOTLIB_AVAILABLE and not PLOTLY_AVAILABLE:
            return self._create_error_image("Chart libraries not available")
        
        try:
            if chart_config.interactive and PLOTLY_AVAILABLE:
                return self._create_plotly_chart(chart_data, chart_config)
            else:
                return self._create_matplotlib_chart(chart_data, chart_config)
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            return self._create_error_image(f"Chart creation failed: {e}")
    
    def _create_matplotlib_chart(self, chart_data: Dict[str, Any], chart_config: ChartConfig) -> bytes:
        """ایجاد نمودار با Matplotlib"""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib is not available")
        
        data = chart_data.get('data', [])
        labels = chart_data.get('labels', [])
        title = chart_data.get('title', 'Chart')
        
        fig, ax = plt.subplots(figsize=(chart_config.width/100, chart_config.height/100))
        
        if chart_config.chart_type == ChartType.LINE:
            ax.plot(labels, data, color='#00ff88', linewidth=2)
        elif chart_config.chart_type == ChartType.BAR:
            ax.bar(labels, data, color='#00ff88')
        elif chart_config.chart_type == ChartType.SCATTER:
            ax.scatter(labels, data, color='#00ff88', s=50)
        elif chart_config.chart_type == ChartType.AREA:
            ax.fill_between(range(len(data)), data, color='#00ff88', alpha=0.3)
            ax.plot(labels, data, color='#00ff88', linewidth=2)
        
        ax.set_title(title, color='#00ff88', fontsize=14, pad=20)
        ax.grid(chart_config.show_grid, alpha=0.3)
        ax.tick_params(colors='#00ff88')
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, facecolor='#0a0a0a', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        return buf.getvalue()
    
    def _create_plotly_chart(self, chart_data: Dict[str, Any], chart_config: ChartConfig) -> bytes:
        """ایجاد نمودار با Plotly"""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly is not available")
        
        data = chart_data.get('data', [])
        labels = chart_data.get('labels', [])
        title = chart_data.get('title', 'Chart')
        
        fig = go.Figure()
        
        if chart_config.chart_type == ChartType.LINE:
            fig.add_trace(go.Scatter(x=labels, y=data, mode='lines+markers', 
                                   line=dict(color='#00ff88', width=2)))
        elif chart_config.chart_type == ChartType.CANDLESTICK:
            fig.add_trace(go.Candlestick(x=labels,
                                       open=chart_data.get('open', []),
                                       high=chart_data.get('high', []),
                                       low=chart_data.get('low', []),
                                       close=data))
        
        fig.update_layout(
            title=title,
            template='plotly_dark',
            width=chart_config.width,
            height=chart_config.height
        )
        
        img_bytes = pio.to_image(fig, format='png')
        return img_bytes
    
    def create_error_image(self, error_message: str = "An error occurred") -> bytes:
        """ایجاد تصویر خطا"""
        width, height = self.get_image_size('error')
        theme = self.get_theme()
        
        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)
        
        draw.rectangle([(0, 0), (width, height)], outline=theme['danger'], width=3)
        
        font_title = self._get_font(36, bold=True)
        font_sub = self._get_font(24)
        
        draw.text((50, 50), "❌ Error", fill=theme['danger'], font=font_title)
        draw.line([(50, 100), (width - 50, 100)], fill=theme['danger'], width=2)
        
        draw.text((50, 130), error_message, fill=theme['text'], font=font_sub)
        
        draw.text((50, 200), "Please try again or contact support", fill=theme['subtext'], font=font_sub)
        
        self._draw_footer(draw, width, height, theme)
        
        return self._image_to_bytes(img)
    
    def _create_error_image(self, error_message: str) -> bytes:
        """متد داخلی برای ایجاد تصویر خطا"""
        return self.create_error_image(error_message)
    
    def create_success_image(self, message: str = "Operation successful") -> bytes:
        """ایجاد تصویر موفقیت"""
        width, height = self.get_image_size('success')
        theme = self.get_theme()
        
        img = Image.new('RGB', (width, height), color=theme['background'])
        draw = ImageDraw.Draw(img)
        
        draw.rectangle([(0, 0), (width, height)], outline=theme['success'], width=3)
        
        font_title = self._get_font(36, bold=True)
        font_sub = self._get_font(24)
        
        draw.text((50, 50), "✅ Success", fill=theme['success'], font=font_title)
        draw.line([(50, 100), (width - 50, 100)], fill=theme['success'], width=2)
        
        draw.text((50, 130), message, fill=theme['text'], font=font_sub)
        
        self._draw_footer(draw, width, height, theme)
        
        return self._image_to_bytes(img)
    
    # ==================== ابزارهای کمکی ====================
    
    def _image_to_bytes(self, img: Image.Image, format: str = None) -> bytes:
        """تبدیل تصویر PIL به bytes"""
        if format is None:
            format = self.format
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format, quality=self.quality)
        return img_bytes.getvalue()
    
    def resize_image(self, img_bytes: bytes, width: int, height: int) -> bytes:
        """تغییر اندازه تصویر"""
        try:
            img = Image.open(io.BytesIO(img_bytes))
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            return self._image_to_bytes(img)
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return img_bytes
    
    def optimize_image(self, img_bytes: bytes, max_size: int = 1024 * 1024) -> bytes:
        """بهینه‌سازی حجم تصویر"""
        try:
            quality = self.quality
            
            while True:
                img_bytes_optimized = io.BytesIO()
                img = Image.open(io.BytesIO(img_bytes))
                img.save(img_bytes_optimized, format=self.format, quality=quality, optimize=True)
                
                if len(img_bytes_optimized.getvalue()) <= max_size or quality <= 10:
                    return img_bytes_optimized.getvalue()
                
                quality -= 10
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return img_bytes
    
    def add_text_overlay(self, img_bytes: bytes, text: str, position: Tuple[int, int] = (10, 10),
                        color: str = '#ffffff', size: int = 20) -> bytes:
        """افزودن متن روی تصویر"""
        try:
            img = Image.open(io.BytesIO(img_bytes))
            draw = ImageDraw.Draw(img)
            font = self._get_font(size)
            
            draw.text(position, text, fill=color, font=font)
            
            return self._image_to_bytes(img)
        except Exception as e:
            logger.error(f"Error adding text overlay: {e}")
            return img_bytes
    
    def create_collage(self, images: List[bytes], cols: int = 2) -> bytes:
        """ایجاد کلاژ از چند تصویر"""
        try:
            pil_images = [Image.open(io.BytesIO(img)) for img in images]
            
            # تعیین ابعاد کلاژ
            max_width = max(img.width for img in pil_images)
            max_height = max(img.height for img in pil_images)
            
            rows = (len(pil_images) + cols - 1) // cols
            collage_width = max_width * cols
            collage_height = max_height * rows
            
            collage = Image.new('RGB', (collage_width, collage_height), '#000000')
            
            for i, img in enumerate(pil_images):
                row = i // cols
                col = i % cols
                x = col * max_width
                y = row * max_height
                
                # تغییر اندازه تصاویر
                img_resized = img.resize((max_width, max_height), Image.Resampling.LANCZOS)
                collage.paste(img_resized, (x, y))
            
            return self._image_to_bytes(collage)
        except Exception as e:
            logger.error(f"Error creating collage: {e}")
            return self.create_error_image("Failed to create collage")
    
    def get_image_info(self, img_bytes: bytes) -> Dict[str, Any]:
        """دریافت اطلاعات تصویر"""
        try:
            img = Image.open(io.BytesIO(img_bytes))
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': len(img_bytes)
            }
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            return {}
    
    def clear_cache(self):
        """پاکسازی کش فونت‌ها و تصاویر"""
        self.font_manager = FontManager()
        if hasattr(self, '_custom_font_cache'):
            del self._custom_font_cache
        logger.info("Cache cleared")

# ============================================================
# SINGLETON INSTANCE
# ============================================================

# ایجاد نمونه سراسری
image_manager = ImageManager()

# ============================================================
# UTILITY FUNCTIONS - توابع کمکی
# ============================================================

def get_image(image_type: str = "welcome", **kwargs) -> bytes:
    """
    دریافت تصویر با نوع مشخص
    
    Args:
        image_type: نوع تصویر (welcome, signal, analysis, ...)
        **kwargs: پارامترهای اضافی برای هر نوع تصویر
    
    Returns:
        bytes: تصویر به صورت باینری
    """
    try:
        if image_type == ImageType.WELCOME.value:
            return image_manager.create_welcome_image(
                user_name=kwargs.get('user_name', ''),
                coin=kwargs.get('coin', 'BTC')
            )
        elif image_type == ImageType.SIGNAL.value:
            return image_manager.create_signal_image(kwargs.get('signal', {}))
        elif image_type == ImageType.ANALYSIS.value:
            return image_manager.create_analysis_image(
                kwargs.get('coin', 'BTC'),
                kwargs.get('analysis', {})
            )
        elif image_type == ImageType.VIP.value:
            return image_manager.create_vip_image(kwargs.get('user_data', {}))
        elif image_type == ImageType.WALLET.value:
            return image_manager.create_wallet_image(kwargs.get('wallet_data', {}))
        elif image_type == ImageType.ADMIN.value:
            return image_manager.create_admin_image(kwargs.get('stats', {}))
        elif image_type == ImageType.CHART.value:
            chart_config = kwargs.get('chart_config')
            return image_manager.create_chart_image(kwargs.get('chart_data', {}), chart_config)
        elif image_type == 'error':
            return image_manager.create_error_image(kwargs.get('message', 'Error'))
        elif image_type == 'success':
            return image_manager.create_success_image(kwargs.get('message', 'Success'))
        else:
            # بازگشت تصویر پیش‌فرض
            return image_manager.get_image_path(image_type)
    except Exception as e:
        logger.error(f"Error in get_image: {e}")
        return image_manager.create_error_image(f"Failed to create {image_type} image")

def create_qr_code(data: str, size: int = 200) -> bytes:
    """ایجاد QR Code"""
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#00ff88", back_color="#0a0a0a")
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    except ImportError:
        logger.warning("qrcode library not installed")
        return image_manager.create_error_image("QR Code library not available")
    except Exception as e:
        logger.error(f"Error creating QR code: {e}")
        return image_manager.create_error_image("Failed to create QR code")

def create_progress_bar(value: int, max_value: int = 100, width: int = 300, height: int = 30) -> bytes:
    """ایجاد نوار پیشرفت"""
    try:
        theme = image_manager.get_theme()
        
        img = Image.new('RGB', (width, height), theme['background'])
        draw = ImageDraw.Draw(img)
        
        # پس‌زمینه
        draw.rectangle([(0, 0), (width, height)], outline=theme['border'], width=1)
        
        # نوار پیشرفت
        progress_width = int((value / max_value) * (width - 2))
        if progress_width > 0:
            draw.rectangle([(1, 1), (progress_width, height - 1)], fill=theme['primary'])
        
        # متن درصد
        font = image_manager._get_font(14)
        text = f"{value}%"
        text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (50, 14)
        
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        draw.text((text_x, text_y), text, fill=theme['text'], font=font)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    except Exception as e:
        logger.error(f"Error creating progress bar: {e}")
        return image_manager.create_error_image("Failed to create progress bar")

# ============================================================
# MAIN - برای تست
# ============================================================

def main():
    """تابع اصلی برای تست ماژول"""
    print("=" * 60)
    print("  CryptoPulse AI - Image Manager Test")
    print("=" * 60)
    
    # تست ایجاد تصاویر
    test_images = [
        ("welcome", lambda: image_manager.create_welcome_image("TestUser", "ETH")),
        ("signal", lambda: image_manager.create_signal_image({
            'coin': 'BTC',
            'signal': 'strong_buy',
            'confidence': 85,
            'current_price': 45000.50,
            'targets': [46000, 47500, 50000],
            'stop_loss': 44000
        })),
        ("analysis", lambda: image_manager.create_analysis_image("SOL", {
            'rsi': 65.5,
            'macd': 2.3,
            'bb_position': 0.7,
            'adx': 30,
            'mfi': 55,
            'cci': 120,
            'support': 100,
            'resistance': 150,
            'signal': 'buy',
            'confidence': 75
        })),
        ("vip", lambda: image_manager.create_vip_image({
            'is_vip': True,
            'vip_expire': '2024-12-31',
            'vip_level': 3
        })),
        ("wallet", lambda: image_manager.create_wallet_image({
            'balance': 15000.75,
            'total_deposited': 20000,
            'total_withdrawn': 5000,
            'total_profit': 3000.25,
            'referral_code': 'VIP2024',
            'status': 'active'
        })),
        ("admin", lambda: image_manager.create_admin_image({
            'total_users': 5000,
            'total_vip': 250,
            'total_signals': 15000,
            'total_transactions': 8000,
            'total_volume': 2500000,
            'system_status': {
                'cpu': 45,
                'memory': 60,
                'disk': 35
            },
            'recent_logs': [
                "User 12345 logged in successfully",
                "Signal sent to 100 users",
                "Payment processed: $500",
                "Error: Database connection failed"
            ]
        }))
    ]
    
    for name, create_func in test_images:
        try:
            img_bytes = create_func()
            filename = f"./temp/test_{name}.png"
            
            with open(filename, 'wb') as f:
                f.write(img_bytes)
            
            print(f"✅ {name:10} - Created: {filename} ({len(img_bytes)} bytes)")
        except Exception as e:
            print(f"❌ {name:10} - Error: {e}")
    
    print("=" * 60)
    print("  Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
