# main.py
# هسته مرکزی WhaleMind AI

from data.connectors import get_binance_price
from analysis.indicators import calculate_rsi
from analysis.price_action import detect_trend

from brain.groq_fast_logic import fast_signal
from brain.deepseek_strategic import long_term_trend

from execution.risk_manager import position_size
from utils.logger import log


def ai_decision(price, prices):

    indicators = {
        "rsi": calculate_rsi(prices),
        "trend": detect_trend(prices)
    }

    signal = None

    # اول Groq
    try:
        signal = fast_signal(price, indicators)
        log(f"GROQ SIGNAL: {signal}")

    except Exception as e:

        log("Groq failed -> switching to DeepSeek")

        try:
            trend = long_term_trend(
                [{"close": p} for p in prices],
                0
            )

            if trend == "up":
                signal = "buy"

            elif trend == "down":
                signal = "sell"

            else:
                signal = "hold"

        except Exception as e2:

            log("DeepSeek also failed")
            signal = "hold"

    return signal


def run_bot():

    prices = []

    while True:

        data = get_binance_price("BTCUSDT")

        if not data:
            continue

        price = data["price"]

        prices.append(price)

        if len(prices) > 200:
            prices.pop(0)

        if len(prices) < 20:
            continue

        signal = ai_decision(price, prices)

        log(f"Price: {price} | Signal: {signal}")



if __name__ == "__main__":

    log("WhaleMind AI started")

    run_bot()
