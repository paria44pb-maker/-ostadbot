import requests
import os

NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")


def get_wallets():
    if not NOBITEX_API_KEY:
        return "❌ API Key تنظیم نشده"

    url = "https://api.nobitex.ir/users/wallets/list"

    headers = {
        "Authorization": f"Token {NOBITEX_API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code != 200:
            return f"❌ خطا از نوبیتکس: {data}"

        wallets = data.get("wallets", [])

        if not wallets:
            return "📭 هیچ موجودی‌ای پیدا نشد"

        text = "💰 موجودی حساب نوبیتکس:\n\n"

        for w in wallets:
            currency = w.get("currency", "unknown")
            balance = w.get("balance", 0)

            if float(balance) > 0:
                text += f"• {currency}: {balance}\n"

        return text

    except Exception as e:
        return f"❌ خطا در اتصال: {str(e)}"
