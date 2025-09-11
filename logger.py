import logging
import os
import contextvars
from logging.handlers import RotatingFileHandler
from config import LOG_DIR, LOG_FILE, LOG_LEVEL

# Context variable for chat_id
_current_chat_id: contextvars.ContextVar[str] = contextvars.ContextVar("chat_id", default="unknown")


def set_chat_id(chat_id):
    """Set chat_id for logging in current context."""
    _current_chat_id.set(str(chat_id))


class ChatIDFilter(logging.Filter):
    def filter(self, record):
        record.chat_id = _current_chat_id.get()
        return True


# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Full log path
log_path = os.path.join(LOG_DIR, LOG_FILE)

# Configure logger
logger = logging.getLogger("cable_bot")
logger.setLevel(LOG_LEVEL)

# Prevent adding handlers multiple times
if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - chat_id:%(chat_id)s - %(message)s"
    )

    # File handler with rotation (5 MB, 5 backups)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)

    # Add handlers and filter
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addFilter(ChatIDFilter())
