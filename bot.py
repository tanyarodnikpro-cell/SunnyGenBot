import telebot
import os
import random
import time

from telebot import types
from openai import OpenAI

TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Эти данные существуют только в оперативной памяти процесса.
# После перезапуска они исчезают и никогда не записываются на диск.
USER_MODES = {}
CONSENTED_USERS = set()
PENDING_TASK_USERS = set()

PRIVACY_NOTICE = """
🔐 Приватность Солнечного Гена

Ген не сохраняет на диск:
— Telegram ID, имя или username;
— историю переписки;
— выбранный режим общения;
— содержимое сообщений.

Режим и факт согласия существуют только в оперативной памяти и исчезают после перезапуска.

Чтобы получить AI-ответ, текст твоего сообщения передаётся сервису OpenAI. В передаче и обработке также участвуют Telegram и серверная инфраструктура. Не отправляй пароли, банковские данные, документы, медицинские сведения и рабочие секреты.

Нажимая «Согласен», ты разрешаешь обработать и трансгранично передать текст сообщения исключительно для формирования ответа. Согласие можно отозвать командой /revoke.
""".strip()


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

MODE_RESPONSES = {
    "gentle": [
        "☀️ Так. Без геройства сегодня. Просто живём день аккуратно.",
        "☀️ Потихоньку, спокойно, без самосожжения.",
        "☀️ Давай просто переживём этот день красиво."
    ],
    "mem": [
        "🤡 Психика надела клоунский нос и пошла арбайтен.",
        "🤡 Корпоративная турбулентность штатная.",
        "🤡 Teams издал звук — давление упало."
    ],
    "post": [
        "💀 Духовно уже на даче.",
        "💀 Работаем без иллюзий.",
        "💀 Психика вышла покурить и не вернулась.",
        "💀 Сегодня арбайтен через внутреннее страдание.",
        "💀 Внутри — пепел. Снаружи — созвон.",
        "💀 Корпоративный апокалипсис идёт по расписанию.",
        "💀 Не день, а лепнина из говна и палок.",
        "💀 Состояние: тихо ору в Excel.",
        "💀 Работаем на морально-волевых и кофеине.",
        "💀 Внутренне уже написала заявление.",
        "💀 Teams пиликнул — душа покинула тело.",
        "💀 Мотивация найдена не была.",
        "💀 Дедлайновая лава подошла к горлу.",
        "💀 Иван-дурак на коне-дебиле въехал в рабочий день.",
        "💀 Плавали, знаем, вся жопа в ракушках.",
        "💀 Внутренний ресурс: две макаронины.",
        "💀 Сегодня не живём, а технически существуем.",
        "💀 Рабочее настроение: чай в ладошку и в дорожку."
    ],
    "adhd": [
        "🧠 47 вкладок обнаружено.",
        "🧠 Одну задачу. Одну. Не устраиваем фестиваль хаоса.",
        "🧠 Мозг открыл TikTok внутри головы."
    ],
    "potato": [
        "🥔 Режим картошки активирован.",
        "🥔 Сегодня арбайтен без геройства.",
        "🥔 Психика ушла полежать."
    ]
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

TASK_PROMPT = """
Сейчас включён одноразовый режим подробного разбора задачи.

Разбери задачу практично и без воды:
— сначала сформулируй понятную цель одним предложением;
— затем дай 5–8 конкретных пронумерованных шагов в правильном порядке;
— каждый шаг должен быть небольшим действием, а не расплывчатым советом;
— отдельно укажи «С чего начать прямо сейчас» — одно действие примерно на 5–10 минут;
— отдельно укажи «Что пока можно не делать», чтобы не раздувать хаос;
— учитывай усталость и не требуй героизма.

Если для полезного разбора критически не хватает информации, задай не больше двух коротких уточняющих вопросов и не выдумывай детали.
Ответ может быть развёрнутым, но остаётся живым, ясным и без канцелярита.
""".strip()


def get_user_mode(chat_id):
    chat_id = str(chat_id)
    return USER_MODES.get(chat_id, "gentle")


def set_user_mode(chat_id, mode_key):
    chat_id = str(chat_id)
    USER_MODES[chat_id] = mode_key


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


def make_consent_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(
            "✅ Согласен",
            callback_data="privacy_accept"
        ),
        types.InlineKeyboardButton(
            "❌ Не согласен",
            callback_data="privacy_decline"
        )
    )
    return keyboard


def has_ai_consent(chat_id):
    return str(chat_id) in CONSENTED_USERS


def request_ai_consent(chat_id):
    bot.send_message(
        chat_id,
        PRIVACY_NOTICE,
        reply_markup=make_consent_keyboard()
    )


def ask_openai_with_retry(messages, max_tokens=260):
    for attempt in range(2):
        try:
            return client.chat.completions.create(
                model="gpt-4.1-mini",
                max_tokens=max_tokens,
                temperature=1.0,
                messages=messages
            )
        except Exception as e:
            print(f"Попытка {attempt + 1} не удалась: {e}")
            time.sleep(2)

    return None


@bot.message_handler(commands=['start'])
def start(message):
    current_mode = get_user_mode(message.chat.id)
    current_mode_name = MODE_NAMES.get(current_mode, "☀️ Нежный")

    bot.send_message(
        message.chat.id,
        f"Бомжур ☀️\nЯ Солнечный Ген.\n\nТвой режим: {current_mode_name}\n\nЯ не храню твою переписку и не подписываю тебя на рассылки.",
        reply_markup=make_modes_keyboard()
    )
    request_ai_consent(message.chat.id)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Я умею:\n/modes — выбрать режим\n/potato — режим картошки\n/panic — если накрыло\n/task — подробно разложить следующую задачу\n/meme — офисный мем\n/privacy — как обрабатываются сообщения\n/revoke — отозвать согласие на AI"
    )


