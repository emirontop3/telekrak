import telebot
from telebot import types
from flask import Flask, request

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Botun ekli olduğu ve işlem yapabileceğin kanalların listesi
# Not: Botun bu kanallarda mesaj atabilmesi için ADMIN olması gerekir.
CHANNELS = {
    "Genel Sohbet": "-100123456789", # Kendi Kanal ID'lerini buraya ekle
    "Duyuru Kanalı": "-100987654321",
    "Test Grubu": "-100555444333"
}

selected_target = {} # Hangi kullanıcının hangi kanalı seçtiğini tutar

@bot.message_handler(commands=['serv'])
def server_list(message):
    """Sistemdeki kayıtlı sunucuları listeler."""
    markup = types.InlineKeyboardMarkup()
    for name, cid in CHANNELS.items():
        markup.add(types.InlineKeyboardButton(f"🌐 {name}", callback_data=f"select_{cid}"))
    
    bot.send_message(message.chat.id, "<b>Yönetilebilir Sunucular Listesi:</b>\nBir hedef seçin:", parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def handle_selection(call):
    chat_id = call.message.chat.id
    target_id = call.data.split("_")[1]
    
    # Seçimi kaydet
    selected_target[chat_id] = target_id
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 NUKE (Mesaj Gönder)", callback_data="action_nuke"))
    markup.add(types.InlineKeyboardButton("❌ Vazgeç", callback_data="action_cancel"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"✅ Hedef Seçildi: <code>{target_id}</code>\nŞimdi ne yapmak istersin?",
        parse_mode='HTML',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("action_"))
def handle_action(call):
    chat_id = call.message.chat.id
    
    if call.data == "action_nuke":
        if chat_id in selected_target:
            target = selected_target[chat_id]
            try:
                # İstediğin o meşhur mesajı gönderiyoruz
                bot.send_message(target, "<b>Hello from me!</b> 🚀🔥", parse_mode='HTML')
                bot.answer_callback_query(call.id, "Nuke başarılı! 💥")
                bot.send_message(chat_id, f"✅ Mesaj başarıyla iletildi: <code>{target}</code>", parse_mode='HTML')
            except Exception as e:
                bot.send_message(chat_id, f"❌ Hata: Bot bu kanalda yönetici mi?\nDetay: {e}")
        else:
            bot.answer_callback_query(call.id, "Önce bir hedef seçmelisin!")
            
    elif call.data == "action_cancel":
        bot.edit_message_text("İşlem iptal edildi.", chat_id, call.message.message_id)

# --- STANDART VERCEL AYARLARI ---

@app.route('/favicon.ico')
def favicon(): return '', 204

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
