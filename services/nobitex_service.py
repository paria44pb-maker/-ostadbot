import requests
import time

URL = "https://api.nobitex.ir/market/stats"
CACHE_TIME = 10

_cache = {"time": 0, "data": None}

def fetch():
    try:
        r = requests.get(URL, timeout=10)
        if r.status_code != 200:
            return None
        stats = r.json()["stats"]
        return {
            "btc": float(stats["btc-rls"]["latest"]),
            "eth": float(stats["eth-rls"]["latest"]),
            "usdt": float(stats["usdt-rls"]["latest"]),
        }
    except:
        return None

def get_prices():
    now = time.time()
    if _cache["data"] and now - _cache["time"] < CACHE_TIME:
        return _cache["data"]

    data = fetch()
    if data:
        _cache["data"] = data
        _cache["time"] = now
        return data

    return {"btc":0,"eth":0,"usdt":0}
