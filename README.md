# Zerodha AI Financial Intelligence Platform

An AI-powered full-stack financial intelligence platform that combines portfolio analytics, market analysis, financial news, MCP-based tool access, agentic AI workflows, local LLM intelligence, and policy-validated recommendations.

> This project is designed for financial intelligence and decision support. It does not provide direct buy, sell, or hold instructions.


## Project Overview

The Zerodha AI Financial Intelligence Platform helps users understand their portfolio and market environment through a structured financial intelligence pipeline.

The platform combines:

- Portfolio data
- Market data
- Financial news
- Deterministic portfolio analytics
- Technical market indicators
- AI-powered financial intelligence
- MCP-based governed tool access
- LangGraph agentic workflow
- Local LLM using Ollama
- Evidence-based recommendation cards
- Recommendation safety validation
- Interactive React dashboard
- Authentication

The goal is to transform raw financial data into structured, explainable and reviewable financial intelligence.


## Key Features

### Portfolio Analysis

The platform provides:

- Invested value
- Current portfolio value
- Profit/Loss
- Overall return
- Risk level
- Holding-level performance
- Best and worst performing holdings
- Portfolio composition
- Portfolio areas to review


### Portfolio Analytics

Deterministic analytics are calculated by the backend.

The analytics engine provides:

- Portfolio allocation
- Holding concentration
- Sector exposure
- Portfolio volatility
- Maximum drawdown
- Risk classification
- Holding contribution to portfolio performance

These calculations are performed by backend services rather than relying on the LLM.


### Market Analysis

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


### Financial News

The platform displays financial news with:

- Article title
- Source
- Description
- Publication time
- Sentiment
- Overall sentiment
- Positive news count
- Negative news count
- Neutral news count


## AI Financial Intelligence

The platform uses a local LLM through Ollama to generate financial intelligence from supplied financial data.

The AI receives structured and grounded context rather than directly accessing the database.

The generated report covers:

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
- Avoid hold recommendations
- Clearly distinguish observed data from interpretation


## AI Recommendations

AI Recommendations are intentionally kept separate from the main AI Financial Intelligence section.

The recommendation engine generates evidence-based areas for review using deterministic portfolio and market analytics.

Example recommendation types include:

- Portfolio Concentration Review
- Portfolio Volatility Review
- Portfolio Drawdown Review
- Sector Exposure Review
- Portfolio Performance Review
- Market Signal Monitoring
- Portfolio Structure Insight

The system uses review-oriented language such as:

- Review
- Monitor
- Evaluate
- Assess
- Understand

It does not intentionally generate direct:

- Buy instructions
- Sell instructions
- Hold instructions


## Recommendation Safety and Policy Validation

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
- Unsupported market/portfolio relationships
- Unsupported correlation claims

Only approved recommendation cards are exposed to the frontend.

Example validation result:

{
  "status": "passed",
  "total_cards": 6,
  "approved_cards": 6,
  "blocked_count": 0,
  "errors": []
}


## Agentic AI Workflow

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


## MCP Tool Layer

The platform uses the Model Context Protocol (MCP) as a governed tool layer between backend financial services and the AI workflow.

MCP server:

http://127.0.0.1:8100/mcp

Available MCP tools:

### 1. get_portfolio

Retrieves:

- Portfolio name
- Holdings
- Quantity
- Buy price
- Invested value
- Sector

### 2. get_market_analysis

Retrieves deterministic market indicators including:

- Trend
- RSI
- MACD
- Volatility
- Signal score
- Overall signal

### 3. analyze_portfolio

Runs the portfolio analysis pipeline.

### 4. run_portfolio_analytics

Runs deterministic portfolio analytics including:

- Allocation
- Concentration
- Sector exposure
- Volatility
- Drawdown
- Risk level


## System Architecture

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
             |                    Ollama LLM
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


## Backend Architecture

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


## Frontend

The frontend is built using React and Vite.

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


## Authentication

The application includes an authentication flow.

After successful login, the frontend stores the access token and sends it to protected backend endpoints using:

Authorization: Bearer <access_token>

If the backend returns an HTTP 401 response, the frontend clears the session and asks the user to log in again.


## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite

### AI

- Ollama
- Llama 3.2
- LangGraph

### Agent / Tool Layer

- MCP Python SDK
- Streamable HTTP

### Financial Data

- yfinance
- Financial news service

### Analytics

- Pandas
- NumPy


## Project Structure

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
│   │
│   ├── package.json
│   └── ...
│
├── README.md
└── ...


## API Endpoints

### Health Check

GET /

Example response:

{
  "message": "Welcome to Zerodha AI Financial Intelligence Platform!"
}


### Financial Intelligence

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


## Sample Portfolios

The development database contains three sample portfolios.

### Growth Portfolio

- RELIANCE.NS
- TCS.NS
- INFY.NS

### Balanced Portfolio

- HDFCBANK.NS
- ITC.NS
- TCS.NS

### Conservative Portfolio

- ITC.NS
- HDFCBANK.NS

These portfolios are used to demonstrate the platform across different portfolio compositions.


## Running the Backend

Navigate to the backend directory:

cd backend

Activate the virtual environment:

source venv/bin/activate

Initialize the database:

python -m app.database.seed

Start FastAPI:

python -m uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000


## Running the MCP Server

From the backend directory:

python -m app.mcp.server

MCP server:

