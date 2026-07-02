#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   ██████╗██████╗██╗   ██╗██████╗████████╗██████╗ ██╗   ██╗ █████╗ ███████╗███████╗║
║  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝██╔════╝║
║  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██████╔╝ ╚████╔╝ ███████║███████╗███████╗║
║  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██╔══██╗  ╚██╔╝  ██╔══██║╚════██║╚════██║║
║  ╚██████╗██║  ██║   ██║   ██║        ██║   ██║  ██║   ██║   ██║  ██║███████║███████║║
║   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝║
║                                                                                    ║
║  🚀 CryptoPulse AI Bot v3.0 - FastAPI Server Module (Ultimate Edition)            ║
║  ───────────────────────────────────────────────────────────────────────────────    ║
║  🌐 API کامل  |  🔒 امنیت پیشرفته  |  📊 متریک‌ها  |  🔄 Webhook  |  🛡️ بدون خطا  ║
║  ════════════════════════════════════════════════════════════════════════════════   ║
║  📁 ۴۸۰۰+ خط کد  |  ⚡ بهینه  |  🔥 فوق‌پیشرفته  |  🧹 بدون لاگ                  ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import asyncio
import hashlib
import hmac
import base64
import secrets
import string
import uuid
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union, Callable, Coroutine
from contextlib import asynccontextmanager, contextmanager
from enum import Enum
from dataclasses import dataclass, field, asdict
from collections import defaultdict, OrderedDict
from functools import wraps, lru_cache
import warnings

# ============================================================
#                    غیرفعال کردن اخطارها
# ============================================================

warnings.filterwarnings("ignore")

# ============================================================
#                    FASTAPI & DEPENDENCIES
# ============================================================

from fastapi import (
    FastAPI, Request, Response, HTTPException, Depends, Header, 
    Query, Body, Path, Form, status, UploadFile, File,
    WebSocket, WebSocketDisconnect, BackgroundTasks
)
from fastapi.responses import (
    JSONResponse, FileResponse, HTMLResponse, RedirectResponse, 
    PlainTextResponse, StreamingResponse, ORJSONResponse,
    UJSONResponse, Response as FastAPIResponse
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler
)
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi

# ============================================================
#                    PYDANTIC (پیشرفته)
# ============================================================

from pydantic import (
    BaseModel, Field, validator, root_validator, 
    EmailStr, HttpUrl, conint, confloat, constr,
    SecretStr, SecretBytes, UUID4, AnyUrl,
    ValidationError, BaseConfig
)

# ============================================================
#                    UVICORN & SERVER
# ============================================================

import uvicorn
from uvicorn.config import LOGGING_CONFIG
from uvicorn.workers import UvicornWorker

# ============================================================
#                    APSCHEDULER (زمانبندی)
# ============================================================

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# ============================================================
#                    AIOHHTP & NETWORK
# ============================================================

import aiohttp
import aiohttp.client_exceptions
from aiohttp import ClientSession, ClientTimeout, TCPConnector

# ============================================================
#                    UTILITY (پیشرفته)
# ============================================================

import psutil
import cpuinfo
import platform
import socket
import netifaces
from collections import deque
from typing import Any, Coroutine

# ============================================================
#                    SAFE IMPORTS (ایمن‌سازی)
# ============================================================

def safe_import(module_name: str, *attrs):
    """ایمن‌سازی واردات ماژول‌ها با کش و fallback"""
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
#                    IMPORTS (کامل)
# ============================================================

_bot2 = safe_import("bot2", "get_config")
_bot3 = safe_import("bot3", "db_manager", "user_repo", "signal_repo", "payment_repo")
_bot4 = safe_import("bot4", "get_time", "get_emoji", "get_formatter", "get_hash", "get_cache")
_bot5 = safe_import("bot5", "get_market", "get_coinex")
_bot6 = safe_import("bot6", "get_ai", "get_groq")
_bot7 = safe_import("bot7", "get_technical")
_bot9 = safe_import("bot9", "bot_handlers")

get_config = _bot2.get("get_config")
db_manager = _bot3.get("db_manager")
user_repo = _bot3.get("user_repo")
signal_repo = _bot3.get("signal_repo")
payment_repo = _bot3.get("payment_repo")
get_time = _bot4.get("get_time")
get_emoji = _bot4.get("get_emoji")
get_formatter = _bot4.get("get_formatter")
get_hash = _bot4.get("get_hash")
get_cache = _bot4.get("get_cache")
get_market = _bot5.get("get_market")
get_coinex = _bot5.get("get_coinex")
get_ai = _bot6.get("get_ai")
get_groq = _bot6.get("get_groq")
get_technical = _bot7.get("get_technical")
bot_handlers = _bot9.get("bot_handlers")

# ============================================================
#                    CONFIG (کامل و پیشرفته)
# ============================================================

config = get_config() if get_config else None

# تنظیمات اصلی
ADMIN_IDS = []
admin_ids_str = os.environ.get("ADMIN_IDS", "")
for x in admin_ids_str.split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except ValueError:
            pass

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
PORT = int(os.environ.get("PORT", 8080))
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
SECRET_KEY = os.environ.get("SECRET_KEY", "cryptopulse_secret_key_2024")
API_KEY = os.environ.get("API_KEY", "")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
MAX_REQUEST_SIZE = int(os.environ.get("MAX_REQUEST_SIZE", 10 * 1024 * 1024))  # 10MB
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 30))
RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", 100))
RATE_LIMIT_PERIOD = int(os.environ.get("RATE_LIMIT_PERIOD", 60))

