#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🚀 CryptoPulse AI Bot v3.0 - Part 13 (Balanced Production Edition)        ║
║  ────────────────────────────────────────────────────────────────────────   ║
║  ✅ Fixed: async bugs, rate limit lock, security, imports, error handling  ║
║  Run: uvicorn part13:app --host 0.0.0.0 --port 8080                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import uuid
import asyncio
import hashlib
import hmac
import logging
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from enum import Enum

import psutil
import uvicorn
import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector

from fastapi import (
    FastAPI, Request, HTTPException, Depends, Header,
    Query, Path, WebSocket, WebSocketDisconnect, status
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer

from pydantic import BaseModel, Field

# ============================================================
#                    LOGGING (CLEAN)
# ============================================================

# خاموش کردن لاگ کتابخونه‌های خارجی
for lib in ["uvicorn", "uvicorn.access", "uvicorn.error", "aiohttp", "apscheduler"]:
    logging.getLogger(lib).setLevel(logging.CRITICAL + 1)

logger = logging.getLogger("cryptopulse")
logger.setLevel(logging.WARNING)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter('%(levelname)s | %(message)s'))
    logger.addHandler(handler)

# ============================================================
#                    SAFE IMPORT SYSTEM
# ============================================================

def safe_import(module_name: str, *attrs: str) -> Dict[str, Any]:
    """ایمن‌سازی import با fallback"""
    result = {}
    try:
        mod = __import__(module_name, fromlist=list(attrs))
        for attr in attrs:
            result[attr] = getattr(mod, attr, None)
    except Exception as e:
        logger.warning(f"Module '{module_name}' not available: {e}")
        for attr in attrs:
            result[attr] = None
    return result

# وارد کردن ماژول‌های پروژه
_bot1 = safe_import("bot1", "get_config", "verify_api_key", "hash_api_key")
_bot2 = safe_import("bot2", "db_manager", "user_repo", "signal_repo", "payment_repo")
_bot3 = safe_import("bot3", "get_cache", "get_time", "get_emoji")
_bot4 = safe_import("bot4", "get_market", "get_coinex")
_bot5 = safe_import("bot5", "get_ai", "get_groq")
_bot7 = safe_import("bot7", "bot_handlers")

get_config = _bot1.get("get_config")
verify_api_key_fn = _bot1.get("verify_api_key")
hash_api_key = _bot1.get("hash_api_key")

db_manager = _bot2.get("db_manager")
user_repo = _bot2.get("user_repo")
signal_repo = _bot2.get("signal_repo")
payment_repo = _bot2.get("payment_repo")

get_cache = _bot3.get("get_cache")
get_time = _bot3.get("get_time")
get_emoji = _bot3.get("get_emoji")

get_market = _bot4.get("get_market")
get_coinex = _bot4.get("get_coinex")

get_ai = _bot5.get("get_ai")
get_groq = _bot5.get("get_groq")

bot_handlers = _bot7.get("bot_handlers")

# ============================================================
#                    CONFIGURATION
# ============================================================

PORT = int(os.environ.get("PORT", "8080"))
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_KEY = os.environ.get("API_KEY", "")
API_KEY_HASH = os.environ.get("API_KEY_HASH", "")
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "*").split(",") if h.strip()]
RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_PERIOD = int(os.environ.get("RATE_LIMIT_PERIOD", "60"))
CACHE_TTL = int(os.environ.get("CACHE_TTL", "300"))

ADMIN_IDS = []
for x in os.environ.get("ADMIN_IDS", "").split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except ValueError:
            pass

# ============================================================
#                    ENUMS
# ============================================================

