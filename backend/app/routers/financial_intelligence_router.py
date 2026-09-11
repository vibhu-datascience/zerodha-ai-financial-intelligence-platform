from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService
)
from app.services.auth_dependency import (
    get_current_user
)


router = APIRouter()


@router.get("/financial-intelligence")
def get_financial_intelligence(
    portfolio_name: str = "Growth Portfolio",
    timeframe: str = "1Y",
    db: Session = Depends(get_db),
    current_user: str = Depends(
        get_current_user
    )
):

    service = FinancialIntelligenceService(db)

    return service.generate_financial_intelligence(
        portfolio_name=portfolio_name,
        timeframe=timeframe
    )