import os
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode


class CoinExEngine:
    """
    Basic CoinEx trading connector
    """

    def __init__(self):
        self.api_key = os.getenv("COINEX_API_KEY")
        self.secret_key = os.getenv("COINEX_SECRET_KEY")
        self.base_url = "https://api.coinex.com/v1"

    # =========================
    # 🔐 SIGNATURE
    # =========================
    def _sign(self, params: dict):
        query = urlencode(sorted(params.items()))
        signature = hmac.new(
            self.secret_key.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    # =========================
    # 📊 GET MARKET PRICE
    # =========================
    def get_ticker(self, market="BTCUSDT"):
        url = f"{self.base_url}/market/ticker"
        params = {"market": market}

        res = requests.get(url, params=params)
        return res.json()

    # =========================
    # 💰 PLACE ORDER
    # =========================
    def place_order(self, market, side, amount, price=None):
        url = f"{self.base_url}/order/limit"

        params = {
            "access_id": self.api_key,
            "market": market,
            "type": side,  # buy / sell
            "amount": amount,
            "price": price or 0,
            "tonce": int(time.time() * 1000)
        }

        params["signature"] = self._sign(params)

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=params, headers=headers)
        return response.json()

    # =========================
    # 📊 SIMPLE PRICE CHANGE ANALYSIS
    # =========================
    def get_price_change_signal(self, market="BTCUSDT"):
        data = self.get_ticker(market)

        try:
            last = float(data["data"]["ticker"]["last"])
            open_price = float(data["data"]["ticker"]["open"])

            change = ((last - open_price) / open_price) * 100

            if change > 2:
                return {"signal": "BUY", "change": change}

            if change < -2:
                return {"signal": "SELL", "change": change}

            return {"signal": "HOLD", "change": change}

        except Exception:
            return {"signal": "ERROR", "change": 0}
