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
from constants import *
from lib.cache import cacheMessage

from lib.database.db import DatabaseConnection
from lib.database.model.user_model import User
from lib.database.model.cashflow_model import CashflowItem
from lib.database.model.wallet_model import Wallet
from lib.database.manager.user_manager import UserManager
from lib.database.manager.cashflow_manager import CashflowManager
from lib.database.manager.wallet_manager import WalletManager

from helpers.output_message import render_grouped_table

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

for log_name in ['httpx', 'telegram.bot', 'telegram.ext._application']:
    logging.getLogger(log_name).setLevel(logging.WARNING)

load_dotenv()


BOT_TOKEN = os.getenv('BOT_TELEGRAM_API')
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')

Db = DatabaseConnection()
user_manager = UserManager(Db)
cashflow_manager = CashflowManager(Db)
wallet_manager = WalletManager(Db)

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

async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f'Halo {user.username} ID: {user.id}')

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 Cek Saldo", "/tambah_wallet"],
        ["📊 Laporan", "⚙️ Pengaturan"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Silakan pilih menu:", reply_markup=reply_markup)

async def add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(f'Halo {user.username} masukkan nama wallet:')
    return WALLET_NAME

async def get_wallet_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['wallet_name'] = update.message.text

    await update.message.reply_text(f'Masukkan nominal awal wallet:')
    return WALLET_BALANCE

async def get_wallet_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    me = user_manager.get_user_by_telegram_id(user.id)

    wallet = Wallet(
        id=str(ObjectId()),
        userId=me.id,
        name= str(context.user_data['wallet_name']).strip(),
        description='',
        balance=float(update.message.text),
    )

    wallet_manager.insert_wallet(wallet)

    await update.message.reply_text("✅ Wallet berhasil ditambahkan!")
    return  ConversationHandler.END

async def cancel_add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operasi dibatalkan.")
    return ConversationHandler.END

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

    chat_log = memory.get_context(user_id)['messages']

    wallet_input = ''
    for item in chat_log:
        if item["role"] == "model":
            text = item["text"]
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            try:
                data = json.loads(text)
                for entry in data:
                    if "activityName" in entry:
                        wallet_input = entry['wallet']
            except Exception as e:
                logger.error("Gagal parse JSON:", e)

    wallet = wallet_manager.get_wallet_by_name(me.id, wallet_input)

    if query.data == 'confirmed_yes':

        total_walet_minus = 0
        for row in data:
            cashflow_item = CashflowItem(
                id=str(ObjectId()),
                userId=me.id,
                walletId=wallet.id,
                transactionDate=datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S'),
                activityName=row['activityName'],
                description='',
                categoryId=1,
                quantity=row['quantity'],
                unit=row['unit'],
                flowType=row['flowType'],
                price=row['price'],
                total=row['price'] * row['quantity'],
            )
            total_walet_minus += row['price'] * row['quantity']
            cashflow_manager.insert_cashflow(cashflow_item)

        wallet_manager.update_balance(wallet.id, wallet.balance - total_walet_minus)

        await query.edit_message_text('✅ Data telah disimpan. Terima kasih!')
    elif query.data == 'confirmed_no':
        await query.edit_message_text('🚫 Data dibatalkan. Silakan kirim ulang input.')

    memory.clear_user_data(user_id)
    return

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

    WALLET_NAME, WALLET_BALANCE = range(2)
    
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('tambah_wallet', add_wallet)],
        states={
            WALLET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wallet_name)],
            WALLET_BALANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wallet_balance)],
        },
        fallbacks=[CommandHandler('cancel', cancel_add_wallet)],
    ))

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('register', register))
    app.add_handler(CommandHandler('menu', menu))
    app.add_handler(CommandHandler('tambah_wallet', add_wallet))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(confirmation_callback_handler))

    app.run_polling()
