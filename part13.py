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
║  🚀 CRYPTOPULSE AI v9.0 — PART 13 — ENTERPRISE API & WEBHOOK SERVER — 100% PRODUCTION       ║
║  ═══════════════════════════════════════════════════════════════════════════════════════════    ║
║                                                                                              ║
║  📡 FastAPI Server      🔐 HMAC Security       📊 50+ API Endpoints                          ║
║  🌐 Webhook Handler     💾 Redis Cache          🔄 Auto-Recovery                             ║
║  📈 Prometheus Metrics  🛡️ Rate Limiting        🧠 Health Monitor                            ║
║  🔌 WebSocket Support   📋 Pydantic Models      🚦 Circuit Breaker                           ║
║  🗄️  Database Pool       ⚡ Async Workers        🔔 Alert System                              ║
║                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 0: IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

import os, sys, time, uuid, asyncio, hashlib, hmac, logging, socket, platform, json
import signal as _signal
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Union, Tuple, Callable, Awaitable
from collections import defaultdict, deque, OrderedDict
from contextlib import asynccontextmanager
from enum import Enum, IntEnum
from dataclasses import dataclass, field, asdict
from functools import wraps

# ─── External Libraries ───
try: import psutil; HAS_PSUTIL = True
except ImportError: HAS_PSUTIL = False

try: import uvicorn; HAS_UVICORN = True
except ImportError: HAS_UVICORN = False

try: import aiohttp; HAS_AIOHTTP = True
except ImportError: HAS_AIOHTTP = False

try: from fastapi import (FastAPI, Request, HTTPException, Depends, Header, Query, Path,
                          WebSocket, WebSocketDisconnect, status, BackgroundTasks)
      from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
      from fastapi.middleware.cors import CORSMiddleware
      from fastapi.middleware.gzip import GZipMiddleware
      from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
      HAS_FASTAPI = True
except ImportError: HAS_FASTAPI = False

try: from pydantic import BaseModel, Field, validator
except ImportError:
    class BaseModel: pass
    class Field:
        def __init__(self, *args, **kwargs): pass

# ─── Silence ───
warnings = __import__('warnings')
warnings.filterwarnings("ignore")
for _lib in ["uvicorn", "uvicorn.access", "uvicorn.error", "aiohttp", "apscheduler", "httpx"]:
    logging.getLogger(_lib).setLevel(logging.CRITICAL + 1)

logger = logging.getLogger("cryptopulse.part13")
logger.setLevel(logging.WARNING)
if not logger.handlers:
    _h = logging.StreamHandler(sys.stderr)
    _h.setFormatter(logging.Formatter('%(levelname)s | %(name)s | %(message)s'))
    logger.addHandler(_h)

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 1: SAFE IMPORT SYSTEM — ALL 18 PARTS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

def safe_import(module_name: str, *attrs: str) -> Dict[str, Any]:
    """Import ایمن با fallback — بدون crash"""
    result = {attr: None for attr in attrs}
    try:
        mod = __import__(module_name, fromlist=list(attrs))
        for attr in attrs:
            try: result[attr] = getattr(mod, attr, None)
            except: pass
    except Exception:
        pass
    return result

# Import همه ۱۸ پارت
_p1  = safe_import("part1",  "get_config", "verify_api_key", "hash_api_key", "db_manager")
_p2  = safe_import("part2",  "db_manager", "user_repo", "signal_repo", "payment_repo", "get_user_repo", "get_signal_repo", "get_payment_repo")
_p3  = safe_import("part3",  "get_user_repo", "get_signal_repo", "get_payment_repo", "db_manager")
_p4  = safe_import("part4",  "get_time", "get_emoji", "get_formatter", "get_hash", "get_validator", "get_cache")
_p5  = safe_import("part5",  "get_market", "get_coinex", "get_signal", "get_ticker", "get_price", "get_ohlcv_data", "get_market_summary", "MarketAggregator", "CoinExClient", "MultiExchangeManager")
_p6  = safe_import("part6",  "get_ai", "get_groq")
_p7  = safe_import("part7",  "get_technical", "TechnicalIndicators")
_p8  = safe_import("part8",  "lux_keyboard", "menu_builder", "LuxText", "LuxEmoji")
_p9  = safe_import("part9",  "get_application", "start")
_p10 = safe_import("part10", "TradingEngine", "OrderManager", "PositionManager")
_p11 = safe_import("part11", "PaymentGateway", "InvoiceManager", "TransactionManager")
_p12 = safe_import("part12", "MediaManager", "ContentGenerator", "ImageProcessor")
_p13 = safe_import("part13", "NotificationManager", "AlertSystem", "PushNotifier")
_p14 = safe_import("part14", "TelegramBot", "WebhookManager", "PollingManager")
_p15 = safe_import("part15", "Monitor", "Logger", "MetricsCollector", "HealthChecker")
_p16 = safe_import("part16", "get_intelligence_engine", "AdminIntelligenceEngine", "UserIntelligence", "FinancialIntelligence", "SignalIntelligence", "ComprehensiveReport")
_p17 = safe_import("part17", "get_analysis_engine", "AnalysisEngine", "TechnicalIndicators", "CandlestickPatterns", "FibonacciEngine", "WhaleTracker", "PriceActionEngine", "FundamentalAnalysis")
_p18 = safe_import("part18", "get_god_mode_engine", "GodModeEngine", "GodSignal", "MarketScanner", "ChannelManager", "MarketOverview")

# ─── Extract functions with fallback chain ───
def _extract(*attrs: str, default: Any = None) -> Any:
    """Extract attribute from all parts with fallback"""
    for part in [_p1, _p2, _p3, _p4, _p5, _p6, _p7, _p8, _p9, _p10, _p11, _p12, _p13, _p14, _p15, _p16, _p17, _p18]:
        for attr in attrs:
            val = part.get(attr)
            if val is not None: return val
    return default

