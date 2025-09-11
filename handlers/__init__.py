from aiogram import Router
from .auth import register_auth_handlers
from .user import register_user_handlers
from .support import register_support_handlers
from .check import register_check_handlers
from .billing import handle_billing_notification, handle_broadcast_notification

def register_handlers(dp: Dispatcher):
    router = Router()
    register_auth_handlers(router)
    register_user_handlers(router)
    register_support_handlers(router)
    register_check_handlers(router)
    dp.include_router(router)