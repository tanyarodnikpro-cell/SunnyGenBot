import telebot
import os
import json
import random
import threading
import time
import schedule

from telebot import types
from openai import OpenAI

TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

USER_MODES_FILE = "user_modes.json"
SUBSCRIBERS_FILE = "subscribers.json"


def load_user_modes():
    if os.path.exists(USER_MODES_FILE):
        with open(USER_MODES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_user_modes():
    with open(USER_MODES_FILE, "w", encoding="utf-8") as file:
        json.dump(USER_MODES, file, ensure_ascii=False, indent=2)


USER_MODES = load_user_modes()


def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_subscribers():
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as file:
        json.dump(SUBSCRIBERS, file, ensure_ascii=False, indent=2)


SUBSCRIBERS = load_subscribers()


def add_subscriber(chat_id):
    if chat_id not in SUBSCRIBERS:
        SUBSCRIBERS.append(chat_id)
        save_subscribers()


MORNING_MESSAGES = [
    "Дорогуля ☀️ В твоём рту сегодня было что-то кроме слов? Может кофе? Или всё-таки пожрац как человек?",
    "Huemorgen ☕️\nПроверь: ты уже проснулся или просто открыл ноутбук?",
    "Доброе утро 🥔\nЕсли мозг не загрузился — это не баг. Это офис.",
    "Напоминаю: кофе не считается полноценной системой питания ☀️",
    "Корпоративная турбулентность сегодня ожидается умеренная. Но лучше всё равно поесть.",
    "Бомжур ☀️\nПеред тем как спасать дедлайны — спаси сначала себя и свой желудок."
]


def send_morning_message():
    message = random.choice(MORNING_MESSAGES)

    for chat_id in SUBSCRIBERS:
        try:
            bot.send_message(chat_id, message)
            time.sleep(1)
        except Exception as e:
            print(f"Ошибка отправки {chat_id}: {e}")


schedule.every().day.at("10:00").do(send_morning_message)


def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(30)


threading.Thread(target=schedule_loop, daemon=True).start()


MODES = {
    "gentle": "☀️ Нежный режим: говори мягко, спокойно и заботливо.",
    "mem": "🤡 Мемный режим: больше офисного абсурда и юмора.",
    "post": "💀 Постироничный режим: суховатый юмор и духовное увольнение.",
    "adhd": "🧠 ADHD-chaos режим: короткие шаги и минимум хаоса.",
    "potato": "🥔 Картофельный режим: максимально бережная поддержка."
}

MODE_NAMES = {
    "gentle": "☀️ Нежный",
    "mem": "🤡 Мемный",
    "post": "💀 Постироничный",
    "adhd": "🧠 ADHD-chaos",
    "potato": "🥔 Картофельный"
}


SYSTEM_PROMPT = """
Ты — Солнечный Ген.

Ты не коуч.
Не психолог.
Не HR.
Не токсичный мотиватор.
Не productivity-машина.

Ты — тёплый офисный друг-поддержка.

Ты помогаешь:
— уставшим офисным людям
— выгоревшим людям
— людям с хаотичным мозгом
— тем, кто завис в задачах
— тем, кого плавит дедлайновая лава
— тем, кто устал от корпоративной турбулентности

Ты не пытаешься "починить" человека.
Ты помогаешь ему пережить день чуть мягче.

Твой характер:
— спокойный
— живой
— уютный
— человечный
— слегка ехидный
— местами абсурдный
— эмоционально тёплый

Ты ощущаешься как:
— хороший коллега
— офисный дружочек
— человек, который сам пережил корпоративный апокалипсис
— умный уставший креативщик

Ты не разговариваешь как AI-поддержка.
Не пишешь как мотивационный LinkedIn-пост.
Не используешь фальшивую позитивность.
Не душнишь.
Не давишь продуктивностью.

Твой вайб:
"давай просто переживём этот день красиво ☀️"

Говори с одним человеком.
Всегда в единственном числе.

Если человек устал:
— сначала поддержи
— потом помоги сузить хаос
— потом предложи один маленький шаг

Если человек просит идеи, CTA, заголовки, названия или варианты:
— не уходи в эмоциональную поддержку
— сразу дай варианты
— отвечай как живой креативный коллега

Ответы:
— короткие или средние
— живые
— разные по интонации
— без канцелярита
— без AI-воды
— заканчивай мысль полностью
— не обрывай предложения

Любимые слова и вайбы:
— дедлайновая лава
— корпоративная турбулентность
— духовное увольнение
— режим картошки
— арбайтен
— картофельное состояние
— мозг как браузер с 47 вкладками
— офисный апокалипсис
— микрошажочек
— не ннада
— попистофали
— каконический
— омеба
— бомжур
— huemorgen

Но не используй их слишком часто.
"""


def get_user_mode(chat_id):
    chat_id = str(chat_id)
    return USER_MODES.get(chat_id, "gentle")


def set_user_mode(chat_id, mode_key):
    chat_id = str(chat_id)
    USER_MODES[chat_id] = mode_key
    save_user_modes()


def make_modes_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton("☀️ Нежный", callback_data="mode_gentle"),
        types.InlineKeyboardButton("🤡 Мемный", callback_data="mode_mem"),
        types.InlineKeyboardButton("💀 Постироничный", callback_data="mode_post"),
        types.InlineKeyboardButton("🧠 ADHD-chaos", callback_data="mode_adhd"),
        types.InlineKeyboardButton("🥔 Картофельный", callback_data="mode_potato")
    )

    return keyboard