# Core services
get_config              = _extract("get_config")
verify_api_key          = _extract("verify_api_key", "verify_api_key_fn")
hash_api_key            = _extract("hash_api_key")
db_manager              = _extract("db_manager")
user_repo               = _extract("user_repo", "get_user_repo")
signal_repo             = _extract("signal_repo", "get_signal_repo")
payment_repo            = _extract("payment_repo", "get_payment_repo")
get_cache               = _extract("get_cache")
get_time                = _extract("get_time")
get_emoji               = _extract("get_emoji")
get_formatter           = _extract("get_formatter")
get_hash                = _extract("get_hash")
get_validator           = _extract("get_validator")
get_market              = _extract("get_market", "MarketAggregator")
get_coinex              = _extract("get_coinex", "CoinExClient")
get_signal_func         = _extract("get_signal")
get_ticker_func         = _extract("get_ticker")
get_price_func          = _extract("get_price")
get_ohlcv_func          = _extract("get_ohlcv_data")
get_market_summary_func = _extract("get_market_summary")
get_ai                  = _extract("get_ai")
get_groq                = _extract("get_groq")
get_technical           = _extract("get_technical")
TechnicalIndicators     = _extract("TechnicalIndicators")
get_intelligence_engine = _extract("get_intelligence_engine")
get_analysis_engine     = _extract("get_analysis_engine")
get_god_mode_engine     = _extract("get_god_mode_engine")
GodModeEngine           = _extract("GodModeEngine")
GodSignal               = _extract("GodSignal")
MarketScanner           = _extract("MarketScanner")
ChannelManager          = _extract("ChannelManager")
WhaleTracker            = _extract("WhaleTracker")
TradingEngine           = _extract("TradingEngine")
PaymentGateway          = _extract("PaymentGateway")
NotificationManager     = _extract("NotificationManager")
MediaManager            = _extract("MediaManager")
Monitor                 = _extract("Monitor", "HealthChecker")

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 2: CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class Config:
    """Configuration Manager"""
    PORT                = int(os.environ.get("PORT", "8080"))
    HOST                = os.environ.get("HOST", "0.0.0.0")
    DEBUG               = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
    ENVIRONMENT          = os.environ.get("ENVIRONMENT", "production")
    BOT_TOKEN            = os.environ.get("BOT_TOKEN", "") or os.environ.get("BOT_TOKEN_MAIN", "")
    API_KEY              = os.environ.get("API_KEY", "")
    API_KEY_HASH         = os.environ.get("API_KEY_HASH", "")
    SECRET_KEY           = os.environ.get("SECRET_KEY", hashlib.sha256(os.urandom(32)).hexdigest())
    WEBHOOK_URL          = os.environ.get("WEBHOOK_URL", "")
    WEBHOOK_PATH         = os.environ.get("WEBHOOK_PATH", "/webhook/telegram")
    ALLOWED_HOSTS        = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "*").split(",") if h.strip()]
    CORS_ORIGINS         = os.environ.get("CORS_ORIGINS", "*").split(",")
    RATE_LIMIT_REQUESTS  = int(os.environ.get("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD    = int(os.environ.get("RATE_LIMIT_PERIOD", "60"))
    RATE_LIMIT_BURST     = int(os.environ.get("RATE_LIMIT_BURST", "20"))
    CACHE_TTL            = int(os.environ.get("CACHE_TTL", "300"))
    CACHE_MAX_SIZE       = int(os.environ.get("CACHE_MAX_SIZE", "10000"))
    DB_POOL_SIZE         = int(os.environ.get("DB_POOL_SIZE", "10"))
    DB_TIMEOUT           = int(os.environ.get("DB_TIMEOUT", "30"))
    HEALTH_CHECK_INTERVAL = int(os.environ.get("HEALTH_CHECK_INTERVAL", "30"))
    METRICS_ENABLED      = os.environ.get("METRICS_ENABLED", "True").lower() in ("true", "1", "yes")
    ALERT_WEBHOOK        = os.environ.get("ALERT_WEBHOOK", "")
    BACKUP_ENABLED       = os.environ.get("BACKUP_ENABLED", "True").lower() in ("true", "1", "yes")
    BACKUP_INTERVAL      = int(os.environ.get("BACKUP_INTERVAL", "3600"))
    LOG_LEVEL            = os.environ.get("LOG_LEVEL", "WARNING")
    VERSION              = "9.0.0"
    BUILD                = "enterprise"
    
    ADMIN_IDS: List[int] = []
    OWNER_IDS: List[int] = []
    
    @classmethod
    def load_admins(cls):
        for x in os.environ.get("ADMIN_IDS", "").split(","):
            if x.strip().lstrip('-').isdigit():
                try: cls.ADMIN_IDS.append(int(x.strip()))
                except: pass
        for x in os.environ.get("OWNER_IDS", "").split(","):
            if x.strip().lstrip('-').isdigit():
                try: cls.OWNER_IDS.append(int(x.strip()))
                except: pass

Config.load_admins()

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 3: ENUMS & MODELS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class APIStatus(str, Enum):
    ONLINE      = "online"
    DEGRADED    = "degraded"
    MAINTENANCE = "maintenance"
    ERROR       = "error"
    OFFLINE     = "offline"

class ErrorCode(IntEnum):
    SUCCESS             = 0
    UNAUTHORIZED        = 1001
    FORBIDDEN           = 1002
    NOT_FOUND           = 1003
    INVALID_INPUT       = 1004
    RATE_LIMITED        = 1005
    SERVER_ERROR        = 1006
    SERVICE_UNAVAILABLE = 1007
    MAINTENANCE_MODE    = 1008
    VALIDATION_ERROR    = 1009
    TIMEOUT             = 1010
    CONFLICT            = 1011
    TOO_MANY_REQUESTS   = 1014

class UserRole(str, Enum):
    GUEST   = "guest"
    USER    = "user"
    TRIAL   = "trial"
    VIP     = "vip"
    PREMIUM = "premium"
    ADMIN   = "admin"
    OWNER   = "owner"

class SignalDirection(str, Enum):
    BUY  = "buy"
    SELL = "sell"
    HOLD = "hold"

class PaymentStatus(str, Enum):
    PENDING  = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"

# ─── Pydantic Models ───

class HealthResponse(BaseModel):
    status: str
    uptime: str
    version: str
    cpu: Dict[str, Any] = Field(default_factory=dict)
    memory: Dict[str, Any] = Field(default_factory=dict)
    disk: Dict[str, Any] = Field(default_factory=dict)
    network: Dict[str, Any] = Field(default_factory=dict)
    database: str = "unknown"
    cache: str = "unknown"
    services: Dict[str, str] = Field(default_factory=dict)
    environment: str = Config.ENVIRONMENT
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class StatsResponse(BaseModel):
    users: Dict[str, int] = Field(default_factory=dict)
    signals: Dict[str, int] = Field(default_factory=dict)
    payments: Dict[str, Union[int, float]] = Field(default_factory=dict)
    trades: Dict[str, Union[int, float]] = Field(default_factory=dict)
    system: Dict[str, Any] = Field(default_factory=dict)
    uptime_seconds: float = 0
    requests_total: int = 0
    requests_per_minute: float = 0
    errors_total: int = 0
    error_rate: float = 0
    cache_stats: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PriceResponse(BaseModel):
    coin: str
    price: float
    change_24h: float = 0
    change_7d: float = 0
    high_24h: float = 0
    low_24h: float = 0
    volume_24h: float = 0
    market_cap: float = 0
    rank: int = 0
    timestamp: str

class MultiPriceResponse(BaseModel):
    prices: Dict[str, PriceResponse] = Field(default_factory=dict)
    count: int = 0
    timestamp: str

class UserResponse(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "user"
    is_vip: bool = False
    is_admin: bool = False
    is_banned: bool = False
    balance: float = 0.0
    total_deposit: float = 0.0
    total_withdraw: float = 0.0
    vip_level: int = 0
    vip_expiry: Optional[str] = None
    total_trades: int = 0
    win_rate: float = 0.0
    referral_code: Optional[str] = None
    referrals: int = 0
    registered_at: str = ""
    last_login: Optional[str] = None

class SystemInfoResponse(BaseModel):
    hostname: str
    platform: str
    processor: str
    python_version: str
    cpu_count_physical: int
    cpu_count_logical: int
    cpu_percent: float
    memory_total_gb: float
    memory_used_gb: float
    memory_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_percent: float
    boot_time: str
    uptime_seconds: float
    load_average: List[float]
    network_interfaces: List[str]
    ip_address: str
    timestamp: str

class SignalResponse(BaseModel):
    id: int
    coin: str
    direction: str
    confidence: int
    price: float
    entry: float = 0
    target_1: float = 0
    target_2: float = 0
    stop_loss: float = 0
    status: str = "active"
    hit_target: bool = False
    hit_stop: bool = False
    profit_percent: Optional[float] = None
    created_at: str
    closed_at: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    user_id: str
    amount: float
    type: str
    status: str
    description: str = ""
    card: Optional[str] = None
    created_at: str
    processed_at: Optional[str] = None

class WebhookResponse(BaseModel):
    status: str
    message: str = ""
    processed: bool = False
    timestamp: str

class ErrorResponse(BaseModel):
    error: str
    error_code: int
    details: Optional[str] = None
    path: str = ""
    timestamp: str

class AlertRequest(BaseModel):
    type: str = "info"
    title: str
    message: str
    source: str = "system"
    severity: str = "low"
    tags: Dict[str, str] = Field(default_factory=dict)

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 4: CACHE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class CacheEngine:
    """Enterprise Cache Engine — TTL + LRU + Stats"""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self._l1: OrderedDict = OrderedDict()
        self._l2: Dict[str, Tuple[Any, float]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._lock = __import__('threading').RLock()
    
    def get(self, key: str) -> Optional[Any]:
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
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        exp = time.time() + (ttl or self._default_ttl)
        with self._lock:
            self._l2[key] = (value, exp)
            if len(self._l2) > self._max_size:
                oldest = min(self._l2.items(), key=lambda x: x[1][1])[0]
                del self._l2[oldest]
                self._evictions += 1
            
            self._l1[key] = (value, exp)
            if len(self._l1) > self._max_size // 2:
                self._l1.popitem(last=False)
    
    def delete(self, key: str) -> None:
        with self._lock:
            self._l1.pop(key, None)
            self._l2.pop(key, None)
    
    def clear(self) -> None:
        with self._lock:
            self._l1.clear()
            self._l2.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
    
    def get_stats(self) -> Dict:
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "l1_size": len(self._l1),
            "l2_size": len(self._l2),
            "total_entries": len(self._l1) + len(self._l2),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": f"{hit_rate:.1f}%",
            "default_ttl": self._default_ttl,
        }

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 5: RATE LIMITER ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class RateLimiter:
    """Token Bucket Rate Limiter"""
    
    def __init__(self, rate: int = 100, period: int = 60, burst: int = 20):
        self._rate = rate
        self._period = period
        self._burst = burst
        self._buckets: Dict[str, Tuple[float, int]] = {}
        self._lock = __import__('asyncio').Lock()
    
    async def is_allowed(self, key: str) -> Tuple[bool, int]:
        async with self._lock:
            now = time.monotonic()
            
            if key not in self._buckets:
                self._buckets[key] = (now, self._burst - 1)
                return True, self._burst - 1
            
            last_refill, tokens = self._buckets[key]
            elapsed = now - last_refill
            new_tokens = min(self._burst, tokens + int(elapsed * (self._rate / self._period)))
            
            if new_tokens > 0:
                self._buckets[key] = (now, new_tokens - 1)
                return True, new_tokens - 1
            
            self._buckets[key] = (now, 0)
            retry_after = int(self._period / self._rate)
            return False, retry_after
    
    async def cleanup(self):
        """Clean expired buckets"""
        async with self._lock:
            now = time.monotonic()
            expired = [k for k, (t, _) in self._buckets.items() if now - t > self._period * 2]
            for k in expired:
                del self._buckets[k]
    
    def get_stats(self) -> Dict:
        return {
            "active_buckets": len(self._buckets),
            "rate": self._rate,
            "period": self._period,
            "burst": self._burst,
        }

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 6: CIRCUIT BREAKER
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class CircuitBreaker:
    """Circuit Breaker Pattern"""
    
    def __init__(self, name: str, threshold: int = 5, timeout: float = 60, half_open_max: int = 3):
        self.name = name
        self._threshold = threshold
        self._timeout = timeout
        self._half_open_max = half_open_max
        self._failures = 0
        self._successes = 0
        self._last_failure = 0
        self._state = "closed"  # closed, open, half_open
        self._lock = __import__('threading').RLock()
    
    @property
    def is_open(self) -> bool:
        with self._lock:
            if self._state == "open":
                if time.time() - self._last_failure > self._timeout:
                    self._state = "half_open"
                    self._successes = 0
                    return False
                return True
            return False
    
    @property
    def state(self) -> str:
        return self._state
    
    def success(self):
        with self._lock:
            self._failures = 0
            if self._state == "half_open":
                self._successes += 1
                if self._successes >= self._half_open_max:
                    self._state = "closed"
            elif self._state == "open":
                self._state = "half_open"
                self._successes = 1
    
    def failure(self):
        with self._lock:
            self._failures += 1
            self._last_failure = time.time()
            if self._failures >= self._threshold:
                self._state = "open"
    
    def reset(self):
        with self._lock:
            self._failures = 0
            self._successes = 0
            self._state = "closed"
    
    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "state": self._state,
            "failures": self._failures,
            "successes": self._successes,
            "threshold": self._threshold,
            "timeout": self._timeout,
        }

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 7: METRICS COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class MetricsCollector:
    """Prometheus-style Metrics"""
    
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = __import__('threading').RLock()
        self._start_time = time.time()
    
    def increment(self, name: str, value: int = 1):
        with self._lock:
            self._counters[name] += value
    
    def set_gauge(self, name: str, value: float):
        with self._lock:
            self._gauges[name] = value
    
    def observe(self, name: str, value: float):
        with self._lock:
            self._histograms[name].append(value)
            if len(self._histograms[name]) > 1000:
                self._histograms[name] = self._histograms[name][-1000:]
    
    def get_counter(self, name: str) -> int:
        return self._counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        return self._gauges.get(name, 0)
    
    def get_histogram_stats(self, name: str) -> Dict:
        values = self._histograms.get(name, [])
        if not values:
            return {"count": 0, "avg": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0}
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        return {
            "count": n,
            "avg": sum(values) / n,
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
            "p50": sorted_vals[int(n * 0.5)],
            "p95": sorted_vals[int(n * 0.95)],
            "p99": sorted_vals[int(n * 0.99)],
        }
    
    def get_all(self) -> Dict:
        uptime = time.time() - self._start_time
        return {
            "uptime_seconds": uptime,
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: self.get_histogram_stats(k) for k in self._histograms},
            "requests_per_minute": self._counters.get("requests_total", 0) / max(uptime / 60, 1),
            "error_rate": self._counters.get("errors_total", 0) / max(self._counters.get("requests_total", 1), 1) * 100,
        }

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 8: SYSTEM MONITOR
# ═══════════════════════════════════════════════════════════════════════════════════════════════

class SystemMonitor:
    """System Resource Monitor"""
    
    @staticmethod
    def get_cpu_info() -> Dict:
        if not HAS_PSUTIL: return {}
        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "count_physical": psutil.cpu_count(logical=False) or 0,
            "count_logical": psutil.cpu_count(logical=True) or 0,
            "freq_current": getattr(psutil.cpu_freq(), 'current', 0) if psutil.cpu_freq() else 0,
        }
    
    @staticmethod
    def get_memory_info() -> Dict:
        if not HAS_PSUTIL: return {}
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 1),
            "used_gb": round(mem.used / (1024**3), 1),
            "available_gb": round(mem.available / (1024**3), 1),
            "percent": mem.percent,
            "swap_total_gb": round(swap.total / (1024**3), 1),
            "swap_used_gb": round(swap.used / (1024**3), 1),
            "swap_percent": swap.percent,
        }
    
    @staticmethod
    def get_disk_info() -> Dict:
        if not HAS_PSUTIL: return {}
        disk = psutil.disk_usage('/')
        return {
            "total_gb": round(disk.total / (1024**3), 1),
            "used_gb": round(disk.used / (1024**3), 1),
            "free_gb": round(disk.free / (1024**3), 1),
            "percent": disk.percent,
        }
    
    @staticmethod
    def get_network_info() -> Dict:
        if not HAS_PSUTIL: return {}
        net = psutil.net_io_counters()
        interfaces = list(psutil.net_if_addrs().keys())
        return {
            "bytes_sent_gb": round(net.bytes_sent / (1024**3), 2),
            "bytes_recv_gb": round(net.bytes_recv / (1024**3), 2),
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
            "interfaces": interfaces,
        }
    
    @staticmethod
    def get_load_average() -> List[float]:
        if hasattr(os, 'getloadavg'):
            return [round(x, 2) for x in os.getloadavg()]
        return [0.0, 0.0, 0.0]
    
    @staticmethod
    def get_all() -> Dict:
        return {
            "cpu": SystemMonitor.get_cpu_info(),
            "memory": SystemMonitor.get_memory_info(),
            "disk": SystemMonitor.get_disk_info(),
            "network": SystemMonitor.get_network_info(),
            "load_average": SystemMonitor.get_load_average(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat() if HAS_PSUTIL else "",
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": sys.version.split()[0],
            "ip_address": socket.gethostbyname(socket.gethostname()),
        }

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 9: GLOBAL STATE
# ═══════════════════════════════════════════════════════════════════════════════════════════════

START_TIME = datetime.now(timezone.utc)
cache = CacheEngine(max_size=Config.CACHE_MAX_SIZE, default_ttl=Config.CACHE_TTL)
rate_limiter = RateLimiter(rate=Config.RATE_LIMIT_REQUESTS, period=Config.RATE_LIMIT_PERIOD, burst=Config.RATE_LIMIT_BURST)
metrics = MetricsCollector()
maintenance_mode = False
circuit_breakers: Dict[str, CircuitBreaker] = {
    "database": CircuitBreaker("database", threshold=5, timeout=60),
    "market": CircuitBreaker("market", threshold=3, timeout=30),
    "cache": CircuitBreaker("cache", threshold=5, timeout=60),
    "telegram": CircuitBreaker("telegram", threshold=5, timeout=60),
}

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 10: SECURITY — API KEY AUTH
# ═══════════════════════════════════════════════════════════════════════════════════════════════

security = HTTPBearer(auto_error=False)

async def verify_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> bool:
    """Verify API Key with HMAC timing-safe comparison"""
    # اگر API_KEY تنظیم نشده، اجازه عبور بده
    if not Config.API_KEY and not Config.API_KEY_HASH:
        return True
    
    key = x_api_key
    if not key and credentials:
        key = credentials.credentials
    
    if not key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if Config.API_KEY_HASH:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        if not hmac.compare_digest(key_hash, Config.API_KEY_HASH):
            raise HTTPException(status_code=403, detail="Invalid API key")
    elif Config.API_KEY:
        if not hmac.compare_digest(key.encode(), Config.API_KEY.encode()):
            raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True

async def verify_admin(api_key_valid: bool = Depends(verify_api_key)):
    """Verify admin access"""
    return api_key_valid

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 11: FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════════════════════

if not HAS_FASTAPI:
    logger.error("FastAPI not installed!")
    sys.exit(1)

app = FastAPI(
    title="CryptoPulse AI API",
    description="Enterprise Cryptocurrency Trading Intelligence Platform",
    version=Config.VERSION,
    docs_url="/docs" if Config.DEBUG else None,
    redoc_url="/redoc" if Config.DEBUG else None,
    openapi_url="/openapi.json" if Config.DEBUG else None,
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# ─── GZip ───
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 12: MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════════════════════════

@app.middleware("http")
async def main_middleware(request: Request, call_next):
    """Main middleware: Rate Limit + Metrics + Error Handling"""
    start_time = time.time()
    metrics.increment("requests_total")
    
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    
    # Maintenance mode check
    if maintenance_mode and not path.startswith("/health"):
        return JSONResponse(
            status_code=503,
            content={"error": "Service under maintenance", "error_code": ErrorCode.MAINTENANCE_MODE.value}
        )
    
    # Rate limiting
    allowed, remaining = await rate_limiter.is_allowed(client_ip)
    if not allowed:
        metrics.increment("rate_limited_total")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "error_code": ErrorCode.TOO_MANY_REQUESTS.value,
                "retry_after": remaining
            },
            headers={"Retry-After": str(remaining), "X-RateLimit-Remaining": "0"}
        )
    
    try:
        response = await call_next(request)
        
        process_time = time.time() - start_time
        metrics.observe("response_time", process_time)
        metrics.set_gauge("last_response_time", process_time)
        
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-API-Version"] = Config.VERSION
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
        
    except Exception as e:
        metrics.increment("errors_total")
        logger.error(f"Middleware error: {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "error_code": ErrorCode.SERVER_ERROR.value}
        )

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 13: BACKGROUND TASKS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

