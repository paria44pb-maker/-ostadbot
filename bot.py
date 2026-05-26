#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 LIVE FOREX — فقط call1.ir | قیمت زنده به تومان
📅 تاریخ شمسی | ⏰ ساعت تهران | 🔄 هر ۳ ثانیه
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime, timedelta

# ============================================================
# نصب خودکار
# ============================================================
for pkg in ['httpx', 'jdatetime', 'pytz']:
    try: __import__(pkg)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import httpx
import jdatetime
import pytz

# ============================================================
# تاریخ و ساعت تهران
# ============================================================
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

def now_tehran():
    return datetime.now(TEHRAN_TZ)

def shamsi():
    n = now_tehran()
    j = jdatetime.datetime.fromgregorian(datetime=n)
    months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
    days = ['دوشنبه','سه‌شنبه','چهارشنبه','پنج‌شنبه','جمعه','شنبه','یکشنبه']
    return f"{days[n.weekday()]} {j.day} {months[j.month-1]} {j.year}"

def now_time():
    return now_tehran().strftime('%H:%M:%S')

def gregorian():
    return now_tehran().strftime('%Y-%m-%d')

# ============================================================
# دریافت قیمت از call1.ir
# ============================================================
def get_prices():
    """دریافت قیمت از call1.ir API"""
    try:
        client = httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"})
        r = client.get("https://call1.ir/api/currency.php")
        client.close()
        
        if r.status_code != 200:
            return None, f"❌ status={r.status_code}"
        
        data = r.json()
        
        # DEBUG: نشون بده API چی برگردونده
        # print(json.dumps(data[:3], indent=2, ensure_ascii=False))
        
        prices = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            
            name = str(item.get('name', '')).strip()
            price_raw = item.get('price', 0)
            
            try:
                price = int(price_raw)
            except:
                price = 0
            
            if price <= 0:
                continue
            
            # تشخیص نوع ارز
            if 'دلار' in name and 'سکه' not in name and 'نیم' not in name and 'ربع' not in name:
                prices['💵 دلار آمریکا'] = price
            elif 'یورو' in name:
                prices['🇪🇺 یورو'] = price
            elif 'پوند' in name:
                prices['🇬🇧 پوند'] = price
            elif 'لیر' in name or 'ترکیه' in name:
                prices['🇹🇷 لیر ترکیه'] = price
            elif 'دینار' in name or 'عراق' in name:
                prices['🇮🇶 دینار عراق'] = price
            elif 'درهم' in name:
                prices['🇦🇪 درهم'] = price
            elif 'یوان' in name or 'چین' in name:
                prices['🇨🇳 یوان'] = price
            elif 'طلای ۲۴' in name or 'عیار ۲۴' in name or ('طلا' in name and '۲۴' in name):
                prices['🥇 طلای ۲۴ عیار'] = price
            elif 'طلای ۱۸' in name or 'عیار ۱۸' in name or ('طلا' in name and '۱۸' in name):
                prices['🥈 طلای ۱۸ عیار'] = price
            elif 'مثقال' in name:
                prices['📀 مثقال طلا'] = price
            elif 'سکه امامی' in name or ('سکه' in name and 'تمام' in name):
                prices['🪙 سکه امامی'] = price
            elif 'نیم سکه' in name:
                prices['🪙 نیم سکه'] = price
            elif 'ربع سکه' in name:
                prices['🪙 ربع سکه'] = price
            elif 'سکه' in name and 'گرم' in name:
                prices['🪙 سکه گرمی'] = price
            elif 'انس' in name and 'طلا' in name:
                prices['🌍 انس طلا (دلار)'] = price
        
        return prices, None
        
    except Exception as e:
        return None, f"❌ {str(e)}"

# ============================================================
# نمایش
# ============================================================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_toman(p):
    return f"{p:,} تومان"

def format_dollar(p):
    return f"${p:,.2f}"

def main():
    print("🚀 اتصال به call1.ir...")
    
    while True:
        try:
            clear()
            
            # Header
            print("🟢" + "═" * 55 + "🟢")
            print("║" + " " * 14 + "💰 قیمت زنده بازار 💰" + " " * 15 + "║")
            print("🟢" + "═" * 55 + "🟢")
            print(f"📅 {shamsi()}")
            print(f"📅 میلادی: {gregorian()}")
            print(f"⏰ ساعت: {now_time()} | 📍 تهران")
            print(f"📡 منبع: call1.ir")
            print("═" * 57)
            
            # Prices
            prices, error = get_prices()
            
            if error:
                print(f"\n  {error}")
                print("  🔄 تلاش مجدد...")
            elif prices:
                # دسته‌بندی
                forex = {k: v for k, v in prices.items() if '💵' in k or '🇪🇺' in k or '🇬🇧' in k or '🇹🇷' in k or '🇮🇶' in k or '🇦🇪' in k or '🇨🇳' in k}
                gold = {k: v for k, v in prices.items() if '🥇' in k or '🥈' in k or '📀' in k or '🌍' in k}
                coin = {k: v for k, v in prices.items() if '🪙' in k}
                
                if forex:
                    print("\n  💵 ارزهای خارجی:")
                    print("  " + "─" * 53)
                    for name, price in forex.items():
                        print(f"    {name:<22} {format_toman(price)}")
                
                if gold:
                    print("\n  🥇 طلا:")
                    print("  " + "─" * 53)
                    for name, price in gold.items():
                        if 'دلار' in name:
                            print(f"    {name:<22} {format_dollar(price)}")
                        else:
                            print(f"    {name:<22} {format_toman(price)}")
                
                if coin:
                    print("\n  🪙 سکه:")
                    print("  " + "─" * 53)
                    for name, price in coin.items():
                        print(f"    {name:<22} {format_toman(price)}")
                
                print(f"\n  📊 تعداد آیتم‌های دریافت شده: {len(prices)}")
            else:
                print("\n  ❌ هیچ قیمتی دریافت نشد!")
            
            print("\n" + "🟢" + "═" * 55 + "🟢")
            print(f"  🔄 بروزرسانی: هر ۳ ثانیه | ⏰ {now_time()}")
            print(f"  Ctrl+C برای خروج")
            
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n\n👋 خروج...")
            break
        except Exception as e:
            print(f"\n❌ خطا: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
