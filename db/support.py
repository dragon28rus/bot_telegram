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

async def save_support_request(
    chat_id: int,
    contract_title: Optional[str],
    support_message_id: int,
    admin_message_id: int,
    message_text: Optional[str]
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO support (user_chat_id, contract_title, support_message_id, admin_message_id, support_message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (chat_id, contract_title, support_message_id, admin_message_id, message_text)
        )
        await db.commit()



async def link_admin_message(support_message_id: int, admin_message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE support SET admin_message_id = ? WHERE support_message_id = ?
        """, (admin_message_id, support_message_id))
        await db.commit()


async def get_chat_id_by_support_message_id(support_message_id: int) -> Optional[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_chat_id FROM support WHERE admin_message_id = ?
        """, (support_message_id,))
        row = await cursor.fetchone()
        return row[0] if row else None
    
async def get_support_message_id_by_admin_message_id(admin_message_id: int):
    """
    Возвращает support_message_id (исходное сообщение пользователя),
    связанное с admin_message_id (ответ оператора).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT support_message_id FROM support WHERE admin_message_id = ?",
            (admin_message_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
