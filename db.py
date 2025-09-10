### db.py
import sqlite3
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

# Инициализация базы данных
def init_db():
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                contract_number TEXT NOT NULL,
                contract_id TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        logger.set_chat_id('system')
        logger.info('Database initialized')
    except Exception as e:
        logger.error(f'Error initializing DB: {e}')

# Сохранение пользователя
def save_user(chat_id, contract_number, contract_id):
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (chat_id, contract_number, contract_id)
            VALUES (?, ?, ?)
        ''', (chat_id, contract_number, contract_id))
        conn.commit()
        conn.close()
        logger.set_chat_id(chat_id)
        logger.info('User saved successfully')
        return True
    except Exception as e:
        logger.error(f'Error saving user: {e}')
        return False

# Получение contract_id по chat_id
def get_contract_id(chat_id):
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT contract_id FROM users WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        conn.close()
        logger.set_chat_id(chat_id)
        logger.info('Contract ID retrieved')
        return result[0] if result else None
    except Exception as e:
        logger.error(f'Error getting contract_id: {e}')
        return None

# Получение contract_number по chat_id
def get_contract_number(chat_id):
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT contract_number FROM users WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        conn.close()
        logger.set_chat_id(chat_id)
        logger.info('Contract number retrieved')
        return result[0] if result else None
    except Exception as e:
        logger.error(f'Error getting contract_number: {e}')
        return None

# Удаление пользователя
def delete_user(chat_id):
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE chat_id = ?', (chat_id,))
        conn.commit()
        conn.close()
        logger.set_chat_id(chat_id)
        logger.info('User deleted successfully')
        return True
    except Exception as e:
        logger.error(f'Error deleting user: {e}')
        return False

# Получение chat_id по contract_id
def get_chat_id_by_contract_id(contract_id):
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM users WHERE contract_id = ?', (contract_id,))
        result = cursor.fetchone()
        conn.close()
        logger.set_chat_id('system')
        logger.info(f'Chat ID retrieved for contract_id {contract_id}')
        return result[0] if result else None
    except Exception as e:
        logger.error(f'Error getting chat_id for contract_id {contract_id}: {e}')
        return None