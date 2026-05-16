import os
import requests

API_KEY = os.getenv("NOBITEX_API_KEY")

URL = "https://api.nobitex.ir/market/orders/add"

def buy_btc(amount):

    headers = {
        "Authorization": f"Token {API_KEY}"
    }

    payload = {
        "type":"buy",
        "srcCurrency":"rls",
        "dstCurrency":"btc",
        "amount":amount
    }

    r = requests.post(URL,json=payload,headers=headers)

    return r.json()
