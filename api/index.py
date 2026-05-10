import os
import re
import io
import random
import string
from flask import Flask, request, Response
import telebot

# --- AYARLAR ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

def generate_junk(size_kb=8):
    """Kodun içine gömmek için devasa anlamsız veriler üretir."""
    junk = ""
    for _ in range(size_kb):
        # Rastgele anlamsız JS fonksiyonları ve değişkenleri üretir
        func_name = "_0x" + "".join(random.choices(string.ascii_lowercase, k=10))
        var_name = "_0x" + "".join(random.choices(string.ascii_lowercase, k=10))
        val = random.randint(1000, 999999)
        junk += f"function {func_name}(){{ var {var_name} = {val}; return {var_name} * Math.random(); }}; \n"
        # Rastgele uzun yorum satırları (Base64 gibi görünür)
        fake_data = "".join(random.choices(string.ascii_letters + string.digits, k=100))
        junk += f"/* {fake_data} */ \n"
    return junk

def titan_v6_fatpacker(code: str) -> str:
    """300 Byte'lık kodu 10+ KB'lık devasa bir labirente dönüştürür."""
    if not code.strip(): return "/* No Code */"

    # 1. Asıl kodu şifrele
    key = random.randint(30, 250)
    encoded_payload = [ord(c) ^ key for c in code]
    
    # 2. Payload'u parçalara ayır ve çöp karakterlerle karıştır
    payload_str = ",".join(map(str, encoded_payload))
    
    # 3. Değişken isimlerini rastgele belirle
    v_main = "_0x" + "".join(random.choices(string.ascii_lowercase, k=12))
    v_junk_data = "_0x" + "".join(random.choices(string.ascii_lowercase, k=15))
    
    # 4. Şişirme (Bloating) işlemi
    junk_top = generate_junk(4) # Başa 4 KB çöp
    junk_mid = generate_junk(4) # Araya 4 KB çöp
    junk_bottom = generate_junk(2) # Sona 2 KB çöp

    # 5. Ana Şablon (Self-Executing + Junk Protection)
    js_template = f"""
{junk_top}
(function(){{
    var {v_junk_data} = "DEBUG_MODE_STRICT_PROTECTION";
    {junk_mid}
    var {v_main} = function(p, k){{
        var r = '';
        var arr = p.split(',');
        for(var i=0; i<arr.length; i++){{
            r += String.fromCharCode(parseInt(arr[i]) ^ k);
        }}
        return r;
    }};
    var _exec = Function;
    new _exec({v_main}('{payload_str}', {key}))();
}})();
{junk_bottom}
    """
    
    # Fazla boşlukları temizleyip tek satıra yaklaştır ama yorum satırlarını (çöpleri) koru
    return js_template.strip()

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🦾 **Titan V6 - FatPacker Aktif.**\n\nKüçük kodları devasa dosyalara dönüştürerek analizi imkansız kılıyorum. Kodunu gönder!")

@bot.message_handler(func=lambda m: True)
def handle_obfuscation(message):
    if len(message.text) < 2: return
    
    bot.send_chat_action(message.chat.id, 'upload_document')
    try:
        # Kodun 10 KB civarı olması sağlanıyor
        bloated_code = titan_v6_fatpacker(message.text)
        
        bio = io.BytesIO()
        bio.name = "titan_v6_heavy.js"
        bio.write(bloated_code.encode('utf-8'))
        bio.seek(0)
        
        bot.send_document(
            message.chat.id, 
            bio, 
            caption=f"📦 **İşlem Tamam!**\nDosya Boyutu: ~{len(bloated_code)/1024:.2f} KB\n\nKod artık hem şifreli hem de devasa!",
            parse_mode='Markdown'
        )
    except Exception as e:
        bot.reply_to(message, f"Hata: {str(e)}")

# --- VERCEL ALTYAPISI ---
@app.route('/')
def home(): return "Titan V6 Running", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
        return '', 200
    return 'Error', 403
