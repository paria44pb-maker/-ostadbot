import requests


BASE_URL = "https://api.nobitex.ir"


def get_usdt_price():

    try:

        url = f"{BASE_URL}/market/stats"

        params = {
            "srcCurrency": "usdt",
            "dstCurrency": "rls"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        print("Nobitex Response:", data)

        return data["stats"]["usdt-rls"]["latest"]

    except Exception as e:

        print("Nobitex Error:", e)

        return "خطا در دریافت قیمت"
