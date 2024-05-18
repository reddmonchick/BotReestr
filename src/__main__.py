import telebot
from telebot import types
import sqlite3

from src.dto import FiltersParser
from src.parsing import Nopriz, Novstroy

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
    cursor.execute('''CREATE TABLE IF NOT EXISTS date_joined
                   (user_id TEXT PRIMARY KEY, message TEXT)''')
    conn.close()

create_tables()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Дата')
    itembtn2 = types.KeyboardButton('Статус')
    itembtn3 = types.KeyboardButton('Исключены или вступили за эти даты в сро')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Выберите фильтр:", reply_markup=markup)

@bot.message_handler(commands=['run'])
def run_pars(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    id_user = message.chat.id


    cursor.execute("SELECT user_id, message FROM date_responses WHERE user_id = ?", (id_user,))
    result_data = cursor.fetchone()
    cursor.execute("SELECT user_id, message FROM status_responses WHERE user_id = ?", (id_user,))
    fetchone = cursor.fetchone()
    result_status = True if fetchone[-1] == 'Является' else False if fetchone[-1] == 'Исключен' else True

    cursor.execute("SELECT user_id, message FROM date_joined WHERE user_id = ?", (id_user,))
    fetchone = cursor.fetchone()
    date_join = True if fetchone[-1] == 'Вступили' else False if fetchone[-1] == 'Исключены' else True

    filters_data = FiltersParser(data_start=result_data[1].split('-')[0].strip(), data_end=result_data[1].split('-')[-1].strip(), date_join=date_join,
                                 status=result_status, user_id=id_user)




    nopriz = Nopriz(filters_data)
    novstroy = Novstroy(filters_data)

    nopriz.parse()


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if message.text == 'Дата':
        response = 'Введите дату:'
        bot.reply_to(message, response)
        cursor.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (message.chat.id, 'Дата'))
    elif message.text == 'Статус':
        response = 'Введите статус(Является/Исключен):'
        bot.reply_to(message, response)
        cursor.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (message.chat.id, 'Статус'))
    elif message.text == 'Исключены или вступили за эти даты в сро':
        response = 'Введите исключены или вступили за эти даты в сро(Исключены/Вступили):'
        bot.reply_to(message, response)
        cursor.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (message.chat.id, 'Вступили или исключены даты'))
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
            elif filter_type[0] == 'Вступили или исключены даты':
                cursor.execute("INSERT OR REPLACE INTO date_joined (user_id, message) VALUES (?, ?)", (message.chat.id, message.text))
                bot.reply_to(message, 'Дата присоединения или исключения была успешно добавлена в базу данных.')

            cursor.execute("DELETE FROM user_states WHERE user_id = ?", (message.chat.id,))

    conn.commit()
    conn.close()

bot.polling()
