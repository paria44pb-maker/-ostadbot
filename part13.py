#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - FastAPI Server Module
ماژول سرور FastAPI با پشتیبانی از Webhook و API
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from bot2 import get_config
from bot3 import db_manager
from bot4 import get_time
from bot5 import get_market
from bot6 import get_ai
from bot8 import LuxEmoji

config = get_config()
time_manager = get_time()
market = get_market()
ai_manager = get_ai()

# ==================== FastAPI App ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """مدیریت چرخه حیات سرور"""
    print("🚀 Starting CryptoPulse AI Server...")
    yield
    print("🛑 Shutting down CryptoPulse AI Server...")

app = FastAPI(
    title="CryptoPulse AI API",
    description="API for CryptoPulse AI Trading Bot",
    version="3.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Routes ====================

@app.get("/")
async def root():
    """صفحه اصلی"""
    return {
        "status": "online",
        "name": "CryptoPulse AI",
        "version": "3.0.0",
        "time": time_manager.now_persian(),
        "channel": "@CryptoPulse606"
    }

@app.get("/health")
async def health_check():
    """بررسی سلامت"""
    db_health = db_manager.health_check()
    
    return {
        "status": "healthy" if db_health['connected'] else "unhealthy",
        "database": db_health,
        "uptime": "3 days 12 hours",
        "time": time_manager.now_persian()
    }

@app.get("/stats")
async def get_stats():
    """دریافت آمار"""
    stats = db_manager.get_stats()
    
    return {
        "users": {
            "total": stats.get('users', 0),
            "active": stats.get('active_users', 0),
            "vip": stats.get('vip_users', 0),
            "banned": stats.get('banned_users', 0)
        },
        "signals": {
            "total": stats.get('signals', 0),
            "active": stats.get('active_signals', 0),
            "vip": stats.get('vip_signals', 0)
        },
        "payments": {
            "total": stats.get('payments', 0),
            "pending": stats.get('pending_payments', 0),
            "revenue": stats.get('total_revenue', 0)
        },
        "time": time_manager.now_persian()
    }

@app.get("/api/v1/price/{coin}")
async def get_price(coin: str):
    """دریافت قیمت ارز"""
    ticker = await market.get_market_data(coin.upper())
    if ticker:
        return {
            "coin": coin.upper(),
            "price": ticker.price,
            "change_24h": ticker.change_24h,
            "high_24h": ticker.high_24h,
            "low_24h": ticker.low_24h,
            "volume_24h": ticker.volume_24h,
            "time": time_manager.now_persian()
        }
    return {"error": "Coin not found"}

@app.get("/api/v1/signal/{coin}")
async def get_signal(coin: str):
    """دریافت سیگنال"""
    signal = await market.get_signal(coin.upper(), "4h")
    if signal:
        return {
            "coin": coin.upper(),
            "signal": signal.get('signal', 'hold'),
            "confidence": signal.get('confidence', 50),
            "price": signal.get('current_price', 0),
            "targets": signal.get('targets', []),
            "stop_loss": signal.get('stop_loss', 0),
            "time": time_manager.now_persian()
        }
    return {"error": "Signal not available"}

@app.get("/api/v1/market")
async def get_market_data():
    """دریافت داده‌های بازار"""
    tickers = await market.get_all_prices()
    return {
        "tickers": tickers,
        "count": len(tickers),
        "time": time_manager.now_persian()
    }

@app.post("/webhook")
async def webhook(request: Request):
    """Webhook برای تلگرام"""
    try:
        data = await request.json()
        # پردازش آپدیت
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}

@app.get("/admin/stats")
async def admin_stats():
    """آمار پیشرفته برای ادمین"""
    stats = db_manager.get_stats()
    return {
        "users": stats,
        "time": time_manager.now_persian()
    }

# ==================== Error Handlers ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """مدیریت خطاهای سراسری"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "time": time_manager.now_persian()
        }
    )

# ==================== Server Manager ====================

class ServerManager:
    """مدیریت سرور"""
    
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = config.get('port', 8080)
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
            access_log=False
        )
        self.server = uvicorn.Server(config_uvicorn)
        await self.server.serve()
    
    async def stop(self):
        """توقف سرور"""
        self._running = False
        if self.server:
            self.server.should_exit = True

# ==================== Export ====================

server_manager = ServerManager()

def get_server() -> ServerManager:
    return server_manager
