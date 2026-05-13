   import telebot
   bot = telebot.TeleBot("توکن_خودت")
   @bot.message_handler(commands=['start'])
   def go(m): bot.reply_to(m, "بله، وصل شدم :)")
   bot.infinity_polling()
