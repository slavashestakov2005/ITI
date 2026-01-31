"""FastApi обработчики, возвращающие html страницы."""

from fastapi import APIRouter
from news.create import router as create_router

router = APIRouter()
router.include_router(create_router)

__all__ = ["router"]
