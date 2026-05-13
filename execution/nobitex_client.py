# nobitex_client.py
# ارتباط با API نوبیتکس

import requests

BASE_URL = "https://api.nobitex.ir"


class NobitexClient:

    def __init__(self, api_key):
        self.api_key = api_key

    def get_wallet(self):
        url = f"{BASE_URL}/users/wallets/list"

        headers = {
            "Authorization": f"Token {self.api_key}"
        }

        r = requests.get(url, headers=headers)

        return r.json()

    def place_order(self, market, side, price, amount):
        """
        market: BTCUSDT
        side: buy or sell
        """

        url = f"{BASE_URL}/market/orders/add"

        headers = {
            "Authorization": f"Token {self.api_key}"
        }

        data = {
            "type": side,
            "srcCurrency": market[:3],
            "dstCurrency": market[3:],
            "amount": str(amount),
            "price": str(price)
        }

        r = requests.post(url, json=data, headers=headers)

        return r.json()
