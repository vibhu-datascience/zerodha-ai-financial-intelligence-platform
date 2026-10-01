from pydantic import BaseModel, Field


# =====================================================
# PORTFOLIO ANALYSIS REQUEST
# =====================================================

class PortfolioAnalysisRequest(BaseModel):

    portfolio_name: str

    timeframe: str


# =====================================================
# HOLDING ANALYSIS RESPONSE
# =====================================================

class HoldingAnalysisResponse(BaseModel):

    symbol: str

    quantity: float

    buy_price: float

    current_price: float

    invested_value: float

    current_value: float

    profit_loss: float


# =====================================================
# PORTFOLIO ANALYSIS RESPONSE
# =====================================================

class PortfolioAnalysisResponse(BaseModel):

    message: str

    portfolio_name: str

    timeframe: str

    total_value: float

    current_value: float

    profit_loss: float

    risk_level: str

    overall_return: str

    holdings: list[HoldingAnalysisResponse] = []

    insight: str


# =====================================================
# PORTFOLIO RESPONSE
# =====================================================

class PortfolioResponse(BaseModel):

    portfolio_name: str

    total_value: float

    day_change: str


# =====================================================
# HOLDING CREATE
# =====================================================

class HoldingCreate(BaseModel):

    symbol: str = Field(
        ...,
        min_length=1
    )

    quantity: float = Field(
        ...,
        gt=0
    )

    buy_price: float = Field(
        ...,
        gt=0
    )

    sector: str | None = None


# =====================================================
# HOLDING UPDATE
# =====================================================

class HoldingUpdate(BaseModel):

    symbol: str = Field(
        ...,
        min_length=1
    )

    quantity: float = Field(
        ...,
        gt=0
    )

    buy_price: float = Field(
        ...,
        gt=0
    )

    sector: str | None = None


# =====================================================
# HOLDING CRUD RESPONSE
# =====================================================

class HoldingResponse(BaseModel):

    id: int

    symbol: str

    quantity: float

    buy_price: float

    sector: str | None = None

    invested_value: float