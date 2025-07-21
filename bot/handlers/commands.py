import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from bot.handlers.base import BaseHandler
from bot.services.user_service import UserService

logger = logging.getLogger(__name__)

class CommandHandler(BaseHandler):
    def __init__(self, user_service: UserService):
        super().__init__(user_service=user_service)

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Optional override
        pass
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        await update.message.reply_text(f'Halo {user.username} ID: {user.id}')
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command."""
        keyboard = [
            ["💰 Cek Saldo", "/tambah_wallet"],
            ["📊 Laporan", "⚙️ Pengaturan"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Silakan pilih menu:", reply_markup=reply_markup)
    
    async def register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /register command."""
        telegram_user = update.effective_user
        success, message = self.user_service.register_user(telegram_user)
        await update.message.reply_text(message)
