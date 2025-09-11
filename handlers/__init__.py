<<<<<<< HEAD
from aiogram import Dispatcher

=======
>>>>>>> d6abbb87cf2476e7ee56460275e748e499ad14ed
from .auth import router as auth_router
from .check import router as check_router
from .support import router as support_router
from .user import router as user_router
<<<<<<< HEAD
=======

>>>>>>> d6abbb87cf2476e7ee56460275e748e499ad14ed
from .billing import handle_billing_notification, handle_broadcast_notification


def register_handlers(dp: Dispatcher):
    dp.include_router(auth_router)
    dp.include_router(check_router)
    dp.include_router(support_router)
    dp.include_router(user_router)