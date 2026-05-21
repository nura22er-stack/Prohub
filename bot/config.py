import os
from dotenv import load_dotenv
import json

load_dotenv()

# Telegram Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME', '@ProHubBot')
REQUIRED_CHANNEL = os.getenv('REQUIRED_CHANNEL', '@ProHubChannel')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '-1001234567890'))
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
APPS_PER_PAGE = int(os.getenv('APPS_PER_PAGE', '10'))

# Database
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'bot_data.json')

# API Configuration
API_PORT = int(os.getenv('API_PORT', '5000'))
API_HOST = os.getenv('API_HOST', '0.0.0.0')

# Admin session timeout (in seconds)
ADMIN_SESSION_TIMEOUT = 3600  # 1 hour
