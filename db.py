import aiosqlite
from logger import logger, set_chat_id
from config import DB_PATH


async def init_db():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    contract_id TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS support_requests (
                    chat_id INTEGER,
                    support_message_id INTEGER,
                    PRIMARY KEY (chat_id, support_message_id),
                    FOREIGN KEY (chat_id) REFERENCES users(chat_id) ON DELETE CASCADE
                )
                """
            )
            await db.commit()
        logger.info("chat_id:system - Database initialized")
    except Exception as e:
        logger.error(f"chat_id:system - Error initializing database: {e}")


async def save_support_request(chat_id: int, support_message_id: int):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO support_requests (chat_id, support_message_id) VALUES (?, ?)",
                (chat_id, support_message_id),
            )
            await db.commit()
        logger.info(f"chat_id:{chat_id} - Support request saved with message_id: {support_message_id}")
    except Exception as e:
        logger.error(f"chat_id:{chat_id} - Error saving support request: {e}")


async def get_chat_id_by_support_message_id(support_message_id: int):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT chat_id FROM support_requests WHERE support_message_id = ?",
                (support_message_id,),
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    except Exception as e:
        logger.error(f"chat_id:system - Error retrieving chat_id for support_message_id {support_message_id}: {e}")
        return None


async def save_user(chat_id: int, contract_id: str):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT OR REPLACE INTO users (chat_id, contract_id) VALUES (?, ?)",
                (chat_id, contract_id),
            )
            await db.commit()
        logger.info(f"chat_id:{chat_id} - User saved with contract_id: {contract_id}")
    except Exception as e:
        logger.error(f"chat_id:{chat_id} - Error saving user: {e}")


async def is_user_authorized(chat_id: int) -> bool:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT contract_id FROM users WHERE chat_id = ?", (chat_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result is not None
    except Exception as e:
        logger.error(f"chat_id:{chat_id} - Error checking authorization: {e}")
        return False


async def get_chat_id_by_contract_id(contract_id: str):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT chat_id FROM users WHERE contract_id = ?", (contract_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    except Exception as e:
        logger.error(f"chat_id:system - Error retrieving chat_id for contract_id {contract_id}: {e}")
        return None


async def get_contract_id_by_chat_id(chat_id: int):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT contract_id FROM users WHERE chat_id = ?", (chat_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    except Exception as e:
        logger.error(f"chat_id:{chat_id} - Error retrieving contract_id: {e}")
        return None


async def get_all_chat_ids():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT chat_id FROM users") as cursor:
                result = await cursor.fetchall()
                return [row[0] for row in result]
    except Exception as e:
        logger.error(f"chat_id:system - Error retrieving all chat_ids: {e}")
        return []
