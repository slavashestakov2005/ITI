from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from .db_functions import get_feedback_page, get_feedback_count


def contact_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Мой аккаунт')
            ],
            [
                KeyboardButton(text='Мои результаты')
            ],
            [
                KeyboardButton(text='Обратная связь')
            ]
        ],
        resize_keyboard=True
    )
    return markup


def admin_main_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Отзывы')
            ],
            [
                KeyboardButton(text='Список админов')
            ],
            [
                KeyboardButton(text='Узнать PID')
            ],
            [
                KeyboardButton(text='Остановить бота')
            ]
        ],
        resize_keyboard=True
    )
    return markup


def user_createdcreate_inline_keyboard():
    kb_list = [
        [InlineKeyboardButton(text="Да", callback_data='replace_auth_yes')],
        [InlineKeyboardButton(text="Нет", callback_data='replace_auth_no')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard


def create_results_keyboard(data: list) -> InlineKeyboardMarkup:
    kb_list = []
    
    for a, b, c, d in data:
        kb_list.append([
            InlineKeyboardButton(text=f"{a} | {b} | {c} | {d}",
                                 callback_data='result_data_hz')])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard


async def create_feedback_keyboard(page: int) -> InlineKeyboardMarkup:
    kb_list = []
    
    feedback_list = await get_feedback_page(page)
    for feedback in feedback_list:
        button = InlineKeyboardButton(text=feedback.message, callback_data=f'feedback_{feedback.id}')
        kb_list.append([button])

    total_feedback_count = await get_feedback_count()
    total_pages = (total_feedback_count + 5 - 1) // 5

    arr = []
    if page > 1:
        prev_button = InlineKeyboardButton(text='◀️ Предыдущая', callback_data=f'feedback_page_{page - 1}')
        arr.append(prev_button)

    if page < total_pages:
        next_button = InlineKeyboardButton(text='Следующая ▶️', callback_data=f'feedback_page_{page + 1}')
        arr.append(next_button)
    kb_list.append(arr)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard
