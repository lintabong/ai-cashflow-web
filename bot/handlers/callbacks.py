import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.base import BaseHandler
from bot.services.user_service import UserService
from bot.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)

class CallbackHandler(BaseHandler):
    def __init__(self, user_service: UserService, transaction_service: TransactionService, memory_cache):
        super().__init__(user_service=user_service, transaction_service=transaction_service)
        self.memory = memory_cache

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Optional override
        pass
    
    async def handle_confirmation_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle confirmation callbacks."""
        query = update.callback_query
        await query.answer()
        
        telegram_user = update.effective_user
        user = self.user_service.get_or_create_user(telegram_user)
        
        if not user:
            await query.edit_message_text('❌ User tidak ditemukan.')
            return
        
        try:
            if query.data == 'confirmed_yes':
                chat_log = self.memory.get_context(user.id)['messages']
                success, message = self.transaction_service.save_transactions(user.id, chat_log)
                await query.edit_message_text(message)
                
            elif query.data == 'confirmed_no':
                await query.edit_message_text('🚫 Data dibatalkan. Silakan kirim ulang input.')
            
            # Clear user data
            self.memory.clear_user_data(user.id)
            
        except Exception as e:
            logger.error(f"Error handling confirmation: {e}")
            await query.edit_message_text('❌ Terjadi kesalahan saat memproses konfirmasi.')