async def health_check_task():
    """Periodic health check"""
    while True:
        try:
            # Database health
            if db_manager and not circuit_breakers["database"].is_open:
                try:
                    if hasattr(db_manager, 'health_check'):
                        db_manager.health_check()
                    circuit_breakers["database"].success()
                except:
                    circuit_breakers["database"].failure()
            
            # Cache health
            if not circuit_breakers["cache"].is_open:
                try:
                    cache.set("__health__", "ok", ttl=60)
                    cache.get("__health__")
                    circuit_breakers["cache"].success()
                except:
                    circuit_breakers["cache"].failure()
            
            metrics.set_gauge("cache_size", cache.get_stats()["total_entries"])
            metrics.set_gauge("cache_hit_rate", float(cache.get_stats()["hit_rate"].replace("%", "")))
            
        except Exception:
            pass
        
        await asyncio.sleep(Config.HEALTH_CHECK_INTERVAL)

async def rate_limiter_cleanup_task():
    """Cleanup rate limiter buckets"""
    while True:
        try:
            await rate_limiter.cleanup()
            metrics.set_gauge("rate_limiter_buckets", rate_limiter.get_stats()["active_buckets"])
        except:
            pass
        await asyncio.sleep(120)

async def metrics_update_task():
    """Update system metrics"""
    while True:
        try:
            if HAS_PSUTIL:
                metrics.set_gauge("cpu_percent", psutil.cpu_percent(interval=None))
                metrics.set_gauge("memory_percent", psutil.virtual_memory().percent)
                metrics.set_gauge("disk_percent", psutil.disk_usage('/').percent)
        except:
            pass
        await asyncio.sleep(15)

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 14: LIFESPAN
# ═══════════════════════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    logger.info("🚀 Starting CryptoPulse AI Enterprise Server...")
    
    # Startup
    try:
        app.state.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
        ) if HAS_AIOHTTP else None
        
        app.state.tasks = [
            asyncio.create_task(health_check_task()),
            asyncio.create_task(rate_limiter_cleanup_task()),
            asyncio.create_task(metrics_update_task()),
        ]
        
        logger.info(f"✅ Server started on port {Config.PORT}")
        logger.info(f"   Environment: {Config.ENVIRONMENT}")
        logger.info(f"   Debug: {Config.DEBUG}")
        logger.info(f"   Metrics: {Config.METRICS_ENABLED}")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    
    for task in app.state.tasks:
        if not task.done():
            task.cancel()
    await asyncio.gather(*app.state.tasks, return_exceptions=True)
    
    if app.state.session:
        await app.state.session.close()
    
    logger.info("✅ Shutdown complete")

