from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User

from app.dependencies.auth import get_current_user

from app.services.portfolio_service import PortfolioService

from app.schemas.portfolio_schema import (
    PortfolioResponse,
    PortfolioAnalysisRequest,
    PortfolioAnalysisResponse,
    HoldingCreate,
    HoldingUpdate,
    HoldingResponse
)


router = APIRouter()


# =====================================================
# GET PORTFOLIO
# =====================================================

@router.get(
    "/portfolio",
    response_model=PortfolioResponse
)
def get_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    portfolio_service = PortfolioService(db)

    return portfolio_service.get_portfolio(
        user_id=current_user.id
    )


# =====================================================
# GET HOLDINGS
# =====================================================

@router.get(
    "/holdings",
    response_model=list[HoldingResponse]
)
def get_holdings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    portfolio_service = PortfolioService(db)

    return portfolio_service.get_holdings(
        user_id=current_user.id
    )


# =====================================================
# ADD HOLDING
# =====================================================

@router.post(
    "/holdings",
    response_model=HoldingResponse
)
def add_holding(
    request: HoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    portfolio_service = PortfolioService(db)

    return portfolio_service.add_holding(
        user_id=current_user.id,
        symbol=request.symbol,
        quantity=request.quantity,
        buy_price=request.buy_price,
        sector=request.sector
    )


# =====================================================
# UPDATE HOLDING
# =====================================================

@router.put(
    "/holdings/{holding_id}",
    response_model=HoldingResponse
)
def update_holding(
    holding_id: int,
    request: HoldingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    portfolio_service = PortfolioService(db)

    result = portfolio_service.update_holding(
        user_id=current_user.id,
        holding_id=holding_id,
        symbol=request.symbol,
        quantity=request.quantity,
        buy_price=request.buy_price,
        sector=request.sector
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="Holding not found."
        )

    return result


# =====================================================
# DELETE HOLDING
# =====================================================

@router.delete(
    "/holdings/{holding_id}"
)
def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    portfolio_service = PortfolioService(db)

    result = portfolio_service.delete_holding(
        user_id=current_user.id,
        holding_id=holding_id
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail="Holding not found."
        )

    return {
        "message": "Holding deleted successfully."
    }


# =====================================================
# PORTFOLIO ANALYSIS
# =====================================================

@router.post(
    "/portfolio-analysis",
    response_model=PortfolioAnalysisResponse
)
def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    portfolio_service = PortfolioService(db)

    return portfolio_service.analyze_portfolio(
        request.portfolio_name,
        request.timeframe,
        user_id=current_user.id
    )