import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.routers import financial_insight
from app.database.database import Base, engine
from app.database.seed import seed_database
Base.metadata.create_all(bind=engine)
seed_database()
from app.database import models
from app.routers import portfolio
from app.routers import market
from app.routers import news
from app.routers.ai_router import router as ai_router
from app.routers.financial_intelligence_router import (
    router as financial_intelligence_router
)
from app.routers import stock


app = FastAPI(
    title="Zerodha AI Financial Intelligence Platform",
    version="1.0.0"
)


# =====================================================
# DATABASE
# =====================================================

Base.metadata.create_all(bind=engine)


# =====================================================
# CORS
# =====================================================

frontend_url = os.getenv("FRONTEND_URL")

allowed_origins = [
    # Local development
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5177",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5177",

    # Vercel production
    "https://zerodha-ai-financial-intelligence-p.vercel.app",
]

if frontend_url:
    allowed_origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://[a-zA-Z0-9-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# ROUTERS
# =====================================================

app.include_router(auth.router)

app.include_router(portfolio.router)

app.include_router(market.router)

app.include_router(news.router)

app.include_router(financial_insight.router)

app.include_router(ai_router)

app.include_router(
    financial_intelligence_router
)

app.include_router(stock.router)


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():
    return {
        "message": "Welcome to Zerodha AI Financial Intelligence Platform!"
    }