import os
import requests

from dotenv import load_dotenv
from app.services.sentiment_service import SentimentService


# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()


class NewsService:

    def __init__(self):

        self.sentiment_service = SentimentService()

        # -------------------------------------------------
        # STOCK SYMBOL → COMPANY ALIASES
        # -------------------------------------------------

        self.stock_aliases = {

            "RELIANCE.NS": [
                "Reliance Industries",
                "Reliance Industries Limited",
                "Reliance Jio",
                "Reliance Retail"
            ],

            "TCS.NS": [
                "Tata Consultancy Services",
                "Tata Consultancy",
                "TCS"
            ],

            "INFY.NS": [
                "Infosys",
                "Infosys Limited"
            ],

            "HDFCBANK.NS": [
                "HDFC Bank",
                "HDFC Bank Limited"
            ],

            "ICICIBANK.NS": [
                "ICICI Bank",
                "ICICI Bank Limited"
            ],

            "SBIN.NS": [
                "State Bank of India",
                "State Bank",
                "SBI"
            ],

            "BHARTIARTL.NS": [
                "Bharti Airtel",
                "Bharti Airtel Limited",
                "Airtel India"
            ],

            "ITC.NS": [
                "ITC Limited",
                "ITC Ltd"
            ],

            "LT.NS": [
                "Larsen & Toubro",
                "Larsen and Toubro",
                "Larsen Toubro"
            ],

            "HINDUNILVR.NS": [
                "Hindustan Unilever",
                "Hindustan Unilever Limited",
                "HUL"
            ],

            "AXISBANK.NS": [
                "Axis Bank",
                "Axis Bank Limited"
            ],

            "KOTAKBANK.NS": [
                "Kotak Mahindra Bank",
                "Kotak Mahindra",
                "Kotak Bank"
            ],

            "MARUTI.NS": [
                "Maruti Suzuki",
                "Maruti Suzuki India",
                "Maruti"
            ],

            "TATAMOTORS.NS": [
                "Tata Motors",
                "Tata Motors Limited"
            ],

            "SUNPHARMA.NS": [
                "Sun Pharma",
                "Sun Pharmaceutical",
                "Sun Pharmaceutical Industries"
            ],

            "ADANIENT.NS": [
                "Adani Enterprises",
                "Adani Enterprises Limited"
            ],

            "ADANIPORTS.NS": [
                "Adani Ports",
                "Adani Ports and SEZ",
                "Adani Ports and Special Economic Zone"
            ]
        }

    # =========================================================
    # API KEY
    # =========================================================

    def _get_api_key(self):

        api_key = os.getenv("NEWS_API_KEY")

        if not api_key:
            return None

        api_key = api_key.strip()

        if not api_key:
            return None

        return api_key

    # =========================================================
    # SENTIMENT
    # =========================================================

    def analyze_sentiment(self, text):

        try:

            result = self.sentiment_service.analyze(
                text
            )

            if isinstance(result, dict):

                return result

            return {
                "sentiment": "Neutral",
                "positive_score": 0,
                "negative_score": 0
            }

        except Exception as e:

            print(
                "Sentiment analysis error:",
                str(e)
            )

            return {
                "sentiment": "Neutral",
                "positive_score": 0,
                "negative_score": 0
            }

    # =========================================================
    # NEWSAPI REQUEST
    # =========================================================

    def _request_newsapi(
        self,
        query,
        page_size=50
    ):

        api_key = self._get_api_key()

        if not api_key:

            return {
                "success": False,
                "error": "NEWS_API_KEY is missing."
            }

        try:

            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": page_size,
                    "apiKey": api_key
                },
                timeout=15
            )

            print(
                "NEWS API STATUS:",
                response.status_code
            )

            try:
                data = response.json()

            except Exception:

                data = {}

            if response.status_code != 200:

                return {
                    "success": False,
                    "error": (
                        data.get(
                            "message",
                            "NewsAPI request failed."
                        )
                        if isinstance(data, dict)
                        else "NewsAPI request failed."
                    ),
                    "status_code": response.status_code,
                    "details": data
                }

            if data.get("status") != "ok":

                return {
                    "success": False,
                    "error": data.get(
                        "message",
                        "NewsAPI returned an error."
                    ),
                    "details": data
                }

            return {
                "success": True,
                "articles": data.get(
                    "articles",
                    []
                )
            }

        except requests.exceptions.RequestException as e:

            print(
                "NEWS NETWORK ERROR:",
                str(e)
            )

            return {
                "success": False,
                "error": (
                    "Network error while fetching news."
                ),
                "details": str(e)
            }

        except Exception as e:

            print(
                "NEWS UNEXPECTED ERROR:",
                str(e)
            )

            return {
                "success": False,
                "error": "Unexpected news error.",
                "details": str(e)
            }

    # =========================================================
    # GENERAL FINANCIAL NEWS
    # =========================================================

    def get_news(self):

        print(
            "INSIDE GET_NEWS"
        )

        query = (
            '(Nifty OR Sensex OR NSE OR BSE OR '
            '"Indian stock market" OR "Indian stocks" '
            'OR Reliance OR TCS OR Infosys) '
            'AND '
            '(stock OR stocks OR market OR shares OR '
            'equity OR equities OR trading OR investor OR '
            'earnings OR results OR finance OR economy)'
        )

        result = self._request_newsapi(
            query=query,
            page_size=50
        )

        if not result.get("success"):

            print(
                "NEWS API ERROR:",
                result.get("error")
            )

            return {
                "error": result.get(
                    "error",
                    "Unable to fetch news."
                ),
                "status_code": result.get(
                    "status_code"
                ),
                "details": result.get(
                    "details"
                )
            }

        articles = result.get(
            "articles",
            []
        )

        news_list = []
        seen_urls = set()

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

        # -----------------------------------------------------
        # FIRST PASS
        # Strict financial relevance
        # -----------------------------------------------------

        for article in articles:

            title = (
                article.get("title")
                or ""
            ).strip()

            description = (
                article.get("description")
                or ""
            ).strip()

            article_url = (
                article.get("url")
                or ""
            ).strip()

            if not title:
                continue

            text = (
                f"{title} {description}"
            ).lower()

            is_financial = any(
                keyword in text
                for keyword in financial_keywords
            )

            if not is_financial:
                continue

            if article_url and article_url in seen_urls:
                continue

            if article_url:
                seen_urls.add(article_url)

            sentiment = self.analyze_sentiment(
                text
            )

            news_list.append({

                "title": title,

                "description": description,

                "source": (
                    article.get(
                        "source",
                        {}
                    ).get("name")
                    or "Unknown"
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

        # -----------------------------------------------------
        # FALLBACK
        #
        # If NewsAPI returned articles but our filter removed
        # everything, show the returned financial-market
        # articles instead of falsely displaying zero news.
        # -----------------------------------------------------

        if not news_list:

            print(
                "Financial filter returned 0 articles."
            )

            for article in articles:

                title = (
                    article.get("title")
                    or ""
                ).strip()

                description = (
                    article.get("description")
                    or ""
                ).strip()

                article_url = (
                    article.get("url")
                    or ""
                ).strip()

                if not title:
                    continue

                if article_url and article_url in seen_urls:
                    continue

                if article_url:
                    seen_urls.add(article_url)

                text = (
                    f"{title} {description}"
                ).lower()

                sentiment = self.analyze_sentiment(
                    text
                )

                news_list.append({

                    "title": title,

                    "description": description,

                    "source": (
                        article.get(
                            "source",
                            {}
                        ).get("name")
                        or "Unknown"
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

    # =========================================================
    # FIND COMPANY ALIAS
    # =========================================================

    def _find_matching_alias(
        self,
        title,
        description,
        aliases
    ):

        title_lower = (
            title or ""
        ).lower()

        description_lower = (
            description or ""
        ).lower()

        # -----------------------------------------------------
        # TITLE
        # -----------------------------------------------------

        for alias in aliases:

            alias_lower = alias.lower()

            if alias_lower in title_lower:

                return alias

        # -----------------------------------------------------
        # DESCRIPTION
        # -----------------------------------------------------

        for alias in aliases:

            alias_lower = alias.lower()

            if len(alias_lower) <= 4:
                continue

            if alias_lower in description_lower:

                return alias

        return None

    # =========================================================
    # STOCK NEWS
    # =========================================================

    def get_stock_news(
        self,
        symbol
    ):

        print(
            "INSIDE GET_STOCK_NEWS:",
            symbol
        )

        symbol = (
            symbol or ""
        ).upper().strip()

        aliases = self.stock_aliases.get(
            symbol
        )

        if not aliases:

            clean_symbol = (
                symbol
                .replace(".NS", "")
                .replace(".BO", "")
                .strip()
            )

            aliases = [
                clean_symbol
            ]

        query = " OR ".join(
            f'"{alias}"'
            for alias in aliases
        )

        print(
            "STOCK NEWS QUERY:",
            query
        )

        result = self._request_newsapi(
            query=query,
            page_size=50
        )

        if not result.get("success"):

            return {
                "error": result.get(
                    "error",
                    "Unable to fetch stock news."
                ),
                "status_code": result.get(
                    "status_code"
                ),
                "details": result.get(
                    "details"
                )
            }

        articles = result.get(
            "articles",
            []
        )

        news_list = []
        seen_urls = set()

        for article in articles:

            title = (
                article.get("title")
                or ""
            ).strip()

            description = (
                article.get("description")
                or ""
            ).strip()

            article_url = (
                article.get("url")
                or ""
            ).strip()

            if not title:
                continue

            matched_alias = (
                self._find_matching_alias(
                    title,
                    description,
                    aliases
                )
            )

            if matched_alias is None:
                continue

            if article_url and article_url in seen_urls:
                continue

            if article_url:
                seen_urls.add(article_url)

            text = (
                f"{title} {description}"
            )

            sentiment = self.analyze_sentiment(
                text
            )

            news_list.append({

                "title": title,

                "description": description,

                "source": (
                    article.get(
                        "source",
                        {}
                    ).get("name")
                    or "Unknown"
                ),

                "url": article_url,

                "published_at": (
                    article.get(
                        "publishedAt"
                    )
                ),

                "matched_company":
                    matched_alias,

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
            f"{symbol} relevant articles:",
            len(news_list)
        )

        return news_list

    # =========================================================
    # OVERALL SENTIMENT
    # =========================================================

    def get_overall_sentiment(self):

        print(
            "INSIDE GET_OVERALL_SENTIMENT"
        )

        news = self.get_news()

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
                    "Unable to analyze market news sentiment.",

                "error":
                    news
            }

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
                    "No news available for sentiment analysis."
            }

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for article in news:

            sentiment = str(
                article.get(
                    "sentiment",
                    "Neutral"
                )
            ).lower()

            if sentiment == "positive":

                positive_count += 1

            elif sentiment == "negative":

                negative_count += 1

            else:

                neutral_count += 1

        if positive_count > negative_count:

            overall_sentiment = "Positive"

        elif negative_count > positive_count:

            overall_sentiment = "Negative"

        else:

            overall_sentiment = "Neutral"

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
                "News sentiment analyzed successfully."
        }