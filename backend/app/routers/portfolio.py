from fastapi import APIRouter
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio_schema import(PortfolioResponse,
                                         PortfolioAnalysisRequest,
                                         PortfolioAnalysisResponse)


router = APIRouter()

portfolio_service = PortfolioService()

@router.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio():
    return portfolio_service.get_portfolio()

@router.post("/portfolio-analysis", response_model=PortfolioAnalysisResponse)
def analyze_portfolio(request: PortfolioAnalysisRequest):
    return{
        "message": "Portfolio analysis started",
        "portfolio_name": request.portfolio_name,
        "timeframe": request.timeframe
    }