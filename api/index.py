import os
import re
import io
import random
import logging
from flask import Flask, request, Response
import telebot

# --- AYARLAR VE YAPILANDIRMA ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- ANA FONKSİYONLAR ---

def pro_js_obfuscator(code: str) -> str:
    """
    Titan V4 - XOR Payload Packer Algoritması
    Kodu kelime kelime değiştirmek yerine tamamen şifreler (XOR Encryption).
    Bu sayede kod %100 bozulmadan çalışır ama dışarıdan asla okunamaz.
    """
    code = code.strip()
    if not code: 
        return "/* HATA: Kod bulunamadı */"

    # 1. XOR Şifreleme Anahtarı (Her şifrelemede kodu bambaşka gösterir)
    xor_key = random.randint(10, 250)
    
    # 2. Orijinal kodu XOR ile şifreleyerek tamamen sayısal bir diziye çevir
    encoded_array = [str(ord(c) ^ xor_key) for c in code]
    array_str = ",".join(encoded_array)
    
    # 3. Şifre çözücü (Decoder) için rastgele karmaşık Hex değişken isimleri üret
    v_data      = f"_0x{random.getrandbits(16):x}"
    v_global    = f"_0x{random.getrandbits(16):x}"
    v_string    = f"_0x{random.getrandbits(16):x}"
    v_from_char = f"_0x{random.getrandbits(16):x}"
    v_eval      = f"_0x{random.getrandbits(16):x}"
    v_decoded   = f"_0x{random.getrandbits(16):x}"
    v_i         = f"_0x{random.getrandbits(16):x}"
    
    # 4. Şifre Çözücü JavaScript Çekirdeği
    # Kritik JS kelimeleri string hex olarak gizlendi ('\x75\x6e...' = undefined vb.)
    js_template = f"""
    var {v_data}=[{array_str}];
    var {v_global}=typeof window!=='\\x75\\x6e\\x64\\x65\\x66\\x69\\x6e\\x65\\x64'?window:typeof global!=='\\x75\\x6e\\x64\\x65\\x66\\x69\\x6e\\x65\\x64'?global:this;
    var {v_string}={v_global}['\\x53\\x74\\x72\\x69\\x6e\\x67'];
    var {v_from_char}={v_string}['\\x66\\x72\\x6f\\x6d\\x43\\x68\\x61\\x72\\x43\\x6f\\x64\\x65'];
    var {v_eval}={v_global}['\\x65\\x76\\x61\\x6c'];
    var {v_decoded}='';
    for(var {v_i}=0x0;{v_i}<{v_data}['\\x6c\\x65\\x6e\\x67\\x74\\x68'];{v_i}++){{
    {v_decoded}+={v_from_char}({v_data}[{v_i}]^{hex(xor_key)});
    }}
    {v_eval}({v_decoded});
    """
    
    # 5. Kodu tek satıra indir (Aradaki tüm boşlukları yok et)
    js_template = re.sub(r'\s+', ' ', js_template).strip()
    
    # 6. Analizi zorlaştırmak için Anonim fonksiyona çöp (junk) parametreler göm
    junk_id = f"0x{random.getrandbits(32):x}"
    junk_func_name = f"_0xXOR_{random.getrandbits(16):x}"
    
    final_code = (
        "/**\n"
        " * TeleKrak JS Titan V4 - EXTREME XOR ENCRYPTION\n"
        " * Warning: Protected against reversing & tampering.\n"
        " */\n"
        f";(function({junk_func_name}){{\n"
        f" {js_template}\n"
        f"}})( {junk_id} );"
    )
    return final_code

# --- TELEGRAM BOT KOMUTLARI ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: telebot.types.Message):
    welcome_text = (
        "🚀 *TeleKrak JS Titan V4*\n\n"
        "Kodunu XOR Payload Packer ile %100 güvenli şifreliyor ve çalışma sistemini kesinlikle bozmuyorum.\n\n"
        "👉 *Obfuscate etmek istediğin kodu gönder!*"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_obfuscation(message: telebot.types.Message):
    if len(message.text.strip()) < 2:
        bot.reply_to(message, "❌ *Hata:* Kod çok kısa!", parse_mode='Markdown')
        return

    bot.send_chat_action(message.chat.id, 'upload_document')
    
    try:
        # Karartma işlemini yap (XOR Engine)
        obfuscated_code = pro_js_obfuscator(message.text)
        
        # Vercel RAM üzerinden sanal dosya oluşturma
        bio = io.BytesIO()
        bio.name = "telekrak_titan_v4.js"
        bio.write(obfuscated_code.encode('utf-8'))
        bio.seek(0)
        
        caption_text = (
            "✅ <b>Şifreleme Başarılı!</b>\n\n"
            "Kod <i>Titan V4 XOR Packer</i> ile kilitlendi. Sisteminin bozulma ihtimali ortadan kaldırıldı."
        )
        
        bot.send_document(
            message.chat.id, 
            bio, 
            caption=caption_text,
            parse_mode='HTML'
        )
        logger.info(f"V4 Şifreleme Tamamlandı - Chat ID: {message.chat.id}")
        
    except Exception as e:
        logger.error(f"İşlem Hatası: {str(e)}")
        bot.reply_to(message, f"❌ <b>Sistem Hatası:</b>\n<code>{str(e)}</code>", parse_mode='HTML')

# --- VERCEL FLASK WEBHOOK AYARLARI ---

@app.route('/', methods=['GET'])
def home():
    return "🚀 TeleKrak Titan V4 (XOR Engine) is Running Active!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return Response('OK', status=200)
    
    return Response('Forbidden', status=403)
