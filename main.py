from fastapi import FastAPI
from bot.bot_main import router as bot_router

app = FastAPI(title="WhaleMind AI")

app.include_router(bot_router)


@app.get("/")
async def root():
    return {"message": "WhaleMind AI Running"}
