from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .db_functions import (add_feedback, get_all_admin_telegram_ids)
from .keyboards import create_results_keyboard
from .queries import get_student, get_results_for_student


user_router = Router()


class Feedback(StatesGroup):
    message = State()


async def check_adm(user_id):
    admin_list = await get_all_admin_telegram_ids()
    return user_id in admin_list


@user_router.message(F.text == "Мой аккаунт")
async def cmd_user_account(message: Message):
    if await check_adm(message.from_user.id):
        return await message.answer('Вы являетесь администратором и не можете использовать эту функцию\nПропишите /start чтобы получить клавиатуру для админов')
    
    data = get_student(message.from_user.id)
    if data is None:
        return await message.answer(f'''
Мы не смогли Вас найти, попробуйте сделать /auth ещё раз
''', parse_mode="HTML")
    
    student = data['student']
    name = student['name_1'] + ' ' + student['name_2'] + ' ' + student['name_3']
    role = data['role']

    await message.answer(f'''
Вы: <b>{name}</b>
Ваша роль: <b>{role}</b>
''', parse_mode="HTML")


@user_router.message(F.text == "Мои результаты")
async def cmd_user_results(message: Message):
    if await check_adm(message.from_user.id):
        return await message.answer('Вы являетесь администратором и не можете использовать эту функцию\nПропишите /start чтобы получить клавиатуру для админов')
    
    data = get_student(message.from_user.id)
    if data is None:
        return await message.answer(f'''
Мы не смогли Вас найти, попробуйте сделать /auth ещё раз
''', parse_mode="HTML")

    iti_id = 8
    results = get_results_for_student(data['student']['id'], iti_id)
    await message.reply("Предмет | Место | Баллы | Балл в рейтинг \nВаши результаты:",
                    reply_markup=create_results_keyboard(results))


@user_router.callback_query(F.data == "result_data_hz")
async def call_result_hz(call: CallbackQuery):
    return await call.answer()


@user_router.message(F.text == "Обратная связь")
async def cmd_user_feedback(message: Message, state: FSMContext) -> None:
    if await check_adm(message.from_user.id):
        return await message.answer('Вы являетесь администратором и не можете использовать эту функцию\nПропишите /start чтобы получить клавиатуру для админов')
    
    await message.answer('Отправьте вашу проблему. Для отмены введите /cancel')
    await state.set_state(Feedback.message)


@user_router.message(Feedback.message)
async def cmd_user_process_problem(message: Message, state: FSMContext) -> None:
    if await check_adm(message.from_user.id):
        return await message.answer('Вы являетесь администратором и не можете использовать эту функцию\nПропишите /start чтобы получить клавиатуру для админов')
    
    feedback_text = message.text
    await add_feedback(message.from_user.id, feedback_text)
    await message.answer("Ваша обратная связь принята.")
    await state.clear()
