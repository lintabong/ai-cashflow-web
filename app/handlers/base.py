from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes

class BaseHandler(ABC):
    """Base handler class for all handlers."""
    
    def __init__(self, **services):
        """Initialize handler with required services."""
        for service_name, service in services.items():
            setattr(self, service_name, service)
    
    @abstractmethod
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the incoming update."""
        pass
