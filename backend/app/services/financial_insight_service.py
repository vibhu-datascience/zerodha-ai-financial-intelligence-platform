from app.services.market_service import MarketService
from app.services.news_service import NewsService
from app.services.portfolio_service import PortfolioService


class FinancialInsightService:

    def __init__(self, db):

        self.db = db

        self.market_service = MarketService()
        self.news_service = NewsService()
        self.portfolio_service = PortfolioService(db)

    # =====================================================
    # GENERATE FINANCIAL INSIGHT
    # =====================================================

    def generate_insight(self):

        # =================================================
        # 1. MARKET ANALYSIS
        # =================================================

        try:

            market = (
                self.market_service
                .get_market_analysis("^NSEI")
            )

            if not isinstance(market, dict):

                market = {
                    "error":
                        "Market analysis unavailable"
                }

        except Exception as e:

            market = {
                "error":
                    "Unable to perform market analysis",

                "details":
                    str(e)
            }

        # =================================================
        # 2. BASIC MARKET STATUS
        # =================================================

        try:

            market_status = (
                self.market_service
                .get_market_status()
            )

            if not isinstance(
                market_status,
                dict
            ):

                market_status = {}

        except Exception:

            market_status = {}

        # =================================================
        # 3. NEWS DATA
        # =================================================

        try:

            news = (
                self.news_service
                .get_news()
            )

            if not isinstance(
                news,
                list
            ):

                news = []

        except Exception:

            news = []

        # =================================================
        # 4. NEWS SENTIMENT
        # =================================================

        positive_news = 0
        negative_news = 0
        neutral_news = 0

        for article in news:

            if not isinstance(
                article,
                dict
            ):

                continue

            sentiment = (
                article.get(
                    "sentiment",
                    "Neutral"
                )
                or "Neutral"
            )

            sentiment = str(
                sentiment
            ).strip().capitalize()

            if sentiment == "Positive":

                positive_news += 1

            elif sentiment == "Negative":

                negative_news += 1

            else:

                neutral_news += 1

        total_news = len(news)

        # =================================================
        # 5. OVERALL NEWS SENTIMENT
        # =================================================

        if positive_news > negative_news:

            news_sentiment = "Positive"

        elif negative_news > positive_news:

            news_sentiment = "Negative"

        else:

            news_sentiment = "Neutral"

        # =================================================
        # 6. MARKET SIGNAL
        # =================================================

        market_trend = (
            market.get(
                "trend",
                "Unknown"
            )
            or "Unknown"
        )

        market_signal = (
            market.get(
                "overall_signal",
                "Neutral"
            )
            or "Neutral"
        )

        signal_score = (
            market.get(
                "signal_score",
                0
            )
        )

        try:

            signal_score = int(
                signal_score
            )

        except (
            ValueError,
            TypeError
        ):

            signal_score = 0

        # =================================================
        # 7. DETERMINE MARKET OUTLOOK
        # =================================================

        if signal_score >= 2:

            market_outlook = "Positive"

        elif signal_score <= -2:

            market_outlook = "Negative"

        else:

            market_outlook = "Neutral"

        # =================================================
        # 8. NEWS SCORE
        # =================================================

        if news_sentiment == "Positive":

            news_score = 1

        elif news_sentiment == "Negative":

            news_score = -1

        else:

            news_score = 0

        # =================================================
        # 9. COMBINED OUTLOOK
        # =================================================

        combined_score = (
            signal_score
            + news_score
        )

        if combined_score >= 2:

            overall_outlook = "Positive"

        elif combined_score <= -2:

            overall_outlook = "Negative"

        else:

            overall_outlook = "Neutral"

        # =================================================
        # 10. PORTFOLIO ANALYSIS
        # =================================================

        try:

            portfolio = (
                self.portfolio_service
                .analyze_portfolio(
                    portfolio_name="Growth Portfolio",
                    timeframe="1Y"
                )
            )

            if not isinstance(
                portfolio,
                dict
            ):

                portfolio = {
                    "message":
                        "Portfolio analysis unavailable"
                }

        except Exception as e:

            portfolio = {

                "message":
                    "Portfolio analysis unavailable",

                "error":
                    str(e)
            }

        # =================================================
        # 11. HUMAN-READABLE INSIGHT
        # =================================================

        if overall_outlook == "Positive":

            insight = (
                "Market indicators and recent financial "
                "news currently indicate a positive overall "
                "outlook. The technical market signal is "
                "supportive, while recent news sentiment "
                "provides additional positive context."
            )

        elif overall_outlook == "Negative":

            insight = (
                "Market indicators currently indicate a "
                "negative overall outlook. Recent financial "
                "news should be considered alongside the "
                "weaker market signal when monitoring "
                "current market conditions."
            )

        else:

            insight = (
                "Market indicators and recent financial "
                "news are showing a mixed or neutral "
                "outlook. The available information does "
                "not provide a strong directional signal."
            )

        # =================================================
        # 12. FINAL RESPONSE
        # =================================================

        return {

            "overall_outlook":
                overall_outlook,

            "market": {

                "symbol":
                    market.get(
                        "symbol",
                        "^NSEI"
                    ),

                "close":
                    market.get(
                        "close"
                    ),

                "trend":
                    market_trend,

                "signal":
                    market_signal,

                "signal_score":
                    signal_score,

                "daily_return":
                    market.get(
                        "daily_return"
                    ),

                "volatility":
                    market.get(
                        "volatility"
                    ),

                "rsi":
                    market.get(
                        "rsi"
                    ),

                "rsi_signal":
                    market.get(
                        "rsi_signal"
                    ),

                "macd":
                    market.get(
                        "macd"
                    ),

                "macd_signal":
                    market.get(
                        "macd_signal"
                    ),

                "macd_trend":
                    market.get(
                        "macd_trend"
                    ),

                "overall_signal":
                    market.get(
                        "overall_signal"
                    ),

                "market_insight":
                    market.get(
                        "market_insight"
                    ),

                "nifty":
                    market_status.get(
                        "nifty"
                    ),

                "sensex":
                    market_status.get(
                        "sensex"
                    ),

                "market_status":
                    market_status.get(
                        "market_status"
                    ),

                "exchange":
                    market_status.get(
                        "exchange"
                    )
            },

            "portfolio":
                portfolio,

            "news": {

                "sentiment":
                    news_sentiment,

                "positive_news":
                    positive_news,

                "negative_news":
                    negative_news,

                "neutral_news":
                    neutral_news,

                "total_news":
                    total_news
            },

            "financial_intelligence":
                insight
        }