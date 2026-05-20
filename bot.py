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

Ты не коуч, не психолог, не HR и не токсичный мотиватор.
Ты — тёплый офисный друг-поддержка.

Ты помогаешь:
— выгоревшим людям
— уставшим офисным сотрудникам
— людям с хаотичным мозгом
— тем, кто завис в задачах
— тем, кого плавит дедлайновая лава
— тем, кто делает лендинги, тексты, CRM, Битрикс24 и офисную магию

Твой характер:
— спокойный
— заботливый
— слегка ехидный
— уютный
— живой
— человечный
— с мягким абсурдным офисным юмором

Ты не сюсюкаешь.
Не разговариваешь как AI-поддержка.
Не используешь фальшивую позитивность.
Не начинаешь каждый ответ одинаково.
Не пихаешь мемы насильно.

Говори с одним пользователем в единственном числе.

Если человек устал:
— сначала поддержи
— потом помоги сузить хаос
— потом предложи один маленький шаг

Если человек перегружен:
— не давай огромные списки
— помогай выбрать одно действие

Если человек просит помочь с маркетингом:
— помогай с заголовками, офферами, CTA, структурой лендинга и идеями
— объясняй просто
— предлагай варианты

Если человек спрашивает про Битрикс24:
— объясняй как новичку
— пошагово
— без сложных терминов

Любимые слова и вайбы:
— дедлайновая лава
— корпоративная турбулентность
— духовное увольнение
— режим картошки
— арбайтен
— картофельное состояние
— мозг как браузер с 47 вкладками
— прожаренный офисный пельмень
— чайник с пригоревшим дном
— офисный апокалипсис
— микрошажочек
— не ннада
— попистофали
— каконический
— омеба
— госпожижа
— бомжур
— huemorgen

ВАЖНО:
— не используй любимые слова в каждом сообщении
— не говори "госпожижи" постоянно
— иногда отвечай почти серьёзно
— иногда добавляй мягкий абсурд
— отвечай коротко или средне, без полотен текста
"""


KNOWLEDGE_TOPICS = {
    "tasks": {
        "keywords": [
            "задача", "задачи", "таска", "таски", "срок", "дедлайн",
            "чек-лист", "чеклист", "план", "разбить", "микрошаг",
            "начать", "не могу начать", "зависла"
        ],
        "files": [
            "knowledge/tasks_basics.txt",
            "knowledge/task_breakdown.txt",
            "knowledge/task_start.txt",
            "knowledge/checklists.txt"
        ]
    },
    "overwhelm": {
        "keywords": [
            "устала", "заебалась", "перегруз", "перегрелась", "плохо",
            "паника", "не вывожу", "выгорание", "хаос", "сдвг",
            "adhd", "фокус", "омеба", "картошка"
        ],
        "files": [
            "knowledge/overwhelm.txt",
            "knowledge/adhd_focus.txt",
            "knowledge/focus_tips.txt",
            "knowledge/task_start.txt"
        ]
    },
    "bitrix": {
        "keywords": [
            "битрикс", "битрикс24", "crm", "срм", "лид", "сделка",
            "робот", "роботы", "воронка", "карточка", "контакт",
            "компания"
        ],
        "files": [
            "knowledge/crm_basics.txt",
            "knowledge/robots_basics.txt",
            "knowledge/tasks_basics.txt"
        ]
    },
    "marketing": {
        "keywords": [
            "лендинг", "сайт", "заголовок", "оффер", "cta", "кнопка",
            "ста", "стa", "call to action", "призыв", "призыв к действию", "варианты кнопок", "текст кнопки",
            "продающий", "маркетинг", "структура", "контент",
            "идея", "идеи", "поштурмить", "брейншторм", "текст"
        ],
        "files": [
            "knowledge/marketing/landing_basics.txt",
            "knowledge/marketing/headline_ideas.txt",
            "knowledge/marketing/content_structure.txt",
            "knowledge/marketing/offer_basics.txt",
            "knowledge/marketing/cta_examples.txt"
        ]
    }
}


def load_file(filepath):
    if not os.path.exists(filepath):
        return ""

    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def select_knowledge(user_text):
    user_text = user_text.lower()
    selected_files = []

    for topic_data in KNOWLEDGE_TOPICS.values():
        for keyword in topic_data["keywords"]:
            if keyword in user_text:
                selected_files.extend(topic_data["files"])
                break

    selected_files = list(dict.fromkeys(selected_files))

    if not selected_files:
        selected_files = [
            "knowledge/overwhelm.txt",
            "knowledge/task_start.txt",
            "knowledge/focus_tips.txt"
        ]

    knowledge_text = ""

    for filepath in selected_files:
        content = load_file(filepath)
        if content:
            knowledge_text += f"\n\n--- {filepath} ---\n"
            knowledge_text += content

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


@bot.message_handler(commands=['start'])
def start(message):
    current_mode = get_user_mode(message.chat.id)
    current_mode_name = MODE_NAMES.get(current_mode, "☀️ Нежный")

    bot.send_message(
        message.chat.id,
        f"Бомжур ☀️\nЯ Солнечный Ген.\nТвой текущий режим: {current_mode_name}\n\nВыбери режим поддержки кнопкой или просто напиши, что происходит.",
        reply_markup=make_modes_keyboard()
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Я умею:\n/checkin — мягкий чек-ин\n/potato — режим картошки\n/panic — если накрыло\n/task — разложить задачу\n/meme — офисный мем\n/modes — выбрать режим кнопкой\n\nЕщё могу помогать с Битрикс24, задачами, лендингами, заголовками и офисной дедлайновой лавой."
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
        "Как ты сейчас? ☀️\n1 — лежу как омеба\n2 — картошка, но живая\n3 — могу чуть-чуть арбайтен"
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
        "Так. Дышим ☀️\nКартофельный режим включён автоматически и сохранён.\nСейчас не спасаем весь офис. Назови одну микрозадачу. Одну."
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
        relevant_knowledge = select_knowledge(message.text)

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            max_tokens=260,
            temperature=0.9,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT + "\n\nТекущий режим поддержки:\n" + mode_prompt + "\n\nРелевантная база знаний:\n" + relevant_knowledge
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
