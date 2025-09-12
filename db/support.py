import aiosqlite
from config import DB_PATH
from typing import Optional

async def init_support_table():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS support (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_chat_id TEXT NOT NULL,
            contract_title TEXT,
            support_message_id INTEGER NOT NULL,
            support_message TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            admin_message_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await db.commit()


async def save_support_request(user_chat_id: int, contract_title: str, support_message_id: int,
                               support_message: str, message_type: str = "text") -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO support (user_chat_id, contract_title, support_message_id, support_message, message_type)
            VALUES (?, ?, ?, ?, ?)
        """, (user_chat_id, contract_title, support_message_id, support_message, message_type))
        await db.commit()
        return cursor.lastrowid


async def link_admin_message(support_message_id: int, admin_message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE support SET admin_message_id = ? WHERE support_message_id = ?
        """, (admin_message_id, support_message_id))
        await db.commit()


async def get_chat_id_by_support_message_id(support_message_id: int) -> Optional[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_chat_id FROM support WHERE support_message_id = ?
        """, (support_message_id,))
        row = await cursor.fetchone()
        return row[0] if row else None
