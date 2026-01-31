"""Тестовые страницы."""

from database import engine
from fastapi import APIRouter, UploadFile, status
from fastapi.exceptions import HTTPException
from models import News
from PIL import Image
from sqlmodel import Session

router = APIRouter()


@router.post("/api/news/create")
def create(title: str, text: str, image: UploadFile | None = None) -> None:
    """Создать пост."""
    post = News(title=title, text=text)
    if image is None:
        post.has_image = False
    else:
        if image.content_type in ["image/jpeg", "image/png", "image/webp", "image/svg+xml"]:
            post.has_image = True
        else:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file must be image")
    with Session(engine) as session:
        session.add(post)
        session.commit()
        Image.open(image.file).save(f"static/news_images/{post.id}.webp")
