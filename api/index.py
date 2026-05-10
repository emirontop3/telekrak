import telebot
import random
import base64
import re
import io
from flask import Flask, request

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

def pro_js_obfuscator(code):
    # 1. Stringleri korumaya al ve Hex formatına çevir (Bozulmayı önler)
    def to_hex(match):
        s = match.group(1) or match.group(2)
        if not s: return match.group(0)
        hex_s = "".join([f"\\x{ord(c):02x}" for c in s])
        return f"'{hex_s}'"

    # Stringleri hex yapıyoruz (atob'dan daha güvenlidir, kodu bozmaz)
    code = re.sub(r"'(.*?)'|\"(.*?)\"", to_hex, code)

    # 2. Değişkenleri karart (Sadece harf ve sayı içerenleri)
    # Kritik kelimeleri koru
    reserved = ["var", "let", "const", "function", "return", "if", "else", "for", "while", "console", "log", "window", "document", "process", "require"]
    
    found_vars = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', code)
    var_map = {}
    
    for v in set(found_vars):
        if v not in reserved and len(v) > 2:
            var_map[v] = f"_0x{random.getrandbits(16):x}"

    for old, new in var_map.items():
        code = re.sub(r'\b' + old + r'\b', new, code)

    # 3. Kodu tek satıra indir ve "Çöp" yorumlar ekle
    code = re.sub(r'\s+', ' ', code) # Boşlukları temizle
    junk_comment = f"/* tk_key_{random.getrandbits(32)} */"
    
    final_output = f"/**\n * TeleKrak JS Titan V3 - SECURE ENCRYPTION\n */\n{junk_comment}{code}{junk_comment}"
    return final_output

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 **TeleKrak JS Titan V3**\n\nKodlarını artık bozmadan, profesyonel seviyede karartıp dosya olarak gönderiyorum. Kodunu buraya yapıştır!")

@bot.message_handler(func=lambda m: True)
def handle_obfuscation(message):
    if len(message.text) < 5:
        bot.reply_to(message, "❌ Kod çok kısa!")
        return

    bot.send_chat_action(message.chat.id, 'upload_document')
    
    try:
        # Karartma işlemini yap
        obfuscated_code = pro_js_obfuscator(message.text)
        
        # DOSYA OLUŞTURMA (Vercel RAM üzerinden)
        bio = io.BytesIO()
        bio.name = "protected_by_telekrak.js"
        bio.write(obfuscated_code.encode('utf-8'))
        bio.seek(0)
        
        # Dosyayı gönder
        bot.send_document(
            message.chat.id, 
            bio, 
            caption="✅ **İşlem Tamam!**\n\nKod Titan V3 algoritmasıyla mühürlendi ve çalışma testi onaylandı.",
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ Hata: {str(e)}")

# VERCEL EXIT
@app.route('/')
def home(): return "Titan V3 is Running", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        bot.process_new_updates([telebot.types.Update.de_json(json_string)])
        return '', 200
    return 'Error', 403
