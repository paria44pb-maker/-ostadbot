import os
import requests

# دریافت API KEY از Railway
API_KEY = os.getenv("NOBITEX_API_KEY")

if not API_KEY:
    raise Exception("NOBITEX_API_KEY not found")

# هدر صحیح نوبیتکس
HEADERS = {
    "Authorization": f"Token {API_KEY}"
}

BASE_URL = "https://api.nobitex.ir"


# تست اتصال
def test_connection():

    try:

        response = requests.get(
            f"{BASE_URL}/users/wallets/list",
            headers=HEADERS,
            timeout=15
        )

        print("STATUS CODE:", response.status_code)
        print("RESPONSE:", response.text)

        return {
            "status": response.status_code,
            "data": response.text
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "status": "error",
            "data": str(e)
        }


# گرفتن کیف پول‌ها
def get_wallets():

    try:

        response = requests.get(
            f"{BASE_URL}/users/wallets/list",
            headers=HEADERS,
            timeout=15
        )

        if response.status_code == 200:
            return response.json()

        return {
            "error": response.text,
            "status_code": response.status_code
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# قیمت بازار
def get_market_stats():

    try:

        response = requests.get(
            f"{BASE_URL}/market/stats",
            timeout=15
        )

        return response.json()

    except Exception as e:

        return {
            "error": str(e)
        }
