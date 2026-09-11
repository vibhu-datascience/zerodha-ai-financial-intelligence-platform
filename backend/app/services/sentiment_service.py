class SentimentService:

    def analyze(self, text):

        positive_words = [
            "gain",
            "gains",
            "rise",
            "rises",
            "growth",
            "positive",
            "bullish",
            "surge",
            "strong",
            "profit",
            "profits",
            "recovery",
            "up"
        ]

        negative_words = [
            "fall",
            "falls",
            "decline",
            "declines",
            "negative",
            "bearish",
            "drop",
            "drops",
            "loss",
            "losses",
            "weak",
            "crash",
            "down"
        ]

        text = text.lower()

        positive_score = sum(
            word in text for word in positive_words
        )

        negative_score = sum(
            word in text for word in negative_words
        )

        if positive_score > negative_score:
            sentiment = "Positive"

        elif negative_score > positive_score:
            sentiment = "Negative"

        else:
            sentiment = "Neutral"

        return {
            "sentiment": sentiment,
            "positive_score": positive_score,
            "negative_score": negative_score
        }