import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('6999754629:AAHJmqrqQ2NhlF5hAz54o-nv6ZEUtn_MhrE')

# Создание таблиц, если они не существуют
def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS date_responses
                   (user_id TEXT PRIMARY KEY, message TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS status_responses
                   (user_id TEXT PRIMARY KEY, message TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_states
                   (user_id TEXT PRIMARY KEY, state TEXT)''')
    conn.close()

create_tables()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Дата')
    itembtn2 = types.KeyboardButton('Статус')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, "Выберите фильтр:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if message.text == 'Дата':
        response = 'Введите дату:'
        bot.reply_to(message, response)
        cursor.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (message.chat.id, 'Дата'))
    elif message.text == 'Статус':
        response = 'Введите статус:'
        bot.reply_to(message, response)
        cursor.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (message.chat.id, 'Статус'))
    else:
        cursor.execute("SELECT state FROM user_states WHERE user_id = ?", (message.chat.id,))
        filter_type = cursor.fetchone()
        if filter_type is not None:
            if filter_type[0] == 'Дата':
                # Сохранение ответа в базу данных
                cursor.execute("INSERT OR REPLACE INTO date_responses (user_id, message) VALUES (?, ?)", (message.chat.id, message.text))
                bot.reply_to(message, 'Ваша дата была успешно добавлена в базу данных.')
            elif filter_type[0] == 'Статус':
                # Сохранение ответа в базу данных
                cursor.execute("INSERT OR REPLACE INTO status_responses (user_id, message) VALUES (?, ?)", (message.chat.id, message.text))
                bot.reply_to(message, 'Ваш статус был успешно добавлен в базу данных.')
            cursor.execute("DELETE FROM user_states WHERE user_id = ?", (message.chat.id,))

    conn.commit()
    conn.close()

bot.polling()
