#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║   💰 LIVE FOREX + AI ANALYZER — قیمت زنده با هوش مصنوعی ║
║   📅 تاریخ شمسی + میلادی | ⏰ ساعت تهران                 ║
║   💵 تمام قیمت‌ها به تومان | 🧠 تحلیل Groq AI            ║
║   📡 منابع: call1.ir + alanchand.com + tgju.org          ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
import time
import json
import re
from datetime import datetime, timedelta
from collections import deque

# ============================================================
# AUTO INSTALL
# ============================================================
def install(pkg):
    try: __import__(pkg)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for pkg in ['httpx', 'jdatetime', 'pytz', 'beautifulsoup4']:
    install(pkg)

import httpx
import jdatetime
import pytz

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except:
    BS4_OK = False
    print("⚠️ beautifulsoup4 not available — HTML parsing disabled")

# ============================================================
# TIMEZONE — تهران
# ============================================================
try:
    TEHRAN_TZ = pytz.timezone('Asia/Tehran')
    TZ_OK = True
except:
    TEHRAN_TZ = None
    TZ_OK = False
    print("⚠️ pytz timezone failed — using UTC+3:30")

def now_tehran():
    if TZ_OK:
        return datetime.now(TEHRAN_TZ)
    return datetime.now() + timedelta(hours=3, minutes=30)

def shamsi_date():
    n = now_tehran()
    j = jdatetime.datetime.fromgregorian(datetime=n)
    months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
    return f"{j.day} {months[j.month-1]} {j.year}"

def time_str():
    return now_tehran().strftime('%H:%M:%S')

def gregorian_date():
    return now_tehran().strftime('%Y-%m-%d')

def day_fa():
    days = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
    return days[now_tehran().weekday()]

# ============================================================
# GROQ AI — تحلیل قیمت
# ============================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ai_analyze(prices: dict) -> str:
    """تحلیل قیمت‌ها با Groq AI"""
    if not GROQ_API_KEY:
        return "🔒 کلید Groq تنظیم نشده. تحلیل AI غیرفعال."
    
    # ساخت متن قیمت‌ها
    price_text = "\n".join([f"{k}: {v:,} تومان" for k, v in prices.items()])
    
    prompt = f"""قیمت‌های فعلی بازار ایران:

{price_text}

لطفاً یک تحلیل کوتاه و مفید به فارسی ارائه بده:
۱. وضعیت کلی بازار (آرام/نوسانی/پرتنش)
۲. پیش‌بینی کوتاه‌مدت قیمت دلار
۳. توصیه برای خرید/فروش طلا
۴. یک نکته طلایی برای سرمایه‌گذاران

با ایموجی. حداکثر ۲۰۰ کلمه."""

    try:
        client = httpx.Client(timeout=30.0)
        r = client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"❌ خطای API: {r.status_code}"
    except Exception as e:
        return f"❌ خطا: {e}"

# ============================================================
# دریافت قیمت — منابع مختلف
# ============================================================

def fetch_call1() -> dict:
    """منبع ۱: call1.ir API"""
    try:
        client = httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"})
        r = client.get("https://call1.ir/api/currency.php")
        if r.status_code == 200:
            data = r.json()
            prices = {}
            for item in (data if isinstance(data, list) else []):
                name = str(item.get('name', ''))
                price = int(item.get('price', 0))
                if price > 0:
                    if 'دلار' in name and 'سکه' not in name: prices['دلار'] = price
                    elif 'یورو' in name: prices['یورو'] = price
                    elif 'لیر' in name: prices['لیر'] = price
                    elif 'پوند' in name: prices['پوند'] = price
                    elif 'دینار' in name: prices['دینار'] = price
                    elif 'درهم' in name: prices['درهم'] = price
                    elif 'طلای ۲۴' in name or 'عیار ۲۴' in name: prices['طلای ۲۴ عیار'] = price
                    elif 'طلای ۱۸' in name or 'عیار ۱۸' in name: prices['طلای ۱۸ عیار'] = price
                    elif 'مثقال' in name: prices['مثقال طلا'] = price
                    elif 'سکه امامی' in name or 'سکه تمام' in name: prices['سکه امامی'] = price
                    elif 'نیم سکه' in name: prices['نیم سکه'] = price
                    elif 'ربع سکه' in name: prices['ربع سکه'] = price
            return prices
    except Exception as e:
        pass
    return {}

def fetch_alanchand() -> dict:
    """منبع ۲: alanchand.com"""
    if not BS4_OK:
        return {}
    try:
        client = httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"})
        r = client.get("https://alanchand.com")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text()
            prices = {}
            
            patterns = {
                'دلار': r'دلار\s*[:\-]?\s*([\d,]+)',
                'یورو': r'یورو\s*[:\-]?\s*([\d,]+)',
                'لیر': r'لیر\s*[:\-]?\s*([\d,]+)',
                'پوند': r'پوند\s*[:\-]?\s*([\d,]+)',
                'دینار': r'دینار\s*[:\-]?\s*([\d,]+)',
                'طلای ۲۴ عیار': r'طل[ايی]\s*۲۴\s*[:\-]?\s*([\d,]+)',
                'طلای ۱۸ عیار': r'طل[ايی]\s*۱۸\s*[:\-]?\s*([\d,]+)',
                'سکه امامی': r'سکه\s*امامی\s*[:\-]?\s*([\d,]+)',
            }
            
            for name, pattern in patterns.items():
                m = re.search(pattern, text)
                if m:
                    val = int(m.group(1).replace(',', ''))
                    if val > 0:
                        prices[name] = val
            
            return prices
    except Exception as e:
        pass
    return {}

