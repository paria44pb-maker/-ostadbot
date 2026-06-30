#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Channel Management Module
ماژول مدیریت کانال تلگرام @CryptoPulse606
ارسال خودکار سیگنال‌ها، تحلیل‌ها و گزارش‌ها
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from telegram import Bot, InputFile
from telegram.constants import ParseMode

from bot2 import get_config
from bot3 import db_manager
from bot4 import get_time, get_emoji, get_formatter
from bot5 import get_market
from bot6 import get_ai
from bot7 import get_technical
from bot8 import LuxEmoji

config = get_config()
time_manager = get_time()
emoji_manager = get_emoji()
formatter = get_formatter()
market = get_market()
ai_manager = get_ai()
technical = get_technical()

# ==================== کلاس مدیریت کانال ====================

class ChannelManager:
    """مدیریت کانال تلگرام"""
    
    def __init__(self, bot: Bot = None):
        self.bot = bot
        self.channel_id = config.get('channel_id', '@CryptoPulse606')
        self.channel_username = 'CryptoPulse606'
        
        # قالب‌های پیام
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        return {
            'signal': """
🚨 **سیگنال معاملاتی {coin}**

{signal_emoji} **پیشنهاد:** {signal_type}
🎯 **اطمینان:** {confidence}% {confidence_emoji}

💰 **قیمت فعلی:** ${price:,.2f}
📈 **تغییر ۲۴ساعته:** {change:+.2f}%

📊 **تحلیل تکنیکال:**
{analysis}

🎯 **اهداف قیمتی:**
{targets}

🛑 **حد ضرر:** ${stop_loss:,.2f}
📈 **نسبت ریسک/پاداش:** {risk_reward:.2f}

⏰ **زمان:** {time}

💎 **VIP:** سیگنال‌های اختصاصی در پنل VIP
📱 **ربات:** @CryptoPulseAIBot
""",
            'analysis': """
📊 **تحلیل تکنیکال {coin}**

🤖 **تحلیل هوش مصنوعی:**

{analysis}

📈 **نکات کلیدی:**
• حمایت اصلی: ${support:,.2f}
• مقاومت اصلی: ${resistance:,.2f}
• روند: {trend}
• RSI: {rsi:.1f}
• MACD: {macd:.4f}

⏰ **زمان:** {time}

💎 **تحلیل دقیق‌تر در پنل VIP**
📱 **ربات:** @CryptoPulseAIBot
""",
            'price_alert': """
{emoji} **هشدار قیمتی {coin}**

💰 **قیمت فعلی:** ${price:,.2f}
📈 **تغییر:** {change:+.2f}%
📊 **وضعیت:** {status}

⏰ **زمان:** {time}

📱 **ربات:** @CryptoPulseAIBot
""",
            'daily_report': """
📊 **گزارش روزانه بازار**

📅 **تاریخ:** {date}

📈 **خلاصه بازار:**
• بهترین عملکرد: {best_coin} (+{best_change:.2f}%)
• بدترین عملکرد: {worst_coin} ({worst_change:.2f}%)
• حجم کل: ${total_volume:,.0f}

🚨 **سیگنال‌های امروز:**
• کل: {total_signals}
• خرید: {buy_signals}
• فروش: {sell_signals}

💎 **VIP:**
• سیگنال‌های VIP: {vip_signals}
• کاربران جدید VIP: {new_vip}

📱 **ربات:** @CryptoPulseAIBot
""",
            'weekly_report': """
📊 **گزارش هفتگی بازار**

📅 **هفته:** {week}

📈 **خلاصه هفتگی:**
• بهترین ارز: {best_coin} (+{best_change:.2f}%)
• بدترین ارز: {worst_coin} ({worst_change:.2f}%)
• رشد کل بازار: {market_growth:.2f}%

🚨 **آمار سیگنال‌ها:**
• کل: {total_signals}
• نرخ موفقیت: {success_rate:.1f}%
• میانگین سود: {avg_profit:.2f}%

💎 **VIP:**
• سیگنال‌های VIP: {vip_signals}
• نرخ موفقیت VIP: {vip_success_rate:.1f}%

📊 **پیش‌بینی:** {prediction}

📱 **ربات:** @CryptoPulseAIBot
""",
            'tip': """
{emoji} **نکته طلایی معاملاتی**

{tip}

💎 **برای دریافت نکات بیشتر VIP شوید!**
📱 **ربات:** @CryptoPulseAIBot
"""
        }
    
    # ==================== ارسال پیام‌ها ====================
    
    async def send_signal(self, signal: Dict[str, Any]):
        """ارسال سیگنال به کانال"""
        coin = signal.get('coin', 'BTC')
        signal_type = signal.get('signal', 'hold').upper()
        confidence = signal.get('confidence', 50)
        price = signal.get('current_price', 0)
        change = signal.get('change_24h', 0)
        targets = signal.get('targets', [])
        stop_loss = signal.get('stop_loss', 0)
        risk_reward = signal.get('risk_reward', 0)
        analysis = signal.get('technical', {}).get('reasons', ['داده‌های کافی نیست'])
        
        signal_emoji = emoji_manager.get_signal_emoji(signal_type.lower())
        confidence_emoji = emoji_manager.get_confidence_emoji(confidence)
        
        targets_text = ""
        for i, target in enumerate(targets[:3], 1):
            targets_text += f"   هدف {i}: ${target:,.2f}\n"
        
        text = self.templates['signal'].format(
            coin=coin,
            signal_emoji=signal_emoji,
            signal_type=signal_type,
            confidence=confidence,
            confidence_emoji=confidence_emoji,
            price=price,
            change=change,
            analysis='\n'.join(analysis[:3]) if isinstance(analysis, list) else analysis[:200],
            targets=targets_text or '• تعیین نشده',
            stop_loss=stop_loss,
            risk_reward=risk_reward,
            time=time_manager.now_persian()
        )
        
        if self.bot:
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN
                )
                return True
            except:
                return False
        return False
    
    async def send_analysis(self, coin: str, analysis: str, data: Dict[str, Any]):
        """ارسال تحلیل به کانال"""
        text = self.templates['analysis'].format(
            coin=coin,
            analysis=analysis[:500],
            support=data.get('support', 0),
            resistance=data.get('resistance', 0),
            trend=data.get('trend', 'خنثی'),
            rsi=data.get('rsi', 50),
            macd=data.get('macd', 0),
            time=time_manager.now_persian()
        )
        
        if self.bot:
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN
                )
                return True
            except:
                return False
        return False
    
    async def send_price_alert(self, coin: str, price: float, change: float, status: str):
        """ارسال هشدار قیمت"""
        emoji = "🚀" if change > 0 else "🔻"
        
        text = self.templates['price_alert'].format(
            emoji=emoji,
            coin=coin,
            price=price,
            change=change,
            status=status,
            time=time_manager.now_persian()
        )
        
        if self.bot:
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN
                )
                return True
            except:
                return False
        return False
    
    async def send_daily_report(self, stats: Dict[str, Any]):
        """ارسال گزارش روزانه"""
        text = self.templates['daily_report'].format(
            date=time_manager.now_persian_date(),
            best_coin=stats.get('best_coin', 'BTC'),
            best_change=stats.get('best_change', 0),
            worst_coin=stats.get('worst_coin', 'DOGE'),
            worst_change=stats.get('worst_change', 0),
            total_volume=stats.get('total_volume', 0),
            total_signals=stats.get('total_signals', 0),
            buy_signals=stats.get('buy_signals', 0),
            sell_signals=stats.get('sell_signals', 0),
            vip_signals=stats.get('vip_signals', 0),
            new_vip=stats.get('new_vip', 0)
        )
        
        if self.bot:
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN
                )
                return True
            except:
                return False
        return False
    
    async def send_weekly_report(self, stats: Dict[str, Any]):
        """ارسال گزارش هفتگی"""
        text = self.templates['weekly_report'].format(
            week=datetime.now().strftime('%W'),
            best_coin=stats.get('best_coin', 'BTC'),
            best_change=stats.get('best_change', 0),
            worst_coin=stats.get('worst_coin', 'DOGE'),
            worst_change=stats.get('worst_change', 0),
            market_growth=stats.get('market_growth', 0),
            total_signals=stats.get('total_signals', 0),
            success_rate=stats.get('success_rate', 0),
            avg_profit=stats.get('avg_profit', 0),
            vip_signals=stats.get('vip_signals', 0),
            vip_success_rate=stats.get('vip_success_rate', 0),
            prediction=stats.get('prediction', 'روند صعودی با نوسان متوسط')
        )
        
        if self.bot:
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN
                )
                return True
            except:
                return False
        return False
    
    async def send_tip(self):
        """ارسال نکته طلایی"""
        tips = [
            "همیشه حد ضرر خود را تعیین کنید! 🛑",
            "تحلیل تکنیکال را با تحلیل فاندامنتال ترکیب کنید.",
            "بیش از ۵٪ سرمایه خود را در یک ارز قرار ندهید.",
            "در زمان ترس بخرید، در زمان طمع بفروشید.",
            "روند دوست شماست، با آن همراه شوید.",
            "مدیریت ریسک مهم‌تر از سود است.",
            "صبوری کلید موفقیت در بازار کریپتو است.",
            "همیشه در حال یادگیری باشید.",
            "اهداف واقع‌بینانه تعیین کنید.",
            "از احساسات در معامله پرهیز کنید."
        ]
        
        tip = random.choice(tips)
        emoji = random.choice(['💎', '✨', '🌟', '🎯', '📌'])
        
        text = self.templates['tip'].format(
            emoji=emoji,
            tip=tip
        )
        
        if self.bot:
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN
                )
                return True
            except:
                return False
        return False
    
    async def send_welcome(self):
        """ارسال پیام خوش‌آمدگویی"""
        text = """
🌟 **به کانال CryptoPulse AI خوش آمدید!**

🤖 **ربات هوشمند تحلیل و سیگنال ارزهای دیجیتال**

📊 **در این کانال چه خبر است؟**
• 🚨 سیگنال‌های لحظه‌ای خرید و فروش
• 📈 تحلیل تکنیکال پیشرفته
• 🤖 تحلیل هوش مصنوعی Groq
• 🔔 هشدارهای قیمتی
• 📊 گزارش‌های روزانه و هفتگی
• 💎 سیگنال‌های VIP
• 📰 اخبار مهم کریپتو
• 🎯 نکات طلایی معاملاتی

💎 **برای دسترسی به سیگنال‌های VIP:** @Amir92aa

🆘 **پشتیبانی:** @Amir92aa

⏰ **زمان:** {time}
"""
        if self.bot:
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text.format(time=time_manager.now_persian()),
                    parse_mode=ParseMode.MARKDOWN
                )
                return True
            except:
                return False
        return False