class APIStatus(str, Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    ERROR = "error"

class ErrorCode(int, Enum):
    SUCCESS = 0
    UNAUTHORIZED = 1001
    FORBIDDEN = 1002
    NOT_FOUND = 1003
    INVALID_INPUT = 1004
    RATE_LIMIT = 1005
    SERVER_ERROR = 1006
    TOO_MANY_REQUESTS = 1014

# ============================================================
#                    PYDANTIC MODELS
# ============================================================

class HealthResponse(BaseModel):
    status: str
    uptime: str
    version: str
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    database: str
    services: Dict[str, str]
    timestamp: str

class StatsResponse(BaseModel):
    users: Dict[str, int] = Field(default_factory=dict)
    signals: Dict[str, int] = Field(default_factory=dict)
    payments: Dict[str, Union[int, float]] = Field(default_factory=dict)
    trades: Dict[str, Union[int, float]] = Field(default_factory=dict)
    uptime_seconds: float = 0
    requests_total: int = 0
    errors_total: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class PriceResponse(BaseModel):
    coin: str
    price: float
    change_24h: float = 0
    high_24h: float = 0
    low_24h: float = 0
    volume_24h: float = 0
    timestamp: str

class UserResponse(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    is_vip: bool = False
    is_admin: bool = False
    is_banned: bool = False
    balance: float = 0.0
    vip_level: int = 0
    total_trades: int = 0
    win_rate: float = 0.0
    registered_at: str = ""

class SystemInfoResponse(BaseModel):
    hostname: str
    platform: str
    python_version: str
    cpu_count: int
    memory_total: int
    disk_total: int
    uptime_seconds: float
    load_average: List[float]
    timestamp: str

# ============================================================
#                    GLOBAL STATE
# ============================================================

START_TIME = datetime.now()
REQUEST_COUNT = 0
ERROR_COUNT = 0

CACHE_STATS = {'hits': 0, 'misses': 0, 'size': 0}

HEALTH_STATUS = {
    'status': APIStatus.ONLINE.value,
    'last_check': None,
    'components': {}
}

RATE_LIMITS: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_LOCK = asyncio.Lock()

# ============================================================
#                    FASTAPI APP
# ============================================================

app = FastAPI(
    title="CryptoPulse AI API",
    version="3.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None
)

# ============================================================
#                    MIDDLEWARE
# ============================================================

@app.middleware("http")
async def main_middleware(request: Request, call_next):
    """میدلور اصلی: rate limit + metrics + error handling"""
    global REQUEST_COUNT, ERROR_COUNT
    
    start_time = time.time()
    REQUEST_COUNT += 1
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Rate Limiting
        async with RATE_LIMIT_LOCK:
            now = time.monotonic()
            RATE_LIMITS[client_ip] = [
                t for t in RATE_LIMITS[client_ip]
                if now - t < RATE_LIMIT_PERIOD
            ]
            
            if len(RATE_LIMITS[client_ip]) >= RATE_LIMIT_REQUESTS:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "error_code": ErrorCode.TOO_MANY_REQUESTS.value,
                        "retry_after": RATE_LIMIT_PERIOD
                    },
                    headers={"Retry-After": str(RATE_LIMIT_PERIOD)}
                )
            
            RATE_LIMITS[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add headers
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-API-Version"] = "3.0.0"
        
        return response
        
    except Exception as e:
        ERROR_COUNT += 1
        logger.error(f"Middleware error: {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "error_code": ErrorCode.SERVER_ERROR.value}
        )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)

# GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ============================================================
#                    SECURITY
# ============================================================

security = HTTPBearer(auto_error=False)

async def verify_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")
) -> bool:
    """تایید API Key با HMAC (timing-attack safe)"""
    if not API_KEY and not API_KEY_HASH:
        return True
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if API_KEY_HASH:
        key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
        if not hmac.compare_digest(key_hash, API_KEY_HASH):
            raise HTTPException(status_code=403, detail="Invalid API key")
    elif API_KEY:
        if not hmac.compare_digest(x_api_key.encode(), API_KEY.encode()):
            raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True

# ============================================================
#                    BACKGROUND TASKS
# ============================================================

async def background_health_check():
    """بررسی سلامت سیستم"""
    while True:
        try:
            components = {}
            
            # Database
            if db_manager:
                try:
                    health = db_manager.health_check()
                    components['database'] = health.get('status', 'unknown')
                except:
                    components['database'] = 'error'
            else:
                components['database'] = 'unavailable'
            
            # Market
            if get_market:
                try:
                    market = get_market()
                    if market:
                        ticker = await market.get_market_data("BTC")
                        components['market'] = "healthy" if ticker else "unhealthy"
                except:
                    components['market'] = 'error'
            
            # Cache
            if get_cache:
                try:
                    cache = get_cache()
                    components['cache'] = "healthy" if cache else "unavailable"
                except:
                    components['cache'] = 'error'
            
            HEALTH_STATUS['components'] = components
            HEALTH_STATUS['last_check'] = datetime.now().isoformat()
            HEALTH_STATUS['status'] = APIStatus.ONLINE.value
            
        except Exception:
            HEALTH_STATUS['status'] = APIStatus.DEGRADED.value
        
        await asyncio.sleep(30)

async def background_rate_limiter_cleanup():
    """پاکسازی داده‌های rate limiter"""
    while True:
        try:
            now = time.monotonic()
            async with RATE_LIMIT_LOCK:
                expired = []
                for ip, timestamps in RATE_LIMITS.items():
                    RATE_LIMITS[ip] = [
                        t for t in timestamps
                        if now - t < RATE_LIMIT_PERIOD
                    ]
                    if not RATE_LIMITS[ip]:
                        expired.append(ip)
                for ip in expired:
                    del RATE_LIMITS[ip]
            await asyncio.sleep(120)
        except asyncio.CancelledError:
            break

