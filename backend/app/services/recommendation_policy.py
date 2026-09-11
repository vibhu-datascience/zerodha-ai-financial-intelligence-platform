from typing import Any


class RecommendationPolicy:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.forbidden_phrases = [

            # Direct buy advice
            "buy this stock",
            "buy the stock",
            "buy this share",
            "you should buy",
            "recommend buying",
            "recommended to buy",
            "strong buy",

            # Direct sell advice
            "sell this stock",
            "sell the stock",
            "sell this share",
            "you should sell",
            "recommend selling",
            "recommended to sell",
            "strong sell",

            # Direct investment instructions
            "invest in this stock",
            "invest in this share",
            "purchase this stock",
            "purchase this share",
            "exit this stock",
            "exit the stock",

            # Guaranteed outcomes
            "guaranteed profit",
            "guaranteed return",
            "risk-free",
            "certain profit",
            "will definitely increase",
            "will definitely rise",
            "will definitely fall",
            "will definitely decline",

            # Unsupported market causation
            "market caused the portfolio",
            "market movements caused the portfolio",
            "market conditions caused the portfolio",
            "portfolio declined because of the market",
            "portfolio increased because of the market",

            # Unsupported correlation
            "portfolio is correlated with the market",
            "portfolio is highly correlated with the market",
            "portfolio has a strong correlation with the market",
            "portfolio has a positive correlation with the market",
            "portfolio has a negative correlation with the market"
        ]

    # =====================================================
    # VALIDATE SINGLE CARD
    # =====================================================

    def validate_card(
        self,
        card: dict[str, Any]
    ):

        errors = []

        # -------------------------------------------------
        # CARD TYPE
        # -------------------------------------------------

        if not isinstance(card, dict):

            return {
                "valid": False,
                "errors": [
                    "Recommendation card must be an object."
                ]
            }

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        required_fields = [

            "type",
            "category",
            "title",
            "severity",
            "rationale",
            "supporting_metrics",
            "source",
            "freshness",
            "confidence",
            "suggested_action"
        ]

        for field in required_fields:

            if field not in card:

                errors.append(
                    f"Missing required field: {field}"
                )

        # -------------------------------------------------
        # TYPE VALIDATION
        # -------------------------------------------------

        allowed_types = [

            "RISK_ALERT",
            "DIVERSIFICATION_REVIEW",
            "WATCHLIST_MONITORING",
            "PORTFOLIO_FOLLOW_UP",
            "EDUCATIONAL_INSIGHT"
        ]

        if (
            card.get("type")
            not in allowed_types
        ):

            errors.append(
                "Invalid recommendation type."
            )

        # -------------------------------------------------
        # SEVERITY VALIDATION
        # -------------------------------------------------

        allowed_severity = [

            "INFO",
            "LOW",
            "MODERATE",
            "HIGH"
        ]

        if (
            card.get("severity")
            not in allowed_severity
        ):

            errors.append(
                "Invalid recommendation severity."
            )

        # -------------------------------------------------
        # CONFIDENCE VALIDATION
        # -------------------------------------------------

        confidence = card.get(
            "confidence"
        )

        try:

            confidence = float(
                confidence
            )

            if not 0 <= confidence <= 1:

                errors.append(
                    "Confidence must be between 0 and 1."
                )

        except (
            TypeError,
            ValueError
        ):

            errors.append(
                "Confidence must be numeric."
            )

        # -------------------------------------------------
        # SUPPORTING METRICS
        # -------------------------------------------------

        if not isinstance(
            card.get(
                "supporting_metrics"
            ),
            dict
        ):

            errors.append(
                "Supporting metrics must be an object."
            )

        # -------------------------------------------------
        # TEXT SAFETY CHECK
        # -------------------------------------------------

        text_fields = [

            card.get(
                "title",
                ""
            ),

            card.get(
                "rationale",
                ""
            ),

            card.get(
                "suggested_action",
                ""
            )
        ]

        combined_text = " ".join(
            str(value)
            for value in text_fields
            if value is not None
        ).lower()

        # -------------------------------------------------
        # FORBIDDEN PHRASES
        # -------------------------------------------------

        for phrase in self.forbidden_phrases:

            if phrase in combined_text:

                errors.append(
                    "Forbidden recommendation language "
                    f"detected: '{phrase}'"
                )

        # -------------------------------------------------
        # UNSUPPORTED ACTION WORDS
        # -------------------------------------------------

        direct_actions = [

            "sell ",
            "buy ",
            "purchase ",
            "liquidate ",
            "exit ",
            "short ",
            "go long "
        ]

        for phrase in direct_actions:

            if phrase in combined_text:

                errors.append(
                    "Direct investment action detected: "
                    f"'{phrase.strip()}'"
                )

        # =================================================
        # RESULT
        # =================================================

        if errors:

            return {
                "valid": False,
                "errors": errors
            }

        return {
            "valid": True,
            "errors": []
        }

    # =====================================================
    # VALIDATE ALL CARDS
    # =====================================================

    def validate_recommendations(
        self,
        recommendations
    ):

        if not isinstance(
            recommendations,
            list
        ):

            return {

                "status":
                    "failed",

                "valid_cards":
                    [],

                "blocked_cards":
                    [],

                "errors": [
                    "Recommendations must be a list."
                ]
            }

        valid_cards = []
        blocked_cards = []
        errors = []

        for card in recommendations:

            validation = (
                self.validate_card(
                    card
                )
            )

            if validation["valid"]:

                valid_cards.append(
                    card
                )

            else:

                blocked_cards.append(
                    card
                )

                errors.extend(
                    validation["errors"]
                )

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        if blocked_cards:

            status = "partial"

        else:

            status = "passed"

        return {

            "status":
                status,

            "valid_cards":
                valid_cards,

            "blocked_cards":
                blocked_cards,

            "errors":
                errors,

            "total_cards":
                len(recommendations),

            "approved_cards":
                len(valid_cards),

            "blocked_count":
                len(blocked_cards)
        }