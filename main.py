# =========================================================
# WHALEMIND AI - INSTITUTIONAL VERSION
# main.py
# =========================================================

import requests
import time
import datetime
import json
import os
import numpy as np

# =========================================================
# CONFIG
# =========================================================

SYMBOL = "BTCUSDT"

BINANCE_PRICE_API = "https://api.binance.com/api/v3/ticker/price"
BINANCE_DEPTH_API = "https://api.binance.com/api/v3/depth"
BINANCE_KLINE_API = "https://api.binance.com/api/v3/klines"

MEMORY_DIR = "memory"
TRADES_FILE = f"{MEMORY_DIR}/trades.json"

START_BALANCE = 10000

# =========================================================
# INIT
# =========================================================

if not os.path.exists(MEMORY_DIR):
    os.makedirs(MEMORY_DIR)

if not os.path.exists(TRADES_FILE):
    with open(TRADES_FILE, "w") as f:
        json.dump([], f)

# =========================================================
# LOGGER
# =========================================================

def log(msg):

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{now}] {msg}"

    print(line)

    with open("whalemind.log", "a") as f:
        f.write(line + "\n")

# =========================================================
# MARKET DATA
# =========================================================

def get_price():

    try:

        r = requests.get(
            BINANCE_PRICE_API,
            params={"symbol": SYMBOL},
            timeout=5
        )

        return float(r.json()["price"])

    except Exception as e:

        log(f"PRICE ERROR {e}")

        return None


def get_order_book(limit=20):

    try:

        r = requests.get(
            BINANCE_DEPTH_API,
            params={
                "symbol": SYMBOL,
                "limit": limit
            },
            timeout=5
        )

        return r.json()

    except Exception as e:

        log(f"ORDERBOOK ERROR {e}")

        return None


def get_historical_klines(interval="1m", limit=200):

    try:

        r = requests.get(
            BINANCE_KLINE_API,
            params={
                "symbol": SYMBOL,
                "interval": interval,
                "limit": limit
            },
            timeout=10
        )

        data = r.json()

        closes = [float(k[4]) for k in data]

        return closes

    except Exception as e:

        log(f"KLINE ERROR {e}")

        return []

# =========================================================
# INDICATORS
# =========================================================

def ema(prices, period):

    alpha = 2 / (period + 1)

    e = prices[0]

    for p in prices[1:]:
        e = alpha * p + (1 - alpha) * e

    return e


def rsi(prices, period=14):

    if len(prices) < period + 1:
        return 50

    gains = []
    losses = []

    for i in range(1, period):

        diff = prices[-i] - prices[-i - 1]

        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = np.mean(gains) if gains else 0.0001
    avg_loss = np.mean(losses) if losses else 0.0001

    rs = avg_gain / avg_loss

    return round(100 - (100 / (1 + rs)), 2)


def macd(prices):

    return round(ema(prices, 12) - ema(prices, 26), 2)

# =========================================================
# PRICE ACTION
# =========================================================

def trend(prices):

    fast = ema(prices, 12)
    slow = ema(prices, 26)

    if fast > slow:
        return "up"

    if fast < slow:
        return "down"

    return "side"


def bos(prices):

    if len(prices) < 10:
        return None

    recent_high = max(prices[-10:-1])
    recent_low = min(prices[-10:-1])

    if prices[-1] > recent_high:
        return "bullish"

    if prices[-1] < recent_low:
        return "bearish"

    return None

# =========================================================
# WHALE DETECTOR
# =========================================================

def whale_activity(prices):

    if len(prices) < 20:
        return False

    moves = [
        abs(prices[i] - prices[i - 1])
        for i in range(1, len(prices))
    ]

    avg_move = np.mean(moves[:-1])

    last_move = moves[-1]

    return last_move > avg_move * 3

# =========================================================
# ORDER BOOK AI
# =========================================================

def analyze_orderbook():

    data = get_order_book()

    if not data:
        return "neutral"

    bids = data["bids"]
    asks = data["asks"]

    bid_volume = sum(float(b[1]) for b in bids)
    ask_volume = sum(float(a[1]) for a in asks)

    ratio = bid_volume / (ask_volume + 0.0001)

    if ratio > 1.5:
        return "bullish"

    if ratio < 0.7:
        return "bearish"

    return "neutral"

# =========================================================
# SMART MONEY DETECTOR
# =========================================================

def smart_money_signal(prices):

    if len(prices) < 30:
        return None

    volume_spike = whale_activity(prices)

    structure = bos(prices)

    if volume_spike and structure == "bullish":
        return "buy"

    if volume_spike and structure == "bearish":
        return "sell"

    return None

# =========================================================
# AI ENGINE
# =========================================================

