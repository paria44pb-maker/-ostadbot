import os

REQUIRED_ENVS = [
    "BOT_TOKEN",
    "GROQ_API_KEY",
]

def validate_env():
    missing = []

    for key in REQUIRED_ENVS:
        value = os.getenv(key)
        if not value or value.strip() == "":
            missing.append(key)

    if missing:
        raise RuntimeError(f"❌ Missing environment variables: {', '.join(missing)}")

    print("✅ All critical envs are OK")
