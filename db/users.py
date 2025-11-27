import aiosqlite
import os
from typing import Optional, List
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
                contract_id TEXT,
                contract_title TEXT,
                password TEXT
            )
        """)
        # Индексы для быстрого поиска
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_contract_id ON users (contract_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_chat_id ON users (chat_id)")
        await db.commit()

async def add_chat(chat_id: int) -> None:
    """
    Добавляет новый чат в таблицу users.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Сначала проверим, есть ли такой пользователь
        cursor = await db.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
        row = await cursor.fetchone()

        if not row:
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
                await db.commit()

async def add_user(chat_id: str, contract_id: str, password: str, contract_title: Optional[str] = None) -> None:
    """
    Добавляет или обновляет пользователя в таблице.
    Совместимо со старыми версиями SQLite без ON CONFLICT.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Сначала проверим, есть ли такой пользователь
        cursor = await db.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
        row = await cursor.fetchone()

        if row:
            # Обновляем существующую запись
            await db.execute(
                "UPDATE users SET contract_id = ?, contract_title = ?, password = ? WHERE chat_id = ?",
                (contract_id, contract_title, password, chat_id)
            )
        else:
            # Вставляем новую запись
            await db.execute(
                "INSERT INTO users (chat_id, contract_id, contract_title, password) VALUES (?, ?, ?, ?)",
                (chat_id, contract_id, contract_title, password)
            )

        await db.commit()

async def get_user_by_chat_id(chat_id: int) -> Optional[dict]:
    """
    Возвращает пользователя по chat_id в виде словаря.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT chat_id, contract_id, contract_title FROM users WHERE chat_id = ?", (chat_id,))
        row = await cursor.fetchone()
        if row:
            return {
                "chat_id": row[0],
                "contract_id": row[1],
                "contract_title": row[2],
            }
        else:
            await add_chat(chat_id)
        return None

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


async def get_chat_ids_by_contract_id(contract_id: str) -> List[str]:
    """
    Получает все chat_id по contract_id (теперь возвращает список, так как может быть несколько).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM users WHERE contract_id = ?", (contract_id,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows] if rows else []


async def logout_user(chat_id: int) -> None:
    """
    разлогинить пользователя по chat_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET contract_id = "", contract_title = "", password = "" WHERE chat_id = ?", (chat_id,))
        await db.commit()

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
