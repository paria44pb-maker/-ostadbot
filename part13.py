#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="CryptoPulse AI API")

# ==================== داده‌های نمونه ====================

SIGNALS = {
    "BTC": {"signal": "buy", "confidence": 72, "price": 67845.32, "targets": [68578.12, 70123.45, 72456.78], "stop_loss": 65312.45},
    "ETH": {"signal": "hold", "confidence": 55, "price": 3456.78, "targets": [3500.00, 3600.00], "stop_loss": 3350.00},
    "BNB": {"signal": "sell", "confidence": 68, "price": 567.89, "targets": [550.00, 530.00], "stop_loss": 585.00}
}

PRICES = {
    "BTC": 67845.32, "ETH": 3456.78, "BNB": 567.89, "SOL": 145.67, "XRP": 0.5678,
    "ADA": 0.4567, "DOGE": 0.1234, "DOT": 7.89, "MATIC": 0.6789, "SHIB": 0.00002345
}

# ==================== مسیرها ====================

@app.get("/")
async def root():
    return {"status": "online", "name": "CryptoPulse AI", "version": "3.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/price/{coin}")
async def get_price(coin: str):
    coin = coin.upper()
    if coin not in PRICES:
        raise HTTPException(404, f"Coin {coin} not found")
    return {"coin": coin, "price": PRICES[coin], "time": "2026-06-30"}

@app.get("/api/v1/signal/{coin}")
async def get_signal(coin: str):
    coin = coin.upper()
    if coin not in SIGNALS:
        raise HTTPException(404, f"Signal for {coin} not available")
    return SIGNALS[coin]

@app.get("/api/v1/market")
async def get_market():
    return {"tickers": PRICES, "count": len(PRICES)}

# ==================== اجرا ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
