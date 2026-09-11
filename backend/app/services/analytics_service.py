import yfinance as yf
import pandas as pd
import numpy as np


class AnalyticsService:

    # ---------------------------------------------------------
    # 1. HISTORICAL DATA
    # ---------------------------------------------------------

    def get_historical_data(self, symbol, period="1y"):
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period)

            if history.empty:
                return pd.DataFrame()

            return history

        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    # ---------------------------------------------------------
    # 2. PORTFOLIO ALLOCATION
    # ---------------------------------------------------------

    def calculate_allocation(self, holdings_data, current_value):
        allocation = []

        if current_value <= 0:
            return allocation

        for holding in holdings_data:
            holding_value = holding["current_value"]

            percentage = (holding_value / current_value) * 100

            allocation.append({
                "symbol": holding["symbol"],
                "value": round(float(holding_value), 2),
                "percentage": round(float(percentage), 2)
            })

        return allocation

    # ---------------------------------------------------------
    # 3. CONCENTRATION RISK
    # ---------------------------------------------------------

    def calculate_concentration_risk(self, allocation):
        if not allocation:
            return {
                "largest_holding": None,
                "largest_holding_percentage": 0,
                "concentration_level": "Unknown"
            }

        largest = max(
            allocation,
            key=lambda x: x["percentage"]
        )

        largest_percentage = largest["percentage"]

        if largest_percentage >= 50:
            concentration_level = "High"
        elif largest_percentage >= 30:
            concentration_level = "Moderate"
        else:
            concentration_level = "Low"

        return {
            "largest_holding": largest["symbol"],
            "largest_holding_percentage": round(
                float(largest_percentage), 2
            ),
            "concentration_level": concentration_level
        }

    # ---------------------------------------------------------
    # 4. HOLDING CONTRIBUTION
    # ---------------------------------------------------------

    def calculate_holding_contribution(
        self,
        holdings_data,
        total_profit_loss
    ):
        contributions = []

        for holding in holdings_data:

            holding_profit_loss = holding["profit_loss"]

            if total_profit_loss != 0:
                contribution_percentage = (
                    holding_profit_loss / abs(total_profit_loss)
                ) * 100
            else:
                contribution_percentage = 0

            contributions.append({
                "symbol": holding["symbol"],
                "profit_loss": round(
                    float(holding_profit_loss), 2
                ),
                "contribution_percentage": round(
                    float(contribution_percentage), 2
                )
            })

        return contributions

    # ---------------------------------------------------------
    # 5. SECTOR EXPOSURE
    # ---------------------------------------------------------

    def calculate_sector_exposure(
        self,
        holdings_data,
        current_value
    ):
        sector_totals = {}

        if current_value <= 0:
            return []

        for holding in holdings_data:

            sector = holding.get("sector") or "Unknown"

            holding_value = holding["current_value"]

            sector_totals[sector] = (
                sector_totals.get(sector, 0)
                + holding_value
            )

        sector_exposure = []

        for sector, value in sector_totals.items():

            percentage = (
                value / current_value
            ) * 100

            sector_exposure.append({
                "sector": sector,
                "value": round(float(value), 2),
                "percentage": round(
                    float(percentage), 2
                )
            })

        sector_exposure.sort(
            key=lambda x: x["percentage"],
            reverse=True
        )

        return sector_exposure

    # ---------------------------------------------------------
    # 6. PORTFOLIO VOLATILITY
    # ---------------------------------------------------------

    def calculate_portfolio_volatility(
        self,
        holdings_data
    ):
        weighted_returns = []

        total_value = sum(
            holding["current_value"]
            for holding in holdings_data
        )

        if total_value <= 0:
            return 0

        for holding in holdings_data:

            symbol = holding["symbol"]

            history = self.get_historical_data(
                symbol,
                period="1y"
            )

            if history.empty or len(history) < 30:
                continue

            daily_returns = (
                history["Close"]
                .pct_change()
                .dropna()
            )

            if daily_returns.empty:
                continue

            volatility = (
                daily_returns.std()
                * np.sqrt(252)
                * 100
            )

            weight = (
                holding["current_value"]
                / total_value
            )

            weighted_returns.append(
                volatility * weight
            )

        if not weighted_returns:
            return 0

        portfolio_volatility = sum(
            weighted_returns
        )

        return round(
            float(portfolio_volatility),
            2
        )

    # ---------------------------------------------------------
    # 7. MAXIMUM DRAWDOWN
    # ---------------------------------------------------------

    def calculate_portfolio_drawdown(
        self,
        holdings_data
    ):
        weighted_returns = []

        total_value = sum(
            holding["current_value"]
            for holding in holdings_data
        )

        if total_value <= 0:
            return 0

        for holding in holdings_data:

            symbol = holding["symbol"]

            history = self.get_historical_data(
                symbol,
                period="1y"
            )

            if history.empty or len(history) < 30:
                continue

            daily_returns = (
                history["Close"]
                .pct_change()
                .fillna(0)
            )

            weight = (
                holding["current_value"]
                / total_value
            )

            weighted_returns.append(
                daily_returns * weight
            )

        if not weighted_returns:
            return 0

        portfolio_returns = pd.concat(
            weighted_returns,
            axis=1
        ).sum(axis=1)

        cumulative_returns = (
            1 + portfolio_returns
        ).cumprod()

        running_max = (
            cumulative_returns
            .cummax()
        )

        drawdown = (
            cumulative_returns
            / running_max
            - 1
        )

        max_drawdown = (
            drawdown.min() * 100
        )

        return round(
            float(max_drawdown),
            2
        )

    # ---------------------------------------------------------
    # 8. RISK LEVEL
    # ---------------------------------------------------------

    def calculate_risk_level(
        self,
        volatility,
        max_drawdown,
        concentration_percentage
    ):
        risk_score = 0

        # Volatility component
        if volatility >= 30:
            risk_score += 2
        elif volatility >= 20:
            risk_score += 1

        # Drawdown component
        if max_drawdown <= -30:
            risk_score += 2
        elif max_drawdown <= -15:
            risk_score += 1

        # Concentration component
        if concentration_percentage >= 50:
            risk_score += 2
        elif concentration_percentage >= 30:
            risk_score += 1

        if risk_score >= 5:
            return "High"

        elif risk_score >= 2:
            return "Moderate"

        return "Low"

    # ---------------------------------------------------------
    # 9. COMPLETE PORTFOLIO ANALYTICS
    # ---------------------------------------------------------

    def run_portfolio_analytics(
        self,
        holdings_data,
        current_value,
        total_profit_loss
    ):

        # Allocation
        allocation = self.calculate_allocation(
            holdings_data,
            current_value
        )

        # Concentration
        concentration = (
            self.calculate_concentration_risk(
                allocation
            )
        )

        # Holding contribution
        holding_contribution = (
            self.calculate_holding_contribution(
                holdings_data,
                total_profit_loss
            )
        )

        # Sector exposure
        sector_exposure = (
            self.calculate_sector_exposure(
                holdings_data,
                current_value
            )
        )

        # Volatility
        volatility = (
            self.calculate_portfolio_volatility(
                holdings_data
            )
        )

        # Drawdown
        max_drawdown = (
            self.calculate_portfolio_drawdown(
                holdings_data
            )
        )

        # Risk
        risk_level = self.calculate_risk_level(
            volatility=volatility,
            max_drawdown=max_drawdown,
            concentration_percentage=concentration[
                "largest_holding_percentage"
            ]
        )

        return {
            "allocation": allocation,

            "concentration_risk": concentration,

            "holding_contribution": holding_contribution,

            "sector_exposure": sector_exposure,

            "volatility": volatility,

            "max_drawdown": max_drawdown,

            "risk_level": risk_level
        }