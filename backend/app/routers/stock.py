from fastapi import APIRouter
from app.services.stock_service import StockService


router = APIRouter()

stock_service = StockService()


@router.get("/stock-analysis")
def get_stock_analysis(symbol: str):

    return stock_service.analyze_stock(symbol)