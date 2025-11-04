"""FastApi обработчики, возвращающие html страницы."""

from fastapi import APIRouter

from pages.simple import router as simple_router

router = APIRouter()
router.include_router(simple_router)

__all__ = ["router"]
