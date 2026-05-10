import telebot
import requests
import pandas as pd
from flask import Flask, request

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- ANALİZ MOTORU ---

def get_deep_crypto_analysis(coin_id="bitcoin"):
    """CoinGecko ve basit teknik analiz mantığı kullanarak veri çeker."""
    try:
        # Market verilerini çek
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id.lower()}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
        res = requests.get(url).json()
        
        data = res['market_data']
        price = data['current_price']['usd']
        change_24h = data['price_change_percentage_24h']
        high_24h = data['high_24h']['usd']
        low_24h = data['low_24h']['usd']
        ath = data['ath']['usd']
        
        # Basit "Deep Analiz" Mantığı
        sentiment = "NÖTR ⚖️"
        if change_24h > 5: sentiment = "AŞIRI ALIM (BULLISH) 🔥"
        elif change_24h < -5: sentiment = "AŞIRI SATIM (BEARISH) 🧊"
        
        analysis = (
            f"📊 <b>{res['name']} ({res['symbol'].upper()}) Derin Analiz</b>\n\n"
            f"💰 <b>Güncel Fiyat:</b> ${price:,}\n"
            f"📈 <b>24s Değişim:</b> %{change_24h:.2f}\n"
            f"🏔️ <b>24s En Yüksek:</b> ${high_24h:,}\n"
            f"📉 <b>24s En Düşük:</b> ${low_24h:,}\n"
            f"🏆 <b>Tüm Zamanlar Zirvesi (ATH):</b> ${ath:,}\n\n"
            f"🧠 <b>Piyasa Duyarlılığı:</b> {sentiment}\n"
            f"💡 <i>Öneri: ATH noktasından %{abs((price-ath)/ath*100):.1f} uzakta.</i>"
        )
        return analysis
    except Exception as e:
        return f"Hata: Veri çekilemedi. (Coin adını doğru yazdığınızdan emin olun) {e}"

def get_stock_price(symbol):
    """Global hisse senetleri için basit analiz."""
    # Yahoo Finance üzerinden veri çekmek için hızlı bir API
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers).json()
    
    try:
        price = res['chart']['result'][0]['meta']['regularMarketPrice']
        prev_close = res['chart']['result'][0]['meta']['previousClose']
        diff = ((price - prev_close) / prev_close) * 100
        
        return (
            f"🍏 <b>Hisse Analizi: {symbol.upper()}</b>\n\n"
            f"💵 <b>Fiyat:</b> ${price}\n"
            f"📊 <b>Günlük Fark:</b> %{diff:.2f}\n"
            f"📉 <b>Önceki Kapanış:</b> ${prev_close}"
        )
    except:
        return "Hisse senedi bulunamadı."

# --- BOT KOMUTLARI ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💎 Bitcoin Analiz", "🚀 Altcoin Analiz", "🍏 Hisse Senedi", "📈 Genel Durum")
    bot.send_message(message.chat.id, "<b>TeleKrak Pro Analiz Paneline Hoş Geldin!</b>\n\nAnaliz etmek istediğin varlığı seç veya bir sembol gönder (Örn: /analiz ethereum)", parse_mode='HTML', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💎 Bitcoin Analiz")
def btc_analiz(message):
    bot.reply_to(message, "Bitcoin verileri analiz ediliyor...")
    analysis = get_deep_crypto_analysis("bitcoin")
    bot.send_message(message.chat.id, analysis, parse_mode='HTML')

@bot.message_handler(commands=['analiz'])
def custom_analiz(message):
    msg = message.text.split()
    if len(msg) > 1:
        target = msg[1]
        analysis = get_deep_crypto_analysis(target)
        bot.send_message(message.chat.id, analysis, parse_mode='HTML')
    else:
        bot.reply_to(message, "Lütfen bir isim yazın. Örn: /analiz solana")

@bot.message_handler(func=lambda m: m.text == "🍏 Hisse Senedi")
def stock_prompt(message):
    msg = bot.send_message(message.chat.id, "Analiz edilecek hisse sembolünü yaz (Örn: AAPL, TSLA, NVDA):")
    bot.register_next_step_handler(msg, process_stock)

def process_stock(message):
    symbol = message.text.upper()
    analysis = get_stock_price(symbol)
    bot.send_message(message.chat.id, analysis, parse_mode='HTML')

# --- VERCEL GATEWAY ---
@app.route('/webhook', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Hata', 403
