from fastapi import APIRouter, Depends

from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio_schema import (
    PortfolioResponse,
    PortfolioAnalysisRequest,
    PortfolioAnalysisResponse
)

from app.database.database import get_db


router = APIRouter()


@router.get(
    "/portfolio",
    response_model=PortfolioResponse
)
def get_portfolio(db=Depends(get_db)):

    portfolio_service = PortfolioService(db)

    return portfolio_service.get_portfolio()


@router.post(
    "/portfolio-analysis",
    response_model=PortfolioAnalysisResponse
)
def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    db=Depends(get_db)
):

    portfolio_service = PortfolioService(db)

    return portfolio_service.analyze_portfolio(
        request.portfolio_name,
        request.timeframe
    )