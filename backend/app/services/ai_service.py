import os
import requests

from dotenv import load_dotenv


load_dotenv()


class AIService:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        # Supported providers:
        # - ollama
        # - gemini
        self.ai_provider = os.getenv(
            "AI_PROVIDER",
            "ollama"
        ).lower()

        # -------------------------------------------------
        # OLLAMA CONFIGURATION
        # -------------------------------------------------

        self.ollama_url = os.getenv(
            "OLLAMA_URL",
            "http://localhost:11434"
        )

        self.ollama_model = os.getenv(
            "OLLAMA_MODEL",
            "llama3.2:3b"
        )

        self.ollama_timeout = int(
            os.getenv(
                "OLLAMA_TIMEOUT",
                "120"
            )
        )

        # -------------------------------------------------
        # GEMINI CONFIGURATION
        # -------------------------------------------------

        self.gemini_api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        self.gemini_model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        self.gemini_timeout = int(
            os.getenv(
                "GEMINI_TIMEOUT",
                "120"
            )
        )

        # -------------------------------------------------
        # LOG PROVIDER
        # -------------------------------------------------

        print(
            "AI PROVIDER:",
            self.ai_provider
        )

        if self.ai_provider == "gemini":

            print(
                "GEMINI MODEL:",
                self.gemini_model
            )

        else:

            print(
                "OLLAMA URL:",
                self.ollama_url
            )

            print(
                "OLLAMA MODEL:",
                self.ollama_model
            )

    # =====================================================
    # AI REQUEST ROUTER
    # =====================================================

    def _ask_ollama(self, prompt):

        if self.ai_provider == "gemini":

            return self._ask_gemini(
                prompt
            )

        return self._ask_local_ollama(
            prompt
        )

    # =====================================================
    # LOCAL OLLAMA REQUEST
    # =====================================================

    def _ask_local_ollama(self, prompt):

        try:

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.ollama_timeout
            )

            response.raise_for_status()

            data = response.json()

            result = (
                data.get("response")
                or ""
            ).strip()

            if not result:

                print(
                    "Ollama returned an empty response."
                )

                return None

            return result

        except requests.exceptions.RequestException as e:

            print(
                "OLLAMA REQUEST ERROR:",
                repr(e)
            )

            return None

        except Exception as e:

            print(
                "OLLAMA ERROR:",
                repr(e)
            )

            return None

    # =====================================================
    # GEMINI REQUEST
    # =====================================================

    def _ask_gemini(self, prompt):

        if not self.gemini_api_key:

            print(
                "GEMINI API KEY is not configured."
            )

            return None

        try:

            url = (
                "https://generativelanguage.googleapis.com/"
                f"v1beta/models/"
                f"{self.gemini_model}:generateContent"
            )

            headers = {
                "x-goog-api-key":
                    self.gemini_api_key,

                "Content-Type":
                    "application/json"
            }

            payload = {

                "contents": [

                    {
                        "parts": [

                            {
                                "text": prompt
                            }

                        ]
                    }

                ]
            }

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.gemini_timeout
            )

            response.raise_for_status()

            data = response.json()

            candidates = data.get(
                "candidates",
                []
            )

            if not candidates:

                print(
                    "Gemini returned no candidates."
                )

                return None

            content = candidates[0].get(
                "content",
                {}
            )

            parts = content.get(
                "parts",
                []
            )

            result = "\n".join(
                part.get("text", "")
                for part in parts
                if part.get("text")
            ).strip()

            if not result:

                print(
                    "Gemini returned an empty response."
                )

                return None

            return result

        except requests.exceptions.RequestException as e:

            print(
                "GEMINI REQUEST ERROR:",
                repr(e)
            )

            return None

        except Exception as e:

            print(
                "GEMINI ERROR:",
                repr(e)
            )

            return None

    # =====================================================
    # SAFE NUMBER
    # =====================================================

    def _number(self, value):

        try:

            return float(value)

        except (
            TypeError,
            ValueError
        ):

            return 0.0

    # =====================================================
    # NORMALIZE NEWS
    # =====================================================

    def _normalize_news(self, news):

        if isinstance(news, list):

            return news

        if isinstance(news, dict):

            articles = news.get("articles")

            if isinstance(articles, list):

                return articles

            articles = news.get("news")

            if isinstance(articles, list):

                return articles

            if "title" in news:

                return [news]

        return []

    # =====================================================
    # NEWS SUMMARY
    # =====================================================

    def _summarize_news(self, news):

        news = self._normalize_news(news)

        positive = 0
        negative = 0
        neutral = 0

        articles = []

        for article in news:

            if not isinstance(article, dict):

                continue

            sentiment = (
                article.get(
                    "sentiment",
                    "Neutral"
                )
                or "Neutral"
            )

            sentiment = (
                str(sentiment)
                .strip()
                .capitalize()
            )

            if sentiment == "Positive":

                positive += 1

            elif sentiment == "Negative":

                negative += 1

            else:

                neutral += 1

            articles.append({
                "title":
                    article.get(
                        "title",
                        ""
                    ) or "",

                "description":
                    article.get(
                        "description",
                        ""
                    ) or "",

                "source":
                    article.get(
                        "source",
                        ""
                    ) or "",

                "sentiment":
                    sentiment
            })

        total = (
            positive
            + negative
            + neutral
        )

        if positive > negative:

            overall = "Positive"

        elif negative > positive:

            overall = "Negative"

        else:

            overall = "Neutral"

        return {
            "sentiment":
                overall,

            "positive_news":
                positive,

            "negative_news":
                negative,

            "neutral_news":
                neutral,

            "total_news":
                total,

            "articles":
                articles
        }

    # =====================================================
    # PORTFOLIO INSIGHT
    #
    # IMPORTANT:
    # This section is deterministic.
    # We do NOT ask the LLM to calculate or interpret
    # holding performance.
    # =====================================================

    def generate_portfolio_insight(
        self,
        portfolio_name,
        total_value,
        current_value,
        profit_loss,
        overall_return,
        risk_level,
        holdings_data,
        performance_summary=None
    ):

        total_value = self._number(
            total_value
        )

        current_value = self._number(
            current_value
        )

        profit_loss = self._number(
            profit_loss
        )

        valid_holdings = [
            holding
            for holding in (holdings_data or [])
            if isinstance(holding, dict)
        ]

        # -------------------------------------------------
        # CLASSIFY HOLDINGS
        # -------------------------------------------------

        positive_holdings = [
            holding
            for holding in valid_holdings
            if self._number(
                holding.get(
                    "profit_loss",
                    0
                )
            ) > 0
        ]

        negative_holdings = [
            holding
            for holding in valid_holdings
            if self._number(
                holding.get(
                    "profit_loss",
                    0
                )
            ) < 0
        ]

        zero_holdings = [
            holding
            for holding in valid_holdings
            if self._number(
                holding.get(
                    "profit_loss",
                    0
                )
            ) == 0
        ]

        # -------------------------------------------------
        # BEST / WORST HOLDING
        # -------------------------------------------------

        best_holding = None
        worst_holding = None

        if positive_holdings:

            best_holding = max(
                positive_holdings,
                key=lambda holding:
                    self._number(
                        holding.get(
                            "profit_loss",
                            0
                        )
                    )
            )

        if negative_holdings:

            worst_holding = min(
                negative_holdings,
                key=lambda holding:
                    self._number(
                        holding.get(
                            "profit_loss",
                            0
                        )
                    )
            )

        # -------------------------------------------------
        # BEST RESULT TEXT
        # -------------------------------------------------

        if best_holding:

            best_symbol = best_holding.get(
                "symbol",
                "Unknown"
            )

            best_profit = self._number(
                best_holding.get(
                    "profit_loss",
                    0
                )
            )

            best_text = (
                f"{best_symbol} with a gain of "
                f"₹{best_profit:,.2f}"
            )

        elif negative_holdings:

            least_loss = max(
                negative_holdings,
                key=lambda holding:
                    self._number(
                        holding.get(
                            "profit_loss",
                            0
                        )
                    )
            )

            least_loss_symbol = (
                least_loss.get(
                    "symbol",
                    "Unknown"
                )
            )

            least_loss_value = self._number(
                least_loss.get(
                    "profit_loss",
                    0
                )
            )

            best_text = (
                "No holding is currently profitable. "
                f"The smallest loss is from "
                f"{least_loss_symbol} at "
                f"₹{abs(least_loss_value):,.2f}."
            )

        else:

            best_text = (
                "No holding-level gain or loss "
                "was recorded."
            )

        # -------------------------------------------------
        # WORST RESULT TEXT
        # -------------------------------------------------

        if worst_holding:

            worst_symbol = worst_holding.get(
                "symbol",
                "Unknown"
            )

            worst_loss = self._number(
                worst_holding.get(
                    "profit_loss",
                    0
                )
            )

            worst_text = (
                f"{worst_symbol} with a loss of "
                f"₹{abs(worst_loss):,.2f}"
            )

        else:

            worst_text = (
                "No holding-level loss was recorded."
            )

        # -------------------------------------------------
        # PORTFOLIO PERFORMANCE
        # -------------------------------------------------

        if profit_loss > 0:

            performance_text = (
                f"The {portfolio_name} has a gain of "
                f"₹{profit_loss:,.2f}, with an overall "
                f"return of {overall_return}. "
                f"The invested value is "
                f"₹{total_value:,.2f} and the current "
                f"value is ₹{current_value:,.2f}."
            )

        elif profit_loss < 0:

            performance_text = (
                f"The {portfolio_name} has a loss of "
                f"₹{abs(profit_loss):,.2f}, with an overall "
                f"return of {overall_return}. "
                f"The invested value is "
                f"₹{total_value:,.2f} and the current "
                f"value is ₹{current_value:,.2f}."
            )

        else:

            performance_text = (
                f"The {portfolio_name} has no recorded "
                f"profit or loss. The invested value is "
                f"₹{total_value:,.2f} and the current "
                f"value is ₹{current_value:,.2f}."
            )

        # -------------------------------------------------
        # HOLDING PERFORMANCE
        # -------------------------------------------------

        holding_lines = []

        for holding in valid_holdings:

            symbol = holding.get(
                "symbol",
                "Unknown"
            )

            holding_profit_loss = self._number(
                holding.get(
                    "profit_loss",
                    0
                )
            )

            holding_current_value = self._number(
                holding.get(
                    "current_value",
                    0
                )
            )

            if holding_profit_loss > 0:

                status = "Gain"

            elif holding_profit_loss < 0:

                status = "Loss"

            else:

                status = "No gain or loss"

            holding_lines.append(
                f"- {symbol}: "
                f"Current Value ₹{holding_current_value:,.2f}, "
                f"Profit/Loss ₹{holding_profit_loss:,.2f}, "
                f"Status: {status}"
            )

        if not holding_lines:

            holding_lines.append(
                "- No holding-level data is available."
            )

        # -------------------------------------------------
        # IMPORTANT OBSERVATIONS
        # -------------------------------------------------

        observation_parts = []

        observation_parts.append(
            f"The portfolio contains "
            f"{len(valid_holdings)} holding(s)."
        )

        if positive_holdings:

            observation_parts.append(
                f"{len(positive_holdings)} holding(s) "
                f"show a gain."
            )

        if negative_holdings:

            observation_parts.append(
                f"{len(negative_holdings)} holding(s) "
                f"show a loss."
            )

        if zero_holdings:

            observation_parts.append(
                f"{len(zero_holdings)} holding(s) "
                f"show no gain or loss."
            )

        important_observations = " ".join(
            observation_parts
        )

        # -------------------------------------------------
        # RISK OBSERVATIONS
        # -------------------------------------------------

        risk_observation = (
            f"The supplied portfolio risk level "
            f"is {risk_level}."
        )

        if negative_holdings:

            risk_observation += (
                f" {len(negative_holdings)} holding(s) "
                f"currently show a loss based on the "
                f"supplied holding-level data."
            )

        # -------------------------------------------------
        # AREAS TO REVIEW
        # -------------------------------------------------

        review_items = []

        if worst_holding:

            worst_symbol = worst_holding.get(
                "symbol",
                "Unknown"
            )

            worst_loss = abs(
                self._number(
                    worst_holding.get(
                        "profit_loss",
                        0
                    )
                )
            )

            review_items.append(
                f"Review {worst_symbol}, which has the "
                f"largest supplied holding-level loss "
                f"of ₹{worst_loss:,.2f}."
            )

        if positive_holdings and negative_holdings:

            review_items.append(
                "Review the difference in performance "
                "between gain-making and loss-making "
                "holdings."
            )

        if len(valid_holdings) > 1:

            review_items.append(
                "Review the current portfolio allocation "
                "and holding-level performance."
            )

        if not review_items:

            review_items.append(
                "Review the available portfolio metrics "
                "periodically."
            )

        # -------------------------------------------------
        # FINAL DETERMINISTIC REPORT
        # -------------------------------------------------

        report = (
            "Portfolio Performance\n\n"

            f"{performance_text}\n\n"

            "Holdings Performance\n\n"

            f"The strongest supplied holding result is "
            f"{best_text}. "
            f"The weakest supplied holding result is "
            f"{worst_text}.\n\n"

            + "\n".join(
                holding_lines
            )

            + "\n\n"

            "Important Observations\n\n"

            f"{important_observations}\n\n"

            "Portfolio Composition\n\n"

            f"The {portfolio_name} contains "
            f"{len(valid_holdings)} holding(s). "
            f"Allocation percentages should be "
            f"interpreted from the supplied portfolio "
            f"analytics.\n\n"

            "Portfolio Risk Observations\n\n"

            f"{risk_observation}\n\n"

            "Areas to Review\n\n"

            + "\n".join(
                f"{index + 1}. {item}"
                for index, item in enumerate(
                    review_items
                )
            )
        )

        return report

    # =====================================================
    # STOCK INSIGHT
    # =====================================================

    def generate_stock_insight(
        self,
        symbol,
        market_analysis,
        news=None,
        news_data=None
    ):

        if news is None:

            news = news_data

        if not isinstance(
            market_analysis,
            dict
        ):

            market_analysis = {}

        news_summary = (
            self._summarize_news(
                news
            )
        )

        close = self._number(
            market_analysis.get(
                "close",
                0
            )
        )

        daily_return = self._number(
            market_analysis.get(
                "daily_return",
                0
            )
        )

        volatility = self._number(
            market_analysis.get(
                "volatility",
                0
            )
        )

        trend = (
            market_analysis.get(
                "trend",
                "Neutral"
            )
            or "Neutral"
        )

        rsi = self._number(
            market_analysis.get(
                "rsi",
                0
            )
        )

        rsi_signal = (
            market_analysis.get(
                "rsi_signal",
                "Neutral"
            )
            or "Neutral"
        )

        macd = self._number(
            market_analysis.get(
                "macd",
                0
            )
        )

        macd_signal = self._number(
            market_analysis.get(
                "macd_signal",
                0
            )
        )

        macd_trend = (
            market_analysis.get(
                "macd_trend",
                "Neutral"
            )
            or "Neutral"
        )

        signal_score = int(
            self._number(
                market_analysis.get(
                    "signal_score",
                    0
                )
            )
        )

        overall_signal = (
            market_analysis.get(
                "overall_signal",
                "Neutral"
            )
            or "Neutral"
        )

        # -------------------------------------------------
        # NEWS TEXT
        # -------------------------------------------------

        news_text = ""

        for article in news_summary["articles"]:

            title = article.get(
                "title",
                ""
            )

            source = article.get(
                "source",
                ""
            )

            sentiment = article.get(
                "sentiment",
                "Neutral"
            )

            if title:

                news_text += (
                    f"- {title} | "
                    f"{source} | "
                    f"Sentiment: {sentiment}\n"
                )

        if not news_text:

            news_text = (
                "No relevant company-specific "
                "news articles were available."
            )

        # -------------------------------------------------
        # PROMPT
        # -------------------------------------------------

        prompt = f"""
You are a financial intelligence assistant.

Analyze this stock using ONLY the supplied data.

Stock:
{symbol}

TECHNICAL DATA

Current Price:
₹{close:,.2f}

Daily Return:
{daily_return:.2f}%

Volatility:
{volatility:.2f}%

Trend:
{trend}

RSI:
{rsi:.2f}

RSI Signal:
{rsi_signal}

MACD:
{macd:.2f}

MACD Signal:
{macd_signal:.2f}

MACD Trend:
{macd_trend}

Signal Score:
{signal_score}

Overall Technical Signal:
{overall_signal}

NEWS DATA

Overall News Sentiment:
{news_summary['sentiment']}

Positive News:
{news_summary['positive_news']}

Negative News:
{news_summary['negative_news']}

Neutral News:
{news_summary['neutral_news']}

Total News:
{news_summary['total_news']}

Recent Articles:
{news_text}

Generate a concise Stock Intelligence Report.

Use exactly these five sections:

1. Technical Overview
2. News Overview
3. Key Observations
4. Risk Factors
5. What to Monitor

STRICT RULES:

- Use only supplied data.
- Do not invent company events.
- Do not invent news.
- Do not give buy recommendations.
- Do not give sell recommendations.
- Do not give hold recommendations.
- Do not provide investment advice.
- Explain conflicting technical signals when present.
- Explain whether news sentiment supports or differs
  from the technical picture.
- Mention volatility only based on the supplied value.
- Do not claim causation.
- Do not invent correlations.
- If no news is available, clearly state that.
- Avoid repetition.
- Keep the report professional.
"""

        response = self._ask_ollama(
            prompt
        )

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        if not response:

            return (
                f"Stock Intelligence Report: "
                f"{symbol}\n\n"

                "1. Technical Overview:\n"
                f"The stock is trading at "
                f"₹{close:,.2f}. "
                f"The current trend is {trend} "
                f"with an overall technical signal "
                f"of {overall_signal}.\n\n"

                "2. News Overview:\n"
                f"There are "
                f"{news_summary['positive_news']} "
                f"positive, "
                f"{news_summary['negative_news']} "
                f"negative and "
                f"{news_summary['neutral_news']} "
                f"neutral articles. "
                f"Overall news sentiment is "
                f"{news_summary['sentiment']}.\n\n"

                "3. Key Observations:\n"
                f"RSI is {rsi:.2f} with a "
                f"{rsi_signal} signal. "
                f"MACD shows a "
                f"{macd_trend} trend.\n\n"

                "4. Risk Factors:\n"
                f"Current volatility is "
                f"{volatility:.2f}%. "
                f"Mixed technical signals may "
                f"create uncertainty.\n\n"

                "5. What to Monitor:\n"
                "Monitor changes in trend, RSI, "
                "MACD, volatility and relevant "
                "company-specific news."
            )

        return response

    # =====================================================
    # FINANCIAL INTELLIGENCE
    # =====================================================

    def generate_financial_intelligence(
        self,
        market_analysis,
        portfolio_analysis,
        news
    ):

        if not isinstance(
            market_analysis,
            dict
        ):

            market_analysis = {}

        if not isinstance(
            portfolio_analysis,
            dict
        ):

            portfolio_analysis = {}

        news_summary = (
            self._summarize_news(
                news
            )
        )

        # -------------------------------------------------
        # PROMPT
        # -------------------------------------------------

        prompt = f"""
You are a financial intelligence assistant.

Create a high-level Financial Intelligence Report
using ONLY the supplied data.

Your job is to summarize the available evidence.

You must NOT invent facts or infer unsupported
relationships.

==================================================
MARKET DATA
==================================================

Trend:
{market_analysis.get('trend', 'Unknown')}

Daily Return:
{market_analysis.get('daily_return', 0)}%

Volatility:
{market_analysis.get('volatility', 0)}%

Signal Score:
{market_analysis.get('signal_score', 0)}

Overall Signal:
{market_analysis.get('overall_signal', 'Unknown')}

==================================================
PORTFOLIO DATA
==================================================

Portfolio:
{portfolio_analysis.get('portfolio_name', 'Unknown')}

Invested Value:
₹{portfolio_analysis.get('total_value', 0)}

Current Value:
₹{portfolio_analysis.get('current_value', 0)}

Profit/Loss:
₹{portfolio_analysis.get('profit_loss', 0)}

Overall Return:
{portfolio_analysis.get('overall_return', '0%')}

Risk Level:
{portfolio_analysis.get('risk_level', 'Unknown')}

==================================================
NEWS DATA
==================================================

Overall Sentiment:
{news_summary['sentiment']}

Positive:
{news_summary['positive_news']}

Negative:
{news_summary['negative_news']}

Neutral:
{news_summary['neutral_news']}

Total:
{news_summary['total_news']}

==================================================
REPORT FORMAT
==================================================

Use EXACTLY these five sections:

1. Current Market Condition

2. Portfolio Performance

3. Relationship Between Market and Portfolio

4. Important Financial News Themes

5. Key Risks or Areas to Monitor

==================================================
STRICT RULES
==================================================

1. Use ONLY the supplied data.

2. Do NOT invent facts.

3. Do NOT invent financial events.

4. Do NOT invent numbers.

5. Do NOT provide direct buy recommendations.

6. Do NOT provide direct sell recommendations.

7. Do NOT provide hold recommendations.

8. Do NOT provide investment advice.

9. Do NOT claim that market movements caused
   portfolio performance.

10. Do NOT claim that market and portfolio are
    correlated unless actual correlation data
    has explicitly been supplied.

11. In Section 3, if the supplied data is not
    sufficient to establish a relationship,
    explicitly state that the relationship
    cannot be determined from the supplied data.

12. Do NOT assume that a Moderate risk level means
    the portfolio is sensitive to market movements.

13. Do NOT interpret volatility beyond the supplied
    volatility value.

14. Clearly distinguish observed data from interpretation.

15. Avoid repetition.

16. Keep the report concise, professional and factual.
"""

        response = self._ask_ollama(
            prompt
        )

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        if not response:

            market_signal = market_analysis.get(
                "overall_signal",
                "Unknown"
            )

            daily_return = market_analysis.get(
                "daily_return",
                0
            )

            portfolio_profit_loss = (
                portfolio_analysis.get(
                    "profit_loss",
                    0
                )
            )

            portfolio_return = (
                portfolio_analysis.get(
                    "overall_return",
                    "0%"
                )
            )

            return (
                "Financial Intelligence Report\n\n"

                "1. Current Market Condition:\n"
                f"The current market signal is "
                f"{market_signal} "
                f"with a daily return of "
                f"{daily_return}%.\n\n"

                "2. Portfolio Performance:\n"
                f"The portfolio has a profit/loss "
                f"of ₹{portfolio_profit_loss} "
                f"with an overall return of "
                f"{portfolio_return}.\n\n"

                "3. Relationship Between Market "
                "and Portfolio:\n"
                "The supplied data does not provide "
                "sufficient information to establish "
                "a direct relationship between market "
                "conditions and portfolio performance.\n\n"

                "4. Important Financial News Themes:\n"
                f"Overall news sentiment is "
                f"{news_summary['sentiment']} "
                f"based on "
                f"{news_summary['total_news']} "
                f"articles.\n\n"

                "5. Key Risks or Areas to Monitor:\n"
                "Monitor portfolio performance, "
                "market signals, volatility and "
                "relevant financial news."
            )

        return response