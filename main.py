# main.py
# WhaleMind AI - Full Integrated Version

import requests
import datetime
import json
import os
import time
import numpy as np

# =========================================================
# CONFIG
# =========================================================

MEMORY_DIR = "memory"
MEMORY_FILE = f"{MEMORY_DIR}/trades.json"

BINANCE_API = "https://api.binance.com/api/v3/ticker/price"

DEFAULT_SYMBOL = "BTCUSDT"

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
        with open("whalemind.log", "a", encoding="utf-8") as f:
            f.write(log_message + "\n")

    except Exception as e:
        print("Log Error:", e)

# =========================================================
# MARKET DATA
# =========================================================

def get_binance_price(symbol=DEFAULT_SYMBOL):

    try:

        response = requests.get(
            BINANCE_API,
            params={"symbol": symbol},
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        return {
            "symbol": symbol,
            "price": float(data["price"])
        }

    except Exception as e:

        log(f"Binance Error: {e}")

        return None

# =========================================================
# NEWS ANALYSIS
# =========================================================

def analyze_news(news_text):

    positive_words = [
        "ETF",
        "Bullish",
        "Adoption",
        "Partnership",
        "Pump"
    ]

    negative_words = [
        "Hack",
        "Ban",
        "Crash",
        "Dump",
        "Liquidation"
    ]

    score = 0

    for word in positive_words:

        if word.lower() in news_text.lower():
            score += 1

    for word in negative_words:

        if word.lower() in news_text.lower():
            score -= 1

    return score

# =========================================================
# INDICATORS
# =========================================================

def calculate_rsi(prices, period=14):

    prices = np.array(prices)

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

    if len(prices) < period:
        return float(np.mean(prices))

    alpha = 2 / (period + 1)

    ema = prices[0]

    for price in prices[1:]:
        ema = alpha * price + (1 - alpha) * ema

    return round(float(ema), 2)


def calculate_macd(prices):

    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)

    macd = ema12 - ema26

    return round(macd, 4)

# =========================================================
# PRICE ACTION
# =========================================================

def detect_trend(prices):

    if len(prices) < 20:
        return "side"

    ema_fast = calculate_ema(prices, 12)
    ema_slow = calculate_ema(prices, 26)

    if ema_fast > ema_slow:
        return "up"

    elif ema_fast < ema_slow:
        return "down"

    return "side"


def detect_liquidity_sweep(prices):

    if len(prices) < 5:
        return False

    recent_high = max(prices[-5:-1])

    if prices[-1] > recent_high:
        return True

    return False


def detect_break_of_structure(prices):

    if len(prices) < 10:
        return None

    recent_high = max(prices[-10:-1])
    recent_low = min(prices[-10:-1])

    if prices[-1] > recent_high:
        return "bullish_bos"

    if prices[-1] < recent_low:
        return "bearish_bos"

    return None

# =========================================================
# WHALE DETECTION
# =========================================================

def whale_activity(prices):

    if len(prices) < 15:
        return False

    recent_move = abs(prices[-1] - prices[-2])

    average_move = np.mean([
        abs(prices[i] - prices[i - 1])
        for i in range(1, len(prices) - 1)
    ])

    if average_move == 0:
        return False

    if recent_move > average_move * 3:
        return True

    return False

# =========================================================
# AI BRAINS
# =========================================================

def groq_fast_signal(price, indicators):

    rsi = indicators.get("rsi", 50)
    trend = indicators.get("trend", "side")
    macd = indicators.get("macd", 0)

    if rsi < 30 and trend == "up" and macd > 0:
        return "buy"

    if rsi > 70 and trend == "down" and macd < 0:
        return "sell"

    return "hold"


def deepseek_strategic_trend(candles, news_sentiment):

    score = 0

    closes = [c["close"] for c in candles]

    if news_sentiment > 0:
        score += 1

    if closes[-1] > closes[0]:
        score += 1

    bos = detect_break_of_structure(closes)

    if bos == "bullish_bos":
        score += 1

    if detect_liquidity_sweep(closes):
        score -= 1

    if score >= 2:
        return "up"

    if score <= 0:
        return "down"

    return "side"

# =========================================================
# RISK MANAGEMENT
# =========================================================

def position_size(balance, risk_percent, stop_loss_percent):

    if stop_loss_percent <= 0:
        return 0

    risk_amount = balance * (risk_percent / 100)

    position = risk_amount / stop_loss_percent

    return round(position, 4)


def kelly_criterion(win_rate, risk_reward):

    if risk_reward <= 0:
        return 0

    kelly = win_rate - ((1 - win_rate) / risk_reward)

    return max(kelly, 0)

# =========================================================
# MEMORY SYSTEM
# =========================================================

def load_memory():

    try:

        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    except Exception:
        return []


def save_trade(trade):

    memory = load_memory()

    memory.append(trade)

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def last_trades(limit=5):

    memory = load_memory()

    return memory[-limit:]


def strategy_stats():

    trades = load_memory()

    if len(trades) == 0:

        return {
            "total": 0,
            "wins": 0,
            "losses": 0,
            "winrate": 0
        }

    wins = 0
    losses = 0

    for trade in trades:

        if trade.get("profit", 0) > 0:
            wins += 1
        else:
            losses += 1

    total = wins + losses

    winrate = (wins / total) * 100

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "winrate": round(winrate, 2)
    }

# =========================================================
# AI DECISION ENGINE
# =========================================================

def ai_decision(price, prices):

    indicators = {
        "rsi": calculate_rsi(prices),
        "trend": detect_trend(prices),
        "macd": calculate_macd(prices)
    }

    signal = None

    try:

        signal = groq_fast_signal(
            price,
            indicators
        )

        log(f"GROQ SIGNAL => {signal}")

    except Exception as e:

        log(f"Groq Failed => {e}")

        try:

            trend = deepseek_strategic_trend(
                [{"close": p} for p in prices],
                0
            )

            if trend == "up":
                signal = "buy"

            elif trend == "down":
                signal = "sell"

            else:
                signal = "hold"

            log(f"DEEPSEEK SIGNAL => {signal}")

        except Exception as e2:

            log(f"DeepSeek Failed => {e2}")

            signal = "hold"

    return signal

# =========================================================
# MAIN BOT LOOP
# =========================================================

def run_bot():

    prices = []

    balance = 10000

    log("WhaleMind AI Started")

    while True:

        try:

            market = get_binance_price(DEFAULT_SYMBOL)

            if not market:
                time.sleep(5)
                continue

            price = market["price"]

            prices.append(price)

            if len(prices) > 300:
                prices.pop(0)

            if len(prices) < 30:

                log("Collecting market data...")

                time.sleep(2)

                continue

            signal = ai_decision(price, prices)

            whale = whale_activity(prices)

            if whale:
                log("🐋 Whale Activity Detected")

            position = position_size(
                balance=balance,
                risk_percent=1,
                stop_loss_percent=0.5
            )

            stats = strategy_stats()

            log(
                f"""
PRICE: {price}
SIGNAL: {signal}
TREND: {detect_trend(prices)}
RSI: {calculate_rsi(prices)}
MACD: {calculate_macd(prices)}
POSITION SIZE: {position}
WINRATE: {stats['winrate']}%
                """
            )

            save_trade({
                "timestamp": str(datetime.datetime.utcnow()),
                "price": price,
                "signal": signal,
                "profit": 0
            })

            time.sleep(5)

        except KeyboardInterrupt:

            log("Bot stopped manually")

            break

        except Exception as e:

            log(f"MAIN LOOP ERROR => {e}")

            time.sleep(5)

# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    run_bot()
