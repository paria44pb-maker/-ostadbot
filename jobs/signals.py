import asyncio

async def signal_job():
    while True:
        print("Scanning market...")
        await asyncio.sleep(60)