@bot.message_handler(commands=['privacy'])
def privacy(message):
    request_ai_consent(message.chat.id)


@bot.message_handler(commands=['revoke'])
def revoke_consent(message):
    chat_id = str(message.chat.id)
    CONSENTED_USERS.discard(chat_id)
    USER_MODES.pop(chat_id, None)
    PENDING_TASK_USERS.discard(chat_id)
    bot.send_message(
        message.chat.id,
        "Согласие отозвано. Временный режим удалён из памяти. AI-ответы отключены до нового согласия через /privacy."
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


@bot.callback_query_handler(func=lambda call: call.data.startswith("privacy_"))
def privacy_callback(call):
    chat_id = str(call.message.chat.id)

    if call.data == "privacy_accept":
        CONSENTED_USERS.add(chat_id)
        bot.answer_callback_query(call.id, "Согласие принято")
        bot.send_message(
            call.message.chat.id,
            "Готово. Согласие хранится только в памяти до перезапуска. Можно писать ☀️"
        )
        return

    CONSENTED_USERS.discard(chat_id)
    USER_MODES.pop(chat_id, None)
    PENDING_TASK_USERS.discard(chat_id)
    bot.answer_callback_query(call.id, "AI-обработка отключена")
    bot.send_message(
        call.message.chat.id,
        "Понял. Текст в OpenAI не отправляю. Локальные команды вроде /meme продолжат работать."
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("mode_"))
def mode_callback(call):
    chat_id = str(call.message.chat.id)
    mode_key = call.data.replace("mode_", "")
    set_user_mode(call.message.chat.id, mode_key)
    PENDING_TASK_USERS.discard(chat_id)

    responses = MODE_RESPONSES.get(mode_key, ["☀️ Режим обновлён."])
    random_response = random.choice(responses)

    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, random_response)


@bot.message_handler(commands=['potato'])
def potato(message):
    PENDING_TASK_USERS.discard(str(message.chat.id))
    set_user_mode(message.chat.id, "potato")
    response = random.choice(MODE_RESPONSES["potato"])

    bot.send_message(
        message.chat.id,
        response
    )


@bot.message_handler(commands=['panic'])
def panic(message):
    PENDING_TASK_USERS.discard(str(message.chat.id))
    set_user_mode(message.chat.id, "potato")
    bot.send_message(
        message.chat.id,
        "Так. Дышим ☀️\nКартофельный режим включён.\nСейчас не спасаем весь офис. Назови одну микрозадачу. Одну."
    )


@bot.message_handler(commands=['task'])
def task(message):
    PENDING_TASK_USERS.add(str(message.chat.id))
    bot.send_message(
        message.chat.id,
        "Кидай задачу одним сообщением. Я подробно разложу её на понятные шаги, выберу первый микрошажочек и отрежу лишнее 🥔"
    )


@bot.message_handler(commands=['meme'])
def meme(message):
    memes = [
        "Я: сейчас быстренько сделаю задачу.\nЗадача: добро пожаловать в дедлайновую лаву ☕️",
        "Когда открыл Битрикс и Битрикс открыл тебя.",
        "Мой карьерный план: не сдохнуть.",
        "Я не прокрастинирую. Я жду пока паника включит турборежим.",
        "Сегодня мой максимум — не расплакаться в Excel."
    ]

    bot.send_message(
        message.chat.id,
        random.choice(memes)
    )


@bot.message_handler(
    content_types=[
        'photo',
        'voice',
        'audio',
        'video',
        'document',
        'sticker',
        'animation',
        'video_note',
        'location',
        'contact'
    ]
)
def unsupported_content(message):
    bot.send_message(
        message.chat.id,
        "Я пока работаю только с текстом. Опиши словами — так надёжнее и без лишней передачи файлов ☀️"
    )


@bot.message_handler(func=lambda message: True, content_types=['text'])
def chat(message):
    if not has_ai_consent(message.chat.id):
        bot.send_message(
            message.chat.id,
            "Перед AI-ответом мне нужно твоё согласие на обработку текста."
        )
        request_ai_consent(message.chat.id)
        return

    chat_id = str(message.chat.id)
    task_requested = chat_id in PENDING_TASK_USERS
    mode_key = get_user_mode(message.chat.id)
    mode_prompt = MODES.get(mode_key, MODES["gentle"])

    if task_requested:
        active_prompt = SYSTEM_PROMPT + "\n\n" + TASK_PROMPT
        max_tokens = 800
    else:
        active_prompt = SYSTEM_PROMPT + "\n\nТекущий режим:\n" + mode_prompt
        max_tokens = 260

    messages = [
        {
            "role": "system",
            "content": active_prompt
        },
        {
            "role": "user",
            "content": message.text
        }
    ]

    response = ask_openai_with_retry(messages, max_tokens=max_tokens)

    if response is None:
        bot.send_message(
            message.chat.id,
            "Связь чихнула, дорогуля ☀️\nПовтори сообщение ещё раз — я уже поправил плед и делаю вид, что не было корпоративной турбулентности."
        )
        return

    answer = response.choices[0].message.content
    bot.send_message(message.chat.id, answer)

    if task_requested:
        PENDING_TASK_USERS.discard(chat_id)


print("Ген проснулся ☀️")

bot.infinity_polling()
