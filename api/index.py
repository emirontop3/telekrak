from flask import Flask, request
import telebot
import re
import base64

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- LUA ÖZEL MODÜLLERİ ---

def lua_deobfuscator(code):
    """VM tabanlı olmayan, yaygın karartmaları temizler."""
    # 1. Hex/Byte Escape Çözücü (\108\117\97 -> lua)
    def byte_match(m):
        return chr(int(m.group(1)))
    code = re.sub(r'\\(\d{1,3})', byte_match, code)
    
    # 2. String Concatenation Temizliği ("a" .. "b" -> "ab")
    code = re.sub(r'"\s*\.\.\s*"', '', code)
    
    # 3. Gereksiz Boşluk ve Yorum Satırlarını Temizleme
    code = re.sub(r'--\[\[.*?\]\]', '', code, flags=re.DOTALL)
    
    # 4. Yaygın Loadstring/Base64 Patternlerini Çözme
    if "base64" in code.lower() or "b64" in code.lower():
        b64_matches = re.findall(r'"([A-Za-z0-9+/=]{20,})"', code)
        for match in b64_matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                code = code.replace(match, f" [DECODED: {decoded}] ")
            except: pass
            
    return code.strip()

def lua_obfuscator(code):
    """Kodu temel düzeyde karartır (String hexing & Junk code)."""
    # Karakterleri \ddd formatına çevirir
    obfuscated = "".join(f"\\{ord(c):03d}" for c in code)
    junk = "--[[ Obfuscated by TeleKrak Master ]]\n"
    return f'{junk}loadstring("{obfuscated}")()'

# --- BOT MANTIĞI ---

user_modes = {} # Kullanıcıların hangi modda olduğunu tutar

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔍 Deobfuscate", "🔐 Obfuscate")
    bot.send_message(message.chat.id, "Lua Master Bot'a hoş geldin. Bir mod seç:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["🔍 Deobfuscate", "🔐 Obfuscate"])
def set_mode(message):
    user_modes[message.chat.id] = message.text
    bot.reply_to(message, f"Mod ayarlandı: {message.text}. Şimdi Lua kodunu gönder.")

@bot.message_handler(func=lambda message: True)
def handle_lua(message):
    mode = user_modes.get(message.chat.id, "🔍 Deobfuscate")
    code = message.text
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    if mode == "🔍 Deobfuscate":
        result = lua_deobfuscator(code)
        bot.send_message(message.chat.id, f"📝 **Çözülen Kod:**\n\n<code>{result}</code>", parse_mode='HTML')
    else:
        result = lua_obfuscator(code)
        bot.send_message(message.chat.id, f"🔐 **Karartılan Kod:**\n\n<code>{result}</code>", parse_mode='HTML')

@app.route('/webhook', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Hata', 403
