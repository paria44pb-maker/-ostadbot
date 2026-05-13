import requests

BASE_URL = "https://api.nobitex.ir"


def get_usdt_price():

    url = f"{BASE_URL}/market/stats"

    params = {
        "srcCurrency": "usdt",
        "dstCurrency": "rls"
    }

    response = requests.get(url, params=params)

    data = response.json()

    return data["stats"]["usdt-rls"]["latest"]
