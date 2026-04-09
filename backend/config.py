import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    # RetailCRM
    RETAILCRM_URL = os.getenv("RETAILCRM_URL")
    RETAILCRM_API_KEY = os.getenv("RETAILCRM_API_KEY")
    RETAILCRM_SITE_CODE = os.getenv("RETAILCRM_SITE_CODE", "default")
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", False)
    API_PORT = int(os.getenv("API_PORT", 5000))

config = Config()
