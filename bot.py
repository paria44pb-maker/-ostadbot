#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Simple Entry Point
"""

import os
import sys
import time

print("🚀 Starting CryptoPulse AI Bot...")

# ============================================================
#                    SIMPLE FASTAPI SERVER
# ============================================================

from fastapi import FastAPI
import uvicorn

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

# ============================================================
#                    IMPORT ALL PARTS (با مدیریت خطا)
# ============================================================

print("📁 Loading all 15 parts...")

parts = [
    ("Part 1", "Main Entry Point"),
    ("Part 2", "Config & Settings"),
    ("Part 3", "Database Models"),
    ("Part 4", "Utils & Tehran Time"),
    ("Part 5", "CoinEx Exchange"),
    ("Part 6", "Groq AI"),
    ("Part 7", "Technical Analysis"),
    ("Part 8", "Keyboards & Menus"),
    ("Part 9", "Main Handlers"),
    ("Part 10", "Admin Panel"),
    ("Part 11", "VIP & Payment"),
    ("Part 12", "Channel Management"),
    ("Part 13", "FastAPI Server"),
    ("Part 14", "Background Tasks"),
    ("Part 15", "Media Management")
]

for num, name in parts:
    try:
        exec(f"from part{num.split()[1]} import *")
        print(f"  ✅ {num}: {name}")
    except Exception as e:
        print(f"  ❌ {num}: {e}")

print("\n" + "="*50)
print("🚀 All parts loaded!")
print("="*50)

# ============================================================
#                    RUN
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Server running on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
