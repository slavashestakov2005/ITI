from aiogram import F, Router
from aiogram.types import Message

from . import bot
from .config import Config
from .db_functions import get_feedback, get_problem


async def forward_feedback(feedback_id: int, text: str):
    msg = 'Отзыв #{}:\n{}'.format(feedback_id, text)
    await bot.send_message(chat_id=Config.TELEGRAM_ADMIN_CHAT_FEEDBACK, text=msg)


async def forward_problem(problem_id: int, text: str):
    msg = 'Ошибка #{}:\n{}'.format(problem_id, text)
    await bot.send_message(chat_id=Config.TELEGRAM_ADMIN_CHAT_PROBLEM, text=msg)


admin_chat_router = Router()


async def cmd_admin_chat_reply_feedback(feedback_id: int, answer: Message):
    if not answer.text.startswith('/ans '):
        return answer.answer('Чтобы ответить на отзыв - нужно прописать /ans в начале')
    text = answer.text.replace('/ans ', 'Ответ на ваш отзыв:\n')
    feedback = await get_feedback(feedback_id)
    await bot.send_message(chat_id=feedback.telegram_id, text=text)
    return await answer.answer('Ответ на отзыв #{} отправлен'.format(feedback_id))


async def cmd_admin_chat_reply_problem(problem_id: int, answer: Message):
    if not answer.text.startswith('/ans '):
        return answer.answer('Чтобы ответить на ошибку - нужно прописать /ans в начале')
    text = answer.text.replace('/ans ', 'Ответ на вашу ошибку:\n')
    problem = await get_problem(problem_id)
    await bot.send_message(chat_id=problem.telegram_id, text=text)
    return await answer.answer('Ответ на ошибку #{} отправлен'.format(problem_id))


@admin_chat_router.message(F.chat.id == Config.TELEGRAM_ADMIN_CHAT_FEEDBACK | F.chat.id == Config.TELEGRAM_ADMIN_CHAT_PROBLEM)
async def cmd_admin_chat(message: Message):
    try:
        msg = message.reply_to_message
        if msg.from_user.id != Config.TELEGRAM_BOT_ID:
            return
        reply = msg.text
        reply_id = int(reply.split(':\n')[0].split('#')[1])
        if reply.startswith('Отзыв #') and message.chat.id == Config.TELEGRAM_ADMIN_CHAT_FEEDBACK:
            return await cmd_admin_chat_reply_feedback(reply_id, message)
        if reply.startswith('Ошибка #') and message.chat.id == Config.TELEGRAM_ADMIN_CHAT_PROBLEM:
            return await cmd_admin_chat_reply_problem(reply_id, message)
        return await message.answer('Бот не понял, на какой отзыв/ошибку Вы отвечали')
    except BaseException:
        pass
