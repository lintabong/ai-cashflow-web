import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN = os.getenv('BOT_TELEGRAM_API')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'finance_bot')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()