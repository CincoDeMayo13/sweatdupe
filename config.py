"""
Configuration settings for Sweat Dupe bot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Whitelist - Read from .env as comma-separated usernames
WHITELIST_STR = os.getenv("WHITELIST", "")
WHITELIST = [username.strip() for username in WHITELIST_STR.split(",") if username.strip()]

# Data file
DATA_FILE = "bot_data.json"

# Limits
MAX_USERS = 2
MIN_WEEKLY_GOAL = 1
MAX_WEEKLY_GOAL = 7

# Whitelist (Private Mode)
# Set to empty list [] to allow anyone, or add Telegram usernames (without @)
# Example: WHITELIST = ["CincoDeMayo13", "canliddatmeh"]
WHITELIST = ["CincoDeMayo13", "canliddatmeh"]  # Add partner's username here (without @)
