from flask import Flask, request
import telebot
import os

# Bot tokenini buraya tanımlıyoruz
TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot aktif ve Webhook bekliyor..."

@app.route(f'/{TOKEN}', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Hata', 403

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Selam! Vercel üzerinde kesintisiz çalışıyorum.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Mesajını aldım: {message.text}")
