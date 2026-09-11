import os
import requests

from dotenv import load_dotenv
from app.services.sentiment_service import SentimentService


load_dotenv()


class NewsService:

    def __init__(self):

        self.sentiment_service = SentimentService()

        # =================================================
        # STOCK SYMBOL → COMPANY NAME / ALIASES
        # =================================================

        self.stock_aliases = {

            "RELIANCE.NS": [
                "reliance industries",
                "reliance industries limited",
                "reliance jio",
                "reliance retail"
            ],

            "TCS.NS": [
                "tata consultancy services",
                "tata consultancy",
                "tcs"
            ],

            "INFY.NS": [
                "infosys",
                "infosys limited"
            ],

            "HDFCBANK.NS": [
                "hdfc bank",
                "hdfc bank limited"
            ],

            "ICICIBANK.NS": [
                "icici bank",
                "icici bank limited"
            ],

            "SBIN.NS": [
                "state bank of india",
                "state bank",
                "sbi"
            ],

            "BHARTIARTL.NS": [
                "bharti airtel",
                "bharti airtel limited",
                "airtel india"
            ],

            "ITC.NS": [
                "itc limited",
                "itc ltd"
            ],

            "LT.NS": [
                "larsen & toubro",
                "larsen and toubro",
                "larsen toubro"
            ],

            "HINDUNILVR.NS": [
                "hindustan unilever",
                "hindustan unilever limited",
                "hul"
            ],

            "AXISBANK.NS": [
                "axis bank",
                "axis bank limited"
            ],

            "KOTAKBANK.NS": [
                "kotak mahindra bank",
                "kotak mahindra",
                "kotak bank"
            ],

            "MARUTI.NS": [
                "maruti suzuki",
                "maruti suzuki india",
                "maruti"
            ],

            "TATAMOTORS.NS": [
                "tata motors",
                "tata motors limited"
            ],

            "SUNPHARMA.NS": [
                "sun pharma",
                "sun pharmaceutical",
                "sun pharmaceutical industries"
            ],

            "ADANIENT.NS": [
                "adani enterprises",
                "adani enterprises limited"
            ],

            "ADANIPORTS.NS": [
                "adani ports",
                "adani ports and sez",
                "adani ports and special economic zone"
            ]
        }

    # =====================================================
    # SENTIMENT HELPER
    # =====================================================

    def analyze_sentiment(self, text):

        try:

            result = self.sentiment_service.analyze(text)

            return result

        except Exception as e:

            print(
                f"Sentiment analysis error: {e}"
            )

            return {
                "sentiment": "Neutral",
                "positive_score": 0,
                "negative_score": 0
            }

    # =====================================================
    # GET GENERAL FINANCIAL NEWS
    # =====================================================

    def get_news(self):

        print("INSIDE GET_NEWS")

        api_key = os.getenv("NEWS_API_KEY")

        if not api_key:

            return {
                "error": "NEWS_API_KEY not found in .env file"
            }

        query = (
            "(Nifty OR Sensex OR NSE OR BSE OR "
            "\"Indian stock market\" OR \"Indian stocks\") "
            "AND "
            "(stock OR stocks OR market OR shares OR "
            "equity OR equities OR trading OR investor OR "
            "earnings OR results OR finance OR economy)"
        )

        try:

            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 50,
                    "apiKey": api_key
                },
                timeout=15
            )

            print(
                "NEWS API STATUS:",
                response.status_code
            )

            if response.status_code != 200:

                try:
                    details = response.json()
                except Exception:
                    details = response.text

                return {
                    "error": "Unable to fetch news",
                    "status_code": response.status_code,
                    "details": details
                }

            data = response.json()

            news_list = []

            financial_keywords = [

                "nifty",
                "sensex",
                "nse",
                "bse",
                "stock",
                "stocks",
                "share",
                "shares",
                "equity",
                "equities",
                "market",
                "trading",
                "investor",
                "investment",
                "earnings",
                "profit",
                "loss",
                "revenue",
                "quarter",
                "results",
                "ipo",
                "dividend",
                "mutual fund",
                "bank",
                "banking",
                "rbi",
                "rupee",
                "inflation",
                "interest rate",
                "economy",
                "economic",
                "finance",
                "financial"
            ]

            seen_urls = set()

            for article in data.get("articles", []):

                title = (
                    article.get("title")
                    or ""
                )

                description = (
                    article.get("description")
                    or ""
                )

                article_url = (
                    article.get("url")
                    or ""
                )

                text = (
                    f"{title} {description}"
                ).lower()

                is_financial = any(
                    keyword in text
                    for keyword in financial_keywords
                )

                if not is_financial:
                    continue

                if article_url in seen_urls:
                    continue

                seen_urls.add(article_url)

                sentiment = self.analyze_sentiment(text)

                news_list.append({

                    "title": title,

                    "description": description,

                    "source": (
                        article.get(
                            "source",
                            {}
                        ).get("name")
                    ),

                    "url": article_url,

                    "published_at": (
                        article.get(
                            "publishedAt"
                        )
                    ),

                    "sentiment": (
                        sentiment.get(
                            "sentiment",
                            "Neutral"
                        )
                    ),

                    "positive_score": (
                        sentiment.get(
                            "positive_score",
                            0
                        )
                    ),

                    "negative_score": (
                        sentiment.get(
                            "negative_score",
                            0
                        )
                    )
                })

                if len(news_list) >= 10:
                    break

            print(
                "Financial articles:",
                len(news_list)
            )

            return news_list

        except requests.exceptions.RequestException as e:

            print(
                "NEWS NETWORK ERROR:",
                str(e)
            )

            return {
                "error":
                    "Network error while fetching news",

                "details":
                    str(e)
            }

        except Exception as e:

            print(
                "NEWS UNEXPECTED ERROR:",
                str(e)
            )

            return {
                "error":
                    "Unexpected error",

                "details":
                    str(e)
            }

    # =====================================================
    # CHECK STOCK RELEVANCE
    # =====================================================

    def _find_matching_alias(
        self,
        title,
        description,
        aliases
    ):

        title_lower = title.lower()
        description_lower = description.lower()

        # =================================================
        # 1. FIRST PRIORITY:
        # COMPANY NAME IN TITLE
        # =================================================

        for alias in aliases:

            alias_lower = alias.lower()

            if alias_lower in title_lower:

                return alias

        # =================================================
        # 2. SECOND PRIORITY:
        # COMPANY NAME IN DESCRIPTION
        #
        # Only allow aliases longer than 4 characters.
        # This prevents very generic words from matching.
        # =================================================

        for alias in aliases:

            alias_lower = alias.lower()

            if len(alias_lower) <= 4:
                continue

            if alias_lower in description_lower:

                return alias

        return None

    # =====================================================
    # GET STOCK-SPECIFIC NEWS
    # =====================================================

    def get_stock_news(
        self,
        symbol
    ):

        print(
            "INSIDE GET_STOCK_NEWS:",
            symbol
        )

        api_key = os.getenv("NEWS_API_KEY")

        if not api_key:

            return {
                "error":
                    "NEWS_API_KEY not found in .env file"
            }

        symbol = symbol.upper().strip()

        # =================================================
        # GET COMPANY ALIASES
        # =================================================

        aliases = self.stock_aliases.get(symbol)

        # =================================================
        # FALLBACK FOR UNKNOWN STOCK
        # =================================================

        if not aliases:

            clean_symbol = (
                symbol
                .replace(".NS", "")
                .replace(".BO", "")
                .strip()
                .lower()
            )

            aliases = [
                clean_symbol
            ]

        # =================================================
        # BUILD NEWSAPI QUERY
        # =================================================

        query_parts = []

        for alias in aliases:

            query_parts.append(
                f'"{alias}"'
            )

        query = " OR ".join(
            query_parts
        )

        print(
            "STOCK NEWS QUERY:",
            query
        )

        try:

            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 50,
                    "apiKey": api_key
                },
                timeout=15
            )

            print(
                "STOCK NEWS API STATUS:",
                response.status_code
            )

            if response.status_code != 200:

                try:
                    details = response.json()
                except Exception:
                    details = response.text

                return {
                    "error":
                        "Unable to fetch stock news",

                    "status_code":
                        response.status_code,

                    "details":
                        details
                }

            data = response.json()

            news_list = []

            seen_urls = set()

            # =================================================
            # STRICT RELEVANCE CHECK
            # =================================================

            for article in data.get(
                "articles",
                []
            ):

                title = (
                    article.get("title")
                    or ""
                )

                description = (
                    article.get("description")
                    or ""
                )

                article_url = (
                    article.get("url")
                    or ""
                )

                # =================================================
                # FIND ACTUAL COMPANY MATCH
                # =================================================

                matched_alias = (
                    self._find_matching_alias(
                        title,
                        description,
                        aliases
                    )
                )

                # =================================================
                # IGNORE UNRELATED ARTICLE
                # =================================================

                if matched_alias is None:

                    continue

                # =================================================
                # REMOVE DUPLICATES
                # =================================================

                if article_url in seen_urls:

                    continue

                seen_urls.add(
                    article_url
                )

                # =================================================
                # SENTIMENT
                # =================================================

                text = (
                    f"{title} {description}"
                )

                sentiment = (
                    self.analyze_sentiment(
                        text
                    )
                )

                news_list.append({

                    "title":
                        title,

                    "description":
                        description,

                    "source":
                        article.get(
                            "source",
                            {}
                        ).get("name"),

                    "url":
                        article_url,

                    "published_at":
                        article.get(
                            "publishedAt"
                        ),

                    "matched_company":
                        matched_alias,

                    "sentiment":
                        sentiment.get(
                            "sentiment",
                            "Neutral"
                        ),

                    "positive_score":
                        sentiment.get(
                            "positive_score",
                            0
                        ),

                    "negative_score":
                        sentiment.get(
                            "negative_score",
                            0
                        )
                })

                # =================================================
                # MAX 10 STOCK NEWS
                # =================================================

                if len(news_list) >= 10:

                    break

            print(
                f"{symbol} relevant articles:",
                len(news_list)
            )

            return news_list

        except requests.exceptions.RequestException as e:

            print(
                f"{symbol} NEWS NETWORK ERROR:",
                str(e)
            )

            return {
                "error":
                    "Network error while fetching stock news",

                "details":
                    str(e)
            }

        except Exception as e:

            print(
                f"{symbol} NEWS UNEXPECTED ERROR:",
                str(e)
            )

            return {
                "error":
                    "Unexpected error while fetching stock news",

                "details":
                    str(e)
            }

    # =====================================================
    # OVERALL NEWS SENTIMENT
    # =====================================================

    def get_overall_sentiment(self):

        print(
            "INSIDE GET_OVERALL_SENTIMENT"
        )

        news = self.get_news()

        # =================================================
        # ERROR HANDLING
        # =================================================

        if isinstance(news, dict):

            return {

                "overall_sentiment":
                    "Neutral",

                "positive_count":
                    0,

                "negative_count":
                    0,

                "neutral_count":
                    0,

                "total_articles":
                    0,

                "message":
                    "Unable to analyze market "
                    "news sentiment.",

                "error":
                    news
            }

        # =================================================
        # NO NEWS
        # =================================================

        if not news:

            return {

                "overall_sentiment":
                    "Neutral",

                "positive_count":
                    0,

                "negative_count":
                    0,

                "neutral_count":
                    0,

                "total_articles":
                    0,

                "message":
                    "No news available for "
                    "sentiment analysis."
            }

        # =================================================
        # COUNT SENTIMENT
        # =================================================

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for article in news:

            sentiment = article.get(
                "sentiment",
                "Neutral"
            )

            if sentiment == "Positive":

                positive_count += 1

            elif sentiment == "Negative":

                negative_count += 1

            else:

                neutral_count += 1

        # =================================================
        # DETERMINE OVERALL SENTIMENT
        # =================================================

        if positive_count > negative_count:

            overall_sentiment = "Positive"

        elif negative_count > positive_count:

            overall_sentiment = "Negative"

        else:

            overall_sentiment = "Neutral"

        # =================================================
        # FINAL RESPONSE
        # =================================================

        return {

            "overall_sentiment":
                overall_sentiment,

            "positive_count":
                positive_count,

            "negative_count":
                negative_count,

            "neutral_count":
                neutral_count,

            "total_articles":
                len(news),

            "message":
                (
                    f"Market news sentiment is "
                    f"{overall_sentiment.lower()} "
                    f"based on the latest "
                    f"{len(news)} financial news "
                    f"articles."
                )
        }