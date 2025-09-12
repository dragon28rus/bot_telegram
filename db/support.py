# db/support.py
import aiosqlite
import os
from config import DB_PATH

async def init_support_table() -> None:
    """Создание таблицы для хранения обращений в техподдержку."""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS support_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_chat_id TEXT NOT NULL,
                support_message_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def save_support_request(user_chat_id: str, support_message_id: int) -> None:
    """
    Сохраняет обращение пользователя в таблицу support_requests.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO support_requests (user_chat_id, support_message_id) VALUES (?, ?)",
            (user_chat_id, support_message_id),
        )
        await db.commit()


async def get_chat_id_by_support_message_id(support_message_id: int) -> str | None:
    """
    Возвращает chat_id пользователя по message_id в чате поддержки.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_chat_id FROM support_requests WHERE support_message_id = ?",
            (support_message_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
