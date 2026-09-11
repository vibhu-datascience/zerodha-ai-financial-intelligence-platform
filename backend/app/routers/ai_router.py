from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.portfolio_service import PortfolioService


router = APIRouter()


@router.post("/ai/portfolio-insight")
def generate_portfolio_insight(
    portfolio_name: str,
    timeframe: str,
    db: Session = Depends(get_db)
):

    portfolio_service = PortfolioService(db)

    result = portfolio_service.analyze_portfolio(
        portfolio_name=portfolio_name,
        timeframe=timeframe
    )

    return result