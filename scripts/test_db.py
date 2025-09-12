# scripts/test_db.py
import asyncio
from db.users import init_users_table, add_user, get_user_by_chat_id, delete_user, get_all_chat_ids

async def main():
    # Создаём таблицу, если её нет
    await init_users_table()

    test_chat_id = 123456
    test_contract_id = 101252
    test_contract_title = "Тестовый договор"

    print("=== Тест добавления пользователя ===")
    await add_user(test_chat_id, test_contract_id, test_contract_title)

    print("=== Тест получения пользователя ===")
    user = await get_user_by_chat_id(test_chat_id)
    print("Получено:", user)

    print("=== Тест получения всех chat_id ===")
    all_ids = await get_all_chat_ids()
    print("Список chat_id:", all_ids)

    print("=== Тест удаления пользователя ===")
    await delete_user(test_chat_id)

    print("=== Проверка удаления ===")
    user = await get_user_by_chat_id(test_chat_id)
    print("После удаления:", user)

if __name__ == "__main__":
    asyncio.run(main())
