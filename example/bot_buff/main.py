import logging
from telegram.ext import CommandHandler as TelegramCommandHandler, MessageHandler as TelegramMessageHandler
from telegram.ext import CallbackQueryHandler, ConversationHandler, filters

from bot_buff.core.bot import BotCore
from bot_buff.config.settings import settings
from lib.cache import cacheMessage
from lib.database.db import DatabaseConnection
from lib.database.manager.user_manager import UserManager
from lib.database.manager.cashflow_manager import CashflowManager
from lib.database.manager.wallet_manager import WalletManager

# Services
from bot_buff.services.ai_service import AIService
from bot_buff.services.user_service import UserService
from bot_buff.services.wallet_service import WalletService
from bot_buff.services.transaction_service import TransactionService

# Handlers
from bot_buff.handlers.commands import CommandHandler
from bot_buff.handlers.conversations.wallet import WalletConversationHandler
from bot_buff.handlers.messages import MessageHandler
from bot_buff.handlers.callbacks import CallbackHandler

logger = logging.getLogger(__name__)

class TelegramFinanceBot:
    def __init__(self):
        # Initialize core
        self.bot_core = BotCore()
        self.bot_core.setup_logging()
        
        # Initialize database and managers
        self.db = DatabaseConnection()
        self.user_manager = UserManager(self.db)
        self.cashflow_manager = CashflowManager(self.db)
        self.wallet_manager = WalletManager(self.db)
        
        # Initialize cache
        self.memory = cacheMessage()
        
        # Initialize services
        self.ai_service = AIService()
        self.user_service = UserService(self.user_manager)
        self.wallet_service = WalletService(self.wallet_manager)
        self.transaction_service = TransactionService(
            self.ai_service, self.cashflow_manager, self.wallet_service
        )
        
        # Initialize handlers
        self.command_handler = CommandHandler(self.user_service)
        self.wallet_conversation_handler = WalletConversationHandler(
            self.user_service, self.wallet_service
        )
        self.message_handler = MessageHandler(
            self.user_service, self.ai_service, self.transaction_service, self.wallet_service, self.memory
        )
        self.callback_handler = CallbackHandler(
            self.user_service, self.transaction_service, self.memory
        )
    
    def setup_handlers(self, app):
        """Setup all command and message handlers."""
        app.add_handler(ConversationHandler(
            entry_points=[TelegramCommandHandler('tambah_wallet', self.wallet_conversation_handler.start_add_wallet)],
            states={
                self.wallet_conversation_handler.WALLET_NAME: [
                    TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, self.wallet_conversation_handler.get_wallet_name)
                ],
                self.wallet_conversation_handler.WALLET_BALANCE: [
                    TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, self.wallet_conversation_handler.get_wallet_balance)
                ],
            },
            fallbacks=[TelegramCommandHandler('cancel', self.wallet_conversation_handler.cancel_add_wallet)],
        ))
        app.add_handler(TelegramCommandHandler('start', self.command_handler.start_command))
        app.add_handler(TelegramCommandHandler('register', self.command_handler.register_command))
        app.add_handler(TelegramCommandHandler('menu', self.command_handler.menu_command))
        app.add_handler(TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler.handle_text_message))
        app.add_handler(CallbackQueryHandler(self.callback_handler.handle_confirmation_callback))
    
    def run(self):
        """Run the bot."""
        app = self.bot_core.create_application()
        self.setup_handlers(app)
        
        logger.info("Starting Telegram Finance Bot...")
        app.run_polling()

def main():
    bot = TelegramFinanceBot()
    bot.run()

if __name__ == '__main__':
    main()
