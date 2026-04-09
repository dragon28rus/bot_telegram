# config.py
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# --- Telegram ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Database ---
DB_PATH = os.getenv("DB_PATH", "./data/bot.db")

# --- BGBilling API ---
BGBILLING_API_URL = os.getenv("BGBILLING_API_URL")
BGBILLING_AUTH = (os.getenv("BGBILLING_USER"), os.getenv("BGBILLING_PASSWORD"))
BILLING_API_TOKEN = os.getenv("BILLING_API_TOKEN")

# --- Webhook ---
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
BILLING_WEBHOOK_PORT = int(os.getenv("BILLING_WEBHOOK_PORT", 8443))

# --- Support ---
SUPPORT_CHAT_ID = int(os.getenv("SUPPORT_CHAT_ID", "0"))

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "./logs")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# --- Admins ---
ADMIN_CHAT_IDS = [x.strip() for x in os.getenv("ADMIN_CHAT_IDS", "").split(",") if x.strip()]

# Телефоны операторов (для кнопок звонка)
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "")
BILLING_PHONE = os.getenv("BILLING_PHONE", "")

# Service-code магазина в сервисе ccassa
PAYMENT_SHOP_ID = os.getenv("PAYMENT_SHOP_ID")

# --- Security ---
# Ключ для шифрования паролей абонентов в БД (Fernet, urlsafe base64, 32-byte key)
PASSWORD_ENCRYPTION_KEY = os.getenv("PASSWORD_ENCRYPTION_KEY")
