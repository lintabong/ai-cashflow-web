
import os
import logging
from telegram.ext import (
    ApplicationBuilder, 
    filters,
    CommandHandler, 
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler
)
from dotenv import load_dotenv
from bot.handlers.index import IndexHandler
from bot.handlers.base_intent import BaseIntent
from bot.handlers.wallet import WalletHandler
from bot.handlers.cashflow import CashflowHandler
from bot.services.llm_model import LLMModel
from bot.services.cache import CacheMessage
from bot.services.image import ImageManager
from bot.config import setup_logging

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

class TelegramFinanceBot:
    def __init__(self):
        self.token = os.getenv('BOT_TELEGRAM_API')
        self.app = ApplicationBuilder().token(self.token).build()

        self.llm_model = LLMModel()
        self.cache = CacheMessage()
        self.image_manager = ImageManager()

        self.index_handler = IndexHandler()
        self.base_intent = BaseIntent(self.llm_model, self.cache, self.image_manager)
        self.cashflow_handler = CashflowHandler(self.llm_model, self.cache)

        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler('start', self.index_handler.start))
        self.app.add_handler(CommandHandler('register', self.index_handler.register))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.base_intent.handle_message))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.base_intent.handle_photo))
        self.app.add_handler(CallbackQueryHandler(self.cashflow_handler.handle_confirmation_callback))

    def run(self):
        logger.info('Bot is starting...')
        self.app.run_polling()

def main():
    bot = TelegramFinanceBot()
    bot.run()

if __name__ == '__main__':
    main()
