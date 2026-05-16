import requests
import time

# آدرس جایگزین در صورت اختلال در دامنه اصلی
URL = "https://api.nobitex.ir/market/stats"
CACHE_TIME = 15

_cache = {"time": 0, "data": None}

def fetch():
    try:
        # اضافه کردن هدر برای شبیه‌سازی مرورگر
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        r = requests.get(URL, headers=headers, timeout=10)
        
        # اگر وضعیت ۲۰ Wid0 نبود
        if r.status_code != 200:
            print(f"DEBUG: Nobitex Error Code: {r.status_code}")
            return None
            
        data = r.json()
        
        if "stats" not in data:
            print("DEBUG: 'stats' not found in response")
            return None
            
        stats = data["stats"]
        
        # استخراج قیمت‌ها
        return {
            "btc": float(stats.get("btc-rls", {}).get("latest", 0)),
            "eth": float(stats.get("eth-rls", {}).get("latest", 0)),
            "usdt": float(stats.get("usdt-rls", {}).get("latest", 0)),
        }
    except Exception as e:
        print(f"DEBUG: Request failed: {e}")
        return None

def get_prices():
    now = time.time()
    if _cache["data"] and now - _cache["time"] < CACHE_TIME:
        return _cache["data"]

    data = fetch()
    if data and data["btc"] > 0:
        _cache["data"] = data
        _cache["time"] = now
        return data

    return {"btc": 0, "eth": 0, "usdt": 0}
