from flask import Flask, request
import telebot
import random
import re
import base64

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- ULTRA LUA OBFUSCATOR ENGINE ---

def advanced_lua_obfuscate(code):
    # 1. Stringleri Byte Tablosuna Çevir ve Gizle
    def encode_string(s):
        bytes_list = [str(ord(c)) for c in s]
        return "({(function() local t={ " + ",".join(bytes_list) + " } local s='' for i=1,#t do s=s..string.char(t[i]) end return s end)()})"

    # 2. Sayıları Matematiksel Denklemlere Çevir (Örn: 10 -> (0x14 / 2))
    def math_obf(match):
        num = int(match.group(0))
        offset = random.randint(1, 100)
        return f"((0x{num+offset:x} - {offset}))"

    # Sayıları bul ve değiştir
    # Hatalı olan satır:
    # code = re.sub(r'\b\countd+\b', math_obf, code)

    # Doğru olan (sadece sayıları yakalar):
    code = re.sub(r'\b\d+\b', math_obf, code)

    # 3. Değişken İsimlerini Karmaşıklaştır
    var_map = {}
    def var_replacer(m):
        var_name = m.group(0)
        if var_name not in ["local", "function", "return", "end", "if", "then", "else", "for", "in", "do", "while"]:
            if var_name not in var_map:
                var_map[var_name] = f"_0x{random.randint(0x1000, 0x9999):x}"
            return var_map[var_name]
        return var_name

    # Basit bir regex ile yerel değişkenleri yakala (Daha karmaşık hale getirilebilir)
    code = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', var_replacer, code)

    # 4. Junk Code (Çöp Kod) Ekleme
    junk = [
        f"if (0x{random.randint(1,100):x} == 0x{random.randint(101,200):x}) then print('error') end",
        f"local _0x999 = math.sin({random.random()})",
    ]
    
    header = "--[[ Encrypted by TeleKrak Master V10 ]]\n"
    footer = f"\n-- {random.getrandbits(32)}"
    
    # Kodu string obfuscation ile birleştir
    final_code = f"{header}{random.choice(junk)}\n{code}\n{random.choice(junk)}{footer}"
    return final_code

# --- DEOBFUSCATOR (LOGIC RECOVERY) ---

def advanced_lua_deobfuscate(code):
    # 1. Matematiksel işlemleri basitleştir (Statik analiz)
    # Bu kısım basit (0x.. - ..) yapılarını çözer
    def math_solve(m):
        try:
            val = eval(m.group(0).replace("0x", "0x"))
            return str(int(val))
        except: return m.group(0)

    code = re.sub(r'\(\(0x[0-9a-fA-F]+ \- \d+\)\)', math_solve, code)
    
    # 2. Gereksiz yorumları ve boşlukları temizle
    code = re.sub(r'--\[\[.*?\]\]', '', code, flags=re.DOTALL)
    code = re.sub(r'--.*', '', code)
    
    return code.strip()

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔥 ULTRA OBFUSCATE", "🔓 DECODE & CLEAN")
    bot.send_message(message.chat.id, "<b>LUA TITAN ENGINE V10</b>\nKodunu bir üst seviyeye taşı.", parse_mode='HTML', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔥 ULTRA OBFUSCATE")
def mode_obf(message):
    msg = bot.reply_to(message, "Lütfen korumak istediğin LUA kodunu gönder:")
    bot.register_next_step_handler(msg, process_obfuscation)

def process_obfuscation(message):
    try:
        protected = advanced_lua_obfuscate(message.text)
        # Kodu dosya olarak gönder (Daha profesyonel durur)
        with open("obfuscated.lua", "w") as f:
            f.write(protected)
        with open("obfuscated.lua", "rb") as f:
            bot.send_document(message.chat.id, f, caption="✅ Kodun Titan Engine ile korundu.")
    except Exception as e:
        bot.reply_to(message, f"Hata: {e}")

@bot.message_handler(func=lambda m: m.text == "🔓 DECODE & CLEAN")
def mode_deobf(message):
    msg = bot.reply_to(message, "Çözmek istediğin kodu gönder:")
    bot.register_next_step_handler(msg, process_deobfuscation)

def process_deobfuscation(message):
    clean = advanced_lua_deobfuscate(message.text)
    bot.send_message(message.chat.id, f"🔍 <b>Temizlenen Mantık:</b>\n\n<code>{clean}</code>", parse_mode='HTML')

# Vercel Webhook API
@app.route('/webhook', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Hata', 403
