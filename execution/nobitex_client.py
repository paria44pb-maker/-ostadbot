import requests

BASE_URL = "https://api.nobitex.ir"
API_TOKEN = "YOUR_API_TOKEN"

session = requests.Session()
session.headers.update({
    "Content-Type": "application/json",
    "Authorization": f"Token {API_TOKEN}"
})

def safe_get(endpoint):
    try:
        r = session.get(BASE_URL + endpoint, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("GET ERROR:", e)
        return None


def safe_post(endpoint, payload):
    try:
        r = session.post(BASE_URL + endpoint, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("POST ERROR:", e)
        return None


def execute_trade(side, amount, symbol="btc-usdt", order_type="market", price=None):

    src, dst = symbol.split("-")

    payload = {
        "type": order_type,
        "side": side,
        "amount": str(amount),
        "srcCurrency": src,
        "dstCurrency": dst
    }

    if order_type == "limit":
        payload["price"] = str(price)

    return safe_post("/market/orders/add", payload)
