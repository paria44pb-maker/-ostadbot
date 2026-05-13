# test_nobitex.py

import os
import requests

# دریافت API KEY از متغیر محیطی
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")

if not NOBITEX_API_KEY:
    raise ValueError("متغیر محیطی NOBITEX_API_KEY تنظیم نشده است!")

# هدر احراز هویت
HEADERS = {
    "Authorization": f"Token {NOBITEX_API_KEY}",
    "Content-Type": "application/json"
}

# آدرس تست دریافت موجودی
URL = "https://api.nobitex.ir/users/wallets/list"

try:
    print("در حال اتصال به نوبیتکس...")

    response = requests.get(URL, headers=HEADERS)

    print(f"Status Code: {response.status_code}")
    print("Response:")

    try:
        data = response.json()
        print(data)
    except:
        print(response.text)

    if response.status_code == 200:
        print("\n✅ اتصال به نوبیتکس موفق بود")
    elif response.status_code == 401:
        print("\n❌ خطای احراز هویت - API KEY اشتباه است")
    elif response.status_code == 403:
        print("\n❌ دسترسی ممنوع")
    else:
        print("\n⚠️ خطای ناشناخته")

except Exception as ex:
    print(f"\n❌ خطای سیستمی:\n{ex}")