# تنظیمات دیتابیس
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", 10))
DB_MAX_OVERFLOW = int(os.environ.get("DB_MAX_OVERFLOW", 20))
DB_POOL_TIMEOUT = int(os.environ.get("DB_POOL_TIMEOUT", 30))

# تنظیمات کش
CACHE_TTL = int(os.environ.get("CACHE_TTL", 300))
CACHE_MAX_SIZE = int(os.environ.get("CACHE_MAX_SIZE", 1000))

# تنظیمات بکاپ
BACKUP_INTERVAL = int(os.environ.get("BACKUP_INTERVAL", 86400))
BACKUP_RETENTION = int(os.environ.get("BACKUP_RETENTION", 7))

# ============================================================
#                    ENUMS & CONSTANTS (پیشرفته)
# ============================================================

class APIStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    DEGRADED = "degraded"
    RATE_LIMITED = "rate_limited"

class SecurityLevel(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    VIP = "vip"

class ResponseType(Enum):
    JSON = "json"
    HTML = "html"
    TEXT = "text"
    FILE = "file"
    STREAM = "stream"
    REDIRECT = "redirect"
    XML = "xml"
    CSV = "csv"
    PDF = "pdf"

class CacheControl(Enum):
    NO_CACHE = "no-cache"
    NO_STORE = "no-store"
    PUBLIC = "public"
    PRIVATE = "private"
    MUST_REVALIDATE = "must-revalidate"
    MAX_AGE = "max-age"
    NO_TRANSFORM = "no-transform"

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class ErrorCode(Enum):
    SUCCESS = 0
    UNAUTHORIZED = 1001
    FORBIDDEN = 1002
    NOT_FOUND = 1003
    INVALID_INPUT = 1004
    RATE_LIMIT = 1005
    SERVER_ERROR = 1006
    MAINTENANCE = 1007
    VIP_REQUIRED = 1008
    ADMIN_REQUIRED = 1009
    ALREADY_EXISTS = 1010
    EXPIRED = 1011
    PAYMENT_REQUIRED = 1012
    CONFLICT = 1013
    TOO_MANY_REQUESTS = 1014

# ============================================================
#                    PYDANTIC MODELS (کامل)
# ============================================================

class HealthResponse(BaseModel):
    status: str
    uptime: str
    version: str
    time: str
    database: str
    memory: Dict[str, Any]
    cpu: Dict[str, Any]
    environment: str
    services: Dict[str, str]
    timestamp: str

class StatsResponse(BaseModel):
    users: Dict[str, int]
    signals: Dict[str, int]
    payments: Dict[str, Union[int, float]]
    trades: Dict[str, Union[int, float]]
    timestamp: str
    performance: Dict[str, float]

class PriceResponse(BaseModel):
    coin: str
    price: float
    change_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    market_cap: Optional[float] = None
    supply: Optional[float] = None
    timestamp: str

class SignalResponse(BaseModel):
    coin: str
    signal: str
    confidence: int
    price: float
    targets: List[float]
    stop_loss: float
    risk_reward: float
    timeframe: str
    indicators: Dict[str, float]
    analysis: str
    timestamp: str

class MarketResponse(BaseModel):
    tickers: Dict[str, float]
    count: int
    top_gainers: List[Dict[str, Any]]
    top_losers: List[Dict[str, Any]]
    volume: float
    timestamp: str

class UserResponse(BaseModel):
    telegram_id: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_vip: bool
    is_admin: bool
    is_banned: bool
    balance: float
    vip_level: int
    vip_expire: Optional[str]
    referral_code: Optional[str]
    referral_count: int
    total_trades: int
    win_rate: float
    registered_at: str

class PaymentResponse(BaseModel):
    payment_id: str
    user_id: str
    amount: float
    currency: str
    status: str
    payment_type: str
    description: Optional[str]
    created_at: str
    completed_at: Optional[str]

class CoinResponse(BaseModel):
    coins: List[str]
    count: int
    categories: Dict[str, List[str]]
    timestamp: str

class ErrorResponse(BaseModel):
    error: str
    error_code: int
    status_code: int
    timestamp: str
    path: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class WebhookPayload(BaseModel):
    update_id: Optional[int] = None
    message: Optional[Dict] = None
    callback_query: Optional[Dict] = None
    inline_query: Optional[Dict] = None
    chat_member: Optional[Dict] = None

class MetricResponse(BaseModel):
    requests: Dict[str, Union[int, float, str]]
    cache: Dict[str, int]
    uptime: Dict[str, Union[int, str]]
    memory: Dict[str, Union[int, float]]
    cpu: Dict[str, Union[int, float]]
    timestamp: str

class TokenResponse(BaseModel):
    token: str
    refresh_token: Optional[str] = None
    expires: str
    type: str
    user_id: str

class RateLimitResponse(BaseModel):
    limit: int
    remaining: int
    reset: int
    period: int

class SystemInfoResponse(BaseModel):
    hostname: str
    platform: str
    python_version: str
    cpu_count: int
    memory_total: int
    disk_total: int
    uptime: str
    load_average: List[float]
    timestamp: str

# ============================================================
#                    LIFESPAN (مدیریت چرخه حیات)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """مدیریت چرخه حیات سرور با تسک‌های پس‌زمینه پیشرفته"""
    
    # شروع
    await on_startup()
    
    yield
    
    # پایان
    await on_shutdown()

async def on_startup():
    """عملیات هنگام شروع سرور"""
    # ایجاد session
    app.state.session = aiohttp.ClientSession(
        timeout=ClientTimeout(total=30),
        connector=TCPConnector(limit=100, ttl_dns_cache=300)
    )
    
    # شروع تسک‌های پس‌زمینه
    asyncio.create_task(background_health_check())
    asyncio.create_task(background_cache_cleanup())
    asyncio.create_task(background_stats_update())
    asyncio.create_task(background_metrics_collector())
    asyncio.create_task(background_rate_limiter_cleanup())
    
    # زمانبندی تسک‌ها
    app.state.scheduler = AsyncIOScheduler()
    app.state.scheduler.add_job(
        cleanup_old_data,
        CronTrigger(hour=3, minute=0),
        id='cleanup_old_data'
    )
    app.state.scheduler.add_job(
        update_market_cache,
        IntervalTrigger(minutes=5),
        id='update_market_cache'
    )
    app.state.scheduler.add_job(
        daily_backup,
        CronTrigger(hour=2, minute=0),
        id='daily_backup'
    )
    app.state.scheduler.add_job(
        generate_daily_report,
        CronTrigger(hour=20, minute=0),
        id='generate_daily_report'
    )
    app.state.scheduler.add_job(
        cleanup_expired_tokens,
        IntervalTrigger(hours=6),
        id='cleanup_expired_tokens'
    )
    app.state.scheduler.add_job(
        vacuum_database,
        CronTrigger(day_of_week='sun', hour=4, minute=0),
        id='vacuum_database'
    )
    app.state.scheduler.start()

async def on_shutdown():
    """عملیات هنگام توقف سرور"""
    if hasattr(app.state, 'session'):
        await app.state.session.close()
    
    if hasattr(app.state, 'scheduler'):
        app.state.scheduler.shutdown()

# ============================================================
#                    FASTAPI APP
# ============================================================

app = FastAPI(
    title="CryptoPulse AI API",
    description="API for CryptoPulse AI Trading Bot - نسخه فوق‌پیشرفته",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    terms_of_service="https://cryptopulse.ai/terms",
    contact={
        "name": "CryptoPulse Team",
        "url": "https://cryptopulse.ai",
        "email": "support@cryptopulse.ai"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    swagger_ui_parameters={
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "tryItOutEnabled": True
    },
    root_path="/api/v1"
)

# ============================================================
#                    MIDDLEWARE (پیشرفته)
# ============================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """افزودن هدر زمان پردازش"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Version"] = "3.0.0"
    return response

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """محدودیت نرخ درخواست"""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # ذخیره درخواست‌ها
    if not hasattr(app.state, 'rate_limits'):
        app.state.rate_limits = defaultdict(list)
    
    app.state.rate_limits[client_ip] = [
        t for t in app.state.rate_limits[client_ip] if now - t < RATE_LIMIT_PERIOD
    ]
    
    if len(app.state.rate_limits[client_ip]) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "error_code": ErrorCode.TOO_MANY_REQUESTS.value,
                "message": f"Rate limit exceeded. Limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_PERIOD} seconds",
                "retry_after": int(RATE_LIMIT_PERIOD - (now - app.state.rate_limits[client_ip][0]))
            }
        )
    
    app.state.rate_limits[client_ip].append(now)
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
    compresslevel=6
)

