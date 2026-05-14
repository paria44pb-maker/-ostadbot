import requests
import os

NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")

session = requests.Session()
session.trust_env = False  # 🚀 جلوگیری از DNS/env conflict


def get_wallets():
    if not NOBITEX_API_KEY:
        return "❌ API Key تنظیم نشده"

    url = "https://api.nobitex.ir/users/wallets/list"

    headers = {
        "Authorization": f"Token {NOBITEX_API_KEY}"
    }

    try:
        response = session.get(
            url,
            headers=headers,
            timeout=20
        )

        data = response.json()

        if response.status_code != 200:
            return f"❌ خطای نوبیتکس: {data}"

        wallets = data.get("wallets", [])

        if not wallets:
            return "📭 موجودی‌ای پیدا نشد"

        text = "💰 موجودی نوبیتکس:\n\n"

        for w in wallets:
            currency = w.get("currency")
            balance = w.get("balance", 0)

            if float(balance) > 0:
                text += f"• {currency}: {balance}\n"

        return text

    except Exception as e:
        return f"❌ خطای اتصال (DNS/Network): {str(e)}"
