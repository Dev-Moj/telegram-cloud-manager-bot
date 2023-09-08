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
             create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


@bot.message_handler(commands=['start'])
def start(message):
    if not user_exists(message.from_user):
        add_user(message.from_user)
        print('User added')
    else:
        print('User was available')


if __name__ == "__main__":
    bot.polling()
