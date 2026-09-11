from app.services.market_service import MarketService
from app.services.news_service import NewsService
from app.services.ai_service import AIService


class StockService:

    def __init__(self):

        self.market_service = MarketService()
        self.news_service = NewsService()
        self.ai_service = AIService()

    # =====================================================
    # STOCK ANALYSIS
    # =====================================================

    def analyze_stock(self, symbol):

        # -------------------------------------------------
        # NORMALIZE SYMBOL
        # -------------------------------------------------

        symbol = symbol.upper().strip()

        # -------------------------------------------------
        # 1. TECHNICAL / MARKET ANALYSIS
        # -------------------------------------------------

        try:

            market_analysis = (
                self.market_service
                .get_market_analysis(symbol)
            )

        except Exception as e:

            return {
                "error": "Unable to analyze stock",
                "details": str(e)
            }

        # -------------------------------------------------
        # CHECK MARKET ANALYSIS
        # -------------------------------------------------

        if not isinstance(
            market_analysis,
            dict
        ):

            return {
                "error":
                    "Invalid market analysis response"
            }

        if "error" in market_analysis:

            return market_analysis

        # -------------------------------------------------
        # 2. STOCK-SPECIFIC NEWS
        # -------------------------------------------------

        try:

            relevant_news = (
                self.news_service
                .get_stock_news(symbol)
            )

        except Exception as e:

            return {
                "symbol":
                    symbol,

                "error":
                    "Unable to fetch stock news",

                "details":
                    str(e)
            }

        # -------------------------------------------------
        # CHECK NEWS RESPONSE
        # -------------------------------------------------

        if isinstance(
            relevant_news,
            dict
        ):

            if "error" in relevant_news:

                return {

                    "symbol":
                        symbol,

                    "error":
                        relevant_news.get(
                            "error"
                        ),

                    "details":
                        relevant_news.get(
                            "details"
                        ),

                    "status_code":
                        relevant_news.get(
                            "status_code"
                        )
                }

            relevant_news = []

        elif not isinstance(
            relevant_news,
            list
        ):

            relevant_news = []

        # -------------------------------------------------
        # 3. NEWS SENTIMENT
        # -------------------------------------------------

        positive_news = 0
        negative_news = 0
        neutral_news = 0

        for article in relevant_news:

            sentiment = article.get(
                "sentiment",
                "Neutral"
            )

            if sentiment == "Positive":

                positive_news += 1

            elif sentiment == "Negative":

                negative_news += 1

            else:

                neutral_news += 1

        # -------------------------------------------------
        # TOTAL NEWS
        # -------------------------------------------------

        total_news = len(
            relevant_news
        )

        # -------------------------------------------------
        # OVERALL NEWS SENTIMENT
        # -------------------------------------------------

        if positive_news > negative_news:

            news_sentiment = "Positive"

        elif negative_news > positive_news:

            news_sentiment = "Negative"

        else:

            news_sentiment = "Neutral"

        # -------------------------------------------------
        # NEWS DATA FOR AI
        # -------------------------------------------------

        news_data = {

            "sentiment":
                news_sentiment,

            "positive_news":
                positive_news,

            "negative_news":
                negative_news,

            "neutral_news":
                neutral_news,

            "total_news":
                total_news,

            "articles":
                relevant_news
        }

        # -------------------------------------------------
        # 4. GENERATE AI INSIGHT
        # -------------------------------------------------

        try:

            ai_insight = (
                self.ai_service
                .generate_stock_insight(
                    symbol=symbol,

                    market_analysis=
                        market_analysis,

                    news_data=
                        news_data
                )
            )

        except Exception as e:

            ai_insight = (
                "AI insight unavailable: "
                f"{str(e)}"
            )

        # -------------------------------------------------
        # 5. FINAL RESPONSE
        # -------------------------------------------------

        return {

            "symbol":
                symbol,

            # =============================================
            # TECHNICAL ANALYSIS
            # =============================================

            "market_analysis": {

                "close":
                    market_analysis.get(
                        "close"
                    ),

                "daily_return":
                    market_analysis.get(
                        "daily_return"
                    ),

                "volatility":
                    market_analysis.get(
                        "volatility"
                    ),

                "trend":
                    market_analysis.get(
                        "trend"
                    ),

                "rsi":
                    market_analysis.get(
                        "rsi"
                    ),

                "rsi_signal":
                    market_analysis.get(
                        "rsi_signal"
                    ),

                "macd":
                    market_analysis.get(
                        "macd"
                    ),

                "macd_signal":
                    market_analysis.get(
                        "macd_signal"
                    ),

                "macd_trend":
                    market_analysis.get(
                        "macd_trend"
                    ),

                "signal_score":
                    market_analysis.get(
                        "signal_score"
                    ),

                "overall_signal":
                    market_analysis.get(
                        "overall_signal"
                    ),

                "market_insight":
                    market_analysis.get(
                        "market_insight"
                    )
            },

            # =============================================
            # STOCK NEWS
            # =============================================

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
                    total_news,

                "articles":
                    relevant_news
            },

            # =============================================
            # AI INSIGHT
            # =============================================

            "ai_insight":
                ai_insight
        }