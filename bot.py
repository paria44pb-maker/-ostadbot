#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 LIVE FOREX — bonbast.com (واقعی و زنده)
📅 تاریخ شمسی | ⏰ ساعت تهران | 🔄 هر ۳ ثانیه
"""

import os, sys, subprocess, time, json, re
from datetime import datetime, timedelta

# نصب خودکار
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

def get_bonbast_prices():
    """
    دریافت قیمت واقعی از bonbast.com
    این سایت معتبرترین منبع قیمت ارز در ایرانه
    و از سرورهای خارج از ایران هم در دسترسه
    """
    prices = {}
    client = httpx.Client(timeout=20.0, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
        "Referer": "https://bonbast.com/",
    })
    
    try:
        # درخواست به API اصلی bonbast
        r = client.get("https://bonbast.com/graph/latest", 
                       headers={"Origin": "https://bonbast.com"})
        
        if r.status_code == 200:
            try:
                data = r.json()
                
                # bonbast API structure: list of currency objects
                # هر ارز: name, price, change, etc.
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    
                    name = str(item.get('name', '')).upper().strip()
                    sell_price = item.get('price', 0)  # قیمت فروش
                    
                    try:
                        sell_price = int(sell_price)
                    except:
                        sell_price = 0
                    
                    if sell_price <= 0 or sell_price > 1000000:
                        continue
                    
                    # تبدیل به تومان (bonbast معمولاً قیمت رو به تومان میده)
                    if sell_price < 1000:  # اگه قیمت کمه، احتمالاً دلار یا یوروی واقعیه
                        sell_price = sell_price * 10  # تبدیل به تومان
                    
                    if name in ['USD', 'US DOLLAR', 'DOLLAR'] or 'USD' in name:
                        prices['💵 دلار'] = sell_price
                    elif name in ['EUR', 'EURO']:
                        prices['🇪🇺 یورو'] = sell_price
                    elif name in ['GBP', 'POUND']:
                        prices['🇬🇧 پوند'] = sell_price
                    elif name in ['TRY', 'LIRA', 'TURKEY']:
                        prices['🇹🇷 لیر'] = sell_price
                    elif name in ['IQD', 'DINAR']:
                        prices['🇮🇶 دینار'] = sell_price
                    elif name in ['AED', 'DIRHAM']:
                        prices['🇦🇪 درهم'] = sell_price
                    elif name in ['CNY', 'YUAN']:
                        prices['🇨🇳 یوان'] = sell_price
                    
                    # طلا و سکه
                    elif 'GOLD' in name and '24' in name or 'EMAMI' in name:
                        prices['🥇 طلای ۲۴'] = sell_price
                    elif 'COIN' in name and 'IMAM' in name or 'SEKEH' in name:
                        prices['🪙 سکه امامی'] = sell_price
                
                logger.info(f"✅ bonbast: {len(prices)} prices")
                
            except json.JSONDecodeError:
                # شاید HTML برگردونده
                text = r.text
                
                # پارس با regex
                patterns = {
                    '💵 دلار': [r'USD.*?(\d{1,3}(?:,\d{3})*)', r'دلار.*?(\d{1,3}(?:,\d{3})*)'],
                    '🇪🇺 یورو': [r'EUR.*?(\d{1,3}(?:,\d{3})*)', r'یورو.*?(\d{1,3}(?:,\d{3})*)'],
                    '🇬🇧 پوند': [r'GBP.*?(\d{1,3}(?:,\d{3})*)', r'پوند.*?(\d{1,3}(?:,\d{3})*)'],
                }
                
                for name, pats in patterns.items():
                    for pat in pats:
                        m = re.search(pat, text)
                        if m:
                            val = int(m.group(1).replace(',', ''))
                            if 1000 < val < 1000000:
                                prices[name] = val
                            break
        
        # Fallback: اگه bonbast جواب نداد
        if not prices:
            r2 = client.get("https://alanchand.com", headers={"User-Agent": "Mozilla/5.0"})
            if r2.status_code == 200:
                text = r2.text
                
                # دلار
                m = re.search(r'USD.*?(\d{1,3}(?:,\d{3})*)', text)
                if not m: m = re.search(r'دلار.*?(\d{1,3}(?:,\d{3})*)', text)
                if m: prices['💵 دلار'] = int(m.group(1).replace(',', ''))
                
                # یورو
                m = re.search(r'EUR.*?(\d{1,3}(?:,\d{3})*)', text)
                if not m: m = re.search(r'یورو.*?(\d{1,3}(?:,\d{3})*)', text)
                if m: prices['🇪🇺 یورو'] = int(m.group(1).replace(',', ''))
                
                # طلا
                m = re.search(r'GOLD.*?(\d{1,3}(?:,\d{3})*)', text)
                if not m: m = re.search(r'طلا.*?(\d{1,3}(?:,\d{3})*)', text)
                if m: prices['🥇 طلای ۲۴'] = int(m.group(1).replace(',', ''))
    
    except Exception as e:
        prices['error'] = str(e)
    
    finally:
        client.close()
    
    return prices

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("🚀 اتصال به bonbast.com (قیمت واقعی)...")
    
    while True:
        try:
            clear()
            prices = get_bonbast_prices()
            
            print("🟢" + "═" * 55 + "🟢")
            print("║" + " " * 14 + "💰 قیمت واقعی بازار 💰" + " " * 14 + "║")
            print("🟢" + "═" * 55 + "🟢")
            print(f"📅 {shamsi()}")
            print(f"⏰ ساعت: {now_time()} | 📍 تهران")
            print(f"📡 منبع: bonbast.com (واقعی)")
            print("═" * 57)
            
            if prices:
                for name, price in prices.items():
                    if name.startswith('💵') or name.startswith('🇪🇺') or name.startswith('🇬🇧') or name.startswith('🇹🇷') or name.startswith('🇮🇶') or name.startswith('🇦🇪') or name.startswith('🇨🇳'):
                        print(f"  {name}: {price:,} تومان")
                    elif name.startswith('🥇') or name.startswith('🪙'):
                        print(f"  {name}: {price:,} تومان")
                    elif name == 'error':
                        print(f"  ⚠️ {price[:100]}")
            else:
                print("\n  ❌ قیمتی دریافت نشد — در حال تلاش مجدد...")
            
            print("\n" + "🟢" + "═" * 55 + "🟢")
            print(f"  🔄 بروزرسانی: هر ۵ ثانیه | ⏰ {now_time()}")
            print(f"  Ctrl+C برای خروج")
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\n👋 خروج...")
            break
        except Exception as e:
            print(f"\n❌ {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
