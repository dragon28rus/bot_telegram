#### logger.py
import logging

# Кастомный форматтер для обработки отсутствия chat_id
class CustomFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'chat_id'):
            record.chat_id = 'unknown'
        return super().format(record)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    filename='cable_bot.log',
    format='%(asctime)s - %(levelname)s - chat_id:%(chat_id)s - %(message)s'
)

# Применяем кастомный форматтер
handler = logging.FileHandler('cable_bot.log')
handler.setFormatter(CustomFormatter('%(asctime)s - %(levelname)s - chat_id:%(chat_id)s - %(message)s'))
logging.getLogger().handlers = [handler]

# Добавляем chat_id в контекст логирования
class ContextualLogger(logging.LoggerAdapter):
    def __init__(self, logger, chat_id='unknown'):
        super().__init__(logger, {})
        self.chat_id = chat_id

    def process(self, msg, kwargs):
        kwargs['extra'] = {'chat_id': self.chat_id}
        return msg, kwargs

    def set_chat_id(self, chat_id):
        self.chat_id = str(chat_id) if chat_id else 'unknown'

logger = ContextualLogger(logging.getLogger(), chat_id='unknown')

def set_chat_id(chat_id):
    logger.set_chat_id(chat_id)
