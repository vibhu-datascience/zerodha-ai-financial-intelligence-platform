from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User

from app.dependencies.auth import get_current_user

from app.services.portfolio_service import (
    PortfolioService
)

from app.services.ai_workflow import (
    run_financial_workflow_sync
)


router = APIRouter()


# =========================================================
# AI PORTFOLIO INSIGHT
# =========================================================

@router.post("/ai/portfolio-insight")
def generate_portfolio_insight(
    portfolio_name: str,
    timeframe: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    portfolio_service = PortfolioService(db)

    try:

        result = (
            portfolio_service
            .analyze_portfolio(
                portfolio_name=portfolio_name,
                timeframe=timeframe,
                user_id=current_user.id
            )
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Portfolio insight failed: {str(e)}"
            )
        )


# =========================================================
# AI FINANCIAL COPILOT
# =========================================================

@router.post("/ai/copilot")
def financial_copilot(
    question: str,
    portfolio_name: str = "Growth Portfolio",
    timeframe: str = "1Y",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    question = question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please enter a financial question."
            )
        )

    portfolio_service = PortfolioService(db)

    # =====================================================
    # STEP 1
    # AUTHORITATIVE PORTFOLIO ANALYSIS
    # =====================================================

    try:

        portfolio_analysis = (
            portfolio_service
            .analyze_portfolio(
                portfolio_name=portfolio_name,
                timeframe=timeframe,
                user_id=current_user.id
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Portfolio analysis failed: {str(e)}"
            )
        )

    question_lower = question.lower()

    holdings = portfolio_analysis.get(
        "holdings",
        []
    )

    # =====================================================
    # STEP 2
    # PORTFOLIO ANALYTICS
    # =====================================================

    analytics = portfolio_analysis.get(
        "analytics",
        {}
    )

    if not isinstance(
        analytics,
        dict
    ):

        analytics = {}

    # =====================================================
    # HOLDING-SPECIFIC CURRENT VALUE
    # =====================================================

    if (
        "current value" in question_lower
        or "worth" in question_lower
        or "value of" in question_lower
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
                and symbol in question_lower
            ):

                current_value = float(
                    holding.get(
                        "current_value",
                        0
                    )
                )

                return {
                    "question": question,

                    "answer": (
                        f"The current value of "
                        f"{holding.get('symbol')} "
                        f"is ₹{current_value:,.2f}."
                    ),

                    "validation_status":
                        "passed",

                    "validation_errors":
                        []
                }

    # =====================================================
    # HOLDING-SPECIFIC CURRENT PRICE
    # =====================================================

    if (
        "current price" in question_lower
        or "latest price" in question_lower
        or "market price" in question_lower
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
                and symbol in question_lower
            ):

                current_price = float(
                    holding.get(
                        "current_price",
                        0
                    )
                )

                return {
                    "question": question,

                    "answer": (
                        f"The current price of "
                        f"{holding.get('symbol')} "
                        f"is ₹{current_price:,.2f}."
                    ),

                    "validation_status":
                        "passed",

                    "validation_errors":
                        []
                }

    # =====================================================
    # HOLDING-SPECIFIC INVESTED VALUE
    # =====================================================

    if (
        "invested value" in question_lower
        or "investment in" in question_lower
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
                and symbol in question_lower
            ):

                invested_value = float(
                    holding.get(
                        "invested_value",
                        0
                    )
                )

                return {
                    "question": question,

                    "answer": (
                        f"The invested value of "
                        f"{holding.get('symbol')} "
                        f"is ₹{invested_value:,.2f}."
                    ),

                    "validation_status":
                        "passed",

                    "validation_errors":
                        []
                }

    # =====================================================
    # HOLDING-SPECIFIC PROFIT / LOSS
    # =====================================================

    if (
        "profit" in question_lower
        or "loss" in question_lower
        or "p&l" in question_lower
        or "pnl" in question_lower
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
                and symbol in question_lower
            ):

                profit_loss = float(
                    holding.get(
                        "profit_loss",
                        0
                    )
                )

                if profit_loss >= 0:

                    answer = (
                        f"{holding.get('symbol')} "
                        f"currently has a profit of "
                        f"₹{profit_loss:,.2f}."
                    )

                else:

                    answer = (
                        f"{holding.get('symbol')} "
                        f"currently has a loss of "
                        f"₹{abs(profit_loss):,.2f}."
                    )

                return {
                    "question": question,

                    "answer":
                        answer,

                    "validation_status":
                        "passed",

                    "validation_errors":
                        []
                }

    # =====================================================
    # TOTAL INVESTED
    # =====================================================

    if (
        "total invested" in question_lower
        or "invested amount" in question_lower
        or "how much did i invest" in question_lower
    ):

        invested = float(
            portfolio_analysis.get(
                "total_value",
                0
            )
        )

        return {
            "question": question,

            "answer": (
                f"Your total invested amount is "
                f"₹{invested:,.2f}."
            ),

            "validation_status":
                "passed",

            "validation_errors":
                []
        }

    # =====================================================
    # CURRENT PORTFOLIO VALUE
    # =====================================================

    if (
        "current portfolio value"
        in question_lower
        or "portfolio value"
        in question_lower
        or "portfolio worth"
        in question_lower
    ):

        current_value = float(
            portfolio_analysis.get(
                "current_value",
                0
            )
        )

        return {
            "question": question,

            "answer": (
                f"Your current portfolio value is "
                f"₹{current_value:,.2f}."
            ),

            "validation_status":
                "passed",

            "validation_errors":
                []
        }

    # =====================================================
    # NUMBER OF STOCKS
    # =====================================================

    if (
        "how many stocks" in question_lower
        or "number of stocks" in question_lower
        or "how many holdings" in question_lower
    ):

        return {
            "question": question,

            "answer": (
                f"You currently own "
                f"{len(holdings)} stocks "
                f"in your portfolio."
            ),

            "validation_status":
                "passed",

            "validation_errors":
                []
        }

    # =====================================================
    # INVESTMENT / BUY / SELL SUGGESTION
    #
    # We do NOT give direct buy/sell instructions.
    # Instead, return evidence-based portfolio
    # review information.
    # =====================================================

    investment_keywords = [

        "investment suggestion",
        "investment advice",
        "investing advice",
        "what should i invest",
        "where should i invest",
        "what should i buy",
        "what stock should i buy",
        "which stock should i buy",
        "should i buy",
        "should i sell",
        "what should i sell",
        "buy or sell",
        "buy this stock",
        "sell this stock",
        "give me investment",
        "suggest an investment",
        "investment recommendation"
    ]

    is_investment_question = any(
        keyword in question_lower
        for keyword in investment_keywords
    )

    if is_investment_question:

        total_invested = float(
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

        overall_return = (
            portfolio_analysis.get(
                "overall_return",
                "0.00%"
            )
        )

        risk_level = (
            portfolio_analysis.get(
                "risk_level",
                "Unknown"
            )
        )

        volatility = float(
            analytics.get(
                "volatility",
                0
            )
        )

        max_drawdown = float(
            analytics.get(
                "max_drawdown",
                0
            )
        )

        concentration = analytics.get(
            "concentration_risk",
            {}
        )

        largest_holding = (
            concentration.get(
                "largest_holding",
                "N/A"
            )
        )

        largest_percentage = float(
            concentration.get(
                "largest_holding_percentage",
                0
            )
        )

        sector_exposure = analytics.get(
            "sector_exposure",
            []
        )

        sector_count = len(
            sector_exposure
        )

        answer = (
            "I can help you review your portfolio "
            "using the available data, but I won't "
            "give a direct buy, sell or hold instruction.\n\n"

            "Here are the current evidence-based "
            "areas to review:\n\n"

            f"• Invested value: "
            f"₹{total_invested:,.2f}\n"

            f"• Current value: "
            f"₹{current_value:,.2f}\n"

            f"• Profit/Loss: "
            f"₹{profit_loss:,.2f}\n"

            f"• Overall return: "
            f"{overall_return}\n"

            f"• Risk level: "
            f"{risk_level}\n"

            f"• Volatility: "
            f"{volatility:.2f}%\n"

            f"• Maximum observed drawdown: "
            f"{max_drawdown:.2f}%\n\n"

            "Portfolio areas to review:\n\n"

            f"• Concentration: "
            f"{largest_holding} represents "
            f"{largest_percentage:.2f}% "
            f"of the portfolio.\n"

            f"• Diversification: "
            f"{len(holdings)} holdings across "
            f"{sector_count} reported sectors.\n"

            "• Performance: The portfolio's "
            "current return and historical risk "
            "metrics warrant review of the "
            "underlying holdings and portfolio "
            "allocation.\n\n"

            "You can also ask me about a specific "
            "holding, its current value, current "
            "price, invested amount or profit/loss."
        )

        return {
            "question": question,

            "answer":
                answer,

            "validation_status":
                "passed",

            "validation_errors":
                []
        }

    # =====================================================
    # GENERAL PORTFOLIO / RISK QUESTIONS
    # =====================================================

    general_portfolio_keywords = [

        "risk",
        "volatility",
        "drawdown",
        "diversification",
        "concentration",
        "allocation",
        "performance",
        "portfolio analysis",
        "portfolio health"
    ]

    if any(
        keyword in question_lower
        for keyword in general_portfolio_keywords
    ):

        total_invested = float(
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

        overall_return = (
            portfolio_analysis.get(
                "overall_return",
                "0.00%"
            )
        )

        risk_level = (
            portfolio_analysis.get(
                "risk_level",
                "Unknown"
            )
        )

        volatility = float(
            analytics.get(
                "volatility",
                0
            )
        )

        max_drawdown = float(
            analytics.get(
                "max_drawdown",
                0
            )
        )

        return {
            "question": question,

            "answer": (
                f"Your portfolio has an invested "
                f"value of ₹{total_invested:,.2f} "
                f"and a current value of "
                f"₹{current_value:,.2f}. "
                f"The current profit/loss is "
                f"₹{profit_loss:,.2f}, with an "
                f"overall return of "
                f"{overall_return}. "
                f"The calculated risk level is "
                f"{risk_level}. "
                f"Portfolio volatility is "
                f"{volatility:.2f}% and the "
                f"maximum observed drawdown is "
                f"{max_drawdown:.2f}%."
            ),

            "validation_status":
                "passed",

            "validation_errors":
                []
        }

    # =====================================================
    # STEP 3
    # COMPLEX QUESTIONS
    # LANGGRAPH / MCP / AI WORKFLOW
    # =====================================================

    try:

        result = run_financial_workflow_sync(

            portfolio_name=
                portfolio_name,

            timeframe=
                timeframe,

            user_id=
                current_user.id,

            user_question=
                question
        )

        return {
            "question": question,

            "answer": result.get(
                "final_answer",
                result.get(
                    "final_report",
                    ""
                )
            ),

            "validation_status": result.get(
                "validation_status",
                "unknown"
            ),

            "validation_errors": result.get(
                "validation_errors",
                []
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"AI Copilot failed: {str(e)}"
            )
        )