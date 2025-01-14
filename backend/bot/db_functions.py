from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy import update

from .db_tables import *


async def add_admin(full_name: str, tg_id: int) -> BotAdmin:
    async with async_session() as session:
        async with session.begin():
            new_admin = BotAdmin(
                full_name=full_name,
                telegram_id=tg_id
            )
            session.add(new_admin)
        await session.commit()
        return new_admin


async def update_admin_name(tg_id: int, new_name: str) -> None:
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(BotAdmin)
                .where(BotAdmin.telegram_id == tg_id)
                .values(full_name=new_name)
            )
        await session.commit()


async def get_all_admin_telegram_ids() -> list[int]:
    async with async_session() as session:
        result = await session.execute(select(BotAdmin.telegram_id))
        telegram_ids = [row[0] for row in result.all()]
        return telegram_ids


async def add_feedback(tg_id: int, message: str) -> int:
    async with async_session() as session:
        async with session.begin():
            new_feedback = BotFeedback(
                telegram_id=tg_id,
                message=message,
                timestamp=datetime.now()
            )
            session.add(new_feedback)
            await session.flush()
            await session.refresh(new_feedback)
            feedback_id = new_feedback.id
        await session.commit()
        return feedback_id


async def get_feedback(id: int) -> BotFeedback:
    async with async_session() as session:
        result = await session.execute(select(BotFeedback).where(BotFeedback.id == id))
        res = result.scalars().first()
        return res


async def get_all_feedback() -> list[BotFeedback]:
    async with async_session() as session:
        result = await session.execute(select(BotFeedback))
        feedback_list = result.scalars().all()
        return feedback_list


async def get_feedback_page(page: int) -> list[BotFeedback]:
    items_per_page = 5
    offset_value = (page - 1) * items_per_page
    
    async with async_session() as session:
        result = await session.execute(
            select(BotFeedback)
            .order_by(BotFeedback.id.desc())
            .limit(items_per_page)
            .offset(offset_value)
        )
        feedback_list = result.scalars().all()
        return feedback_list


async def get_feedback_count() -> int:
    async with async_session() as session:
        result = await session.execute(select(BotFeedback))
        return len(result.scalars().all())


async def add_problem(tg_id: int, message: str) -> int:
    async with async_session() as session:
        async with session.begin():
            new_problem = BotProblem(
                telegram_id=tg_id,
                message=message,
                timestamp=datetime.now()
            )
            session.add(new_problem)
            await session.flush()
            await session.refresh(new_problem)
            problem_id = new_problem.id
        await session.commit()
        return problem_id


async def get_problem(id: int) -> BotProblem:
    async with async_session() as session:
        result = await session.execute(select(BotProblem).where(BotProblem.id == id))
        res = result.scalars().first()
        return res
