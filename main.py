import os
import sqlite3
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher
from telegram.ext import Updater

TOKEN = "7501206181:AAFGPiup1j1VVXZt_9FE8rQ71px1dztGa38"  # Replace with your bot token
TRADE_API_URL = "https://api.tradingview.com"  # Example API URL, replace with actual one

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

# Fetch Live Market Data (Placeholder, will integrate actual API)
def fetch_market_data():
    # Placeholder for actual API call to fetch live data
    # Replace with a real market data fetching API
    response = requests.get(f'{TRADE_API_URL}/live_data')
    data = response.json()
    return data  # Example structure: {'price': 1000, 'trend': 'up'}

# Analyze Market Data (Placeholder for Analysis Logic)
def analyze_market(data):
    # Placeholder for actual analysis logic based on market data
    # Implement your analysis strategy here
    if data['price'] > 1000:
        return "Uptrend detected. Consider buying."
    else:
        return "Downtrend detected. Consider selling."

# Send Analysis to User
def send_analysis(update, analysis):
    update.message.reply_text(analysis)

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
        update.message.reply_text("To get market analysis, send /analysis.")
    else:
        update.message.reply_text("Invalid code. Please contact the admin for access.")

def analysis(update, context):
    # Fetch live market data
    market_data = fetch_market_data()
    
    # Analyze the market data
    analysis = analyze_market(market_data)
    
    # Send the analysis to the user
    send_analysis(update, analysis)

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
    dispatcher.add_handler(CommandHandler('analysis', analysis))  # Add new command for market analysis

    bot.setWebhook(f'https://<your-render-app-url>/{TOKEN}')  # Replace with actual URL when deployed

# Initialize DB and Dispatcher
init_db()
setup_dispatcher()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