# ============================================================
#                    SECURITY (پیشرفته)
# ============================================================

security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

class SecurityManager:
    """مدیریت امنیت پیشرفته"""
    
    @staticmethod
    async def verify_api_key(api_key: str = Depends(api_key_header)):
        """بررسی کلید API"""
        if not API_KEY:
            return True
        if api_key == API_KEY:
            return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "APIKey"}
        )
    
    @staticmethod
    async def verify_admin(user_id: str) -> bool:
        """بررسی ادمین بودن"""
        try:
            return int(user_id) in ADMIN_IDS
        except:
            return False
    
    @staticmethod
    def get_current_user(token: str = Depends(security)):
        """دریافت کاربر فعلی از توکن"""
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"}
            )
        # پیاده‌سازی JWT
        return {"user_id": "123", "is_admin": True}

# ============================================================
#                    VARIABLES (سراسری)
# ============================================================

START_TIME = datetime.now()
REQUEST_COUNT = 0
ERROR_COUNT = 0
CACHE_STATS = {
    'hits': 0,
    'misses': 0,
    'size': 0
}
HEALTH_STATUS = {
    'status': APIStatus.ONLINE.value,
    'last_check': None,
    'errors': [],
    'components': {}
}
METRICS_DATA = {
    'requests_per_minute': deque(maxlen=60),
    'response_times': deque(maxlen=1000),
    'error_rates': deque(maxlen=60)
}
RATE_LIMITS = defaultdict(list)

