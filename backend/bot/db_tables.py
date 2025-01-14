from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker

from .config import Config


class BotBase(DeclarativeBase, AsyncAttrs):
    id: Mapped[int] = mapped_column(primary_key=True)


class BotAdmin(BotBase):
    __tablename__ = 'bot_admins'

    full_name: Mapped[str] = mapped_column(String(50))
    telegram_id: Mapped[int] = mapped_column()


class BotFeedback(BotBase):
    __tablename__ = 'bot_feedbacks'

    telegram_id: Mapped[int] = mapped_column()
    message: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class BotProblem(BotBase):
    __tablename__ = 'bot_problems'

    telegram_id: Mapped[int] = mapped_column()
    message: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


engine = create_async_engine(url='sqlite+aiosqlite:///{}'.format(Config.DB))
async_session = async_sessionmaker(engine)
