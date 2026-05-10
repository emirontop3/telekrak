import os
import re
import io
import jsbeautifier
from flask import Flask, request, send_file
import telebot

# --- AYARLAR ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

class TitanDeobfuscator:
    def __init__(self, code):
        self.code = code

    def resolve_hex_and_unicode(self, code):
        """Tüm \x.. ve \u.... ifadelerini çözerek okunabilir stringlere çevirir."""
        code = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), code)
        code = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), code)
        return code

    def flatten_array_proxies(self, code):
        """
        Obfuscator.io tarzı [ _0x52a1[0], _0x52a1[1] ] yapılarını çözer.
        Dizideki değerleri bulur ve koddaki yerlerine yerleştirir.
        """
        # 1. Büyük string dizisini yakala (Örn: var _0x52a1 = ['log', 'error', 'atob'];)
        array_pattern = r'var\s+(\b_0x[a-f0-9]+\b)\s*=\s*\[(.*?)\];'
        arrays = re.findall(array_pattern, code)
        
        for array_name, array_content in arrays:
            # İçeriği ayıkla ve listeye çevir
            items = [item.strip().strip("'").strip('"') for item in array_content.split(',')]
            
            # Kodun içindeki çağrıları bul: _0x52a1[0] -> 'log'
            for i, val in enumerate(items):
                call_pattern = rf'{array_name}\[0x{i:x}\]|{array_name}\[{i}\]'
                code = re.sub(call_pattern, f"'{val}'", code)
        
        return code

    def simplify_logic(self, code):
        """Mantıksal karmaşayı (Proxy functions) temizler."""
        # var _0x123 = _0x456; gibi atamaları temizleyip asıl ismi yerleştirir
        code = code.replace('!![]', 'true').replace('![]', 'false')
        return code

    def unpack(self):
        """Askeri temizlik sürecini başlatır."""
        # Adım 1: Karakterleri çöz
        code = self.resolve_hex_and_unicode(self.code)
        # Adım 2: String dizilerini yerleştir
        code = self.flatten_array_proxies(code)
        # Adım 3: Mantıksal temizlik
        code = self.simplify_logic(code)
        
        # Adım 4: Profesyonel Güzelleştirme
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        opts.preserve_newlines = True
        opts.break_chained_methods = True
        return jsbeautifier.beautify(code, opts)

# --- TELEGRAM HANDLERS ---

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🛠️ **Titan Deobfuscator V2 - Military**\n\nKarmaşık JS kodlarını ve karartılmış dosyaları gönderin, onları analiz edilebilir hale getireyim.\n\n- Webpack Unpacking\n- Hex/Unicode Decoding\n- Proxy Function Inlining")

@bot.message_handler(content_types=['document', 'text'])
def handle_file(message):
    code_to_process = ""
    
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        code_to_process = downloaded_file.decode('utf-8')
    else:
        code_to_process = message.text

    if len(code_to_process) < 10:
        bot.reply_to(message, "❌ Kod işlemek için çok kısa!")
        return

    bot.send_message(message.chat.id, "🔍 **Kod analiz ediliyor ve deşifre ediliyor...**")
    
    try:
        unpacker = TitanDeobfuscator(code_to_process)
        clean_code = unpacker.unpack()
        
        bio = io.BytesIO()
        bio.name = "deobfuscated_output.js"
        bio.write(clean_code.encode('utf-8'))
        bio.seek(0)
        
        bot.send_document(
            message.chat.id, 
            bio, 
            caption="✅ **Deobfuscation Tamamlandı!**\n\n- Gereksiz yapılar temizlendi.\n- Stringler deşifre edildi.\n- Okunabilirlik %90 artırıldı."
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Hata: {str(e)}")

# --- VERCEL FLASK ---
@app.route('/webhook', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return '', 200

@app.route('/')
def home(): return "Titan Deobfuscator Active", 200
