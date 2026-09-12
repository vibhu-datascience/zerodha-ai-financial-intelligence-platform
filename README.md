# Zerodha AI Financial Intelligence Platform

An AI-powered full-stack financial intelligence platform that combines portfolio analytics, market analysis, financial news, MCP-based governed tool access, LangGraph agentic AI workflows, Gemini-powered financial intelligence, and policy-validated recommendation cards.

> This project is designed for financial intelligence and decision support. It does not provide direct buy, sell, or hold instructions.

---

## Live Deployment

### Frontend
https://zerodha-ai-financial-intelligence-p.vercel.app

### Backend API
https://zerodha-ai-financial-intelligence-net0.onrender.com

### Backend Swagger Documentation
https://zerodha-ai-financial-intelligence-net0.onrender.com/docs

### MCP Server
https://zerodha-ai-mcp.onrender.com/mcp

---

# Project Overview

The Zerodha AI Financial Intelligence Platform helps users understand their portfolio and market environment through a structured financial intelligence pipeline.

The platform combines:

- Portfolio data
- Market data
- Financial news
- Deterministic portfolio analytics
- Technical market indicators
- Gemini-powered AI financial intelligence
- MCP-based governed tool access
- LangGraph agentic workflow
- Evidence-based recommendation cards
- Recommendation safety validation
- React dashboard
- Authentication
- Persistent PostgreSQL database

The goal is to transform raw financial data into structured, explainable and reviewable financial intelligence.

---

# Key Features

## Portfolio Analysis

The platform provides:

- Invested value
- Current portfolio value
- Profit/Loss
- Overall return
- Risk level
- Holding-level performance
- Best-performing holdings
- Worst-performing holdings
- Portfolio composition
- Portfolio areas to review

---

# Portfolio Analytics

Deterministic analytics are calculated by backend services.

The analytics engine provides:

- Portfolio allocation
- Holding concentration
- Sector exposure
- Portfolio volatility
- Maximum drawdown
- Risk classification
- Holding contribution to portfolio performance

These calculations are performed by backend services rather than relying on the LLM.

The LLM receives the calculated financial evidence and primarily explains it.

---

# Market Analysis

Market intelligence includes:

- NIFTY market data
- Daily return
- Volatility
- Trend
- RSI
- RSI signal
- MACD
- MACD signal
- MACD trend
- Signal score
- Overall technical signal

The market indicators are calculated deterministically by the backend market-analysis service.

---

# Financial News

The platform displays financial news with:

- Article title
- Source
- Description
- Publication time
- Article sentiment
- Overall sentiment
- Positive news count
- Negative news count
- Neutral news count
- Total articles analyzed

News data is supplied to the financial intelligence workflow as structured context.

---

# AI Financial Intelligence

The platform uses Google Gemini to generate grounded financial intelligence from structured portfolio, market and news data.

The AI does not directly access the database.

Instead, the application:

1. Fetches financial data
2. Runs deterministic analytics
3. Builds structured grounded context
4. Passes the context to the Gemini model
5. Generates financial intelligence
6. Validates the generated report
7. Displays the result on the dashboard

The generated report covers areas such as:

1. Current Market Condition
2. Portfolio Performance
3. Relationship Between Market and Portfolio
4. Important Financial News Themes
5. Key Risks or Areas to Monitor

The AI is instructed to:

- Use only supplied data
- Avoid inventing facts
- Avoid inventing financial events
- Avoid unsupported correlations
- Avoid unsupported causation
- Avoid direct buy recommendations
- Avoid direct sell recommendations
- Avoid direct hold recommendations
- Clearly distinguish observed data from interpretation

---

# AI Recommendations

AI Recommendations are intentionally kept separate from the main AI Financial Intelligence section.

The recommendation engine generates evidence-based areas for review using deterministic portfolio and market analytics.

Recommendation categories include:

