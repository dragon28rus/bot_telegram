### db.py
import sqlite3
from logger import logger, set_chat_id

# Инициализация базы данных
def init_db():
    try:
        conn = sqlite3.connect('/opt/cable_bot/users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                contract_id TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_requests (
                chat_id INTEGER,
                support_message_id INTEGER,
                PRIMARY KEY (chat_id, support_message_id)
            )
        ''')
        conn.commit()
        logger.info("chat_id:system - Database initialized")
    except Exception as e:
        logger.error(f"chat_id:system - Error initializing database: {e}")
    finally:
        conn.close()

# Сохранение обращения в техподдержку
def save_support_request(chat_id, support_message_id):
    try:
        conn = sqlite3.connect('/opt/cable_bot/users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO support_requests (chat_id, support_message_id) VALUES (?, ?)', (chat_id, support_message_id))
        conn.commit()
        logger.info(f"chat_id:{chat_id} - Support request saved with message_id: {support_message_id}")
    except Exception as e:
        logger.error(f"chat_id:{chat_id} - Error saving support request: {e}")
    finally:
        conn.close()

# Получение chat_id пользователя по message_id в группе техподдержки
def get_chat_id_by_support_message_id(support_message_id):
    try:
        conn = sqlite3.connect('/opt/cable_bot/users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM support_requests WHERE support_message_id = ?', (support_message_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"chat_id:system - Error retrieving chat_id for support_message_id {support_message_id}: {e}")
        return None
    finally:
        conn.close()

# Существующие функции (для полноты, без изменений)
def save_user(chat_id, contract_id):
    try:
        conn = sqlite3.connect('/opt/cable_bot/users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO users (chat_id, contract_id) VALUES (?, ?)', (chat_id, contract_id))
        conn.commit()
        logger.info(f"chat_id:{chat_id} - User saved with contract_id: {contract_id}")
    except Exception as e:
        logger.error(f"chat_id:{chat_id} - Error saving user: {e}")
    finally:
        conn.close()

def is_user_authorized(chat_id):
    try:
        conn = sqlite3.connect('/opt/cable_bot/users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT contract_id FROM users WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        logger.error(f"chat_id:{chat_id} - Error checking authorization: {e}")
        return False
    finally:
        conn.close()

def get_chat_id_by_contract_id(contract_id):
    try:
        conn = sqlite3.connect('/opt/cable_bot/users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM users WHERE contract_id = ?', (contract_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"chat_id:system - Error retrieving chat_id for contract_id {contract_id}: {e}")
        return None
    finally:
        conn.close()

def get_contract_id_by_chat_id(chat_id):
    try:
        conn = sqlite3.connect('/opt/cable_bot/users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT contract_id FROM users WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"chat_id:{chat_id} - Error retrieving contract_id: {e}")
        return None
    finally:
        conn.close()

def get_all_chat_ids():
    try:
        conn = sqlite3.connect('/opt/cable_bot/users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM users')
        result = cursor.fetchall()
        return [row[0] for row in result]
    except Exception as e:
        logger.error(f"chat_id:system - Error retrieving all chat_ids: {e}")
        return []
    finally:
        conn.close()