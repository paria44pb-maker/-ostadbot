import os
import asyncio
import requests
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@CryptoPulse606"

def get_crypto():
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=bitcoin,ethereum,tether"
        "&vs_currencies=usd"
    )

    data = requests.get(url, timeout=20).json()

    btc = data["bitcoin"]["usd"]
    eth = data["ethereum"]["usd"]
    usdt = data["tether"]["usd"]

    return btc, eth, usdt


def usd_to_toman():
    # قیمت دستی دلار
    # هر زمان خواستی تغییر بده
    return 85000


async def send_market():
    bot = Bot(BOT_TOKEN)

    btc, eth, usdt = get_crypto()

    dollar = usd_to_toman()

    btc_toman = int(btc * dollar)
    eth_toman = int(eth * dollar)
    usdt_toman = int(usdt * dollar)

    text = f"""
📊 CryptoPulse Market

💵 دلار:
{dollar:,} تومان

💲 تتر:
{usdt_toman:,} تومان

₿ بیت کوین:
{btc_toman:,} تومان

◆ اتریوم:
{eth_toman:,} تومان

🚀 @CryptoPulse606
"""

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=text
    )


async def scheduler():
    while True:
        try:
            await send_market()
        except:
            pass

        await asyncio.sleep(900)


if __name__ == "__main__":
    asyncio.run(scheduler())
