#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 LIVE FOREX — منبع دوم: call1.ir + alanchand.com
"""

import httpx
import re
import time
from datetime import datetime

def get_prices_call1():
    """دریافت از call1.ir"""
    try:
        client = httpx.Client(timeout=15.0, headers={"User-Agent": "Mozilla/5.0"})
        r = client.get("https://call1.ir/api/currency.php")
        if r.status_code == 200:
            data = r.json()
            prices = {}
            for item in data if isinstance(data, list) else []:
                name = str(item.get('name', ''))
                price = int(item.get('price', 0))
                if 'دلار' in name: prices['دلار'] = price
                elif 'یورو' in name: prices['یورو'] = price
                elif 'لیر' in name: prices['لیر'] = price
                elif 'پوند' in name: prices['پوند'] = price
                elif 'دینار' in name: prices['دینار'] = price
                elif 'طلای ۲۴' in name: prices['طلای ۲۴'] = price
                elif 'سکه' in name: prices['سکه'] = price
            return prices
    except Exception as e:
        print(f"call1.ir error: {e}")
    return {}

def get_prices_alanchand():
    """دریافت از alanchand.com"""
    try:
        from bs4 import BeautifulSoup
        client = httpx.Client(timeout=15.0, headers={"User-Agent": "Mozilla/5.0"})
        r = client.get("https://alanchand.com")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text()
            prices = {}
            
            # دلار
            m = re.search(r'دلار\s*[:\-]?\s*([\d,]+)', text)
            if m: prices['دلار'] = int(m.group(1).replace(',',''))
            
            # یورو
            m = re.search(r'یورو\s*[:\-]?\s*([\d,]+)', text)
            if m: prices['یورو'] = int(m.group(1).replace(',',''))
            
            # لیر
            m = re.search(r'لیر\s*[:\-]?\s*([\d,]+)', text)
            if m: prices['لیر'] = int(m.group(1).replace(',',''))
            
            # طلا
            m = re.search(r'طل[ايی]\s*۲۴\s*[:\-]?\s*([\d,]+)', text)
            if m: prices['طلای ۲۴'] = int(m.group(1).replace(',',''))
            
            # سکه
            m = re.search(r'سکه\s*[:\-]?\s*([\d,]+)', text)
            if m: prices['سکه'] = int(m.group(1).replace(',',''))
            
            return prices
    except Exception as e:
        print(f"alanchand error: {e}")
    return {}

# تست
print("🔄 تست منابع...")
print("=" * 50)

print("\n📡 منبع ۱: call1.ir")
p1 = get_prices_call1()
for k, v in p1.items():
    print(f"  {k}: {v:,} تومان")

print("\n📡 منبع ۲: alanchand.com")
p2 = get_prices_alanchand()
for k, v in p2.items():
    print(f"  {k}: {v:,} تومان")

print("\n✅ تموم شد.")
