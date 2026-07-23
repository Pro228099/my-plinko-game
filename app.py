import os
import sys
import json
import subprocess
import telebot
from telebot.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    WebAppInfo
)
from dotenv import load_dotenv

# --- Блок авто-обновления перед запуском бота ---
def update_code():
    if "--updated" not in sys.argv:
        try:
            print("--> Скачиваем свежий код из GitHub...")
            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("Git Warning/Error:", result.stderr)
            
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

if not BOT_TOKEN:
    print("CRITICAL ERROR: BOT_TOKEN не задан в переменной окружения / .env")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# --- КОМАНДА /start И /help ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(
        InlineKeyboardButton(
            text="Играть в Plinko 🎲", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )
    
    bot.reply_to(
        message, 
        "Привет! Нажми на кнопку ниже, чтобы запустить игру прямо в Telegram:", 
        reply_markup=inline_markup
    )

# --- ОБРАБОТКА ДАННЫХ ИЗ WEB APP (ОТЗЫВЫ И ИДЕИ) ---
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        # Распаковываем данные от клиента
        payload = json.loads(message.web_app_data.data)
        
        if payload.get('action') == 'feedback':
            user_text = payload.get('text', '')
            user = message.from_user
            
            # Формируем красивое имя пользователя
            user_info = f"@{user.username}" if user.username else f"{user.first_name} (ID: {user.id})"
            
            msg = f"💡 <b>Новый отзыв / идея!</b>\n\n<b>От:</b> {user_info}\n<b>Текст:</b> {user_text}"
            
            # Пересылаем отзыв админу
            if ADMIN_CHAT_ID:
                bot.send_message(ADMIN_CHAT_ID, msg, parse_mode='HTML')
                bot.reply_to(message, "Спасибо! Ваш отзыв успешно отправлен разработчику. 👍")
            else:
                print("ОШИБКА: ADMIN_CHAT_ID не настроен в .env!")
                
    except Exception as e:
        print(f"Ошибка обработки WebApp Data: {e}")

if __name__ == '__main__':
    print("Бот успешно запущен!")
    bot.infinity_polling()
    
