import requests
import os
print("DEBUG: Bot starting...")

API_KEY = os.getenv("NOBITEX_API_KEY")

headers = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json"
}

BASE_URL = "https://185.xxx.xxx.xxx"   # IP واقعی که پیدا کردی

def get_wallet():

    try:

        url = f"{BASE_URL}/users/wallets/balance"

        r = requests.post(
            url,
            headers=headers,
            timeout=20,
            verify=False
        )

        print("STATUS:", r.status_code)
        print(r.text)

    except Exception as e:

        print("❌ Connection Error:", e)


get_wallet()
