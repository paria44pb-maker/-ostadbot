import requests
import time

URL = "https://api.nobitex.ir/market/stats"

CACHE_TIME = 10  # seconds

_cache = {
    "time": 0,
    "data": None
}


def fetch_prices():

    try:

        r = requests.get(URL, timeout=10)

        if r.status_code != 200:
            return None

        data = r.json()["stats"]

        return {
            "btc": data.get("btc-rls", {}).get("latest", "-"),
            "eth": data.get("eth-rls", {}).get("latest", "-"),
            "usdt": data.get("usdt-rls", {}).get("latest", "-"),
            "xrp": data.get("xrp-rls", {}).get("latest", "-"),
            "ton": data.get("ton-rls", {}).get("latest", "-")
        }

    except:
        return None


def get_prices():

    now = time.time()

    if _cache["data"] and now - _cache["time"] < CACHE_TIME:
        return _cache["data"]

    data = fetch_prices()

    if data:

        _cache["data"] = data
        _cache["time"] = now

        return data

    return {
        "btc": "-",
        "eth": "-",
        "usdt": "-",
        "xrp": "-",
        "ton": "-"
    }
