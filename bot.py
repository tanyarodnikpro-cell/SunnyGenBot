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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Эти данные существуют только в оперативной памяти процесса.
# После перезапуска они исчезают и никогда не записываются на диск.
CONSENTED_USERS = set()
PENDING_TASK_USERS = set()

PRIVACY_NOTICE = """
🔐 Приватность Солнечного Гена

Ген не сохраняет на диск:
— Telegram ID, имя или username;
— историю переписки;
— содержимое сообщений.

Согласие и временные технические состояния существуют только в оперативной памяти и исчезают после перезапуска.

Чтобы получить AI-ответ, текст твоего сообщения передаётся сервису OpenAI. В передаче и обработке также участвуют Telegram и серверная инфраструктура. Не отправляй пароли, банковские данные, документы, медицинские сведения и рабочие секреты.

Нажимая «Согласен», ты разрешаешь обработать и трансгранично передать текст сообщения исключительно для формирования ответа. Согласие можно отозвать командой /revoke.
""".strip()

POTATO_RESPONSES = [
    "🥔 Режим картошки активирован. Сегодня без геройства.",
    "🥔 Сегодня арбайтен бережно. Одно маленькое дело — уже достаточно.",
    "🥔 Психика ушла полежать. Имеет право."
]

MEMES = [
    {
        "path": os.path.join("memes", "dogs", "dog_01.jpg"),
        "caption": "Когда на созвоне спросили: «Ну что там по срокам?»\nА ты там по выживанию."
    },
    {
        "path": os.path.join("memes", "dogs", "dog_02.jpg"),
        "caption": "Понедельник. 09:07.\nЯ уже качественно устал."
    },
    {
        "path": os.path.join("memes", "dogs", "dog_03.jpg"),
        "caption": "Когда коллега пишет: «Есть маленькая правочка».\nМаленькая, сука, правочка."
    },
    {
        "path": os.path.join("memes", "dogs", "dog_04.jpg"),
        "caption": "Алло, техподдержка?\nЯ нажал «ответить всем» и теперь хочу исчезнуть."
    },
    {
        "path": os.path.join("memes", "dogs", "dog_05.jpg"),
        "caption": "Когда сказали: «Давайте без лишних созвонов»\nи назначили созвон обсудить созвоны."
    },
    {
        "path": os.path.join("memes", "dogs", "dog_06.jpg"),
        "caption": "Задачу сделал.\nТЗ не читал. Риски люблю."
    },
    {
        "path": os.path.join("memes", "dogs", "dog_07.jpg"),
        "caption": "Я на испытательном сроке:\nделаю вид, что понимаю корпоративную культуру."
    },
    {
        "path": os.path.join("memes", "dogs", "dog_08.jpg"),
        "caption": "Открыл одну задачу.\nОна открыла ещё семнадцать."
    },
    {
        "path": os.path.join("memes", "dogs", "dog_09.jpg"),
        "caption": "ЭТО МОГЛО БЫТЬ ПИСЬМОМ!\nСпасибо, я закончил."
    },
    {
        "path": os.path.join("memes", "cats", "cat_01.jpg"),
        "caption": "Когда дедлайн был вчера,\nа согласование пришло сегодня."
    },
    {
        "path": os.path.join("memes", "cats", "cat_02.jpg"),
        "caption": "Я посмотрел ваш отчёт.\nЭто говно надо переписать."
    },
    {
        "path": os.path.join("memes", "cats", "cat_03.jpg"),
        "caption": "Я: спокойно проверю почту.\nПочта: СРОЧНО!!!"
    },
    {
        "path": os.path.join("memes", "cats", "cat_04.jpg"),
        "caption": "Когда случайно включила камеру\nдо того, как включила лицо."
    },
    {
        "path": os.path.join("memes", "cats", "cat_05.jpg"),
        "caption": "Сегодня я отвечаю за стратегию.\nСтратегия: не отсвечивать."
    },
    {
        "path": os.path.join("memes", "cats", "cat_06.jpg"),
        "caption": "Коллеги, мы всё уронили.\nНо есть нюанс: оно и так еле стояло."
    },
    {
        "path": os.path.join("memes", "cats", "cat_07.jpg"),
        "caption": "Третья чашка кофе.\nТеперь я тревожусь продуктивно."
    },
    {
        "path": os.path.join("memes", "cats", "cat_08.jpg"),
        "caption": "Новый опенспейс.\nЛоток — в конце коридора, выгорание — по расписанию."
    },
    {
        "path": os.path.join("memes", "cats", "cat_09.jpg"),
        "caption": "Я изучил архитектуру.\nПепелац держится на скотче и вере."
    }
]


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


