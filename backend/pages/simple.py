"""Тестовые страницы."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

router = APIRouter()


@router.get("/example", response_class=HTMLResponse)
async def get_example() -> str:
    """Пример html страницы."""
    text = """<html>
    <body>
        <h1>Hello FastApi!</h1>
    </body>
</html>"""
    return text


class ExampleItem(BaseModel):
    """Пример класса с которым будет работать api."""

    name: str
    price: float


@router.get("/example_item")
def get_item() -> ExampleItem:
    """Пример возвращения класса."""
    return ExampleItem(name="name", price=3)
