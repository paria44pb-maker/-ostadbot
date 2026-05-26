#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 LIVE FOREX — APIهای بین‌المللی + تبدیل به تومان
📅 تاریخ شمسی | ⏰ ساعت تهران | 🔄 هر ۳ ثانیه
"""

import os, sys, subprocess, time
from datetime import datetime, timedelta

for pkg in ['httpx', 'jdatetime', 'pytz']:
    try: __import__(pkg)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import httpx
import jdatetime
import pytz

TEHRAN_TZ = pytz.timezone('Asia/Tehran')

def now_tehran(): return datetime.now(TEHRAN_TZ)
def shamsi():
    n = now_tehran(); j = jdatetime.datetime.fromgregorian(datetime=n)
    months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
    days = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
    return f"{days[n.weekday()]} {j.day} {months[j.month-1]} {j.year}"
def now_time(): return now_tehran().strftime('%H:%M:%S')

def get_prices():
    """دریافت قیمت از APIهای بین‌المللی"""
    prices = {}
    client = httpx.Client(timeout=15.0)
    
    try:
        # ۱. قیمت دلار آزاد (از exchange-rate API)
        r = client.get("https://open.er-api.com/v6/latest/USD")
        if r.status_code == 200:
            data = r.json()
            rates = data.get('rates', {})
            
            # قیمت‌های جهانی
            prices['eur_usd'] = rates.get('EUR', 0.92)
            prices['gbp_usd'] = rates.get('GBP', 0.78)
            prices['try_usd'] = rates.get('TRY', 32.5)
            prices['iqd_usd'] = rates.get('IQD', 1310)
            
            # تبدیل به تومان (با نرخ تقریبی)
            # میتونی نرخ رو دستی تنظیم کنی
            USD_TO_TOMAN = 70000  # ← اینو هر وقت خواستی عوض کن
            
            prices['دلار'] = USD_TO_TOMAN
            prices['یورو'] = int(USD_TO_TOMAN * rates.get('EUR', 0.92))
            prices['پوند'] = int(USD_TO_TOMAN * rates.get('GBP', 0.78))
            prices['لیر'] = int(USD_TO_TOMAN / rates.get('TRY', 32.5))
            prices['دینار'] = int(USD_TO_TOMAN / rates.get('IQD', 1310))
    
    except Exception as e:
        prices['error'] = str(e)
    
    try:
        # ۲. قیمت طلا (انس جهانی)
        r = client.get("https://api.metals.live/v1/spot/gold")
        if r.status_code == 200:
            data = r.json()
            gold_oz = data[0].get('price', 0) if isinstance(data, list) and len(data) > 0 else 0
            if gold_oz > 0:
                # تبدیل انس به قیمت مثقال و گرم
                usd_toman = prices.get('دلار', 70000)
                gold_gram_usd = gold_oz / 31.1035
                gold_gram_toman = int(gold_gram_usd * usd_toman)
                prices['طلای ۲۴ (هر گرم)'] = gold_gram_toman
                prices['انس طلا (دلار)'] = int(gold_oz)
                prices['مثقال طلا'] = int(gold_gram_toman * 4.608)
    except Exception as e:
        prices['gold_error'] = str(e)
    
    client.close()
    return prices

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("🚀 اتصال به APIهای جهانی...")
    
    while True:
        try:
            clear()
            prices = get_prices()
            
            print("🟢" + "═" * 50 + "🟢")
            print("║" + " " * 12 + "💰 قیمت زنده بازار 💰" + " " * 12 + "║")
            print("🟢" + "═" * 50 + "🟢")
            print(f"📅 {shamsi()}")
            print(f"⏰ ساعت: {now_time()} | 📍 تهران")
            print(f"📡 منبع: APIهای جهانی (exchange-rate + metals)")
            print("═" * 52)
            
            print("\n  💵 ارزها (تومان):")
            print("  " + "─" * 48)
            for key in ['دلار', 'یورو', 'پوند', 'لیر', 'دینار']:
                if key in prices:
                    print(f"    • {key}: {prices[key]:,} تومان")
            
            print("\n  🥇 طلا:")
            print("  " + "─" * 48)
            for key in ['انس طلا (دلار)', 'طلای ۲۴ (هر گرم)', 'مثقال طلا']:
                if key in prices:
                    if 'دلار' in key:
                        print(f"    • {key}: ${prices[key]:,}")
                    else:
                        print(f"    • {key}: {prices[key]:,} تومان")
            
            if 'error' in prices:
                print(f"\n  ⚠️ خطا: {prices['error'][:80]}")
            
            print("\n" + "🟢" + "═" * 50 + "🟢")
            print(f"  ⚠️ نرخ دلار دستی: {prices.get('دلار', 70000):,} تومان")
            print(f"  🔄 بروزرسانی: هر ۳ ثانیه | ⏰ {now_time()}")
            
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n\n👋 خروج...")
            break
        except Exception as e:
            print(f"\n❌ {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
