import os
import sys
import json
import subprocess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
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

# Загружаем переменные из файла .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot = telebot.TeleBot(BOT_TOKEN)

# --- КОМАНДА /start И /help ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    
    play_button = InlineKeyboardButton(
        text="Играть в Plinko 🎲", 
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    markup.add(play_button)
    
    bot.reply_to(
        message, 
        "Привет! Нажми на кнопку ниже, чтобы запустить игру прямо в Telegram:", 
        reply_markup=markup
    )

# --- ОБРАБОТКА ДАННЫХ ИЗ WEBAPP (Идея / Баг) ---
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        # Парсим JSON, переданный из index.html
        data = json.loads(message.web_app_data.data)

        if data.get("type") == "feedback":
            user = message.from_user
            username = f"@{user.username}" if user.username else user.first_name
            feedback_text = data.get("text", "")

            # Формируем сообщение для администратора
            report_message = (
                f"📩 *Новый отзыв/баг из Plinko!*\n\n"
                f"👤 *От кого:* {username} (ID: `{user.id}`)\n"
                f"💬 *Сообщение:*\n{feedback_text}"
            )

            # Отправляем сообщение администратору
            if ADMIN_CHAT_ID:
                bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=report_message,
                    parse_mode="Markdown"
                )

            # Подтверждение пользователю
            bot.reply_to(message, "Спасибо! Твой отзыв успешно отправлен разработчику. 🔥")

    except Exception as e:
        print(f"Ошибка при обработке WebApp Data: {e}")

if __name__ == '__main__':
    print("Бот успешно запущен!")
    bot.infinity_polling()
        
