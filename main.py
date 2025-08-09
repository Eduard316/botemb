# main.py
import os
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

# === Config ===
TOKEN = os.getenv("TELEGRAM_TOKEN")                # En Render
BASE_URL = os.getenv("BASE_URL")                   # ej: https://botemb.onrender.com

if not TOKEN:
    raise RuntimeError("Falta TELEGRAM_TOKEN en variables de entorno.")
if not BASE_URL:
    raise RuntimeError("Falta BASE_URL en variables de entorno.")

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

# === Handlers ===
usuarios = {}

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    usuarios[chat_id] = {"step": 1}
    context.bot.send_message(chat_id=chat_id, text="👋 ¡Hola! ¿Cómo te llamas?")

def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("Comandos: /start")

def es_entero(txt: str) -> bool:
    try:
        int(txt); return True
    except:
        return False

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

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_cmd))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

# === Flask app ===
app = Flask(__name__)

@app.get("/")
def health():
    return jsonify(status="ok", service="telegram-bot", webhook=f"/webhook/{TOKEN}")

@app.post(f"/webhook/{TOKEN}")
def telegram_webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "no data"}), 400
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return jsonify({"status": "ok"}), 200

def ensure_webhook():
    """Configura/valida el webhook siempre al iniciar."""
    url = f"{BASE_URL}/webhook/{TOKEN}"  # Debe coincidir con la ruta Flask
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
    ensure_webhook()  # <-- siempre
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
