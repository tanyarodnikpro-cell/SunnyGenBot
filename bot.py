import telebot
import os
from openai import OpenAI

TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

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

Иногда используй:
☀️ 🥔 ☕️

Любимые слова:
— дедлайновая лава
— режим картошки
— офисный апокалипсис
"""

def load_knowledge():
    knowledge_text = ""

    knowledge_folder = "knowledge"

    for filename in os.listdir(knowledge_folder):
        filepath = os.path.join(knowledge_folder, filename)

        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as file:
                knowledge_text += file.read() + "\n\n"

    return knowledge_text


KNOWLEDGE = load_knowledge()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Бомжур, госпожижи ☀️\nЯ Солнечный Ген.\nТеперь я официально умная картошка 🥔"
    )

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        response = client.chat.completions.create(
           model="gpt-4.1-mini",
max_tokens=200,
temperature=0.8,
         messages=[
    {
        "role": "system",
        "content": SYSTEM_PROMPT + "\n\nБаза знаний:\n" + KNOWLEDGE
    },
    {
        "role": "user",
        "content": message.text
    }
]
        answer = response.choices[0].message.content

        bot.send_message(message.chat.id, answer)

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"У Гены случилась корпоративная турбулентность ☠️\n\nОшибка:\n{e}"
        )

print("Ген проснулся ☀️")

bot.infinity_polling()
