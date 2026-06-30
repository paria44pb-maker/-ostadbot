#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - FastAPI Server Module
ماژول سرور FastAPI کامل با پشتیبانی از Webhook، API، و مدیریت ربات
طراحی شده با بهترین استانداردهای حرفه‌ای
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException, Depends, Header, Query
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, validator
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# ==================== ایمپورت ماژول‌های داخلی ====================

try:
    from bot2 import get_config
    from bot3 import db_manager, user_repo, signal_repo, payment_repo
    from bot4 import get_time, get_emoji, get_formatter, get_hash, get_cache
    from bot5 import get_market
    from bot6 import get_ai
    from bot7 import get_technical
    from bot8 import lux_keyboard, LuxText, LuxEmoji
except ImportError as e:
    print(f"⚠️ Error importing modules: {e}")

# ==================== تنظیمات ====================

config = get_config() if 'get_config' in dir() else None
time_manager = get_time() if 'get_time' in dir() else None
emoji_manager = get_emoji() if 'get_emoji' in dir() else None
formatter = get_formatter() if 'get_formatter' in dir() else None
cache = get_cache() if 'get_cache' in dir() else None
market = get_market() if 'get_market' in dir() else None

# ==================== مدل‌های Pydantic ====================

class HealthResponse(BaseModel):
    status: str
    uptime: str
    database: str
    version: str
    time: str

class StatsResponse(BaseModel):
    users: Dict[str, int]
    signals: Dict[str, int]
    payments: Dict[str, Union[int, float]]
    time: str

class PriceResponse(BaseModel):
    coin: str
    price: float
    change_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    time: str

class SignalResponse(BaseModel):
    coin: str
    signal: str
    confidence: int
    price: float
    targets: List[float]
    stop_loss: float
    time: str

class WebhookPayload(BaseModel):
    update_id: Optional[int] = None
    message: Optional[Dict] = None
    callback_query: Optional[Dict] = None

# ==================== ایجاد اپلیکیشن FastAPI ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """مدیریت چرخه حیات سرور"""
    print("🚀 Starting CryptoPulse AI Server...")
    
    # شروع تسک‌های پس‌زمینه
    asyncio.create_task(background_health_check())
    asyncio.create_task(background_cache_cleanup())
    asyncio.create_task(background_stats_update())
    
    # زمانبندی تسک‌ها
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        cleanup_old_data,
        CronTrigger(hour=3, minute=0),
        id='cleanup_old_data'
    )
    scheduler.add_job(
        update_market_cache,
        IntervalTrigger(minutes=5),
        id='update_market_cache'
    )
    scheduler.start()
    
    yield
    
    print("🛑 Shutting down CryptoPulse AI Server...")

