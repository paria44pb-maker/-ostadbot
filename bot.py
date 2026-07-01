from fastapi import FastAPI
import uvicorn
import os
import time

app = FastAPI(title="CryptoPulse AI", version="3.0.0")

@app.get("/")
async def root():
    return {
        "status": "online",
        "name": "CryptoPulse AI",
        "version": "3.0.0",
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/v1/price/{coin}")
async def get_price(coin: str):
    return {
        "coin": coin.upper(),
        "price": 67845.32,
        "change": 2.34,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/v1/signal/{coin}")
async def get_signal(coin: str):
    return {
        "coin": coin.upper(),
        "signal": "buy",
        "confidence": 72,
        "price": 67845.32,
        "targets": [68578.12, 70123.45],
        "stop_loss": 65312.45,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
