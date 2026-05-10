from flask import Flask, request
import telebot
import random
import re
import io  # Bellek üzerinden dosya yönetimi için

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- LUA OBFUSCATOR ENGINE (Düzeltilmiş) ---

def advanced_lua_obfuscate(code):
    # Sayıları matematiksel denklemlere çevir
    def math_obf(match):
        try:
            num = int(match.group(0))
            offset = random.randint(10, 100)
            return f"((0x{num+offset:x} - {offset}))"
        except:
            return match.group(0)

    # regex hatası düzeltildi: \b\d+\b kullanıldı
    code = re.sub(r'\b\d+\b', math_obf, code)

    # Değişkenleri karmaşıklaştır (Basit versiyon)
    var_map = {}
    def var_replacer(m):
        name = m.group(0)
        keywords = ["local", "function", "return", "end", "if", "then", "else", "for", "in", "do", "while", "nil", "true", "false"]
        if name not in keywords and len(name) > 1:
            if name not in var_map:
                var_map[name] = f"_0x{random.randint(0x100, 0xfff):x}"
            return var_map[name]
        return name

    code = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', var_replacer, code)
    
    header = "--[[ Encrypted by TeleKrak Titan V10 ]]\n"
    return header + code

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔥 ULTRA OBFUSCATE", "🔓 DECODE & CLEAN")
    bot.send_message(message.chat.id, "<b>LUA TITAN ENGINE V10</b>\nVercel Uyumlu Sürüm", parse_mode='HTML', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔥 ULTRA OBFUSCATE")
def mode_obf(message):
    msg = bot.reply_to(message, "Korumak istediğin LUA kodunu gönder (Metin olarak):")
    bot.register_next_step_handler(msg, process_obfuscation)

def process_obfuscation(message):
    try:
        protected_code = advanced_lua_obfuscate(message.text)
        
        # ÇÖZÜM: Dosyayı diske yazmak yerine belleğe (RAM) yazıyoruz
        bio = io.BytesIO()
        bio.name = "protected_script.tx5"
        bio.write(protected_code.encode('utf-8'))
        bio.seek(0) # İmleci dosya başına getir
        
        bot.send_document(message.chat.id, bio, caption="✅ Kodun başarıyla obfuscate edildi.")
    except Exception as e:
        bot.reply_to(message, f"Hata oluştu: {str(e)}")

@bot.message_handler(func=lambda m: m.text == "🔓 DECODE & CLEAN")
def mode_deobf(message):
    msg = bot.reply_to(message, "Temizlemek istediğin kodu gönder:")
    bot.register_next_step_handler(msg, process_deobfuscation)

def process_deobfuscation(message):
    # Basit temizlik işlemi
    code = message.text
    # Matematik çözücü ekleyebilirsin
    bot.send_message(message.chat.id, f"🔍 <b>Analiz Edildi:</b>\n\n<code>{code[:1000]}...</code>", parse_mode='HTML')

# Vercel entry point
@app.route('/webhook', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Hata', 403
