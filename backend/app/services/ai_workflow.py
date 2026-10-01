import asyncio
import os
import json
from typing import Any, TypedDict

from langgraph.graph import StateGraph, START, END
from mcp import Client

from app.services.ai_service import AIService


# =========================================================
# MCP CONFIGURATION
# =========================================================

MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "http://127.0.0.1:8100/mcp"
)


# =========================================================
# WORKFLOW STATE
# =========================================================

class FinancialWorkflowState(TypedDict, total=False):

    portfolio_name: str
    timeframe: str

    # Multi-user support
    user_id: int

    # AI Copilot question
    user_question: str

    # MCP data
    portfolio_data: dict[str, Any]
    analytics_data: dict[str, Any]
    market_data: dict[str, Any]
    news_data: list[dict[str, Any]]

    # Grounded context
    grounded_context: dict[str, Any]

    # AI output
    ai_report: str
    final_report: str
    final_answer: str

    # Validation
    validation_status: str
    validation_errors: list[str]


# =========================================================
# SAFE HELPERS
# =========================================================

def _number(value: Any) -> float:

    try:
        return float(value)

    except (TypeError, ValueError):
        return 0.0


def _safe_dict(value: Any) -> dict:

    if isinstance(value, dict):
        return value

    return {}


def _safe_list(value: Any) -> list:

    if isinstance(value, list):
        return value

    return []


# =========================================================
# MCP TOOL CALL
# =========================================================

async def _call_mcp_tool(
    client,
    tool_name: str,
    arguments: dict
):

    result = await client.call_tool(
        tool_name,
        arguments
    )

    # -----------------------------------------------------
    # Structured MCP response
    # -----------------------------------------------------

    structured = getattr(
        result,
        "structured_content",
        None
    )

    if isinstance(
        structured,
        dict
    ):
        return structured

    # -----------------------------------------------------
    # Text MCP response
    # -----------------------------------------------------

    content = getattr(
        result,
        "content",
        None
    )

    if isinstance(
        content,
        list
    ):

        for item in content:

            text = getattr(
                item,
                "text",
                None
            )

            if not text:
                continue

            try:

                parsed = json.loads(
                    text
                )

                if isinstance(
                    parsed,
                    dict
                ):
                    return parsed

            except Exception:
                continue

    return {}


# =========================================================
# FETCH PORTFOLIO
# =========================================================

async def fetch_portfolio(
    state: FinancialWorkflowState
):

    portfolio_name = state.get(
        "portfolio_name",
        "Growth Portfolio"
    )

    user_id = state.get(
        "user_id"
    )

    arguments = {
        "portfolio_name": portfolio_name
    }

    # Multi-user portfolio isolation
    if user_id is not None:

        arguments["user_id"] = user_id

    async with Client(
        MCP_SERVER_URL
    ) as client:

        result = await _call_mcp_tool(
            client,
            "get_portfolio",
            arguments
        )

    return {
        "portfolio_data": result
    }


# =========================================================
# RUN PORTFOLIO ANALYTICS
# =========================================================

async def run_analytics(
    state: FinancialWorkflowState
):

    portfolio_name = state.get(
        "portfolio_name",
        "Growth Portfolio"
    )

    user_id = state.get(
        "user_id"
    )

    arguments = {
        "portfolio_name": portfolio_name
    }

    # Multi-user portfolio isolation
    if user_id is not None:

        arguments["user_id"] = user_id

    async with Client(
        MCP_SERVER_URL
    ) as client:

        result = await _call_mcp_tool(
            client,
            "run_portfolio_analytics",
            arguments
        )

    return {
        "analytics_data": result
    }


# =========================================================
# FETCH MARKET
# =========================================================

async def fetch_market(
    state: FinancialWorkflowState
):

    async with Client(
        MCP_SERVER_URL
    ) as client:

        result = await _call_mcp_tool(
            client,
            "get_market_analysis",
            {
                "symbol": "^NSEI"
            }
        )

    return {
        "market_data": result
    }


