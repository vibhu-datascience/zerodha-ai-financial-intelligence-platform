from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User

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
    current_user=Depends(get_current_user)
):

    # -------------------------------------------------
    # get_current_user returns JWT payload:
    #
    # {
    #     "user_id": 1,
    #     "username": "demo_user1"
    # }
    # -------------------------------------------------

    if not isinstance(current_user, dict):
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user."
        )

    user_id = current_user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID missing from authentication token."
        )

    # -------------------------------------------------
    # Verify user exists
    # -------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user was not found."
        )

    # -------------------------------------------------
    # Generate USER-SCOPED financial intelligence
    # -------------------------------------------------

    service = FinancialIntelligenceService(db)

    return service.generate_financial_intelligence(
        portfolio_name=portfolio_name,
        timeframe=timeframe,
        user_id=user.id
    )
