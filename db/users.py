import aiosqlite
import os
from typing import Optional, List, Tuple
from config import DB_PATH


async def init_users_table() -> None:
    """
    Создаёт таблицу users и индексы, если они ещё не существуют.
    Таблица хранит соответствие chat_id ↔ contract_id ↔ contract_title.
    """
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT UNIQUE NOT NULL,
                contract_id TEXT NOT NULL,
                contract_title TEXT
            )
        """)
        # Индексы для быстрого поиска
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_contract_id ON users (contract_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_chat_id ON users (chat_id)")
        await db.commit()


async def add_user(chat_id: str, contract_id: str, contract_title: Optional[str] = None) -> None:
    """
    Добавляет пользователя в таблицу или обновляет данные при конфликте по chat_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (chat_id, contract_id, contract_title)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                contract_id=excluded.contract_id,
                contract_title=excluded.contract_title
        """, (chat_id, contract_id, contract_title))
        await db.commit()


async def get_user_by_chat_id(chat_id: str) -> Optional[Tuple[str, str, Optional[str]]]:
    """
    Получает пользователя по chat_id.
    Возвращает (chat_id, contract_id, contract_title) или None.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT chat_id, contract_id, contract_title FROM users WHERE chat_id = ?",
            (chat_id,)
        ) as cursor:
            return await cursor.fetchone()


async def get_contract_id_by_chat_id(chat_id: str) -> Optional[str]:
    """
    Получает contract_id по chat_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT contract_id FROM users WHERE chat_id = ?", (chat_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def get_chat_id_by_contract_id(contract_id: str) -> Optional[str]:
    """
    Получает chat_id по contract_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM users WHERE contract_id = ?", (contract_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def remove_user(chat_id: str) -> None:
    """
    Удаляет пользователя по chat_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE chat_id = ?", (chat_id,))
        await db.commit()


async def get_all_chat_ids() -> List[str]:
    """
    Возвращает список всех chat_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
