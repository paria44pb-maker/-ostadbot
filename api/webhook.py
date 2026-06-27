from fastapi import Request

async def telegram_webhook(request: Request):
    return {"ok": True}
