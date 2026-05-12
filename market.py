import requests

BASE_URL = "https://api.binance.com/api/v3"


def get_price(symbol="BTCUSDT"):

    url = f"{BASE_URL}/ticker/price?symbol={symbol}"

    response = requests.get(url, timeout=10)

    data = response.json()

    return float(data["price"])


def get_24h(symbol="BTCUSDT"):

    url = f"{BASE_URL}/ticker/24hr?symbol={symbol}"

    response = requests.get(url, timeout=10)

    return response.json()
  
