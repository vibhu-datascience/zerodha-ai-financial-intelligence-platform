from pydantic import BaseModel

class PortfolioAnalysisRequest(BaseModel):
    portfolio_name: str
    timeframe: str

class PortfolioAnalysisResponse(BaseModel):
    message: str
    portfolio_name: str
    timeframe: str

class PortfolioResponse(BaseModel):
    portfolio_name: str
    total_value: float
    day_change: str