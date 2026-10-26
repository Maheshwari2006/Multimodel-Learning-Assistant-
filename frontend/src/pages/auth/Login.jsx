
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser } from "../../api/authApi";
import "./AuthBase.css";
import "./Auth.css";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await loginUser(email, password);

      if (!data?.access_token) {
        throw new Error("No access token received from the server.");
      }

      localStorage.setItem("token", data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(
        typeof err.response?.data?.detail === "string"
          ? err.response.data.detail
          : err.message || "Login failed. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand-icon" aria-hidden="true">✦</div>
        <h1>Welcome back</h1>
        <p className="auth-subtitle">Continue your learning journey</p>

        <form className="auth-form" onSubmit={handleLogin}>
          <input
            className="auth-input"
            type="email"
            placeholder="Email address"
            aria-label="Email address"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <div className="auth-password-wrap">
            <input
              className="auth-input"
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              aria-label="Password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button
              className="auth-eye"
              type="button"
              onClick={() => setShowPassword((value) => !value)}
            >
              {showPassword ? "HIDE" : "SHOW"}
            </button>
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button className="auth-submit" type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in →"}
          </button>
        </form>

        <div className="auth-divider">Your learning starts here</div>

        <p className="auth-switch">
          New to learning? <Link to="/register">Create account</Link>
        </p>
      </section>

      <AuthVisual />
    </main>
  );
}

function AuthVisual() {
  return (
    <section className="auth-visual">
      <div className="auth-visual-heading">
        <h2>
          Multimodel
          <span>Learning Assistant</span>
        </h2>
        <p>UPLOAD · LEARN · PRACTICE · GROW</p>
      </div>

      <div className="auth-illustration">
        <div className="auth-orbit" />
        <div className="auth-orbit auth-orbit-two" />
        <div className="auth-book" aria-hidden="true">📖</div>

        <div className="auth-feature feature-one">📄 Upload Materials</div>
        <div className="auth-feature feature-two">💬 AI Chat</div>
        <div className="auth-feature feature-three">📝 Summary</div>
        <div className="auth-feature feature-four">🗂️ Flashcards</div>
        <div className="auth-feature feature-five">🧠 Quiz</div>
        <div className="auth-feature feature-six">💡 Study Plan</div>
      </div>

      <p className="auth-visual-note">
        One smart space to understand concepts, practise your skills,
        and build a personalized learning plan.
      </p>
    </section>
  );
}
