import asyncio
import websockets

async def stream():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@trade"

    async with websockets.connect(uri) as ws:
        while True:
            msg = await ws.recv()
            print(msg)
