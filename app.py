import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv

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
    
