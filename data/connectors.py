# connectors.py
# اتصال به صرافی‌ها و دریافت قیمت

import requests

BINANCE_API = "https://api.binance.com/api/v3/ticker/price"


def get_binance_price(symbol="BTCUSDT"):
    """
    دریافت قیمت لحظه‌ای از بایننس
    """

    try:
        response = requests.get(
            BINANCE_API,
            params={"symbol": symbol},
            timeout=5
        )

        data = response.json()

        return {
            "symbol": symbol,
            "price": float(data["price"])
        }

    except Exception as e:
        print("Binance Error:", e)
        return None


# تست مستقیم فایل
if __name__ == "__main__":
    result = get_binance_price()

    print(result)
