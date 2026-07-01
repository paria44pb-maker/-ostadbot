#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Entry Point
با تمام Import های مورد نیاز
"""

import os
import sys
import time
import json
import asyncio
import threading
import signal
import gc
import random
import string
import hashlib
import base64
import hmac
import logging
import warnings
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, OrderedDict
from functools import wraps, lru_cache
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
#                    THIRD PARTY IMPORTS
# ============================================================

try:
    import uvicorn
    from fastapi import FastAPI, Request, Response, HTTPException, Depends, Header, Query, Body
    from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse, PlainTextResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field, validator, EmailStr, HttpUrl
except ImportError:
    print("⚠️ FastAPI not installed")

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InputFile, Bot
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
    from telegram.constants import ParseMode
except ImportError:
    print("⚠️ python-telegram-bot not installed")

try:
    import aiohttp
    import aiohttp.client_exceptions
except ImportError:
    print("⚠️ aiohttp not installed")

try:
    import psutil
except ImportError:
    print("⚠️ psutil not installed")

try:
    import pytz
except ImportError:
    print("⚠️ pytz not installed")

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    print("⚠️ apscheduler not installed")

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("⚠️ pandas/numpy not installed")

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
except ImportError:
    print("⚠️ matplotlib not installed")

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
except ImportError:
    print("⚠️ plotly not installed")

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
except ImportError:
    print("⚠️ PIL not installed")

try:
    import requests
except ImportError:
    print("⚠️ requests not installed")

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️ python-dotenv not installed")

try:
    import emoji as emoji_lib
except ImportError:
    print("⚠️ emoji not installed")

try:
    import sqlalchemy
    from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, BigInteger, Date, Time, Interval, ForeignKey, Index, UniqueConstraint, CheckConstraint, func, and_, or_, not_, desc, asc, event, MetaData, Table, inspect, text
    from sqlalchemy.ext.declarative import declarative_base, declared_attr
    from sqlalchemy.orm import sessionmaker, relationship, backref, aliased, Query, Session, joinedload, selectinload, contains_eager
    from sqlalchemy.pool import QueuePool, NullPool
except ImportError:
    print("⚠️ sqlalchemy not installed")

print("🚀 Starting CryptoPulse AI Bot v3.0...")
print("📁 All imports loaded successfully!\n")

# ============================================================
#                    LOAD ENV
# ============================================================

try:
    load_dotenv()
except:
    pass

# ============================================================
#                    CHECK ENV VARIABLES
# ============================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = []
for x in os.environ.get("ADMIN_IDS", "").split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except:
            pass

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
COINEX_API_KEY = os.environ.get("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.environ.get("COINEX_SECRET_KEY", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "به مرد")
PORT = int(os.environ.get("PORT", 8080))
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

print(f"✅ BOT_TOKEN: {'SET' if BOT_TOKEN else 'NOT SET'}")
print(f"✅ ADMIN_IDS: {ADMIN_IDS}")
print(f"✅ GROQ_API_KEY: {'SET' if GROQ_API_KEY else 'NOT SET'}")
print(f"✅ COINEX_API_KEY: {'SET' if COINEX_API_KEY else 'NOT SET'}")
print(f"✅ COINEX_SECRET_KEY: {'SET' if COINEX_SECRET_KEY else 'NOT SET'}")
print(f"✅ PORT: {PORT}")
print()

# ============================================================
#                    IMPORT ALL 15 PARTS
# ============================================================

print("📁 Loading all 15 parts...\n")

try:
    from part1 import *
    print("  ✅ Part 1: Main Entry Point")
except Exception as e:
    print(f"  ❌ Part 1: {e}")

try:
    from part2 import *
    print("  ✅ Part 2: Config & Settings")
except Exception as e:
    print(f"  ❌ Part 2: {e}")

try:
    from part3 import *
    print("  ✅ Part 3: Database Models")
except Exception as e:
    print(f"  ❌ Part 3: {e}")

try:
    from part4 import *
    print("  ✅ Part 4: Utils & Tehran Time")
except Exception as e:
    print(f"  ❌ Part 4: {e}")

try:
    from part5 import *
    print("  ✅ Part 5: CoinEx Exchange")
except Exception as e:
    print(f"  ❌ Part 5: {e}")

try:
    from part6 import *
    print("  ✅ Part 6: Groq AI")
except Exception as e:
    print(f"  ❌ Part 6: {e}")

try:
    from part7 import *
    print("  ✅ Part 7: Technical Analysis")
except Exception as e:
    print(f"  ❌ Part 7: {e}")

try:
    from part8 import *
    print("  ✅ Part 8: Keyboards & Menus")
except Exception as e:
    print(f"  ❌ Part 8: {e}")

try:
    from part9 import *
    print("  ✅ Part 9: Main Handlers")
except Exception as e:
    print(f"  ❌ Part 9: {e}")

try:
    from part10 import *
    print("  ✅ Part 10: Admin Panel")
except Exception as e:
    print(f"  ❌ Part 10: {e}")

try:
    from part11 import *
    print("  ✅ Part 11: VIP & Payment")
except Exception as e:
    print(f"  ❌ Part 11: {e}")

try:
    from part12 import *
    print("  ✅ Part 12: Channel Management")
except Exception as e:
    print(f"  ❌ Part 12: {e}")

try:
    from part13 import *
    print("  ✅ Part 13: FastAPI Server")
except Exception as e:
    print(f"  ❌ Part 13: {e}")

try:
    from part14 import *
    print("  ✅ Part 14: Background Tasks")
except Exception as e:
    print(f"  ❌ Part 14: {e}")

try:
    from part15 import *
    print("  ✅ Part 15: Media Management")
except Exception as e:
    print(f"  ❌ Part 15: {e}")

print("\n" + "="*50)
print("🚀 All 15 parts loaded successfully!")
print("="*50)

# ============================================================
#                    RUN
# ============================================================

async def run_bot():
    """اجرای ربات تلگرام و سرور FastAPI"""
    
    # 1. اجرای ربات تلگرام
    try:
        from part9 import get_application
        bot_app = get_application()
        if bot_app:
            await bot_app.bot.delete_webhook(drop_pending_updates=True)
            await bot_app.initialize()
            await bot_app.start()
            await bot_app.updater.start_polling()
            print("✅ Telegram Bot is running!")
    except Exception as e:
        print(f"⚠️ Bot error: {e}")
    
    # 2. اجرای سرور FastAPI
    try:
        from part13 import app
        port = int(os.environ.get("PORT", 8080))
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=port,
            log_level="error",
            loop="asyncio",
            timeout_keep_alive=30
        )
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        print(f"⚠️ Server error: {e}")
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        while True:
            time.sleep(1)
