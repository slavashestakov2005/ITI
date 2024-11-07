from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .queries import get_student
from ..eljur import ConfigEljur


auth_router = Router()


class user(StatesGroup):
    login_eljur = State()
    created = State()


@auth_router.message(F.text == "/auth")
async def cmd_user_rules(message: Message, state: FSMContext):
    url = ConfigEljur.OAUTH_ELJUR_PAGE_TG.format(message.from_user.id)
    await message.answer(f'''
Зайдите в элжур по <a href="{url}">ссылке</a>. Когда зайдёте - напишите.
''', parse_mode="HTML")

    await state.set_state(user.login_eljur)


@auth_router.message(user.login_eljur)
async def get_login(message: Message, state: FSMContext) -> None:
    text = message.text
    
    find = get_student(message.from_user.id)
    if find is None:
        await message.answer(f'''
Вам не удалось зайти на сайт ИТИ через Eljur. Для повтора /auth
''', parse_mode="HTML")
        return await state.clear()
    else:
        await message.answer(f'''
Вы зашли на сайт ИТИ и в бота через Eljur
''', parse_mode="HTML")
        return await state.clear()
