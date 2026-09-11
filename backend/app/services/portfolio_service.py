from app.services.market_service import MarketService
from app.database.models import Portfolio
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService


class PortfolioService:

    def __init__(self, db):

        self.db = db

        self.market_service = MarketService()

        self.ai_service = AIService()

        self.analytics_service = AnalyticsService()

    # =====================================================
    # CALCULATE PORTFOLIO DAY CHANGE
    # =====================================================

    def calculate_day_change(self, portfolio):

        current_portfolio_value = 0
        previous_portfolio_value = 0

        for holding in portfolio.holdings:

            price_data = (
                self.market_service
                .get_current_and_previous_price(
                    holding.symbol
                )
            )

            if not price_data:
                continue

            current_price = price_data["current_price"]

            previous_price = price_data["previous_price"]

            current_value = (
                holding.quantity
                * current_price
            )

            previous_value = (
                holding.quantity
                * previous_price
            )

            current_portfolio_value += current_value

            previous_portfolio_value += previous_value

        if previous_portfolio_value <= 0:

            return "0.00%"

        day_change = (
            (
                current_portfolio_value
                - previous_portfolio_value
            )
            / previous_portfolio_value
        ) * 100

        return f"{day_change:+.2f}%"

    # =====================================================
    # GET PORTFOLIO
    # =====================================================

    def get_portfolio(self):

        market = (
            self.market_service
            .get_market_status()
        )

        portfolio = (
            self.db.query(Portfolio)
            .filter(
                Portfolio.name == "Growth Portfolio"
            )
            .first()
        )

        if not portfolio:

            return {

                "portfolio_name":
                    "Growth Portfolio",

                "total_value":
                    0,

                "day_change":
                    "0.00%",

                "market":
                    market
            }

        total_value = sum(

            holding.quantity
            * holding.buy_price

            for holding
            in portfolio.holdings
        )

        day_change = (
            self.calculate_day_change(
                portfolio
            )
        )

        return {

            "portfolio_name":
                portfolio.name,

            "total_value":
                round(
                    float(total_value),
                    2
                ),

            "day_change":
                day_change,

            "market":
                market
        }

    # =====================================================
    # PORTFOLIO ANALYSIS
    # =====================================================

    def analyze_portfolio(
        self,
        portfolio_name,
        timeframe
    ):

        # -------------------------------------------------
        # GET PORTFOLIO
        # -------------------------------------------------

        portfolio = (
            self.db.query(Portfolio)
            .filter(
                Portfolio.name == portfolio_name
            )
            .first()
        )

        if not portfolio:

            return {

                "message":
                    "Portfolio not found",

                "portfolio_name":
                    portfolio_name,

                "timeframe":
                    timeframe,

                "total_value":
                    0,

                "current_value":
                    0,

                "profit_loss":
                    0,

                "risk_level":
                    "Unknown",

                "overall_return":
                    "0%",

                "analytics":
                    {},

                "insight":
                    "Selected portfolio was not found."
            }

        # -------------------------------------------------
        # INVESTED VALUE
        # -------------------------------------------------

        invested_value = sum(

            holding.quantity
            * holding.buy_price

            for holding
            in portfolio.holdings
        )

        # -------------------------------------------------
        # CURRENT VALUE
        # -------------------------------------------------

        current_value = 0

        holdings_data = []

        # -------------------------------------------------
        # PROCESS HOLDINGS
        # -------------------------------------------------

        for holding in portfolio.holdings:

            current_price = (
                self.market_service
                .get_current_price(
                    holding.symbol
                )
            )

            # Fallback to buy price if market
            # data is unavailable

            if current_price is None:

                current_price = float(
                    holding.buy_price
                )

            holding_invested_value = (

                holding.quantity
                * holding.buy_price
            )

            holding_current_value = (

                holding.quantity
                * current_price
            )

            holding_profit_loss = (

                holding_current_value
                - holding_invested_value
            )

            current_value += (
                holding_current_value
            )

            holdings_data.append({

                "symbol":
                    holding.symbol,

                "quantity":
                    float(
                        holding.quantity
                    ),

                "buy_price":
                    round(
                        float(
                            holding.buy_price
                        ),
                        2
                    ),

                "current_price":
                    round(
                        float(
                            current_price
                        ),
                        2
                    ),

                "invested_value":
                    round(
                        float(
                            holding_invested_value
                        ),
                        2
                    ),

                "current_value":
                    round(
                        float(
                            holding_current_value
                        ),
                        2
                    ),

                "profit_loss":
                    round(
                        float(
                            holding_profit_loss
                        ),
                        2
                    )
            })

        # -------------------------------------------------
        # TOTAL PROFIT / LOSS
        # -------------------------------------------------

        profit_loss = (
            current_value
            - invested_value
        )

        # -------------------------------------------------
        # OVERALL RETURN
        # -------------------------------------------------

        if invested_value > 0:

            return_percentage = (

                profit_loss
                / invested_value

            ) * 100

        else:

            return_percentage = 0

        # -------------------------------------------------
        # FIND HOLDING PERFORMANCE
        # -------------------------------------------------

        best_performer = None

        least_loss = None

        largest_loss = None

        positive_holdings = [

            holding

            for holding in holdings_data

            if holding["profit_loss"] > 0
        ]

        negative_holdings = [

            holding

            for holding in holdings_data

            if holding["profit_loss"] < 0
        ]

        # -------------------------------------------------
        # BEST PERFORMER
        # -------------------------------------------------

        if positive_holdings:

            best_performer = max(

                positive_holdings,

                key=lambda x:
                    x["profit_loss"]
            )

        # -------------------------------------------------
        # LEAST LOSS
        # -------------------------------------------------

        if negative_holdings:

            least_loss = max(

                negative_holdings,

                key=lambda x:
                    x["profit_loss"]
            )

        # -------------------------------------------------
        # LARGEST LOSS
        # -------------------------------------------------

        if negative_holdings:

            largest_loss = min(

                negative_holdings,

                key=lambda x:
                    x["profit_loss"]
            )

        # -------------------------------------------------
        # PERFORMANCE SUMMARY FOR AI
        # -------------------------------------------------

        performance_summary = {

            "best_performer":
                best_performer,

            "least_loss":
                least_loss,

            "largest_loss":
                largest_loss,

            "all_holdings_in_loss":

                len(negative_holdings)
                == len(holdings_data)

                and len(holdings_data) > 0
        }

        # -------------------------------------------------
        # PORTFOLIO ANALYTICS
        # -------------------------------------------------

        analytics = (

            self.analytics_service
            .run_portfolio_analytics(

                holdings_data=
                    holdings_data,

                current_value=
                    current_value,

                total_profit_loss=
                    profit_loss
            )
        )

        # -------------------------------------------------
        # RISK LEVEL
        # -------------------------------------------------

        risk_level = (
            analytics["risk_level"]
        )

        # -------------------------------------------------
        # AI INSIGHT
        # -------------------------------------------------

        insight = (

            self.ai_service
            .generate_portfolio_insight(

                portfolio_name=
                    portfolio.name,

                total_value=
                    invested_value,

                current_value=
                    current_value,

                profit_loss=
                    profit_loss,

                overall_return=
                    f"{return_percentage:+.2f}%",

                risk_level=
                    risk_level,

                holdings_data=
                    holdings_data,

                performance_summary=
                    performance_summary
            )
        )

        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

        return {

            "message":
                "Portfolio analysis completed",

            "portfolio_name":
                portfolio.name,

            "timeframe":
                timeframe,

            "total_value":
                round(
                    float(invested_value),
                    2
                ),

            "current_value":
                round(
                    float(current_value),
                    2
                ),

            "profit_loss":
                round(
                    float(profit_loss),
                    2
                ),

            "risk_level":
                risk_level,

            "overall_return":
                f"{return_percentage:+.2f}%",

            "analytics":
                analytics,

            "insight":
                insight
        }