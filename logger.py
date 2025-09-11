import logging
import os
from datetime import datetime
import contextvars
from config import LOG_DIR, LOG_FILE

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
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logger
logger = logging.getLogger("cable_bot")
logger.setLevel(logging.INFO)

# Prevent adding handlers multiple times
if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - chat_id:%(chat_id)s - %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers and filter
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addFilter(ChatIDFilter())