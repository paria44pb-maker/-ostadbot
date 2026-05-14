import requests
import os

API = os.getenv("NOBITEX_API_KEY")

headers = {
    "Authorization": f"Token {API}"
}

url = "https://api.nobitex.ir/users/wallets/list"

try:
    r = requests.get(url, headers=headers, timeout=20)

    print("STATUS:", r.status_code)
    print(r.text)

except Exception as e:
    print("ERROR:", e)
