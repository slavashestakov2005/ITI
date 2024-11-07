from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from .help import is_admin
from .keyboards import admin_main_keyboard, contact_keyboard


simple_router = Router()


@simple_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    
    kb = contact_keyboard()
    if await is_admin(message.from_user.id):
        kb = admin_main_keyboard()
    return await message.answer(f"Отменено.", reply_markup=kb)


@simple_router.message(F.text == "/start")
async def cmd_user_rules(message: Message):
    if await is_admin(message.from_user.id):
        return await message.answer(f'''
<b>Вы администратор</b>
''',
            parse_mode="HTML",
            reply_markup=admin_main_keyboard())
    
    await message.answer(f'''
<b>ИТИ!!!</b>
''',
        parse_mode="HTML",
        reply_markup=contact_keyboard())
