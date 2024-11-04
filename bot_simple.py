import os
from dotenv import load_dotenv
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv('.env')


from aiogram import Bot, Dispatcher
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import asyncio


def contact_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Мой аккаунт')
            ],
            [
                KeyboardButton(text='Обратная связь')
            ]
        ],
        resize_keyboard=True
    )
    return markup


API_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()


@router.message(F.text == "/start")
async def cmd_user_rules(message: Message):
    await message.answer('<b>ИТИ!!!</b>',
        parse_mode="HTML",
        reply_markup=contact_keyboard())


def start_bot():
    dp.include_routers(router)
    asyncio.run(dp.start_polling(bot))

    
if '__main__' == __name__:
    start_bot()
