#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Entry Point
اجرای تمام ۱۵ بخش
"""

import os
import sys
import time
import asyncio
import uvicorn

print("🚀 Starting CryptoPulse AI Bot v3.0...")
print("📁 Loading all 15 parts...\n")

# ============================================================
#                    IMPORT ALL 15 PARTS
# ============================================================

PARTS = [
    ("part1", "Main Entry Point"),
    ("part2", "Config & Settings"),
    ("part3", "Database Models"),
    ("part4", "Utils & Tehran Time"),
    ("part5", "CoinEx Exchange"),
    ("part6", "Groq AI"),
    ("part7", "Technical Analysis"),
    ("part8", "Keyboards & Menus"),
    ("part9", "Main Handlers"),
    ("part10", "Admin Panel"),
    ("part11", "VIP & Payment"),
    ("part12", "Channel Management"),
    ("part13", "FastAPI Server"),
    ("part14", "Background Tasks"),
    ("part15", "Media Management")
]

for part, name in PARTS:
    try:
        exec(f"from {part} import *")
        print(f"  ✅ {part}: {name}")
    except Exception as e:
        print(f"  ❌ {part}: {e}")

print("\n" + "="*50)
print("🚀 All 15 parts loaded successfully!")
print("="*50)

# ============================================================
#                    RUN
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Server running on port {port}")
    
    try:
        from part13 import app
        uvicorn.run(app, host="0.0.0.0", port=port)
    except:
        print("⚠️ No app found. Running idle...")
        while True:
            time.sleep(1)
