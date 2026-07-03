#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                              ║
║   ██████╗██████╗ ██╗   ██╗██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗███████╗███████╗        ║
║  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗██║   ██║██╔════╝██╔════╝        ║
║  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║██████╔╝██║   ██║█████╗  ███████╗        ║
║  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║██╔═══╝ ██║   ██║██╔══╝  ╚════██║        ║
║  ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝██║     ╚██████╔╝██║     ███████║        ║
║   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝ ╚═╝      ╚═════╝ ╚═╝     ╚══════╝        ║
║                                                                                              ║
║  🚀 CRYPTOPULSE AI v9.0 — PART 6 — ULTIMATE AI ENGINE — 100% PRODUCTION                     ║
║  ═══════════════════════════════════════════════════════════════════════════════════════════    ║
║                                                                                              ║
║  🤖 Groq AI           📊 Market Analysis      🔮 Price Prediction                           ║
║  🧠 Deep Learning      📈 Signal Generation     💡 Smart Insights                            ║
║  🔄 Multi-Model        💬 AI Chat              📝 Content Generator                         ║
║  ⚡ Rate Limit Mgmt     🗄️  Smart Cache          🛡️ Error Recovery                           ║
║                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 0: ABSOLUTE SILENCE SETUP
# ═══════════════════════════════════════════════════════════════════════════════════════════════

import os, sys, json, time, random, hashlib, hmac, base64, re, asyncio
import threading, itertools, functools
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union, Callable
from collections import defaultdict, OrderedDict, deque
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

# ─── KILL ALL WARNINGS & LOGS ───
import warnings
warnings.filterwarnings("ignore")
for _cat in [DeprecationWarning, FutureWarning, RuntimeWarning, UserWarning,
             SyntaxWarning, PendingDeprecationWarning, ImportWarning, BytesWarning, ResourceWarning]:
    warnings.filterwarnings("ignore", category=_cat)

import logging
logging.basicConfig(level=logging.CRITICAL, handlers=[logging.NullHandler()])
for _name in list(logging.root.manager.loggerDict.keys()):
    logging.getLogger(_name).setLevel(logging.CRITICAL)
    logging.getLogger(_name).handlers.clear()
    logging.getLogger(_name).addHandler(logging.NullHandler())
    logging.getLogger(_name).propagate = False

# ─── OPTIONAL IMPORTS ───
HAS_AIOHTTP = False
HAS_GROQ = False

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    pass

try:
    from groq import AsyncGroq
    HAS_GROQ = True
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 1: SAFE IMPORT FROM OTHER PARTS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

def _silent_import(module_name: str, *attrs: str) -> Dict[str, Any]:
    """ایمپورت کاملاً بی‌صدا"""
    result = {attr: None for attr in attrs}
    try:
        mod = __import__(module_name, fromlist=list(attrs))
        for attr in attrs:
            try:
                result[attr] = getattr(mod, attr, None)
            except:
                pass
    except:
        pass
    return result

# ایمپورت از پارت‌های دیگه
_part2 = _silent_import("part2", "get_config", "db_manager")
_part4 = _silent_import("part4", "get_time", "get_emoji", "get_formatter", "get_cache")
_part5 = _silent_import("part5", "get_market", "get_price", "get_ticker", "get_market_summary")

get_config = _part2.get("get_config")
db_manager = _part2.get("db_manager")

get_time = _part4.get("get_time")
get_emoji = _part4.get("get_emoji")
get_formatter = _part4.get("get_formatter")
get_cache = _part4.get("get_cache")