- Diversification Review
- Risk Alert
- Watchlist Monitoring
- Portfolio Follow-up
- Educational Insight

Example review-oriented language includes:

- Review
- Monitor
- Evaluate
- Assess
- Understand

The system does not intentionally provide direct:

- Buy instructions
- Sell instructions
- Hold instructions

The purpose of the recommendation layer is decision support rather than personalized investment advice.

---

# Recommendation Cards

Each recommendation card can contain:

- Recommendation type
- Category
- Title
- Severity
- Rationale
- Supporting metrics
- Source
- Freshness
- Confidence
- Suggested action/review

This makes recommendations reviewable and traceable to the underlying financial evidence.

---

# Recommendation Safety and Policy Validation

Every recommendation card passes through a policy validation layer before reaching the dashboard.

The policy validates:

- Required fields
- Recommendation type
- Severity
- Confidence
- Supporting metrics
- Forbidden investment language
- Direct investment actions
- Guaranteed-return language
- Risk-free claims
- Unsupported market/portfolio relationships
- Unsupported correlation claims
- Unsupported causation claims

Only approved recommendation cards are exposed to the frontend.

Example validation result:

{
  "status": "passed",
  "total_cards": 5,
  "approved_cards": 5,
  "blocked_count": 0,
  "errors": []
}

---

# Agentic AI Workflow

The platform uses LangGraph to orchestrate the financial intelligence workflow.

Workflow:

START
  |
  v
FETCH PORTFOLIO
  |
  v
RUN ANALYTICS
  |
  v
FETCH MARKET
  |
  v
BUILD GROUNDED CONTEXT
  |
  v
GENERATE AI REPORT
  |
  v
VALIDATE AI REPORT
  |
  v
END

The workflow is implemented in:

backend/app/services/ai_workflow.py

The workflow uses MCP tools to retrieve structured financial information.

---

# Grounded AI Architecture

The platform separates deterministic computation from AI interpretation.

Financial Data
      |
      v
MCP Tools
      |
      v
Deterministic Analytics
      |
      v
Grounded Context
      |
      v
Gemini LLM
      |
      v
AI Financial Intelligence
      |
      v
Validation
      |
      v
Dashboard

The LLM is not responsible for core financial calculations.

For example, the backend calculates:

- Portfolio value
- Profit/Loss
- Allocation
- Volatility
- Drawdown
- Concentration
- Risk level

Gemini receives these results and produces a structured explanation.

---

# MCP Tool Layer

The platform uses the Model Context Protocol (MCP) as a governed tool layer.

The MCP server is deployed separately from the main FastAPI backend.

Production MCP endpoint:

https://zerodha-ai-mcp.onrender.com/mcp

Available MCP tools:

## 1. get_portfolio

Retrieves:

- Portfolio name
- Holdings
- Quantity
- Buy price
- Invested value
- Sector

## 2. get_market_analysis

Retrieves deterministic market indicators including:

- Trend
- RSI
- MACD
- Volatility
- Signal score
- Overall signal

## 3. analyze_portfolio

Runs the portfolio analysis pipeline.

## 4. run_portfolio_analytics

Runs deterministic portfolio analytics including:

- Allocation
- Concentration
- Sector exposure
- Volatility
- Drawdown
- Risk level

---

# System Architecture

React Dashboard
       |
       v
FastAPI Backend
       |
       v
Financial Intelligence Service
       |
       +------------------+------------------+
       |                  |                  |
       v                  v                  v
Portfolio Service   Market Service    News Service
       |                  |                  |
       +------------------+------------------+
                          |
                          v
                    MCP Tool Layer
                          |
                          v
                   LangGraph Workflow
                          |
             +------------+------------+
             |                         |
             v                         v
   Deterministic Analytics     Grounded AI Context
             |                         |
             |                         v
             |                    Gemini LLM
             |                         |
             +------------+------------+
                          |
                          v
                 Recommendation Engine
                          |
                          v
                 Recommendation Policy
                      Validation
                          |
                          v
                   React Dashboard