http://127.0.0.1:8100/mcp

The MCP server can be tested using MCP Inspector.


## Running Ollama

Make sure Ollama is running locally.

The default model is:

llama3.2:3b

The backend supports the following environment variables:

- OLLAMA_URL
- OLLAMA_MODEL
- OLLAMA_TIMEOUT

Example:

OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=120


## Running the Frontend

Navigate to the frontend:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

Frontend:

http://localhost:5174


## Testing

The application has been tested across the sample portfolios.

### Growth Portfolio

Portfolio: Growth Portfolio
Workflow: passed
Recommendations: 6
Policy: passed

### Balanced Portfolio

Portfolio: Balanced Portfolio
Workflow: passed
Recommendations: 6
Policy: passed

### Conservative Portfolio

Portfolio: Conservative Portfolio
Workflow: passed
Recommendations: 6
Policy: passed

The AI workflow validation returns:

{
  "status": "passed",
  "validation_errors": []
}

Recommendation policy validation returns:

{
  "status": "passed",
  "total_cards": 6,
  "approved_cards": 6,
  "blocked_count": 0,
  "errors": []
}


## Validation Architecture

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
LLM Generated Intelligence
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


## Financial Safety

The platform is designed for financial intelligence and decision support.

It intentionally avoids direct instructions such as:

BUY
SELL
HOLD

It also attempts to prevent:

- Guaranteed Returns
- Risk-Free Claims
- Unsupported Correlations
- Unsupported Causation
- Unsupported Financial Events

Instead, recommendation cards focus on:

- Review
- Monitor
- Evaluate
- Assess
- Understand

This allows the platform to surface potentially important areas without presenting them as personalized investment instructions.


## Design Principles

### 1. Deterministic Analytics First

Financial calculations are performed by backend services.

The LLM does not determine:

- Portfolio value
- Profit/Loss
- Allocation
- Volatility
- Drawdown
- Concentration
- Risk score


### 2. Grounded AI

The AI receives structured data produced by the application.

It is instructed not to invent information outside the supplied context.


### 3. Governed Tool Access

MCP provides a structured tool layer for the AI workflow.

The AI workflow interacts with defined tools instead of directly accessing the database.


### 4. Policy-Controlled Recommendations

Recommendation cards are generated separately and validated before being shown to the user.


### 5. Separation of Intelligence and Recommendations

The platform intentionally keeps:

AI Financial Intelligence

and

AI Recommendations

as separate dashboard sections.

Financial Intelligence explains the available evidence.

Recommendations identify evidence-based areas that may require review.


## Limitations

This project is currently a capstone/demo implementation.

### Market Data

External financial data may be delayed, unavailable or subject to provider limitations.

### Market Status

The current market-status implementation is simplified and should be replaced with production-grade exchange calendar and real-time market-status logic.

### Risk Analytics

The volatility and drawdown calculations are intended for portfolio intelligence and are not a complete institutional risk-management model.

### AI

LLM-generated language can still be imperfect. The application therefore applies validation rules to reduce unsupported or unsafe outputs.

### Recommendations

Recommendations are designed as decision-support prompts and should not be interpreted as personalized investment advice.


## Future Improvements

Potential future improvements include:

- Production cloud deployment
- Real broker integration
- User-specific portfolios
- PostgreSQL
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
- Production-grade authentication


## Demo Flow

Recommended product demonstration:

1. Open the application
        ↓
2. Login
        ↓
3. Show Overall Market Outlook
        ↓
4. Show Market Analysis
        ↓
5. Show Portfolio Analysis
        ↓
6. Show Portfolio Analytics
        ↓
7. Show Financial News
        ↓
8. Show AI Financial Intelligence
        ↓
9. Show AI Recommendations
        ↓
10. Show Supporting Evidence
        ↓
11. Show Policy Validation
        ↓
12. Demonstrate another portfolio
        ↓
13. Explain MCP + LangGraph workflow


## Submission Highlights

This project demonstrates:

- Full-stack application development
- FastAPI REST APIs
- React frontend
- SQLite database
- SQLAlchemy ORM
- External financial data integration
- Deterministic financial analytics
- Technical market analysis
- Financial news integration
- Local LLM integration
- Ollama
- LangGraph agentic workflow
- MCP tool integration
- Structured AI output
- Recommendation engine
- Recommendation policy validation
- Authentication
- Multi-portfolio testing
- Evidence-based decision support


## Deployment

Live application URL:

[ADD DEPLOYED URL HERE]

Replace the placeholder with the deployed application URL after deployment.


## Disclaimer

This project is intended for educational, analytical and demonstration purposes.

The information and recommendations generated by this application should not be treated as personalized financial, investment, legal or tax advice.

Users should independently evaluate financial decisions and consult a qualified professional where appropriate.


## Conclusion

The Zerodha AI Financial Intelligence Platform demonstrates how deterministic financial analytics, governed tool access, agentic AI workflows, local LLMs and policy validation can be combined to create a structured financial intelligence system.

The overall architecture is:

Data
  ↓
Analytics
  ↓
MCP Tools
  ↓
Agentic Workflow
  ↓
AI Financial Intelligence
  ↓
Recommendation Engine
  ↓
Policy Validation
  ↓
Dashboard

The system is designed so that AI enhances the understanding of financial evidence while deterministic services and validation layers remain responsible for reliability, structure and safety.