import os
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

# === Config ===
TOKEN = os.getenv("TELEGRAM_TOKEN")  # pon tu token en un env var de Render
PUBLIC_URL = os.getenv("https://botemb.onrender.com")  # ej: https://tu-servicio.onrender.com
SET_WEBHOOK = os.getenv("SET_WEBHOOK_ON_START", "0") == "1"
if not TOKEN:
    raise RuntimeError("Falta TELEGRAM_TOKEN en variables de entorno.")

bot = Bot(token=TOKEN)

# Dispatcher sin Updater (apto para webhook)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

# === Handlers ===
usuarios = {}

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    usuarios[chat_id] = {"step": 1}
    context.bot.send_message(chat_id=chat_id, text="👋 ¡Hola! ¿Cómo te llamas?")

def es_entero(txt: str) -> bool:
    try:
        int(txt); return True
    except: return False

def message_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text = (update.message.text or "").strip()

    if chat_id not in usuarios:
        context.bot.send_message(chat_id=chat_id, text="Escribe /start para comenzar.")
        return

    step = usuarios[chat_id].get("step", 1)

    if step == 1:
        usuarios[chat_id]["nombre"] = text
        usuarios[chat_id]["step"] = 2
        context.bot.send_message(chat_id=chat_id, text=f"Encantado, {text}. Dame un número entero.")
        return

    if step == 2:
        if not es_entero(text):
            context.bot.send_message(chat_id=chat_id, text="Solo enteros, intenta de nuevo.")
            return
        usuarios[chat_id]["valor"] = int(text)
        usuarios[chat_id]["step"] = 3
        context.bot.send_message(chat_id=chat_id, text="¡Listo! Guardé tu dato. Escribe /start para reiniciar.")
        return

def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("Comandos: /start")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_cmd))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

# === Flask app ===
app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "no data"}), 400
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return jsonify({"status": "ok"}), 200

# Configura el webhook al iniciar en Render
  if not BASE_URL:
        print("[init] BASE_URL no está definido; no se configurará webhook.")
        return
    url = f"{BASE_URL}/{TOKEN}"
    try:
        current = bot.get_webhook_info().url
        if current != url:
            bot.delete_webhook()
            bot.set_webhook(url=url)
            print(f"[init] Webhook configurado: {url}")
        else:
            print(f"[init] Webhook ya apuntaba a: {url}")
    except Exception as e:
        print(f"[init] No se pudo configurar el webhook: {e}")


if __name__ == "__main__":
    # Para correr localmente: export PUBLIC_URL="https://<ngrok>.ngrok.io"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
