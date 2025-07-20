import os
import json
import re
import logging
from datetime import datetime
from bson import ObjectId

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ContextTypes, filters, ConversationHandler
)
from google import genai
from google.genai import types
from dotenv import load_dotenv

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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress verbose logs
for log_name in ['httpx', 'telegram.bot', 'telegram.ext._application']:
    logging.getLogger(log_name).setLevel(logging.WARNING)

load_dotenv()

class TelegramFinanceBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TELEGRAM_API')
        os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
        
        # Initialize database and managers
        self.db = DatabaseConnection()
        self.user_manager = UserManager(self.db)
        self.cashflow_manager = CashflowManager(self.db)
        self.wallet_manager = WalletManager(self.db)
        
        # Initialize cache and AI client
        self.memory = cacheMessage()
        self.client = genai.Client()
        
        # Conversation states
        self.WALLET_NAME, self.WALLET_BALANCE = range(2)
        
    def create_chat_model(self, instruction, history=None):
        """Create a chat model with given instruction and history."""
        return self.client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(system_instruction=instruction),
            history=history
        )

    def parse_json_response(self, text):
        """Parse JSON from Gemini response, handling code blocks."""
        return json.loads(re.sub(r'^```json\s*|\s*```$', '', text))

    def get_or_create_user(self, telegram_user):
        """Get existing user or return None if not registered."""
        return self.user_manager.get_user_by_telegram_id(telegram_user.id)

    def build_history_from_memory(self, user_id):
        """Build conversation history from memory cache."""
        history = []
        context = self.memory.get_context(user_id)
        
        if context and 'messages' in context and len(context['messages']) >= 2:
            for message in context['messages']:
                content = types.Content(
                    role=message['role'], 
                    parts=[types.Part.from_text(text=message['text'])]
                )
                history.append(content)
        
        return history if history else None

    # Command handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(f'Halo {user.username} ID: {user.id}')

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            ["💰 Cek Saldo", "/tambah_wallet"],
            ["📊 Laporan", "⚙️ Pengaturan"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Silakan pilih menu:", reply_markup=reply_markup)

    async def register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        
        # Check if user already exists
        if self.get_or_create_user(telegram_user):
            await update.message.reply_text(f'⚠️ Kamu sudah terdaftar, {telegram_user.first_name}')
            return

        # Create new user
        user = User(
            id=str(ObjectId()),
            name=f'{telegram_user.first_name}'.strip(),
            telegramId=telegram_user.id,
            password='',
            username=telegram_user.username,
            email='',
            phone='',
        )
        
        self.user_manager.insert_user(user)
        await update.message.reply_text(f'✅ Pendaftaran berhasil, {telegram_user.first_name}!')

    # Wallet conversation handlers
    async def add_wallet_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(f'Halo {user.username} masukkan nama wallet:')
        return self.WALLET_NAME

    async def get_wallet_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['wallet_name'] = update.message.text.strip()
        await update.message.reply_text('Masukkan nominal awal wallet:')
        return self.WALLET_BALANCE

    async def get_wallet_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        user = self.get_or_create_user(telegram_user)
        
        if not user:
            await update.message.reply_text('Kamu belum terdaftar. Ketik /register')
            return ConversationHandler.END

        try:
            balance = float(update.message.text)
            wallet = Wallet(
                id=str(ObjectId()),
                userId=user.id,
                name=context.user_data['wallet_name'],
                description='',
                balance=balance,
            )
            
            self.wallet_manager.insert_wallet(wallet)
            await update.message.reply_text("✅ Wallet berhasil ditambahkan!")
            
        except ValueError:
            await update.message.reply_text("❌ Nominal tidak valid. Masukkan angka yang benar.")
            return self.WALLET_BALANCE
            
        return ConversationHandler.END

    async def cancel_add_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Operasi dibatalkan.")
        return ConversationHandler.END

    # Text message handler
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        message = update.message.text.strip()
        
        user = self.get_or_create_user(telegram_user)
        if not user:
            await update.message.reply_text('Kamu belum terdaftar. Ketik /register')
            return

        try:
            # Process message with AI
            chat = self.create_chat_model(GEMINI_SYSTEM_INSTRUCTION_BASE)
            response = chat.send_message(message)
            parsed_data = self.parse_json_response(response.text)
            parsed_data['message'] = message

            logger.info(f'{telegram_user.id} || {parsed_data["intent"]} || send: {message}')

            # Handle different intents
            if parsed_data['intent'] == 'CATAT_TRANSAKSI':
                await self.handle_transaction_intent(update, user.id, parsed_data)
                
            elif parsed_data['intent'] == 'TANYA_SALDO':
                await update.message.reply_text(f'Saldo kamu Rp. {user.balance}')
                
            elif parsed_data['intent'] == 'LAINNYA':
                response_text = self.handle_normal_conversation(user.id, parsed_data)
                await update.message.reply_text(response_text)
                
            else:
                await update.message.reply_text(f"Intent tidak dikenali: {parsed_data['intent']}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat memproses pesan Anda.")

    async def handle_transaction_intent(self, update, user_id, parsed_data):
        """Handle transaction recording intent."""
        try:
            response_text = self.process_transaction_data(user_id, parsed_data)
            response_data = self.parse_json_response(response_text)
            formatted_response = render_grouped_table(response_data)

            # Create confirmation buttons
            keyboard = [
                [
                    InlineKeyboardButton('✅ Ya', callback_data='confirmed_yes'),
                    InlineKeyboardButton('❌ Tidak', callback_data='confirmed_no'),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(formatted_response, parse_mode='Markdown')
            await update.message.reply_text('Apakah data transaksi ini benar?', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error handling transaction intent: {e}")
            await update.message.reply_text("❌ Gagal memproses data transaksi.")

    def process_transaction_data(self, user_id, parsed_data):
        """Process transaction data using AI."""
        history = self.build_history_from_memory(user_id)
        
        instruction = GEMINI_SYSTEM_INSTRUCTION_PARSE.replace(
            '{d}', str(datetime.now().replace(microsecond=0))
        )
        chat = self.create_chat_model(instruction, history)

        self.memory.save_message(user_id, parsed_data['message'], 'user')
        response = chat.send_message(parsed_data['message'])
        self.memory.save_message(user_id, response.text, 'model')

        return response.text

    def handle_normal_conversation(self, user_id, parsed_data):
        """Handle normal conversation using AI."""
        history = self.build_history_from_memory(user_id)
        chat = self.create_chat_model(GEMINI_SYSTEM_INSTRUCTION_NORMAL, history)

        self.memory.save_message(user_id, parsed_data['message'], 'user')
        response = chat.send_message(parsed_data['message'])
        self.memory.save_message(user_id, response.text, 'model')

        return response.text

    # Callback handler for confirmations
    async def handle_confirmation_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        telegram_user = update.effective_user
        user = self.get_or_create_user(telegram_user)
        
        if not user:
            await query.edit_message_text('❌ User tidak ditemukan.')
            return

        try:
            if query.data == 'confirmed_yes':
                await self.save_confirmed_transaction(query, user)
            elif query.data == 'confirmed_no':
                await query.edit_message_text('🚫 Data dibatalkan. Silakan kirim ulang input.')
                
            self.memory.clear_user_data(user.id)
            
        except Exception as e:
            logger.error(f"Error handling confirmation: {e}")
            await query.edit_message_text('❌ Terjadi kesalahan saat memproses konfirmasi.')

    async def save_confirmed_transaction(self, query, user):
        """Save confirmed transaction to database."""
        chat_log = self.memory.get_context(user.id)['messages']
        
        # Extract wallet information from chat log
        wallet_name = self.extract_wallet_from_chat_log(chat_log)
        wallet = self.wallet_manager.get_wallet_by_name(user.id, wallet_name)
        
        if not wallet:
            await query.edit_message_text('❌ Wallet tidak ditemukan.')
            return

        # Process and save transactions
        transaction_data = self.extract_transaction_data_from_chat_log(chat_log)
        total_amount = 0
        
        for transaction in transaction_data:
            cashflow_item = CashflowItem(
                id=str(ObjectId()),
                userId=user.id,
                walletId=wallet.id,
                transactionDate=datetime.strptime(transaction['date'], '%Y-%m-%d %H:%M:%S'),
                activityName=transaction['activityName'],
                description='',
                categoryId=1,
                quantity=transaction['quantity'],
                unit=transaction['unit'],
                flowType=transaction['flowType'],
                price=transaction['price'],
                total=transaction['price'] * transaction['quantity'],
            )
            
            if transaction['flowType'] == 'income':
                total_amount -= transaction['price'] * transaction['quantity']
            if transaction['flowType'] == 'expense':
                total_amount += transaction['price'] * transaction['quantity']

            self.cashflow_manager.insert_cashflow(cashflow_item)

        # Update wallet balance
        self.wallet_manager.update_balance(wallet.id, wallet.balance - total_amount)
        await query.edit_message_text('✅ Data telah disimpan. Terima kasih!')

    def extract_wallet_from_chat_log(self, chat_log):
        """Extract wallet name from chat log."""
        for message in chat_log:
            if message["role"] == "model":
                text = message["text"]
                if text.startswith("```json"):
                    text = text.replace("```json", "").replace("```", "").strip()
                try:
                    data = json.loads(text)
                    for entry in data:
                        if "activityName" in entry and "wallet" in entry:
                            return entry['wallet']
                except Exception as e:
                    logger.error(f"Failed to parse JSON from chat log: {e}")
        return None

    def extract_transaction_data_from_chat_log(self, chat_log):
        """Extract transaction data from chat log."""
        for message in chat_log:
            if message["role"] == "model":
                text = message["text"]
                if text.startswith("```json"):
                    text = text.replace("```json", "").replace("```", "").strip()
                try:
                    return json.loads(text)
                except Exception as e:
                    logger.error(f"Failed to parse transaction data: {e}")
        return []

    def setup_handlers(self, app):
        """Setup all command and message handlers."""
        # Conversation handler for adding wallet
        wallet_conversation = ConversationHandler(
            entry_points=[CommandHandler('tambah_wallet', self.add_wallet_start)],
            states={
                self.WALLET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_wallet_name)],
                self.WALLET_BALANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_wallet_balance)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel_add_wallet)],
        )
        
        # Add all handlers
        app.add_handler(wallet_conversation)
        app.add_handler(CommandHandler('start', self.start_command))
        app.add_handler(CommandHandler('register', self.register_command))
        app.add_handler(CommandHandler('menu', self.menu_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        app.add_handler(CallbackQueryHandler(self.handle_confirmation_callback))

    def run(self):
        """Run the bot."""
        app = ApplicationBuilder().token(self.bot_token).build()
        self.setup_handlers(app)
        
        logger.info("Starting Telegram Finance Bot...")
        app.run_polling()


def main():
    bot = TelegramFinanceBot()
    bot.run()


if __name__ == '__main__':
    main()
