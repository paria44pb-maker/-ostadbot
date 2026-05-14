import requests
import time

session = requests.Session()
session.trust_env = False

URL = "https://api.nobitex.ir/users/wallets/list"


def get_wallets(api_key):
    headers = {
        "Authorization": f"Token {api_key}",
        "User-Agent": "Mozilla/5.0"
    }

    for i in range(3):  # 🔥 retry system
        try:
            r = session.get(URL, headers=headers, timeout=15)

            if r.status_code == 200:
                return r.json()

            elif r.status_code == 401:
                return {"error": "❌ API Key اشتباه است"}

            else:
                return {
                    "error": f"❌ خطای HTTP: {r.status_code}",
                    "body": r.text[:200]
                }

        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection Error: {str(e)}"

        except requests.exceptions.Timeout:
            last_error = "Timeout Error"

        time.sleep(2)

    return {"error": f"❌ تلاش ناموفق: {last_error}"}
