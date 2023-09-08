import telebot
import sqlite3

BOT_TOKEN = 'BOT_TOKEN'
bot = telebot.TeleBot(BOT_TOKEN)

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id TEXT,
             user_name TEXT,
             view_name TEXT,
             create_date DATETIME
             )''')

c.execute('''CREATE TABLE IF NOT EXISTS folders 
             (user_id TEXT,
             folder_id INTEGER PRIMARY KEY AUTOINCREMENT,
             folder_name TEXT, 
             parent_folder_id TEXT DEFAULT 'root',
             create_date DATETIME,
             FOREIGN KEY(user_id) REFERENCES users(user_id),
             FOREIGN KEY(parent_folder_id) REFERENCES folders(folder_id))''')

c.execute('''CREATE TABLE IF NOT EXISTS files
             (file_id TEXT,
             file_name TEXT,
             path_file TEXT,
             user_id TEXT,
             folder_id TEXT,
             upload_date DATETIME,
             file_size INTEGER,
             FOREIGN KEY(user_id) REFERENCES users(user_id),
             FOREIGN KEY(folder_id) REFERENCES folders(folder_id))''')
conn.close()