---

# Backend Architecture

The backend follows a modular architecture:

FastAPI
   ↓
Routers
   ↓
Services
   ↓
Database / External Data

Important backend services include:

backend/app/services/

- ai_service.py
- ai_workflow.py
- analytics_service.py
- financial_intelligence_service.py
- market_service.py
- news_service.py
- portfolio_service.py
- recommendation_service.py
- recommendation_policy.py

---

# Database

The production application uses PostgreSQL hosted on Neon.

PostgreSQL is used for persistent application data including authentication and portfolio records.

The database configuration is loaded through:

DATABASE_URL

The application supports SQLite as a local development fallback when DATABASE_URL is not configured.

Production architecture:

FastAPI
   |
   v
SQLAlchemy
   |
   v
Neon PostgreSQL

---

# Authentication

The application includes an authentication flow.

Users can:

- Register
- Login
- Logout
- Access protected financial intelligence endpoints

After successful login, the frontend stores the access token and sends it to protected backend endpoints using:

Authorization: Bearer <access_token>

If the backend returns HTTP 401, the frontend clears the session and asks the user to log in again.

Authentication data is stored in the persistent PostgreSQL database.

---

# Frontend

The frontend is built using:

- React
- Vite
- JavaScript
- CSS

The dashboard contains separate sections for:

- Overall Market Outlook
- Market Analysis
- Portfolio Analysis
- Portfolio Analytics
- Financial News
- AI Financial Intelligence
- AI Recommendations

The AI Recommendations section displays:

- Recommendation type
- Severity
- Rationale
- Supporting evidence
- Suggested review
- Confidence
- Source
- Policy validation status

---

# Technology Stack

## Frontend

- React
- Vite
- JavaScript
- CSS

## Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic

## Database

- PostgreSQL
- Neon

## AI

- Google Gemini
- LangGraph

## Agent / Tool Layer

- MCP Python SDK
- Streamable HTTP

## Financial Data

- yfinance
- Financial News API

## Analytics

- Pandas
- NumPy

## Deployment

- Vercel
- Render
- Neon PostgreSQL

---

# Project Structure

zerodha-ai-financial-intelligence-platform/
|
├── backend/
│   |
│   ├── app/
│   │   |
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── seed.py
│   │   |
│   │   ├── mcp/
│   │   │   └── server.py
│   │   |
│   │   ├── routers/
│   │   |
│   │   ├── schemas/
│   │   |
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── ai_workflow.py
│   │   │   ├── analytics_service.py
│   │   │   ├── financial_intelligence_service.py
│   │   │   ├── market_service.py
│   │   │   ├── news_service.py
│   │   │   ├── portfolio_service.py
│   │   │   ├── recommendation_service.py
│   │   │   └── recommendation_policy.py
│   │   |
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .gitignore
│
├── frontend/
│   |
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── Login.jsx
│   |
│   ├── package.json
│   └── ...
│
├── README.md
└── ...

---

# API Endpoints

## Health Check

GET /

Example response:

{
  "message": "Welcome to Zerodha AI Financial Intelligence Platform!"
}

---

## Authentication

### Register

POST /auth/register

### Login

POST /auth/login

---

## Portfolio

GET /portfolio

POST /portfolio-analysis

---

## Market

GET /market

GET /market/analysis

---

## Financial News

GET /news

GET /news/sentiment

---

## Financial Intelligence

GET /financial-intelligence

Optional parameters:

- portfolio_name
- timeframe

Example:

/financial-intelligence?portfolio_name=Growth%20Portfolio&timeframe=1Y

The endpoint combines:

Market
+
Portfolio
+
Analytics
+
News
+
AI Intelligence
+
Recommendations
+
Policy Validation
+
Workflow Validation

---

# Sample Portfolios

The application contains three sample portfolios.

## Growth Portfolio

