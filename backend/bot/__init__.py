from aiogram import Bot, Dispatcher
import asyncio

from backend.bot.config import Config


API_TOKEN = Config.TELEGRAM_TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def start_bot():
    from backend.bot.auth import auth_router
    from backend.bot.cmds_admin_chat import admin_chat_router
    from backend.bot.cmds_admin import admin_router
    from backend.bot.cmds_simple import simple_router
    from backend.bot.cmds_user import user_router

    dp.include_routers(simple_router)
    dp.include_routers(auth_router)
    dp.include_routers(user_router)
    dp.include_routers(admin_router)
    dp.include_router(admin_chat_router)
    
    asyncio.run(dp.start_polling(bot))
