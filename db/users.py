# db/users.py
import aiosqlite
import os
from typing import Optional, List, Dict, Any
from config import DB_PATH

# --- SQL для инициализации таблицы ---
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    contract_title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

async def init_users_table() -> None:
    """
    Создает таблицу users, если она не существует.
    Также гарантирует, что директория для базы создана.
    """
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()

# --- CRUD операции ---

async def add_user(chat_id: int, contract_id: int, contract_title: str) -> None:
    """
    Добавляет или обновляет пользователя в таблице users.
    Если chat_id уже существует — обновляет contract_id и contract_title.
    """
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

async def get_user(chat_id: int) -> Optional[Dict[str, Any]]:
    """
    Возвращает информацию о пользователе по chat_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT chat_id, contract_id, contract_title, created_at FROM users WHERE chat_id = ?",
            (chat_id,),
        )
        row = await cursor.fetchone()
        if row:
            return {
                "chat_id": row[0],
                "contract_id": row[1],
                "contract_title": row[2],
                "created_at": row[3],
            }
        return None

async def delete_user(chat_id: int) -> None:
    """
    Удаляет пользователя из таблицы users по chat_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE chat_id = ?", (chat_id,))
        await db.commit()

async def get_chat_id_by_contract_id(contract_id: int) -> Optional[int]:
    """
    Возвращает chat_id по contract_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT chat_id FROM users WHERE contract_id = ?", (contract_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None

async def get_all_chat_ids() -> List[int]:
    """
    Возвращает список всех chat_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT chat_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows] if rows else []