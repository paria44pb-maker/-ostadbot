import os
import json
import logging
import hmac
import hashlib
from flask import Flask, request, jsonify
import threading
import numpy as np
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx
import asyncio
from functools import wraps

# تنظیمات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-key-here")

# ========== Flask Webhook Server برای تریدینگ ویو ==========
flask_app = Flask(__name__)

# ذخیره سیگنال‌های دریافتی
signal_queue = []
bot_instance = None

def verify_webhook_signature(data, signature):
    """بررسی صحت سیگنال تریدینگ ویو"""
    if not signature:
        return False
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@flask_app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """دریافت سیگنال از تریدینگ ویو"""
    try:
        # دریافت داده
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
        
        logger.info(f"📡 سیگنال دریافتی از تریدینگ ویو: {data}")
        
        # بررسی احراز هویت
        signature = request.headers.get('X-Signature', '')
        if WEBHOOK_SECRET and WEBHOOK_SECRET != "your-secret-key-here":
            raw_data = request.get_data(as_text=True)
            if not verify_webhook_signature(raw_data, signature):
                logger.warning("❌ امضای نامعتبر")
                return jsonify({"error": "Invalid signature"}), 401
        
        # استخراج اطلاعات سیگنال
        signal = {
            "symbol": data.get("symbol", "BTCUSDT"),
            "action": data.get("action", data.get("side", data.get("message", "unknown"))),
            "price": data.get("price", data.get("close", 0)),
            "quantity": data.get("quantity", 0.01),
            "stop_loss": data.get("stop_loss", 0),
            "take_profit": data.get("take_profit", 0),
            "strategy": data.get("strategy", "unknown"),
            "timeframe": data.get("timeframe", "1h"),
            "timestamp": datetime.now().isoformat(),
            "raw": data
        }
        
        # عادی‌سازی action
        action_lower = str(signal["action"]).lower()
        if "buy" in action_lower or "long" in action_lower:
            signal["action"] = "BUY"
        elif "sell" in action_lower or "short" in action_lower:
            signal["action"] = "SELL"
        elif "close" in action_lower:
            signal["action"] = "CLOSE"
        else:
            signal["action"] = "HOLD"
        
        # ذخیره سیگنال
        signal_queue.append(signal)
        
        # ارسال به تلگرام
        if bot_instance:
            asyncio.create_task(send_signal_to_telegram(signal))
        
        return jsonify({"status": "ok", "signal": signal}), 200
        
    except Exception as e:
        logger.error(f"خطا در پردازش سیگنال: {e}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/webhook/health', methods=['GET'])
def health_check():
    """بررسی سلامت وب‌هوک"""
    return jsonify({
        "status": "ok",
        "signals_received": len(signal_queue),
        "timestamp": datetime.now().isoformat()
    })

async def send_signal_to_telegram(signal):
    """ارسال سیگنال دریافتی به تلگرام"""
    if not bot_instance:
        return
    
    emoji = "🟢" if signal["action"] == "BUY" else "🔴" if signal["action"] == "SELL" else "⚪"
    text = f"""
{emoji} **سیگنال جدید از تریدینگ ویو** {emoji}

📊 **نماد:** {signal['symbol']}
🎯 **اقدام:** {signal['action']}
💰 **قیمت:** ${signal['price']:,.0f if signal['price'] else 'نامشخص'}
📈 **استراتژی:** {signal['strategy']}
⏰ **تایم‌فریم:** {signal['timeframe']}

---
📌 برای دریافت سیگنال‌های بیشتر، تنظیمات تریدینگ ویو رو بررسی کن.
"""
    
    try:
        await bot_instance.application.bot.send_message(
            chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"خطا در ارسال به تلگرام: {e}")

def start_webhook_server():
    """اجرای سرور فلاسک در یک ترد جداگانه"""
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ========== ربات اصلی تلگرام ==========
class TradingBot:
    def __init__(self):
        self.application = None
        self.received_signals = []
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
            [InlineKeyboardButton("🎯 سیگنال", callback_data="signals")],
            [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
            [InlineKeyboardButton("📡 سیگنال‌های تریدینگ ویو", callback_data="tv_signals")],
            [InlineKeyboardButton("⚙️ تنظیمات وب‌هوک", callback_data="webhook_settings")],
            [InlineKeyboardButton("💰 پرتفوی", callback_data="portfolio")],
            [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ]
        
        text = """
🔥 **ربات تریدر حرفه‌ای + تریدینگ ویو** 🔥

✅ **قابلیت‌های جدید:**
• 📡 دریافت خودکار سیگنال از تریدینگ ویو
• 🔗 وب‌هوک امن با امضای HMAC
• 📊 پشتیبانی از تمام استراتژی‌های تریدینگ ویو
• 🎯 اجرای خودکار سیگنال‌ها (اختیاری)

---
📌 **تنظیمات تریدینگ ویو:**
Webhook URL: `https://your-domain/webhook/tradingview`
Secret Key: `{WEBHOOK_SECRET[:10]}...`

---
📌 از منوی زیر انتخاب کن 👇
"""
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def tv_signals_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش سیگنال‌های دریافتی از تریدینگ ویو"""
        if not signal_queue:
            text = """
📡 **سیگنال‌های تریدینگ ویو**

هنوز سیگنالی دریافت نشده.

📌 **تنظیمات در تریدینگ ویو:**
1. در استراتژی خود Alert ایجاد کن
2. Webhook URL رو تنظیم کن:
   `https://your-railway-app.railway.app/webhook/tradingview`
3. Message رو به این فرمت بفرست:

```json
{
    "symbol": "BTCUSDT",
    "action": "buy",
    "price": {{close}},
    "stop_loss": {{plot("SL")}},
    "take_profit": {{plot("TP")}},
    "strategy": "SuperTrend",
    "timeframe": "1h"
}