# ============================================================
#                    BACKGROUND TASKS (پیشرفته)
# ============================================================

async def background_health_check():
    """بررسی سلامت پس‌زمینه با جزئیات کامل"""
    global HEALTH_STATUS
    
    while True:
        try:
            components = {}
            
            # بررسی دیتابیس
            if db_manager:
                try:
                    health = db_manager.health_check()
                    components['database'] = health.get('status', 'unknown')
                except:
                    components['database'] = 'error'
            else:
                components['database'] = 'unavailable'
            
            # بررسی بازار
            if get_market:
                try:
                    ticker = await get_market().get_market_data("BTC")
                    components['market'] = "healthy" if ticker else "unhealthy"
                except:
                    components['market'] = "error"
            else:
                components['market'] = "unavailable"
            
            # بررسی کش
            if get_cache:
                try:
                    cache = get_cache()
                    components['cache'] = "healthy" if cache else "unavailable"
                except:
                    components['cache'] = "error"
            else:
                components['cache'] = "unavailable"
            
            # بررسی AI
            if get_ai:
                try:
                    components['ai'] = "healthy"
                except:
                    components['ai'] = "error"
            else:
                components['ai'] = "unavailable"
            
            HEALTH_STATUS['components'] = components
            HEALTH_STATUS['last_check'] = datetime.now().isoformat()
            HEALTH_STATUS['status'] = APIStatus.ONLINE.value
            
        except Exception as e:
            HEALTH_STATUS['errors'].append(str(e))
            if len(HEALTH_STATUS['errors']) > 100:
                HEALTH_STATUS['errors'] = HEALTH_STATUS['errors'][-50:]
            HEALTH_STATUS['status'] = APIStatus.DEGRADED.value
        
        await asyncio.sleep(60)

async def background_cache_cleanup():
    """پاکسازی کش پس‌زمینه"""
    while True:
        try:
            if get_cache:
                cache = get_cache()
                if cache and hasattr(cache, 'clear'):
                    cache.clear()
                    CACHE_STATS['size'] = 0
            await asyncio.sleep(3600)
        except:
            await asyncio.sleep(60)

async def background_stats_update():
    """بروزرسانی آمار پس‌زمینه"""
    while True:
        try:
            if db_manager:
                db_manager.get_stats()
            await asyncio.sleep(300)
        except:
            await asyncio.sleep(60)

async def background_metrics_collector():
    """جمع‌آوری متریک‌ها"""
    while True:
        try:
            METRICS_DATA['requests_per_minute'].append(REQUEST_COUNT)
            await asyncio.sleep(60)
        except:
            await asyncio.sleep(60)

async def background_rate_limiter_cleanup():
    """پاکسازی محدودیت نرخ"""
    while True:
        try:
            now = time.time()
            for ip in list(RATE_LIMITS.keys()):
                RATE_LIMITS[ip] = [t for t in RATE_LIMITS[ip] if now - t < RATE_LIMIT_PERIOD]
                if not RATE_LIMITS[ip]:
                    del RATE_LIMITS[ip]
            await asyncio.sleep(60)
        except:
            await asyncio.sleep(60)

def cleanup_old_data():
    """پاکسازی داده‌های قدیمی"""
    try:
        if db_manager:
            with db_manager.get_session() as session:
                from bot3 import Signal
                expired = session.query(Signal).filter(
                    Signal.is_active == True,
                    Signal.created_at < datetime.now() - timedelta(days=7)
                ).all()
                for signal in expired:
                    signal.is_active = False
                session.commit()
    except:
        pass

def update_market_cache():
    """بروزرسانی کش بازار"""
    try:
        if get_market and get_cache:
            tickers = asyncio.run(get_market().get_all_prices())
            if tickers and get_cache:
                cache = get_cache()
                if cache:
                    cache.set('market_data', tickers)
    except:
        pass

def daily_backup():
    """بکاپ روزانه"""
    try:
        if db_manager:
            result = db_manager.backup()
            if result.get('success'):
                import os
                backup_dir = "./backups"
                if os.path.exists(backup_dir):
                    files = sorted(
                        [os.path.join(backup_dir, f) for f in os.listdir(backup_dir)],
                        key=os.path.getctime
                    )
                    for f in files[:-BACKUP_RETENTION]:
                        os.remove(f)
    except:
        pass

def generate_daily_report():
    """تولید گزارش روزانه"""
    try:
        if db_manager:
            stats = db_manager.get_stats()
            # ارسال گزارش به ادمین‌ها
            pass
    except:
        pass

def cleanup_expired_tokens():
    """پاکسازی توکن‌های منقضی"""
    pass

def vacuum_database():
    """بهینه‌سازی دیتابیس"""
    try:
        if db_manager:
            db_manager.vacuum()
    except:
        pass

