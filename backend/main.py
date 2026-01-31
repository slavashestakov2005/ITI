"""Создаёт экземпляр приложения."""

from fastapi import FastAPI
from news import router

app = FastAPI()

app.include_router(router)
