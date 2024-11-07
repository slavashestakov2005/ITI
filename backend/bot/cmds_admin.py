from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
import os

from .db_functions import get_feedback
from .help import is_admin
from .keyboards import create_feedback_keyboard
from . import bot


admin_router = Router()


@admin_router.message(F.text == "Отзывы")
async def cmd_user_account(message: Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("У вас нет прав")
    
    page = 1
    keyboard = await create_feedback_keyboard(page)
    await message.answer("Вот отзывы:", reply_markup=keyboard)


@admin_router.callback_query(F.data.startswith('feedback_page_'))
async def process_feedback_page(callback_query: CallbackQuery):
    page = int(callback_query.data.split('_')[-1])
    keyboard = await create_feedback_keyboard(page)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@admin_router.callback_query(F.data.startswith('feedback_'))
async def feedback_by_user(callback_query: CallbackQuery):
    id = int(callback_query.data.split('_')[-1])
    feedback = await get_feedback(id)
    
    await bot.send_message(callback_query.from_user.id, f'''
<a href="tg://user?id={feedback.telegram_id}">Профиль пользователя</a>
Дата и время: {feedback.timestamp.strftime("%d.%m.%Y %H:%M")}
Сообщение: {feedback.message}
''', parse_mode="HTML")


@admin_router.message(F.text == "Список админов")
async def cmd_user_account(message: Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("У вас нет прав")
    
    return await message.answer("Пока не готово")


@admin_router.message(F.text == "Узнать PID")
async def cmd_user_account(message: Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("У вас нет прав")
    
    return await message.answer(f"Бот запущен в процессе pid={os.getpid()}")


@admin_router.message(F.text == "Остановить бота")
async def cmd_user_account(message: Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("У вас нет прав")
    
    await message.answer("Бот остановлен!")
    exit()
