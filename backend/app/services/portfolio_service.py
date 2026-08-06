from app.services.market_service import MarketService

class PortfolioService:
    def __init__(self):
        self.market_service = MarketService()

    def get_portfolio(self):
        market = self.market_service.get_market_status()
        return {
            "portfolio_name": "Growth Portfolio",
            "total_value": 850000,
            "day_change": "+2.3%",
            "market": market
        }
    