# =========================================================
# BUILD GROUNDED CONTEXT
# =========================================================

def build_grounded_context(
    state: FinancialWorkflowState
):

    portfolio_data = _safe_dict(
        state.get(
            "portfolio_data",
            {}
        )
    )

    analytics_data = _safe_dict(
        state.get(
            "analytics_data",
            {}
        )
    )

    market_data = _safe_dict(
        state.get(
            "market_data",
            {}
        )
    )

    news_data = _safe_list(
        state.get(
            "news_data",
            []
        )
    )

    portfolio_name = state.get(
        "portfolio_name",
        "Portfolio"
    )

    user_question = state.get(
        "user_question",
        ""
    )

    # =====================================================
    # BASIC PORTFOLIO VALUES
    # =====================================================

    raw_total_invested = _number(
        portfolio_data.get(
            "total_invested",
            0
        )
    )

    current_value = _number(
        analytics_data.get(
            "current_value",
            0
        )
    )

    profit_loss = _number(
        analytics_data.get(
            "profit_loss",
            0
        )
    )

    # =====================================================
    # IMPORTANT FALLBACK
    #
    # If MCP portfolio data does not provide invested value,
    # reconstruct it from:
    #
    # Current Value - Profit/Loss
    #
    # Example:
    #
    # 59157.50 - (-45342.50)
    # = 104500.00
    # =====================================================

    if raw_total_invested <= 0:

        reconstructed_invested = (
            current_value
            - profit_loss
        )

        if reconstructed_invested > 0:

            total_invested = (
                reconstructed_invested
            )

        else:

            total_invested = 0.0

    else:

        total_invested = (
            raw_total_invested
        )

    # =====================================================
    # ANALYTICS OBJECT
    # =====================================================

    analytics = _safe_dict(
        analytics_data.get(
            "analytics",
            {}
        )
    )

    # =====================================================
    # HOLDING CONTRIBUTION
    #
    # This contains deterministic holding-level P/L.
    # =====================================================

    holding_contribution = _safe_list(
        analytics.get(
            "holding_contribution",
            []
        )
    )

    contribution_map = {}

    for item in holding_contribution:

        if not isinstance(
            item,
            dict
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                ""
            )
        ).strip()

        if not symbol:
            continue

        contribution_map[
            symbol
        ] = _number(
            item.get(
                "profit_loss",
                0
            )
        )

    # =====================================================
    # RAW HOLDINGS
    # =====================================================

    raw_holdings = _safe_list(
        portfolio_data.get(
            "holdings",
            []
        )
    )

    # =====================================================
    # ENRICH HOLDINGS
    #
    # MCP get_portfolio() gives invested_value.
    # Analytics gives holding-level profit/loss.
    #
    # Therefore:
    #
    # current_value =
    # invested_value + profit_loss
    # =====================================================

    enriched_holdings = []

    for holding in raw_holdings:

        if not isinstance(
            holding,
            dict
        ):
            continue

        symbol = str(
            holding.get(
                "symbol",
                ""
            )
        ).strip()

        invested_value = _number(
            holding.get(
                "invested_value",
                0
            )
        )

        holding_profit_loss = (
            contribution_map.get(
                symbol,
                0.0
            )
        )

        holding_current_value = (
            invested_value
            +
            holding_profit_loss
        )

        enriched_holding = dict(
            holding
        )

        enriched_holding[
            "invested_value"
        ] = round(
            invested_value,
            2
        )

        enriched_holding[
            "profit_loss"
        ] = round(
            holding_profit_loss,
            2
        )

        enriched_holding[
            "current_value"
        ] = round(
            holding_current_value,
            2
        )

        # -------------------------------------------------
        # Current price
        # -------------------------------------------------

        quantity = _number(
            holding.get(
                "quantity",
                0
            )
        )

        if quantity > 0:

            current_price = (
                holding_current_value
                /
                quantity
            )

        else:

            current_price = _number(
                holding.get(
                    "buy_price",
                    0
                )
            )

        enriched_holding[
            "current_price"
        ] = round(
            current_price,
            2
        )

        enriched_holdings.append(
            enriched_holding
        )

    # =====================================================
    # OVERALL RETURN
    # =====================================================

    if total_invested > 0:

        return_percentage = (
            profit_loss
            /
            total_invested
            *
            100
        )

    else:

        return_percentage = 0.0

    # =====================================================
    # PORTFOLIO ANALYSIS OBJECT
    # =====================================================

    portfolio_analysis = {

        "portfolio_name":
            portfolio_data.get(
                "portfolio_name",
                portfolio_name
            ),

        "total_value":
            round(
                total_invested,
                2
            ),

        "total_invested":
            round(
                total_invested,
                2
            ),

        "current_value":
            round(
                current_value,
                2
            ),

        "profit_loss":
            round(
                profit_loss,
                2
            ),

        "overall_return":
            f"{return_percentage:+.2f}%",

        "risk_level":
            analytics.get(
                "risk_level",
                "Unknown"
            ),

        "holdings":
            enriched_holdings,

        "analytics":
            analytics
    }

    # =====================================================
    # GROUNDED CONTEXT
    # =====================================================

    context = {

        "user_id":
            state.get(
                "user_id"
            ),

        "user_question":
            user_question,

        "portfolio":
            portfolio_data,

        "portfolio_analysis":
            portfolio_analysis,

        "analytics":
            analytics_data,

        "market":
            market_data,

        "news":
            news_data
    }

    return {
        "grounded_context": context
    }


