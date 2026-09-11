from pydantic import BaseModel


class MarketAnalysisResponse(BaseModel):
    symbol: str
    close: float
    daily_return: float
    volatility: float
    trend: str
    rsi: float
    rsi_signal: str
    macd: float
    macd_signal: float
    macd_trend: str
    signal_score: int
    overall_signal: str
    market_insight: str