async def background_cache_cleanup():
    """پاکسازی کش"""
    while True:
        try:
            CACHE_STATS['size'] = max(0, CACHE_STATS['size'] - 10)
            await asyncio.sleep(3600)
        except asyncio.CancelledError:
            break

# ============================================================
#                    LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """مدیریت چرخه حیات سرور"""
    logger.info("🚀 Starting CryptoPulse AI Server...")
    
    # Startup
    try:
        app.state.session = aiohttp.ClientSession(
            timeout=ClientTimeout(total=30),
            connector=TCPConnector(limit=100, ttl_dns_cache=300)
        )
        
        app.state.background_tasks = [
            asyncio.create_task(background_health_check()),
            asyncio.create_task(background_rate_limiter_cleanup()),
            asyncio.create_task(background_cache_cleanup())
        ]
        
        logger.info("✅ Server started successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    
    if hasattr(app.state, 'background_tasks'):
        for task in app.state.background_tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*app.state.background_tasks, return_exceptions=True)
    
    if hasattr(app.state, 'session'):
        await app.state.session.close()
    
    logger.info("✅ Shutdown complete")

app.router.lifespan_context = lifespan

# ============================================================
#                    API ROUTES
# ============================================================

@app.get("/")
async def root():
    """صفحه اصلی"""
    return {
        "name": "CryptoPulse AI",
        "version": "3.0.0",
        "status": "running",
        "uptime": str(datetime.now() - START_TIME).split('.')[0],
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    """بررسی سلامت کامل"""
    uptime = datetime.now() - START_TIME
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes = remainder // 60
    
    memory_info = {}
    cpu_info = {}
    
    try:
        mem = psutil.virtual_memory()
        memory_info = {
            'total_gb': round(mem.total / (1024**3), 1),
            'used_gb': round(mem.used / (1024**3), 1),
            'percent': mem.percent
        }
        cpu_info = {
            'percent': psutil.cpu_percent(interval=None),
            'count': psutil.cpu_count(logical=True) or 0
        }
    except:
        pass
    
    return HealthResponse(
        status=HEALTH_STATUS['status'],
        uptime=f"{days}d {hours}h {minutes}m",
        version="3.0.0",
        cpu=cpu_info,
        memory=memory_info,
        database=HEALTH_STATUS.get('components', {}).get('database', 'unknown'),
        services=HEALTH_STATUS.get('components', {}),
        timestamp=datetime.now().isoformat()
    )

@app.get("/stats", response_model=StatsResponse)
async def stats():
    """آمار کلی سیستم"""
    db_stats = {}
    if db_manager:
        try:
            db_stats = db_manager.get_stats()
        except:
            pass
    
    return StatsResponse(
        users={
            "total": db_stats.get('users', 0),
            "active": db_stats.get('active_users', 0),
            "vip": db_stats.get('vip_users', 0)
        },
        signals={
            "total": db_stats.get('signals', 0),
            "active": db_stats.get('active_signals', 0)
        },
        payments={
            "total": db_stats.get('payments', 0),
            "revenue": db_stats.get('total_revenue', 0.0)
        },
        trades={
            "total": db_stats.get('trades', 0),
            "profit": db_stats.get('total_profit', 0.0)
        },
        uptime_seconds=(datetime.now() - START_TIME).total_seconds(),
        requests_total=REQUEST_COUNT,
        errors_total=ERROR_COUNT,
        timestamp=datetime.now().isoformat()
    )

@app.get("/system", response_model=SystemInfoResponse)
async def system_info():
    """اطلاعات سیستم"""
    load_avg = [0.0, 0.0, 0.0]
    if hasattr(os, 'getloadavg'):
        try:
            load_avg = list(os.getloadavg())
        except:
            pass
    
    return SystemInfoResponse(
        hostname=socket.gethostname(),
        platform=sys.platform,
        python_version=sys.version.split()[0],
        cpu_count=psutil.cpu_count(logical=True) or 0,
        memory_total=psutil.virtual_memory().total,
        disk_total=psutil.disk_usage('/').total if hasattr(psutil, 'disk_usage') else 0,
        uptime_seconds=(datetime.now() - START_TIME).total_seconds(),
        load_average=load_avg,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/v1/price/{coin}", response_model=PriceResponse)
async def get_price(
    coin: str = Path(..., description="نماد ارز"),
    auth: bool = Depends(verify_api_key)
):
    """قیمت لحظه‌ای ارز"""
    global CACHE_STATS
    coin = coin.upper()
    
    # Check cache
    cache_key = f"price_{coin}"
    if get_cache:
        try:
            cache = get_cache()
            if cache:
                cached = cache.get(cache_key)
                if cached:
                    CACHE_STATS['hits'] += 1
                    return cached
        except:
            pass
    
    CACHE_STATS['misses'] += 1
    
    # Fetch from market
    if get_market:
        try:
            market = get_market()
            if market:
                ticker = await market.get_market_data(coin)
                if ticker:
                    response = PriceResponse(
                        coin=coin,
                        price=getattr(ticker, 'price', 0),
                        change_24h=getattr(ticker, 'change_24h', 0),
                        high_24h=getattr(ticker, 'high_24h', 0),
                        low_24h=getattr(ticker, 'low_24h', 0),
                        volume_24h=getattr(ticker, 'volume_24h', 0),
                        timestamp=datetime.now().isoformat()
                    )
                    
                    # Save to cache
                    if get_cache:
                        try:
                            cache = get_cache()
                            if cache:
                                cache.set(cache_key, response, ttl=CACHE_TTL)
                                if hasattr(cache, 'size'):
                                    CACHE_STATS['size'] = cache.size()
                        except:
                            pass
                    
                    return response
        except Exception as e:
            logger.error(f"Price fetch error for {coin}: {e}")
    
    raise HTTPException(status_code=404, detail=f"Coin '{coin}' not found")

@app.get("/api/v1/market")
async def get_market_data(auth: bool = Depends(verify_api_key)):
    """داده‌های بازار"""
    if not get_market:
        raise HTTPException(status_code=503, detail="Market service unavailable")
    
    try:
        market = get_market()
        tickers = await market.get_all_prices()
        
        if not tickers:
            return {"tickers": {}, "count": 0, "timestamp": datetime.now().isoformat()}
        
        result = {}
        top_gainers = []
        top_losers = []
        
        for symbol, ticker in tickers.items():
            price = getattr(ticker, 'price', 0)
            change = getattr(ticker, 'change_24h', 0)
            
            result[symbol] = price
            
            if change > 5:
                top_gainers.append({"symbol": symbol, "change": round(change, 2), "price": price})
            elif change < -5:
                top_losers.append({"symbol": symbol, "change": round(change, 2), "price": price})
        
        top_gainers.sort(key=lambda x: x['change'], reverse=True)
        top_losers.sort(key=lambda x: x['change'])
        
        return {
            "tickers": result,
            "count": len(result),
            "top_gainers": top_gainers[:5],
            "top_losers": top_losers[:5],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market data")

@app.get("/api/v1/user/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str = Path(..., description="شناسه کاربر"),
    auth: bool = Depends(verify_api_key)
):
    """اطلاعات کاربر"""
    if not user_repo:
        raise HTTPException(status_code=503, detail="User service unavailable")
    
    user = user_repo.get_by_telegram_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        telegram_id=str(user.telegram_id),
        username=getattr(user, 'username', None),
        is_vip=getattr(user, 'is_vip', False),
        is_admin=getattr(user, 'is_admin', False),
        is_banned=getattr(user, 'is_banned', False),
        balance=getattr(user, 'balance', 0.0),
        vip_level=getattr(user, 'vip_level', 0),
        total_trades=getattr(user, 'total_trades', 0),
        win_rate=getattr(user, 'win_rate', 0.0),
        registered_at=user.created_at.isoformat() if getattr(user, 'created_at', None) else ""
    )

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Webhook تلگرام"""
    try:
        data = await request.json()
        if bot_handlers:
            await bot_handlers(data)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(status_code=400, content={"status": "error", "message": str(e)[:200]})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "echo": data,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        pass

# ============================================================
#                    ERROR HANDLERS
# ============================================================

@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    """مدیریت خطاهای HTTP"""
    global ERROR_COUNT
    ERROR_COUNT += 1
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": str(exc.detail),
            "error_code": ErrorCode.SERVER_ERROR.value,
            "status_code": exc.status_code,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    """مدیریت خطاهای عمومی"""
    global ERROR_COUNT
    ERROR_COUNT += 1
    
    logger.error(f"Unhandled error: {type(exc).__name__}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_code": ErrorCode.SERVER_ERROR.value,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================
#                    MAIN
# ============================================================

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🚀 CryptoPulse AI Server v3.0                             ║
║  ────────────────────────────────────────────────────────   ║
║  Port: {PORT:<52} ║
║  Debug: {str(DEBUG):<51} ║
║  Environment: {ENVIRONMENT:<45} ║
║  ────────────────────────────────────────────────────────   ║
║  API: http://0.0.0.0:{PORT:<37} ║
║  Docs: http://0.0.0.0:{PORT}/docs{' ' * (31 - len(str(PORT)))} ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "part13:app",
        host="0.0.0.0",
        port=PORT,
        log_level="warning",
        access_log=False,
        reload=DEBUG
    )
