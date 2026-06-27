import asyncio
from market.coinex import ticker
from signals.engine import generate_signal

async def run():
    while True:
        data = await ticker("BTCUSDT")
        signal = generate_signal(60, 28, 900000)

        print("SIGNAL:", signal)

        await asyncio.sleep(60)
