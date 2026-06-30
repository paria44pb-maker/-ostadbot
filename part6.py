#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - AI & Advanced Analysis Module
ماژول هوش مصنوعی Groq با مدیریت بهینه محدودیت‌ها
تحلیل‌های پیشرفته، تولید محتوا، و پردازش هوشمند
"""

import os
import sys
import json
import asyncio
import time
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import aiohttp
from groq import AsyncGroq

# ==================== تنظیمات هوش مصنوعی ====================

class AIModel(Enum):
    """مدل‌های هوش مصنوعی Groq"""
    LLAMA_3_70B = "llama3-70b-8192"
    LLAMA_3_8B = "llama3-8b-8192"
    MIXTRAL_8X7B = "mixtral-8x7b-32768"
    GEMMA_7B = "gemma-7b-it"
    LLAMA_3_2_90B = "llama-3.2-90b-vision-preview"
    LLAMA_3_2_11B = "llama-3.2-11b-vision-preview"
    LLAMA_3_2_3B = "llama-3.2-3b-preview"

class AITaskType(Enum):
    """نوع وظیفه هوش مصنوعی"""
    SIGNAL_ANALYSIS = "signal_analysis"
    MARKET_SUMMARY = "market_summary"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    PRICE_PREDICTION = "price_prediction"
    PORTFOLIO_ADVICE = "portfolio_advice"
    EDUCATION = "education"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NEWS_SUMMARY = "news_summary"
    TRADING_STRATEGY = "trading_strategy"

@dataclass
class AIRequest:
    """درخواست هوش مصنوعی"""
    prompt: str
    task_type: AITaskType
    model: AIModel = AIModel.LLAMA_3_2_90B
    temperature: float = 0.3
    max_tokens: int = 800
    priority: int = 1
    user_id: Optional[str] = None

@dataclass
class AIResponse:
    """پاسخ هوش مصنوعی"""
    content: str
    model: str
    tokens_used: int
    processing_time: float
    task_type: AITaskType
    success: bool
    error: Optional[str] = None

# ==================== مدیریت محدودیت‌ها ====================

class RateLimitManager:
    """مدیریت محدودیت‌های نرخ و توکن"""
    
    def __init__(self):
        # محدودیت‌های Groq (رایگان)
        self.max_requests_per_minute = 30
        self.max_requests_per_day = 14400
        self.max_tokens_per_minute = 10000
        self.max_tokens_per_day = 500000
        self.max_concurrent_requests = 5
        
        # وضعیت فعلی
        self.requests_minute = deque(maxlen=self.max_requests_per_minute)
        self.tokens_minute = 0
        self.requests_day = 0
        self.tokens_day = 0
        self.concurrent_requests = 0
        self.last_reset = datetime.now()
        
        # قفل برای جلوگیری از تداخل
        self._lock = asyncio.Lock()
    
    async def check_and_wait(self, estimated_tokens: int = 500) -> bool:
        """بررسی و انتظار برای محدودیت‌ها"""
        async with self._lock:
            now = datetime.now()
            
            # ریست روزانه
            if (now - self.last_reset).days >= 1:
                self.requests_day = 0
                self.tokens_day = 0
                self.last_reset = now
            
            # بررسی محدودیت‌ها
            if len(self.requests_minute) >= self.max_requests_per_minute:
                await asyncio.sleep(1)
                return False
            
            if self.tokens_minute + estimated_tokens > self.max_tokens_per_minute:
                await asyncio.sleep(0.5)
                return False
            
            if self.requests_day >= self.max_requests_per_day:
                await asyncio.sleep(60)
                return False
            
            if self.tokens_day + estimated_tokens > self.max_tokens_per_day:
                await asyncio.sleep(60)
                return False
            
            if self.concurrent_requests >= self.max_concurrent_requests:
                await asyncio.sleep(0.5)
                return False
            
            # ثبت درخواست
            self.requests_minute.append(now)
            self.tokens_minute += estimated_tokens
            self.requests_day += 1
            self.tokens_day += estimated_tokens
            self.concurrent_requests += 1
            
            return True
    
    def release(self):
        """آزاد کردن درخواست"""
        self.concurrent_requests -= 1
        if self.concurrent_requests < 0:
            self.concurrent_requests = 0
    
    def get_status(self) -> Dict[str, Any]:
        """دریافت وضعیت محدودیت‌ها"""
        return {
            'requests_minute': len(self.requests_minute),
            'requests_minute_limit': self.max_requests_per_minute,
            'tokens_minute': self.tokens_minute,
            'tokens_minute_limit': self.max_tokens_per_minute,
            'requests_day': self.requests_day,
            'requests_day_limit': self.max_requests_per_day,
            'tokens_day': self.tokens_day,
            'tokens_day_limit': self.max_tokens_per_day,
            'concurrent_requests': self.concurrent_requests,
            'concurrent_limit': self.max_concurrent_requests
        }

# ==================== کش هوش مصنوعی ====================

class AICache:
    """کش هوشمند برای پاسخ‌های هوش مصنوعی"""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self._cache = {}
        self._max_size = max_size
        self._ttl = ttl
    
    def _get_key(self, prompt: str, model: str, temperature: float) -> str:
        """تولید کلید یکتا برای کش"""
        content = f"{prompt}_{model}_{temperature}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, temperature: float) -> Optional[str]:
        """دریافت از کش"""
        key = self._get_key(prompt, model, temperature)
        
        if key in self._cache:
            data, timestamp = self._cache[key]
            if (datetime.now() - timestamp).seconds < self._ttl:
                return data
            else:
                del self._cache[key]
        
        return None
    
    def set(self, prompt: str, model: str, temperature: float, response: str):
        """ذخیره در کش"""
        key = self._get_key(prompt, model, temperature)
        
        if len(self._cache) >= self._max_size:
            # حذف قدیمی‌ترین
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]
        
        self._cache[key] = (response, datetime.now())
    
    def clear(self):
        """پاکسازی کش"""
        self._cache.clear()
    
    def remove_expired(self):
        """حذف موارد منقضی شده"""
        now = datetime.now()
        expired = [k for k, v in self._cache.items() if (now - v[1]).seconds >= self._ttl]
        for k in expired:
            del self._cache[k]

# ==================== کلاس اصلی هوش مصنوعی ====================

class GroqAI:
    """مدیریت هوش مصنوعی Groq با بهینه‌سازی محدودیت‌ها"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        from bot2 import get_config
        config = get_config()
        
        self.api_key = config.get('groq_api_key', '')
        self.client = AsyncGroq(api_key=self.api_key)
        self.rate_limiter = RateLimitManager()
        self.cache = AICache()
        
        # مدل‌های قابل استفاده
        self.models = {
            'premium': AIModel.LLAMA_3_2_90B.value,
            'advanced': AIModel.LLAMA_3_70B.value,
            'standard': AIModel.MIXTRAL_8X7B.value,
            'basic': AIModel.LLAMA_3_8B.value,
            'fast': AIModel.GEMMA_7B.value
        }
        
        # تنظیمات پیش‌فرض
        self.default_model = self.models['standard']
        self.default_temperature = 0.3
        self.default_max_tokens = 800
        
        # پرامپت‌های آماده
        self.prompts = self._load_prompts()
        
        # آمار
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'avg_response_time': 0
        }
    
    def _load_prompts(self) -> Dict[str, str]:
        """بارگذاری پرامپت‌های آماده"""
        return {
            'signal_analysis': """
🔍 **تحلیل هوشمند سیگنال {coin}**

📊 **داده‌های تکنیکال:**
• قیمت فعلی: ${price:.2f}
• تغییر ۲۴ ساعت: {change_24h:.2f}%
• بالاترین ۲۴ ساعت: ${high_24h:.2f}
• پایین‌ترین ۲۴ ساعت: ${low_24h:.2f}
• حجم ۲۴ ساعت: ${volume_24h:,.0f}
• RSI: {rsi:.1f}
• MACD: {macd:.4f}
• باند بولینگر: {bb_position:.2f}
• ADX: {adx:.1f}
• MFI: {mfi:.1f}

📈 **اندیکاتورها:**
{indicators}

🎯 **سیگنال‌ها:**
{signals}

📝 **تحلیل پرایس اکشن:**
{price_action}

💎 **تحلیل فاندامنتال:**
{fundamental}

🤖 **پیشنهاد نهایی:** {final_signal}
🎯 **سطح اطمینان:** {confidence}%

📊 **اهداف قیمتی:**
{targets}

🛑 **حد ضرر:** ${stop_loss:.2f}

⏰ **زمان تحلیل:** {time}
""",
            'market_summary': """
🌍 **خلاصه بازار ارزهای دیجیتال**

📊 **وضعیت کلی بازار:**
{market_status}

💰 **ارزهای برتر امروز:**
{top_coins}

📉 **ارزهای در حال سقوط:**
{bottom_coins}

🔥 **ارزهای داغ:**
{hot_coins}

📈 **تحلیل کلی:**
{overall_analysis}

⏰ **زمان:** {time}
""",
            'portfolio_advice': """
💼 **مشاوره مدیریت پورتفولیو**

📊 **پورتفولیو فعلی:**
{portfolio}

🎯 **اهداف سرمایه‌گذاری:**
{goals}

⚖️ **تخصیص بهینه:**
{allocation}

📈 **پیشنهادات معاملاتی:**
{suggestions}

⚠️ **هشدارهای ریسک:**
{warnings}

💎 **نکات کلیدی:**
{key_points}

⏰ **زمان:** {time}
""",
            'education': """
📚 **آموزش معاملات ارز دیجیتال**

🎓 **موضوع:** {topic}

📖 **مقدمه:**
{introduction}

🎯 **نکات کلیدی:**
{key_points}

📊 **مثال عملی:**
{example}

⚠️ **هشدارهای مهم:**
{warnings}

💎 **نکته طلایی:**
{golden_tip}

⏰ **زمان:** {time}
""",
            'price_prediction': """
🔮 **پیش‌بینی قیمت {coin}**

📊 **داده‌های تاریخی:**
• قیمت فعلی: ${current_price:.2f}
• میانگین ۷ روزه: ${sma_7:.2f}
• میانگین ۲۵ روزه: ${sma_25:.2f}
• RSI: {rsi:.1f}
• روند: {trend}

🔮 **پیش‌بینی:**
• قیمت پیش‌بینی شده (۲۴ ساعت): ${prediction_24h:.2f}
• قیمت پیش‌بینی شده (۷ روز): ${prediction_7d:.2f}
• قیمت پیش‌بینی شده (۳۰ روز): ${prediction_30d:.2f}

📈 **سناریوها:**
{scenarios}

⚠️ **عوامل مؤثر:**
{factors}

⏰ **زمان پیش‌بینی:** {time}
"""
        }
    
    # ==================== متدهای اصلی ====================
    
    async def _call_api(
        self,
        prompt: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        task_type: AITaskType = AITaskType.SIGNAL_ANALYSIS
    ) -> AIResponse:
        """فراخوانی API هوش مصنوعی با مدیریت محدودیت‌ها"""
        
        if model is None:
            model = self.default_model
        if temperature is None:
            temperature = self.default_temperature
        if max_tokens is None:
            max_tokens = self.default_max_tokens
        
        # بررسی کش
        cached = self.cache.get(prompt, model, temperature)
        if cached:
            return AIResponse(
                content=cached,
                model=model,
                tokens_used=len(cached.split()),
                processing_time=0,
                task_type=task_type,
                success=True
            )
        
        # بررسی محدودیت‌ها
        estimated_tokens = max_tokens + len(prompt.split()) * 2
        can_proceed = await self.rate_limiter.check_and_wait(estimated_tokens)
        
        if not can_proceed:
            return AIResponse(
                content="",
                model=model,
                tokens_used=0,
                processing_time=0,
                task_type=task_type,
                success=False,
                error="Rate limit exceeded"
            )
        
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "شما یک تحلیلگر حرفه‌ای بازار ارزهای دیجیتال هستید. پاسخ‌های خود را به فارسی، زیبا، دقیق و با استفاده از ایموجی‌های مناسب ارائه دهید."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            processing_time = time.time() - start_time
            content = response.choices[0].message.content
            
            # ذخیره در کش
            self.cache.set(prompt, model, temperature, content)
            
            # بروزرسانی آمار
            self.stats['total_requests'] += 1
            self.stats['successful_requests'] += 1
            self.stats['total_tokens'] += len(content.split())
            self.stats['avg_response_time'] = (
                (self.stats['avg_response_time'] * (self.stats['successful_requests'] - 1) + processing_time)
                / self.stats['successful_requests']
            )
            
            return AIResponse(
                content=content,
                model=model,
                tokens_used=len(content.split()),
                processing_time=processing_time,
                task_type=task_type,
                success=True
            )
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            return AIResponse(
                content="",
                model=model,
                tokens_used=0,
                processing_time=0,
                task_type=task_type,
                success=False,
                error=str(e)
            )
        
        finally:
            self.rate_limiter.release()
    
    # ==================== تحلیل‌های مختلف ====================
    
    async def analyze_signal(
        self,
        coin: str,
        market_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any] = None,
        is_vip: bool = False
    ) -> str:
        """تحلیل سیگنال معاملاتی"""
        
        # انتخاب مدل بر اساس سطح کاربر
        model = self.models['premium'] if is_vip else self.models['advanced']
        max_tokens = 1200 if is_vip else 800
        
        # ساخت پرامپت
        prompt = self.prompts['signal_analysis'].format(
            coin=coin,
            price=market_data.get('price', 0),
            change_24h=market_data.get('change_24h', 0),
            high_24h=market_data.get('high_24h', 0),
            low_24h=market_data.get('low_24h', 0),
            volume_24h=market_data.get('volume_24h', 0),
            rsi=technical_data.get('rsi', 50),
            macd=technical_data.get('macd', 0),
            bb_position=technical_data.get('bb_position', 0.5),
            adx=technical_data.get('adx', 25),
            mfi=technical_data.get('mfi', 50),
            indicators=self._format_indicators(technical_data),
            signals=self._format_signals(technical_data),
            price_action=self._format_price_action(technical_data),
            fundamental=self._format_fundamental(fundamental_data),
            final_signal=technical_data.get('signal', 'hold').upper(),
            confidence=technical_data.get('confidence', 50),
            targets=self._format_targets(technical_data.get('targets', [])),
            stop_loss=technical_data.get('stop_loss', 0),
            time=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        response = await self._call_api(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            task_type=AITaskType.SIGNAL_ANALYSIS
        )
        
        return response.content if response.success else self._get_fallback_analysis()
    
    async def get_market_summary(self, market_data: Dict[str, Any]) -> str:
        """دریافت خلاصه بازار"""
        prompt = self.prompts['market_summary'].format(
            market_status=market_data.get('status', 'خنثی'),
            top_coins=market_data.get('top_coins', ''),
            bottom_coins=market_data.get('bottom_coins', ''),
            hot_coins=market_data.get('hot_coins', ''),
            overall_analysis=market_data.get('analysis', ''),
            time=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        response = await self._call_api(
            prompt=prompt,
            max_tokens=600,
            task_type=AITaskType.MARKET_SUMMARY
        )
        
        return response.content if response.success else "📊 خلاصه بازار در حال حاضر در دسترس نیست."
    
    async def get_portfolio_advice(self, portfolio: Dict[str, Any]) -> str:
        """دریافت مشاوره پورتفولیو"""
        prompt = self.prompts['portfolio_advice'].format(
            portfolio=portfolio.get('holdings', ''),
            goals=portfolio.get('goals', ''),
            allocation=portfolio.get('allocation', ''),
            suggestions=portfolio.get('suggestions', ''),
            warnings=portfolio.get('warnings', ''),
            key_points=portfolio.get('key_points', ''),
            time=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        response = await self._call_api(
            prompt=prompt,
            max_tokens=800,
            task_type=AITaskType.PORTFOLIO_ADVICE
        )
        
        return response.content if response.success else "💼 مشاوره پورتفولیو در حال حاضر در دسترس نیست."
    
    async def get_education(self, topic: str) -> str:
        """دریافت آموزش"""
        prompt = self.prompts['education'].format(
            topic=topic,
            introduction="",
            key_points="",
            example="",
            warnings="",
            golden_tip="",
            time=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        response = await self._call_api(
            prompt=prompt,
            max_tokens=1000,
            task_type=AITaskType.EDUCATION
        )
        
        return response.content if response.success else "📚 آموزش در حال حاضر در دسترس نیست."
    
    async def predict_price(
        self,
        coin: str,
        current_price: float,
        sma_7: float,
        sma_25: float,
        rsi: float,
        trend: str
    ) -> str:
        """پیش‌بینی قیمت"""
        prompt = self.prompts['price_prediction'].format(
            coin=coin,
            current_price=current_price,
            sma_7=sma_7,
            sma_25=sma_25,
            rsi=rsi,
            trend=trend,
            prediction_24h=current_price * (1.01 if trend == 'صعودی' else 0.99),
            prediction_7d=current_price * (1.05 if trend == 'صعودی' else 0.95),
            prediction_30d=current_price * (1.10 if trend == 'صعودی' else 0.90),
            scenarios="• سناریو صعودی: رشد ۱۰٪\n• سناریو نزولی: افت ۵٪\n• سناریو خنثی: نوسان ۲٪",
            factors="• اخبار مثبت\n• ورود سرمایه\n• تحلیل تکنیکال",
            time=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        response = await self._call_api(
            prompt=prompt,
            max_tokens=600,
            task_type=AITaskType.PRICE_PREDICTION
        )
        
        return response.content if response.success else "🔮 پیش‌بینی قیمت در حال حاضر در دسترس نیست."
    
    # ==================== متدهای کمکی ====================
    
    def _format_indicators(self, data: Dict[str, Any]) -> str:
        """فرمت‌سازی اندیکاتورها"""
        indicators = []
        for key, value in data.items():
            if key in ['rsi', 'macd', 'bb_position', 'adx', 'mfi', 'cci']:
                indicators.append(f"• {key.upper()}: {value:.2f}")
        return '\n'.join(indicators) if indicators else "• اطلاعاتی موجود نیست"
    
    def _format_signals(self, data: Dict[str, Any]) -> str:
        """فرمت‌سازی سیگنال‌ها"""
        signals = data.get('reasons', [])
        if not signals:
            return "• هیچ سیگنال مشخصی یافت نشد"
        return '\n'.join([f"• {s}" for s in signals[:5]])
    
    def _format_price_action(self, data: Dict[str, Any]) -> str:
        """فرمت‌سازی پرایس اکشن"""
        pattern = data.get('pattern', 'none')
        description = data.get('description', '')
        if pattern == 'none' or not description:
            return "• الگوی مشخصی یافت نشد"
        return f"• {pattern}: {description}"
    
    def _format_fundamental(self, data: Dict[str, Any]) -> str:
        """فرمت‌سازی فاندامنتال"""
        if not data:
            return "• اطلاعات فاندامنتال در دسترس نیست"
        reasons = data.get('reasons', [])
        if not reasons:
            return "• اطلاعات فاندامنتال در دسترس نیست"
        return '\n'.join([f"• {r}" for r in reasons[:5]])
    
    def _format_targets(self, targets: List[float]) -> str:
        """فرمت‌سازی اهداف"""
        if not targets:
            return "• هدفی تعیین نشده است"
        result = []
        for i, target in enumerate(targets, 1):
            result.append(f"   هدف {i}: ${target:.2f}")
        return '\n'.join(result)
    
    def _get_fallback_analysis(self) -> str:
        """تحلیل جایگزین در صورت خطا"""
        return """
🤖 **تحلیل هوشمند (حالت آفلاین)**

⚠️ **متاسفانه سرور AI در دسترس نیست.**

📊 **تحلیل تکنیکال بر اساس داده‌های موجود:**

🔹 **وضعیت:** روند خنثی
🔹 **سطح اطمینان:** ۵۰%
🔹 **پیشنهاد:** نگهداری و مشاهده

💡 **نکته:** لطفاً بعداً دوباره تلاش کنید.

⏰ **زمان:** {time}
""".format(time=datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    # ==================== متدهای مدیریت ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار هوش مصنوعی"""
        return {
            **self.stats,
            'rate_limit': self.rate_limiter.get_status(),
            'cache_size': len(self.cache._cache)
        }
    
    def clear_cache(self):
        """پاکسازی کش"""
        self.cache.clear()
    
    def get_models(self) -> Dict[str, str]:
        """دریافت لیست مدل‌ها"""
        return self.models

# ==================== کلاس مدیریت تحلیل ====================

import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

class GroqAI:
    """کلاس پایه هوش مصنوعی Groq"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self._cache = {}
    
    async def analyze_signal(
        self,
        coin: str,
        market_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any] = None,
        is_vip: bool = False
    ) -> str:
        """تحلیل سیگنال"""
        return f"""
🤖 **تحلیل هوشمند {coin}**

📊 **داده‌های تکنیکال:**
• قیمت فعلی: ${market_data.get('price', 0):.2f}
• تغییر ۲۴ ساعت: {market_data.get('change_24h', 0):.2f}%
• RSI: {technical_data.get('rsi', 50):.1f}
• MACD: {technical_data.get('macd', 0):.4f}

🎯 **پیشنهاد:** {technical_data.get('signal', 'hold').upper()}
🎯 **سطح اطمینان:** {technical_data.get('confidence', 50)}%

⏰ **زمان:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    async def predict_price(
        self,
        coin: str,
        current_price: float,
        sma_7: float = None,
        sma_25: float = None,
        rsi: float = 50,
        trend: str = "خنثی"
    ) -> str:
        """پیش‌بینی قیمت"""
        return f"""
🔮 **پیش‌بینی قیمت {coin}**

💰 **قیمت فعلی:** ${current_price:.2f}
📈 **پیش‌بینی ۲۴ ساعت:** ${current_price * 1.02:.2f}
📈 **پیش‌بینی ۷ روز:** ${current_price * 1.05:.2f}

⏰ **زمان:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    async def get_market_summary(self, market_data: Dict[str, Any]) -> str:
        """خلاصه بازار"""
        return f"""
🌍 **خلاصه بازار**

📊 بازار در حالت {market_data.get('status', 'خنثی')} قرار دارد.
💰 ارزهای برتر: BTC, ETH, BNB

⏰ **زمان:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    async def get_portfolio_advice(self, portfolio: Dict[str, Any]) -> str:
        """مشاوره پورتفولیو"""
        return "💼 مشاوره پورتفولیو در حال توسعه..."
    
    async def get_education(self, topic: str) -> str:
        """آموزش"""
        return f"📚 آموزش {topic} در حال توسعه..."
    
    def get_stats(self) -> Dict[str, Any]:
        """آمار"""
        return {"cache_size": len(self._cache)}
    
    def clear_cache(self):
        """پاکسازی کش"""
        self._cache.clear()


class AIAnalysisManager:
    """مدیریت تحلیل‌های هوش مصنوعی"""
    
    def __init__(self):
        self.groq = GroqAI()
        self._cache = {}
        self._cache_ttl = 300
    
    async def analyze_coin(
        self,
        coin: str,
        market_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any] = None,
        is_vip: bool = False
    ) -> Dict[str, Any]:
        """تحلیل کامل یک ارز"""
        
        # کش کردن
        cache_key = f"{coin}_{hashlib.md5(str(market_data).encode()).hexdigest()[:8]}"
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp).seconds < self._cache_ttl:
                return data
        
        # دریافت تحلیل از AI
        ai_analysis = await self.groq.analyze_signal(
            coin=coin,
            market_data=market_data,
            technical_data=technical_data,
            fundamental_data=fundamental_data,
            is_vip=is_vip
        )
        
        # دریافت پیش‌بینی
        prediction = await self.groq.predict_price(
            coin=coin,
            current_price=market_data.get('price', 0),
            sma_7=technical_data.get('sma_7', market_data.get('price', 0)),
            sma_25=technical_data.get('sma_25', market_data.get('price', 0)),
            rsi=technical_data.get('rsi', 50),
            trend=technical_data.get('trend', 'خنثی')
        )
        
        result = {
            'coin': coin,
            'ai_analysis': ai_analysis,
            'prediction': prediction,
            'is_vip': is_vip,
            'timestamp': datetime.now().isoformat()
        }
        
        self._cache[cache_key] = (result, datetime.now())
        return result
    
    async def get_market_summary(self, market_data: Dict[str, Any]) -> str:
        """دریافت خلاصه بازار"""
        return await self.groq.get_market_summary(market_data)
    
    async def get_portfolio_advice(self, portfolio: Dict[str, Any]) -> str:
        """دریافت مشاوره پورتفولیو"""
        return await self.groq.get_portfolio_advice(portfolio)
    
    async def get_education(self, topic: str) -> str:
        """دریافت آموزش"""
        return await self.groq.get_education(topic)
    
    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار"""
        return self.groq.get_stats()
    
    def clear_cache(self):
        """پاکسازی کش"""
        self.groq.clear_cache()
        self._cache.clear()


# ==================== Export ====================

ai_manager = AIAnalysisManager()
groq_ai = ai_manager.groq

def get_ai() -> AIAnalysisManager:
    return ai_manager

def get_groq() -> GroqAI:
    return groq_ai
