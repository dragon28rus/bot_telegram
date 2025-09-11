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

class ChatIdFilter(logging.Filter):
    """
    Кастомный фильтр для добавления chat_id из contextvars в каждую запись лога.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        record.chat_id = _current_chat_id.get()
        return True

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

# Базовая конфигурация
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] [chat_id=%(chat_id)s] %(name)s: %(message)s",
    handlers=[file_handler, console_handler]
)

# Создаём логгер
logger = logging.getLogger("bot")
logger.addFilter(ChatIdFilter())