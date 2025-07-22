import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot_buff.handlers.base import BaseHandler
from bot_buff.services.user_service import UserService
from bot_buff.services.wallet_service import WalletService

logger = logging.getLogger(__name__)

class WalletConversationHandler(BaseHandler):
    def __init__(self, user_service: UserService, wallet_service: WalletService):
        super().__init__(user_service=user_service, wallet_service=wallet_service)
        self.WALLET_NAME, self.WALLET_BALANCE = range(2)
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Optional override
        pass
    
    async def start_add_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start wallet addition conversation."""
        user = update.effective_user
        await update.message.reply_text(f'Halo {user.username} masukkan nama wallet:')
        return self.WALLET_NAME
    
    async def get_wallet_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get wallet name from user."""
        context.user_data['wallet_name'] = update.message.text.strip()
        await update.message.reply_text('Masukkan nominal awal wallet:')
        return self.WALLET_BALANCE
    
    async def get_wallet_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get wallet balance and create wallet."""
        telegram_user = update.effective_user
        user = self.user_service.get_or_create_user(telegram_user)
        
        if not user:
            await update.message.reply_text('Kamu belum terdaftar. Ketik /register')
            return ConversationHandler.END
        
        try:
            balance = float(update.message.text)
            wallet_name = context.user_data['wallet_name']
            
            success, message = self.wallet_service.create_wallet(user.id, wallet_name, balance)
            await update.message.reply_text(message)
            
        except ValueError:
            await update.message.reply_text("❌ Nominal tidak valid. Masukkan angka yang benar.")
            return self.WALLET_BALANCE
        
        return ConversationHandler.END
    
    async def cancel_add_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel wallet addition."""
        await update.message.reply_text("Operasi dibatalkan.")
        return ConversationHandler.END
