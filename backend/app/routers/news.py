from fastapi import APIRouter
from app.services.news_service import NewsService

router = APIRouter()

news_service = NewsService()

@router.get("/news")
def get_news():
    return news_service.get_news()

@router.get("/news/sentiment")
def get_news_sentiment():
    return news_service.get_overall_sentiment()



