from aiogram import Dispatcher
from .auth import router as auth_router
from .user import router as user_router
from .support import router as support_router
from .check import router as check_router
from .billing import handle_billing_notification, handle_broadcast_notification

def register_handlers(dp: Dispatcher):
    dp.include_router(auth_router)
    dp.include_router(user_router)
    dp.include_router(support_router)
    dp.include_router(check_router)