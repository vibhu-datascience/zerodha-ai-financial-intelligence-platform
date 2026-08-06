from fastapi import APIRouter
from app.services.news_service import NewsService

router = APIRouter()

news_service = NewsService()

@router.get("/news")
def get_news():
    return news_service.get_news()