# =========================================================
# GENERATE AI REPORT
# =========================================================

def generate_ai_report(
    state: FinancialWorkflowState
):

    context = _safe_dict(
        state.get(
            "grounded_context",
            {}
        )
    )

    portfolio_analysis = _safe_dict(
        context.get(
            "portfolio_analysis",
            {}
        )
    )

    market_data = _safe_dict(
        context.get(
            "market",
            {}
        )
    )

    news_data = _safe_list(
        context.get(
            "news",
            []
        )
    )

    user_question = state.get(
        "user_question",
        ""
    )

    # =====================================================
    # COPILOT QUESTION
    # =====================================================

    if user_question:

        portfolio_analysis = dict(
            portfolio_analysis
        )

        portfolio_analysis[
            "user_question"
        ] = user_question

    # =====================================================
    # AI SERVICE
    # =====================================================

    ai_service = AIService()

    report = (
        ai_service
        .generate_financial_intelligence(
            market_analysis=
                market_data.get(
                    "data",
                    market_data
                ),

            portfolio_analysis=
                portfolio_analysis,

            news=
                news_data
        )
    )

    return {

        "ai_report":
            report,

        "final_answer":
            report
    }


# =========================================================
# DETERMINISTIC FALLBACK REPORT
# =========================================================

def build_safe_fallback_report(
    state: FinancialWorkflowState
):

    portfolio_data = _safe_dict(
        state.get(
            "portfolio_data",
            {}
        )
    )

    analytics_data = _safe_dict(
        state.get(
            "analytics_data",
            {}
        )
    )

    market_data = _safe_dict(
        state.get(
            "market_data",
            {}
        )
    )

    news_data = _safe_list(
        state.get(
            "news_data",
            []
        )
    )

    analytics = _safe_dict(
        analytics_data.get(
            "analytics",
            {}
        )
    )

    market = _safe_dict(
        market_data.get(
            "data",
            market_data
        )
    )

    portfolio_name = state.get(
        "portfolio_name",
        "Portfolio"
    )

    # =====================================================
    # INVESTED VALUE
    # =====================================================

    raw_invested = _number(
        portfolio_data.get(
            "total_invested",
            0
        )
    )

    current_value = _number(
        analytics_data.get(
            "current_value",
            0
        )
    )

    profit_loss = _number(
        analytics_data.get(
            "profit_loss",
            0
        )
    )

    if raw_invested > 0:

        invested = raw_invested

    else:

        reconstructed_invested = (
            current_value
            - profit_loss
        )

        invested = (
            reconstructed_invested
            if reconstructed_invested > 0
            else 0.0
        )

    # =====================================================
    # RETURN
    # =====================================================

    if invested > 0:

        overall_return = (
            profit_loss
            /
            invested
            *
            100
        )

    else:

        overall_return = 0.0

    # =====================================================
    # OTHER ANALYTICS
    # =====================================================

    risk_level = analytics.get(
        "risk_level",
        "Unknown"
    )

    market_signal = market.get(
        "overall_signal",
        "Unknown"
    )

    daily_return = _number(
        market.get(
            "daily_return",
            0
        )
    )

    volatility = _number(
        analytics.get(
            "volatility",
            0
        )
    )

    drawdown = _number(
        analytics.get(
            "max_drawdown",
            0
        )
    )

    holdings = _safe_list(
        portfolio_data.get(
            "holdings",
            []
        )
    )

    allocation = _safe_list(
        analytics.get(
            "allocation",
            []
        )
    )

    sector_exposure = _safe_list(
        analytics.get(
            "sector_exposure",
            []
        )
    )

    # =====================================================
    # HOLDING CONTRIBUTION
    # =====================================================

    holding_contribution = _safe_list(
        analytics.get(
            "holding_contribution",
            []
        )
    )

    contribution_map = {}

    for item in holding_contribution:

        if not isinstance(
            item,
            dict
        ):
            continue

        symbol = str(
            item.get(
                "symbol",
                ""
            )
        ).strip()

        contribution_map[
            symbol
        ] = _number(
            item.get(
                "profit_loss",
                0
            )
        )

    # =====================================================
    # HOLDING SUMMARY
    # =====================================================

    holding_lines = []

    for holding in holdings:

        if not isinstance(
            holding,
            dict
        ):
            continue

        symbol = holding.get(
            "symbol",
            "Unknown"
        )

        invested_value = _number(
            holding.get(
                "invested_value",
                0
            )
        )

        holding_profit_loss = (
            contribution_map.get(
                str(symbol),
                0.0
            )
        )

        holding_current_value = (
            invested_value
            +
            holding_profit_loss
        )

        status = (
            "Gain"
            if holding_profit_loss > 0
            else "Loss"
            if holding_profit_loss < 0
            else "Flat"
        )

        holding_lines.append(
            f"- {symbol}: "
            f"Current Value ₹"
            f"{holding_current_value:,.2f}, "
            f"Profit/Loss ₹"
            f"{holding_profit_loss:,.2f}, "
            f"Status: {status}"
        )

    if not holding_lines:

        holding_lines.append(
            "- No holding-level data available."
        )

    holding_text = "\n".join(
        holding_lines
    )

    # =====================================================
    # NEWS SENTIMENT
    # =====================================================

    news_count = len(
        news_data
    )

    positive_news = 0
    negative_news = 0
    neutral_news = 0

    for article in news_data:

        if not isinstance(
            article,
            dict
        ):
            continue

        sentiment = str(
            article.get(
                "sentiment",
                "Neutral"
            )
        ).lower()

        if sentiment == "positive":

            positive_news += 1

        elif sentiment == "negative":

            negative_news += 1

        else:

            neutral_news += 1

    if positive_news > negative_news:

        news_sentiment = "Positive"

    elif negative_news > positive_news:

        news_sentiment = "Negative"

    else:

        news_sentiment = "Neutral"

    # =====================================================
    # SAFE REPORT
    # =====================================================

    return f"""
Financial Intelligence Report

1. Current Market Condition

The supplied market signal is {market_signal}. The supplied daily return is {daily_return:.2f}% and market data should be interpreted only from the available indicators.

2. Portfolio Performance

The {portfolio_name} has an invested value of ₹{invested:,.2f}, a current value of ₹{current_value:,.2f}, and a profit/loss of ₹{profit_loss:,.2f}. The calculated overall return is {overall_return:+.2f}%.

3. Relationship Between Market and Portfolio

The supplied data is not sufficient to establish a direct relationship between market conditions and portfolio performance.

4. Important Financial News Themes

The supplied news data contains {news_count} articles. Overall supplied news sentiment is {news_sentiment}, with {positive_news} positive, {negative_news} negative and {neutral_news} neutral items.

5. Key Risks or Areas to Monitor

The supplied portfolio risk level is {risk_level}. Portfolio volatility is {volatility:.2f}% and maximum observed drawdown is {drawdown:.2f}%. Review the supplied allocation, concentration, sector exposure and holding-level results.

Holding-level observations:

{holding_text}

Reported holdings: {len(holdings)}.
Reported allocation entries: {len(allocation)}.
Reported sector entries: {len(sector_exposure)}.
""".strip()


