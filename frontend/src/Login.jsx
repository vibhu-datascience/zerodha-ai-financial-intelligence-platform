import { useState } from "react";

const API_URL = (
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8001"
).replace(/\/$/, "");

function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const resetMessages = () => {
    setError("");
    setSuccess("");
  };

  const switchMode = (registerMode) => {
    setIsRegister(registerMode);
    setUsername("");
    setPassword("");
    setConfirmPassword("");
    resetMessages();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (isRegister) {
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }

      if (username.trim().length < 3) {
        setError("Username must contain at least 3 characters.");
        return;
      }

      if (password.length < 6) {
        setError("Password must contain at least 6 characters.");
        return;
      }
    }

    setLoading(true);

    try {
      const endpoint = isRegister
        ? "/auth/register"
        : "/auth/login";

      const response = await fetch(
        `${API_URL}${endpoint}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: username.trim(),
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          (isRegister
            ? "Registration failed."
            : "Login failed.")
        );
      }

      /*
       * Registration API also returns a JWT.
       * So the user can enter the dashboard
       * immediately after creating the account.
       */
      localStorage.setItem(
        "access_token",
        data.access_token
      );

      localStorage.setItem(
        "username",
        username.trim()
      );

      if (isRegister) {
        setSuccess(
          "Account created successfully. Opening your dashboard..."
        );
      }

      onLogin(data.access_token);

    } catch (error) {
      setError(
        error.message ||
        "Unable to connect to the server."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">

      <div className="login-card">

        <div className="login-header">

          <div className="login-logo">
            Z
          </div>

          <h1>
            Zerodha AI
          </h1>

          <p>
            Financial Intelligence Platform
          </p>

        </div>

        {/* Login / Register Toggle */}

        <div className="auth-toggle">

          <button
            type="button"
            className={!isRegister ? "active" : ""}
            onClick={() => switchMode(false)}
          >
            Login
          </button>

          <button
            type="button"
            className={isRegister ? "active" : ""}
            onClick={() => switchMode(true)}
          >
            Create Account
          </button>

        </div>

        <div className="auth-title">

          <h2>
            {isRegister
              ? "Create your account"
              : "Welcome back"}
          </h2>

          <p>
            {isRegister
              ? "Start managing your portfolio with AI-powered insights."
              : "Sign in to access your financial intelligence dashboard."}
          </p>

        </div>

        <form onSubmit={handleSubmit}>

          {/* Username */}

          <div className="login-field">

            <label>
              Username
            </label>

            <input
              type="text"
              value={username}
              onChange={(event) =>
                setUsername(event.target.value)
              }
              placeholder="Enter username"
              autoComplete="username"
              required
            />

          </div>

          {/* Password */}

          <div className="login-field">

            <label>
              Password
            </label>

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder={
                isRegister
                  ? "Minimum 6 characters"
                  : "Enter password"
              }
              autoComplete={
                isRegister
                  ? "new-password"
                  : "current-password"
              }
              required
            />

          </div>

          {/* Confirm Password */}

          {isRegister && (

            <div className="login-field">

              <label>
                Confirm Password
              </label>

              <input
                type="password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                placeholder="Re-enter password"
                autoComplete="new-password"
                required
              />

            </div>

          )}

          {/* Error */}

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          {/* Success */}

          {success && (
            <div className="login-success">
              {success}
            </div>
          )}

          {/* Submit */}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading
              ? isRegister
                ? "Creating account..."
                : "Signing in..."
              : isRegister
                ? "Create Account"
                : "Login"}
          </button>

        </form>

        {/* Bottom switch */}

        <div className="auth-switch">

          {isRegister ? (
            <>
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => switchMode(false)}
              >
                Login
              </button>
            </>
          ) : (
            <>
              Don't have an account?{" "}
              <button
                type="button"
                onClick={() => switchMode(true)}
              >
                Create Account
              </button>
            </>
          )}

        </div>

        <div className="login-footer">
          AI-powered financial decision support
        </div>

      </div>

    </div>
  );
}

export default Login;
