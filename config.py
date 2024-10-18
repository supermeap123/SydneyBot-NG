# config.py
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from .env file
load_dotenv()

# Environment Variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_API_KEY_EXPENSIVE = os.getenv('OPENROUTER_API_KEY_EXPENSIVE')  # For advanced models

if not DISCORD_TOKEN:
    raise EnvironmentError("Missing DISCORD_TOKEN in environment variables.")
if not OPENROUTER_API_KEY:
    raise EnvironmentError("Missing OPENROUTER_API_KEY in environment variables.")
if not OPENROUTER_API_KEY_EXPENSIVE:
    raise EnvironmentError("Missing OPENROUTER_API_KEY_EXPENSIVE in environment variables.")

# Logging Configuration
if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger('sydneybot')
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs

# File Handler with Rotation
file_handler = RotatingFileHandler('logs/sydneybot.log', maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)