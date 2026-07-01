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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
