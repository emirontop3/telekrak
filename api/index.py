import telebot
import requests
from flask import Flask, request

# Bot Tokenin
TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- ANALİZ MOTORU ---

def get_deep_analysis(coin_id="bitcoin"):
    try:
        # CoinGecko API üzerinden veri çekme
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id.lower()}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
        response = requests.get(url, timeout=10)
        res = response.json()
        
        data = res['market_data']
        price = data['current_price']['usd']
        change_24h = data['price_change_percentage_24h']
        ath = data['ath']['usd']
        market_cap = data['market_cap']['usd']
        
        # Duyarlılık Analizi (Sentiment)
        if change_24h > 7:
            sentiment = "AŞIRI BOĞA (BULLISH) 🔥"
        elif change_24h > 2:
            sentiment = "POZİTİF (UPWARD) 📈"
        elif change_24h < -7:
            sentiment = "AŞIRI AYI (BEARISH) 🧊"
        elif change_24h < -2:
            sentiment = "NEGATİF (DOWNWARD) 📉"
        else:
            sentiment = "NÖTR / YATAY ⚖️"
        
        analysis = (
            f"📊 <b>{res['name']} ({res['symbol'].upper()}) Analiz</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>Fiyat:</b> ${price:,.2f}\n"
            f"📈 <b>24s Değişim:</b> %{change_24h:.2f}\n"
            f"🏛️ <b>Market Hacmi:</b> ${market_cap:,.0f}\n"
            f"🏔️ <b>Zirve Uzaklığı (ATH):</b> %{abs((price-ath)/ath*100):.1f}\n\n"
            f"🧠 <b>Derin Duyarlılık:</b> {sentiment}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 <i>Veriler CoinGecko üzerinden anlık çekilmiştir.</i>"
        )
        return analysis
    except Exception:
        return "❌ Veri alınamadı. Sembolün doğru olduğundan emin ol (Örn: bitcoin, solana, ripple)."

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💎 Bitcoin", "🚀 Ethereum", "📊 Diğer Analizler", "🛠️ Yardım")
    bot.send_message(
        message.chat.id, 
        "🚀 <b>TeleKrak Deep Analiz V10</b>\n\nAnaliz etmek istediğin varlığı seçebilir veya bota ismini yazabilirsin.", 
        parse_mode='HTML', 
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "💎 Bitcoin")
def btc_analiz(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, get_deep_analysis("bitcoin"), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "🚀 Ethereum")
def eth_analiz(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, get_deep_analysis("ethereum"), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "📊 Diğer Analizler")
def other_analiz(message):
    msg = bot.send_message(message.chat.id, "Analiz etmek istediğiniz coin adını küçük harflerle yazın (Örn: solana, cardano):")
    bot.register_next_step_handler(msg, process_custom_analiz)

def process_custom_analiz(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, get_deep_analysis(message.text), parse_mode='HTML')

# --- VERCEL ROUTING ---

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    return "Bot Aktif ve Çalışıyor!"

@app.route('/webhook', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Hata', 403

if __name__ == "__main__":
    app.run()
