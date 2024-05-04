import telebot
import sqlite3
from dotenv import load_dotenv
import os
from telebot import apihelper
from pprint import pprint

load_dotenv()

apihelper.proxy = {
    'http': 'http://127.0.0.1:8889',
    'https': 'http://127.0.0.1:8889'
}
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
conn = sqlite3.connect('database.db')
c = conn.cursor()

current_path = ''


def db_handler():
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT,
                 user_name TEXT,
                 view_name TEXT,
                 create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS dir 
                 (user_id TEXT,
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 type TEXT, 
                 parent_id TEXT DEFAULT '',
                 create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY(user_id) REFERENCES users(user_id),
                 FOREIGN KEY(parent_id) REFERENCES dir(id))''')
    conn.close()


def user_exists(user):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE user_id=?", (user.id,))
    result = c.fetchone()
    count = result[0]
    conn.close()
    if count > 0:
        return True
    else:
        return False


def add_user(user):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, user_name, view_name, create_date) VALUES (?, ?, ?, datetime('now'))",
              (user.id, user.username, user.first_name))
    conn.commit()
    conn.close()


def create_folder(user_id, name, parent_folder_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO dir (user_id, name ,parent_id,  create_date, type) VALUES (? ,? ,? ,datetime('now'),'d')",
              (user_id, name, parent_folder_id))
    conn.commit()
    conn.close()


def folder_file_view(user_id, parent_folder_id=''):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM dir WHERE user_id=? AND parent_id=?',
              (user_id, parent_folder_id))
    result = c.fetchall()
    print(result)
    global current_path
    current_path = result[0][4]
    back = [telebot.types.InlineKeyboardButton('../', callback_data=f'?q=b-{result[0][4]}')] if result else []
    dirs = [telebot.types.InlineKeyboardButton(i[2], callback_data=f'?q=d-{i[1]}') for i in result if i[3] == 'd']
    files = [telebot.types.InlineKeyboardButton(i[2], callback_data=f'?q=-f{i[1]}') for i in result if i[3] == 'f']
    conn.commit()
    conn.close()
    return back + dirs + files


# @bot.message_handler(func=lambda x: True, content_types=['audio', 'photo', 'voice', 'video', 'document', 'contact'])
# def handle_docs(message):
#     print(message)
#     print(current_path)


@bot.callback_query_handler(func=lambda call: call.data.startswith('?q=b-'))
def back(message):
    dir = message.data.replace('?q=b-', '')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT parent_id FROM dir WHERE user_id=? AND id=?', (message.from_user.id, dir))
    result = c.fetchone()
    d = folder_file_view(message.from_user.id, result[0])
    buttons = telebot.types.InlineKeyboardMarkup(row_width=1)
    buttons.add(*d)

    chat_id = message.from_user.id
    bot.send_message(chat_id, "list", reply_markup=buttons)


@bot.callback_query_handler(func=lambda call: call.data.startswith('?q=d-'))
def get_dirs(message):
    dir = message.data.replace('?q=d-', '')
    d = folder_file_view(message.from_user.id, parent_folder_id=dir)
    buttons = telebot.types.InlineKeyboardMarkup(row_width=1)
    buttons.add(*d)
    print(dir)
    chat_id = message.from_user.id
    txt = 'list' if d else 'noting'
    bot.send_message(chat_id, txt, reply_markup=buttons)


@bot.callback_query_handler(func=lambda call: call.data.startswith('?q=f-'))
def get_files(message):
    file = message.data.replace('?q=f-', '')
    d = folder_file_view(message.from_user.id, parent_folder_id=file)
    print(d)


@bot.message_handler(commands=['start'])
def start(message):
    if not user_exists(message.from_user):
        add_user(message.from_user)
        create_folder(user_id=message.from_user.id, name='root', parent_folder_id='')
        print('User added')
    else:
        d = folder_file_view(message.from_user.id, parent_folder_id='1')
        buttons = telebot.types.InlineKeyboardMarkup(row_width=1)
        buttons.add(*d)
        chat_id = message.chat.id
        bot.send_message(chat_id, "list", reply_markup=buttons)


if __name__ == "__main__":
    db_handler()
    bot.polling()
