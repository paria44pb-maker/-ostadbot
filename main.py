import requests
import datetime
import json
import os
import time
import numpy as np

# =========================================================
# CONFIG
# =========================================================

BINANCE_API = "https://api.binance.com/api/v3/ticker/price"
DEFAULT_SYMBOL = "BTCUSDT"

MEMORY_DIR = "memory"
MEMORY_FILE = f"{MEMORY_DIR}/trades.json"

# =========================================================
# STARTUP
# =========================================================

if not os.path.exists(MEMORY_DIR):
    os.makedirs(MEMORY_DIR)

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)

# =========================================================
# LOGGER
# =========================================================

def log(message):

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log_message = f"[{now}] {message}"

    print(log_message)

    try:
        with open("whalemind.log", "a") as f:
            f.write(log_message + "\n")
    except:
        pass


# =========================================================
# MARKET DATA
# =========================================================

def get_binance_price(symbol=DEFAULT_SYMBOL):

    try:

        r = requests.get(
            BINANCE_API,
            params={"symbol": symbol},
            timeout=5
        )

        data = r.json()

        return float(data["price"])

    except Exception as e:

        log(f"Binance Error {e}")

        return None


# =========================================================
# INDICATORS
# =========================================================

def calculate_rsi(prices, period=14):

    if len(prices) < period:
        return 50

    deltas = np.diff(prices)

    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)


def calculate_ema(prices, period=20):

    prices = np.array(prices)

    alpha = 2 / (period + 1)

    ema = prices[0]

    for price in prices[1:]:
        ema = alpha * price + (1 - alpha) * ema

    return float(ema)


def calculate_macd(prices):

    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)

    return round(ema12 - ema26, 4)


# =========================================================
# PRICE ACTION
# =========================================================

def detect_trend(prices):

    if len(prices) < 30:
        return "side"

    ema_fast = calculate_ema(prices, 12)
    ema_slow = calculate_ema(prices, 26)

    if ema_fast > ema_slow:
        return "up"

    if ema_fast < ema_slow:
        return "down"

    return "side"


def detect_break_of_structure(prices):

    if len(prices) < 10:
        return None

    high = max(prices[-10:-1])
    low = min(prices[-10:-1])

    if prices[-1] > high:
        return "bullish_bos"

    if prices[-1] < low:
        return "bearish_bos"

    return None


def detect_liquidity_sweep(prices):

    if len(prices) < 5:
        return False

    recent_high = max(prices[-5:-1])

    if prices[-1] > recent_high:
        return True

    return False


# =========================================================
# WHALE DETECTION
# =========================================================

def whale_activity(prices):

    if len(prices) < 20:
        return False

    recent_move = abs(prices[-1] - prices[-2])

    avg_move = np.mean([
        abs(prices[i] - prices[i-1])
        for i in range(1, len(prices)-1)
    ])

    if avg_move == 0:
        return False

    if recent_move > avg_move * 3:
        return True

    return False


# =========================================================
# AI BRAINS
# =========================================================

def groq_fast_signal(indicators):

    rsi = indicators["rsi"]
    trend = indicators["trend"]
    macd = indicators["macd"]

    if rsi < 30 and trend == "up" and macd > 0:
        return "buy"

    if rsi > 70 and trend == "down" and macd < 0:
        return "sell"

    return "hold"


def deepseek_trend(prices):

    bos = detect_break_of_structure(prices)

    if bos == "bullish_bos":
        return "buy"

    if bos == "bearish_bos":
        return "sell"

    return "hold"


def ai_decision(prices):

    indicators = {
        "rsi": calculate_rsi(prices),
        "trend": detect_trend(prices),
        "macd": calculate_macd(prices)
    }

    try:

        signal = groq_fast_signal(indicators)

        log(f"GROQ SIGNAL {signal}")

        return signal

    except Exception as e:

        log(f"GROQ FAILED {e}")

        signal = deepseek_trend(prices)

        log(f"DEEPSEEK SIGNAL {signal}")

        return signal


# =========================================================
# RISK MANAGEMENT
# =========================================================

def position_size(balance, risk_percent, stop_loss_percent):

    risk_amount = balance * (risk_percent / 100)

    position = risk_amount / stop_loss_percent

    return round(position, 4)


# =========================================================
# MEMORY
# =========================================================

def load_memory():

    try:
        with open(MEMORY_FILE) as f:
            return json.load(f)
    except:
        return []


def save_trade(trade):

    data = load_memory()

    data.append(trade)

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def strategy_stats():

    trades = load_memory()

    if len(trades) == 0:
        return {"winrate":0}

    wins = 0

    for t in trades:
        if t.get("profit",0) > 0:
            wins += 1

    winrate = wins / len(trades) * 100

    return {"winrate":round(winrate,2)}


# =========================================================
# TRADE ENGINE
# =========================================================

open_position = None


def open_trade(signal, price, balance):

    global open_position

    if signal not in ["buy","sell"]:
        return

    size = position_size(balance,1,0.5)

    if signal == "buy":

        sl = price * 0.995
        tp = price * 1.01

    else:

        sl = price * 1.005
        tp = price * 0.99

    open_position = {
        "side":signal,
        "entry":price,
        "size":size,
        "stop":sl,
        "tp":tp
    }

    log(f"OPEN {signal} {price}")


def check_position(price):

    global open_position

    if open_position is None:
        return

    side = open_position["side"]
    entry = open_position["entry"]
    size = open_position["size"]
    sl = open_position["stop"]
    tp = open_position["tp"]

    if side == "buy":

        if price <= sl or price >= tp:

            profit = (price-entry)*size

            close_trade(price,profit)

    else:

        if price >= sl or price <= tp:

            profit = (entry-price)*size

            close_trade(price,profit)


def close_trade(price,profit):

    global open_position

    log(f"CLOSE TRADE PROFIT {profit}")

    save_trade({
        "entry":open_position["entry"],
        "exit":price,
        "side":open_position["side"],
        "profit":profit,
        "time":str(datetime.datetime.utcnow())
    })

    open_position = None


# =========================================================
# MAIN LOOP
# =========================================================

def run_bot():

    prices=[]

    balance=10000

    log("WhaleMind AI Started")

    while True:

        try:

            price=get_binance_price()

            if price is None:
                time.sleep(5)
                continue

            prices.append(price)

            if len(prices)>300:
                prices.pop(0)

            if len(prices)<40:
                log("Collecting data")
                time.sleep(2)
                continue

            signal=ai_decision(prices)

            if whale_activity(prices):
                log("WHALE ACTIVITY DETECTED")

            if open_position is None:
                open_trade(signal,price,balance)

            check_position(price)

            stats=strategy_stats()

            log(f"""
PRICE {price}
SIGNAL {signal}
TREND {detect_trend(prices)}
RSI {calculate_rsi(prices)}
MACD {calculate_macd(prices)}
WINRATE {stats['winrate']}%
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
