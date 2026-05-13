# indicators.py
# محاسبه اندیکاتورهای تکنیکال

import numpy as np


# =========================
# RSI
# =========================
def calculate_rsi(prices, period=14):
    prices = np.array(prices)

    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)


# =========================
# EMA
# =========================
def calculate_ema(prices, period=20):
    prices = np.array(prices)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()

    ema = np.convolve(prices, weights, mode='valid')

    return round(ema[-1], 2)


# =========================
# MACD
# =========================
def calculate_macd(prices):
    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)

    macd = ema12 - ema26

    return round(macd, 4)
