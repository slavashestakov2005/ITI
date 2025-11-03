"""Создаёт экземпляр приложения."""

from fastapi import FastAPI

from pages import router as pages_router

app = FastAPI()
app.include_router(pages_router)
