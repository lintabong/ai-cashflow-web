import logging
import os

def setup_logging():
    """Setup global logging configuration."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s - %(name)s >> %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Suppress noisy loggers
    for log_name in ['httpx', 'telegram.bot', 'telegram.ext._application', 
                     'sqlalchemy.engine', 'google_genai.models']:
        logging.getLogger(log_name).setLevel(logging.WARNING)
