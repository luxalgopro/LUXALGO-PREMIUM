import os
import sqlite3
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher
from telegram.ext import Updater

TOKEN = "your_bot_token_here"  # Replace with your bot token

# Initialize Flask
app = Flask(__name__)

# Initialize Telegram Bot
bot = Bot(token=TOKEN)

# SQLite Database Setup
def init_db():
    conn = sqlite3.connect('access.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS codes (code TEXT UNIQUE)''')
    conn.commit()
    conn.close()

# Commands
def start(update, context):
    update.message.reply_text("Welcome to LUXALGO PREMIUM! To begin, enter your code using: /code <yourcode>.")

def code(update, context):
    user_code = ' '.join(context.args)
    conn = sqlite3.connect('access.db')
    c = conn.cursor()
    c.execute("SELECT * FROM codes WHERE code=?", (user_code,))
    result = c.fetchone()
    conn.close()

    if result:
        update.message.reply_text("Access granted! You can now use the bot commands.")
    else:
        update.message.reply_text("Invalid code. Please contact the admin for access.")

# New route to add code
@app.route('/addcode/<code>', methods=['GET'])
def add_code(code):
    conn = sqlite3.connect('access.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO codes (code) VALUES (?)", (code,))
        conn.commit()
        return f"Code {code} added successfully!"
    except sqlite3.IntegrityError:
        return f"Code {code} already exists."
    finally:
        conn.close()

# Flask routes for webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return 'ok'

# Start function to set up commands and webhook
def setup_dispatcher():
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('code', code))

    bot.setWebhook(f'https://luxalgo-premium.onrender.com/{TOKEN}')  # Replace with actual URL when deployed

# Initialize DB and Dispatcher
init_db()
setup_dispatcher()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