get_market = _part5.get("get_market")
get_price_func = _part5.get("get_price")
get_ticker_func = _part5.get("get_ticker")
get_market_summary_func = _part5.get("get_market_summary")

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 2: CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
AI_ENABLED = bool(GROQ_API_KEY) and HAS_GROQ
AI_MAX_REQUESTS_PER_MINUTE = int(os.environ.get("AI_MAX_REQUESTS_PER_MINUTE", "25"))
AI_MAX_REQUESTS_PER_DAY = int(os.environ.get("AI_MAX_REQUESTS_PER_DAY", "14000"))
AI_MAX_TOKENS_PER_MINUTE = int(os.environ.get("AI_MAX_TOKENS_PER_MINUTE", "8000"))
AI_MAX_TOKENS_PER_DAY = int(os.environ.get("AI_MAX_TOKENS_PER_DAY", "400000"))
AI_MAX_CONCURRENT = int(os.environ.get("AI_MAX_CONCURRENT", "4"))
AI_CACHE_SIZE = int(os.environ.get("AI_CACHE_SIZE", "500"))
AI_CACHE_TTL = int(os.environ.get("AI_CACHE_TTL", "3600"))
AI_DEFAULT_MODEL = os.environ.get("AI_DEFAULT_MODEL", "llama-3.2-90b-vision-preview")
AI_DEFAULT_TEMPERATURE = float(os.environ.get("AI_DEFAULT_TEMPERATURE", "0.3"))
AI_DEFAULT_MAX_TOKENS = int(os.environ.get("AI_DEFAULT_MAX_TOKENS", "800"))

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 3: ENUMS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class AIModel(str, Enum):
    LLAMA_90B = "llama-3.2-90b-vision-preview"
    LLAMA_11B = "llama-3.2-11b-vision-preview"
    LLAMA_3B = "llama-3.2-3b-preview"
    LLAMA_70B = "llama3-70b-8192"
    LLAMA_8B = "llama3-8b-8192"
    MIXTRAL = "mixtral-8x7b-32768"
    GEMMA = "gemma-7b-it"

class AITaskType(str, Enum):
    SIGNAL_ANALYSIS = "signal_analysis"
    MARKET_SUMMARY = "market_summary"
    TECHNICAL_ANALYSIS = "technical_analysis"
    PRICE_PREDICTION = "price_prediction"
    PORTFOLIO_ADVICE = "portfolio_advice"
    EDUCATION = "education"
    SENTIMENT = "sentiment_analysis"
    STRATEGY = "trading_strategy"
    CHAT = "ai_chat"
    EXPLAIN = "ai_explain"
    BACKTEST = "ai_backtest"

class SignalStrength(str, Enum):
    VERY_STRONG_BUY = "very_strong_buy"
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    WEAK_BUY = "weak_buy"
    NEUTRAL = "neutral"
    WEAK_SELL = "weak_sell"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    VERY_STRONG_SELL = "very_strong_sell"

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 4: DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

@dataclass
class AIRequest:
    prompt: str
    task_type: AITaskType = AITaskType.CHAT
    model: str = AI_DEFAULT_MODEL
    temperature: float = AI_DEFAULT_TEMPERATURE
    max_tokens: int = AI_DEFAULT_MAX_TOKENS
    priority: int = 1
    user_id: Optional[str] = None
    system_prompt: Optional[str] = None
    context: Optional[Dict] = None

@dataclass
class AIResponse:
    content: str
    model: str
    tokens_used: int = 0
    processing_time: float = 0.0
    task_type: AITaskType = AITaskType.CHAT
    success: bool = True
    error: Optional[str] = None
    from_cache: bool = False

@dataclass
class SignalResult:
    symbol: str
    signal: str
    strength: float
    confidence: float
    price: float
    stop_loss: float
    take_profits: List[float]
    reasons: List[str]
    ai_analysis: str = ""
    timestamp: str = ""