def make_panic_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(
            "🫁 Накрыло тревогой",
            callback_data="panic_grounding"
        ),
        types.InlineKeyboardButton(
            "🔥 Горит работа",
            callback_data="panic_work"
        ),
        types.InlineKeyboardButton(
            "🥔 Просто побудь рядом",
            callback_data="panic_stay"
        ),
        types.InlineKeyboardButton(
            "🆘 Нужна срочная помощь",
            callback_data="panic_urgent"
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
    bot.send_message(
        message.chat.id,
        "Бомжур ☀️\nЯ Солнечный Ген.\n\nЯ не храню твою переписку и не подписываю тебя на рассылки. Команды и возможности покажу по /help."
    )
    request_ai_consent(message.chat.id)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Я умею:\n/potato — бережно пережить день\n/panic — если накрыло\n/task — подробно разложить следующую задачу\n/meme — офисный мем\n/privacy — как обрабатываются сообщения\n/revoke — отозвать согласие на AI"
    )


@bot.message_handler(commands=['privacy'])
def privacy(message):
    request_ai_consent(message.chat.id)


@bot.message_handler(commands=['revoke'])
def revoke_consent(message):
    chat_id = str(message.chat.id)
    CONSENTED_USERS.discard(chat_id)
    PENDING_TASK_USERS.discard(chat_id)
    bot.send_message(
        message.chat.id,
        "Согласие отозвано. AI-ответы отключены до нового согласия через /privacy."
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
    PENDING_TASK_USERS.discard(chat_id)
    bot.answer_callback_query(call.id, "AI-обработка отключена")
    bot.send_message(
        call.message.chat.id,
        "Понял. Текст в OpenAI не отправляю. Локальные команды вроде /meme и /panic продолжат работать."
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("panic_"))
def panic_callback(call):
    chat_id = str(call.message.chat.id)
    bot.answer_callback_query(call.id)

    if call.data == "panic_grounding":
        bot.send_message(
            call.message.chat.id,
            "Так, возвращаем мозг из дедлайновой лавы в комнату. Без спешки назови:\n\n"
            "5 вещей, которые видишь;\n"
            "4 ощущения в теле — например, стопы в носках или спину на стуле;\n"
            "3 звука, которые слышишь;\n"
            "2 запаха;\n"
            "1 вкус.\n\n"
            "Если тебе комфортно, сделай три спокойных выдоха чуть длиннее вдоха. Не надо выполнять идеально — мы не сдаём экзамен по существованию."
        )
        return

    if call.data == "panic_work":
        PENDING_TASK_USERS.add(chat_id)
        bot.send_message(
            call.message.chat.id,
            "Хорошо. Не спасаем весь офис — тушим один стул. Напиши одним сообщением, что именно горит. Я разложу это на шаги и выберу первый микрошажочек."
        )
        return

    if call.data == "panic_stay":
        PENDING_TASK_USERS.discard(chat_id)
        bot.send_message(
            call.message.chat.id,
            "Я рядом. Сейчас ничего не чиним и не требуем от тебя красивого объяснения. Напиши хоть одно слово: «страшно», «злюсь», «устала» или своё. Дальше разберёмся без геройства 🥔"
        )
        return

    PENDING_TASK_USERS.discard(chat_id)
    bot.send_message(
        call.message.chat.id,
        "Если есть реальная угроза жизни или здоровью — не оставайся только с ботом. Позови человека рядом и позвони в экстренную службу.\n\n"
        "В Казахстане: 112 — единая экстренная служба, 103 — скорая помощь. В другой стране используй местный экстренный номер. Сообщи, что случилось и где ты находишься."
    )


@bot.message_handler(commands=['potato'])
def potato(message):
    PENDING_TASK_USERS.discard(str(message.chat.id))
    bot.send_message(
        message.chat.id,
        random.choice(POTATO_RESPONSES)
    )


@bot.message_handler(commands=['panic'])
def panic(message):
    PENDING_TASK_USERS.discard(str(message.chat.id))
    bot.send_message(
        message.chat.id,
        "Так. Я рядом. Сейчас не решаем всю жизнь и не спасаем офис.\n\n"
        "Упрись стопами в пол или кровать. Найди глазами три предмета вокруг. Если комфортно — спокойно выдохни. Можно сделать глоток воды.\n\n"
        "Теперь выбери, что ближе:",
        reply_markup=make_panic_keyboard()
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
    selected_meme = random.choice(MEMES)
    photo_path = os.path.join(BASE_DIR, selected_meme["path"])

    try:
        with open(photo_path, "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=selected_meme["caption"]
            )
    except OSError as e:
        print(f"Не удалось открыть мем {photo_path}: {e}")
        bot.send_message(
            message.chat.id,
            selected_meme["caption"]
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

    if task_requested:
        active_prompt = SYSTEM_PROMPT + "\n\n" + TASK_PROMPT
        max_tokens = 800
    else:
        active_prompt = SYSTEM_PROMPT
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
