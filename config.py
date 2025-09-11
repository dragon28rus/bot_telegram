import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Токен Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# SQLite Database
DB_PATH = os.getenv("DB_PATH", "./db.sqlite3")

# Настройки BGBilling API
BGBILLING_API_URL = os.getenv('BGBILLING_API_URL')
BGBILLING_AUTH = (os.getenv('BGBILLING_USERNAME'), os.getenv('BGBILLING_PASSWORD'))

# Настройки вебхука
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

# Chat ID технической поддержки
SUPPORT_CHAT_ID = int(os.getenv("SUPPORT_CHAT_ID", "0"))

# Токен для авторизации биллинг API
BILLING_API_TOKEN = os.getenv('BILLING_API_TOKEN')

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "./logs")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")