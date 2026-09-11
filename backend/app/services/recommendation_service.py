from datetime import datetime, timezone


class RecommendationService:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.source = "Deterministic Portfolio Analytics"

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
    # CONFIDENCE
    # =====================================================

    def _confidence(self, value):

        value = self._number(value)

        return round(
            max(
                0.0,
                min(
                    1.0,
                    value
                )
            ),
            2
        )

    # =====================================================
    # CREATE CARD
    # =====================================================

    def _create_card(
        self,
        recommendation_type,
        category,
        title,
        severity,
        rationale,
        supporting_metrics,
        suggested_action,
        confidence
    ):

        return {

            "type":
                recommendation_type,

            "category":
                category,

            "title":
                title,

            "severity":
                severity,

            "rationale":
                rationale,

            "supporting_metrics":
                supporting_metrics,

            "source":
                self.source,

            "freshness":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "confidence":
                self._confidence(
                    confidence
                ),

            "suggested_action":
                suggested_action
        }

    # =====================================================
    # CONCENTRATION RECOMMENDATION
    # =====================================================

    def _concentration_card(
        self,
        concentration
    ):

        if not isinstance(
            concentration,
            dict
        ):

            return None

        symbol = concentration.get(
            "largest_holding"
        )

        percentage = self._number(
            concentration.get(
                "largest_holding_percentage",
                0
            )
        )

        level = concentration.get(
            "concentration_level",
            "Unknown"
        )

        if not symbol or percentage <= 0:

            return None

        if percentage >= 50:

            severity = "HIGH"
            confidence = 0.98

        elif percentage >= 30:

            severity = "MODERATE"
            confidence = 0.94

        else:

            return None

        return self._create_card(

            recommendation_type=
                "DIVERSIFICATION_REVIEW",

            category=
                "CONCENTRATION",

            title=
                "Portfolio Concentration Review",

            severity=
                severity,

            rationale=(
                f"{symbol} represents "
                f"{percentage:.2f}% of portfolio "
                "value, making it the largest "
                "portfolio holding."
            ),

            supporting_metrics={

                "symbol":
                    symbol,

                "allocation_percentage":
                    round(
                        percentage,
                        2
                    ),

                "concentration_level":
                    level
            },

            suggested_action=(
                "Review whether the current "
                "holding concentration is "
                "consistent with the intended "
                "portfolio allocation."
            ),

            confidence=
                confidence
        )

    # =====================================================
    # VOLATILITY RECOMMENDATION
    # =====================================================

    def _volatility_card(
        self,
        volatility
    ):

        volatility = self._number(
            volatility
        )

        if volatility >= 30:

            severity = "HIGH"
            confidence = 0.96

        elif volatility >= 20:

            severity = "MODERATE"
            confidence = 0.91

        else:

            return None

        return self._create_card(

            recommendation_type=
                "RISK_ALERT",

            category=
                "VOLATILITY",

            title=
                "Portfolio Volatility Review",

            severity=
                severity,

            rationale=(
                f"Portfolio volatility is "
                f"{volatility:.2f}% based on the "
                "supplied historical data."
            ),

            supporting_metrics={

                "volatility":
                    round(
                        volatility,
                        2
                    )
            },

            suggested_action=(
                "Review portfolio volatility "
                "against the intended risk "
                "profile."
            ),

            confidence=
                confidence
        )

    # =====================================================
    # DRAWDOWN RECOMMENDATION
    # =====================================================

    def _drawdown_card(
        self,
        max_drawdown
    ):

        max_drawdown = self._number(
            max_drawdown
        )

        absolute_drawdown = abs(
            max_drawdown
        )

        if absolute_drawdown >= 30:

            severity = "HIGH"
            confidence = 0.97

        elif absolute_drawdown >= 15:

            severity = "MODERATE"
            confidence = 0.92

        else:

            return None

        return self._create_card(

            recommendation_type=
                "RISK_ALERT",

            category=
                "DRAWDOWN",

            title=
                "Portfolio Drawdown Review",

            severity=
                severity,

            rationale=(
                f"The maximum observed portfolio "
                f"drawdown is "
                f"{max_drawdown:.2f}%."
            ),

            supporting_metrics={

                "max_drawdown":
                    round(
                        max_drawdown,
                        2
                    )
            },

            suggested_action=(
                "Review historical downside "
                "behaviour and portfolio risk "
                "controls."
            ),

            confidence=
                confidence
        )

    # =====================================================
    # SECTOR DIVERSIFICATION
    # =====================================================

    def _sector_cards(
        self,
        sector_exposure
    ):

        cards = []

        if not isinstance(
            sector_exposure,
            list
        ):

            return cards

        for sector in sector_exposure:

            if not isinstance(
                sector,
                dict
            ):

                continue

            sector_name = sector.get(
                "sector",
                "Unknown"
            )

            percentage = self._number(
                sector.get(
                    "percentage",
                    0
                )
            )

            if percentage < 50:

                continue

            cards.append(

                self._create_card(

                    recommendation_type=
                        "DIVERSIFICATION_REVIEW",

                    category=
                        "SECTOR_EXPOSURE",

                    title=
                        "Sector Exposure Review",

                    severity=
                        "MODERATE",

                    rationale=(
                        f"{sector_name} represents "
                        f"{percentage:.2f}% of "
                        "portfolio value."
                    ),

                    supporting_metrics={

                        "sector":
                            sector_name,

                        "allocation_percentage":
                            round(
                                percentage,
                                2
                            )
                    },

                    suggested_action=(
                        "Review whether the current "
                        "sector exposure is aligned "
                        "with the intended portfolio "
                        "diversification."
                    ),

                    confidence=
                        0.93
                )
            )

        return cards

    # =====================================================
    # PORTFOLIO PERFORMANCE FOLLOW-UP
    # =====================================================

    def _performance_card(
        self,
        profit_loss,
        overall_return
    ):

        profit_loss = self._number(
            profit_loss
        )

        try:

            return_percentage = float(
                str(
                    overall_return
                ).replace(
                    "%",
                    ""
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return_percentage = 0.0

        if return_percentage > -20:

            return None

        severity = (
            "HIGH"
            if return_percentage <= -30
            else "MODERATE"
        )

        confidence = (
            0.97
            if return_percentage <= -30
            else 0.92
        )

        return self._create_card(

            recommendation_type=
                "PORTFOLIO_FOLLOW_UP",

            category=
                "PERFORMANCE",

            title=
                "Portfolio Performance Review",

            severity=
                severity,

            rationale=(
                f"The portfolio has an overall "
                f"return of "
                f"{return_percentage:+.2f}% "
                f"with a profit/loss of "
                f"₹{profit_loss:,.2f}."
            ),

            supporting_metrics={

                "profit_loss":
                    round(
                        profit_loss,
                        2
                    ),

                "overall_return":
                    f"{return_percentage:+.2f}%"
            },

            suggested_action=(
                "Review the portfolio holdings "
                "and the factors contributing "
                "to the observed performance."
            ),

            confidence=
                confidence
        )

    # =====================================================
    # MARKET WATCHLIST
    # =====================================================

    def _market_watchlist_card(
        self,
        market_analysis
    ):

        if not isinstance(
            market_analysis,
            dict
        ):

            return None

        signal = market_analysis.get(
            "overall_signal",
            "Unknown"
        )

        trend = market_analysis.get(
            "trend",
            "Unknown"
        )

        signal_score = self._number(
            market_analysis.get(
                "signal_score",
                0
            )
        )

        if (
            signal not in
            ["Bearish", "Bullish"]
        ):

            return None

        return self._create_card(

            recommendation_type=
                "WATCHLIST_MONITORING",

            category=
                "MARKET_SIGNAL",

            title=
                "Market Signal Monitoring",

            severity=
                "MODERATE",

            rationale=(
                f"The supplied market analysis "
                f"shows a {signal.lower()} "
                f"overall signal with a "
                f"{trend.lower()} trend."
            ),

            supporting_metrics={

                "overall_signal":
                    signal,

                "trend":
                    trend,

                "signal_score":
                    int(
                        signal_score
                    )
            },

            suggested_action=(
                "Monitor changes in the market "
                "trend and supplied technical "
                "signals."
            ),

            confidence=
                0.88
        )

    # =====================================================
    # EDUCATIONAL INSIGHT
    # =====================================================

    def _educational_card(
        self,
        analytics
    ):

        if not isinstance(
            analytics,
            dict
        ):

            return None

        allocation = analytics.get(
            "allocation",
            []
        )

        sector_exposure = analytics.get(
            "sector_exposure",
            []
        )

        if not allocation:

            return None

        return self._create_card(

            recommendation_type=
                "EDUCATIONAL_INSIGHT",

            category=
                "PORTFOLIO_STRUCTURE",

            title=
                "Portfolio Structure Insight",

            severity=
                "INFO",

            rationale=(
                f"The portfolio contains "
                f"{len(allocation)} holdings "
                f"across "
                f"{len(sector_exposure)} "
                "reported sectors."
            ),

            supporting_metrics={

                "holding_count":
                    len(allocation),

                "sector_count":
                    len(sector_exposure)
            },

            suggested_action=(
                "Review the portfolio structure "
                "periodically to understand "
                "allocation and diversification."
            ),

            confidence=
                0.99
        )

    # =====================================================
    # MAIN RECOMMENDATION ENGINE
    # =====================================================

    def generate_recommendations(
        self,
        analytics,
        portfolio_analysis=None,
        market_analysis=None
    ):

        recommendations = []

        if not isinstance(
            analytics,
            dict
        ):

            analytics = {}

        if not isinstance(
            portfolio_analysis,
            dict
        ):

            portfolio_analysis = {}

        if not isinstance(
            market_analysis,
            dict
        ):

            market_analysis = {}

        # -------------------------------------------------
        # CONCENTRATION
        # -------------------------------------------------

        concentration_card = (
            self._concentration_card(
                analytics.get(
                    "concentration_risk",
                    {}
                )
            )
        )

        if concentration_card:

            recommendations.append(
                concentration_card
            )

        # -------------------------------------------------
        # VOLATILITY
        # -------------------------------------------------

        volatility_card = (
            self._volatility_card(
                analytics.get(
                    "volatility",
                    0
                )
            )
        )

        if volatility_card:

            recommendations.append(
                volatility_card
            )

        # -------------------------------------------------
        # DRAWDOWN
        # -------------------------------------------------

        drawdown_card = (
            self._drawdown_card(
                analytics.get(
                    "max_drawdown",
                    0
                )
            )
        )

        if drawdown_card:

            recommendations.append(
                drawdown_card
            )

        # -------------------------------------------------
        # SECTOR EXPOSURE
        # -------------------------------------------------

        recommendations.extend(

            self._sector_cards(
                analytics.get(
                    "sector_exposure",
                    []
                )
            )
        )

        # -------------------------------------------------
        # PERFORMANCE
        # -------------------------------------------------

        performance_card = (
            self._performance_card(

                portfolio_analysis.get(
                    "profit_loss",
                    0
                ),

                portfolio_analysis.get(
                    "overall_return",
                    "0%"
                )
            )
        )

        if performance_card:

            recommendations.append(
                performance_card
            )

        # -------------------------------------------------
        # MARKET WATCHLIST
        # -------------------------------------------------

        market_card = (
            self._market_watchlist_card(
                market_analysis
            )
        )

        if market_card:

            recommendations.append(
                market_card
            )

        # -------------------------------------------------
        # EDUCATIONAL INSIGHT
        # -------------------------------------------------

        educational_card = (
            self._educational_card(
                analytics
            )
        )

        if educational_card:

            recommendations.append(
                educational_card
            )

        # -------------------------------------------------
        # EMPTY RESULT
        # -------------------------------------------------

        if not recommendations:

            recommendations.append(

                self._create_card(

                    recommendation_type=
                        "PORTFOLIO_FOLLOW_UP",

                    category=
                        "GENERAL_REVIEW",

                    title=
                        "Portfolio Review",

                    severity=
                        "INFO",

                    rationale=(
                        "No threshold-based risk "
                        "or diversification alert "
                        "was triggered by the "
                        "supplied analytics."
                    ),

                    supporting_metrics={},

                    suggested_action=(
                        "Continue reviewing portfolio "
                        "analytics and market signals "
                        "periodically."
                    ),

                    confidence=
                        0.90
                )
            )

        return recommendations