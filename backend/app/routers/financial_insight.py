from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService
)


router = APIRouter()


@router.get("/financial-insight")
def get_financial_insight(
    db: Session = Depends(get_db)
):

    financial_intelligence_service = (
        FinancialIntelligenceService(db)
    )

    return (
        financial_intelligence_service
        .generate_financial_intelligence()
    )