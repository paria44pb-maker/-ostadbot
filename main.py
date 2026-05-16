# ---------------- MAIN
def main():

    print("Booting Crypto Bot...")

    if not TELEGRAM_TOKEN:
        print("FATAL ERROR: TELEGRAM_TOKEN is not set in environment variables")
        return

    try:

        app = (
            ApplicationBuilder()
            .token(TELEGRAM_TOKEN)
            .build()
        )

        # Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(callback))
        app.add_handler(MessageHandler(filters.VOICE, ai_voice))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

        print("Handlers registered successfully")
        print("Bot is starting polling...")

        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

    except Exception as e:
        print("CRITICAL ERROR IN MAIN:", e)


if __name__ == "__main__":
    main()
