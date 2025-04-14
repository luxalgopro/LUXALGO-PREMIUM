import os
import sqlite3
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher

# Bot token and admin ID
TOKEN = "7501206181:AAFGPiup1j1VVXZt_9FE8rQ71px1dztGa38"
ADMIN_ID = 7619488744  # Your Telegram user ID

# Initialize Flask app
app = Flask(__name__)

# Initialize bot
bot = Bot(token=TOKEN)

# SQLite setup
def init_db():
    conn = sqlite3.connect('access.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS codes (code TEXT UNIQUE)''')
    conn.commit()
    conn.close()

# Telegram command handlers
def start(update, context):
    update.message.reply_text("Welcome to LUXALGO PREMIUM! To begin, enter your code using: /code <yourcode>.")

def code(update, context):
    if not context.args:
        update.message.reply_text("Please provide a code using: /code <yourcode>")
        return

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

def generate_code(update, context):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Unauthorized access.")
        return

    if not context.args:
        update.message.reply_text("Usage: /generate <code>")
        return

    new_code = context.args[0]
    conn = sqlite3.connect('access.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO codes (code) VALUES (?)", (new_code,))
        conn.commit()
        update.message.reply_text(f"Code '{new_code}' added successfully.")
    except sqlite3.IntegrityError:
        update.message.reply_text("This code already exists.")
    finally:
        conn.close()

# Dispatcher setup
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("code", code))
dispatcher.add_handler(CommandHandler("generate", generate_code))

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Set webhook
@app.before_first_request
def setup():
    init_db()
    bot.setWebhook(f"https://luxalgo-premium.onrender.com/{TOKEN}")

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
