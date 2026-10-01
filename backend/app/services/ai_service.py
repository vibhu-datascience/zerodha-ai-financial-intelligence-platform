import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()


class AIService:

    def __init__(self):
        self.provider = os.getenv(
            "AI_PROVIDER",
            "gemini"
        ).lower()

        self.gemini_api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        self.gemini_model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.0-flash"
        )

        self.ollama_url = os.getenv(
            "OLLAMA_URL",
            "http://localhost:11434/api/generate"
        )

        self.ollama_model = os.getenv(
            "OLLAMA_MODEL",
            "llama3.2"
        )

    # =========================================================
    # MAIN FINANCIAL INTELLIGENCE
    # =========================================================

    def generate_financial_intelligence(
        self,
        portfolio_analysis,
        market_analysis=None,
        news_data=None,
        news=None,
        **kwargs
    ):
        """
        Main AI generation function.

        Compatible with existing workflow callers.

        Supports:
            market_analysis=...
            news_data=...
            news=...
        """

        if portfolio_analysis is None:
            portfolio_analysis = {}

        market_analysis = market_analysis or {}

        if news_data is None:
            news_data = news or {}

        news_data = news_data or {}

        # -----------------------------------------------------
        # Simple factual questions
        # -----------------------------------------------------

        user_question = portfolio_analysis.get(
            "user_question"
        )

        if user_question:

            simple_answer = self._answer_simple_question(
                user_question=user_question,
                portfolio_analysis=portfolio_analysis
            )

            if simple_answer:
                return simple_answer

        # -----------------------------------------------------
        # AI / LLM response
        # -----------------------------------------------------

        prompt = self._build_copilot_prompt(
            portfolio_analysis=portfolio_analysis,
            market_data=market_analysis,
            news_data=news_data
        )

        try:

            if self.provider == "gemini":

                return self._generate_with_gemini(
                    prompt
                )

            if self.provider == "ollama":

                return self._generate_with_ollama(
                    prompt
                )

            return self._safe_fallback(
                portfolio_analysis
            )

        except Exception as e:

            print(
                f"AI generation error: {e}"
            )

            return self._safe_fallback(
                portfolio_analysis
            )

    # =========================================================
    # PORTFOLIO INSIGHT
    # =========================================================

    def generate_portfolio_insight(
        self,
        portfolio_analysis=None,
        portfolio_name=None,
        timeframe=None,
        **kwargs
    ):
        """
        Generates portfolio-level insight.

        Supports the existing PortfolioService caller,
        including portfolio_name and timeframe arguments.
        """

        if portfolio_analysis is None:
            portfolio_analysis = {}

        # -----------------------------------------------------
        # Preserve compatibility with existing callers
        # -----------------------------------------------------

        if portfolio_name:
            portfolio_analysis["portfolio_name"] = (
                portfolio_name
            )

        if timeframe:
            portfolio_analysis["timeframe"] = (
                timeframe
            )

        try:

            prompt = self._build_report_prompt(
                portfolio_analysis
            )

            if self.provider == "gemini":

                return self._generate_with_gemini(
                    prompt
                )

            if self.provider == "ollama":

                return self._generate_with_ollama(
                    prompt
                )

            return self._portfolio_insight_fallback(
                portfolio_analysis
            )

        except Exception as e:

            print(
                f"Portfolio insight error: {e}"
            )

            return self._portfolio_insight_fallback(
                portfolio_analysis
            )

    # =========================================================
    # SIMPLE PORTFOLIO QUESTION ANSWER
    # =========================================================

    def _answer_simple_question(
        self,
        user_question,
        portfolio_analysis
    ):

        question = (
            user_question
            .lower()
            .strip()
        )

        # -----------------------------------------------------
        # Portfolio-level values
        # -----------------------------------------------------

        invested = float(
            portfolio_analysis.get(
                "total_value",
                0
            )
        )

        current_value = float(
            portfolio_analysis.get(
                "current_value",
                0
            )
        )

        profit_loss = float(
            portfolio_analysis.get(
                "profit_loss",
                0
            )
        )

        holdings = portfolio_analysis.get(
            "holdings",
            []
        )

        # =====================================================
        # TOTAL INVESTED
        # =====================================================

        if (
            "total invested" in question
            or "invested amount" in question
            or "how much did i invest" in question
            or "how much have i invested" in question
        ):

            return (
                f"Your total invested amount is "
                f"₹{invested:,.2f}."
            )

        # =====================================================
        # NUMBER OF STOCKS
        # =====================================================

        if (
            "how many stocks" in question
            or "number of stocks" in question
            or "how many holdings" in question
        ):

            return (
                f"You currently own "
                f"{len(holdings)} stocks "
                f"in your portfolio."
            )

        # =====================================================
        # HOLDING-SPECIFIC CURRENT VALUE
        # =====================================================

        if (
            "current value" in question
            or "worth" in question
            or "value of" in question
        ):

            for holding in holdings:

                symbol = str(
                    holding.get(
                        "symbol",
                        ""
                    )
                ).lower()

                if (
                    symbol
                    and symbol in question
                ):

                    value = float(
                        holding.get(
                            "current_value",
                            0
                        )
                    )

                    return (
                        f"The current value of "
                        f"{holding.get('symbol')} "
                        f"is ₹{value:,.2f}."
                    )

        # =====================================================
        # HOLDING-SPECIFIC CURRENT PRICE
        # =====================================================

        if (
            "current price" in question
            or "latest price" in question
            or "market price" in question
        ):

            for holding in holdings:

                symbol = str(
                    holding.get(
                        "symbol",
                        ""
                    )
                ).lower()

                if (
                    symbol
                    and symbol in question
                ):

                    price = float(
                        holding.get(
                            "current_price",
                            0
                        )
                    )

                    return (
                        f"The current price of "
                        f"{holding.get('symbol')} "
                        f"is ₹{price:,.2f}."
                    )

        # =====================================================
        # HOLDING-SPECIFIC INVESTED VALUE
        # =====================================================

        if (
            "invested value" in question
            or "investment in" in question
        ):

            for holding in holdings:

                symbol = str(
                    holding.get(
                        "symbol",
                        ""
                    )
                ).lower()

                if (
                    symbol
                    and symbol in question
                ):

                    value = float(
                        holding.get(
                            "invested_value",
                            0
                        )
                    )

                    return (
                        f"The invested value of "
                        f"{holding.get('symbol')} "
                        f"is ₹{value:,.2f}."
                    )

        # =====================================================
        # HOLDING-SPECIFIC QUANTITY
        # =====================================================

        if (
            "quantity" in question
            or "shares of" in question
            or "how many shares" in question
        ):

            for holding in holdings:

                symbol = str(
                    holding.get(
                        "symbol",
                        ""
                    )
                ).lower()

                if (
                    symbol
                    and symbol in question
                ):

                    quantity = float(
                        holding.get(
                            "quantity",
                            0
                        )
                    )

                    return (
                        f"You currently own "
                        f"{quantity:g} shares of "
                        f"{holding.get('symbol')}."
                    )

        # =====================================================
        # HOLDING-SPECIFIC BUY PRICE
        # =====================================================

        if (
            "buy price" in question
            or "purchase price" in question
            or "bought at" in question
        ):

            for holding in holdings:

                symbol = str(
                    holding.get(
                        "symbol",
                        ""
                    )
                ).lower()

                if (
                    symbol
                    and symbol in question
                ):

                    buy_price = float(
                        holding.get(
                            "buy_price",
                            0
                        )
                    )

                    return (
                        f"Your buy price for "
                        f"{holding.get('symbol')} "
                        f"is ₹{buy_price:,.2f}."
                    )

        # =====================================================
        # HOLDING-SPECIFIC PROFIT / LOSS
        # =====================================================

        if (
            "profit" in question
            or "loss" in question
            or "p&l" in question
            or "pnl" in question
        ):

            for holding in holdings:

                symbol = str(
                    holding.get(
                        "symbol",
                        ""
                    )
                ).lower()

                if (
                    symbol
                    and symbol in question
                ):

                    holding_pl = float(
                        holding.get(
                            "profit_loss",
                            0
                        )
                    )

                    if holding_pl >= 0:

                        return (
                            f"{holding.get('symbol')} "
                            f"currently has a profit of "
                            f"₹{holding_pl:,.2f}."
                        )

                    return (
                        f"{holding.get('symbol')} "
                        f"currently has a loss of "
                        f"₹{abs(holding_pl):,.2f}."
                    )

        # =====================================================
        # CURRENT PORTFOLIO VALUE
        # =====================================================

        if (
            "current portfolio value" in question
            or "portfolio value" in question
            or "portfolio worth" in question
            or "current value of my portfolio" in question
        ):

            return (
                f"Your current portfolio value is "
                f"₹{current_value:,.2f}."
            )

        # =====================================================
        # PORTFOLIO PROFIT / LOSS
        # =====================================================

        if (
            "portfolio profit" in question
            or "portfolio loss" in question
            or "overall profit" in question
            or "overall loss" in question
            or "my profit" in question
            or "my loss" in question
            or question in ["p&l", "pnl"]
        ):

            if profit_loss >= 0:

                return (
                    f"Your current portfolio profit is "
                    f"₹{profit_loss:,.2f}."
                )

            return (
                f"Your current portfolio loss is "
                f"₹{abs(profit_loss):,.2f}."
            )

        return None

    # =========================================================
    # COPILOT PROMPT
    # =========================================================

    def _build_copilot_prompt(
        self,
        portfolio_analysis,
        market_data,
        news_data
    ):

        user_question = portfolio_analysis.get(
            "user_question",
            ""
        )

        return f"""
You are an AI Financial Intelligence Copilot.

Answer the user's question using ONLY the
provided portfolio, market and news data.

Do not invent numbers.

Do not provide personalized financial advice.

Do not instruct the user to buy, sell,
or hold a particular security.

Do not make unsupported predictions.

If the required information is not available,
clearly say that it is not available.

USER QUESTION:
{user_question}

PORTFOLIO DATA:
{json.dumps(
    portfolio_analysis,
    indent=2,
    default=str
)}

MARKET DATA:
{json.dumps(
    market_data,
    indent=2,
    default=str
)}

NEWS DATA:
{json.dumps(
    news_data,
    indent=2,
    default=str
)}

Give a concise, factual and
data-grounded answer.
"""

    # =========================================================
    # REPORT PROMPT
    # =========================================================

    def _build_report_prompt(
        self,
        portfolio_analysis
    ):

        return f"""
You are a financial data analysis assistant.

Analyze the supplied portfolio data.

Do not provide personalized investment advice.

Do not recommend buying, selling or holding
any security.

Use only the supplied data.

PORTFOLIO DATA:

{json.dumps(
    portfolio_analysis,
    indent=2,
    default=str
)}

Provide:

1. Portfolio overview
2. Performance
3. Risk observations
4. Diversification observations
5. Key data-driven insights

Clearly distinguish calculated facts
from general observations.
"""

    # =========================================================
    # GEMINI
    # =========================================================

    def _generate_with_gemini(
        self,
        prompt
    ):

        if not self.gemini_api_key:

            return (
                "Gemini API key is not configured."
            )

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.gemini_model}:generateContent"
            f"?key={self.gemini_api_key}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1000
            }
        }

        response = requests.post(
            url,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        try:

            return (
                data[
                    "candidates"
                ][0][
                    "content"
                ][
                    "parts"
                ][0][
                    "text"
                ]
            )

        except (
            KeyError,
            IndexError,
            TypeError
        ):

            return (
                "I could not generate a valid AI response."
            )

    # =========================================================
    # OLLAMA
    # =========================================================

    def _generate_with_ollama(
        self,
        prompt
    ):

        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            self.ollama_url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            ""
        )

    # =========================================================
    # GENERIC FALLBACK
    # =========================================================

    def _safe_fallback(
        self,
        portfolio_analysis
    ):

        if not portfolio_analysis:

            return (
                "I could not generate the requested "
                "financial analysis."
            )

        invested = float(
            portfolio_analysis.get(
                "total_value",
                0
            )
        )

        current_value = float(
            portfolio_analysis.get(
                "current_value",
                0
            )
        )

        profit_loss = float(
            portfolio_analysis.get(
                "profit_loss",
                0
            )
        )

        risk_level = portfolio_analysis.get(
            "risk_level",
            "Unknown"
        )

        return (
            f"Portfolio invested value: "
            f"₹{invested:,.2f}\n"
            f"Current value: "
            f"₹{current_value:,.2f}\n"
            f"Profit/Loss: "
            f"₹{profit_loss:,.2f}\n"
            f"Risk level: "
            f"{risk_level}"
        )

    # =========================================================
    # PORTFOLIO INSIGHT FALLBACK
    # =========================================================

    def _portfolio_insight_fallback(
        self,
        portfolio_analysis
    ):

        invested = float(
            portfolio_analysis.get(
                "total_value",
                0
            )
        )

        current_value = float(
            portfolio_analysis.get(
                "current_value",
                0
            )
        )

        profit_loss = float(
            portfolio_analysis.get(
                "profit_loss",
                0
            )
        )

        risk_level = portfolio_analysis.get(
            "risk_level",
            "Unknown"
        )

        holdings = portfolio_analysis.get(
            "holdings",
            []
        )

        if invested:

            overall_return = (
                profit_loss / invested
            ) * 100

        else:

            overall_return = 0

        largest_loss_symbol = None
        largest_loss = 0

        for holding in holdings:

            holding_loss = float(
                holding.get(
                    "profit_loss",
                    0
                )
            )

            if holding_loss < largest_loss:

                largest_loss = holding_loss

                largest_loss_symbol = holding.get(
                    "symbol"
                )

        insight = (
            f"The portfolio has an invested value "
            f"of ₹{invested:,.2f} and a current value "
            f"of ₹{current_value:,.2f}. "
            f"The current profit/loss is "
            f"₹{profit_loss:,.2f}, representing an "
            f"overall return of {overall_return:.2f}%. "
            f"The calculated portfolio risk level is "
            f"{risk_level}. "
            f"The portfolio contains "
            f"{len(holdings)} holdings."
        )

        if largest_loss_symbol:

            insight += (
                f" The largest loss among the supplied "
                f"holdings is associated with "
                f"{largest_loss_symbol}."
            )

        return insight