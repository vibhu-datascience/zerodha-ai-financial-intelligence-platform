from fastapi import APIRouter
from app.services.market_service import MarketService

router = APIRouter()

market_service = MarketService()


@router.get("/market")
def get_market():
    return market_service.get_market_status()
