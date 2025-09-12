import aiosqlite
import os
from typing import Optional
from config import DB_PATH


async def init_users_table() -> None:
    """Создание таблицы для хранения пользователей (chat_id ↔ contract_id + contract_title)."""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT UNIQUE NOT NULL,
                contract_id TEXT UNIQUE NOT NULL,
                contract_title TEXT
            )
        """)
        await db.commit()


async def add_user(chat_id: str, contract_id: str, contract_title: Optional[str] = None) -> None:
    """Добавляет или обновляет пользователя по chat_id."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (chat_id, contract_id, contract_title)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                contract_id=excluded.contract_id,
                contract_title=excluded.contract_title
            """,
            (chat_id, contract_id, contract_title),
        )
        await db.commit()


async def remove_user(chat_id: str) -> None:
    """Удаляет пользователя по chat_id (отвязка договора)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE chat_id = ?", (chat_id,))
        await db.commit()


async def get_user_by_chat_id(chat_id: str) -> Optional[dict]:
    """Возвращает пользователя по chat_id."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT chat_id, contract_id, contract_title FROM users WHERE chat_id = ?",
            (chat_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"chat_id": row[0], "contract_id": row[1], "contract_title": row[2]}
            return None


async def get_chat_id_by_contract_id(contract_id: str) -> Optional[str]:
    """Возвращает chat_id по contract_id."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT chat_id FROM users WHERE contract_id = ?", (contract_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def get_all_chat_ids() -> list[str]:
    """Возвращает список всех chat_id."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
