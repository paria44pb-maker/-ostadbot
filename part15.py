#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Media Management Module
ماژول مدیریت عکس، رسانه و تصاویر ربات
پشتیبانی از ارسال عکس در صفحات مختلف
"""

import os
import io
import aiohttp
from typing import Optional, Dict, Any, Tuple
from telegram import InputFile, InputMediaPhoto
from telegram.constants import ParseMode
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

from bot2 import get_config, get_image_settings
from bot4 import get_time, get_emoji
from bot5 import get_market
from bot7 import get_technical

config = get_config()
image_settings = get_image_settings()
time_manager = get_time()
emoji_manager = get_emoji()
market = get_market()
technical = get_technical()

# ==================== تنظیمات تصاویر ====================

class ImageManager:
    """مدیریت تصاویر و رسانه"""
    
    def __init__(self):
        self.image_path = image_settings.image_path
        self.image_url_base = image_settings.image_url_base
        self.use_url = image_settings.use_url
        
        # اطمینان از وجود پوشه
        os.makedirs(self.image_path, exist_ok=True)
        os.makedirs("./assets", exist_ok=True)
        
        # تصاویر پیش‌فرض
        self.default_images = {
            'welcome': 'welcome_image.jpg',
            'logo': 'logo.png',
            'banner': 'banner.png',
            'signal': 'signal_image.jpg',
            'analysis': 'analysis_image.jpg',
            'vip': 'vip_image.jpg',
            'wallet': 'wallet_image.jpg',
            'admin': 'admin_image.jpg'
        }
    
    def get_image_path(self, image_type: str = "welcome") -> str:
        """دریافت مسیر تصویر"""
        if self.use_url:
            return self.image_url_base + self.default_images.get(image_type, self.default_images['welcome'])
        else:
            return os.path.join(self.image_path, self.default_images.get(image_type, self.default_images['welcome']))
    
    def get_image(self, image_type: str = "welcome") -> Optional[InputFile]:
        """دریافت تصویر به عنوان InputFile"""
        path = self.get_image_path(image_type)
        if os.path.exists(path):
            return InputFile(path)
        return None
    
    async def get_image_from_url(self, url: str) -> Optional[bytes]:
        """دریافت تصویر از URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
        except:
            pass
        return None
    
    # ==================== تولید تصاویر ====================
    
    async def create_chart(self, coin: str, df, title: str = "") -> bytes:
        """ایجاد نمودار شمعی"""
        if df is None or df.empty:
            return None
        
        # محاسبه اندیکاتورها
        df = technical.calculate_all_indicators(df)
        
        # تنظیمات نمودار
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
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_7'],
            name='SMA 7',
            line=dict(color='#00ff88', width=1.5)
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_25'],
            name='SMA 25',
            line=dict(color='#ffaa00', width=1.5)
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_99'],
            name='SMA 99',
            line=dict(color='#ff4466', width=1.5)
        ))
        
        # باند بولینگر
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
                font=dict(color='#ffffff', size=20)
            ),
            height=600,
            width=1000,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=80, b=50),
            legend=dict(
                font=dict(color='#ffffff'),
                bgcolor='rgba(0,0,0,0.5)'
            )
        )
        
        fig.update_xaxes(
            gridcolor='rgba(255,255,255,0.05)',
            showgrid=True
        )
        fig.update_yaxes(
            gridcolor='rgba(255,255,255,0.05)',
            showgrid=True,
            title='قیمت (USDT)'
        )
        
        return pio.to_image(fig, format='png', scale=2)
    
    async def create_analysis_chart(self, coin: str, df) -> bytes:
        """ایجاد نمودار تحلیل پیشرفته"""
        if df is None or df.empty:
            return None
        
        df = technical.calculate_all_indicators(df)
        
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
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_7'],
            name='SMA 7',
            line=dict(color='#00ff88', width=1)
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_25'],
            name='SMA 25',
            line=dict(color='#ffaa00', width=1)
        ), row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['rsi'],
            name='RSI',
            line=dict(color='#ffaa00', width=2)
        ), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
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
        
        # هیستوگرام MACD
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
            height=800,
            width=1000,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=50, b=50),
            legend=dict(
                font=dict(color='#ffffff'),
                bgcolor='rgba(0,0,0,0.5)'
            )
        )
        
        return pio.to_image(fig, format='png', scale=2)
    
    # ==================== ایجاد تصاویر سفارشی ====================
    
    def create_welcome_image(self, user_name: str = "") -> bytes:
        """ایجاد تصویر خوش‌آمدگویی"""
        width, height = 1080, 500
        img = Image.new('RGB', (width, height), color='#0a0a0a')
        draw = ImageDraw.Draw(img)
        
        # رنگ‌ها
        colors = {
            'primary': '#00ff88',
            'secondary': '#ffaa00',
            'text': '#ffffff',
            'subtext': '#888888'
        }
        
        # متن
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # لوگو
        draw.text((50, 50), "🪙 CryptoPulse AI", fill=colors['primary'], font=font_large)
        draw.text((50, 140), "ربات هوشمند تحلیل ارزهای دیجیتال", fill=colors['text'], font=font_medium)
        draw.text((50, 200), f"خوش آمدید {user_name or 'کاربر عزیز'}!", fill=colors['secondary'], font=font_medium)
        
        # اطلاعات
        draw.text((50, 280), "📊 تحلیل تکنیکال پیشرفته", fill=colors['text'], font=font_small)
        draw.text((50, 320), "🤖 هوش مصنوعی Groq", fill=colors['text'], font=font_small)
        draw.text((50, 360), "🚨 سیگنال‌های لحظه‌ای", fill=colors['text'], font=font_small)
        
        # خطوط تزئینی
        draw.line([(50, 250), (1030, 250)], fill=colors['primary'], width=2)
        draw.line([(50, 400), (1030, 400)], fill=colors['secondary'], width=1)
        
        # فوتر
        draw.text((50, 430), f"⏰ {time_manager.now_persian()}", fill=colors['subtext'], font=font_small)
        draw.text((800, 430), "📱 @CryptoPulseAIBot", fill=colors['subtext'], font=font_small)
        
        # تبدیل به bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def create_signal_image(self, signal: Dict[str, Any]) -> bytes:
        """ایجاد تصویر سیگنال"""
        width, height = 800, 400
        img = Image.new('RGB', (width, height), color='#0a0a0a')
        draw = ImageDraw.Draw(img)
        
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
        
        coin = signal.get('coin', 'BTC')
        signal_type = signal.get('signal', 'hold').upper()
        confidence = signal.get('confidence', 50)
        price = signal.get('current_price', 0)
        
        colors = {
            'buy': '#00ff88',
            'sell': '#ff4466',
            'hold': '#ffaa00'
        }
        color = colors.get(signal_type.lower(), '#ffffff')
        
        draw.text((50, 30), f"🚨 سیگنال {coin}", fill=color, font=font_title)
        draw.text((50, 100), f"پیشنهاد: {signal_type}", fill=color, font=font_text)
        draw.text((50, 150), f"اطمینان: {confidence}%", fill='#ffffff', font=font_text)
        draw.text((50, 200), f"قیمت فعلی: ${price:,.2f}", fill='#ffffff', font=font_text)
        draw.text((50, 250), f"⏰ {time_manager.now_persian()}", fill='#888888', font=font_text)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

# ==================== Export ====================

image_manager = ImageManager()

def get_image_manager() -> ImageManager:
    return image_manager