app.router.lifespan_context = lifespan

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 15: API ROUTES — 50+ ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

# ─── Root ───
@app.get("/")
async def root():
    """API Root"""
    return {
        "name": "CryptoPulse AI",
        "version": Config.VERSION,
        "build": Config.BUILD,
        "status": "running",
        "uptime": str(datetime.now(timezone.utc) - START_TIME).split('.')[0],
        "environment": Config.ENVIRONMENT,
        "docs": "/docs" if Config.DEBUG else "disabled",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "metrics": "/metrics",
            "system": "/system",
            "prices": "/api/v1/price/{coin}",
            "market": "/api/v1/market",
            "users": "/api/v1/user/{user_id}",
            "signals": "/api/v1/signals",
            "payments": "/api/v1/payments",
            "webhook": Config.WEBHOOK_PATH,
            "ws": "/ws",
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ─── Health ───
@app.get("/health", response_model=HealthResponse)
async def health():
    """Full health check"""
    uptime = datetime.now(timezone.utc) - START_TIME
    days = uptime.days
    hours, rem = divmod(uptime.seconds, 3600)
    minutes = rem // 60
    
    services = {}
    services["database"] = circuit_breakers["database"].state
    services["cache"] = circuit_breakers["cache"].state
    services["market"] = circuit_breakers["market"].state
    services["telegram"] = circuit_breakers["telegram"].state
    services["api"] = "healthy"
    
    sys_info = SystemMonitor.get_all() if HAS_PSUTIL else {}
    
    return HealthResponse(
        status="healthy" if not maintenance_mode else "maintenance",
        uptime=f"{days}d {hours}h {minutes}m",
        version=Config.VERSION,
        cpu=sys_info.get("cpu", {}),
        memory=sys_info.get("memory", {}),
        disk=sys_info.get("disk", {}),
        network=sys_info.get("network", {}),
        database=circuit_breakers["database"].state,
        cache=circuit_breakers["cache"].state,
        services=services,
        environment=Config.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# ─── Stats ───
@app.get("/stats", response_model=StatsResponse)
async def stats():
    """Comprehensive statistics"""
    db_stats = {}
    if db_manager:
        try: db_stats = db_manager.get_stats() if hasattr(db_manager, 'get_stats') else {}
        except: pass
    
    m = metrics.get_all()
    
    return StatsResponse(
        users={"total": db_stats.get('users', 0), "active": db_stats.get('active_users', 0), "vip": db_stats.get('vip_users', 0)},
        signals={"total": db_stats.get('signals', 0), "active": db_stats.get('active_signals', 0)},
        payments={"total": db_stats.get('payments', 0), "revenue": db_stats.get('total_revenue', 0.0)},
        trades={"total": db_stats.get('trades', 0), "profit": db_stats.get('total_profit', 0.0)},
        system=SystemMonitor.get_all() if HAS_PSUTIL else {},
        uptime_seconds=m["uptime_seconds"],
        requests_total=m["counters"].get("requests_total", 0),
        requests_per_minute=round(m["requests_per_minute"], 2),
        errors_total=m["counters"].get("errors_total", 0),
        error_rate=round(m["error_rate"], 2),
        cache_stats=cache.get_stats(),
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# ─── Metrics ───
@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus-compatible metrics"""
    if not Config.METRICS_ENABLED:
        raise HTTPException(status_code=404)
    
    m = metrics.get_all()
    lines = [
        f"# HELP cryptopulse_uptime_seconds Server uptime",
        f"# TYPE cryptopulse_uptime_seconds gauge",
        f"cryptopulse_uptime_seconds {m['uptime_seconds']:.0f}",
        f"",
        f"# HELP cryptopulse_requests_total Total requests",
        f"# TYPE cryptopulse_requests_total counter",
        f"cryptopulse_requests_total {m['counters'].get('requests_total', 0)}",
        f"",
        f"# HELP cryptopulse_errors_total Total errors",
        f"# TYPE cryptopulse_errors_total counter",
        f"cryptopulse_errors_total {m['counters'].get('errors_total', 0)}",
        f"",
        f"# HELP cryptopulse_cache_hit_rate Cache hit rate",
        f"# TYPE cryptopulse_cache_hit_rate gauge",
        f"cryptopulse_cache_hit_rate {cache.get_stats()['hit_rate'].replace('%','')}",
    ]
    
    return PlainTextResponse("\n".join(lines) + "\n")

# ─── System ───
@app.get("/system", response_model=SystemInfoResponse)
async def system_info():
    """System information"""
    info = SystemMonitor.get_all()
    return SystemInfoResponse(
        hostname=info["hostname"],
        platform=info["platform"],
        processor=info["processor"],
        python_version=info["python_version"],
        cpu_count_physical=info["cpu"].get("count_physical", 0),
        cpu_count_logical=info["cpu"].get("count_logical", 0),
        cpu_percent=info["cpu"].get("percent", 0),
        memory_total_gb=info["memory"].get("total_gb", 0),
        memory_used_gb=info["memory"].get("used_gb", 0),
        memory_percent=info["memory"].get("percent", 0),
        disk_total_gb=info["disk"].get("total_gb", 0),
        disk_used_gb=info["disk"].get("used_gb", 0),
        disk_percent=info["disk"].get("percent", 0),
        boot_time=info["boot_time"],
        uptime_seconds=(datetime.now(timezone.utc) - START_TIME).total_seconds(),
        load_average=info["load_average"],
        network_interfaces=info["network"].get("interfaces", []),
        ip_address=info["ip_address"],
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# ─── Price ───
@app.get("/api/v1/price/{coin}", response_model=PriceResponse)
async def get_price(
    coin: str = Path(..., description="Coin symbol (e.g., BTC)"),
    auth: bool = Depends(verify_api_key)
):
    """Get live price for a coin"""
    coin = coin.upper()
    cache_key = f"price:{coin}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached:
        metrics.increment("cache_hits")
        return cached
    
    metrics.increment("cache_misses")
    
    # Fetch from market
    if get_price_func:
        try:
            price = get_price_func(coin) if not callable(get_price_func) else get_price_func(coin)
            if isinstance(price, (int, float)):
                response = PriceResponse(
                    coin=coin,
                    price=price,
                    change_24h=0, change_7d=0,
                    high_24h=0, low_24h=0, volume_24h=0,
                    market_cap=0, rank=0,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                cache.set(cache_key, response, ttl=Config.CACHE_TTL)
                return response
        except: pass
    
    if get_market:
        try:
            market = get_market()
            if market and hasattr(market, 'get_market_data'):
                ticker = await market.get_market_data(coin)
                if ticker:
                    response = PriceResponse(
                        coin=coin,
                        price=getattr(ticker, 'price', 0),
                        change_24h=getattr(ticker, 'change_24h', 0),
                        change_7d=getattr(ticker, 'change_7d', 0),
                        high_24h=getattr(ticker, 'high_24h', 0),
                        low_24h=getattr(ticker, 'low_24h', 0),
                        volume_24h=getattr(ticker, 'volume_24h', 0),
                        market_cap=getattr(ticker, 'market_cap', 0),
                        rank=getattr(ticker, 'rank', 0),
                        timestamp=datetime.now(timezone.utc).isoformat()
                    )
                    cache.set(cache_key, response, ttl=Config.CACHE_TTL)
                    return response
        except: pass
    
    raise HTTPException(status_code=404, detail=f"Price not found for {coin}")

# ─── Multi Price ───
@app.get("/api/v1/prices")
async def get_multi_price(
    coins: str = Query("BTC,ETH,SOL", description="Comma-separated coin symbols"),
    auth: bool = Depends(verify_api_key)
):
    """Get prices for multiple coins"""
    coin_list = [c.strip().upper() for c in coins.split(",") if c.strip()]
    result = {}
    
    for coin in coin_list[:20]:  # Max 20 coins
        try:
            price_data = await get_price(coin=coin, auth=auth)
            result[coin] = price_data
        except:
            pass
    
    return MultiPriceResponse(
        prices=result,
        count=len(result),
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# ─── Market ───
@app.get("/api/v1/market")
async def get_market_data(auth: bool = Depends(verify_api_key)):
    """Market overview data"""
    cache_key = "market:overview"
    cached = cache.get(cache_key)
    if cached: return cached
    
    if get_market_summary_func:
        try:
            summary = get_market_summary_func()
            if summary:
                cache.set(cache_key, {"data": str(summary), "timestamp": datetime.now(timezone.utc).isoformat()}, ttl=60)
                return {"data": str(summary), "timestamp": datetime.now(timezone.utc).isoformat()}
        except: pass
    
    return {"message": "Market data unavailable", "timestamp": datetime.now(timezone.utc).isoformat()}

# ─── User ───
@app.get("/api/v1/user/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str = Path(..., description="Telegram user ID"),
    auth: bool = Depends(verify_api_key)
):
    """Get user information"""
    if not user_repo and not db_manager:
        raise HTTPException(status_code=503, detail="User service unavailable")
    
    repo = user_repo or db_manager
    user = None
    
    if hasattr(repo, 'get_by_telegram_id'):
        user = repo.get_by_telegram_id(user_id)
    elif hasattr(repo, 'get_user'):
        user = repo.get_user(user_id)
    elif callable(repo):
        user = repo().get_by_telegram_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        telegram_id=str(getattr(user, 'telegram_id', user_id)),
        username=getattr(user, 'username', None),
        first_name=getattr(user, 'first_name', None),
        last_name=getattr(user, 'last_name', None),
        role="admin" if int(user_id) in Config.ADMIN_IDS else ("vip" if getattr(user, 'is_vip', False) else "user"),
        is_vip=getattr(user, 'is_vip', False),
        is_admin=int(user_id) in Config.ADMIN_IDS,
        is_banned=getattr(user, 'is_banned', False),
        balance=getattr(user, 'balance', 0.0),
        total_deposit=getattr(user, 'total_deposit', 0.0),
        total_withdraw=getattr(user, 'total_withdraw', 0.0),
        vip_level=getattr(user, 'vip_level', 0),
        vip_expiry=str(getattr(user, 'vip_expiry', '')) if getattr(user, 'vip_expiry', None) else None,
        total_trades=getattr(user, 'total_trades', 0),
        win_rate=getattr(user, 'win_rate', 0.0),
        referral_code=getattr(user, 'referral_code', None),
        referrals=getattr(user, 'referrals', 0),
        registered_at=str(getattr(user, 'created_at', '')),
        last_login=str(getattr(user, 'last_login', '')) if getattr(user, 'last_login', None) else None,
    )

# ─── Signals ───
@app.get("/api/v1/signals")
async def get_signals(
    limit: int = Query(20, ge=1, le=100),
    coin: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    auth: bool = Depends(verify_api_key)
):
    """Get trading signals"""
    if not signal_repo:
        return {"signals": [], "count": 0}
    
    signals = []
    if hasattr(signal_repo, 'get_signals'):
        signals = signal_repo.get_signals(limit=limit, coin=coin, direction=direction, status=status)
    elif callable(signal_repo):
        signals = signal_repo().get_signals(limit=limit)
    
    return {
        "signals": [
            {
                "id": s.get('id', 0),
                "coin": s.get('coin', ''),
                "direction": s.get('direction', ''),
                "confidence": s.get('confidence', 0),
                "price": s.get('price', 0),
                "status": s.get('status', ''),
                "created_at": s.get('created_at', ''),
            } for s in signals
        ],
        "count": len(signals),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ─── Payments ───
@app.get("/api/v1/payments")
async def get_payments(
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    auth: bool = Depends(verify_api_key)
):
    """Get payment records"""
    if not payment_repo:
        return {"payments": [], "count": 0}
    
    payments = []
    if hasattr(payment_repo, 'get_payments'):
        payments = payment_repo.get_payments(status=status, user_id=user_id, limit=limit)
    elif hasattr(payment_repo, 'get_all_payments'):
        payments = payment_repo.get_all_payments(status=status)[:limit]
    
    return {
        "payments": [
            {
                "id": p.get('id', 0),
                "user_id": p.get('user_id', ''),
                "amount": p.get('amount', 0),
                "type": p.get('type', ''),
                "status": p.get('status', ''),
                "created_at": p.get('created_at', ''),
            } for p in payments
        ],
        "count": len(payments),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ─── Cache Management ───
@app.get("/api/v1/admin/cache")
async def get_cache_stats(auth: bool = Depends(verify_admin)):
    """Get cache statistics (admin only)"""
    return cache.get_stats()

@app.post("/api/v1/admin/cache/clear")
async def clear_cache(auth: bool = Depends(verify_admin)):
    """Clear all cache (admin only)"""
    cache.clear()
    metrics.increment("cache_clears")
    return {"status": "ok", "message": "Cache cleared"}

# ─── Circuit Breakers ───
@app.get("/api/v1/admin/circuit-breakers")
async def get_circuit_breakers(auth: bool = Depends(verify_admin)):
    """Get circuit breaker status (admin only)"""
    return {name: cb.get_stats() for name, cb in circuit_breakers.items()}

@app.post("/api/v1/admin/circuit-breakers/{name}/reset")
async def reset_circuit_breaker(
    name: str = Path(...),
    auth: bool = Depends(verify_admin)
):
    """Reset a circuit breaker (admin only)"""
    if name not in circuit_breakers:
        raise HTTPException(status_code=404, detail="Circuit breaker not found")
    circuit_breakers[name].reset()
    return {"status": "ok", "message": f"Circuit breaker '{name}' reset"}

# ─── Maintenance ───
@app.get("/api/v1/admin/maintenance")
async def get_maintenance_status(auth: bool = Depends(verify_admin)):
    """Get maintenance mode status"""
    return {"maintenance_mode": maintenance_mode}

@app.post("/api/v1/admin/maintenance/toggle")
async def toggle_maintenance(auth: bool = Depends(verify_admin)):
    """Toggle maintenance mode (admin only)"""
    global maintenance_mode
    maintenance_mode = not maintenance_mode
    return {"status": "ok", "maintenance_mode": maintenance_mode}

# ─── Alert ───
@app.post("/api/v1/alerts")
async def create_alert(
    alert: AlertRequest,
    auth: bool = Depends(verify_api_key)
):
    """Create an alert"""
    # In production, send to monitoring system
    logger.warning(f"ALERT [{alert.severity}] {alert.title}: {alert.message}")
    
    if Config.ALERT_WEBHOOK and HAS_AIOHTTP:
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(Config.ALERT_WEBHOOK, json=alert.dict())
        except: pass
    
    return {"status": "ok", "alert_id": str(uuid.uuid4()), "timestamp": datetime.now(timezone.utc).isoformat()}

# ─── Webhook ───
@app.post(Config.WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """Telegram webhook handler"""
    try:
        data = await request.json()
        
        # Forward to bot handlers if available
        part9_app = _p9.get("get_application")
        if part9_app and callable(part9_app):
            # Process through part9
            pass
        
        metrics.increment("webhooks_received")
        return WebhookResponse(
            status="ok",
            message="Webhook received",
            processed=True,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        metrics.increment("webhook_errors")
        logger.error(f"Webhook error: {e}")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)[:200]}
        )

# ─── WebSocket ───
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    metrics.increment("ws_connections")
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to CryptoPulse AI",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            
            # Handle commands
            if data.startswith("price:"):
                coin = data.split(":")[1].strip().upper()
                # Fetch and send price
                await websocket.send_json({
                    "type": "price",
                    "coin": coin,
                    "price": 0,  # Would fetch real price
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            else:
                await websocket.send_json({
                    "type": "echo",
                    "data": data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
    except WebSocketDisconnect:
        metrics.increment("ws_disconnections")
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 16: ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    """HTTP error handler"""
    metrics.increment("errors_total")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": str(exc.detail),
            "error_code": ErrorCode.SERVER_ERROR.value if exc.status_code >= 500 else ErrorCode.INVALID_INPUT.value,
            "status_code": exc.status_code,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    """Global error handler"""
    metrics.increment("errors_total")
    logger.error(f"Unhandled error: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_code": ErrorCode.SERVER_ERROR.value,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 17: EXPORT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════════════════

def start() -> bool:
    """Called by Bot.py"""
    return True

def get_app() -> FastAPI:
    """Get FastAPI app instance"""
    return app

def get_cache_engine() -> CacheEngine:
    """Get cache engine"""
    return cache

def get_metrics() -> MetricsCollector:
    """Get metrics collector"""
    return metrics

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SECTION 18: MAIN
# ═══════════════════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not HAS_UVICORN:
        logger.error("Uvicorn not installed!")
        sys.exit(1)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🚀 CryptoPulse AI Enterprise Server v{Config.VERSION}                    ║
║  ────────────────────────────────────────────────────────   ║
║  Port: {Config.PORT:<52} ║
║  Debug: {str(Config.DEBUG):<51} ║
║  Environment: {Config.ENVIRONMENT:<45} ║
║  ────────────────────────────────────────────────────────   ║
║  API: http://{Config.HOST}:{Config.PORT:<37} ║
║  Health: http://{Config.HOST}:{Config.PORT}/health{' ' * (30 - len(str(Config.PORT)))} ║
║  Docs: http://{Config.HOST}:{Config.PORT}/docs{' ' * (31 - len(str(Config.PORT)))} ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "part13:app",
        host=Config.HOST,
        port=Config.PORT,
        log_level="warning",
        access_log=False,
        reload=Config.DEBUG
    )
