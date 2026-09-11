from app.services.news_service import NewsService

from app.services.ai_workflow import (
    run_financial_workflow_sync
)

from app.services.ai_service import (
    AIService
)

from app.services.market_service import (
    MarketService
)

from app.services.recommendation_service import (
    RecommendationService
)

from app.services.recommendation_policy import (
    RecommendationPolicy
)


class FinancialIntelligenceService:

    def __init__(self, db):

        self.db = db

        self.news_service = NewsService()

        self.ai_service = AIService()

        self.market_service = MarketService()

        # Recommendation engine
        self.recommendation_service = (
            RecommendationService()
        )

        # Safety / policy validation
        self.recommendation_policy = (
            RecommendationPolicy()
        )

    # =====================================================
    # GENERATE FINANCIAL INTELLIGENCE
    # =====================================================

    def generate_financial_intelligence(
        self,
        portfolio_name="Growth Portfolio",
        timeframe="1Y"
    ):

        # =================================================
        # NEWS DATA
        # =================================================

        try:

            news = self.news_service.get_news()

        except Exception as e:

            print(
                "[FINANCIAL INTELLIGENCE] "
                f"News fetch error: {e}"
            )

            news = []

        # =================================================
        # NEWS SENTIMENT
        # =================================================

        try:

            sentiment = (
                self.news_service
                .get_overall_sentiment()
            )

        except Exception as e:

            print(
                "[FINANCIAL INTELLIGENCE] "
                f"Sentiment error: {e}"
            )

            sentiment = {
                "overall_sentiment": "Unknown",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "total_articles": 0,
                "message": (
                    "News sentiment was unavailable."
                )
            }

        # =================================================
        # AGENTIC AI WORKFLOW
        # =================================================

        workflow_result = (
            run_financial_workflow_sync(

                portfolio_name=
                    portfolio_name,

                timeframe=
                    timeframe,

                news_data=
                    news
            )
        )

        # =================================================
        # WORKFLOW OUTPUTS
        # =================================================

        portfolio_data = (
            workflow_result.get(
                "portfolio_data",
                {}
            )
        )

        analytics_data = (
            workflow_result.get(
                "analytics_data",
                {}
            )
        )

        market_data = (
            workflow_result.get(
                "market_data",
                {}
            )
        )

        analytics = (
            analytics_data.get(
                "analytics",
                {}
            )
        )

        # =================================================
        # PORTFOLIO VALUES
        # =================================================

        total_invested = (
            portfolio_data.get(
                "total_invested",
                0
            )
        )

        current_value = (
            analytics_data.get(
                "current_value",
                0
            )
        )

        profit_loss = (
            analytics_data.get(
                "profit_loss",
                0
            )
        )

        risk_level = (
            analytics.get(
                "risk_level",
                "Unknown"
            )
        )

        # =================================================
        # OVERALL RETURN
        # =================================================

        try:

            if float(total_invested) > 0:

                return_percentage = (
                    float(profit_loss)
                    / float(total_invested)
                    * 100
                )

            else:

                return_percentage = 0.0

        except (
            TypeError,
            ValueError
        ):

            return_percentage = 0.0

        overall_return = (
            f"{return_percentage:+.2f}%"
        )

        # =================================================
        # MARKET RESPONSE
        # =================================================

        market = market_data.get(
            "data",
            market_data
        )

        # =================================================
        # PORTFOLIO HOLDING DATA
        # =================================================

        holdings_data = []

        workflow_holdings = (
            portfolio_data.get(
                "holdings",
                []
            )
        )

        for holding in workflow_holdings:

            if not isinstance(
                holding,
                dict
            ):
                continue

            symbol = holding.get(
                "symbol"
            )

            quantity = (
                holding.get(
                    "quantity",
                    0
                )
            )

            buy_price = (
                holding.get(
                    "buy_price",
                    0
                )
            )

            sector = holding.get(
                "sector"
            )

            # ---------------------------------------------
            # CURRENT PRICE
            # ---------------------------------------------

            current_price = (
                self.market_service
                .get_current_price(
                    symbol
                )
            )

            if current_price is None:

                current_price = float(
                    buy_price or 0
                )

            # ---------------------------------------------
            # HOLDING VALUES
            # ---------------------------------------------

            invested_value = (
                float(quantity)
                * float(buy_price)
            )

            holding_current_value = (
                float(quantity)
                * float(current_price)
            )

            holding_profit_loss = (
                holding_current_value
                - invested_value
            )

            holdings_data.append({

                "symbol":
                    symbol,

                "quantity":
                    float(quantity),

                "buy_price":
                    round(
                        float(buy_price),
                        2
                    ),

                "current_price":
                    round(
                        float(current_price),
                        2
                    ),

                "invested_value":
                    round(
                        invested_value,
                        2
                    ),

                "current_value":
                    round(
                        holding_current_value,
                        2
                    ),

                "profit_loss":
                    round(
                        holding_profit_loss,
                        2
                    ),

                "sector":
                    sector
            })

        # =================================================
        # PORTFOLIO-SPECIFIC AI INSIGHT
        # =================================================

        portfolio_insight = (
            self.ai_service
            .generate_portfolio_insight(

                portfolio_name=
                    portfolio_name,

                total_value=
                    total_invested,

                current_value=
                    current_value,

                profit_loss=
                    profit_loss,

                overall_return=
                    overall_return,

                risk_level=
                    risk_level,

                holdings_data=
                    holdings_data
            )
        )

        # =================================================
        # PORTFOLIO RESPONSE
        # =================================================

        portfolio_response = {

            "message":
                "Portfolio analysis completed",

            "portfolio_name":
                portfolio_name,

            "timeframe":
                timeframe,

            "total_value":
                round(
                    float(total_invested),
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
                overall_return,

            "analytics":
                analytics,

            # IMPORTANT:
            # This is now the portfolio-specific
            # AI insight, NOT the global workflow report.
            "insight":
                portfolio_insight
        }

        # =================================================
        # GLOBAL AI FINANCIAL INTELLIGENCE
        # =================================================

        intelligence = (
            workflow_result.get(
                "final_report",
                "Financial intelligence report "
                "was unavailable."
            )
        )

        # =================================================
        # GENERATE RECOMMENDATIONS
        # =================================================

        recommendations = (
            self.recommendation_service
            .generate_recommendations(

                analytics=
                    analytics,

                portfolio_analysis=
                    portfolio_response,

                market_analysis=
                    market
            )
        )

        # =================================================
        # VALIDATE RECOMMENDATIONS
        # =================================================

        recommendation_validation = (
            self.recommendation_policy
            .validate_recommendations(
                recommendations
            )
        )

        # =================================================
        # ONLY APPROVED CARDS
        # =================================================

        approved_recommendations = (
            recommendation_validation.get(
                "valid_cards",
                []
            )
        )

        # =================================================
        # FINAL RESPONSE
        # =================================================

        return {

            "portfolio_name":
                portfolio_name,

            "timeframe":
                timeframe,

            # ---------------------------------------------
            # MARKET
            # ---------------------------------------------

            "market":
                market,

            # ---------------------------------------------
            # PORTFOLIO
            # ---------------------------------------------

            "portfolio":
                portfolio_response,

            # ---------------------------------------------
            # NEWS
            # ---------------------------------------------

            "news":
                news,

            "sentiment":
                sentiment,

            # ---------------------------------------------
            # GLOBAL AI FINANCIAL INTELLIGENCE
            # ---------------------------------------------

            "financial_intelligence":
                intelligence,

            # ---------------------------------------------
            # RECOMMENDATIONS
            # ---------------------------------------------

            "recommendations":
                approved_recommendations,

            # ---------------------------------------------
            # RECOMMENDATION POLICY
            # ---------------------------------------------

            "recommendation_policy":
                {

                    "status":
                        recommendation_validation.get(
                            "status",
                            "unknown"
                        ),

                    "total_cards":
                        recommendation_validation.get(
                            "total_cards",
                            0
                        ),

                    "approved_cards":
                        recommendation_validation.get(
                            "approved_cards",
                            0
                        ),

                    "blocked_count":
                        recommendation_validation.get(
                            "blocked_count",
                            0
                        ),

                    "errors":
                        recommendation_validation.get(
                            "errors",
                            []
                        )
                },

            # ---------------------------------------------
            # WORKFLOW OBSERVABILITY
            # ---------------------------------------------

            "workflow":
                {

                    "status":
                        workflow_result.get(
                            "validation_status",
                            "unknown"
                        ),

                    "validation_errors":
                        workflow_result.get(
                            "validation_errors",
                            []
                        )
                }
        }