import requests
from config import NOBITEX_API_KEY

headers = {
    "Authorization": f"Token {NOBITEX_API_KEY}"
}

def get_wallets():
    url = "https://api.nobitex.ir/users/wallets/list"

    response = requests.get(url, headers=headers)

    return response.json()
