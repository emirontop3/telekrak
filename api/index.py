import telebot
import requests
from flask import Flask, request

# Bot Bilgileri
TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- DERİN ANALİZ MOTORU ---

def get_pro_analysis(coin_id="bitcoin"):
    try:
        # CoinGecko Pro-Data Endpoint
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id.lower()}?localization=false&sparkline=false"
        res = requests.get(url, timeout=10).json()
        
        m_data = res['market_data']
        
        # Güncel Veriler
        price = m_data['current_price']['usd']
        change_24h = m_data['price_change_percentage_24h']
        ath = m_data['ath']['usd']
        ath_date = m_data['ath_date']['usd'][:10] # Sadece tarih
        
        # TARİHSEL DEĞERLER (Mükemmel Detay)
        change_30d = m_data.get('price_change_percentage_30d', 0)
        change_200d = m_data.get('price_change_percentage_200d', 0)
        change_1y = m_data.get('price_change_percentage_1y', 0)
        
        # Geçen Yılki Fiyat Tahmini
        price_1y_ago = price / (1 + (change_1y / 100))
        
        # Puanlama Mantığı (0-100)
        score = 50
        if change_24h > 0: score += 10
        if change_1y > 100: score += 20
        if change_30d > 10: score += 15
        
        analysis = (
            f"🏛️ <b>{res['name']} ({res['symbol'].upper()}) DEEP REPORT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>Anlık Fiyat:</b> ${price:,.2f}\n"
            f"📈 <b>24 Saatlik:</b> %{change_24h:.2f}\n"
            f"📉 <b>30 Günlük:</b> %{change_30d:.2f}\n\n"
            f"⏳ <b>TARİHSEL KIYASLAMA</b>\n"
            f"📅 <b>1 Yıl Önce:</b> ~${price_1y_ago:,.2f} (%{change_1y:.1f} değişim)\n"
            f"🏔️ <b>Zirve (ATH):</b> ${ath:,.2f}\n"
            f"🗓️ <b>Zirve Tarihi:</b> {ath_date}\n\n"
            f"🧠 <b>YAPAY ZEKA PUANI:</b> {score}/100\n"
            f"📢 <b>Sinyal:</b> {'GÜÇLÜ AL ✅' if score > 70 else 'BEKLE/İZLE ⏳' if score > 40 else 'DİKKATLİ OL ⚠️'}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛸 <i>TeleKrak Pro Analiz Sistemi</i>"
        )
        return analysis
    except Exception as e:
        return f"❌ Analiz başarısız. Lütfen tam adı yazın (Örn: solana, cardano).\nHata: {str(e)[:50]}"

# --- BOT KOMUTLARI ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 BTC Analiz", "💎 ETH Analiz", "🔍 Özel Analiz", "📜 Hakkında")
    bot.send_message(
        message.chat.id, 
        "🛡️ <b>TeleKrak Pro Borsaya Hoş Geldiniz.</b>\n\nBu bot, verileri derinlemesine tarar ve geçmiş dönemle kıyaslayarak size bir 'Yatırım Puanı' sunar.", 
        parse_mode='HTML', 
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "📊 BTC Analiz")
def btc(message):
    bot.send_message(message.chat.id, get_pro_analysis("bitcoin"), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "💎 ETH Analiz")
def eth(message):
    bot.send_message(message.chat.id, get_pro_analysis("ethereum"), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "🔍 Özel Analiz")
def custom(message):
    msg = bot.send_message(message.chat.id, "Analiz edilecek varlığın tam adını gönder (Örn: dogecoin):")
    bot.register_next_step_handler(msg, process_custom)

def process_custom(message):
    bot.send_message(message.chat.id, get_pro_analysis(message.text), parse_mode='HTML')

# --- VERCEL CONFIG ---

@app.route('/favicon.ico')
def favicon(): return '', 204

@app.route('/')
def home(): return "Pro Bot Online"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

if __name__ == "__main__":
    app.run()
