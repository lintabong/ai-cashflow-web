import os
from telegram import Update, ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from google import genai
from google.genai import types
from dotenv import load_dotenv
from datetime import date, datetime
from bson import ObjectId
import json
import re
import logging
import random
import string
from constants import *
from lib.cache import cacheMessage

from lib.database.db import DatabaseConnection
from lib.database.model.user_model import User
from lib.database.model.cashflow_model import CashflowItem
from lib.database.manager.user_manager import UserManager
from lib.database.manager.cashflow_manager import CashflowManager

from helpers.output_message import render_grouped_table

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram.bot').setLevel(logging.WARNING)
logging.getLogger('telegram.ext._application').setLevel(logging.WARNING)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TELEGRAM_API')
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')

def generate_random_id(length=10):
    """Generate random alphanumeric ID dengan panjang tertentu"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

Db = DatabaseConnection()
user_manager = UserManager(Db)
cashflow_manager = CashflowManager(Db)

memory = cacheMessage()

client = genai.Client()

def model_chat(instruction, history=None):
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
                system_instruction=instruction
            ),
        history=history
    )

    return chat

today = date.today().isoformat()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        f'Halo {user.username} ID: {user.id}'
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 Cek Saldo", "➕ Tambah Transaksi"],
        ["📊 Laporan", "⚙️ Pengaturan"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Silakan pilih menu:", reply_markup=reply_markup)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    telegram_id = user.id
    username = user.username
    first_name = user.first_name or ''
    last_name = user.last_name or ''
    name = f'{first_name} {last_name}'.strip()

    me = user_manager.get_user_by_telegram_id(telegram_id)

    if me:
        await update.message.reply_text(f'⚠️ Kamu sudah terdaftar, {first_name}')
        return

    user = User(
        id=str(ObjectId()),
        name=name,
        telegramId=telegram_id,
        password='',
        username=username,
        email='',
        phone='',
        balance=0.00,
        isActive=True
    )
    
    user_manager.insert_user(user)

    await update.message.reply_text(f'✅ Pendaftaran berhasil, {first_name}!')

# Handler untuk pesan teks biasa
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    message = update.message.text.strip()

    me = user_manager.get_user_by_telegram_id(telegram_id)

    if not me:
        await update.message.reply_text('Kamu belum terdaftar. Ketik /register')
        return
    
    user_id = me.id

    chat = model_chat(GEMINI_SYSTEM_INSTRUCTION_BASE)
    response = chat.send_message(message)
    parsed_data = json.loads(re.sub(r'^```json\s*|\s*```$', '', response.text))
    parsed_data['message'] = message

    logger.info(f'{telegram_id} || {parsed_data["intent"]} || send: {message}')

    if parsed_data['intent'] == 'CATAT_TRANSAKSI':
        response_text = transaction(user_id, parsed_data)
        response_text = json.loads(re.sub(r'^```json\s*|\s*```$', '', response_text))
        response_text = render_grouped_table(response_text)

        keyboard = [
            [
                InlineKeyboardButton('✅ Ya', callback_data='confirmed_yes'),
                InlineKeyboardButton('❌ Tidak', callback_data='confirmed_no'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(response_text, parse_mode='Markdown')
        await update.message.reply_text('Apakah data transaksi ini benar?', reply_markup=reply_markup)
        return

    elif parsed_data['intent'] == 'TANYA_SALDO':
        await update.message.reply_text(f'Saldo kamu Rp. {me.balance}')
        return
    
    elif parsed_data['intent'] == 'LAINNYA':
        response_text = normal(user_id, parsed_data)
        await update.message.reply_text(response_text)
        return

    await update.message.reply_text(parsed_data['intent'])
    return

async def confirmation_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id

    me = user_manager.get_user_by_telegram_id(telegram_id)
    user_id = me.id

    print(memory.get_context(user_id))

    memory.clear_user_data(user_id)

    if query.data == 'confirmed_yes':
        await query.edit_message_text('✅ Data telah disimpan. Terima kasih!')
    elif query.data == 'confirmed_no':
        await query.edit_message_text('🚫 Data dibatalkan. Silakan kirim ulang input.')

def transaction(user_id, parsed_data):
    history = []
    context = memory.get_context(user_id)
    if context is not None and 'messages' in context:
        if len(context['messages']) >= 2:
            for row in context['messages']:
                row = types.Content(role=row['role'], parts=[types.Part.from_text(text=row['text'])])
                history.append(row)

    chat = model_chat(
        GEMINI_SYSTEM_INSTRUCTION_PARSE.replace('{d}', str(datetime.now().replace(microsecond=0))), 
        history if len(history) > 0 else None
    )

    memory.save_message(user_id, parsed_data['message'], 'user')
    response = chat.send_message(parsed_data['message'])
    memory.save_message(user_id, response.text, 'model')

    return response.text

def normal(user_id, parsed_data):
    history = []
    context = memory.get_context(user_id)
    if context is not None and 'messages' in context:
        if len(context['messages']) >= 2:
            for row in context['messages']:
                row = types.Content(role=row['role'], parts=[types.Part.from_text(text=row['text'])])
                history.append(row)

    chat = model_chat(GEMINI_SYSTEM_INSTRUCTION_NORMAL, history if len(history) > 0 else None)

    memory.save_message(user_id, parsed_data['message'], 'user')
    response = chat.send_message(parsed_data['message'])
    memory.save_message(user_id, response.text, 'model')

    return response.text


if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('register', register))
    # app.add_handler(CommandHandler('menu', menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(confirmation_callback_handler))

    app.run_polling()
