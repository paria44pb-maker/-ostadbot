import json
import logging
import sys
import os
import time
import hmac
import hashlib
import random
import numpy as np
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== تنظیمات پیشرفته Railway Logging ====================
class CustomRailwayLogFormatter(logging.Formatter):
    """فرمت‌کننده JSON برای تشخیص سطح لاگ توسط Railway"""
    def format(self, record):
        log_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        return json.dumps(log_record)

def get_railway_logger():
    """پیکربندی لاگر برای نمایش صحیح در Railway"""
    railway_logger = logging.getLogger()
    railway_logger.setLevel(logging.INFO)
    
    # حذف هندلرهای قبلی (اگر وجود داشته باشند)
    for handler in railway_logger.handlers[:]:
        railway_logger.removeHandler(handler)
    
    # ایجاد هندلر جدید برای stdout با فرمت JSON
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomRailwayLogFormatter()
    console_handler.setFormatter(formatter)
    railway_logger.addHandler(console_handler)
    
    # تنظیم سطح httpx به WARNING برای کاهش نویز لاگ‌ها
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return railway_logger

# راه‌اندازی لاگر
logger = get_railway_logger()

# ==================== متغیرهای محیطی و تنظیمات اصلی ====================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@comedyclick")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")

SYMBOLS = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

# ==================== بقیه کد ربات شما (بدون تغییر) ====================
# ... توابع coinex_sign, coinex_request, get_coinex_price و بقیه توابع اینجا قرار می‌گیرند ...
