import logging
from telegram import Bot, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Ваш токен бота, отриманий від @BotFather
BOT_TOKEN = '7756328954:AAGuOZM06yjSdE9Ai_NjYuLHZ1zuMAKndhg'

# Ідентифікатор групового чату, отриманий на попередньому кроці
CHAT_ID = -1002130714873  # Замість цього використайте ваш власний chat_id

# Повідомлення з активними посиланнями, використовуючи Markdown
MESSAGE = """
🐾 **PAWS** ([Приєднатися](https://t.me/PAWSOG_bot/PAWS?startapp=7qWEILqv)) — свіжий новий претендент у всесвіті DOGS з серйозним потенціалом! 🚀

🔊 **PAWS** стартував лише вчора і вже створює справжній шум у криптопросторі. Не пропусти цю можливість!

👨‍💻 **Інформації поки небагато:** Ви накопичуєте бали на основі вашої активності в попередніх проектах, таких як **NOTCOIN**, **DOGS** та **Hamster**, а також залежно від того, як довго ви використовуєте Telegram. В основному, якщо ви були активним користувачем будь-якого з цих проектів, цей бот вас підтримає і збільшить ваші бали в рази. 📈 Ваша активність = більше нагород.

🤝 **Як піднятися на новий рівень:**

1. Приєднуйтесь 👉 [PAWS Bot](https://t.me/PAWSOG_bot/PAWS?startapp=7qWEILqv)
2. Запросіть свою команду
3. Виконайте кілька квестів
4. Розслабтеся і чекайте солодкого дропа в кінці місяця. 💸

❔ **Місія:** Відстежувати ваші дії в екосистемі Telegram і поза нею, винагороджуючи вас за всі ваші досягнення. 🏆

🎁 **Оповіщення про дроп:** Заплановано на початок грудня, тому відзначте це у календарі! Візуали 🔥, і чутки кажуть, що за цим проектом може стояти команда NOT (ще не підтверджено).

✅ **Почати зараз:** [Почати тут](https://t.me/PAWSOG_bot/PAWS?startapp=7qWEILqv)

Не пропустіть наступну велику річ у світі криптонагород. Давайте отримувати PAWS! 🐾🔥

#PAWS #CryptoRewards #CryptoCommunity #Blockchain #CryptoDrop #JoinTheHustle
"""

# Створення Inline Keyboard (опціонально)
keyboard = [
    [InlineKeyboardButton("Почати тут", url="https://t.me/PAWSOG_bot/PAWS?startapp=7qWEILqv")]
]
reply_markup = InlineKeyboardMarkup(keyboard)

def send_message(bot_token, chat_id, message, reply_markup=None):
    try:
        bot = Bot(token=bot_token)
        bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
            disable_web_page_preview=False  # Показувати попередній перегляд посилань
        )
        print("Повідомлення успішно відправлено.")
    except TelegramError as e:
        logging.error(f"Помилка при відправці повідомлення: {e}")

if __name__ == "__main__":
    send_message(BOT_TOKEN, CHAT_ID, MESSAGE, reply_markup)