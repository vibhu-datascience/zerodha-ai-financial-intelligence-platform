import { useEffect, useState } from "react";
import "./App.css";
import Login from "./Login";

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000"
).replace(/\/$/, "");

const API_URL = `${API_BASE_URL}/financial-intelligence`;


function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [isAuthenticated, setIsAuthenticated] =
    useState(
      Boolean(
        localStorage.getItem("access_token")
      )
    );

  // =====================================================
  // LOGIN SUCCESS
  // =====================================================

  const handleLogin = () => {
    setIsAuthenticated(true);
    setLoading(true);
    setError("");
  };

  // =====================================================
  // LOGOUT
  // =====================================================

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");

    setIsAuthenticated(false);
    setData(null);
    setError("");
    setLoading(false);
  };

  // =====================================================
  // FETCH ANALYSIS
  // =====================================================

  const fetchAnalysis = async (
    isRefresh = false
  ) => {
    try {
      if (!isAuthenticated) {
        return;
      }

      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const token =
        localStorage.getItem(
          "access_token"
        );

      const response = await fetch(
        API_URL,
        {
          headers: token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : {},
        }
      );

      if (response.status === 401) {
        localStorage.removeItem(
          "access_token"
        );

        localStorage.removeItem(
          "username"
        );

        setIsAuthenticated(false);
        setData(null);

        throw new Error(
          "Your session has expired. Please login again."
        );
      }

      if (!response.ok) {
        throw new Error(
          "Failed to fetch financial analysis"
        );
      }

      const result =
        await response.json();

      setData(result);

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Unable to connect to the backend. Please make sure your FastAPI server is running."
      );

    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // =====================================================
  // INITIAL LOAD
  // =====================================================

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    fetchAnalysis();
  }, [isAuthenticated]);

  // =====================================================
  // LOGIN SCREEN
  // =====================================================

  if (!isAuthenticated) {
    return (
      <Login
        onLogin={handleLogin}
      />
    );
  }

  // =====================================================
  // FORMAT CURRENCY
  // =====================================================

  const formatCurrency = (value) => {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return "₹0";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
      return value;
    }

    return new Intl.NumberFormat(
      "en-IN",
      {
        style: "currency",
        currency: "INR",
        minimumFractionDigits:
          number % 1 === 0 ? 0 : 1,
        maximumFractionDigits: 2,
      }
    ).format(number);
  };

  // =====================================================
  // FORMAT NUMBER
  // =====================================================

  const formatNumber = (value) => {
    if (
      value === null ||
      value === undefined
    ) {
      return "-";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
      return value;
    }

    return new Intl.NumberFormat(
      "en-IN",
      {
        maximumFractionDigits: 2,
      }
    ).format(number);
  };

  // =====================================================
  // SIGNAL CLASS
  // =====================================================

  const getSignalClass = (
    value = ""
  ) => {
    const text =
      String(value).toLowerCase();

    if (
      text.includes("bullish") ||
      text.includes("positive") ||
      text.includes("profit") ||
      text.includes("low")
    ) {
      return "positive";
    }

    if (
      text.includes("bearish") ||
      text.includes("negative") ||
      text.includes("loss") ||
      text.includes("high")
    ) {
      return "negative";
    }

    return "neutral";
  };

  // =====================================================
  // DATE
  // =====================================================

  const formatDate = (
    dateString
  ) => {
    if (!dateString) {
      return "";
    }

    try {
      const date =
        new Date(dateString);

      return date.toLocaleString(
        "en-IN",
        {
          day: "2-digit",
          month: "short",
          year: "numeric",
          hour: "numeric",
          minute: "2-digit",
        }
      );

    } catch {
      return dateString;
    }
  };

  // =====================================================
  // REPORT RENDERER
  // =====================================================

  const renderReport = (text) => {

    if (!text) {
      return (
        <p className="report-text">
          No intelligence report available.
        </p>
      );
    }

    const lines = String(text)
      .split("\n")
      .map(
        (line) => line.trim()
      )
      .filter(
        (line) => line.length > 0
      );

    const sectionHeadings = [
      "Portfolio Performance",
      "Holdings Performance",
      "Important Observations",
      "Portfolio Composition",
      "Portfolio Risk Observations",
      "Areas to Review",

      "Overall Portfolio Performance",
      "Technical Overview",
      "News Overview",
      "Key Observations",
      "Risk Factors",
      "What to Monitor",

      "Current Market Condition",
      "Relationship Between Market and Portfolio",
      "Important Financial News Themes",
      "Key Risks or Areas to Monitor",
    ];

    return lines.map(
      (line, index) => {

        const cleanLine = line
          .replace(/\*\*/g, "")
          .replace(/^#+\s*/, "")
          .trim();

        const normalizedHeading =
          cleanLine
            .replace(
              /^\d+\.\s*/,
              ""
            )
            .replace(
              /:$/,
              ""
            )
            .trim();

        // -------------------------------------------------
        // SECTION HEADING
        // -------------------------------------------------

        if (
          sectionHeadings.some(
            (heading) =>
              heading.toLowerCase() ===
              normalizedHeading.toLowerCase()
          )
        ) {
          return (
            <div
              className="report-section"
              key={index}
            >
              <h3 className="report-heading">
                {normalizedHeading}
              </h3>
            </div>
          );
        }

        // -------------------------------------------------
        // NUMBERED SECTION HEADING
        // -------------------------------------------------

        if (
          /^\d+\.\s+[A-Za-z]/.test(
            cleanLine
          ) &&
          cleanLine.length < 100
        ) {
          return (
            <div
              className="report-section"
              key={index}
            >
              <h3 className="report-heading">
                {cleanLine}
              </h3>
            </div>
          );
        }

        // -------------------------------------------------
        // NUMBERED REVIEW ITEM
        // -------------------------------------------------

        if (
          /^\d+\.\s+/.test(
            cleanLine
          )
        ) {
          const number =
            cleanLine.match(
              /^\d+/
            )?.[0];

          return (
            <div
              className="report-numbered-item"
              key={index}
            >
              <span className="report-number">
                {number}
              </span>

              <p>
                {cleanLine.replace(
                  /^\d+\.\s*/,
                  ""
                )}
              </p>
            </div>
          );
        }

        // -------------------------------------------------
        // BULLET
        // -------------------------------------------------

        if (
          cleanLine.startsWith("- ")
        ) {
          return (
            <div
              className="report-bullet"
              key={index}
            >
              <span className="bullet-dot">
                •
              </span>

              <p>
                {cleanLine.substring(2)}
              </p>
            </div>
          );
        }

        // -------------------------------------------------
        // REPORT TITLE
        // -------------------------------------------------

        const lowerLine =
          cleanLine.toLowerCase();

        if (
          lowerLine.includes(
            "financial intelligence report"
          ) ||
          lowerLine.includes(
            "portfolio intelligence report"
          ) ||
          lowerLine.includes(
            "stock intelligence report"
          )
        ) {
          return (
            <h2
              className="report-title"
              key={index}
            >
              {cleanLine}
            </h2>
          );
        }

        // -------------------------------------------------
        // NORMAL PARAGRAPH
        // -------------------------------------------------

        return (
          <p
            className="report-text"
            key={index}
          >
            {cleanLine}
          </p>
        );
      }
    );
  };

  // =====================================================
  // RECOMMENDATION ICON
  // =====================================================

  const getRecommendationIcon = (
    type
  ) => {

    const value =
      String(
        type || ""
      ).toUpperCase();

    if (
      value.includes("RISK")
    ) {
      return "⚠️";
    }

    if (
      value.includes(
        "DIVERSIFICATION"
      )
    ) {
      return "🧩";
    }

    if (
      value.includes("WATCH") ||
      value.includes("MONITOR")
    ) {
      return "👀";
    }

    if (
      value.includes(
        "PERFORMANCE"
      )
    ) {
      return "📊";
    }

    return "💡";
  };

  // =====================================================
  // RECOMMENDATION SEVERITY
  // =====================================================

  const getRecommendationSeverityClass = (
    severity
  ) => {

    const value =
      String(
        severity || "INFO"
      ).toLowerCase();

    if (value === "high") {
      return "negative";
    }

    if (value === "moderate") {
      return "neutral";
    }

    return "positive";
  };

  // =====================================================
  // RECOMMENDATION CARD
  // =====================================================

  const RecommendationCard = ({
    recommendation,
  }) => {

    if (!recommendation) {
      return null;
    }

    const type =
      recommendation.type ||
      "PORTFOLIO_REVIEW";

    const severity =
      recommendation.severity ||
      "INFO";

    const confidenceValue =
      Number(
        recommendation.confidence
      );

    const confidence =
      Number.isFinite(
        confidenceValue
      )
        ? Math.round(
            confidenceValue <= 1
              ? confidenceValue * 100
              : confidenceValue
          )
        : null;

    const metrics =
      recommendation.supporting_metrics ||
      recommendation.evidence ||
      {};

    return (
      <div
        className={`recommendation-card ${getRecommendationSeverityClass(
          severity
        )}`}
      >

        <div className="recommendation-card-header">

          <div className="recommendation-heading">

            <span className="recommendation-icon">
              {getRecommendationIcon(
                type
              )}
            </span>

            <div>

              <span className="recommendation-type">
                {String(
                  type
                ).replaceAll(
                  "_",
                  " "
                )}
              </span>

              <h3>
                {recommendation.title ||
                  "Portfolio Review"}
              </h3>

            </div>

          </div>

          <span
            className={`recommendation-severity ${getRecommendationSeverityClass(
              severity
            )}`}
          >
            {String(
              severity
            ).toUpperCase()}
          </span>

        </div>

        <div className="recommendation-body">

          <h4>
            Why this matters
          </h4>

          <p>
            {recommendation.rationale ||
              recommendation.reason ||
              "Review the available portfolio evidence."}
          </p>

        </div>

        {Object.keys(
          metrics
        ).length > 0 && (

          <div className="recommendation-evidence">

            <h4>
              Supporting Evidence
            </h4>

            <div className="evidence-list">

              {Object.entries(
                metrics
              ).map(
                ([key, value]) => (

                  <div
                    className="evidence-row"
                    key={key}
                  >

                    <span>
                      {String(key)
                        .replaceAll(
                          "_",
                          " "
                        )
                        .replace(
                          /\b\w/g,
                          (letter) =>
                            letter.toUpperCase()
                        )}
                    </span>

                    <strong>
                      {String(value)}
                    </strong>

                  </div>

                )
              )}

            </div>

          </div>
        )}

        <div className="recommendation-action">

          <h4>
            Suggested Review
          </h4>

          <p>
            {recommendation.suggested_action ||
              recommendation.action ||
              "Review the relevant portfolio metrics before making any decision."}
          </p>

        </div>

        <div className="recommendation-footer">

          {confidence !== null && (

            <span>
              Confidence:{" "}
              <strong>
                {confidence}%
              </strong>
            </span>

          )}

          <span>
            Source:{" "}
            {recommendation.source ||
              "Portfolio Analytics"}
          </span>

        </div>

      </div>
    );
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="app">

        <div className="loading-container">

          <div className="loader" />

          <h2>
            Loading Financial Intelligence...
          </h2>

          <p>
            Analyzing market, portfolio
            and financial news
          </p>

        </div>

      </div>
    );
  }

  // =====================================================
  // ERROR
  // =====================================================

  if (error || !data) {
    return (
      <div className="app">

        <div className="error-container">

          <h2>
            ⚠️ Connection Error
          </h2>

          <p>
            {error ||
              "No data available."}
          </p>

          <button
            onClick={() =>
              fetchAnalysis()
            }
            className="refresh-button"
          >
            ↻ Try Again
          </button>

          <button
            onClick={handleLogout}
            className="refresh-button logout-button"
          >
            Logout
          </button>

        </div>

      </div>
    );
  }

  // =====================================================
  // DATA
  // =====================================================

  const market =
    data.market || {};

  const portfolio =
    data.portfolio || {};

  const news =
    Array.isArray(
      data.news
    )
      ? data.news
      : [];

  const sentiment =
    data.sentiment || {};

  const financialIntelligence =
    data.financial_intelligence ||
    "";

  const overallSignal =
    market.overall_signal ||
    market.trend ||
    "Neutral";

  const marketSignalClass =
    getSignalClass(
      overallSignal
    );

  const newsSignalClass =
    getSignalClass(
      sentiment.overall_sentiment ||
        "Neutral"
    );

  // =====================================================
  // RECOMMENDATIONS
  // =====================================================

  const recommendations =
    Array.isArray(
      data.recommendations
    )
      ? data.recommendations
      : Array.isArray(
          portfolio.recommendations
        )
      ? portfolio.recommendations
      : [];

  const recommendationPolicy =
    data.recommendation_policy ||
    portfolio.recommendation_policy ||
    {};

  const policyStatus =
    recommendationPolicy.status ||
    recommendationPolicy.validation_status ||
    data.validation_status ||
    "unknown";

  // =====================================================
  // ANALYTICS
  // =====================================================

  const analytics =
    portfolio.analytics || {};

  const allocation =
    Array.isArray(
      analytics.allocation
    )
      ? analytics.allocation
      : [];

  const sectorExposure =
    Array.isArray(
      analytics.sector_exposure
    )
      ? analytics.sector_exposure
      : [];

  const concentration =
    analytics.concentration_risk ||
    {};

  // =====================================================
  // DASHBOARD
  // =====================================================

  return (
    <div className="app">

      <div className="dashboard">

        {/* =================================================
            HEADER
        ================================================= */}

        <header className="header">

          <div>

            <h1>
              Financial Intelligence
            </h1>

            <p>
              AI-powered market, portfolio
              and news analysis
            </p>

          </div>

          <div className="header-actions">

            <button
              className="refresh-button"
              onClick={() =>
                fetchAnalysis(true)
              }
              disabled={refreshing}
            >
              {refreshing
                ? "↻ Refreshing..."
                : "↻ Refresh Analysis"}
            </button>

            <button
              className="refresh-button logout-button"
              onClick={handleLogout}
            >
              Logout
            </button>

          </div>

        </header>

        {/* =================================================
            OVERALL OUTLOOK
        ================================================= */}

        <section className="overall-outlook">

          <div>

            <span className="section-label">
              OVERALL MARKET OUTLOOK
            </span>

            <h2
              className={
                marketSignalClass
              }
            >
              {overallSignal}
            </h2>

          </div>

          <div
            className={`outlook-icon ${marketSignalClass}`}
          >
            {marketSignalClass ===
            "negative"
              ? "↘"
              : marketSignalClass ===
                "positive"
              ? "↗"
              : "→"}
          </div>

        </section>

        {/* =================================================
            TOP CARDS
        ================================================= */}

        <section className="top-cards">

          <div className="summary-card">

            <div className="card-top">

              <span>
                Market Signal
              </span>

              <span className="card-icon">
                📈
              </span>

            </div>

            <h2
              className={
                marketSignalClass
              }
            >
              {overallSignal}
            </h2>

            <p>
              Signal Score:{" "}
              <strong>
                {market.signal_score ??
                  "-"}
              </strong>
            </p>

          </div>

          <div className="summary-card">

            <div className="card-top">

              <span>
                Daily Return
              </span>

              <span className="card-icon">
                %
              </span>

            </div>

            <h2
              className={
                Number(
                  market.daily_return
                ) >= 0
                  ? "positive"
                  : "negative"
              }
            >
              {market.daily_return ??
                "-"}
              %
            </h2>

            <p>
              Market Trend:{" "}
              <strong>
                {market.trend || "-"}
              </strong>
            </p>

          </div>

          <div className="summary-card">

            <div className="card-top">

              <span>
                Portfolio Value
              </span>

              <span className="card-icon">
                💰
              </span>

            </div>

            <h2>
              {formatCurrency(
                portfolio.current_value
              )}
            </h2>

            <p>
              Risk:{" "}
              <strong>
                {portfolio.risk_level ||
                  "-"}
              </strong>
            </p>

          </div>

          <div className="summary-card">

            <div className="card-top">

              <span>
                News Sentiment
              </span>

              <span className="card-icon">
                📰
              </span>

            </div>

            <h2
              className={
                newsSignalClass
              }
            >
              {sentiment.overall_sentiment ||
                "-"}
            </h2>

            <p>
              {sentiment.total_articles ||
                0}{" "}
              articles analyzed
            </p>

          </div>

        </section>

        {/* =================================================
            MARKET ANALYSIS
        ================================================= */}

        <section className="panel">

          <div className="panel-header">

            <h2>
              Market Analysis
            </h2>

            <span>
              NSE Market Data
            </span>

          </div>

          <div className="metrics-grid">

            <MetricCard
              label="Trend"
              value={market.trend}
              className={getSignalClass(
                market.trend
              )}
            />

            <MetricCard
              label="Overall Signal"
              value={
                market.overall_signal
              }
              className={getSignalClass(
                market.overall_signal
              )}
            />

            <MetricCard
              label="Signal Score"
              value={
                market.signal_score
              }
              className={
                Number(
                  market.signal_score
                ) < 0
                  ? "negative"
                  : Number(
                      market.signal_score
                    ) > 0
                  ? "positive"
                  : "neutral"
              }
            />

            <MetricCard
              label="Daily Return"
              value={`${market.daily_return ?? "-"}%`}
              className={
                Number(
                  market.daily_return
                ) >= 0
                  ? "positive"
                  : "negative"
              }
            />

            <MetricCard
              label="Volatility"
              value={`${market.volatility ?? "-"}%`}
            />

            <MetricCard
              label="RSI"
              value={market.rsi}
            />

            <MetricCard
              label="RSI Signal"
              value={market.rsi_signal}
              className={getSignalClass(
                market.rsi_signal
              )}
            />

            <MetricCard
              label="MACD"
              value={market.macd}
            />

            <MetricCard
              label="MACD Signal"
              value={market.macd_signal}
            />

            <MetricCard
              label="MACD Trend"
              value={market.macd_trend}
              className={getSignalClass(
                market.macd_trend
              )}
            />

            <MetricCard
              label="NIFTY Close"
              value={formatNumber(
                market.close
              )}
            />

            <MetricCard
              label="Symbol"
              value={market.symbol}
            />

          </div>

          <div className="insight-section">

            <h3>
              Market Insight
            </h3>

            <p>
              {market.market_insight ||
                "No market insight available."}
            </p>

          </div>

        </section>

        {/* =================================================
            PORTFOLIO ANALYSIS
        ================================================= */}

        <section className="panel">

          <div className="panel-header">

            <h2>
              Portfolio Analysis
            </h2>

            <span>
              {portfolio.portfolio_name ||
                "Portfolio"}
            </span>

          </div>

          <div className="portfolio-grid">

            <MetricCard
              label="Invested Value"
              value={formatCurrency(
                portfolio.total_value
              )}
            />

            <MetricCard
              label="Current Value"
              value={formatCurrency(
                portfolio.current_value
              )}
            />

            <MetricCard
              label="Profit / Loss"
              value={formatCurrency(
                portfolio.profit_loss
              )}
              className={
                Number(
                  portfolio.profit_loss
                ) >= 0
                  ? "positive"
                  : "negative"
              }
            />

            <MetricCard
              label="Overall Return"
              value={
                portfolio.overall_return ||
                "-"
              }
              className={
                String(
                  portfolio.overall_return ||
                    ""
                ).includes("-")
                  ? "negative"
                  : "positive"
              }
            />

            <MetricCard
              label="Risk Level"
              value={
                portfolio.risk_level ||
                "-"
              }
            />

            <MetricCard
              label="Timeframe"
              value={
                data.timeframe ||
                portfolio.timeframe ||
                "-"
              }
            />

          </div>

          <div className="intelligence-section">

            <h3>
              Portfolio Intelligence
            </h3>

            <div className="report-box">
              {renderReport(
                portfolio.insight
              )}
            </div>

          </div>

        </section>

        {/* =================================================
            PORTFOLIO ANALYTICS
        ================================================= */}

        {(allocation.length > 0 ||
          sectorExposure.length > 0 ||
          Object.keys(
            concentration
          ).length > 0) && (

          <section className="panel">

            <div className="panel-header">

              <h2>
                Portfolio Analytics
              </h2>

              <span>
                Deterministic Analytics
              </span>

            </div>

            {allocation.length > 0 && (

              <div className="analytics-block">

                <h3>
                  Portfolio Allocation
                </h3>

                <div className="allocation-list">

                  {allocation.map(
                    (item, index) => {

                      const percentage =
                        Number(
                          item.percentage
                        ) || 0;

                      return (
                        <div
                          className="allocation-row"
                          key={
                            item.symbol ||
                            index
                          }
                        >

                          <div className="allocation-info">

                            <strong>
                              {item.symbol}
                            </strong>

                            <span>
                              {formatCurrency(
                                item.value
                              )}
                            </span>

                          </div>

                          <div className="allocation-bar-wrapper">

                            <div
                              className="allocation-bar"
                              style={{
                                width: `${Math.min(
                                  100,
                                  Math.max(
                                    0,
                                    percentage
                                  )
                                )}%`,
                              }}
                            />

                          </div>

                          <strong>
                            {formatNumber(
                              percentage
                            )}
                            %
                          </strong>

                        </div>
                      );
                    }
                  )}

                </div>

              </div>

            )}

            <div className="portfolio-grid">

              <MetricCard
                label="Concentration Level"
                value={
                  concentration.concentration_level ||
                  "-"
                }
              />

              <MetricCard
                label="Largest Holding"
                value={
                  concentration.largest_holding ||
                  "-"
                }
              />

              <MetricCard
                label="Largest Holding %"
                value={
                  concentration.largest_holding_percentage !==
                  undefined
                    ? `${formatNumber(
                        concentration.largest_holding_percentage
                      )}%`
                    : "-"
                }
              />

              <MetricCard
                label="Portfolio Volatility"
                value={
                  analytics.volatility !==
                  undefined
                    ? `${formatNumber(
                        analytics.volatility
                      )}%`
                    : "-"
                }
              />

              <MetricCard
                label="Maximum Drawdown"
                value={
                  analytics.max_drawdown !==
                  undefined
                    ? `${formatNumber(
                        analytics.max_drawdown
                      )}%`
                    : "-"
                }
              />

              <MetricCard
                label="Analytics Risk"
                value={
                  analytics.risk_level ||
                  portfolio.risk_level ||
                  "-"
                }
              />

            </div>

            {sectorExposure.length > 0 && (

              <div className="analytics-block">

                <h3>
                  Sector Exposure
                </h3>

                <div className="sector-list">

                  {sectorExposure.map(
                    (sector, index) => (

                      <div
                        className="sector-row"
                        key={
                          sector.sector ||
                          index
                        }
                      >

                        <div>

                          <strong>
                            {sector.sector}
                          </strong>

                          <span>
                            {formatCurrency(
                              sector.value
                            )}
                          </span>

                        </div>

                        <strong>
                          {formatNumber(
                            sector.percentage
                          )}
                          %
                        </strong>

                      </div>

                    )
                  )}

                </div>

              </div>

            )}

          </section>

        )}

        {/* =================================================
            FINANCIAL NEWS
        ================================================= */}

        <section className="panel">

          <div className="panel-header">

            <div>

              <h2>
                Financial News
              </h2>

              <span className="panel-subtitle">
                Latest Market News
              </span>

            </div>

            <span
              className={`sentiment-label ${newsSignalClass}`}
            >
              {sentiment.overall_sentiment ||
                "Neutral"}
            </span>

          </div>

          <div className="news-summary">

            <MetricCard
              label="Positive"
              value={
                sentiment.positive_count ??
                0
              }
              className="positive"
            />

            <MetricCard
              label="Negative"
              value={
                sentiment.negative_count ??
                0
              }
              className="negative"
            />

            <MetricCard
              label="Neutral"
              value={
                sentiment.neutral_count ??
                0
              }
            />

            <MetricCard
              label="Total Articles"
              value={
                sentiment.total_articles ??
                news.length
              }
            />

          </div>

          <div className="news-list">

            {news.length === 0 ? (

              <p className="empty-message">
                No financial news available.
              </p>

            ) : (

              news.map(
                (article, index) => (

                  <article
                    className="news-item"
                    key={
                      article.url ||
                      article.title ||
                      index
                    }
                  >

                    <div className="news-meta">

                      <span className="news-source">
                        {article.source ||
                          "Unknown Source"}
                      </span>

                      <span
                        className={`news-sentiment ${getSignalClass(
                          article.sentiment
                        )}`}
                      >
                        {article.sentiment ||
                          "Neutral"}
                      </span>

                    </div>

                    <h3>
                      {article.title}
                    </h3>

                    {article.description && (
                      <p>
                        {article.description}
                      </p>
                    )}

                    <div className="news-footer">

                      <span>
                        {formatDate(
                          article.published_at
                        )}
                      </span>

                      {article.url && (
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Read Article →
                        </a>
                      )}

                    </div>

                  </article>

                )
              )

            )}

          </div>

        </section>

        {/* =================================================
            AI FINANCIAL INTELLIGENCE
        ================================================= */}

        <section className="panel ai-panel">

          <div className="panel-header">

            <div>

              <h2>
                AI Financial Intelligence
              </h2>

              <span>
                Powered by Ollama
              </span>

            </div>

            <span className="ai-grounded-badge">
              Grounded Analysis
            </span>

          </div>

          <div className="report-box ai-report">
            {renderReport(
              financialIntelligence
            )}
          </div>

        </section>

        {/* =================================================
            AI RECOMMENDATIONS
        ================================================= */}

        <section className="panel recommendations-panel">

          <div className="panel-header">

            <div>

              <h2>
                AI Recommendations
              </h2>

              <span className="panel-subtitle">
                Evidence-based decision support
              </span>

            </div>

            <span
              className={`policy-status ${
                String(
                  policyStatus
                ).toLowerCase() ===
                "passed"
                  ? "passed"
                  : ""
              }`}
            >
              {String(
                policyStatus
              ).toLowerCase() ===
              "passed"
                ? "✓ Policy Validated"
                : "Policy Review"}
            </span>

          </div>

          <div className="recommendation-disclaimer">

            <span>
              🛡️
            </span>

            <p>
              These recommendations identify
              evidence-based areas for review.
              They are not direct buy, sell or
              hold instructions and should not be
              treated as investment advice.
            </p>

          </div>

          {recommendations.length === 0 ? (

            <div className="empty-recommendations">

              <div className="empty-icon">
                ✓
              </div>

              <h3>
                No Review Alerts
              </h3>

              <p>
                No recommendation threshold
                was triggered by the currently
                supplied portfolio analytics.
              </p>

            </div>

          ) : (

            <div className="recommendations-grid">

              {recommendations.map(
                (
                  recommendation,
                  index
                ) => (

                  <RecommendationCard
                    key={
                      recommendation.id ||
                      `${recommendation.type}-${index}`
                    }
                    recommendation={
                      recommendation
                    }
                  />

                )
              )}

            </div>

          )}

          {(recommendationPolicy.total_cards !==
            undefined ||
            recommendationPolicy.approved_cards !==
              undefined ||
            recommendationPolicy.blocked_count !==
              undefined) && (

            <div className="recommendation-summary">

              <div>

                <span>
                  Total Cards
                </span>

                <strong>
                  {recommendationPolicy.total_cards ??
                    recommendations.length}
                </strong>

              </div>

              <div>

                <span>
                  Approved
                </span>

                <strong>
                  {recommendationPolicy.approved_cards ??
                    recommendations.length}
                </strong>

              </div>

              <div>

                <span>
                  Blocked
                </span>

                <strong>
                  {recommendationPolicy.blocked_count ??
                    0}
                </strong>

              </div>

            </div>

          )}

        </section>

        {/* =================================================
            FOOTER
        ================================================= */}

        <footer className="footer">

          <h3>
            Financial Intelligence Platform
          </h3>

          <p>
            Market data • Portfolio analytics
            • Financial news • AI insights
            • Evidence-based recommendations
          </p>

        </footer>

      </div>

    </div>
  );
}


// =========================================================
// REUSABLE METRIC CARD
// =========================================================

function MetricCard({
  label,
  value,
  className = "",
}) {
  return (
    <div className="metric-card">

      <span className="metric-label">
        {label}
      </span>

      <strong
        className={`metric-value ${className}`}
      >
        {value ?? "-"}
      </strong>

    </div>
  );
}


export default App;