from flask import Flask, request
import telebot
import speech_recognition as sr
from pydub import AudioSegment
import io
import requests

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

def voice_to_text(file_url):
    # 1. Ses dosyasını Telegram sunucusundan indir
    response = requests.get(file_url)
    audio_data = io.BytesIO(response.content)
    
    # 2. OGG/Opus formatını WAV formatına çevir (SpeechRecognition için)
    # Not: Vercel'de ffmpeg yüklü olmalıdır, pydub bunu kullanır.
    audio = AudioSegment.from_file(audio_data, format="ogg")
    wav_data = io.BytesIO()
    audio.export(wav_data, format="wav")
    wav_data.seek(0)
    
    # 3. Google Speech Recognition ile metne çevir
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_data) as source:
        audio_content = recognizer.record(source)
        try:
            # Türkçe dil desteği ile çeviriyoruz
            text = recognizer.recognize_google(audio_content, language="tr-TR")
            return text
        except sr.UnknownValueError:
            return "Ses anlaşılamadı."
        except sr.RequestError:
            return "Servis şu an çalışmıyor."

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.reply_to(message, "Ses mesajını aldım, metne çeviriyorum... 🎙️")
    
    # Dosya bilgilerini al
    file_info = bot.get_file(message.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    
    try:
        # Dönüştürme işlemini başlat
        translated_text = voice_to_text(file_url)
        bot.send_message(message.chat.id, f"📝 **Metin:**\n\n{translated_text}")
    except Exception as e:
        bot.reply_to(message, f"Bir hata oluştu: {str(e)}\n(Not: Vercel üzerinde ffmpeg kütüphanesi eksik olabilir.)")

@app.route('/webhook', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Hata', 403
