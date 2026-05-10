from flask import Flask, request
import telebot
from telebot import types
import time

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Ultra Bot Aktif!"

@app.route('/webhook', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Hata', 403

# --- 1. ANA MENÜ (REPLY KEYBOARD) ---
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📸 Medya Paketi")
    btn2 = types.KeyboardButton("📊 İnteraktif Test")
    btn3 = types.KeyboardButton("📍 Konum ve Kişi")
    btn4 = types.KeyboardButton("🎮 Mini Uygulama")
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(
        message.chat.id, 
        "<b>Ultra Özellikli Bot Paneline Hoş Geldin!</b>\n\nBu bot Telegram API'nin en gelişmiş fonksiyonlarını kullanır.", 
        parse_mode='HTML', 
        reply_markup=markup
    )

# --- 2. MEDYA GRUBU (ALBÜM) GÖNDERME ---
@bot.message_handler(func=lambda m: m.text == "📸 Medya Paketi")
def send_media_group(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    media = [
        types.InputMediaPhoto('https://picsum.photos/200/300', caption="Çoklu Medya Özelliği"),
        types.InputMediaPhoto('https://picsum.photos/201/301'),
        types.InputMediaVideo('http://techslides.com/demos/sample-videos/small.mp4')
    ]
    bot.send_media_group(message.chat.id, media)

# --- 3. ANKET VE TEST MODU ---
@bot.message_handler(func=lambda m: m.text == "📊 İnteraktif Test")
def send_quiz(message):
    bot.send_poll(
        chat_id=message.chat.id,
        question="Telegram API hangi dilde daha popülerdir?",
        options=["Python", "Node.js", "PHP", "Go"],
        type="quiz",
        correct_option_id=0,
        explanation="En popüler kütüphaneler (telebot, aiogram) Python tabanlıdır."
    )

# --- 4. ÖZEL BUTONLAR (KONUM VE REHBER) ---
@bot.message_handler(func=lambda m: m.text == "📍 Konum ve Kişi")
def share_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    loc_btn = types.KeyboardButton("Konumumu Paylaş", request_location=True)
    con_btn = types.KeyboardButton("Numaramı Paylaş", request_contact=True)
    back_btn = types.KeyboardButton("Ana Menü")
    markup.add(loc_btn, con_btn, back_btn)
    bot.send_message(message.chat.id, "Aşağıdaki butonları kullanarak veri paylaşabilirsin:", reply_markup=markup)

# --- 5. DİNAMİK INLINE BUTONLAR ---
@bot.message_handler(commands=['ayarlar'])
def settings_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔔 Bildirimleri Aç/Kapat", callback_data="toggle_notify"))
    markup.add(types.InlineKeyboardButton("🗑 Mesajı Sil", callback_data="delete_msg"))
    bot.send_message(message.chat.id, "Bot Ayarları:", reply_markup=markup)

# --- 6. CALLBACK İŞLEYİCİ (ARKA PLAN İŞLEMLERİ) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "delete_msg":
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "toggle_notify":
        bot.answer_callback_query(call.id, "Bildirim ayarları güncellendi!", show_alert=True)

# --- 7. MESAJ DÜZENLEME (EDIT MESSAGE) ---
@bot.message_handler(commands=['edit'])
def edit_example(message):
    msg = bot.send_message(message.chat.id, "Bu mesaj 3 saniye içinde değişecek...")
    time.sleep(3)
    bot.edit_message_text("Gördün mü? Mesaj başarıyla güncellendi!", message.chat.id, msg.message_id)

# --- 8. SESLİ MESAJ VE DOSYA YÖNETİMİ ---
@bot.message_handler(content_types=['voice', 'audio', 'document'])
def handle_docs(message):
    bot.reply_to(message, "Dosya/Ses başarıyla alındı ve sunucuya işlendi.")
