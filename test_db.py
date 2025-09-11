import asyncio
import aiosqlite
from config import DB_PATH
from db import init_db
from logger import logger

async def test_db():
    print(f"Testing database at: {DB_PATH}")
    
    # Инициализируем БД
    await init_db()
    
    # Проверим содержимое
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                tables = await cursor.fetchall()
                print(f"Tables in database: {[table[0] for table in tables]}")
                
            # Попробуем вставить тестовую запись
            await db.execute(
                "INSERT OR REPLACE INTO users (chat_id, contract_id, contract_title) VALUES (?, ?, ?)",
                (123456789, 999, "TEST_CONTRACT")
            )
            await db.commit()
            print("Test record inserted successfully")
            
    except Exception as e:
        print(f"Error testing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())