- RELIANCE.NS
- TCS.NS
- INFY.NS

## Balanced Portfolio

- HDFCBANK.NS
- ITC.NS
- TCS.NS

## Conservative Portfolio

- ITC.NS
- HDFCBANK.NS

These portfolios demonstrate the platform across different portfolio compositions.

---

# Running the Backend

Navigate to the backend directory:

cd backend

Activate the virtual environment:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

For local development without PostgreSQL, the application can fall back to SQLite.

Start FastAPI:

python -m uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

---

# Running the MCP Server Locally

From the backend directory:

python -m app.mcp.server

Local MCP endpoint:

http://127.0.0.1:8100/mcp

The MCP server can be tested using MCP Inspector.

The production MCP server is separately deployed on Render.

---

# Gemini Configuration

The production AI provider is Google Gemini.

The backend uses environment variables such as:

AI_PROVIDER=gemini
GEMINI_API_KEY=<your-api-key>
GEMINI_MODEL=gemini-3.8-flash
GEMINI_TIMEOUT=120

API keys must be stored as environment variables and must never be committed to GitHub.

---

# Frontend Configuration

The frontend uses the backend URL through:

VITE_API_URL

Production example:

VITE_API_URL=https://zerodha-ai-financial-intelligence-net0.onrender.com

The frontend is deployed through Vercel.

---

# Testing

The deployed application has been tested across the main application flow.

## Authentication Testing

Tested:

- User registration
- User login
- Protected API access
- Logout
- Login persistence after backend restart

## Database Testing

Tested:

- PostgreSQL connectivity
- Persistent user data
- Persistent portfolio data
- Portfolio retrieval after service restart

## Financial Intelligence Testing

Tested:

- Portfolio retrieval
- Market analysis
- Deterministic portfolio analytics
- Financial news retrieval
- Gemini financial intelligence
- Recommendation generation
- Recommendation policy validation
- LangGraph workflow execution

## Production UI Testing

Tested:

- Login → Dashboard
- Dashboard automatic data loading
- Refresh Analysis
- Portfolio analytics
- Financial news
- AI Financial Intelligence
- AI Recommendations
- Logout → Login persistence

---

# Validation Architecture

The platform uses multiple validation layers.

Financial Data
      |
      v
Deterministic Analytics
      |
      v
Grounded Context
      |
      v
Gemini Generated Intelligence
      |
      v
AI Report Validation
      |
      v
Recommendation Engine
      |
      v
Recommendation Policy
      |
      v
Dashboard

The LLM is not responsible for performing the core financial calculations.

Numerical analytics are generated by deterministic backend services.

The LLM primarily explains the supplied evidence.

---

# Financial Safety

The platform is designed for financial intelligence and decision support.

It intentionally avoids direct instructions such as:

BUY
SELL
HOLD

It also attempts to prevent:

- Guaranteed return claims
- Risk-free claims
- Unsupported correlations
- Unsupported causation
- Unsupported financial events
- Direct investment actions

Instead, recommendation cards focus on:

- Review
- Monitor
- Evaluate
- Assess
- Understand

This allows the platform to surface potentially important areas without presenting them as personalized investment instructions.

---

# Design Principles

## 1. Deterministic Analytics First

Financial calculations are performed by backend services.

The LLM does not determine:

- Portfolio value
- Profit/Loss
- Allocation
- Volatility
- Drawdown
- Concentration
- Risk score

---

## 2. Grounded AI

The AI receives structured data produced by the application.

It is instructed not to invent information outside the supplied context.

---

## 3. Governed Tool Access

MCP provides a structured tool layer for the AI workflow.

The workflow interacts with defined tools instead of allowing the LLM to directly access the database.

---

## 4. Policy-Controlled Recommendations

Recommendation cards are generated separately and validated before being shown to the user.

---

## 5. Separation of Intelligence and Recommendations

The platform intentionally keeps:

