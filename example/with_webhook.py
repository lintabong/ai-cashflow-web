import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import Dispatcher
from telegram.ext import CallbackContext
from dotenv import load_dotenv
import telegram

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TELEGRAM_API")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # misalnya https://yourdomain.com/webhook

app = FastAPI()

# Telegram App
tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Ini bot webhook 🌐")

tg_app.add_handler(CommandHandler("start", start))

# FastAPI route to receive updates
@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), tg_app.bot)
    await tg_app.process_update(update)
    return {"status": "ok"}

# Set webhook saat start
@app.on_event("startup")
async def set_webhook():
    await tg_app.bot.set_webhook(WEBHOOK_URL + "/webhook")
    print("Webhook diset di", WEBHOOK_URL + "/webhook")

'''uvicorn bot_webhook:app --host 0.0.0.0 --port 8000
'''