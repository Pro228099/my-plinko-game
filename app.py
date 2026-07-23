
import os
import sys
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
    
    # 1. Кнопка игры
    inline_markup.add(
        InlineKeyboardButton(
            text="Играть в Plinko 🎲", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )
    
    # 2. Кнопка отзыва
    inline_markup.add(
        InlineKeyboardButton(
            text="💡 Идея / Сообщить о баге", 
            callback_data="start_feedback"
        )
    )
    
    bot.reply_to(
        message, 
        "Привет! Нажми на кнопку ниже, чтобы запустить игру или высказать свою идею:", 
        reply_markup=inline_markup
    )

# --- НАЖАТИЕ НА ИНЛАЙН-КНОПКУ ОТЗЫВА ---
@bot.callback_query_handler(func=lambda call: call.data == "start_feedback")
def callback_feedback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id, 
        "✍️ **Напиши свою идею или описание бага одним сообщением:**\n\n"
        "(Или отправь /cancel для отмены)",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_feedback_step)

# --- КОМАНДА /feedback ИЛИ /bug ИЗ ТЕКСТА ---
@bot.message_handler(commands=['feedback', 'bug'])
def start_feedback_cmd(message):
    msg = bot.reply_to(
        message, 
        "✍️ **Напиши свою идею или описание бага одним сообщением:**\n\n"
        "(Или отправь /cancel для отмены)",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_feedback_step)

# --- ОБРАБОТКА И ОТПРАВКА ТЕКСТА ОТЗЫВА ---
def process_feedback_step(message):
    if message.text and message.text.strip() == '/cancel':
        bot.reply_to(message, "Отправка отзыва отменена.")
        return

    if not message.text:
        bot.reply_to(message, "Пожалуйста, отправь именно текст. Попробуй снова через кнопку или команду /feedback")
        return

    user_text = message.text.strip()
    user = message.from_user
    
    user_info = f"@{user.username}" if user.username else f"{user.first_name} (ID: <code>{user.id}</code>)"
    
    msg_for_admin = (
        f"💡 <b>Новый отзыв / идея!</b>\n\n"
        f"<b>От:</b> {user_info}\n"
        f"<b>Текст:</b>\n{user_text}"
    )

    if ADMIN_CHAT_ID:
        try:
            bot.send_message(ADMIN_CHAT_ID, msg_for_admin, parse_mode='HTML')
            bot.reply_to(message, "Спасибо! Твой отзыв успешно передан разработчику. 👍")
        except Exception as e:
            print(f"Ошибка при отправке админу: {e}")
            bot.reply_to(message, "Произошла ошибка при отправке. Попробуй позже.")
    else:
        print("ОШИБКА: ADMIN_CHAT_ID не настроен в .env!")
        bot.reply_to(message, "Ошибка настройки сервера.")

if __name__ == '__main__':
    print("Бот успешно запущен!")
    bot.infinity_polling()
