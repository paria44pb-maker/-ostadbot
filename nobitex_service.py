import requests
import time
import os

# آدرس جایگزین و اصلی نوبیتکس
URL = "https://api.nobitex.ir/market/stats"
CACHE_TIME = 10

_cache = {"time": 0, "data": None}

def fetch_from_nobitex():
    try:
        # هدرهای حرفه‌ای برای دور زدن محدودیت‌ها
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
        
        print("DEBUG: Fetching prices from Nobitex...") # این توی لاگ ظاهر می‌شه
        
        response = requests.get(URL, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"DEBUG ERROR: Nobitex returned status {response.status_code}")
            # اگر ۴۰۳ یا ۴۲۹ بده یعنی آی‌پی سرور بلاک شده
            return None
            
        data = response.json()
        
        if data.get("status") != "ok":
            print(f"DEBUG ERROR: Nobitex status is not OK: {data}")
            return None
            
        stats = data.get("stats", {})
        
        # استخراج امن قیمت‌ها
        btc_price = stats.get("btc-rls", {}).get("latest", 0)
        eth_price = stats.get("eth-rls", {}).get("latest", 0)
        usdt_price = stats.get("usdt-rls", {}).get("latest", 0)
        
        print(f"DEBUG SUCCESS: BTC is {btc_price}")
        
        return {
            "btc": float(btc_price),
            "eth": float(eth_price),
            "usdt": float(usdt_price)
        }
        
    except Exception as e:
        print(f"DEBUG EXCEPTION: {str(e)}")
        return None

def get_prices():
    now = time.time()
    # استفاده از کش برای جلوگیری از Rate Limit
    if _cache["data"] and (now - _cache["time"] < CACHE_TIME):
        return _cache["data"]

    data = fetch_from_nobitex()
    if data and data["btc"] > 0:
        _cache["data"] = data
        _cache["time"] = now
        return data

    return {"btc": 0, "eth": 0, "usdt": 0}
