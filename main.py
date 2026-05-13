import os
import requests

NOBITEX_BASE_URL = "https://api.nobitex.ir"
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")

HEADERS = {
    "Authorization": f"Token {NOBITEX_API_KEY}",
    "Content-Type": "application/json"
}

def get_balance():
    """
    دریافت موجودی فعلی کیف پول‌ها از نوبیتکس
    خروجی: دیکشنری {ارز: مقدار}
    """
    try:
        url = f"{NOBITEX_BASE_URL}/users/wallets/list"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        wallets = data.get("wallets", [])
        balances = {w["currency"]: float(w["balance"]) for w in wallets if float(w["balance"]) > 0}
        return balances
    except Exception as ex:
        print(f"[Nobitex API] خطا در دریافت موجودی: {ex}")
        return {}

def place_order(side, symbol, amount):
    """
    ثبت سفارش خرید یا فروش به صورت Market Order در نوبیتکس
    آرگومان‌ها:
    - side: "buy" یا "sell"
    - symbol: رشته نماد، مثلا "BTCUSDT"
    - amount: مقدار معامله (float)
    خروجی: پاسخ API به صورت دیکشنری یا None در صورت خطا
    """
    try:
        src_currency = symbol.replace("USDT", "").lower()
        payload = {
            "type": side,
            "srcCurrency": src_currency,
            "dstCurrency": "usdt",
            "amount": str(amount),
            "execution": "market"
        }
        url = f"{NOBITEX_BASE_URL}/market/orders/add"
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as ex:
        print(f"[Nobitex API] خطا در ثبت سفارش: {ex}")
        return None

def get_market_price(symbol="BTCUSDT"):
    """
    دریافت قیمت لحظه‌ای نماد در بازار نوبیتکس
    ورودی:
    - symbol: مثلا "BTCUSDT"
    خروجی:
    - قیمت (float) یا None در صورت خطا
    """
    try:
        src = symbol.replace("USDT", "").lower()
        url = f"{NOBITEX_BASE_URL}/market/stats"
        response = requests.post(url, json={"srcCurrency": src, "dstCurrency": "usdt"})
        response.raise_for_status()
        data = response.json()
        pair = f"{src}-usdt"
        stats = data.get("stats", {})
        if pair not in stats:
            return None
        price = float(stats[pair]["latest"])
        return price
    except Exception as ex:
        print(f"[Nobitex API] خطا در دریافت قیمت: {ex}")
        return None
