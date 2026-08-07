# Zerodha AI Financial Intelligence Platform

An AI-powered financial intelligence platform designed to provide users with market data, portfolio insights, and financial news through a modular backend architecture.

## Project Overview

The Zerodha AI Financial Intelligence Platform is being developed as a full-stack financial intelligence application.

The platform will combine:

- Market data
- Portfolio analysis
- Financial news
- Data analytics
- AI-powered financial insights
- Future LLM/RAG capabilities

The project is being developed in multiple layers, starting with the backend API layer.

## Current Progress

### Layer 1 — Backend APIs

The initial backend API layer has been completed.

Currently available APIs:

- Portfolio API
- Market API
- News API

The backend is built using FastAPI and follows a modular router-service architecture.

## Backend Architecture

```text
backend/
│
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── routers/
│   │   ├── market.py
│   │   ├── news.py
│   │   └── portfolio.py
│   │
│   ├── schemas/
│   │   └── portfolio_schema.py
│   │
│   ├── services/
│   │   ├── market_service.py
│   │   ├── news_service.py
│   │   └── portfolio_service.py
│   │
│   └── main.py
│
├── .gitignore
└── requirements.txt