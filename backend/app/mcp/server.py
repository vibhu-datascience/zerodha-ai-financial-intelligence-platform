import os
from typing import Any

from mcp.server import MCPServer

from app.database.database import Base, engine, SessionLocal
from app.database.models import Portfolio, Holding
from app.services.market_service import MarketService
from app.services.portfolio_service import PortfolioService


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

Base.metadata.create_all(bind=engine)


def initialize_database():
    db = SessionLocal()

    try:
        # Prevent duplicate seed data
        if db.query(Portfolio).count() > 0:
            print("MCP database already contains portfolio data.")
            return

        # -------------------------------------------------
        # Growth Portfolio
        # -------------------------------------------------

        growth = Portfolio(
            name="Growth Portfolio"
        )

        growth.holdings = [
            Holding(
                symbol="RELIANCE.NS",
                quantity=20,
                buy_price=2500,
                sector="Energy"
            ),
            Holding(
                symbol="TCS.NS",
                quantity=10,
                buy_price=3200,
                sector="Information Technology"
            ),
            Holding(
                symbol="INFY.NS",
                quantity=15,
                buy_price=1500,
                sector="Information Technology"
            )
        ]

        # -------------------------------------------------
        # Balanced Portfolio
        # -------------------------------------------------

        balanced = Portfolio(
            name="Balanced Portfolio"
        )

        balanced.holdings = [
            Holding(
                symbol="HDFCBANK.NS",
                quantity=20,
                buy_price=1600,
                sector="Financial Services"
            ),
            Holding(
                symbol="ITC.NS",
                quantity=30,
                buy_price=450,
                sector="Consumer Staples"
            ),
            Holding(
                symbol="TCS.NS",
                quantity=10,
                buy_price=3200,
                sector="Information Technology"
            )
        ]

        # -------------------------------------------------
        # Conservative Portfolio
        # -------------------------------------------------

        conservative = Portfolio(
            name="Conservative Portfolio"
        )

        conservative.holdings = [
            Holding(
                symbol="ITC.NS",
                quantity=40,
                buy_price=450,
                sector="Consumer Staples"
            ),
            Holding(
                symbol="HDFCBANK.NS",
                quantity=15,
                buy_price=1600,
                sector="Financial Services"
            )
        ]

        db.add_all([
            growth,
            balanced,
            conservative
        ])

        db.commit()

        print("MCP database initialized successfully.")

    except Exception as e:
        db.rollback()
        print("MCP database initialization error:", e)

    finally:
        db.close()


# Initialize database when MCP server starts
initialize_database()


# =========================================================
# MCP SERVER
# =========================================================

mcp = MCPServer(
    "Zerodha AI Financial Intelligence MCP"
)


# =========================================================
# TOOL 1 — PORTFOLIO DATA
# =========================================================

@mcp.tool()
def get_portfolio(
    portfolio_name: str = "Growth Portfolio"
) -> dict[str, Any]:

    db = SessionLocal()

    try:
        portfolio = (
            db.query(Portfolio)
            .filter(Portfolio.name == portfolio_name)
            .first()
        )

        if not portfolio:
            return {
                "status": "error",
                "message": f"Portfolio '{portfolio_name}' not found."
            }

        holdings = []
        total_invested = 0.0

        for holding in portfolio.holdings:

            invested_value = (
                float(holding.quantity)
                * float(holding.buy_price)
            )

            total_invested += invested_value

            holdings.append({
                "symbol": holding.symbol,
                "quantity": float(holding.quantity),
                "buy_price": round(
                    float(holding.buy_price),
                    2
                ),
                "invested_value": round(
                    invested_value,
                    2
                ),
                "sector": holding.sector
            })

        return {
            "status": "success",
            "portfolio_name": portfolio.name,
            "total_invested": round(
                total_invested,
                2
            ),
            "holdings": holdings
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        db.close()


# =========================================================
# TOOL 2 — MARKET ANALYSIS
# =========================================================

@mcp.tool()
def get_market_analysis(
    symbol: str = "^NSEI"
) -> dict[str, Any]:

    try:

        market_service = MarketService()

        result = market_service.get_market_analysis(
            symbol=symbol
        )

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# TOOL 3 — COMPLETE PORTFOLIO ANALYSIS
# =========================================================

@mcp.tool()
def analyze_portfolio(
    portfolio_name: str = "Growth Portfolio",
    timeframe: str = "1Y"
) -> dict[str, Any]:

    db = SessionLocal()

    try:

        portfolio_service = PortfolioService(db)

        result = portfolio_service.analyze_portfolio(
            portfolio_name=portfolio_name,
            timeframe=timeframe
        )

        return {
            "status": "success",
            "portfolio_name": portfolio_name,
            "timeframe": timeframe,
            "analysis": result
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        db.close()


# =========================================================
# TOOL 4 — PORTFOLIO ANALYTICS ONLY
# =========================================================

@mcp.tool()
def run_portfolio_analytics(
    portfolio_name: str = "Growth Portfolio"
) -> dict[str, Any]:

    db = SessionLocal()

    try:

        portfolio_service = PortfolioService(db)

        portfolio = (
            db.query(Portfolio)
            .filter(
                Portfolio.name == portfolio_name
            )
            .first()
        )

        if not portfolio:
            return {
                "status": "error",
                "message": f"Portfolio '{portfolio_name}' not found."
            }

        holdings_data = []
        current_value = 0.0

        for holding in portfolio.holdings:

            current_price = (
                portfolio_service.market_service
                .get_current_price(
                    holding.symbol
                )
            )

            if current_price is None:
                current_price = float(
                    holding.buy_price
                )

            invested_value = (
                float(holding.quantity)
                * float(holding.buy_price)
            )

            holding_current_value = (
                float(holding.quantity)
                * float(current_price)
            )

            profit_loss = (
                holding_current_value
                - invested_value
            )

            current_value += holding_current_value

            holdings_data.append({
                "symbol": holding.symbol,
                "quantity": float(
                    holding.quantity
                ),
                "buy_price": round(
                    float(holding.buy_price),
                    2
                ),
                "current_price": round(
                    float(current_price),
                    2
                ),
                "invested_value": round(
                    invested_value,
                    2
                ),
                "current_value": round(
                    holding_current_value,
                    2
                ),
                "profit_loss": round(
                    profit_loss,
                    2
                ),
                "sector": holding.sector
            })

        total_invested = sum(
            holding["invested_value"]
            for holding in holdings_data
        )

        total_profit_loss = (
            current_value
            - total_invested
        )

        analytics = (
            portfolio_service
            .analytics_service
            .run_portfolio_analytics(
                holdings_data=holdings_data,
                current_value=current_value,
                total_profit_loss=total_profit_loss
            )
        )

        return {
            "status": "success",
            "portfolio_name": portfolio_name,
            "current_value": round(
                current_value,
                2
            ),
            "profit_loss": round(
                total_profit_loss,
                2
            ),
            "analytics": analytics
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        db.close()


# =========================================================
# SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "8100"
        )
    )

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        json_response=True
    )