def ai_signal(prices):

    rrsi = rsi(prices)
    mmacd = macd(prices)
    ttrend = trend(prices)

    orderbook = analyze_orderbook()

    smart = smart_money_signal(prices)

    if smart:
        return smart

    if rrsi < 30 and ttrend == "up" and orderbook == "bullish":
        return "buy"

    if rrsi > 70 and ttrend == "down" and orderbook == "bearish":
        return "sell"

    if mmacd > 0 and orderbook == "bullish":
        return "buy"

    if mmacd < 0 and orderbook == "bearish":
        return "sell"

    return "hold"

# =========================================================
# RISK MANAGEMENT
# =========================================================

def position_size(balance, risk=1, stoploss=0.5):

    risk_amount = balance * (risk / 100)

    size = risk_amount / stoploss

    return round(size, 2)

# =========================================================
# MEMORY
# =========================================================

def load_trades():

    with open(TRADES_FILE) as f:
        return json.load(f)


def save_trade(trade):

    data = load_trades()

    data.append(trade)

    with open(TRADES_FILE, "w") as f:
        json.dump(data, f, indent=4)


def strategy_stats():

    trades = load_trades()

    if not trades:
        return 0

    wins = 0

    for t in trades:

        if t["profit"] > 0:
            wins += 1

    return round((wins / len(trades)) * 100, 2)

# =========================================================
# TRADE ENGINE
# =========================================================

position = None

def open_trade(side, price, balance):

    global position

    size = position_size(balance)

    if side == "buy":

        sl = price * 0.995
        tp = price * 1.015

    else:

        sl = price * 1.005
        tp = price * 0.985

    position = {
        "side": side,
        "entry": price,
        "size": size,
        "sl": sl,
        "tp": tp
    }

    log(f"OPEN {side} @ {price}")


def check_trade(price):

    global position

    if not position:
        return

    side = position["side"]

    entry = position["entry"]

    size = position["size"]

    sl = position["sl"]

    tp = position["tp"]

    if side == "buy":

        if price <= sl or price >= tp:

            profit = (price - entry) * size

            close_trade(price, profit)

    else:

        if price >= sl or price <= tp:

            profit = (entry - price) * size

            close_trade(price, profit)


def close_trade(price, profit):

    global position

    log(f"CLOSE TRADE PROFIT {profit}")

    save_trade({
        "side": position["side"],
        "entry": position["entry"],
        "exit": price,
        "profit": profit,
        "time": str(datetime.datetime.utcnow())
    })

    position = None

# =========================================================
# BACKTEST ENGINE
# =========================================================

def backtest():

    log("STARTING BACKTEST")

    prices = get_historical_klines()

    if len(prices) < 50:
        log("NOT ENOUGH DATA")
        return

    wins = 0
    losses = 0

    for i in range(40, len(prices)):

        sample = prices[:i]

        signal = ai_signal(sample)

        current = sample[-1]

        future = prices[i]

        if signal == "buy":

            if future > current:
                wins += 1
            else:
                losses += 1

        elif signal == "sell":

            if future < current:
                wins += 1
            else:
                losses += 1

    total = wins + losses

    if total == 0:
        accuracy = 0
    else:
        accuracy = round((wins / total) * 100, 2)

    log(f"BACKTEST ACCURACY {accuracy}%")

# =========================================================
# NOBITEX PLACEHOLDER
# =========================================================

def send_nobitex_order(side, amount):

    log(f"NOBITEX ORDER => {side} {amount}")

# =========================================================
# MAIN LOOP
# =========================================================

def run_bot():

    prices = []

    balance = START_BALANCE

    log("WHALEMIND AI STARTED")

    backtest()

    while True:

        try:

            price = get_price()

            if not price:

                time.sleep(5)

                continue

            prices.append(price)

            if len(prices) > 300:
                prices.pop(0)

            if len(prices) < 40:

                log("COLLECTING DATA")

                time.sleep(2)

                continue

            signal = ai_signal(prices)

            whale = whale_activity(prices)

            orderbook = analyze_orderbook()

            if whale:
                log("WHALE DETECTED")

            if position is None:

                if signal in ["buy", "sell"]:

                    open_trade(signal, price, balance)

            else:

                check_trade(price)

            winrate = strategy_stats()

            log(f"""
=================================
PRICE: {price}

SIGNAL: {signal}

TREND: {trend(prices)}

RSI: {rsi(prices)}

MACD: {macd(prices)}

ORDERBOOK: {orderbook}

BOS: {bos(prices)}

POSITION: {position}

WINRATE: {winrate}%
=================================
""")

            time.sleep(5)

        except KeyboardInterrupt:

            log("BOT STOPPED")

            break

        except Exception as e:

            log(f"MAIN ERROR {e}")

            time.sleep(5)

# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    run_bot()
