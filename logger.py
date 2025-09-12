import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL, LOG_DIR, LOG_FILE

# Убедимся, что директория для логов существует
os.makedirs(LOG_DIR, exist_ok=True)

# Полный путь к файлу логов
log_path = os.path.join(LOG_DIR, LOG_FILE)

# Формат логов
LOG_FORMAT = "%(asctime)s [%(levelname)s] [chat_id=%(chat_id)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ChatIDFilter(logging.Filter):
    """
    Добавляет поле chat_id в записи лога (по умолчанию 'unknown'),
    чтобы не падал форматтер.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "chat_id"):
            record.chat_id = "unknown"
        return True


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

    # Добавляем хендлеры (только если они ещё не добавлены)
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# Глобальный логгер для проекта
logger = get_logger()