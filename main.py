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



conn.close()