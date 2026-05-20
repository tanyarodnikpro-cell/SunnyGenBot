import telebot
import os

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бомжур, госпожижи ☀️\nЯ Солнечный Ген.\nПомогу пережить офисный апокалипсис.")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Я умею:\n/checkin — мягкий чек-ин\n/potato — режим картошки\n/panic — если накрыло\n/task — разложить задачу\n/meme — офисный мем")

@bot.message_handler(commands=['checkin'])
def checkin(message):
    bot.send_message(message.chat.id, "Как ты, госпожижа? ☀️\n1 — лежу как омеба\n2 — картошка, но живая\n3 — могу чуть-чуть арбайтен")

@bot.message_handler(commands=['potato'])
def potato(message):
    bot.send_message(message.chat.id, "Режим картошки активирован 🥔\nСегодня задача: не сгореть и сделать один маленький шажочек.")

@bot.message_handler(commands=['panic'])
def panic(message):
    bot.send_message(message.chat.id, "Так. Дышим ☀️\nТы не обязана победить весь офисный апокалипсис.\nСейчас выбери одну микрозадачу. Одну. Не героизм.")

@bot.message_handler(commands=['task'])
def task(message):
    bot.send_message(message.chat.id, "Кидай задачу одним сообщением, а я разложу её на маленькие шаги. Пока я ещё учебная картошка, но уже стараюсь 🥔")

@bot.message_handler(commands=['meme'])
def meme(message):
    bot.send_message(message.chat.id, "Мем дня:\nЯ: сейчас быстренько сделаю задачу.\nЗадача: добро пожаловать в дедлайновую лаву ☕️")

print("Ген проснулся ☀️")

bot.infinity_polling()
