import os
import sys
import json
import html
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
    # Единственная инлайн-кнопка под сообщением
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

# --- ОБРАБОТКА ДАННЫХ ИЗ WEBAPP ---
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)

        if data.get("type") == "feedback":
            user = message.from_user
            username = f"@{user.username}" if user.username else user.first_name
            feedback_raw = data.get("text", "")
            
            # Экранируем спецсимволы для безопасной отправки HTML
            safe_username = html.escape(username)
            safe_text = html.escape(feedback_raw)

            report_message = (
                f"<b>📩 Новый отзыв/баг из Plinko!</b>\n\n"
                f"<b>👤 От кого:</b> {safe_username} (ID: <code>{user.id}</code>)\n"
                f"<b>💬 Сообщение:</b>\n{safe_text}"
            )

            if ADMIN_CHAT_ID:
                try:
                    bot.send_message(
                        chat_id=int(ADMIN_CHAT_ID),
                        text=report_message,
                        parse_mode="HTML"
                    )
                except Exception as send_err:
                    print(f"Ошибка при отправке сообщения админу: {send_err}")

            bot.reply_to(message, "Спасибо! Твой отзыв успешно отправлен разработчику. 🔥")

    except Exception as e:
        print(f"Ошибка при обработке WebApp Data: {e}")

if __name__ == '__main__':
    print("Бот успешно запущен!")
    bot.infinity_polling()
    
