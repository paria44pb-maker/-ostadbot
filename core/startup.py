from security.validator import validate_env

async def init_app():
    print("🚀 Starting CryptoPulse SAFE MODE...")

    # 1. validate envs first
    validate_env()

    # 2. later you can add db init
    print("✅ Core systems loaded safely")
