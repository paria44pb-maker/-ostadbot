Trend: {structure['trend']}
RSI: {structure['rsi']}
Momentum: {structure['momentum']}

Signal: {signal}

AI Analysis:
{analysis}
"""

    await update.message.reply_photo(
        open(img,"rb"),
        caption=msg
    )


# -------------------------------
# MAIN
# -------------------------------

def main():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("analyze", analyze))

    print("Bot Started...")

    app.run_polling()


if name == "main":

    main()
