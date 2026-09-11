import yfinance as yf


class MarketService:

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def get_market_status(self):

        try:

            nifty = yf.Ticker("^NSEI")
            sensex = yf.Ticker("^BSESN")

            nifty_history = nifty.history(
                period="5d"
            )

            sensex_history = sensex.history(
                period="5d"
            )

            if nifty_history.empty or sensex_history.empty:

                return {
                    "error":
                        "Unable to fetch market data"
                }

            nifty_price = (
                nifty_history["Close"].iloc[-1]
            )

            sensex_price = (
                sensex_history["Close"].iloc[-1]
            )

            return {

                "exchange":
                    "NSE",

                "market_status":
                    "OPEN",

                "nifty":
                    round(
                        float(nifty_price),
                        2
                    ),

                "sensex":
                    round(
                        float(sensex_price),
                        2
                    )
            }

        except Exception as e:

            return {

                "error":
                    "Unable to fetch market status",

                "details":
                    str(e)
            }

    # =====================================================
    # CURRENT PRICE
    # =====================================================

    def get_current_price(self, symbol):

        try:

            ticker = yf.Ticker(symbol)

            data = ticker.history(
                period="5d"
            )

            if data.empty:

                return None

            current_price = (
                data["Close"].iloc[-1]
            )

            return round(
                float(current_price),
                2
            )

        except Exception as e:

            print(
                f"Error fetching price for "
                f"{symbol}: {e}"
            )

            return None

    # =====================================================
    # CURRENT + PREVIOUS CLOSE
    # =====================================================

    def get_current_and_previous_price(
        self,
        symbol
    ):

        try:

            ticker = yf.Ticker(symbol)

            data = ticker.history(
                period="5d"
            )

            if data.empty:

                return None

            # Need at least 2 trading sessions
            if len(data) < 2:

                return None

            current_price = (
                data["Close"].iloc[-1]
            )

            previous_price = (
                data["Close"].iloc[-2]
            )

            return {

                "current_price":
                    round(
                        float(current_price),
                        2
                    ),

                "previous_price":
                    round(
                        float(previous_price),
                        2
                    )
            }

        except Exception as e:

            print(
                f"Error fetching previous "
                f"price for {symbol}: {e}"
            )

            return None

    # =====================================================
    # MARKET ANALYSIS
    # =====================================================

    def get_market_analysis(
        self,
        symbol="^NSEI"
    ):

        try:

            ticker = yf.Ticker(symbol)

            data = ticker.history(
                period="3mo"
            )

            if data.empty:

                return {

                    "error":
                        "No market data available"
                }

            # =================================================
            # DAILY RETURN
            # =================================================

            data["Daily_Return"] = (
                data["Close"].pct_change()
            )

            # =================================================
            # VOLATILITY
            # =================================================

            data["Volatility"] = (
                data["Daily_Return"]
                .rolling(window=5)
                .std()
            )

            # =================================================
            # MOVING AVERAGE
            # =================================================

            data["MA_5"] = (
                data["Close"]
                .rolling(window=5)
                .mean()
            )

            # =================================================
            # TREND
            # =================================================

            data["Trend"] = data.apply(

                lambda row:

                "Bullish"
                if row["Close"] > row["MA_5"]
                else "Bearish",

                axis=1
            )

            # =================================================
            # RSI
            # =================================================

            delta = (
                data["Close"].diff()
            )

            gain = (
                delta.clip(lower=0)
            )

            loss = (
                -delta.clip(upper=0)
            )

            avg_gain = (
                gain
                .rolling(window=14)
                .mean()
            )

            avg_loss = (
                loss
                .rolling(window=14)
                .mean()
            )

            rs = (
                avg_gain / avg_loss
            )

            data["RSI"] = (
                100
                - (
                    100
                    / (1 + rs)
                )
            )

            # =================================================
            # RSI SIGNAL
            # =================================================

            data["RSI_Signal"] = (
                data["RSI"].apply(

                    lambda x:

                    "Bullish"
                    if x < 30

                    else
                    "Bearish"
                    if x > 70

                    else
                    "Neutral"
                )
            )

            # =================================================
            # MACD
            # =================================================

            ema_12 = (
                data["Close"]
                .ewm(
                    span=12,
                    adjust=False
                )
                .mean()
            )

            ema_26 = (
                data["Close"]
                .ewm(
                    span=26,
                    adjust=False
                )
                .mean()
            )

            data["MACD"] = (
                ema_12 - ema_26
            )

            data["MACD_Signal"] = (
                data["MACD"]
                .ewm(
                    span=9,
                    adjust=False
                )
                .mean()
            )

            # =================================================
            # MACD TREND
            # =================================================

            data["MACD_Trend"] = data.apply(

                lambda row:

                "Bullish"
                if row["MACD"]
                > row["MACD_Signal"]

                else "Bearish",

                axis=1
            )

            # =================================================
            # SIGNAL SCORE
            # =================================================

            data["Signal_Score"] = 0

            data.loc[
                data["Trend"] == "Bullish",
                "Signal_Score"
            ] += 1

            data.loc[
                data["Trend"] == "Bearish",
                "Signal_Score"
            ] -= 1

            data.loc[
                data["RSI_Signal"] == "Bullish",
                "Signal_Score"
            ] += 1

            data.loc[
                data["RSI_Signal"] == "Bearish",
                "Signal_Score"
            ] -= 1

            data.loc[
                data["MACD_Trend"] == "Bullish",
                "Signal_Score"
            ] += 1

            data.loc[
                data["MACD_Trend"] == "Bearish",
                "Signal_Score"
            ] -= 1

            # =================================================
            # OVERALL SIGNAL
            # =================================================

            data["Overall_Signal"] = (
                data["Signal_Score"].apply(

                    lambda x:

                    "Bullish"
                    if x >= 2

                    else
                    "Bearish"
                    if x <= -2

                    else
                    "Neutral"
                )
            )

            # =================================================
            # LATEST DATA
            # =================================================

            latest = data.iloc[-1]

            # =================================================
            # MARKET INSIGHT
            # =================================================

            if latest["Signal_Score"] >= 2:

                market_insight = (
                    "Market sentiment is bullish "
                    "based on the current trend, "
                    "RSI and MACD indicators."
                )

            elif latest["Signal_Score"] <= -2:

                market_insight = (
                    "Market sentiment is bearish "
                    "based on the current trend, "
                    "RSI and MACD indicators."
                )

            else:

                market_insight = (
                    "Market sentiment is neutral "
                    "because the indicators do "
                    "not show a strong directional "
                    "signal."
                )

            # =================================================
            # FINAL RESPONSE
            # =================================================

            return {

                "symbol":
                    symbol,

                "close":
                    round(
                        float(
                            latest["Close"]
                        ),
                        2
                    ),

                "daily_return":
                    round(
                        float(
                            latest["Daily_Return"]
                            * 100
                        ),
                        2
                    ),

                "volatility":
                    round(
                        float(
                            latest["Volatility"]
                            * 100
                        ),
                        2
                    ),

                "trend":
                    latest["Trend"],

                "rsi":
                    round(
                        float(
                            latest["RSI"]
                        ),
                        2
                    ),

                "rsi_signal":
                    latest["RSI_Signal"],

                "macd":
                    round(
                        float(
                            latest["MACD"]
                        ),
                        2
                    ),

                "macd_signal":
                    round(
                        float(
                            latest["MACD_Signal"]
                        ),
                        2
                    ),

                "macd_trend":
                    latest["MACD_Trend"],

                "signal_score":
                    int(
                        latest["Signal_Score"]
                    ),

                "overall_signal":
                    latest["Overall_Signal"],

                "market_insight":
                    market_insight
            }

        except Exception as e:

            return {

                "error":
                    "Unable to perform "
                    "market analysis",

                "details":
                    str(e)
            }