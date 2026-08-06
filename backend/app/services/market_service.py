import yfinance as yf

class MarketService:

    def get_market_status(self):

        try:
           nifty = yf.Ticker("^NSEI")
           sensex = yf.Ticker("^BSESN")

           nifty_history = nifty.history(period="1d")
           sensex_history = sensex.history(period="1d")    

           nifty_price = nifty_history['Close'].iloc[-1]
           sensex_price = sensex_history['Close'].iloc[-1]
 
           return {
                 "exchange": "NSE",
                 "market_status": "OPEN",
                 "nifty": round(float(nifty_price), 2),
                 "sensex": round(float(sensex_price), 2)
                   }

        except Exception as e:
            return {
                "error": "Unable to fetch market status",
                "details": str(e)
            }
    