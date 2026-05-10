from flask import Flask, request
import telebot
import random
import re
import io
import base64
import zlib
import string

TOKEN = "8732882807:AAFAV7CPRlJbl5mKQt2GSV0YX-XQSBT-iyQ"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# =========================
# RANDOM NAME GENERATOR
# =========================

def rand_name():
    return "_" + "".join(random.choice("Il1O0") for _ in range(random.randint(20,40)))

# =========================
# STRING ENCRYPTION
# =========================

def encrypt_strings(code):
    pattern = r'(["\'])(.*?)(\1)'

    def repl(m):
        s = m.group(2)

        key = random.randint(1,255)

        enc = ",".join(str(ord(c)^key) for c in s)

        fn = rand_name()

        return f'(function() local {fn}={{{enc}}} local r="" for _,v in ipairs({fn}) do r=r..string.char(bit32.bxor(v,{key})) end return r end)()'

    return re.sub(pattern, repl, code)

# =========================
# NUMBER OBFUSCATION
# =========================

def obf_numbers(code):

    def repl(m):
        num = int(m.group())

        a = random.randint(100,500)
        b = num + a

        return f"(({b}-{a}))"

    return re.sub(r'\b\d+\b', repl, code)

# =========================
# VARIABLE RENAMER
# =========================

LUA_KEYWORDS = {
    "local","function","return","end","if","then","else",
    "for","while","do","repeat","until","nil","true","false",
    "and","or","not","break","in"
}

def rename_variables(code):

    varmap = {}

    def repl(m):

        name = m.group()

        if name in LUA_KEYWORDS:
            return name

        if len(name) <= 1:
            return name

        if name not in varmap:
            varmap[name] = rand_name()

        return varmap[name]

    return re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', repl, code)

# =========================
# JUNK CODE
# =========================

def junk():
    vars = [rand_name() for _ in range(5)]

    return f'''
local {vars[0]} = {random.randint(1000,9999)}
local {vars[1]} = "{base64.b64encode(str(random.random()).encode()).decode()}"
local function {vars[2]}()
    return {vars[0]} * 2
end
'''

# =========================
# WRAP LOADER
# =========================

def compile_loader(code):

    compressed = zlib.compress(code.encode())

    b64 = base64.b64encode(compressed).decode()

    loader = f'''
local data = "{b64}"

local raw = mime.unb64(data)

local decompressed = zlib.decompress(raw)

load(decompressed)()
'''

    return loader

# =========================
# MAIN ENGINE
# =========================

def ultra_obfuscate(code):

    code = encrypt_strings(code)

    code = obf_numbers(code)

    code = rename_variables(code)

    code = junk() + code + junk()

    header = f'''
--[[
  TITAN ULTRA ENGINE VX
  Anti Skid Protection
]]
'''

    return header + code

# =========================
# BOT
# =========================

@bot.message_handler(commands=['start'])
def start(message):

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add("🔥 OBFUSCATE")

    bot.send_message(
        message.chat.id,
        "ULTRA LUA OBFUSCATOR",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "🔥 OBFUSCATE")
def ask_code(message):

    msg = bot.reply_to(message, "LUA kodunu gönder")

    bot.register_next_step_handler(msg, process)

def process(message):

    try:

        result = ultra_obfuscate(message.text)

        bio = io.BytesIO()

        bio.name = "protected.txt"

        bio.write(result.encode())

        bio.seek(0)

        bot.send_document(message.chat.id, bio)

    except Exception as e:

        bot.reply_to(message, str(e))

# =========================
# WEBHOOK
# =========================

@app.route('/webhook', methods=['POST'])
def webhook():

    if request.headers.get('content-type') == 'application/json':

        json_string = request.get_data().decode('utf-8')

        update = telebot.types.Update.de_json(json_string)

        bot.process_new_updates([update])

        return '', 200

    return '403'
