# db/support.py
import aiosqlite
from config import DB_PATH
from typing import Optional, Tuple

# ==============================
# 🔧 Инициализация
# ==============================
async def create_tables() -> None:
    """
    Создание таблиц для поддержки (если их еще нет).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица активных сессий поддержки
        await db.execute("""
            CREATE TABLE IF NOT EXISTS support_sessions (
                chat_id INTEGER PRIMARY KEY,
                contract_title TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """)

        # Таблица соответствия сообщений абонент ↔ оператор
        await db.execute("""
            CREATE TABLE IF NOT EXISTS support_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_message_id INTEGER NOT NULL,
                support_message_id INTEGER NOT NULL
            )
        """)
        await db.commit()


# Совместимость со старым кодом
async def init_support_table() -> None:
    """Алиас для create_tables (совместимость)."""
    await create_tables()


# ==============================
# 📌 Работа с сессиями
# ==============================
async def start_session(chat_id: int, contract_title: str) -> None:
    """
    Запуск сессии поддержки для пользователя.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO support_sessions (chat_id, contract_title, is_active)
            VALUES (?, ?, 1)
        """, (chat_id, contract_title))
        await db.commit()


async def end_session(chat_id: int) -> None:
    """
    Завершение сессии поддержки.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE support_sessions SET is_active = 0 WHERE chat_id = ?
        """, (chat_id,))
        await db.commit()


async def is_in_support(chat_id: int) -> bool:
    """
    Проверка, находится ли пользователь в режиме поддержки.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT is_active FROM support_sessions WHERE chat_id = ?
        """, (chat_id,)) as cursor:
            row = await cursor.fetchone()
            return bool(row and row[0] == 1)


# ==============================
# 📌 Работа с сообщениями
# ==============================
async def save_message_mapping(chat_id: int, user_message_id: int, support_message_id: int) -> None:
    """
    Сохраняем соответствие между сообщениями пользователя и поддержки.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO support_messages (chat_id, user_message_id, support_message_id)
            VALUES (?, ?, ?)
        """, (chat_id, user_message_id, support_message_id))
        await db.commit()


async def get_user_by_support_msg_id(support_message_id: int) -> Optional[Tuple[int, int]]:
    """
    Получаем пользователя по сообщению из чата поддержки.
    Возвращает (chat_id, user_message_id) или None.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT chat_id, user_message_id FROM support_messages
            WHERE support_message_id = ?
        """, (support_message_id,)) as cursor:
            return await cursor.fetchone()