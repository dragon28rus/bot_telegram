import logging
import os
from datetime import datetime

# Путь к файлу логов
LOG_DIR = '/opt/cable_bot'
LOG_FILE = os.path.join(LOG_DIR, 'cable_bot.log')

# Создание директории для логов, если она не существует
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Настройка логгера
logger = logging.getLogger('cable_bot')
logger.setLevel(logging.INFO)

# Форматтер для логов
formatter = logging.Formatter('%(asctime)s - %(levelname)s - chat_id:%(chat_id)s - %(message)s')

# Файловый обработчик
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Добавление обработчиков к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Хранилище для chat_id
_chat_id = 'unknown'

def set_chat_id(chat_id):
    """Устанавливает chat_id для логирования."""
    global _chat_id
    _chat_id = str(chat_id)

# Переопределение метода логирования для добавления chat_id
class ChatIDFilter(logging.Filter):
    def filter(self, record):
        record.chat_id = _chat_id
        return True

logger.addFilter(ChatIDFilter())