import aiohttp

BASE = "https://api.coinex.com/v2"

async def get_price(symbol="BTCUSDT"):
    url = f"{BASE}/spot/ticker?market={symbol}"
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            return await r.json()
