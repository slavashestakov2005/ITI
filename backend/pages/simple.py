"""Тестовые страницы."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

router = APIRouter()


@router.get("/example", response_class=HTMLResponse)
async def get_example():
    """Пример html страницы."""
    return """<html>
    <body>
        <h1>Hello FastApi!</h1>
    </body>
</html>"""


class Item(BaseModel):
    """Пример класса с которым будет работать api."""

    name: str
    price: float


@router.get("/example_item")
def get_item():
    """Пример возвращения класса."""
    return Item(name="name", price=3.14)
