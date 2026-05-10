from flask import Flask, request
import telebot
from telebot import types

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Bot Gelişmiş Özelliklerle Aktif!"

@app.route('/webhook', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Hata', 403

# 1. Start Komutu ve Butonlar (Inline Keyboard)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Resim Gönder", callback_data='send_photo')
    item2 = types.InlineKeyboardButton("Anket Aç", callback_data='open_poll')
    item3 = types.InlineKeyboardButton("Konum İste", callback_data='get_location')
    item4 = types.InlineKeyboardButton("GitHub Sayfam", url='https://github.com/')
    
    markup.add(item1, item2, item3, item4)
    
    bot.send_message(message.chat.id, "Merhaba! Botun tüm özelliklerini test etmek için butonları kullan:", reply_markup=markup)

# 2. Buton Tıklamalarını Yakalama (Callback Query)
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "send_photo":
        # Örnek bir resim gönderimi
        bot.send_photo(call.message.chat.id, "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png", caption="İşte bir resim!")
    
    elif call.data == "open_poll":
        # Anket oluşturma
        options = ["Python", "JavaScript", "C++", "Lua"]
        bot.send_poll(call.message.chat.id, "En sevdiğin dil hangisi?", options, is_anonymous=False)
    
    elif call.data == "get_location":
        # Konum gönderme (Örn: İstanbul)
        bot.send_location(call.message.chat.id, 41.0082, 28.9784)
        bot.answer_callback_query(call.id, "Konum gönderildi!")

# 3. Dosya/Belge Gönderme Özelliği
@bot.message_handler(commands=['dosya'])
def send_doc(message):
    # Eğer sunucunda bir dosya varsa onu gönderebilirsin
    bot.send_document(message.chat.id, "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf", caption="Örnek PDF Dosyası")

# 4. Kullanıcı Bir Şey Yazdığında (Echo + HTML Formatı)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = f"<b>Gelen Mesaj:</b> <i>{message.text}</i>\n\nKomutları görmek için /start yazabilirsin."
    bot.send_message(message.chat.id, text, parse_mode='HTML')
