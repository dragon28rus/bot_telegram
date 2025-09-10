#### handlers/__init__.py
from .auth import register_auth_handlers
from .user import register_user_handlers
from .support import register_support_handlers
from .check import check_bot
from .billing import handle_billing_notification, handle_broadcast_notification

def register_handlers(dp):
    """
    Регистрирует все хэндлеры для диспетчера.

    Args:
        dp: Dispatcher объект для регистрации хэндлеров
    """
    register_auth_handlers(dp)
    register_user_handlers(dp)
    register_support_handlers(dp)
    dp.register_message_handler(check_bot, commands=['check_bot'])
