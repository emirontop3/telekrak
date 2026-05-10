import telebot
from telebot import types
from flask import Flask, request

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# SUNUCU HAFIZASI (Vercel'de çalışma süresince tutulur)
# Not: Vercel uyuduğunda bu liste sıfırlanabilir. Kalıcı çözüm için MongoDB/Firebase gerekir.
active_servers = {} 
selected_target = {}

# --- OTOMATİK SUNUCU KAYIT SİSTEMİ ---
@bot.message_handler(content_types=['new_chat_members', 'group_chat_created', 'supergroup_chat_created'])
def auto_register(message):
    """Bot bir gruba eklendiğinde orayı hafızaya kaydeder."""
    chat_id = str(message.chat.id)
    chat_title = message.chat.title or "Bilinmeyen Sunucu"
    active_servers[chat_id] = chat_title
    bot.send_message(message.chat.id, f"✅ <b>Sistem Bağlantısı Kuruldu:</b> {chat_title}\nArtık bu sunucu uzaktan yönetilebilir.", parse_mode='HTML')

# --- SERV KOMUTU (DİNAMİK LİSTE) ---
@bot.message_handler(func=lambda m: m.text == "!serv")
def list_servers(message):
    if not active_servers:
        bot.reply_to(message, "⚠️ Henüz hafızada kayıtlı sunucu yok. Botu bir gruba ekle veya botun olduğu grupta bir mesaj yaz.")
        return

    markup = types.InlineKeyboardMarkup()
    for cid, name in active_servers.items():
        markup.add(types.InlineKeyboardButton(f"🌐 {name}", callback_data=f"select_{cid}"))
    
    bot.send_message(message.chat.id, "<b>Aktif Bağlantı Bulunan Sunucular:</b>", parse_mode='HTML', reply_markup=markup)

# --- NUKE VE YÖNETİM İŞLEMLERİ ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def handle_select(call):
    target_id = call.data.split("_")[1]
    selected_target[call.message.chat.id] = target_id
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 NUKE", callback_data="action_nuke"))
    markup.add(types.InlineKeyboardButton("🗑️ Hafızadan Sil", callback_data="action_remove"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📍 Hedef: <b>{active_servers.get(target_id, 'Bilinmeyen')}</b>\nEylem seçin:",
        parse_mode='HTML',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("action_"))
def handle_action(call):
    chat_id = call.message.chat.id
    target_id = selected_target.get(chat_id)

    if call.data == "action_nuke":
        try:
            bot.send_message(target_id, "<b>Hello from me!</b> 🚀🔥", parse_mode='HTML')
            bot.answer_callback_query(call.id, "Nuke başarılı!")
        except:
            bot.answer_callback_query(call.id, "Hata: Yetki yetersiz!", show_alert=True)
            
    elif call.data == "action_remove":
        if target_id in active_servers:
            del active_servers[target_id]
        bot.edit_message_text("Sunucu hafızadan silindi.", chat_id, call.message.message_id)

# Herhangi bir grupta mesaj yazıldığında da bot o grubu hafızaya alsın (Garantilemek için)
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def track_activity(message):
    cid = str(message.chat.id)
    if cid not in active_servers:
        active_servers[cid] = message.chat.title

# --- VERCEL STANDART ---
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