# =========================================================
# VALIDATION
# =========================================================

def validate_ai_report(
    state: FinancialWorkflowState
):

    report = str(
        state.get(
            "ai_report",
            ""
        )
    )

    normalized = (
        report
        .replace(
            "**",
            ""
        )
        .strip()
    )

    errors = []

    user_question = str(
        state.get(
            "user_question",
            ""
        )
    ).strip()

    # =====================================================
    # COPILOT VALIDATION
    # =====================================================

    if user_question:

        if not normalized:

            errors.append(
                "AI Copilot returned an empty response."
            )

        # -------------------------------------------------
        # DIRECT INVESTMENT ADVICE
        # -------------------------------------------------

        direct_advice_patterns = [

            "buy this stock",
            "buy the stock",
            "you should buy",
            "recommend buying",
            "recommended to buy",

            "sell this stock",
            "sell the stock",
            "you should sell",
            "recommend selling",
            "recommended to sell",

            "strong buy",
            "strong sell",

            "invest in this stock",
            "invest in this share",

            "purchase this stock",
            "purchase this share"
        ]

        for phrase in direct_advice_patterns:

            if phrase in normalized.lower():

                errors.append(
                    "Direct investment advice detected: "
                    f"'{phrase}'"
                )

        # -------------------------------------------------
        # MARKET / PORTFOLIO RELATIONSHIP
        # -------------------------------------------------

        forbidden_relationships = [

            "market caused the portfolio",
            "market movements caused the portfolio",
            "market conditions caused the portfolio",
            "portfolio declined because of the market",
            "portfolio increased because of the market",
            "portfolio performance was driven by market movements",
            "portfolio is sensitive to market movements",
            "portfolio was sensitive to market movements",
            "portfolio shows sensitivity to market movements",
            "portfolio has sensitivity to market movements",
            "market movements drove portfolio performance",
            "market movements drove the portfolio",
            "market conditions drove portfolio performance"
        ]

        for phrase in forbidden_relationships:

            if phrase in normalized.lower():

                errors.append(
                    "Unsupported market / portfolio "
                    "relationship detected: "
                    f"'{phrase}'"
                )

        # -------------------------------------------------
        # CORRELATION
        # -------------------------------------------------

        correlation_patterns = [

            "portfolio is correlated with the market",
            "portfolio is highly correlated with the market",
            "portfolio has a strong correlation with the market",
            "portfolio has a positive correlation with the market",
            "portfolio has a negative correlation with the market",
            "portfolio correlates with the market"
        ]

        for phrase in correlation_patterns:

            if phrase in normalized.lower():

                errors.append(
                    "Unsupported correlation claim detected: "
                    f"'{phrase}'"
                )

        # -------------------------------------------------
        # UNSUPPORTED CERTAINTY
        # -------------------------------------------------

        unsupported_certainty = [

            "guaranteed profit",
            "guaranteed return",
            "risk-free return",
            "risk free return",
            "certain profit",
            "will definitely increase",
            "will definitely rise",
            "will definitely fall",
            "will definitely decline"
        ]

        for phrase in unsupported_certainty:

            if phrase in normalized.lower():

                errors.append(
                    "Unsupported certainty detected: "
                    f"'{phrase}'"
                )

        if errors:

            return {
                "validation_status": "failed",
                "validation_errors": errors
            }

        return {
            "validation_status": "passed",
            "validation_errors": []
        }

    # =====================================================
    # NORMAL FINANCIAL REPORT VALIDATION
    # =====================================================

    required_sections = [

        "1. Current Market Condition",

        "2. Portfolio Performance",

        "3. Relationship Between Market and Portfolio",

        "4. Important Financial News Themes",

        "5. Key Risks or Areas to Monitor"
    ]

    for section in required_sections:

        if section.lower() not in normalized.lower():

            errors.append(
                f"Missing required section: {section}"
            )

    # -----------------------------------------------------
    # DIRECT INVESTMENT ADVICE
    # -----------------------------------------------------

    direct_advice_patterns = [

        "buy this stock",
        "buy the stock",
        "you should buy",
        "recommend buying",
        "recommended to buy",

        "sell this stock",
        "sell the stock",
        "you should sell",
        "recommend selling",
        "recommended to sell",

        "strong buy",
        "strong sell",

        "invest in this stock",
        "invest in this share",

        "purchase this stock",
        "purchase this share"
    ]

    for phrase in direct_advice_patterns:

        if phrase in normalized.lower():

            errors.append(
                "Direct investment advice detected: "
                f"'{phrase}'"
            )

    # -----------------------------------------------------
    # MARKET / PORTFOLIO RELATIONSHIP
    # -----------------------------------------------------

    forbidden_relationships = [

        "market caused the portfolio",
        "market movements caused the portfolio",
        "market conditions caused the portfolio",
        "portfolio declined because of the market",
        "portfolio increased because of the market",
        "portfolio performance was driven by market movements",
        "portfolio is sensitive to market movements",
        "portfolio was sensitive to market movements",
        "portfolio shows sensitivity to market movements",
        "portfolio has sensitivity to market movements",
        "indicating sensitivity to market movements",
        "some sensitivity to market movements",
        "sensitivity to market movements",
        "market movements drove portfolio performance",
        "market movements drove the portfolio",
        "market conditions drove portfolio performance"
    ]

    for phrase in forbidden_relationships:

        if phrase in normalized.lower():

            errors.append(
                "Unsupported market / portfolio "
                "relationship detected: "
                f"'{phrase}'"
            )

    # -----------------------------------------------------
    # CORRELATION
    # -----------------------------------------------------

    correlation_patterns = [

        "portfolio is correlated with the market",
        "portfolio is highly correlated with the market",
        "portfolio has a strong correlation with the market",
        "portfolio has a positive correlation with the market",
        "portfolio has a negative correlation with the market",
        "portfolio correlates with the market"
    ]

    for phrase in correlation_patterns:

        if phrase in normalized.lower():

            errors.append(
                "Unsupported correlation claim detected: "
                f"'{phrase}'"
            )

    # -----------------------------------------------------
    # UNSUPPORTED CERTAINTY
    # -----------------------------------------------------

    unsupported_certainty = [

        "guaranteed profit",
        "guaranteed return",
        "risk-free return",
        "risk free return",
        "certain profit",
        "will definitely increase",
        "will definitely rise",
        "will definitely fall",
        "will definitely decline"
    ]

    for phrase in unsupported_certainty:

        if phrase in normalized.lower():

            errors.append(
                "Unsupported certainty detected: "
                f"'{phrase}'"
            )

    if errors:

        return {
            "validation_status": "failed",
            "validation_errors": errors
        }

    return {
        "validation_status": "passed",
        "validation_errors": []
    }


