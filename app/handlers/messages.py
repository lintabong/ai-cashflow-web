import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.handlers.base import BaseHandler
from app.services.user_service import UserService
from app.services.ai_service import AIService
from app.services.transaction_service import TransactionService
from app.services.wallet_service import WalletService
from app.utils.memory_helper import build_history_from_memory
from helpers.output_message import render_grouped_table, render_wallet_summary

logger = logging.getLogger(__name__)

class MessageHandler(BaseHandler):
    def __init__(self, user_service: UserService, ai_service: AIService, 
                 transaction_service: TransactionService, wallet_service:WalletService, 
                 memory_cache):
        super().__init__(
            user_service=user_service,
            ai_service=ai_service,
            transaction_service=transaction_service,
            wallet_service=wallet_service
        )
        self.memory = memory_cache
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Optional override
        pass
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages."""
        telegram_user = update.effective_user
        message = update.message.text.strip()
        
        user = self.user_service.get_or_create_user(telegram_user)
        if not user:
            await update.message.reply_text('Kamu belum terdaftar. Ketik /register')
            return
        
        try:
            # Analyze message intent
            parsed_data = self.ai_service.analyze_message_intent(message)
            parsed_data['message'] = message
            
            logger.info(f'{telegram_user.id} || {parsed_data["intent"]} || send: {message}')
            
            # Handle different intents
            if parsed_data['intent'] == 'CATAT_TRANSAKSI':
                await self._handle_transaction_intent(update, user.id, parsed_data)
                
            elif parsed_data['intent'] == 'TANYA_SALDO':
                wallets = self.wallet_service.get_wallets_name_balance_by_user_id(user.id)
                wallets_json = [{'name': wallet.name, 'balance': wallet.balance} for wallet in wallets]
                await update.message.reply_text(render_wallet_summary(wallets_json), parse_mode='Markdown')
                
            elif parsed_data['intent'] == 'LAINNYA':
                response_text = await self._handle_normal_conversation(user.id, parsed_data)
                await update.message.reply_text(response_text)
                
            else:
                await update.message.reply_text(f"Intent tidak dikenali: {parsed_data['intent']}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat memproses pesan Anda.")
    
    async def _handle_transaction_intent(self, update, user_id, parsed_data):
        """Handle transaction recording intent."""
        try:
            history = build_history_from_memory(self.memory, user_id)
            
            # Save user message to memory
            self.memory.save_message(user_id, parsed_data['message'], 'user')
            
            # Process transaction with AI
            response_text = self.transaction_service.process_transaction_message(
                user_id, parsed_data['message'], history
            )
            
            # Save AI response to memory
            self.memory.save_message(user_id, response_text, 'model')
            
            # Parse and format response
            response_data = self.ai_service.parse_json_response(response_text)
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
    
    async def _handle_normal_conversation(self, user_id, parsed_data):
        """Handle normal conversation."""
        history = build_history_from_memory(self.memory, user_id)
        
        self.memory.save_message(user_id, parsed_data['message'], 'user')
        response_text = self.ai_service.handle_normal_conversation(parsed_data['message'], history)
        self.memory.save_message(user_id, response_text, 'model')
        
        return response_text