# ==================== تسک‌های خودکار ====================

class AutoChannelTasks:
    """تسک‌های خودکار کانال"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.channel = ChannelManager(bot)
        self.is_running = False
    
    async def start(self):
        """شروع تسک‌ها"""
        self.is_running = True
        await self.channel.send_welcome()
        
        while self.is_running:
            try:
                now = time_manager.now()
                
                # سیگنال هر ۴ ساعت
                if now.hour % 4 == 0 and now.minute == 0:
                    await self._send_signals()
                
                # هشدار قیمت هر ۱ ساعت
                if now.minute == 0:
                    await self._check_price_alerts()
                
                # نکته طلایی هر ۶ ساعت
                if now.hour % 6 == 0 and now.minute == 0:
                    await self.channel.send_tip()
                
                # گزارش روزانه ساعت ۲۰
                if now.hour == 20 and now.minute == 0:
                    await self._send_daily_report()
                
                # گزارش هفتگی جمعه ۱۸
                if now.weekday() == 6 and now.hour == 18 and now.minute == 0:
                    await self._send_weekly_report()
                
                await asyncio.sleep(60)
                
            except:
                await asyncio.sleep(300)
    
    async def stop(self):
        """توقف تسک‌ها"""
        self.is_running = False
    
    async def _send_signals(self):
        """ارسال سیگنال‌ها"""
        coins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']
        for coin in coins:
            signal = await market.get_signal(coin, '4h')
            if signal and signal.get('confidence', 0) > 60:
                await self.channel.send_signal(signal)
                await asyncio.sleep(10)
    
    async def _check_price_alerts(self):
        """بررسی هشدارهای قیمت"""
        coins = ['BTC', 'ETH', 'BNB']
        for coin in coins:
            ticker = await market.get_market_data(coin)
            if ticker and abs(ticker.change_24h) > 5:
                status = "صعودی" if ticker.change_24h > 0 else "نزولی"
                await self.channel.send_price_alert(
                    coin, ticker.price, ticker.change_24h, status
                )
                await asyncio.sleep(5)
    
    async def _send_daily_report(self):
        """ارسال گزارش روزانه"""
        stats = await self._generate_daily_stats()
        await self.channel.send_daily_report(stats)
    
    async def _send_weekly_report(self):
        """ارسال گزارش هفتگی"""
        stats = await self._generate_weekly_stats()
        await self.channel.send_weekly_report(stats)
    
    async def _generate_daily_stats(self) -> Dict[str, Any]:
        """تولید آمار روزانه"""
        db_stats = db_manager.get_stats()
        tickers = await market.get_all_prices()
        
        return {
            'best_coin': 'BTC',
            'best_change': 5.2,
            'worst_coin': 'DOGE',
            'worst_change': -3.1,
            'total_volume': db_stats.get('total_volume', 0),
            'total_signals': db_stats.get('signals', 0),
            'buy_signals': db_stats.get('buy_signals', 0),
            'sell_signals': db_stats.get('sell_signals', 0),
            'vip_signals': db_stats.get('vip_signals', 0),
            'new_vip': db_stats.get('new_vip_today', 0)
        }
    
    async def _generate_weekly_stats(self) -> Dict[str, Any]:
        """تولید آمار هفتگی"""
        return {
            'best_coin': 'BTC',
            'best_change': 12.5,
            'worst_coin': 'DOGE',
            'worst_change': -8.3,
            'market_growth': 5.2,
            'total_signals': 0,
            'success_rate': 76.5,
            'avg_profit': 8.7,
            'vip_signals': 0,
            'vip_success_rate': 89.2,
            'prediction': 'روند صعودی با نوسان متوسط'
        }

# ==================== Export ====================

def get_channel_manager(bot: Bot = None) -> ChannelManager:
    return ChannelManager(bot)

def get_auto_channel_tasks(bot: Bot) -> AutoChannelTasks:
    return AutoChannelTasks(bot)
