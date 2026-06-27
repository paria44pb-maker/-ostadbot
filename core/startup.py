from core.database import init_db

async def init_app():
    await init_db()
    print("System Initialized 🚀")
