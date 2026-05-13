# services/nobitex_service.py

import os
import time
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional

import requests


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class NobitexAPIError(Exception):
    """Custom exception for Nobitex API errors."""
    pass


class NobitexClient:
    """
    Professional Nobitex API Client
    --------------------------------
    Features:
    ✅ Railway compatible
    ✅ Smart error handling
    ✅ Timeout protection
    ✅ Retry system
    ✅ Session reuse
    ✅ Logging
    ✅ Wallet methods
    ✅ Market methods
    ✅ Order methods
    ✅ Health check
    """

    def __init__(self):

        self.api_key = os.getenv("NOBITEX_API_KEY")

        if not self.api_key:
            raise ValueError(
                "❌ NOBITEX_API_KEY not found in environment variables."
            )

        self.base_url = "https://api.nobitex.ir"

        self.session = requests.Session()

        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

        self.timeout = 15
        self.max_retries = 3

        logging.info("✅ Nobitex Client Initialized")

    # =========================================================
    # INTERNAL REQUEST ENGINE
    # =========================================================

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> Dict[str, Any]:

        url = f"{self.base_url}{endpoint}"

        for attempt in range(1, self.max_retries + 1):

            try:

                response = self.session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )

                logging.info(
                    f"{method} {url} | Status: {response.status_code}"
                )

                # JSON decode safe
                try:
                    response_data = response.json()
                except Exception:
                    response_data = {
                        "raw_response": response.text
                    }

                # Success
                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "data": response_data
                    }

                # Unauthorized
                if response.status_code == 401:
                    raise NobitexAPIError(
                        "❌ Unauthorized | API Key invalid."
                    )

                # Forbidden
                if response.status_code == 403:
                    raise NobitexAPIError(
                        "❌ Forbidden | Permission denied or IP restricted."
                    )

                # Too many requests
                if response.status_code == 429:
                    logging.warning("⚠️ Rate limit reached.")
                    time.sleep(2)
                    continue

                # Other errors
                raise NobitexAPIError(
                    f"❌ API Error: {response.status_code} | {response.text}"
                )

            except requests.exceptions.Timeout:
                logging.warning(
                    f"⚠️ Timeout attempt {attempt}/{self.max_retries}"
                )

                if attempt == self.max_retries:
                    raise NobitexAPIError(
                        "❌ Request timeout."
                    )

            except requests.exceptions.ConnectionError:
                logging.warning(
                    f"⚠️ Connection error attempt {attempt}/{self.max_retries}"
                )

                if attempt == self.max_retries:
                    raise NobitexAPIError(
                        "❌ Connection failed."
                    )

            except Exception as e:
                raise NobitexAPIError(str(e))

        raise NobitexAPIError("❌ Unknown request error.")

    # =========================================================
    # HEALTH CHECK
    # =========================================================

    def health_check(self):

        try:

            response = requests.get(
                f"{self.base_url}/market/stats",
                timeout=10
            )

            return {
                "success": True,
                "status_code": response.status_code,
                "message": "✅ Nobitex reachable"
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    # =========================================================
    # USER WALLET
    # =========================================================

    def get_wallets(self):

        return self._request(
            method="GET",
            endpoint="/users/wallets/list"
        )

    def get_balance(self, currency: str = "usdt"):

        wallets = self.get_wallets()

        if not wallets["success"]:
            return wallets

        data = wallets["data"]

        for wallet in data.get("wallets", []):

            if wallet.get("currency", "").lower() == currency.lower():

                return {
                    "success": True,
                    "currency": currency,
                    "balance": wallet.get("balance"),
                    "active_balance": wallet.get("activeBalance"),
                    "deposit_address": wallet.get("depositAddress")
                }

        return {
            "success": False,
            "message": f"{currency} wallet not found."
        }

    # =========================================================
    # MARKET DATA
    # =========================================================

    def get_orderbook(self, market: str = "BTCUSDT"):

        return self._request(
            method="GET",
            endpoint=f"/v2/orderbook/{market}"
        )

    def get_market_stats(self):

        return self._request(
            method="GET",
            endpoint="/market/stats"
        )

    # =========================================================
    # ORDERS
    # =========================================================

    def create_order(
        self,
        market: str,
        side: str,
        price: str,
        amount: str,
        order_type: str = "limit"
    ):

        payload = {
            "type": side,
            "srcCurrency": market[:-4].lower(),
            "dstCurrency": market[-4:].lower(),
            "price": price,
            "amount": amount,
            "execution": order_type
        }

        return self._request(
            method="POST",
            endpoint="/market/orders/add",
            data=payload
        )

    def get_open_orders(self):

        return self._request(
            method="POST",
            endpoint="/market/orders/list",
            data={
                "status": "open"
            }
        )

    def cancel_order(self, order_id: str):

        return self._request(
            method="POST",
            endpoint="/market/orders/cancel",
            data={
                "order": order_id
            }
        )

    # =========================================================
    # PRICE
    # =========================================================

    def get_price(self, symbol: str = "BTCUSDT"):

        result = self.get_orderbook(symbol)

        if not result["success"]:
            return result

        data = result["data"]

        try:

            best_sell = data["asks"][0][0]
            best_buy = data["bids"][0][0]

            return {
                "success": True,
                "symbol": symbol,
                "buy_price": best_buy,
                "sell_price": best_sell
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    # =========================================================
    # DEBUG
    # =========================================================

    def debug_connection(self):

        return {
            "base_url": self.base_url,
            "api_key_exists": bool(self.api_key),
            "headers": {
                "Authorization": "Token ********",
                "Content-Type": "application/json"
            }
        }


# =============================================================
# QUICK TEST
# =============================================================

if __name__ == "__main__":

    try:

        client = NobitexClient()

        print("\n✅ HEALTH CHECK")
        print(client.health_check())

        print("\n✅ WALLETS")
        print(client.get_wallets())

        print("\n✅ BTC PRICE")
        print(client.get_price("BTCUSDT"))

    except Exception as error:

        print("\n❌ ERROR")
        print(str(error))
