import os
import sys
import json
import subprocess
import telebot
from telebot.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    WebAppInfo
)
from dotenv import load_dotenv

# --- Блок авто-обновления перед запуском бота ---
def update_code():
    if "--updated" not in sys.argv:
        try:
            print("--> Скачиваем свежий код из GitHub...")
            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
            print(result.stdout)
            
            print("--> Перезапускаем бота с новым кодом...")
            os.execv(sys.executable, [sys.executable] + sys.argv + ["--updated"])
        except Exception as e:
            print(f"--> Ошибка при авто-обновлении: {e}")

update_code()
# -----------------------------------------------

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot = telebot.TeleBot(BOT_TOKEN)

# --- КОМАНДА /start И /help ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # 1. Инлайн-кнопка в сообщении
    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(
        InlineKeyboardButton(
            text="Играть в Plinko 🎲", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )
    
    # 2. Кнопка в обычной клавиатуре (нужна, чтобы работал tg.sendData для отзывов)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(
        KeyboardButton(
            text="🎮 Открыть Plinko", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )
    
    bot.reply_to(
        message, 
        "Привет! Нажми на кнопку ниже, чтобы запустить игру прямо в Telegram:", 
        reply_markup=inline_markup
    )
    
    # Дополнительно выводим кнопку внизу экрана
    bot.send_message(
        message.chat.id,
        "Также кнопка быстрого запуска доступна на вашей клавиатуре 👇",
        reply_markup=reply_markup
    )

# --- ОБРАБОТКА ДАННЫХ ИЗ WEBAPP (Идея / Баг) ---
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)

        if data.get("type") == "feedback":
            user = message.from_user
            username = f"@{user.username}" if user.username else user.first_name
            feedback_text = data.get("text", "")

            report_message = (
                f"📩 *Новый отзыв/баг из Plinko!*\n\n"
                f"👤 *От кого:* {username} (ID: `{user.id}`)\n"
                f"💬 *Сообщение:*\n{feedback_text}"
            )

            if ADMIN_CHAT_ID:
                bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=report_message,
                    parse_mode="Markdown"
                )

            bot.reply_to(message, "Спасибо! Твой отзыв успешно отправлен разработчику. 🔥")

    except Exception as e:
        print(f"Ошибка при обработке WebApp Data: {e}")

if __name__ == '__main__':
    print("Бот успешно запущен!")
    bot.infinity_polling()
    