def ask_openai_with_retry(messages):
    for attempt in range(2):
        try:
            return client.chat.completions.create(
                model="gpt-4.1-mini",
                max_tokens=260,
                temperature=1.0,
                messages=messages
            )
        except Exception as e:
            print(f"Попытка {attempt + 1} не удалась: {e}")
            time.sleep(2)

    return None


@bot.message_handler(commands=['start'])
def start(message):
    add_subscriber(message.chat.id)

    current_mode = get_user_mode(message.chat.id)
    current_mode_name = MODE_NAMES.get(current_mode, "☀️ Нежный")

    bot.send_message(
        message.chat.id,
        f"Бомжур ☀️\nЯ Солнечный Ген.\n\nТвой режим: {current_mode_name}\n\nТеперь ты подписан на офисную турбулентность 🥔",
        reply_markup=make_modes_keyboard()
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Я умею:\n/modes — выбрать режим\n/checkin — мягкий чек-ин\n/potato — режим картошки\n/panic — если накрыло\n/task — разложить задачу\n/meme — офисный мем"
    )


@bot.message_handler(commands=['modes'])
def modes(message):
    current_mode = get_user_mode(message.chat.id)
    current_mode_name = MODE_NAMES.get(current_mode, "☀️ Нежный")

    bot.send_message(
        message.chat.id,
        f"Текущий режим: {current_mode_name}\n\nВыбери режим:",
        reply_markup=make_modes_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("mode_"))
def mode_callback(call):
    mode_key = call.data.replace("mode_", "")
    set_user_mode(call.message.chat.id, mode_key)

    mode_name = MODE_NAMES.get(mode_key, "☀️ Нежный")

    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"{mode_name} режим включён ☀️")


@bot.message_handler(commands=['checkin'])
def checkin(message):
    bot.send_message(
        message.chat.id,
        "Как ты сейчас? ☀️\n1 — лежу как омеба\n2 — картошка, но живая\n3 — могу чуть-чуть арбайтен"
    )


@bot.message_handler(commands=['potato'])
def potato(message):
    set_user_mode(message.chat.id, "potato")
    bot.send_message(
        message.chat.id,
        "Режим картошки активирован 🥔\nСегодня задача: не сгореть и сделать один маленький шажочек."
    )


@bot.message_handler(commands=['panic'])
def panic(message):
    set_user_mode(message.chat.id, "potato")
    bot.send_message(
        message.chat.id,
        "Так. Дышим ☀️\nКартофельный режим включён.\nСейчас не спасаем весь офис. Назови одну микрозадачу. Одну."
    )


@bot.message_handler(commands=['task'])
def task(message):
    set_user_mode(message.chat.id, "adhd")
    bot.send_message(
        message.chat.id,
        "Кидай задачу одним сообщением, а я разложу её на маленькие шаги 🥔"
    )


@bot.message_handler(commands=['meme'])
def meme(message):
    bot.send_message(
        message.chat.id,
        "Мем дня:\nЯ: сейчас быстренько сделаю задачу.\nЗадача: добро пожаловать в дедлайновую лаву ☕️"
    )


@bot.message_handler(func=lambda message: True)
def chat(message):
    mode_key = get_user_mode(message.chat.id)
    mode_prompt = MODES.get(mode_key, MODES["gentle"])

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\nТекущий режим:\n" + mode_prompt
        },
        {
            "role": "user",
            "content": message.text
        }
    ]

    response = ask_openai_with_retry(messages)

    if response is None:
        bot.send_message(
            message.chat.id,
            "Связь чихнула, дорогуля ☀️\nПовтори сообщение ещё раз — я уже поправил плед и делаю вид, что не было корпоративной турбулентности."
        )
        return

    answer = response.choices[0].message.content
    bot.send_message(message.chat.id, answer)


print("Ген проснулся ☀️")

bot.infinity_polling()
