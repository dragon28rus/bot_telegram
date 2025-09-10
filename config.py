from decouple import config

# Токен Telegram-бота
BOT_TOKEN = config('BOT_TOKEN')

# Настройки BGBilling API
BGBILLING_API_URL = config('BGBILLING_API_URL')
BGBILLING_AUTH = (config('BGBILLING_USERNAME'), config('BGBILLING_PASSWORD'))

# Настройки вебхука
WEBHOOK_URL = config('WEBHOOK_URL')
WEBHOOK_PATH = config('WEBHOOK_PATH')

# Chat ID технической поддержки
SUPPORT_CHAT_ID = config('SUPPORT_CHAT_ID', cast=int)