from fastapi import APIRouter
from app.services.market_service import MarketService
from app.schemas.market_schema import MarketAnalysisResponse

router = APIRouter()

market_service = MarketService()


@router.get("/market")
def get_market():
    return market_service.get_market_status()

@router.get("/market/analysis", response_model=MarketAnalysisResponse)
def get_market_analysis(symbol: str = "^NSEI"):
    return market_service.get_market_analysis(symbol)
