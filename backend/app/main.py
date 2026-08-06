from fastapi import FastAPI
from app.routers import portfolio   
from app.routers import market
from app.routers import news    

app = FastAPI(
    title="Zerodha AI Financial Intelligence Platform",
    version="1.0.0"
)

app.include_router(portfolio.router)
app.include_router(market.router)
app.include_router(news.router)

@app.get("/")
def home():
    return {"message": "Welcome to Zerodha AI Financial Intelligence Platform!"}



