import os
import sys
import subprocess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv

# --- Блок авто-обновления перед запуском бота ---
def update_code():
    # Проверяем флаг, чтобы не уйти в бесконечный цикл перезапуска
    if "--updated" not in sys.argv:
        try:
            print("--> Скачиваем свежий код из GitHub...")
            # Выполняем git pull
            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
            print(result.stdout)
            
            print("--> Перезапускаем бота с новым кодом...")
            # Перезапускаем текущий скрипт с флагом --updated
            os.execv(sys.executable, [sys.executable] + sys.argv + ["--updated"])
        except Exception as e:
            print(f"--> Ошибка при авто-обновлении: {e}")

update_code()
# -----------------------------------------------

# Загружаем переменные из файла .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")

bot = telebot.TeleBot(BOT_TOKEN)

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

if __name__ == '__main__':
    print("Бот успешно запущен!")
    bot.infinity_polling()
    
