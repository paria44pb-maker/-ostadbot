# =========================================================
# WHALEMIND AI
# execution/nobitex_client.py
# Institutional Grade Nobitex Client
# =========================================================

import requests
import time
import hashlib
import hmac
import json

# =========================================================
# CONFIG
# =========================================================

API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

BASE_URL = "https://api.nobitex.ir"

# =========================================================
# SESSION
# =========================================================

session = requests.Session()

session.headers.update({
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json"
})

# =========================================================
# LOGGER
# =========================================================

def log(msg):

    print(f"[NOBITEX] {msg}")

# =========================================================
# SAFE REQUEST
# =========================================================

def safe_post(endpoint, payload):

    try:

        url = BASE_URL + endpoint

        response = session.post(
            url,
            data=json.dumps(payload),
            timeout=10
        )

        data = response.json()

        return data

    except Exception as e:

        log(f"POST ERROR => {e}")

        return None


def safe_get(endpoint):

    try:

        url = BASE_URL + endpoint

        response = session.get(
            url,
            timeout=10
        )

        data = response.json()

        return data

    except Exception as e:

        log(f"GET ERROR => {e}")

        return None

# =========================================================
# ACCOUNT
# =========================================================

def get_wallet_balance(currency="usdt"):

    data = safe_get("/users/wallets/list")

    if not data:
        return None

    wallets = data.get("wallets", [])

    for wallet in wallets:

        if wallet["currency"].lower() == currency.lower():

            balance = float(wallet["balance"])

            return balance

    return 0


def get_profile():

    return safe_get("/users/profile")

# =========================================================
# MARKET
# =========================================================

def get_orderbook(symbol="BTCUSDT"):

    market = symbol.lower()

    endpoint = f"/v2/orderbook/{market}"

    return safe_get(endpoint)


def get_market_stats(symbol="BTCUSDT"):

    market = symbol.lower()

    endpoint = f"/market/stats?srcCurrency={market[:-4]}&dstCurrency=usdt"

    return safe_get(endpoint)

# =========================================================
# ORDER ENGINE
# =========================================================

def place_market_order(
    side,
    amount,
    symbol="BTCUSDT"
):

    market = symbol.lower()

    payload = {
        "type": side,
        "execution": "market",
        "srcCurrency": market[:-4],
        "dstCurrency": "usdt",
        "amount": str(amount)
    }

    result = safe_post(
        "/market/orders/add",
        payload
    )

    log(f"MARKET ORDER => {result}")

    return result


def place_limit_order(
    side,
    amount,
    price,
    symbol="BTCUSDT"
):

    market = symbol.lower()

    payload = {
        "type": side,
        "execution": "limit",
        "srcCurrency": market[:-4],
        "dstCurrency": "usdt",
        "amount": str(amount),
        "price": str(price)
    }

    result = safe_post(
        "/market/orders/add",
        payload
    )

    log(f"LIMIT ORDER => {result}")

    return result

# =========================================================
# OPEN ORDERS
# =========================================================

def get_open_orders(symbol="BTCUSDT"):

    market = symbol.lower()

    payload = {
        "srcCurrency": market[:-4],
        "dstCurrency": "usdt"
    }

    result = safe_post(
        "/market/orders/list",
        payload
    )

    return result


def cancel_order(order_id):

    payload = {
        "order": order_id
    }

    result = safe_post(
        "/market/orders/cancel",
        payload
    )

    log(f"CANCEL ORDER => {result}")

    return result

# =========================================================
# POSITION MANAGER
# =========================================================

def emergency_close_all(symbol="BTCUSDT"):

    orders = get_open_orders(symbol)

    if not orders:
        return

    active = orders.get("orders", [])

    for order in active:

        try:

            oid = order["id"]

            cancel_order(oid)

            log(f"ORDER CLOSED => {oid}")

            time.sleep(0.5)

        except Exception as e:

            log(f"CLOSE ERROR => {e}")

# =========================================================
# RISK CONTROLS
# =========================================================

MAX_ORDER_SIZE = 500
SAFE_MODE = True

def validate_order(amount):

    if amount > MAX_ORDER_SIZE:

        log("ORDER BLOCKED => SIZE LIMIT")

        return False

    return True

# =========================================================
# SMART EXECUTION
# =========================================================

def execute_trade(
    side,
    amount,
    symbol="BTCUSDT",
    order_type="market",
    price=None
):

    if SAFE_MODE:

        if not validate_order(amount):

            return {
                "status": "blocked"
            }

    try:

        if order_type == "market":

            return place_market_order(
                side=side,
                amount=amount,
                symbol=symbol
            )

        elif order_type == "limit":

            return place_limit_order(
                side=side,
                amount=amount,
                price=price,
                symbol=symbol
            )

    except Exception as e:

        log(f"EXECUTION ERROR => {e}")

        return None

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n========== WALLET ==========")

    print(get_wallet_balance())

    print("\n========== PROFILE ==========")

    print(get_profile())

    print("\n========== ORDERBOOK ==========")

    print(get_orderbook())

    print("\n========== OPEN ORDERS ==========")

    print(get_open_orders())
