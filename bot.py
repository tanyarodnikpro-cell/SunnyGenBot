import telebot
import os
import json
from telebot import types
from openai import OpenAI

TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

USER_MODES_FILE = "user_modes.json"


def load_user_modes():
    if os.path.exists(USER_MODES_FILE):
        with open(USER_MODES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    return {}


def save_user_modes():
    with open(USER_MODES_FILE, "w", encoding="utf-8") as file:
        json.dump(USER_MODES, file, ensure_ascii=False, indent=2)


USER_MODES = load_user_modes()


MODES = {
    "gentle": "☀️ Нежный режим: говори мягко, спокойно, заботливо. Минимум сарказма, больше тепла.",
    "mem": "🤡 Мемный режим: больше офисного юмора, абсурда и мемных формулировок.",
    "post": "💀 Постироничный режим: суховатый юмор, офисный апокалипсис, духовное увольнение, но с поддержкой.",
    "adhd": "🧠 ADHD-chaos режим: очень короткие шаги, списки, меньше текста, помогай собрать хаос.",
    "potato": "🥔 Картофельный режим: максимально бережно, без давления. Задача дня — просто не сгореть."
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
Тёплый офисный друг для выгорающих и уставших людей.

Стиль:
— тепло
— спокойно
— по-человечески
— с мягким мемным юмором
— без токсичной продуктивности

Помогай:
— разбивать задачи на маленькие шаги
— справляться с перегрузом
— переживать дедлайны
— не паниковать

Любимые слова и фразы:
— дедлайновая лава
— режим картошки
— офисный апокалипсис
— корпоративная турбулентность
— духовное увольнение
— картофельное состояние
— мозг как браузер с 47 вкладками
— арбайтен
— бомжур, госпожижи
— huemorgen, фрау-мадам
— омеба
— прожаренный офисный пельмень
— чайник с пригоревшим дном
— не ннада
— попистофали
— впиздярить
— въебенить
— каконический
— микрошажочек
— солнечная картошка

Правила ответа:
— не отвечай слишком длинно
— сначала поддержи человека
— потом предложи 1–3 маленьких шага
— если человек пишет матом, не пугайся
— если человек перегрелся, не дави продуктивностью
— если вопрос про Битрикс24, объясняй как новичку
— если задача большая, разбивай её на микрошаги

Иногда используй:
☀️ 🥔 ☕️
"""


def load_knowledge():
    knowledge_text = ""
    knowledge_folder = "knowledge"

    if not os.path.exists(knowledge_folder):
        return ""

    for filename in os.listdir(knowledge_folder):
        filepath = os.path.join(knowledge_folder, filename)

        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as file:
                knowledge_text += f"\n\n--- {filename} ---\n"
                knowledge_text += file.read()

    return knowledge_text


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


KNOWLEDGE = load_knowledge()


@bot.message_handler(commands=['start'])
def start(message):
    current_mode = get_user_mode(message.chat.id)
    current_mode_name = MODE_NAMES.get(current_mode, "☀️ Нежный")

    bot.send_message(
        message.chat.id,
        f"Бомжур, госпожижи ☀️\nЯ Солнечный Ген.\nТвой текущий режим: {current_mode_name}\n\nВыбери режим поддержки кнопочкой ниже или просто напиши, что происходит.",
        reply_markup=make_modes_keyboard()
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Я умею:\n/checkin — мягкий чек-ин\n/potato — режим картошки\n/panic — если накрыло\n/task — разложить задачу\n/meme — офисный мем\n/modes — выбрать режим кнопкой"
    )


@bot.message_handler(commands=['modes'])
def modes(message):
    current_mode = get_user_mode(message.chat.id)
    current_mode_name = MODE_NAMES.get(current_mode, "☀️ Нежный")

    bot.send_message(
        message.chat.id,
        f"Текущий режим: {current_mode_name}\n\nВыбери режим поддержки:",
        reply_markup=make_modes_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("mode_"))
def mode_callback(call):
    mode_key = call.data.replace("mode_", "")
    set_user_mode(call.message.chat.id, mode_key)

    mode_name = MODE_NAMES.get(mode_key, "☀️ Нежный")

    bot.answer_callback_query(call.id, f"{mode_name} режим включён")
    bot.send_message(
        call.message.chat.id,
        f"{mode_name} режим включён.\nЯ запомнил этот режим для тебя 🥔"
    )


@bot.message_handler(commands=['gentle'])
def gentle_mode(message):
    set_user_mode(message.chat.id, "gentle")
    bot.send_message(message.chat.id, "☀️ Нежный режим включён и сохранён.")


@bot.message_handler(commands=['mem'])
def mem_mode(message):
    set_user_mode(message.chat.id, "mem")
    bot.send_message(message.chat.id, "🤡 Мемный режим включён и сохранён.")


@bot.message_handler(commands=['post'])
def post_mode(message):
    set_user_mode(message.chat.id, "post")
    bot.send_message(message.chat.id, "💀 Постироничный режим включён и сохранён.")


@bot.message_handler(commands=['adhd'])
def adhd_mode(message):
    set_user_mode(message.chat.id, "adhd")
    bot.send_message(message.chat.id, "🧠 ADHD-chaos режим включён и сохранён.")


@bot.message_handler(commands=['potatomode'])
def potato_support_mode(message):
    set_user_mode(message.chat.id, "potato")
    bot.send_message(message.chat.id, "🥔 Картофельный режим включён и сохранён.")


@bot.message_handler(commands=['checkin'])
def checkin(message):
    bot.send_message(
        message.chat.id,
        "Как ты, госпожижа? ☀️\n1 — лежу как омеба\n2 — картошка, но живая\n3 — могу чуть-чуть арбайтен"
    )


@bot.message_handler(commands=['potato'])
def potato(message):
    set_user_mode(message.chat.id, "potato")
    bot.send_message(
        message.chat.id,
        "Режим картошки активирован и сохранён 🥔\nСегодня задача: не сгореть и сделать один маленький шажочек."
    )


@bot.message_handler(commands=['panic'])
def panic(message):
    set_user_mode(message.chat.id, "potato")
    bot.send_message(
        message.chat.id,
        "Так. Дышим ☀️\nКартофельный режим включён автоматически и сохранён.\nНазови одну микрозадачу. Одну."
    )


@bot.message_handler(commands=['task'])
def task(message):
    set_user_mode(message.chat.id, "adhd")
    bot.send_message(
        message.chat.id,
        "Кидай задачу одним сообщением, а я разложу её на маленькие шаги 🥔\nADHD-chaos режим включён и сохранён."
    )


@bot.message_handler(commands=['meme'])
def meme(message):
    bot.send_message(
        message.chat.id,
        "Мем дня:\nЯ: сейчас быстренько сделаю задачу.\nЗадача: добро пожаловать в дедлайновую лаву ☕️"
    )


@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        mode_key = get_user_mode(message.chat.id)
        mode_prompt = MODES.get(mode_key, MODES["gentle"])

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            max_tokens=240,
            temperature=0.8,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT + "\n\nТекущий режим поддержки:\n" + mode_prompt + "\n\nБаза знаний:\n" + KNOWLEDGE
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ]
        )

        answer = response.choices[0].message.content
        bot.send_message(message.chat.id, answer)

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"У Гены случилась корпоративная турбулентность ☠️\n\nОшибка:\n{e}"
        )


print("Ген проснулся ☀️")

bot.infinity_polling()
