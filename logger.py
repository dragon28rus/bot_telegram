# logger.py
import logging
import os
import contextvars
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL, LOG_DIR, LOG_FILE

# --- Context variable for chat_id ---
_current_chat_id: contextvars.ContextVar[str] = contextvars.ContextVar("chat_id", default="unknown")

def set_chat_id(chat_id: str):
    """
    Устанавливает chat_id в текущем контексте.
    Это удобно для асинхронного кода, чтобы в логах было видно,
    к какому пользователю относится запись.
    """
    _current_chat_id.set(str(chat_id))

class ChatIdFormatter(logging.Formatter):
    """Форматтер, который всегда добавляет chat_id (даже если его нет)"""
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "chat_id"):
            try:
                record.chat_id = _current_chat_id.get()
            except LookupError:
                record.chat_id = "unknown"
        return super().format(record)

# --- Настройка логов ---
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE)

# Обработчики: файл с ротацией + консоль
file_handler = RotatingFileHandler(
    log_path,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,             # хранить 5 старых файлов
    encoding="utf-8"
)

console_handler = logging.StreamHandler()

# Общий формат
fmt = "%(asctime)s [%(levelname)s] [chat_id=%(chat_id)s] %(name)s: %(message)s"
formatter = ChatIdFormatter(fmt)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Настройка root-логгера
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    handlers=[file_handler, console_handler],
)

# Основной логгер проекта
logger = logging.getLogger("bot")