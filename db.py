### db.py
import sqlite3
from logger import logger, set_chat_id

def init_db():
    """
    Инициализирует базу данных SQLite, создавая таблицу users, если она не существует.
    """
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                contract_number TEXT,
                contract_id TEXT
            )
        ''')
        conn.commit()
        logger.info('Database initialized')
    except Exception as e:
        logger.error(f'Error initializing database: {e}')
    finally:
        conn.close()

def save_user(chat_id, contract_number, contract_id):
    """
    Сохраняет данные пользователя в базе данных.
    
    Args:
        chat_id: Telegram chat_id пользователя
        contract_number: Номер договора
        contract_id: ID договора из биллинга
    Returns:
        bool: True если успешно, False в случае ошибки
    """
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (chat_id, contract_number, contract_id)
            VALUES (?, ?, ?)
        ''', (chat_id, contract_number, contract_id))
        conn.commit()
        logger.info(f'User saved: chat_id={chat_id}, contract_number={contract_number}')
        return True
    except Exception as e:
        logger.error(f'Error saving user: {e}')
        return False
    finally:
        conn.close()

def get_contract_id(chat_id):
    """
    Получает contract_id по chat_id из базы данных.
    
    Args:
        chat_id: Telegram chat_id пользователя
    Returns:
        str or None: contract_id или None, если пользователь не найден
    """
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT contract_id FROM users WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.error(f'Error getting contract_id for chat_id {chat_id}: {e}')
        return None
    finally:
        conn.close()

def get_contract_number(chat_id):
    """
    Получает contract_number по chat_id из базы данных.
    
    Args:
        chat_id: Telegram chat_id пользователя
    Returns:
        str or None: contract_number или None, если пользователь не найден
    """
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT contract_number FROM users WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.error(f'Error getting contract_number for chat_id {chat_id}: {e}')
        return None
    finally:
        conn.close()

def delete_user(chat_id):
    """
    Удаляет пользователя из базы данных по chat_id.
    
    Args:
        chat_id: Telegram chat_id пользователя
    Returns:
        bool: True если успешно, False в случае ошибки
    """
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE chat_id = ?', (chat_id,))
        conn.commit()
        logger.info(f'User deleted: chat_id={chat_id}')
        return True
    except Exception as e:
        logger.error(f'Error deleting user with chat_id {chat_id}: {e}')
        return False
    finally:
        conn.close()

def get_chat_id_by_contract_id(contract_id):
    """
    Получает chat_id по contract_id из базы данных.
    
    Args:
        contract_id: ID договора из биллинга
    Returns:
        int or None: chat_id или None, если пользователь не найден
    """
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM users WHERE contract_id = ?', (contract_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.error(f'Error getting chat_id for contract_id {contract_id}: {e}')
        return None
    finally:
        conn.close()

def get_all_chat_ids():
    """
    Получает все chat_id из базы данных.
    
    Returns:
        list: Список всех chat_id
    """
    try:
        conn = sqlite3.connect('cable_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM users')
        result = cursor.fetchall()
        return [row[0] for row in result]
    except Exception as e:
        logger.error(f'Error getting all chat_ids: {e}')
        return []
    finally:
        conn.close()