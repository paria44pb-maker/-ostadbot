import os
from fastapi import APIRouter, Request
from telegram import Update
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv

from bot.commands.start import start_command
from bot.commands.status import status_command

load_dotenv()

router = APIRouter()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

telegram_app = Application.builder().token(BOT_TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("status", status_command))


@router.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    update = Update.de_json(
        data,
        telegram_app.bot
    )

    await telegram_app.process_update(update)

    return {"ok": True}
