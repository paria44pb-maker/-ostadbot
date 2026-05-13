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
    دریافت موجودی کیف پول‌ها
    """
    try:
        url = f"{NOBITEX_BASE_URL}/users/wallets/list"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        wallets = data.get("wallets", [])
        balances = {w["currency"]: float(w["balance"]) for w in wallets if float(w["balance"]) > 0}
        return balances
    except Exception as e:
        print(f"خطا در دریافت موجودی: {e}")
        return {}

def place_order(side, symbol, amount):
    """
    ثبت سفارش خرید یا فروش
    side: "buy" یا "sell"
    symbol: نماد معاملاتی مثل "BTCUSDT"
    amount: مقدار عددی (float)
    """
    try:
        src_currency = symbol.replace("USDT", "").lower()
        url = f"{NOBITEX_BASE_URL}/market/orders/add"
        payload = {
            "type": side,
            "srcCurrency": src_currency,
            "dstCurrency": "usdt",
            "amount": str(amount),
            "execution": "market"
        }
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"خطا در ثبت سفارش: {e}")
        return None

def get_market_price(symbol="BTCUSDT"):
    """
    دریافت قیمت لحظه‌ای نماد
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
        return float(stats[pair]["latest"])
    except Exception as e:
        print(f"خطا در دریافت قیمت: {e}")
        return None
