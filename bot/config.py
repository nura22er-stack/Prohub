import os
from dotenv import load_dotenv
import json

load_dotenv()


def get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


# Telegram Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME', '@ProHubBot')
REQUIRED_CHANNEL = os.getenv('REQUIRED_CHANNEL', '@ProHubChannel')
CHANNEL_ID = get_int_env('CHANNEL_ID', -1001234567890)
ADMIN_ID = get_int_env('ADMIN_ID', 0)
APPS_PER_PAGE = get_int_env('APPS_PER_PAGE', 10)

# Database
DEFAULT_DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'bot_data.json')
DATA_FILE = os.getenv('DATA_FILE', DEFAULT_DATA_FILE)

# API Configuration
API_PORT = get_int_env('PORT', get_int_env('API_PORT', 5000))
API_HOST = os.getenv('API_HOST', '0.0.0.0')

# Admin session timeout (in seconds)
ADMIN_SESSION_TIMEOUT = 3600  # 1 hour
