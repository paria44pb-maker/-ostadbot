#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║   💰 LIVE FOREX MONITOR — قیمت زنده ارز و طلا           ║
║   📡 منبع: tgju.org API | 🔄 بروزرسانی: هر ثانیه        ║
║   💵 تمام قیمت‌ها به تومان                              ║
╚══════════════════════════════════════════════════════════╝
"""

import httpx
import time
import os
from datetime import datetime
from collections import deque

# ============================================================
# تنظیمات
# ============================================================
UPDATE_INTERVAL = 2  # ثانیه — هر چند ثانیه بروز بشه
SAVE_TO_FILE = True   # ذخیره در فایل JSON

# ============================================================
# توابع اصلی
# ============================================================
class LivePriceFeed:
    """
    دریافت قیمت زنده از tgju.org
    تمام قیمت‌ها به تومان
    """
    
    # کدهای tgju.org
    SYMBOLS = {
        'دلار آمریکا':     'price_dollar_rl',
        'یورو':            'price_eur',
        'لیر ترکیه':       'price_try',
        'پوند انگلیس':     'price_gbp',
        'دینار عراق':      'price_iqd',
        'درهم امارات':     'price_aed',
        'یوان چین':        'price_cny',
        'طلای ۲۴ عیار':    'price_gold_24',
        'طلای ۱۸ عیار':    'price_gold_18',
        'مثقال طلا':       'price_gold_mithqal',
        'انس طلا (دلار)':  'price_gold_oz',
        'سکه امامی':       'price_coin_imami',
        'سکه بهار آزادی':  'price_coin_bahar',
        'نیم سکه':         'price_coin_half',
        'ربع سکه':         'price_coin_quarter',
        'بیتکوین (دلار)':  'price_bitcoin',
        'اتریوم (دلار)':   'price_ethereum',
        'تتر':             'price_tether',
    }
    
    def __init__(self):
        self.client = httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0"})
        self.history = {name: deque(maxlen=100) for name in self.SYMBOLS}
        self.last_update = None
    
    def fetch_price(self, symbol_code: str) -> dict:
        """دریافت قیمت یک نماد از tgju.org"""
        url = f"https://api.tgju.org/v1/market/indicator/summary/{symbol_code}"
        try:
            r = self.client.get(url)
            if r.status_code == 200:
                data = r.json()
                indicator = data.get('response', {}).get('indicators', {}).get(symbol_code, {})
                return {
                    'price': indicator.get('p', 0),
                    'change': indicator.get('d', 0),
                    'change_pct': indicator.get('dp', 0),
                    'high': indicator.get('h', 0),
                    'low': indicator.get('l', 0),
                    'time': indicator.get('t', ''),
                }
        except Exception as e:
            pass
        return {'price': 0, 'change': 0, 'change_pct': 0, 'high': 0, 'low': 0, 'time': ''}
    
    def get_all_prices(self) -> dict:
        """دریافت همه قیمت‌ها"""
        results = {}
        for name, code in self.SYMBOLS.items():
            data = self.fetch_price(code)
            price_rial = data['price']
            
            # تبدیل ریال به تومان برای ارزها و طلا
            if 'انس' not in name and 'بیتکوین' not in name and 'اتریوم' not in name and 'تتر' not in name:
                price_toman = int(price_rial / 10)
            else:
                price_toman = price_rial  # دلاری‌ها به همون صورت
            
            results[name] = {
                'price_rial': price_rial,
                'price_toman': price_toman,
                'change': data['change'],
                'change_pct': data['change_pct'],
                'high': data['high'],
                'low': data['low'],
                'updated': data['time'],
            }
            
            # ذخیره در تاریخچه
            self.history[name].append(price_toman)
        
        self.last_update = datetime.now()
        return results
    
    def detect_trend(self, name: str) -> str:
        """تشخیص روند صعودی/نزولی"""
        hist = list(self.history.get(name, []))
        if len(hist) < 5:
            return "⚪"
        
        recent = hist[-5:]
        if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
            return "🟢⬆️"
        elif all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
            return "🔴⬇️"
        elif recent[-1] > recent[0]:
            return "🟢↗️"
        elif recent[-1] < recent[0]:
            return "🔴↘️"
        return "⚪↔️"

# ============================================================
# نمایشگر
# ============================================================
class DisplayManager:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def format_price(price: int, is_toman: bool = True) -> str:
        """فرمت‌بندی قیمت با کاما"""
        if is_toman:
            return f"{price:,} تومان"
        return f"${price:,.2f}"
    
    @staticmethod
    def show_header(feed: LivePriceFeed):
        print("🟢" + "═" * 58 + "🟢")
        print("║" + " " * 15 + "💰 قیمت‌های زنده بازار 💰" + " " * 15 + "║")
        print("🟢" + "═" * 58 + "🟢")
        print(f"📡 منبع: tgju.org | 🔄 بروزرسانی: هر {UPDATE_INTERVAL} ثانیه")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 روند: {'🟢 صعودی' if feed.last_update else '⏳ در حال دریافت...'}")
        print("─" * 60)
    
    @staticmethod
    def show_prices(prices: dict, feed: LivePriceFeed):
        """نمایش قیمت‌ها در کنسول"""
        categories = {
            "💵 ارزهای خارجی": ['دلار آمریکا', 'یورو', 'پوند انگلیس', 'لیر ترکیه', 'دینار عراق', 'درهم امارات', 'یوان چین'],
            "🥇 طلا و سکه": ['طلای ۲۴ عیار', 'طلای ۱۸ عیار', 'مثقال طلا', 'انس طلا (دلار)', 'سکه امامی', 'سکه بهار آزادی', 'نیم سکه', 'ربع سکه'],
            "₿ ارز دیجیتال": ['بیتکوین (دلار)', 'اتریوم (دلار)', 'تتر'],
        }
        
        for category, items in categories.items():
            print(f"\n{category}:")
            print("─" * 60)
            for name in items:
                if name in prices:
                    p = prices[name]
                    trend = feed.detect_trend(name)
                    
                    if 'دلار' in name and 'انس' not in name and 'بیتکوین' not in name and 'اتریوم' not in name:
                        # ارزهای تومانی
                        price_str = f"{p['price_toman']:,} تومان"
                    elif 'انس' in name or 'بیتکوین' in name or 'اتریوم' in name or 'تتر' in name:
                        # دلاری
                        price_str = f"${p['price_toman']:,.2f}"
                    else:
                        # طلا و سکه
                        price_str = f"{p['price_toman']:,} تومان"
                    
                    change_str = ""
                    if p['change_pct'] != 0:
                        emoji = "🟢" if p['change_pct'] > 0 else "🔴"
                        change_str = f"{emoji} {p['change_pct']:+.2f}%"
                    
                    print(f"  {trend} {name:<18} {price_str:<25} {change_str}")

# ============================================================
# ذخیره‌سازی
# ============================================================
def save_to_json(prices: dict):
    """ذخیره قیمت‌ها در فایل JSON"""
    try:
        import json
        data = {
            'updated_at': datetime.now().isoformat(),
            'prices': {}
        }
        for name, p in prices.items():
            data['prices'][name] = {
                'price_toman': p['price_toman'],
                'change_pct': p['change_pct'],
            }
        with open('live_prices.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

# ============================================================
# حلقه اصلی
# ============================================================
def main():
    feed = LivePriceFeed()
    display = DisplayManager()
    
    print("🚀 در حال اتصال به tgju.org...")
    
    while True:
        try:
            display.clear_screen()
            display.show_header(feed)
            
            prices = feed.get_all_prices()
            display.show_prices(prices, feed)
            
            if SAVE_TO_FILE:
                save_to_json(prices)
            
            print(f"\n" + "─" * 60)
            print(f"⏰ آخرین بروزرسانی: {datetime.now().strftime('%H:%M:%S')}")
            print(f"🟢══════════════════════════════════════🟢")
            print(f"   Ctrl+C برای خروج")
            
            time.sleep(UPDATE_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 خروج...")
            break
        except Exception as e:
            print(f"\n❌ خطا: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
