import telebot
import random
import base64
import re
from flask import Flask, request

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

def titan_obfuscate(code):
    # --- 1. STRING HAVUZU OLUŞTURMA ---
    strings = []
    def collect_strings(match):
        s = match.group(1) or match.group(2)
        if s and len(s) > 1:
            encoded = base64.b64encode(s.encode()).decode()
            strings.append(encoded)
            return f"_0x_tk[{len(strings)-1}]"
        return match.group(0)

    # Kod içindeki stringleri topla ve Base64 referansıyla değiştir
    code = re.sub(r"'(.*?)'|\"(.*?)\"", collect_strings, code)

    # --- 2. DEĞİŞKEN KARARTMA (HEXADECIMAL) ---
    var_map = {}
    def rename_logic(match):
        word = match.group(0)
        keywords = ["var", "let", "const", "function", "return", "if", "else", "for", "while", "true", "false", "console", "window", "document"]
        if word not in keywords and len(word) > 2:
            if word not in var_map:
                var_map[word] = f"_0x{random.getrandbits(16):x}"
            return var_map[word]
        return word

    code = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', rename_logic, code)

    # --- 3. JUNK CODE (ÇÖP KOD) EKLEME ---
    junk = [
        f"const _0x_junk{random.randint(1,999)} = () => {{ return '{random.getrandbits(8)}'; }};",
        f"if (Math.random() > 1) {{ console.log('unreachable'); }}",
    ]
    
    # --- 4. SON MONTAJ (DICTIONARY + DECODER) ---
    # Kodun başına stringleri çözen bir fonksiyon ekliyoruz
    dictionary_js = f"const _0x_tk = [{','.join([f'atob(\"{s}\")' for s in strings])}];\n"
    
    final_code = f"/* TELEKRAK TITAN V2 - ANTI-TAMPER ACTIVE */\n{dictionary_js}\n{random.choice(junk)}\n{code}\n{random.choice(junk)}"
    return final_code

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 **JS TITAN V2 AKTİF**\n\nKodunu gönder, onu kimsenin çözemeyeceği bir hale getireyim.")

@bot.message_handler(func=lambda m: True)
def process(message):
    if len(message.text) < 10:
        bot.reply_to(message, "⚠️ Bu kod çok kısa, daha detaylı bir şeyler gönder!")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    try:
        result = titan_obfuscate(message.text)
        # Eğer kod çok uzunsa dosya olarak gönder (Vercel RAM dostu)
        if len(result) > 3000:
            import io
            bio = io.BytesIO()
            bio.name = "obfuscated.js"
            bio.write(result.encode())
            bio.seek(0)
            bot.send_document(message.chat.id, bio, caption="✅ Kodun Titan V2 ile mühürlendi.")
        else:
            bot.send_message(message.chat.id, f"🔐 **Şifrelenmiş Kod:**\n\n<code>{result}</code>", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Kritik Hata: {str(e)}")

# --- VERCEL CONFIG ---
@app.route('/')
def home(): return "Titan Engine Online", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        bot.process_new_updates([telebot.types.Update.de_json(json_string)])
        return '', 200
    return 'Error', 403
