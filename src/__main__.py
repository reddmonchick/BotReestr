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

def send_main_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Дата')
    itembtn2 = types.KeyboardButton('Статус')
    itembtn3 = types.KeyboardButton('Исключены или вступили за эти даты в сро')
    itembtn4 = types.KeyboardButton('Показать фильтры')
    itembtn5 = types.KeyboardButton('Очистить фильтры')
    itembtn6 = types.KeyboardButton('Запустить парсинг')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
    bot.send_message(chat_id, "Выберите фильтр:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_main_keyboard(message.chat.id)

@bot.message_handler(commands=['filters'])
def show_filters(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    user_id = message.chat.id

    cursor.execute("SELECT message FROM date_responses WHERE user_id = ?", (user_id,))
    date_response = cursor.fetchone()
    date_response = date_response[0] if date_response else 'Не указано'

    cursor.execute("SELECT message FROM status_responses WHERE user_id = ?", (user_id,))
    status_response = cursor.fetchone()
    status_response = status_response[0] if status_response else 'Не указано'

    cursor.execute("SELECT message FROM date_joined WHERE user_id = ?", (user_id,))
    date_join_response = cursor.fetchone()
    date_join_response = date_join_response[0] if date_join_response else 'Не указано'

    response = (f"Текущие фильтры:\n"
                f"Дата: {date_response}\n"
                f"Статус: {status_response}\n"
                f"Исключены или вступили: {date_join_response}")

    bot.send_message(message.chat.id, response)

    conn.close()

@bot.message_handler(commands=['clear_filters'])
def clear_filters(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    user_id = message.chat.id

    cursor.execute("DELETE FROM date_responses WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM status_responses WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM date_joined WHERE user_id = ?", (user_id,))

    bot.send_message(message.chat.id, "Все фильтры были успешно очищены.")

    conn.commit()
    conn.close()

def run_pars(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    id_user = message.chat.id

    cursor.execute("SELECT user_id, message FROM date_responses WHERE user_id = ?", (id_user,))
    result_data = cursor.fetchone()
    if not result_data:
        result_data = ['', '']
    cursor.execute("SELECT user_id, message FROM status_responses WHERE user_id = ?", (id_user,))
    fetchone = cursor.fetchone()
    if fetchone:
        result_status = True if fetchone[-1] == 'Является' else False if fetchone[-1] == 'Исключен' else None
    else:
        result_status = True

    cursor.execute("SELECT user_id, message FROM date_joined WHERE user_id = ?", (id_user,))
    fetchone = cursor.fetchone()
    if fetchone:
        date_join = True if fetchone[-1] == 'Вступили' else False if fetchone[-1] == 'Исключены' else True
    else:
        date_join = True

    filters_data = FiltersParser(
        data_start=result_data[1].split(' ')[0].strip(),
        data_end=result_data[1].split(' ')[-1].strip(),
        date_join=date_join,
        status=result_status,
        user_id=id_user
    )
    print(filters_data)

    nopriz = Nopriz(filters_data)
    novstroy = Novstroy(filters_data)

    nopriz.parse()
    novstroy.parse()

    nopriz_file = f"{id_user}_nopriz.xlsx"
    novstroy_file = f"{id_user}_novstroy.xlsx"

    # Send the generated files to the user
    with open(nopriz_file, 'rb') as nopriz_document:
        bot.send_document(chat_id=id_user, document=nopriz_document)

    with open(novstroy_file, 'rb') as novstroy_document:
        bot.send_document(chat_id=id_user, document=novstroy_document)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT state FROM user_states WHERE user_id = ?", (message.chat.id,))
    filter_type = cursor.fetchone()

    if message.text == 'Дата':
        response = ('Введите дату: \n'
                    'Пример, как вводить дату: 2024-08-20 2024-09-30')
        bot.reply_to(message, response)
        cursor.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (message.chat.id, 'Дата'))
    elif message.text == 'Статус':
        # Создание клавиатуры для выбора статуса
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('Является')
        itembtn2 = types.KeyboardButton('Исключен')
        itembtn_back = types.KeyboardButton('Назад')
        markup.add(itembtn1, itembtn2, itembtn_back)
        bot.send_message(message.chat.id, "Выберите статус:", reply_markup=markup)
        cursor.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (message.chat.id, 'Статус'))
    elif message.text == 'Исключены или вступили за эти даты в сро':
        # Создание клавиатуры для выбора вступили или исключены
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('Исключены')
        itembtn2 = types.KeyboardButton('Вступили')
        itembtn_back = types.KeyboardButton('Назад')
        markup.add(itembtn1, itembtn2, itembtn_back)
        bot.send_message(message.chat.id, "Выберите вариант:", reply_markup=markup)
        cursor.execute("INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)", (message.chat.id, 'Вступили или исключены даты'))
    elif message.text == 'Показать фильтры':
        show_filters(message)
    elif message.text == 'Очистить фильтры':
        clear_filters(message)
    elif message.text == 'Запустить парсинг':
        run_pars(message)
    elif message.text == 'Назад':
        send_main_keyboard(message.chat.id)
    else:
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

