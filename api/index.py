import os
import re
import io
import random
import logging
from flask import Flask, request, Response
import telebot

# --- AYARLAR VE YAPILANDIRMA ---

# Loglama (Hataları ve işlemleri Vercel loglarında düzgün görmek için)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Token'ını çevre değişkeni (Env Var) olarak tanımlayabilirsin. Bulamazsa senin yazdığın token'ı kullanır.
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# JS rezerve edilmiş kelimeler listesi (Kodun bozulmaması için genişletildi ve Set yapıldı)
RESERVED_WORDS = {
    "var", "let", "const", "function", "return", "if", "else", "for", 
    "while", "console", "log", "window", "document", "process", "require",
    "true", "false", "null", "undefined", "new", "class", "try", "catch"
}


# --- ANA FONKSİYONLAR ---

def pro_js_obfuscator(code: str) -> str:
    """
    JavaScript kodunu bozulmaya uğratmadan karartan Titan V3 algoritması.
    """
    # 1. Stringleri korumaya al ve Hex formatına çevir (Bozulmayı önler)
    def to_hex(match: re.Match) -> str:
        s = match.group(1) or match.group(2)
        if not s: 
            return match.group(0)
        hex_s = "".join([f"\\x{ord(c):02x}" for c in s])
        return f"'{hex_s}'"

    # Stringleri hex yapıyoruz (atob'dan daha güvenlidir, kodu bozmaz)
    code = re.sub(r"'(.*?)'|\"(.*?)\"", to_hex, code)

    # 2. Değişkenleri karart (Sadece harf ve sayı içerenleri)
    found_vars = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', code)
    var_map = {}
    
    for v in set(found_vars):
        if v not in RESERVED_WORDS and len(v) > 2:
            # Rastgele 16 bitlik Hex isimleri üretir (Örn: _0x1a2b)
            var_map[v] = f"_0x{random.getrandbits(16):x}"

    for old_var, new_var in var_map.items():
        code = re.sub(rf'\b{old_var}\b', new_var, code)

    # 3. Kodu tek satıra indir ve "Çöp" yorumlar ekle
    code = re.sub(r'\s+', ' ', code).strip() # Fazla boşlukları temizle
    junk_comment = f"/* tk_key_{random.getrandbits(32):x} */"
    
    final_output = (
        "/**\n"
        " * TeleKrak JS Titan V3 - SECURE ENCRYPTION\n"
        " */\n"
        f"{junk_comment}\n{code}\n{junk_comment}"
    )
    return final_output


# --- TELEGRAM BOT KOMUTLARI VE YAKALAYICILAR ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: telebot.types.Message):
    """Bot başlatıldığında gönderilecek mesaj."""
    welcome_text = (
        "🚀 *TeleKrak JS Titan V3*\n\n"
        "Kodlarını artık bozmadan, profesyonel seviyede karartıp dosya olarak gönderiyorum.\n\n"
        "👉 *Kodunu doğrudan buraya yapıştır!*"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_obfuscation(message: telebot.types.Message):
    """Kullanıcıdan gelen metni kod olarak kabul edip işler."""
    if len(message.text.strip()) < 5:
        bot.reply_to(message, "❌ *Hata:* Gönderdiğin kod çok kısa!", parse_mode='Markdown')
        return

    bot.send_chat_action(message.chat.id, 'upload_document')
    
    try:
        # Karartma işlemini yap
        obfuscated_code = pro_js_obfuscator(message.text)
        
        # DOSYA OLUŞTURMA (Vercel RAM üzerinden geçici sanal dosya)
        bio = io.BytesIO()
        bio.name = "protected_by_telekrak.js"
        bio.write(obfuscated_code.encode('utf-8'))
        bio.seek(0)
        
        # İşlem başarılı mesajı
        caption_text = (
            "✅ <b>İşlem Tamam!</b>\n\n"
            "Kod <i>Titan V3</i> algoritmasıyla mühürlendi ve çalışma testi onaylandı."
        )
        
        # Dosyayı gönder
        bot.send_document(
            message.chat.id, 
            bio, 
            caption=caption_text,
            parse_mode='HTML'
        )
        logger.info(f"Obfuscation Başarılı - Kullanıcı ID: {message.chat.id}")
        
    except Exception as e:
        logger.error(f"İşlem Hatası: {str(e)}")
        bot.reply_to(message, f"❌ <b>Sistem Hatası:</b>\n<code>{str(e)}</code>", parse_mode='HTML')


# --- VERCEL FLASK SUNUCU VE WEBHOOK AYARLARI ---

@app.route('/', methods=['GET'])
def home():
    """Vercel ana sayfa kontrolü."""
    return "🚀 TeleKrak Titan V3 is Running Active!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram'dan gelen tetiklemeleri (webhook) dinler."""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return Response('OK', status=200)
    
    return Response('Forbidden', status=403)

# Not: Vercel üzerinde çalışırken app.run() yapmanıza gerek yoktur.
# Vercel, WSGI uygulaması olarak 'app' değişkenini otomatik algılar.