@dataclass
class PredictionResult:
    symbol: str
    current_price: float
    prediction_24h: float
    prediction_7d: float
    prediction_30d: float
    confidence: float
    trend: str
    factors: List[str]
    ai_analysis: str = ""
    timestamp: str = ""

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 5: RATE LIMIT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class RateLimitManager:
    def __init__(self):
        self.max_rpm = AI_MAX_REQUESTS_PER_MINUTE
        self.max_rpd = AI_MAX_REQUESTS_PER_DAY
        self.max_tpm = AI_MAX_TOKENS_PER_MINUTE
        self.max_tpd = AI_MAX_TOKENS_PER_DAY
        self.max_concurrent = AI_MAX_CONCURRENT

        self._minute_requests: deque = deque(maxlen=self.max_rpm)
        self._day_requests: int = 0
        self._minute_tokens: int = 0
        self._day_tokens: int = 0
        self._concurrent: int = 0
        self._last_day_reset = datetime.now()
        self._lock = threading.RLock()

    def acquire(self, estimated_tokens: int = 500) -> Tuple[bool, str]:
        with self._lock:
            now = datetime.now()

            if (now - self._last_day_reset).days >= 1:
                self._day_requests = 0
                self._day_tokens = 0
                self._last_day_reset = now

            if len(self._minute_requests) >= self.max_rpm:
                return False, "Minute request limit reached"

            if self._day_requests >= self.max_rpd:
                return False, "Daily request limit reached"

            if self._minute_tokens + estimated_tokens > self.max_tpm:
                return False, "Minute token limit reached"

            if self._day_tokens + estimated_tokens > self.max_tpd:
                return False, "Daily token limit reached"

            if self._concurrent >= self.max_concurrent:
                return False, "Concurrent request limit reached"

            self._minute_requests.append(now)
            self._minute_tokens += estimated_tokens
            self._day_requests += 1
            self._day_tokens += estimated_tokens
            self._concurrent += 1

            return True, "ok"

    def release(self):
        with self._lock:
            self._concurrent = max(0, self._concurrent - 1)

    def get_stats(self) -> Dict:
        with self._lock:
            return {
                "requests_minute": len(self._minute_requests),
                "requests_minute_limit": self.max_rpm,
                "requests_day": self._day_requests,
                "requests_day_limit": self.max_rpd,
                "tokens_minute": self._minute_tokens,
                "tokens_minute_limit": self.max_tpm,
                "tokens_day": self._day_tokens,
                "tokens_day_limit": self.max_tpd,
                "concurrent": self._concurrent,
                "concurrent_limit": self.max_concurrent,
            }

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 6: SMART AI CACHE
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class AICache:
    def __init__(self, max_size: int = AI_CACHE_SIZE, default_ttl: int = AI_CACHE_TTL):
        self._l1: OrderedDict = OrderedDict()
        self._l2: Dict[str, Tuple[Any, float]] = {}
        self._max_size = max_size
        self._ttl = default_ttl
        self._hits = 0
        self._misses = 0
        self._lock = threading.RLock()

    def _make_key(self, prompt: str, model: str, temp: float) -> str:
        raw = f"{prompt[:200]}|{model}|{temp}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, prompt: str, model: str, temp: float) -> Optional[str]:
        key = self._make_key(prompt, model, temp)
        with self._lock:
            if key in self._l1:
                val, exp = self._l1[key]
                if time.time() < exp:
                    self._l1.move_to_end(key)
                    self._hits += 1
                    return val
                del self._l1[key]
            if key in self._l2:
                val, exp = self._l2[key]
                if time.time() < exp:
                    self._l1[key] = (val, exp)
                    if len(self._l1) > self._max_size // 2:
                        self._l1.popitem(last=False)
                    self._hits += 1
                    return val
                del self._l2[key]
            self._misses += 1
            return None

    def set(self, prompt: str, model: str, temp: float, response: str, ttl: int = None):
        key = self._make_key(prompt, model, temp)
        exp = time.time() + (ttl or self._ttl)
        with self._lock:
            self._l2[key] = (response, exp)
            if len(self._l2) > self._max_size:
                oldest = min(self._l2.items(), key=lambda x: x[1][1])[0]
                del self._l2[oldest]
            self._l1[key] = (response, exp)
            if len(self._l1) > self._max_size // 2:
                self._l1.popitem(last=False)

    def clear(self):
        with self._lock:
            self._l1.clear()
            self._l2.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict:
        total = self._hits + self._misses
        rate = (self._hits / total * 100) if total > 0 else 0
        return {"size": len(self._l1) + len(self._l2), "hits": self._hits, "misses": self._misses, "hit_rate": f"{rate:.1f}%"}

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 7: PROMPT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class PromptEngine:
    SYSTEM_PROMPT = "شما یک تحلیلگر حرفه‌ای بازار ارزهای دیجیتال با ۲۰ سال تجربه هستید. پاسخ‌های خود را به زبان فارسی، دقیق، کامل و با استفاده از ایموجی‌های مناسب ارائه دهید. همیشه جوانب مثبت و منفی را بررسی کنید. در پایان یک توصیه عملی ارائه دهید."

    @staticmethod
    def signal_analysis(coin: str, price: float, change_24h: float, rsi: float, macd: float, volume: float, support: float, resistance: float, trend: str) -> str:
        return f"""تحلیل کامل سیگنال معاملاتی برای {coin}:

قیمت فعلی: ${price:,.2f}
تغییر ۲۴ ساعته: {change_24h:+.2f}%
RSI (۱۴): {rsi:.1f}
MACD: {macd:.4f}
حجم معاملات ۲۴h: {volume:,.0f}
حمایت کلیدی: ${support:,.2f}
مقاومت کلیدی: ${resistance:,.2f}
روند کلی: {trend}

لطفاً تحلیل کاملی ارائه دهید شامل:
۱. تحلیل تکنیکال
۲. سطوح حمایت و مقاومت
۳. پیشنهاد معاملاتی (خرید/فروش/نگهداری)
۴. حد ضرر و اهداف قیمتی
۵. سطح اطمینان (درصد)"""

    @staticmethod
    def market_summary(top_gainers: str, top_losers: str, btc_dominance: float, fear_greed: int, total_mcap: str) -> str:
        return f"""خلاصه وضعیت فعلی بازار ارزهای دیجیتال:

بیشترین رشدها: {top_gainers}
بیشترین افت‌ها: {top_losers}
دامیننس بیت‌کوین: {btc_dominance:.1f}%
شاخص ترس و طمع: {fear_greed}/100
ارزش کل بازار: {total_mcap}

لطفاً تحلیل کاملی از وضعیت بازار ارائه دهید و روندهای اصلی را توضیح دهید."""

    @staticmethod
    def price_prediction(coin: str, price: float, sma_7: float, sma_25: float, rsi: float, trend: str) -> str:
        return f"""پیش‌بینی قیمت {coin}:

قیمت فعلی: ${price:,.2f}
میانگین متحرک ۷ روزه: ${sma_7:,.2f}
میانگین متحرک ۲۵ روزه: ${sma_25:,.2f}
RSI: {rsi:.1f}
روند: {trend}

لطفاً پیش‌بینی قیمت برای ۲۴ ساعت، ۷ روز و ۳۰ روز آینده ارائه دهید.
سناریوهای صعودی، نزولی و خنثی را بررسی کنید."""

    @staticmethod
    def portfolio_advice(holdings: str, risk_profile: str, goal: str) -> str:
        return f"""مشاوره مدیریت پورتفولیو:

دارایی‌های فعلی: {holdings}
پروفایل ریسک: {risk_profile}
هدف سرمایه‌گذاری: {goal}

لطفاً توصیه‌های زیر را ارائه دهید:
۱. تخصیص بهینه دارایی
۲. پیشنهادات خرید/فروش
۳. مدیریت ریسک
۴. استراتژی خروج"""

    @staticmethod
    def education(topic: str) -> str:
        return f"""لطفاً یک آموزش کامل و جامع به زبان فارسی درباره "{topic}" در حوزه ارزهای دیجیتال و معاملات ارائه دهید.

شامل:
۱. تعریف و مقدمه
۲. مفاهیم کلیدی
۳. مثال‌های عملی
۴. نکات حرفه‌ای
۵. اشتباهات رایج
۶. جمع‌بندی و توصیه نهایی"""

    @staticmethod
    def strategy(market_condition: str, capital: str, experience: str) -> str:
        return f"""یک استراتژی معاملاتی کامل طراحی کن:

شرایط بازار: {market_condition}
سرمایه: {capital}
سطح تجربه: {experience}

شامل:
۱. استراتژی ورود
۲. استراتژی خروج
۳. مدیریت ریسک
۴. مدیریت سرمایه
۵. اندیکاتورهای پیشنهادی
۶. تایم‌فریم‌های مناسب"""

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 8: AI RESPONSE PARSER
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class AIResponseParser:
    @staticmethod
    def extract_confidence(text: str) -> float:
        patterns = [r'اطمینان[:\s]*(\d+)', r'confidence[:\s]*(\d+)', r'سطح اطمینان[:\s]*(\d+)', r'(\d+)%\s*اطمینان']
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m: return float(m.group(1))
        return 50.0

    @staticmethod
    def extract_price(text: str, label: str = "قیمت") -> Optional[float]:
        patterns = [rf'{label}[:\s]*\$?(\d+[\.,]?\d*)', rf'{label}[:\s]*(\d+[\.,]?\d*)\s*دلار']
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m: return float(m.group(1).replace(',', ''))
        return None

    @staticmethod
    def extract_signal(text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ['خرید قوی', 'strong buy', 'very bullish']): return "strong_buy"
        if any(w in text_lower for w in ['خرید', 'buy', 'bullish', 'صعودی']): return "buy"
        if any(w in text_lower for w in ['فروش قوی', 'strong sell', 'very bearish']): return "strong_sell"
        if any(w in text_lower for w in ['فروش', 'sell', 'bearish', 'نزولی']): return "sell"
        return "neutral"

    @staticmethod
    def extract_targets(text: str) -> List[float]:
        targets = []
        patterns = [r'هدف\s*\d[:\s]*\$?(\d+[\.,]?\d*)', r'target\s*\d[:\s]*\$?(\d+[\.,]?\d*)', r'TP\s*\d[:\s]*\$?(\d+[\.,]?\d*)']
        for p in patterns:
            matches = re.findall(p, text, re.IGNORECASE)
            targets.extend([float(m.replace(',', '')) for m in matches])
        return sorted(set(targets))[:5]

    @staticmethod
    def extract_stop_loss(text: str) -> Optional[float]:
        patterns = [r'حد ضرر[:\s]*\$?(\d+[\.,]?\d*)', r'stop loss[:\s]*\$?(\d+[\.,]?\d*)', r'SL[:\s]*\$?(\d+[\.,]?\d*)']
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m: return float(m.group(1).replace(',', ''))
        return None

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 9: MAIN AI ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class AIEngine:
    """Ultimate AI Engine — Groq Powered"""

    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.enabled = AI_ENABLED
        self.client = None
        self.rate_limiter = RateLimitManager()
        self.cache = AICache()
        self.prompts = PromptEngine()
        self.parser = AIResponseParser()
        self._stats = {"total": 0, "success": 0, "failed": 0, "cached": 0, "total_tokens": 0, "total_time": 0.0}
        self._lock = threading.RLock()

        if self.enabled and HAS_GROQ:
            try:
                self.client = AsyncGroq(api_key=self.api_key)
            except:
                self.enabled = False

    # ═══════════ CORE API CALL ═══════════

    async def _call_api(self, request: AIRequest) -> AIResponse:
        if not self.enabled:
            return AIResponse(content=self._fallback_response(request.task_type), model="fallback", success=False, error="AI disabled", task_type=request.task_type)

        # Check cache
        cached = self.cache.get(request.prompt, request.model, request.temperature)
        if cached:
            self._stats["cached"] += 1
            return AIResponse(content=cached, model=request.model, tokens_used=len(cached.split()), processing_time=0, task_type=request.task_type, success=True, from_cache=True)

        # Rate limit
        estimated_tokens = request.max_tokens + len(request.prompt.split()) * 2
        allowed, reason = self.rate_limiter.acquire(estimated_tokens)
        if not allowed:
            return AIResponse(content=self._fallback_response(request.task_type), model=request.model, success=False, error=reason, task_type=request.task_type)

        try:
            start = time.time()
            system_prompt = request.system_prompt or PromptEngine.SYSTEM_PROMPT

            response = await self.client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": request.prompt}],
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=0.95,
            )

            elapsed = time.time() - start
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if hasattr(response, 'usage') else len(content.split())

            # Update stats
            with self._lock:
                self._stats["total"] += 1
                self._stats["success"] += 1
                self._stats["total_tokens"] += tokens
                self._stats["total_time"] += elapsed

            # Cache
            self.cache.set(request.prompt, request.model, request.temperature, content)

            return AIResponse(content=content, model=request.model, tokens_used=tokens, processing_time=elapsed, task_type=request.task_type, success=True)

        except Exception as e:
            with self._lock:
                self._stats["total"] += 1
                self._stats["failed"] += 1
            return AIResponse(content=self._fallback_response(request.task_type), model=request.model, success=False, error=str(e)[:200], task_type=request.task_type)

        finally:
            self.rate_limiter.release()

    # ═══════════ PUBLIC API METHODS ═══════════

    async def chat(self, message: str, user_id: str = None, model: str = None) -> AIResponse:
        req = AIRequest(prompt=message, task_type=AITaskType.CHAT, model=model or AI_DEFAULT_MODEL, user_id=user_id, max_tokens=1000)
        return await self._call_api(req)

    async def analyze_signal(self, coin: str, price: float, change_24h: float = 0, rsi: float = 50, macd: float = 0, volume: float = 0, support: float = 0, resistance: float = 0, trend: str = "خنثی") -> AIResponse:
        prompt = self.prompts.signal_analysis(coin, price, change_24h, rsi, macd, volume, support, resistance, trend)
        req = AIRequest(prompt=prompt, task_type=AITaskType.SIGNAL_ANALYSIS, model=AIModel.LLAMA_90B.value, max_tokens=1200)
        return await self._call_api(req)

    async def get_market_summary(self, top_gainers: str = "", top_losers: str = "", btc_dominance: float = 52, fear_greed: int = 50, total_mcap: str = "2.4T") -> AIResponse:
        prompt = self.prompts.market_summary(top_gainers, top_losers, btc_dominance, fear_greed, total_mcap)
        req = AIRequest(prompt=prompt, task_type=AITaskType.MARKET_SUMMARY, max_tokens=800)
        return await self._call_api(req)

    async def predict_price(self, coin: str, price: float, sma_7: float = None, sma_25: float = None, rsi: float = 50, trend: str = "خنثی") -> AIResponse:
        prompt = self.prompts.price_prediction(coin, price, sma_7 or price, sma_25 or price, rsi, trend)
        req = AIRequest(prompt=prompt, task_type=AITaskType.PRICE_PREDICTION, max_tokens=800)
        return await self._call_api(req)

    async def get_portfolio_advice(self, holdings: str, risk_profile: str = "متوسط", goal: str = "بلندمدت") -> AIResponse:
        prompt = self.prompts.portfolio_advice(holdings, risk_profile, goal)
        req = AIRequest(prompt=prompt, task_type=AITaskType.PORTFOLIO_ADVICE, max_tokens=1000)
        return await self._call_api(req)

    async def get_education(self, topic: str) -> AIResponse:
        prompt = self.prompts.education(topic)
        req = AIRequest(prompt=prompt, task_type=AITaskType.EDUCATION, max_tokens=1500)
        return await self._call_api(req)

    async def get_strategy(self, market_condition: str = "خنثی", capital: str = "۱۰۰۰ دلار", experience: str = "متوسط") -> AIResponse:
        prompt = self.prompts.strategy(market_condition, capital, experience)
        req = AIRequest(prompt=prompt, task_type=AITaskType.STRATEGY, max_tokens=1200)
        return await self._call_api(req)

    async def explain_concept(self, concept: str) -> AIResponse:
        prompt = f"""لطفاً مفهوم "{concept}" را در حوزه ارزهای دیجیتال و معاملات به زبان ساده و کامل توضیح دهید.

شامل:
۱. تعریف ساده
۲. نحوه استفاده در معاملات
۳. مثال عملی
۴. مزایا و معایب
۵. نکات کلیدی"""
        req = AIRequest(prompt=prompt, task_type=AITaskType.EXPLAIN, max_tokens=1000)
        return await self._call_api(req)

    async def backtest_analysis(self, strategy_desc: str, coin: str = "BTC", timeframe: str = "4h") -> AIResponse:
        prompt = f"""تحلیل بک‌تست استراتژی معاملاتی:

ارز: {coin}
تایم‌فریم: {timeframe}
استراتژی: {strategy_desc}

لطفاً تحلیل کنید:
۱. نقاط قوت استراتژی
۲. نقاط ضعف استراتژی
۳. پیشنهادات بهبود
۴. نرخ برد تخمینی
۵. نسبت ریسک به ریوارد"""
        req = AIRequest(prompt=prompt, task_type=AITaskType.BACKTEST, max_tokens=1000)
        return await self._call_api(req)

    # ═══════════ COMPLETE WORKFLOWS ═══════════

    async def complete_signal(self, coin: str, price: float, change_24h: float = 0, rsi: float = 50, macd: float = 0, volume: float = 0, support: float = 0, resistance: float = 0, trend: str = "خنثی") -> SignalResult:
        resp = await self.analyze_signal(coin, price, change_24h, rsi, macd, volume, support, resistance, trend)

        signal = self.parser.extract_signal(resp.content)
        confidence = self.parser.extract_confidence(resp.content)
        targets = self.parser.extract_targets(resp.content) or [price * 1.05, price * 1.10, price * 1.20]
        stop_loss = self.parser.extract_stop_loss(resp.content) or price * 0.95

        signal_map = {"strong_buy": 90, "buy": 70, "neutral": 50, "sell": 30, "strong_sell": 10}
        strength = signal_map.get(signal, 50)

        return SignalResult(symbol=coin, signal=signal, strength=strength, confidence=confidence, price=price, stop_loss=stop_loss, take_profits=targets, reasons=[resp.content[:200]], ai_analysis=resp.content, timestamp=datetime.now().isoformat())

    async def complete_prediction(self, coin: str, price: float, sma_7: float = None, sma_25: float = None, rsi: float = 50, trend: str = "خنثی") -> PredictionResult:
        resp = await self.predict_price(coin, price, sma_7, sma_25, rsi, trend)

        pred_24h = self.parser.extract_price(resp.content, "۲۴ ساعت") or price * 1.02
        pred_7d = self.parser.extract_price(resp.content, "۷ روز") or price * 1.05
        pred_30d = self.parser.extract_price(resp.content, "۳۰ روز") or price * 1.10
        confidence = self.parser.extract_confidence(resp.content)

        return PredictionResult(symbol=coin, current_price=price, prediction_24h=pred_24h, prediction_7d=pred_7d, prediction_30d=pred_30d, confidence=confidence, trend=trend, factors=[resp.content[:200]], ai_analysis=resp.content, timestamp=datetime.now().isoformat())

    # ═══════════ FALLBACK ═══════════

    def _fallback_response(self, task_type: AITaskType) -> str:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        responses = {
            AITaskType.SIGNAL_ANALYSIS: f"📊 **تحلیل سیگنال (حالت آفلاین)**\n\n⚠️ سرور AI در دسترس نیست.\n\n💡 لطفاً از اندیکاتورهای تکنیکال برای تصمیم‌گیری استفاده کنید.\n\n⏰ {now_str}",
            AITaskType.MARKET_SUMMARY: f"🌍 **خلاصه بازار (حالت آفلاین)**\n\n⚠️ اطلاعات بازار در حال حاضر در دسترس نیست.\n\n⏰ {now_str}",
            AITaskType.PRICE_PREDICTION: f"🔮 **پیش‌بینی قیمت (حالت آفلاین)**\n\n⚠️ سرویس پیش‌بینی در دسترس نیست.\n\n⏰ {now_str}",
            AITaskType.CHAT: f"💬 **چت AI (حالت آفلاین)**\n\n⚠️ سرور AI در حال حاضر در دسترس نیست. لطفاً بعداً تلاش کنید.\n\n⏰ {now_str}",
        }
        return responses.get(task_type, f"⚠️ سرویس AI در دسترس نیست.\n\n⏰ {now_str}")

    # ═══════════ STATS & MANAGEMENT ═══════════

    def get_stats(self) -> Dict:
        with self._lock:
            avg_time = self._stats["total_time"] / max(self._stats["success"], 1)
            return {
                **self._stats,
                "avg_response_time": round(avg_time, 3),
                "enabled": self.enabled,
                "rate_limit": self.rate_limiter.get_stats(),
                "cache": self.cache.get_stats(),
            }

    def clear_cache(self):
        self.cache.clear()

    def is_enabled(self) -> bool:
        return self.enabled

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 10: SINGLETON & EXPORT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

_ai_instance: Optional[AIEngine] = None
_instance_lock = threading.Lock()

def get_ai() -> AIEngine:
    global _ai_instance
    if _ai_instance is None:
        with _instance_lock:
            if _ai_instance is None:
                _ai_instance = AIEngine()
    return _ai_instance

def get_groq() -> AIEngine:
    return get_ai()

def start() -> bool:
    get_ai()
    return True

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 11: STANDALONE
# ═══════════════════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    ai = get_ai()
    if ai.is_enabled():
        print("✅ AI Engine is ENABLED")
        print(f"   Model: {AI_DEFAULT_MODEL}")
        print(f"   Cache: {AI_CACHE_SIZE} entries, TTL: {AI_CACHE_TTL}s")
        print(f"   Rate Limit: {AI_MAX_REQUESTS_PER_MINUTE}/min")
    else:
        print("⚠️ AI Engine is DISABLED (no API key or groq not installed)")
        print("   Set GROQ_API_KEY environment variable to enable")
        print("   Install: pip install groq")
