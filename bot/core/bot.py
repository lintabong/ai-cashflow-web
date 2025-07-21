import logging
from telegram.ext import ApplicationBuilder

from bot.config.settings import settings

logger = logging.getLogger(__name__)

class BotCore:
    def __init__(self):
        self.token = settings.BOT_TOKEN
        self.app = None
    
    def create_application(self):
        """Create and return telegram application."""
        self.app = ApplicationBuilder().token(self.token).build()
        return self.app
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Suppress verbose logs
        for log_name in ['httpx', 'telegram.bot', 'telegram.ext._application']:
            logging.getLogger(log_name).setLevel(logging.WARNING)