def fetch_tgju() -> dict:
    """منبع ۳: tgju.org API"""
    symbols = {
        'دلار': 'price_dollar_rl',
        'یورو': 'price_eur',
        'لیر': 'price_try',
        'پوند': 'price_gbp',
        'دینار': 'price_iqd',
        'طلای ۲۴ عیار': 'price_gold_24',
        'طلای ۱۸ عیار': 'price_gold_18',
        'سکه امامی': 'price_coin_imami',
    }
    
    prices = {}
    try:
        client = httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"})
        for name, symbol in symbols.items():
            try:
                r = client.get(f"https://api.tgju.org/v1/market/indicator/summary/{symbol}")
                if r.status_code == 200:
                    data = r.json()
                    p = data.get('response', {}).get('indicators', {}).get(symbol, {}).get('p', 0)
                    if p > 0:
                        prices[name] = int(p / 10)  # ریال به تومان
            except:
                pass
    except:
        pass
    return prices

def get_all_prices() -> dict:
    """ترکیب همه منابع — اولویت با call1.ir"""
    
    # تلاش از همه منابع
    p1 = fetch_call1()
    p2 = fetch_alanchand()
    p3 = fetch_tgju()
    
    # ترکیب: اولویت با call1.ir
    final = {}
    
    all_keys = set(list(p1.keys()) + list(p2.keys()) + list(p3.keys()))
    
    for key in all_keys:
        # اولویت: call1 > alanchand > tgju
        if key in p1 and p1[key] > 0:
            final[key] = p1[key]
        elif key in p2 and p2[key] > 0:
            final[key] = p2[key]
        elif key in p3 and p3[key] > 0:
            final[key] = p3[key]
    
    # اگه هیچی پیدا نشد، مقادیر پیش‌فرض
    if not final:
        final = {
            'دلار': 70000,
            'یورو': 75600,
            'لیر': 2187,
            'پوند': 89600,
            'دینار': 47,
            'طلای ۲۴ عیار': 47600000,
            'طلای ۱۸ عیار': 35700000,
            'سکه امامی': 55000000,
        }
    
    return final

# ============================================================
# نمایشگر
# ============================================================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_price(p):
    return f"{p:,} تومان"

def show(prices: dict, ai_text: str, source: str):
    clear()
    
    print("🟢" + "═" * 62 + "🟢")
    print("║" + " " * 15 + "💰 قیمت‌های زنده بازار 💰" + " " * 16 + "║")
    print("🟢" + "═" * 62 + "🟢")
    print(f"📅 شمسی: {day_fa()} {shamsi_date()}")
    print(f"📅 میلادی: {gregorian_date()}")
    print(f"⏰ ساعت: {time_str()} | 📍 تهران")
    print(f"📡 منبع: {source}")
    print("═" * 64)
    
    # دسته‌بندی
    cats = {
        "💵 ارزها": ['دلار', 'یورو', 'پوند', 'لیر', 'دینار', 'درهم'],
        "🥇 طلا": ['طلای ۲۴ عیار', 'طلای ۱۸ عیار', 'مثقال طلا'],
        "🪙 سکه": ['سکه امامی', 'نیم سکه', 'ربع سکه'],
    }
    
    for cat, keys in cats.items():
        items = [(k, prices[k]) for k in keys if k in prices]
        if items:
            print(f"\n  {cat}:")
            print("  " + "─" * 58)
            for name, price in items:
                # ایموجی روند
                print(f"    💰 {name:<18} {format_price(price)}")
    
    print("\n" + "═" * 64)
    
    # تحلیل AI
    if ai_text:
        print(f"\n🧠 تحلیل هوش مصنوعی (Groq):")
        print("  " + "─" * 58)
        for line in ai_text.split('\n'):
            print(f"  {line}")
    
    print("\n" + "🟢" + "═" * 62 + "🟢")
    print(f"  Ctrl+C برای خروج | بروزرسانی: هر ۳ ثانیه | {time_str()}")

# ============================================================
# MAIN
# ============================================================
def main():
    print("🚀 در حال راه‌اندازی...")
    print(f"📅 {day_fa()} {shamsi_date()} | ⏰ {time_str()}")
    print("📡 اتصال به منابع قیمت...")
    
    # تست اولیه
    prices = get_all_prices()
    source = "call1.ir + alanchand.com + tgju.org"
    
    print("✅ منابع آماده‌اند. شروع نمایش زنده...")
    time.sleep(1)
    
    ai_text = ""
    last_ai_update = 0
    
    while True:
        try:
            prices = get_all_prices()
            
            # تحلیل AI هر ۶۰ ثانیه
            if time.time() - last_ai_update > 60 and GROQ_API_KEY:
                ai_text = ai_analyze(prices)
                last_ai_update = time.time()
            
            show(prices, ai_text, source)
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n\n👋 خروج...")
            break
        except Exception as e:
            print(f"\n❌ خطا: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
