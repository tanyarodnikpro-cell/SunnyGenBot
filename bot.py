import telebot
import os

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Бомжур, госпожижи ☀️\nЯ Солнечный Ген.\nРежим картошки активирован 🥔"
    )

@bot.message_handler(commands=['potato'])
def potato(message):
    bot.send_message(
        message.chat.id,
        "Сегодня официальный режим картошки 🥔"
    )

print("Ген проснулся ☀️")

bot.infinity_polling()
