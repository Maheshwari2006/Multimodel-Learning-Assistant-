
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../../api/authApi";
import "./AuthBase.css";
import "./Auth.css";

export default function Register() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await registerUser({ username, email, password });
      setSuccess("Account created successfully! Redirecting to login...");

      window.setTimeout(() => navigate("/"), 1200);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : "Registration failed. Please check your details and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand-icon" aria-hidden="true">✦</div>
        <h1>Create account</h1>
        <p className="auth-subtitle">
          Start your smarter learning journey
        </p>

        <form className="auth-form" onSubmit={handleRegister}>
          <input
            className="auth-input"
            type="text"
            placeholder="Username"
            aria-label="Username"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

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
              placeholder="Create password"
              aria-label="Create password"
              autoComplete="new-password"
              minLength={6}
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
          {success && <p className="auth-success">{success}</p>}

          <button
            className="auth-submit"
            type="submit"
            disabled={loading || Boolean(success)}
          >
            {loading ? "Creating account..." : "Create account →"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/">Sign in</Link>
        </p>
      </section>

      <section className="auth-visual">
        <div className="auth-visual-heading">
          <h2>
            Learn smarter.
            <span>Achieve more.</span>
          </h2>
          <p>YOUR PERSONAL AI LEARNING SPACE</p>
        </div>

        <div className="auth-illustration">
          <div className="auth-orbit" />
          <div className="auth-orbit auth-orbit-two" />
          <div className="auth-book" aria-hidden="true">📚</div>

          <div className="auth-feature feature-one">📄 Upload Materials</div>
          <div className="auth-feature feature-two">💬 AI Chat</div>
          <div className="auth-feature feature-three">📝 Summary</div>
          <div className="auth-feature feature-four">🗂️ Flashcards</div>
          <div className="auth-feature feature-five">🧠 Quiz</div>
          <div className="auth-feature feature-six">💡 Study Plan</div>
        </div>

        <p className="auth-visual-note">
          Turn your study material into summaries, quizzes, flashcards,
          and a personalized study plan.
        </p>
      </section>
    </main>
  );
}