# =========================================================
# VALIDATION NODE
# =========================================================

def validate_report_node(
    state: FinancialWorkflowState
):

    validation = validate_ai_report(
        state
    )

    # =====================================================
    # VALIDATION PASSED
    # =====================================================

    if validation[
        "validation_status"
    ] == "passed":

        final_report = state.get(
            "ai_report",
            ""
        )

        return {

            "validation_status":
                "passed",

            "validation_errors":
                [],

            "final_report":
                final_report,

            "final_answer":
                final_report
        }

    # =====================================================
    # COPILOT VALIDATION FAILED
    # =====================================================

    if state.get(
        "user_question",
        ""
    ).strip():

        return {

            "validation_status":
                "failed",

            "validation_errors":
                validation[
                    "validation_errors"
                ],

            "final_report":
                state.get(
                    "ai_report",
                    ""
                ),

            "final_answer":
                state.get(
                    "ai_report",
                    ""
                )
        }

    # =====================================================
    # NORMAL REPORT FALLBACK
    # =====================================================

    fallback_report = (
        build_safe_fallback_report(
            state
        )
    )

    fallback_state = dict(
        state
    )

    fallback_state[
        "ai_report"
    ] = fallback_report

    fallback_validation = (
        validate_ai_report(
            fallback_state
        )
    )

    if fallback_validation[
        "validation_status"
    ] == "passed":

        return {

            "validation_status":
                "passed",

            "validation_errors":
                [],

            "final_report":
                fallback_report,

            "final_answer":
                fallback_report
        }

    return {

        "validation_status":
            "failed",

        "validation_errors":
            (
                validation[
                    "validation_errors"
                ]
                +
                fallback_validation[
                    "validation_errors"
                ]
            ),

        "final_report":
            fallback_report,

        "final_answer":
            fallback_report
    }


