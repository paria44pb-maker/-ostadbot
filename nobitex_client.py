import requests
import time
import logging
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NobitexClient:
    """
    A client for interacting with the Nobitex API, designed with robustness
    and adherence to Nobitex's usage policies in mind.
    """
    BASE_URL = "https://api.nobitex.ir"
    # These placeholders need to be replaced with actual credentials,
    # ideally loaded from environment variables or a secure config file.
    # DO NOT hardcode credentials here in a production environment.
    API_KEY = os.getenv("NOBITEX_API_KEY", "YOUR_API_KEY_HERE")
    SECRET = os.getenv("NOBITEX_SECRET_HERE", "YOUR_SECRET_HERE")

    # Nobitex rate limit is not explicitly stated with an SLA,
    # but general API best practices suggest avoiding excessive requests.
    # We implement a small delay and retry mechanism.
    REQUEST_DELAY = 0.5  # seconds between requests
    MAX_RETRIES = 3
    RETRY_DELAY_MULTIPLIER = 2 # Exponential backoff

    def __init__(self, api_key: Optional[str] = None, secret: Optional[str] = None):
        """
        Initializes the Nobitex client.
        Args:
            api_key: Your Nobitex API key.
            secret: Your Nobitex API secret.
        """
        self.session = requests.Session()
        # Using headers for authentication as per common API practices,
        # but Nobitex might use different mechanisms (e.g., query params for some endpoints).
        # Adjust this part if specific endpoints require different auth methods.
        if api_key and secret:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}', # Example, adjust if needed
                'Content-Type': 'application/json',
                'X-API-KEY': api_key,
                'X-API-SECRET': secret,
            })
        else:
            logging.warning("API Key and Secret not provided. Using public endpoints only or relying on default headers if any.")
            self.session.headers.update({'Content-Type': 'application/json'})

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, is_public: bool = True) -> Dict[str, Any]:
        """
        Internal method to make HTTP requests with retry logic and delay.
        Handles public and private endpoints.
        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint (e.g., "/market/stats").
            params: URL parameters for GET requests.
            data: JSON payload for POST/PUT requests.
            is_public: True if the endpoint is public, False if it requires authentication.
        Returns:
            The JSON response from the API.
        Raises:
            requests.exceptions.RequestException: If the request fails after retries.
            ValueError: If the response is not valid JSON or contains an error.
        """
        url = f"{self.BASE_URL}{endpoint}"
        retries = 0
        backoff_factor = 1

        while retries < self.MAX_RETRIES:
            try:
                # Add a small delay before each request to be polite to the API
                time.sleep(self.REQUEST_DELAY)

                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    # If not public, ensure auth headers are present
                    headers=self.session.headers if not is_public else None # Adjust if public endpoints also need specific headers
                )

                # Check for common error status codes
                if response.status_code == 429: # Too Many Requests
                    logging.warning(f"Rate limit hit for {endpoint}. Retrying in {backoff_factor * self.RETRY_DELAY_MULTIPLIER}s...")
                    time.sleep(backoff_factor * self.RETRY_DELAY_MULTIPLIER)
                    backoff_factor *= self.RETRY_DELAY_MULTIPLIER
                    retries += 1
                    continue
                elif response.status_code >= 400:
                    # Attempt to parse error message from response
                    try:
                        error_data = response.json()
                        error_message = error_data.get("message", f"HTTP Error {response.status_code}")
                        logging.error(f"API Error for {endpoint}: {error_message} - Response: {response.text}")
                    except requests.exceptions.JSONDecodeError:
                        logging.error(f"API Error for {endpoint}: HTTP {response.status_code} - Response: {response.text}")
                    raise requests.exceptions.HTTPError(f"API returned status code {response.status_code}: {response.text}")

                # Success case
                response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
                return response.json()

            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed for {endpoint}: {e}. Attempt {retries + 1}/{self.MAX_RETRIES}")
                if retries >= self.MAX_RETRIES - 1:
                    raise e # Re-raise the last exception if all retries failed
                retries += 1
                time.sleep(backoff_factor * self.RETRY_DELAY_MULTIPLIER)
                backoff_factor *= self.RETRY_DELAY_MULTIPLIER
            except ValueError as e: # For JSON decoding errors
                logging.error(f"JSON decode error for {endpoint}: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
                raise ValueError(f"Failed to decode JSON response: {e}")

        # If loop finishes without returning, it means max retries were exceeded
        raise requests.exceptions.RequestException(f"Max retries ({self.MAX_RETRIES}) exceeded for {endpoint}")

    def get_market_stats(self) -> Dict[str, Any]:
        """
        Fetches market statistics for all trading pairs.
        This is a public endpoint.
        """
        logging.info("Fetching market stats...")
        return self._make_request("GET", "/market/stats", is_public=True)

    def get_trading_pairs(self) -> Dict[str, Any]:
        """
        Fetches available trading pairs.
        This is a public endpoint.
        """
        logging.info("Fetching trading pairs...")
        return self._make_request("GET", "/market/trades", is_public=True)

    def get_order_book(self, pair: str) -> Dict[str, Any]:
        """
        Fetches the order book for a given trading pair.
        Args:
            pair: The trading pair (e.g., "btc-rls").
        This is a public endpoint.
        """
        logging.info(f"Fetching order book for {pair}...")
        return self._make_request("GET", f"/market/orderbook/{pair}", is_public=True)

    def get_latest_price(self, pair: str) -> Optional[str]:
        """
        Fetches the latest price for a given trading pair.
        Args:
            pair: The trading pair (e.g., "btc-rls").
        Returns:
            The latest price as a string, or None if not found or error.
        """
        try:
            stats = self.get_market_stats()
            return stats.get("stats", {}).get(pair, {}).get("latest")
        except Exception as e:
            logging.error(f"Failed to get latest price for {pair}: {e}")
            return None

    # --- Example Private Endpoints (Uncomment and adapt if needed) ---
    # These endpoints require API Key and Secret and are often rate-limited.
    # Make sure your provided API Key and Secret have the necessary permissions.

    # def get_balance(self) -> Dict[str, Any]:
    #     """
    #     Fetches the user's account balance.
    #     Requires authentication.
    #     """
    #     logging.info("Fetching account balance...")
    #     return self._make_request("POST", "/panel/balance", is_public=False)

    # def create_buy_order(self, pair: str, amount: float, price: float) -> Dict[str, Any]:
    #     """
    #     Creates a buy order.
    #     Args:
    #         pair: Trading pair (e.g., "btc-rls").
    #         amount: Amount to buy.
    #         price: Price per unit.
    #     Requires authentication.
    #     """
    #     logging.info(f"Creating buy order for {amount} {pair.split('-')[0]} at {price}...")
    #     data = {
    #         "pair": pair,
    #         "amount": str(amount),
    #         "price": str(price),
    #         "order_type": "buy" # or "sell"
    #     }
    #     return self._make_request("POST", "/exchange/order", data=data, is_public=False)

    # def create_sell_order(self, pair: str, amount: float, price: float) -> Dict[str, Any]:
    #     """
    #     Creates a sell order.
    #     Args:
    #         pair: Trading pair (e.g., "btc-rls").
    #         amount: Amount to sell.
    #         price: Price per unit.
    #     Requires authentication.
    #     """
    #     logging.info(f"Creating sell order for {amount} {pair.split('-')[0]} at {price}...")
    #     data = {
    #         "pair": pair,
    #         "amount": str(amount),
    #         "price": str(price),
    #         "order_type": "sell"
    #     }
    #     return self._make_request("POST", "/exchange/order", data=data, is_public=False)

# --- Example Usage (for testing the client directly) ---
if __name__ == "__main__":
    # Load credentials from environment variables for security
    import os
    nobitex_api_key = os.getenv("NOBITEX_API_KEY")
    nobitex_secret = os.getenv("NOBITEX_SECRET")

    # Instantiate the client. If credentials are not set, it will use placeholders
    # and will only be able to access public endpoints.
    client = NobitexClient(api_key=nobitex_api_key, secret=nobitex_secret)

    try:
        # Example: Get BTC price (public endpoint)
        btc_price = client.get_latest_price("btc-rls")
        if btc_price:
            print(f"Latest BTC price on Nobitex: {btc_price}")
        else:
            print("Could not retrieve BTC price.")

        # Example: Get market stats (public endpoint)
        stats = client.get_market_stats()
        print(f"Market Stats (first few entries): {dict(list(stats.get('stats', {}).items())[:3])}")

        # Example: Get order book for BTC-RLS (public endpoint)
        # order_book = client.get_order_book("btc-rls")
        # print(f"BTC-RLS Order Book (Bids): {order_book.get('bids', [])[:3]}")

        # Example: Get balance (private endpoint - requires valid API Key/Secret)
        # if nobitex_api_key and nobitex_secret:
        #     balance = client.get_balance()
        #     print(f"Account Balance: {balance}")
        # else:
        #     print("\nSkipping balance check: NOBITEX_API_KEY or NOBITEX_SECRET not set.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during API interaction: {e}")
    except ValueError as e:
        print(f"A data processing error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
