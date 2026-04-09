from functools import lru_cache
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from config import PASSWORD_ENCRYPTION_KEY
from logger import logger

ENC_PREFIX = "enc:"


@lru_cache(maxsize=1)
def _get_fernet() -> Optional[Fernet]:
    """
    Возвращает объект Fernet из ключа окружения.
    Если ключ не задан — возвращает None (backward-compatible режим).
    """
    if not PASSWORD_ENCRYPTION_KEY:
        logger.warning(
            "PASSWORD_ENCRYPTION_KEY не задан. Пароли будут храниться в открытом виде."
        )
        return None

    try:
        return Fernet(PASSWORD_ENCRYPTION_KEY.encode("utf-8"))
    except Exception as exc:
        logger.error(f"Некорректный PASSWORD_ENCRYPTION_KEY: {exc}")
        return None


def encrypt_password(plain_password: str) -> str:
    """
    Шифрует пароль для хранения в БД.
    Формат хранения: 'enc:<token>'.
    """
    fernet = _get_fernet()
    if not fernet:
        return plain_password

    token = fernet.encrypt(plain_password.encode("utf-8")).decode("utf-8")
    return f"{ENC_PREFIX}{token}"


def decrypt_password(stored_password: Optional[str]) -> str:
    """
    Расшифровывает пароль из БД.
    Поддерживает legacy-значения (без ENC_PREFIX) как plaintext.
    """
    if not stored_password:
        return ""

    if not stored_password.startswith(ENC_PREFIX):
        return stored_password

    token = stored_password[len(ENC_PREFIX):]
    fernet = _get_fernet()
    if not fernet:
        logger.error("Невозможно расшифровать пароль: PASSWORD_ENCRYPTION_KEY не задан")
        return ""

    try:
        return fernet.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        logger.error("Невозможно расшифровать пароль: invalid token/key mismatch")
        return ""
    except Exception as exc:
        logger.error(f"Ошибка расшифровки пароля: {exc}")
        return ""
