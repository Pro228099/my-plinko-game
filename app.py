import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Замени на свой токен от @BotFather и ссылку на GitHub Pages
BOT_TOKEN = "ТВОЙ_ТОКЕН_ОТ_BOTFATHER"
WEB_APP_URL = "https://твой-логин.github.io/my-plinko-game/"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    
    # Кнопка для открытия WebApp с игрой
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
    
