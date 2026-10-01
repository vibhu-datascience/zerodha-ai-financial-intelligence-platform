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
        timeframe="1Y",
        user_id=None
    ):

        # =================================================
        # NEWS DATA
        # =================================================

        try:

            news_result = (
                self.news_service.get_news()
            )

            if isinstance(
                news_result,
                list
            ):

                news = news_result

            else:

                news = []

                print(
                    "[FINANCIAL INTELLIGENCE] "
                    f"Unexpected news response: {news_result}"
                )

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

            sentiment_result = (
                self.news_service
                .get_overall_sentiment()
            )

            if isinstance(
                sentiment_result,
                dict
            ):

                sentiment = sentiment_result

            else:

                sentiment = {

                    "overall_sentiment":
                        "Unknown",

                    "positive_count":
                        0,

                    "negative_count":
                        0,

                    "neutral_count":
                        0,

                    "total_articles":
                        len(news),

                    "message":
                        "News sentiment was unavailable."
                }

        except Exception as e:

            print(
                "[FINANCIAL INTELLIGENCE] "
                f"Sentiment error: {e}"
            )

            sentiment = {

                "overall_sentiment":
                    "Unknown",

                "positive_count":
                    0,

                "negative_count":
                    0,

                "neutral_count":
                    0,

                "total_articles":
                    len(news),

                "message":
                    "News sentiment was unavailable."
            }

        # =================================================
        # AGENTIC AI WORKFLOW
        # =================================================

        try:

            workflow_result = (
                run_financial_workflow_sync(

                    portfolio_name=
                        portfolio_name,

                    timeframe=
                        timeframe,

                    user_id=
                        user_id,

                    news_data=
                        news
                )
            )

        except TypeError:

            workflow_result = (
                run_financial_workflow_sync(

                    portfolio_name=
                        portfolio_name,

                    timeframe=
                        timeframe,

                    user_id=
                        user_id
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
            analytics_data.get(
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

            holdings_data.append({

                "symbol":
                    holding.get(
                        "symbol"
                    ),

                "quantity":
                    float(
                        holding.get(
                            "quantity",
                            0
                        )
                    ),

                "buy_price":
                    round(
                        float(
                            holding.get(
                                "buy_price",
                                0
                            )
                        ),
                        2
                    ),

                "current_price":
                    round(
                        float(
                            holding.get(
                                "current_price",
                                0
                            )
                        ),
                        2
                    ),

                "invested_value":
                    round(
                        float(
                            holding.get(
                                "invested_value",
                                0
                            )
                        ),
                        2
                    ),

                "current_value":
                    round(
                        float(
                            holding.get(
                                "current_value",
                                0
                            )
                        ),
                        2
                    ),

                "profit_loss":
                    round(
                        float(
                            holding.get(
                                "profit_loss",
                                0
                            )
                        ),
                        2
                    ),

                "sector":
                    holding.get(
                        "sector"
                    )
            })

        # =================================================
        # PORTFOLIO-SPECIFIC AI INSIGHT
        # =================================================

        try:

            portfolio_insight = (
                self.ai_service
                .generate_portfolio_insight(

                    portfolio_analysis={

                        "portfolio_name":
                            portfolio_name,

                        "timeframe":
                            timeframe,

                        "total_value":
                            total_invested,

                        "current_value":
                            current_value,

                        "profit_loss":
                            profit_loss,

                        "overall_return":
                            overall_return,

                        "risk_level":
                            risk_level,

                        "holdings":
                            holdings_data
                    }
                )
            )

        except Exception as e:

            print(
                "[FINANCIAL INTELLIGENCE] "
                f"Portfolio insight error: {e}"
            )

            portfolio_insight = (
                "Portfolio-specific AI insight "
                "is currently unavailable."
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

            "holdings":
                holdings_data,

            "insight":
                portfolio_insight
        }

        # =================================================
        # AI RECOMMENDATION ENGINE
        # =================================================

        try:

            recommendation_result = (
                self.recommendation_service
                .generate_recommendations(

                    analytics=
                        analytics,

                    portfolio_analysis={

                        "portfolio_name":
                            portfolio_name,

                        "timeframe":
                            timeframe,

                        "total_value":
                            total_invested,

                        "current_value":
                            current_value,

                        "profit_loss":
                            profit_loss,

                        "overall_return":
                            overall_return,

                        "risk_level":
                            risk_level
                    },

                    market_analysis=
                        market
                )
            )

            # ---------------------------------------------
            # RECOMMENDATION POLICY VALIDATION
            # ---------------------------------------------

            policy_result = (
                self.recommendation_policy
                .validate_recommendations(
                    recommendation_result
                )
            )

            recommendations = (
                policy_result.get(
                    "valid_cards",
                    []
                )
            )

            recommendation_policy = {

                "status":
                    policy_result.get(
                        "status",
                        "unknown"
                    ),

                "total_cards":
                    policy_result.get(
                        "total_cards",
                        0
                    ),

                "approved_cards":
                    policy_result.get(
                        "approved_cards",
                        0
                    ),

                "blocked_count":
                    policy_result.get(
                        "blocked_count",
                        0
                    ),

                "errors":
                    policy_result.get(
                        "errors",
                        []
                    )
            }

        except Exception as e:

            print(
                "[FINANCIAL INTELLIGENCE] "
                f"Recommendation error: {e}"
            )

            recommendations = []

            recommendation_policy = {

                "status":
                    "failed",

                "total_cards":
                    0,

                "approved_cards":
                    0,

                "blocked_count":
                    0,

                "errors": [
                    str(e)
                ]
            }

        # =================================================
        # FINAL RESPONSE
        # =================================================

        return {

            "portfolio":
                portfolio_response,

            "market":
                market,

            "news":
                news,

            "sentiment":
                sentiment,

            "financial_intelligence":
                workflow_result.get(
                    "final_report",
                    workflow_result.get(
                        "final_answer",
                        ""
                    )
                ),

            "recommendations":
                recommendations,

            "recommendation_policy":
                recommendation_policy
        }