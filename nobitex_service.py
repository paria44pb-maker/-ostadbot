import requests

URL = "https://api.nobitex.ir/market/stats"


def get_prices():

    try:

        data = requests.get(URL, timeout=10).json()["stats"]

        return {
            "btc": data.get("btc-rls", {}).get("latest", "-"),
            "eth": data.get("eth-rls", {}).get("latest", "-"),
            "usdt": data.get("usdt-rls", {}).get("latest", "-"),
            "xrp": data.get("xrp-rls", {}).get("latest", "-"),
            "ton": data.get("ton-rls", {}).get("latest", "-")
        }

    except:

        return {
            "btc": "-",
            "eth": "-",
            "usdt": "-",
            "xrp": "-",
            "ton": "-"
        }
