import math


class AdvancedSignalEngine:
    """
    Multi-layer crypto market analysis engine
    """

    # =========================
    # 📊 RSI CALCULATION
    # =========================
    def rsi(self, closes, period=14):
        gains = 0
        losses = 0

        for i in range(1, period + 1):
            change = closes[-i] - closes[-i - 1]
            if change > 0:
                gains += change
            else:
                losses += abs(change)

        if losses == 0:
            return 100

        rs = gains / losses
        return 100 - (100 / (1 + rs))

    # =========================
    # 📈 EMA
    # =========================
    def ema(self, prices, period=20):
        k = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = price * k + ema * (1 - k)

        return ema

    # =========================
    # 📉 MACD
    # =========================
    def macd(self, prices):
        ema12 = self.ema(prices, 12)
        ema26 = self.ema(prices, 26)

        macd_line = ema12 - ema26
        signal_line = self.ema([macd_line] * 10, 9)

        histogram = macd_line - signal_line

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }

    # =========================
    # 🔁 FIBONACCI RETRACEMENT
    # =========================
    def fibonacci(self, high, low):
        diff = high - low

        return {
            "0.0": high,
            "0.236": high - diff * 0.236,
            "0.382": high - diff * 0.382,
            "0.5": high - diff * 0.5,
            "0.618": high - diff * 0.618,
            "1.0": low
        }

    # =========================
    # 🧠 PRICE ACTION TREND
    # =========================
    def trend(self, prices):
        recent = prices[-5:]

        if all(recent[i] > recent[i - 1] for i in range(1, 5)):
            return "BULLISH"

        if all(recent[i] < recent[i - 1] for i in range(1, 5)):
            return "BEARISH"

        return "SIDEWAYS"

    # =========================
    # 🧠 FINAL SIGNAL ENGINE
    # =========================
    def analyze(self, prices):
        rsi_val = self.rsi(prices)
        macd_val = self.macd(prices)
        trend_val = self.trend(prices)

        score = 0

        # RSI logic
        if rsi_val < 30:
            score += 2
        elif rsi_val > 70:
            score -= 2

        # MACD logic
        if macd_val["histogram"] > 0:
            score += 1
        else:
            score -= 1

        # Trend logic
        if trend_val == "BULLISH":
            score += 2
        elif trend_val == "BEARISH":
            score -= 2

        if score >= 3:
            return {"signal": "BUY", "score": score}

        if score <= -3:
            return {"signal": "SELL", "score": score}

        return {"signal": "HOLD", "score": score}