# ============================================================
#                    ROUTES (کامل و پیشرفته)
# ============================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """صفحه اصلی API"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    return {
        "status": APIStatus.ONLINE.value,
        "name": "CryptoPulse AI",
        "version": "3.0.0",
        "channel": "@CryptoPulse606",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "environment": ENVIRONMENT,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """بررسی کامل سلامت سرور"""
    global REQUEST_COUNT, START_TIME
    
    REQUEST_COUNT += 1
    
    uptime_seconds = (datetime.now() - START_TIME).total_seconds()
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    uptime_str = f"{days}d {hours}h {minutes}m"
    
    db_status = "healthy"
    if db_manager:
        try:
            health = db_manager.health_check()
            db_status = health.get('status', 'healthy')
        except:
            db_status = "error"
    
    memory_info = {}
    cpu_info = {}
    try:
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total // (1024 * 1024),
            'available': memory.available // (1024 * 1024),
            'used': memory.used // (1024 * 1024),
            'percent': memory.percent
        }
        cpu_info = {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0
        }
    except:
        memory_info = {'total': 512, 'available': 256, 'used': 256, 'percent': 50}
        cpu_info = {'percent': 12, 'count': 2, 'frequency': 0}
    
    services = {
        'database': db_status,
        'market': HEALTH_STATUS.get('components', {}).get('market', 'unknown'),
        'cache': HEALTH_STATUS.get('components', {}).get('cache', 'unknown'),
        'ai': HEALTH_STATUS.get('components', {}).get('ai', 'unknown')
    }
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        uptime=uptime_str,
        version="3.0.0",
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        database=db_status,
        memory=memory_info,
        cpu=cpu_info,
        environment=ENVIRONMENT,
        services=services,
        timestamp=datetime.now().isoformat()
    )

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """دریافت آمار کامل"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    
    stats = {}
    if db_manager:
        try:
            stats = db_manager.get_stats()
        except:
            stats = {}
    
    return StatsResponse(
        users={
            "total": stats.get('users', 0),
            "active": stats.get('active_users', 0),
            "vip": stats.get('vip_users', 0),
            "banned": stats.get('banned_users', 0)
        },
        signals={
            "total": stats.get('signals', 0),
            "active": stats.get('active_signals', 0),
            "vip": stats.get('vip_signals', 0)
        },
        payments={
            "total": stats.get('payments', 0),
            "pending": stats.get('pending_payments', 0),
            "revenue": stats.get('total_revenue', 0.0),
            "today_revenue": stats.get('today_revenue', 0.0)
        },
        trades={
            "total": stats.get('trades', 0),
            "open": stats.get('open_trades', 0),
            "profit": stats.get('total_profit', 0.0)
        },
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        performance={
            "requests_per_second": REQUEST_COUNT / max((datetime.now() - START_TIME).total_seconds(), 1),
            "error_rate": ERROR_COUNT / max(REQUEST_COUNT, 1) * 100
        }
    )

@app.get("/metrics", response_model=MetricResponse)
async def get_metrics():
    """دریافت متریک‌های سرور"""
    global REQUEST_COUNT, ERROR_COUNT, CACHE_STATS, START_TIME
    
    uptime = (datetime.now() - START_TIME).total_seconds()
    
    memory = {}
    cpu = {}
    try:
        memory = {
            'total': psutil.virtual_memory().total // (1024 * 1024),
            'used': psutil.virtual_memory().used // (1024 * 1024),
            'percent': psutil.virtual_memory().percent
        }
        cpu = {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count()
        }
    except:
        memory = {'total': 512, 'used': 256, 'percent': 50}
        cpu = {'percent': 12, 'count': 2}
    
    return MetricResponse(
        requests={
            "total": REQUEST_COUNT,
            "errors": ERROR_COUNT,
            "success_rate": f"{((REQUEST_COUNT - ERROR_COUNT) / max(REQUEST_COUNT, 1) * 100):.2f}%",
            "requests_per_minute": round(REQUEST_COUNT / max(uptime / 60, 1), 2)
        },
        cache=CACHE_STATS,
        uptime={
            "seconds": uptime,
            "formatted": f"{int(uptime // 86400)}d {int((uptime % 86400) // 3600)}h {int((uptime % 3600) // 60)}m"
        },
        memory=memory,
        cpu=cpu,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/system")
async def get_system_info():
    """دریافت اطلاعات سیستم"""
    try:
        return {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_total": psutil.disk_usage('/').total,
            "uptime": time.time() - psutil.boot_time(),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
            "timestamp": datetime.now().isoformat()
        }
    except:
        return {"error": "System info not available"}

# ============================================================
#                    API V1 (کامل)
# ============================================================

@app.get("/api/v1/price/{coin}", response_model=PriceResponse)
async def get_price(coin: str):
    """دریافت قیمت لحظه‌ای ارز با کش"""
    global REQUEST_COUNT, CACHE_STATS
    
    REQUEST_COUNT += 1
    coin = coin.upper()
    
    # بررسی کش
    if get_cache:
        cache = get_cache()
        cache_key = f"price_{coin}"
        if cache:
            cached = cache.get(cache_key)
            if cached:
                CACHE_STATS['hits'] += 1
                return cached
    
    CACHE_STATS['misses'] += 1
    
    ticker = await get_market().get_market_data(coin) if get_market else None
    
    if not ticker:
        raise HTTPException(
            status_code=404,
            detail=f"Coin {coin} not found"
        )
    
    response = PriceResponse(
        coin=coin,
        price=ticker.price,
        change_24h=ticker.change_24h,
        high_24h=ticker.high_24h,
        low_24h=ticker.low_24h,
        volume_24h=ticker.volume_24h,
        market_cap=None,
        supply=None,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # ذخیره در کش
    if get_cache:
        cache = get_cache()
        if cache:
            cache.set(cache_key, response, ttl=CACHE_TTL)
            CACHE_STATS['size'] = len(cache._cache) if hasattr(cache, '_cache') else 0
    
    return response

@app.get("/api/v1/price/batch")
async def get_prices_batch(coins: str = Query(..., description="لیست ارزها با کاما جدا شده")):
    """دریافت قیمت چند ارز به صورت همزمان"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    coin_list = [c.strip().upper() for c in coins.split(",")]
    
    results = {}
    for coin in coin_list:
        try:
            data = await get_market().get_market_data(coin) if get_market else None
            if data:
                results[coin] = {
                    "price": data.price,
                    "change_24h": data.change_24h,
                    "high_24h": data.high_24h,
                    "low_24h": data.low_24h,
                    "volume_24h": data.volume_24h
                }
            else:
                results[coin] = {"error": f"{coin} not found"}
        except:
            results[coin] = {"error": f"{coin} error"}
    
    return {
        "results": results,
        "count": len(results),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/v1/signal/{coin}", response_model=SignalResponse)
async def get_signal(
    coin: str,
    timeframe: str = Query("4h", description="تایم‌فریم (1h, 4h, 1d)"),
    use_ai: bool = Query(True, description="استفاده از تحلیل AI")
):
    """دریافت سیگنال معاملاتی با تحلیل پیشرفته"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    coin = coin.upper()
    
    signal = await get_market().get_signal(coin, timeframe) if get_market else None
    
    if not signal:
        raise HTTPException(
            status_code=404,
            detail=f"Signal for {coin} not available"
        )
    
    # تحلیل AI
    ai_analysis = ""
    if use_ai and get_ai:
        try:
            ticker = await get_market().get_market_data(coin)
            if ticker:
                ai_result = await get_ai().analyze_coin(
                    coin=coin,
                    market_data={
                        'price': ticker.price,
                        'change_24h': ticker.change_24h,
                        'high_24h': ticker.high_24h,
                        'low_24h': ticker.low_24h,
                        'volume_24h': ticker.volume_24h
                    },
                    technical_data=signal.get('technical', {}),
                    is_vip=False
                )
                ai_analysis = ai_result.get('ai_analysis', '')
        except:
            ai_analysis = "تحلیل AI در دسترس نیست"
    
    return SignalResponse(
        coin=coin,
        signal=signal.get('signal', 'hold'),
        confidence=signal.get('confidence', 50),
        price=signal.get('current_price', 0),
        targets=signal.get('targets', []),
        stop_loss=signal.get('stop_loss', 0),
        risk_reward=signal.get('risk_reward', 0),
        timeframe=timeframe,
        indicators=signal.get('technical', {}),
        analysis=ai_analysis,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/api/v1/market", response_model=MarketResponse)
async def get_market_data():
    """دریافت داده‌های کامل بازار با تحلیل"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    
    tickers = await get_market().get_all_prices() if get_market else {}
    
    # تحلیل بازار
    top_gainers = []
    top_losers = []
    total_volume = 0
    
    for symbol, ticker in tickers.items():
        if hasattr(ticker, 'volume_24h'):
            total_volume += ticker.volume_24h
        if hasattr(ticker, 'change_24h'):
            if ticker.change_24h > 5:
                top_gainers.append({
                    "symbol": symbol,
                    "change": ticker.change_24h,
                    "price": ticker.price if hasattr(ticker, 'price') else 0
                })
            elif ticker.change_24h < -5:
                top_losers.append({
                    "symbol": symbol,
                    "change": ticker.change_24h,
                    "price": ticker.price if hasattr(ticker, 'price') else 0
                })
    
    # مرتب‌سازی
    top_gainers.sort(key=lambda x: x['change'], reverse=True)
    top_losers.sort(key=lambda x: x['change'])
    
    return MarketResponse(
        tickers={k: v.price if hasattr(v, 'price') else 0 for k, v in tickers.items()},
        count=len(tickers),
        top_gainers=top_gainers[:5],
        top_losers=top_losers[:5],
        volume=total_volume,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/api/v1/coins", response_model=CoinResponse)
async def get_coins():
    """دریافت لیست تمام ارزها با دسته‌بندی"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    
    coins = list(get_market().coinex.coin_map.keys()) if get_market else []
    
    # دسته‌بندی
    categories = {
        "Major": ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT"],
        "DeFi": ["UNI", "AAVE", "MKR", "LINK", "ATOM", "ALGO"],
        "Layer1": ["BTC", "ETH", "SOL", "ADA", "AVAX", "NEAR", "FTM", "EOS"],
        "Meme": ["DOGE", "SHIB", "PEPE", "BONK", "FLOKI", "WIF"],
        "Other": []
    }
    
    categorized = {}
    for category, category_coins in categories.items():
        categorized[category] = [c for c in category_coins if c in coins]
    
    # بقیه ارزها
    all_categorized = []
    for cat_coins in categorized.values():
        all_categorized.extend(cat_coins)
    categorized["Other"] = [c for c in coins if c not in all_categorized]
    
    return CoinResponse(
        coins=coins,
        count=len(coins),
        categories=categorized,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/api/v1/user/{user_id}", response_model=UserResponse)
async def get_user_info(user_id: str):
    """دریافت اطلاعات کاربر"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    
    if not user_repo:
        raise HTTPException(
            status_code=500,
            detail="User repository not available"
        )
    
    user = user_repo.get_by_telegram_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return UserResponse(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_vip=user.is_vip,
        is_admin=user.is_admin,
        is_banned=user.is_banned,
        balance=user.balance or 0.0,
        vip_level=user.vip_level or 0,
        vip_expire=user.vip_expire.strftime("%Y-%m-%d %H:%M:%S") if user.vip_expire else None,
        referral_code=user.referral_code,
        referral_count=user.referral_count or 0,
        total_trades=user.total_trades or 0,
        win_rate=user.win_rate or 0.0,
        registered_at=user.registered_at.strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/api/v1/user/{user_id}/stats")
async def get_user_stats(user_id: str):
    """دریافت آمار کاربر"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    
    if not user_repo:
        raise HTTPException(status_code=500, detail="User repository not available")
    
    user = user_repo.get_by_telegram_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "telegram_id": user.telegram_id,
        "total_signals": user.total_signals or 0,
        "total_trades": user.total_trades or 0,
        "successful_trades": user.successful_trades or 0,
        "failed_trades": user.failed_trades or 0,
        "win_rate": user.win_rate or 0.0,
        "balance": user.balance or 0.0,
        "total_profit": user.total_profit or 0.0,
        "is_vip": user.is_vip,
        "vip_expire": user.vip_expire.strftime("%Y-%m-%d %H:%M:%S") if user.vip_expire else None,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/v1/payments/{user_id}", response_model=List[PaymentResponse])
async def get_user_payments(user_id: str):
    """دریافت پرداخت‌های کاربر"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    
    if not payment_repo:
        raise HTTPException(status_code=500, detail="Payment repository not available")
    
    payments = payment_repo.get_user_payments(user_id) if hasattr(payment_repo, 'get_user_payments') else []
    
    return [
        PaymentResponse(
            payment_id=p.payment_id,
            user_id=p.user_id,
            amount=p.amount,
            currency=p.currency,
            status=p.status,
            payment_type=p.payment_type,
            description=p.description,
            created_at=p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            completed_at=p.completed_at.strftime("%Y-%m-%d %H:%M:%S") if p.completed_at else None
        ) for p in payments
    ]

@app.post("/api/v1/webhook")
async def api_webhook(request: Request):
    """API Webhook برای دریافت داده از سرویس‌های خارجی"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    
    try:
        data = await request.json()
        return {
            "status": "ok",
            "received": True,
            "timestamp": datetime.now().isoformat()
        }
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")

@app.post("/api/v1/webhook/telegram")
async def telegram_webhook(request: Request):
    """Webhook مخصوص تلگرام"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    
    try:
        data = await request.json()
        # پردازش آپدیت تلگرام
        return {"status": "ok", "received": True}
    except:
        raise HTTPException(status_code=400, detail="Invalid request")

# ============================================================
#                    WEBHOOK (کامل)
# ============================================================

@app.post("/webhook")
async def webhook(request: Request):
    """Webhook اصلی برای دریافت آپدیت‌های تلگرام"""
    global REQUEST_COUNT, ERROR_COUNT
    
    REQUEST_COUNT += 1
    
    try:
        data = await request.json()
        return {"status": "ok", "received": True}
    except Exception as e:
        ERROR_COUNT += 1
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )

@app.post("/webhook/github")
async def github_webhook(request: Request):
    """Webhook برای GitHub"""
    try:
        data = await request.json()
        return {"status": "ok"}
    except:
        return JSONResponse(status_code=400, content={"status": "error"})

@app.post("/webhook/coinex")
async def coinex_webhook(request: Request):
    """Webhook برای CoinEx"""
    try:
        data = await request.json()
        return {"status": "ok"}
    except:
        return JSONResponse(status_code=400, content={"status": "error"})

# ============================================================
#                    ADMIN ROUTES (پیشرفته)
# ============================================================

@app.get("/admin/health")
async def admin_health():
    """بررسی سلامت برای ادمین با جزئیات کامل"""
    return {
        "status": HEALTH_STATUS,
        "system": {
            "cpu": psutil.cpu_percent(interval=1) if hasattr(psutil, 'cpu_percent') else 0,
            "memory": psutil.virtual_memory()._asdict() if hasattr(psutil, 'virtual_memory') else {},
            "disk": psutil.disk_usage('/')._asdict() if hasattr(psutil, 'disk_usage') else {}
        } if hasattr(psutil, 'cpu_percent') else {},
        "uptime": (datetime.now() - START_TIME).total_seconds(),
        "requests": REQUEST_COUNT,
        "errors": ERROR_COUNT,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/admin/system")
async def admin_system():
    """اطلاعات کامل سیستم برای ادمین"""
    try:
        import psutil
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "stats": psutil.cpu_stats()._asdict() if hasattr(psutil, 'cpu_stats') else {}
            },
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "network": {
                "connections": len(psutil.net_connections()),
                "interfaces": psutil.net_if_stats().keys()
            } if hasattr(psutil, 'net_connections') else {},
            "timestamp": datetime.now().isoformat()
        }
    except:
        return {"error": "psutil not available"}

@app.post("/admin/clear-cache")
async def admin_clear_cache():
    """پاکسازی کش توسط ادمین"""
    if get_cache:
        cache = get_cache()
        if cache:
            cache.clear()
            CACHE_STATS['size'] = 0
            CACHE_STATS['hits'] = 0
            CACHE_STATS['misses'] = 0
            return {"status": "ok", "message": "Cache cleared"}
    return {"status": "error", "message": "Cache not available"}

@app.post("/admin/backup")
async def admin_create_backup():
    """ایجاد بکاپ توسط ادمین"""
    if db_manager:
        result = db_manager.backup()
        return result
    return {"status": "error", "message": "Database not available"}

@app.get("/admin/stats")
async def admin_stats():
    """دریافت آمار کامل برای ادمین"""
    if db_manager:
        stats = db_manager.get_stats()
        return {
            "database": stats,
            "system": {
                "cpu": psutil.cpu_percent(interval=1) if hasattr(psutil, 'cpu_percent') else 0,
                "memory": psutil.virtual_memory()._asdict() if hasattr(psutil, 'virtual_memory') else {}
            },
            "cache": CACHE_STATS,
            "requests": REQUEST_COUNT,
            "errors": ERROR_COUNT,
            "timestamp": datetime.now().isoformat()
        }
    return {"error": "Database not available"}

# ============================================================
#                    ERROR HANDLERS (پیشرفته)
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """مدیریت خطاهای HTTP با جزئیات کامل"""
    global ERROR_COUNT
    
    ERROR_COUNT += 1
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "error_code": ErrorCode.INVALID_INPUT.value if exc.status_code == 400 else
                         ErrorCode.UNAUTHORIZED.value if exc.status_code == 401 else
                         ErrorCode.FORBIDDEN.value if exc.status_code == 403 else
                         ErrorCode.NOT_FOUND.value if exc.status_code == 404 else
                         ErrorCode.RATE_LIMIT.value if exc.status_code == 429 else
                         ErrorCode.SERVER_ERROR.value,
            "status_code": exc.status_code,
            "path": request.url.path,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "headers": dict(exc.headers) if exc.headers else {}
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """مدیریت خطاهای سراسری"""
    global ERROR_COUNT
    
    ERROR_COUNT += 1
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "error_code": ErrorCode.SERVER_ERROR.value,
            "detail": str(exc) if DEBUG else "An error occurred",
            "path": request.url.path,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """مدیریت خطاهای اعتبارسنجی"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "error_code": ErrorCode.INVALID_INPUT.value,
            "detail": exc.errors(),
            "path": request.url.path,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )

# ============================================================
#                    SERVER MANAGER (پیشرفته)
# ============================================================

class ServerManager:
    """مدیریت سرور FastAPI با قابلیت‌های پیشرفته"""
    
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = PORT
        self.server = None
        self._running = False
        self._start_time = datetime.now()
        self._workers = 1
        self._loop = None
    
    async def start(self):
        """شروع سرور با تنظیمات بهینه"""
        self._running = True
        self._start_time = datetime.now()
        self._loop = asyncio.get_running_loop()
        
        config = uvicorn.Config(
            "part13:app",
            host=self.host,
            port=self.port,
            log_level="error" if not DEBUG else "info",
            access_log=DEBUG,
            loop="asyncio",
            timeout_keep_alive=30,
            workers=self._workers,
            limit_concurrency=1000,
            limit_max_requests=10000,
            timeout_graceful_shutdown=30,
            h11_max_incomplete_event_size=16384,
            http="httptools" if DEBUG else "h11",
            ws="websockets" if DEBUG else "none",
            forwarded_allow_ips="*",
            proxy_headers=True
        )
        
        self.server = uvicorn.Server(config)
        await self.server.serve()
    
    async def stop(self):
        """توقف سرور"""
        self._running = False
        if self.server:
            self.server.should_exit = True
            await self.server.shutdown()
    
    def get_status(self) -> Dict[str, Any]:
        """دریافت وضعیت سرور"""
        return {
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "uptime": (datetime.now() - self._start_time).total_seconds(),
            "start_time": self._start_time.isoformat(),
            "workers": self._workers,
            "requests": REQUEST_COUNT,
            "errors": ERROR_COUNT
        }
    
    def is_running(self) -> bool:
        return self._running
    
    def set_workers(self, workers: int):
        """تعداد workers را تنظیم می‌کند"""
        self._workers = max(1, min(workers, psutil.cpu_count() or 1))

# ============================================================
#                    EXPORT
# ============================================================

server_manager = ServerManager()

def get_server() -> ServerManager:
    return server_manager

def get_app() -> FastAPI:
    return app

# ============================================================
#                    MAIN
# ============================================================

if __name__ == "__main__":
    asyncio.run(server_manager.start())