# =========================================================
# BUILD GRAPH
# =========================================================

def build_workflow():

    workflow = StateGraph(
        FinancialWorkflowState
    )

    workflow.add_node(
        "fetch_portfolio",
        fetch_portfolio
    )

    workflow.add_node(
        "run_analytics",
        run_analytics
    )

    workflow.add_node(
        "fetch_market",
        fetch_market
    )

    workflow.add_node(
        "build_grounded_context",
        build_grounded_context
    )

    workflow.add_node(
        "generate_ai_report",
        generate_ai_report
    )

    workflow.add_node(
        "validate_report",
        validate_report_node
    )

    workflow.add_edge(
        START,
        "fetch_portfolio"
    )

    workflow.add_edge(
        "fetch_portfolio",
        "run_analytics"
    )

    workflow.add_edge(
        "run_analytics",
        "fetch_market"
    )

    workflow.add_edge(
        "fetch_market",
        "build_grounded_context"
    )

    workflow.add_edge(
        "build_grounded_context",
        "generate_ai_report"
    )

    workflow.add_edge(
        "generate_ai_report",
        "validate_report"
    )

    workflow.add_edge(
        "validate_report",
        END
    )

    return workflow.compile()


# =========================================================
# ASYNC WORKFLOW
# =========================================================

async def run_financial_workflow(
    portfolio_name="Growth Portfolio",
    timeframe="1Y",
    news_data=None,
    user_id=None,
    user_question=None
):

    graph = build_workflow()

    initial_state = {

        "portfolio_name":
            portfolio_name,

        "timeframe":
            timeframe,

        "user_id":
            user_id,

        "user_question":
            user_question or "",

        "news_data":
            news_data or [],

        "portfolio_data":
            {},

        "analytics_data":
            {},

        "market_data":
            {},

        "grounded_context":
            {},

        "ai_report":
            "",

        "final_report":
            "",

        "final_answer":
            "",

        "validation_status":
            "unknown",

        "validation_errors":
            []
    }

    result = await graph.ainvoke(
        initial_state
    )

    return result


# =========================================================
# SYNC WORKFLOW
# =========================================================

def run_financial_workflow_sync(
    portfolio_name="Growth Portfolio",
    timeframe="1Y",
    news_data=None,
    user_id=None,
    user_question=None
):

    return asyncio.run(
        run_financial_workflow(
            portfolio_name=
                portfolio_name,

            timeframe=
                timeframe,

            news_data=
                news_data,

            user_id=
                user_id,

            user_question=
                user_question
        )
    )