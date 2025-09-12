import logging
import os
import contextvars
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL, LOG_DIR, LOG_FILE

# ContextVar для хранения chat_id
_current_chat_id: contextvars.ContextVar[str] = contextvars.ContextVar("chat_id", default="unknown")

# Убедимся, что директория для логов существует
os.makedirs(LOG_DIR, exist_ok=True)

# Полный путь к файлу логов
log_path = os.path.join(LOG_DIR, LOG_FILE)

# Формат логов
LOG_FORMAT = "%(asctime)s [%(levelname)s] [chat_id=%(chat_id)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ChatIDFilter(logging.Filter):
    """
    Добавляет поле chat_id в записи лога
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.chat_id = _current_chat_id.get("unknown")
        return True


def set_chat_id(chat_id: str) -> None:
    """
    Устанавливает текущий chat_id для логов
    """
    _current_chat_id.set(chat_id)


def get_logger(name: str = "cable_bot") -> logging.Logger:
    """Создаёт и настраивает логгер"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # --- Консольный хендлер ---
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    console_handler.addFilter(ChatIDFilter())

    # --- Файловый хендлер с ротацией ---
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    file_handler.addFilter(ChatIDFilter())

    # Добавляем хендлеры только один раз
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# Глобальный логгер
logger = get_logger()
