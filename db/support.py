# db/support.py
import aiosqlite
import os
from config import DB_PATH
from typing import Optional


async def init_support_table() -> None:
    """Создание таблицы для хранения обращений в техподдержку."""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS support (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_chat_id TEXT NOT NULL,
                support_message_id INTEGER NOT NULL,
                support_message TEXT NOT NULL,
                admin_message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def save_support_request(user_chat_id: str, support_message: str) -> int:
    """Сохраняет обращение пользователя и возвращает ID записи."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO support (user_chat_id, support_message_id, support_message) VALUES (?, ?, ?)",
            (user_chat_id, 0, support_message),  # временно support_message_id=0, обновим позже
        )
        await db.commit()
        return cursor.lastrowid


async def update_support_message_id(request_id: int, support_message_id: int) -> None:
    """Обновляет support_message_id после отправки в чат поддержки."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE support SET support_message_id = ? WHERE id = ?",
            (support_message_id, request_id)
        )
        await db.commit()


async def get_chat_id_by_support_message_id(support_message_id: int) -> Optional[str]:
    """Возвращает user_chat_id по message_id в чате поддержки."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_chat_id FROM support WHERE support_message_id = ?",
            (support_message_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def get_last_support_message_id(user_chat_id: str) -> Optional[int]:
    """Возвращает последний support_message_id в чате поддержки для данного пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT support_message_id
            FROM support
            WHERE user_chat_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_chat_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def link_admin_message(support_message_id: int, admin_message_id: int) -> None:
    """Привязка сообщения админа к тикету"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE support SET admin_message_id = ? WHERE support_message_id = ?",
            (admin_message_id, support_message_id)
        )
        await db.commit()
