"""
Одноразовая миграция:
- находит plaintext-пароли в таблице users
- шифрует их через services.security.encrypt_password()
- сохраняет обратно в БД

Запуск:
    python -m scripts.migrate_encrypt_passwords
"""

import asyncio
import pathlib
import sys

import aiosqlite

# Обеспечиваем импорт модулей проекта при запуске:
# python -m scripts.migrate_encrypt_passwords
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import DB_PATH
from services.security import encrypt_password, is_encrypted_password, validate_encryption_setup


async def migrate_passwords() -> None:
    validate_encryption_setup(strict=True)

    updated = 0
    skipped = 0

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, password FROM users WHERE password IS NOT NULL") as cursor:
            rows = await cursor.fetchall()

        for user_id, password in rows:
            if not password:
                skipped += 1
                continue

            # Пропускаем только реально зашифрованные значения
            if is_encrypted_password(str(password)):
                skipped += 1
                continue

            encrypted = encrypt_password(str(password))
            await db.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (encrypted, user_id),
            )
            updated += 1

        await db.commit()

    print(f"Migration completed. Updated: {updated}, skipped: {skipped}")


if __name__ == "__main__":
    asyncio.run(migrate_passwords())
