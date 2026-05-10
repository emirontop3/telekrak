import telebot
import random
import re
import base64
from flask import Flask, request

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- JAVASCRIPT OBFUSCATOR ENGINE ---

def js_obfuscator(code):
    # 1. Değişkenleri ve Fonksiyonları Gizle (_0xabc123 formatı)
    def rename_vars(js):
        vars_found = re.findall(r'\b(?:var|let|const|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)', js)
        var_map = {}
        for v in set(vars_found):
            if v not in ["main", "init"]: # Korunacak kelimeler
                var_map[v] = f"_0x{random.getrandbits(16):x}"
        
        for old, new in var_map.items():
            js = re.sub(r'\b' + old + r'\b', new, js)
        return js

    # 2. Stringleri Hex Formatına Çevir
    def hexify_strings(js):
        def to_hex(match):
            s = match.group(1)
            return "'" + "".join([f"\\x{ord(c):02x}" for c in s]) + "'"
        return re.sub(r"'(.*?)'|\"(.*?)\"", to_hex, js)

    # İşlemleri uygula
    code = rename_vars(code)
    code = hexify_strings(code)
    
    # Başına karmaşık bir yorum ekle
    header = f"/* Obfuscated by TeleKrak JS Engine | ID: {random.randint(1000,9999)} */\n"
    return header + code

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 **TeleKrak JS Obfuscator Aktif!**\n\nKarartmak istediğin JavaScript kodunu gönder, anında şifreleyeyim.", parse_mode='HTML')

@bot.message_handler(func=lambda m: True)
def handle_js(message):
    # Eğer gelen mesaj kod bloğu gibi görünüyorsa işlem yap
    if len(message.text) > 5:
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            obfuscated = js_obfuscator(message.text)
            bot.send_message(message.chat.id, f"🔐 **Karartılmış JS Kodun:**\n\n<code>{obfuscated}</code>", parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, f"❌ İşlem sırasında hata: {e}")
    else:
        bot.reply_to(message, "Lütfen geçerli bir JS kodu gönder.")

# --- VERCEL FIX (404 HATASI ÇÖZÜMÜ) ---

@app.route('/')
def home():
    # Bu kısım Vercel'e girdiğinde 404 yerine bu mesajı gösterir
    return "<h1>TeleKrak Bot Aktif!</h1><p>Lütfen Telegram üzerinden iletişime geçin.</p>", 200

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