app = FastAPI(
    title="CryptoPulse AI API",
    description="API for CryptoPulse AI Trading Bot - نسخه حرفه‌ای",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ==================== Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# ==================== متغیرهای سراسری ====================

START_TIME = datetime.now()
REQUEST_COUNT = 0
ERROR_COUNT = 0
CACHE_STATS = {
    'hits': 0,
    'misses': 0,
    'size': 0
}

# ==================== مسیرهای اصلی ====================

@app.get("/", response_model=Dict[str, str])
async def root():
    """صفحه اصلی API"""
    return {
        "status": "online",
        "name": "CryptoPulse AI",
        "version": "3.0.0",
        "channel": "@CryptoPulse606",
        "time": time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "docs": "/docs",
            "price": "/api/v1/price/{coin}",
            "signal": "/api/v1/signal/{coin}"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """بررسی سلامت سرور و دیتابیس"""
    global REQUEST_COUNT, START_TIME
    
    REQUEST_COUNT += 1
    
    # بررسی دیتابیس
    db_status = "connected"
    try:
        if db_manager:
            health = db_manager.health_check()
            db_status = health.get('status', 'connected')
    except:
        db_status = "error"
    
    # محاسبه آپتایم
    uptime_seconds = (datetime.now() - START_TIME).total_seconds()
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    
    uptime_str = f"{days}d {hours}h {minutes}m"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        uptime=uptime_str,
        database=db_status,
        version="3.0.0",
        time=time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """دریافت آمار کامل"""
    global REQUEST_COUNT
    
    REQUEST_COUNT += 1
    
    stats = {}
    try:
        if db_manager:
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
        time=time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.get("/metrics")
async def get_metrics():
    """دریافت متریک‌های سرور"""
    global REQUEST_COUNT, ERROR_COUNT, CACHE_STATS
    
    return {
        "requests": {
            "total": REQUEST_COUNT,
            "errors": ERROR_COUNT,
            "success_rate": f"{((REQUEST_COUNT - ERROR_COUNT) / max(REQUEST_COUNT, 1) * 100):.2f}%"
        },
        "cache": CACHE_STATS,
        "uptime": (datetime.now() - START_TIME).total_seconds(),
        "time": time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# ==================== API V1 ====================

@app.get("/api/v1/price/{coin}", response_model=PriceResponse)
async def get_price(coin: str):
    """دریافت قیمت لحظه‌ای ارز"""
    global CACHE_STATS
    
    coin = coin.upper()
    
    # بررسی کش
    cache_key = f"price_{coin}"
    cached = cache.get(cache_key) if cache else None
    
    if cached:
        CACHE_STATS['hits'] += 1
        return cached
    
    CACHE_STATS['misses'] += 1
    
    ticker = await market.get_market_data(coin) if market else None
    
    if not ticker:
        raise HTTPException(status_code=404, detail=f"Coin {coin} not found")
    
    response = PriceResponse(
        coin=coin,
        price=ticker.price,
        change_24h=ticker.change_24h,
        high_24h=ticker.high_24h,
        low_24h=ticker.low_24h,
        volume_24h=ticker.volume_24h,
        time=time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    # ذخیره در کش
    if cache:
        cache.set(cache_key, response)
        CACHE_STATS['size'] = len(cache._cache) if hasattr(cache, '_cache') else 0
    
    return response

@app.get("/api/v1/signal/{coin}", response_model=SignalResponse)
async def get_signal(coin: str, timeframe: str = Query("4h", description="تایم‌فریم (1h, 4h, 1d)")):
    """دریافت سیگنال معاملاتی"""
    coin = coin.upper()
    
    signal = await market.get_signal(coin, timeframe) if market else None
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal for {coin} not available")
    
    return SignalResponse(
        coin=coin,
        signal=signal.get('signal', 'hold'),
        confidence=signal.get('confidence', 50),
        price=signal.get('current_price', 0),
        targets=signal.get('targets', []),
        stop_loss=signal.get('stop_loss', 0),
        time=time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.get("/api/v1/market")
async def get_market_data():
    """دریافت داده‌های کامل بازار"""
    tickers = await market.get_all_prices() if market else {}
    
    return {
        "tickers": tickers,
        "count": len(tickers),
        "time": time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# ==================== Webhook ====================

@app.post("/webhook")
async def webhook(request: Request):
    """Webhook برای دریافت آپدیت‌های تلگرام"""
    global ERROR_COUNT
    
    try:
        data = await request.json()
        
        # پردازش آپدیت
        if 'message' in data:
            await handle_message(data['message'])
        elif 'callback_query' in data:
            await handle_callback(data['callback_query'])
        
        return JSONResponse(content={"status": "ok"})
    
    except Exception:
        ERROR_COUNT += 1
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal server error"}
        )

# ==================== توابع کمک‌کننده Webhook ====================

async def handle_message(message: Dict):
    """پردازش پیام دریافتی"""
    # اینجا منطق پردازش پیام قرار می‌گیرد
    pass

async def handle_callback(callback: Dict):
    """پردازش کالبک دریافتی"""
    # اینجا منطق پردازش کالبک قرار می‌گیرد
    pass

# ==================== تسک‌های پس‌زمینه ====================

async def background_health_check():
    """بررسی سلامت پس‌زمینه"""
    while True:
        try:
            if db_manager:
                db_manager.health_check()
            await asyncio.sleep(60)
        except:
            await asyncio.sleep(300)

async def background_cache_cleanup():
    """پاکسازی کش پس‌زمینه"""
    while True:
        try:
            if cache:
                cache.clear()
            await asyncio.sleep(3600)
        except:
            await asyncio.sleep(3600)

async def background_stats_update():
    """بروزرسانی آمار پس‌زمینه"""
    while True:
        try:
            if db_manager:
                db_manager.get_stats()
            await asyncio.sleep(300)
        except:
            await asyncio.sleep(300)

def cleanup_old_data():
    """پاکسازی داده‌های قدیمی"""
    try:
        if db_manager:
            with db_manager.get_session() as session:
                # پاکسازی سیگنال‌های منقضی
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
        if market:
            tickers = asyncio.run(market.get_all_prices())
            if cache:
                cache.set('market_data', tickers)
    except:
        pass

# ==================== مدیریت خطا ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """مدیریت خطاهای سراسری"""
    global ERROR_COUNT
    
    ERROR_COUNT += 1
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "time": time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """مدیریت خطاهای HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "time": time_manager.now_persian() if time_manager else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    )

# ==================== سرور ====================

class ServerManager:
    """مدیریت سرور FastAPI"""
    
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = int(os.environ.get("PORT", 8080))
        self.server = None
        self._running = False
    
    async def start(self):
        """شروع سرور"""
        self._running = True
        
        config_uvicorn = uvicorn.Config(
            "bot13:app",
            host=self.host,
            port=self.port,
            log_level="error",
            access_log=False,
            loop="asyncio",
            timeout_keep_alive=30
        )
        
        self.server = uvicorn.Server(config_uvicorn)
        await self.server.serve()
    
    async def stop(self):
        """توقف سرور"""
        self._running = False
        if self.server:
            self.server.should_exit = True

# ==================== اجرا ====================

server_manager = ServerManager()

def get_server() -> ServerManager:
    return server_manager

if __name__ == "__main__":
    import asyncio
    asyncio.run(server_manager.start())

# ==================== Export ====================

__all__ = [
    'app',
    'server_manager',
    'get_server',
    'HealthResponse',
    'StatsResponse',
    'PriceResponse',
    'SignalResponse'
]
