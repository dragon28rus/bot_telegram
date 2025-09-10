from decouple import config

# Токен Telegram-бота
BOT_TOKEN = config('BOT_TOKEN', env_file='env/.env')

# Настройки BGBilling API
BGBILLING_API_URL = config('BGBILLING_API_URL', env_file='env/.env')
BGBILLING_AUTH = (config('BGBILLING_USERNAME', env_file='env/.env'), config('BGBILLING_PASSWORD', env_file='env/.env'))

# Настройки вебхука
WEBHOOK_URL = config('WEBHOOK_URL', env_file='env/.env')
WEBHOOK_PATH = config('WEBHOOK_PATH', env_file='env/.env')

# Chat ID технической поддержки
SUPPORT_CHAT_ID = config('SUPPORT_CHAT_ID', cast=int, env_file='env/.env')