AI Financial Intelligence

and

AI Recommendations

as separate dashboard sections.

Financial Intelligence explains the available evidence.

Recommendations identify evidence-based areas that may require review.

---

# Limitations

This project is a capstone/demo implementation.

## Market Data

External financial data may be delayed, unavailable or subject to provider limitations.

## Market Status

The current market-status implementation is simplified and should be replaced with production-grade exchange calendar and real-time market-status logic.

## Risk Analytics

The volatility and drawdown calculations are intended for portfolio intelligence and are not a complete institutional risk-management model.

## AI

LLM-generated language can still be imperfect. The application therefore applies validation rules to reduce unsupported or unsafe outputs.

## Recommendations

Recommendations are designed as decision-support prompts and should not be interpreted as personalized investment advice.

## Database

The production application uses Neon PostgreSQL for persistent storage.

The database is external to the Render application filesystem, allowing authentication and portfolio data to survive Render service restarts and redeployments.

---

# Future Improvements

Potential future improvements include:

- Real broker integration
- User-specific portfolio management
- Redis caching
- Background data refresh
- Advanced portfolio risk models
- Portfolio/market correlation analysis
- Historical portfolio performance tracking
- RAG-based financial knowledge retrieval
- Additional financial news sources
- Advanced observability
- Human review workflows
- Automated test suite
- Role-based access control
- Production-grade authentication enhancements
- Real-time market-status integration

---

# Demo Flow

Recommended product demonstration:

1. Open the application
2. Login
3. Show Overall Market Outlook
4. Show Market Analysis
5. Show Portfolio Analysis
6. Show Portfolio Analytics
7. Show Financial News
8. Show AI Financial Intelligence
9. Show AI Recommendations
10. Show Supporting Evidence
11. Show Policy Validation
12. Demonstrate another portfolio
13. Explain MCP + LangGraph workflow

---

# Submission Highlights

This project demonstrates:

- Full-stack application development
- FastAPI REST APIs
- React frontend
- PostgreSQL database
- SQLAlchemy ORM
- Persistent authentication
- External financial data integration
- Deterministic financial analytics
- Technical market analysis
- Financial news integration
- Gemini LLM integration
- Grounded AI context
- LangGraph agentic workflow
- MCP tool integration
- Structured AI output
- Recommendation engine
- Recommendation policy validation
- Evidence-based decision support
- Production deployment
- Multi-portfolio analysis

---

# Deployment Architecture

USERS
   |
   v
React / Vercel
   |
   v
FastAPI / Render
   |
   +------------------+------------------+
   |                  |                  |
   v                  v                  v
PostgreSQL          MCP Server       External APIs
/ Neon              / Render         yfinance / News
   |                  |
   |                  v
   |            LangGraph Workflow
   |                  |
   |                  v
   |              Gemini LLM
   |                  |
   +------------------+
                      |
                      v
              Recommendations
                      |
                      v
              Policy Validation
                      |
                      v
                 Dashboard

---

# Disclaimer

This project is intended for educational, analytical and demonstration purposes.

The information and recommendations generated by this application should not be treated as personalized financial, investment, legal or tax advice.

Users should independently evaluate financial decisions and consult a qualified professional where appropriate.

---

# Conclusion

The Zerodha AI Financial Intelligence Platform demonstrates how deterministic financial analytics, persistent data storage, governed MCP tool access, agentic AI workflows, grounded Gemini intelligence and policy validation can be combined to create a structured financial intelligence system.

The overall architecture is:

Data
  ↓
Deterministic Analytics
  ↓
MCP Tools
  ↓
LangGraph Agentic Workflow
  ↓
Grounded Context
  ↓
Gemini AI Financial Intelligence
  ↓
Recommendation Engine
  ↓
Policy Validation
  ↓
Dashboard

The system is designed so that AI enhances the understanding of financial evidence while deterministic services and validation layers remain responsible for reliability, structure and safety.