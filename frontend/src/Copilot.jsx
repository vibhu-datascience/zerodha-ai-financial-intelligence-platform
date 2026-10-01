import { useEffect, useRef, useState } from "react";

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8001"
).replace(/\/$/, "");

const EXAMPLE_QUESTIONS = [
  "What is my total invested amount?",
  "What is my current portfolio value?",
  "What is the current value of RELIANCE.NS?",
  "What is the profit or loss of RELIANCE.NS?",
];

function Copilot() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const askCopilot = async (questionText) => {
    const cleanQuestion = questionText.trim();

    if (!cleanQuestion || loading) {
      return;
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
      setError(
        "Your session has expired. Please login again."
      );
      return;
    }

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: cleanQuestion,
      },
    ]);

    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const params = new URLSearchParams({
        question: cleanQuestion,
        portfolio_name: "Growth Portfolio",
        timeframe: "1Y",
      });

      const response = await fetch(
        `${API_BASE_URL}/ai/copilot?${params.toString()}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("username");

        throw new Error(
          "Your session has expired. Please login again."
        );
      }

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail ||
            "AI Copilot request failed."
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            result.answer ||
            "I could not generate an answer.",
          validationStatus:
            result.validation_status ||
            "unknown",
          validationErrors:
            Array.isArray(
              result.validation_errors
            )
              ? result.validation_errors
              : [],
        },
      ]);
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Unable to connect to AI Financial Copilot."
      );
    } finally {
      setLoading(false);

      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    askCopilot(question);
  };

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      askCopilot(question);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError("");
    setQuestion("");

    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  return (
    <section className="panel copilot-panel">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="copilot-header">

        <div className="copilot-title-area">

          <div className="copilot-avatar">
            ✦
          </div>

          <div>

            <h2>
              AI Financial Copilot
            </h2>

            <div className="copilot-status">
              <span className="status-dot" />
              Portfolio Grounded
            </div>

          </div>

        </div>

        {messages.length > 0 && (

          <button
            type="button"
            className="copilot-clear-button"
            onClick={clearChat}
          >
            + New Chat
          </button>

        )}

      </div>

      {/* =================================================
          CHAT AREA
      ================================================= */}

      <div className="copilot-chat">

        {messages.length === 0 && (

          <div className="copilot-welcome">

            <div className="copilot-welcome-icon">
              ✦
            </div>

            <h3>
              How can I help with your portfolio?
            </h3>

            <p>
              Ask questions about your holdings,
              portfolio value, performance,
              risk or portfolio analytics.
            </p>

            <div className="copilot-suggestions">

              {EXAMPLE_QUESTIONS.map(
                (example, index) => (

                  <button
                    key={index}
                    type="button"
                    className="copilot-suggestion"
                    onClick={() =>
                      askCopilot(example)
                    }
                    disabled={loading}
                  >
                    <span>{example}</span>
                    <span className="suggestion-arrow">
                      →
                    </span>
                  </button>

                )
              )}

            </div>

          </div>

        )}

        {messages.map(
          (message, index) => (

            <div
              key={index}
              className={`chat-message ${
                message.role === "user"
                  ? "user-message"
                  : "assistant-message"
              }`}
            >

              {message.role ===
                "assistant" && (

                <div className="message-avatar">
                  ✦
                </div>

              )}

              <div className="message-content">

                <div className="message-role">
                  {message.role === "user"
                    ? "You"
                    : "AI Copilot"}
                </div>

                <div className="message-bubble">
                  {message.content}
                </div>

                {message.role ===
                  "assistant" &&
                  message.validationStatus ===
                    "passed" && (

                  <div className="message-validation">
                    <span>✓</span>
                    Grounded & validated
                  </div>

                )}

                {message.role ===
                  "assistant" &&
                  message.validationStatus !==
                    "passed" &&
                  message.validationStatus !==
                    "unknown" && (

                  <div className="message-validation warning">
                    ⚠ Validation status:{" "}
                    {message.validationStatus}
                  </div>

                )}

              </div>

            </div>

          )
        )}

        {loading && (

          <div className="chat-message assistant-message">

            <div className="message-avatar">
              ✦
            </div>

            <div className="message-content">

              <div className="message-role">
                AI Copilot
              </div>

              <div className="message-bubble typing-bubble">

                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />

              </div>

            </div>

          </div>

        )}

        <div ref={messagesEndRef} />

      </div>

      {/* =================================================
          ERROR
      ================================================= */}

      {error && (

        <div className="copilot-error">
          <span>⚠</span>
          {error}
        </div>

      )}

      {/* =================================================
          INPUT
      ================================================= */}

      <form
        className="copilot-input-area"
        onSubmit={handleSubmit}
      >

        <div className="copilot-input-wrapper">

          <input
            ref={inputRef}
            type="text"
            value={question}
            onChange={(event) =>
              setQuestion(
                event.target.value
              )
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about your portfolio..."
            disabled={loading}
            autoComplete="off"
          />

          <button
            type="submit"
            disabled={
              loading ||
              !question.trim()
            }
            className="copilot-send-button"
            aria-label="Send message"
          >
            {loading ? (
              <span className="send-spinner">
                •••
              </span>
            ) : (
              "↑"
            )}
          </button>

        </div>

        <div className="copilot-input-footer">

          <span>
            ↵ Enter to send
          </span>

          <span>
            Portfolio-grounded AI
          </span>

        </div>

        <p className="copilot-disclaimer">
          AI Financial Copilot uses your portfolio
          data and validated analytics. It does not
          provide direct buy or sell instructions.
        </p>

      </form>

    </section>
  );
}

export default Copilot;