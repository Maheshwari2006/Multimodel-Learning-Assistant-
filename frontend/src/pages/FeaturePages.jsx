
import { useState } from "react";
import api from "../api/api";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";

const featureInfo = {
  upload: {
    title: "Upload Learning Material",
    description: "Upload a file to your learning assistant.",
  },
  chat: {
    title: "AI Chat",
    description: "Ask questions using your learning material as context.",
  },
  summary: {
    title: "Text Summary",
    description: "Generate a summary from your learning material.",
  },
  quiz: {
    title: "Quiz Generator",
    description: "Generate a quiz from your learning material.",
  },
  studyPlan: {
    title: "Study Plan",
    description: "Create a study plan for your topic.",
  },
  recommendations: {
    title: "Learning Recommendations",
    description:
      "Get recommendations based on your quiz scores and completed topics.",
  },
};

function FeaturePage({ type }) {
  const info = featureInfo[type];

  const [text, setText] = useState("");
  const [context, setContext] = useState("");
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [topic, setTopic] = useState("");
  const [days, setDays] = useState(7);
  const [scores, setScores] = useState('{"JavaScript": 70}');
  const [completedTopics, setCompletedTopics] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);

    try {
      let response;

      if (type === "upload") {
        if (!file) {
          throw new Error("Please select a file first.");
        }

        const formData = new FormData();
        formData.append("file", file);

        response = await api.post("/upload/", formData);
      } else if (type === "chat") {
        if (!text.trim()) {
          throw new Error("Please enter your question.");
        }

        response = await api.post("/chat/query", {
          message: text.trim(),
          context: context.trim() || undefined,
        });
      } else if (type === "summary") {
        if (!text.trim()) {
          throw new Error("Please enter text to summarize.");
        }

        response = await api.post("/summary/", {
          text: text.trim(),
        });
      } else if (type === "quiz") {
        if (!text.trim()) {
          throw new Error("Please enter learning material.");
        }

        // Updated Quiz API expects JSON, not a query parameter.
        response = await api.post("/quiz", {
          text: text.trim(),
        });
      } else if (type === "studyPlan") {
        if (!topic.trim()) {
          throw new Error("Please enter a study topic.");
        }

        response = await api.post("/study-plan/", {
          topic: topic.trim(),
          days: Number(days),
        });
      } else if (type === "recommendations") {
        let parsedScores;

        try {
          parsedScores = JSON.parse(scores);
        } catch {
          throw new Error(
            'Quiz scores must be valid JSON, for example {"JavaScript": 70}.'
          );
        }

        response = await api.post("/recommendation/", {
          quiz_scores: parsedScores,
          completed_topics: completedTopics
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
        });
      }

      setResult(response.data);
    } catch (err) {
      console.error(`${type} error:`, err);

      setError(
        err.response?.data?.detail ||
          err.message ||
          "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: "100%",
    padding: "13px 15px",
    marginTop: "8px",
    marginBottom: "18px",
    border: "1px solid #d5dced",
    borderRadius: "10px",
    boxSizing: "border-box",
    fontSize: "15px",
    fontFamily: "inherit",
    outlineColor: "#7055ef",
    background: "#ffffff",
  };

  const labelStyle = {
    display: "block",
    fontWeight: 600,
    color: "#24304f",
  };

  return (
    <div style={{ minHeight: "100vh", background: "#f4f6fc" }}>
      <Navbar />

      <div style={{ display: "flex", alignItems: "stretch" }}>
        <Sidebar />

        <main
          style={{
            flex: 1,
            minWidth: 0,
            padding: "clamp(18px, 4vw, 40px)",
            minHeight: "100vh",
            background:
              "radial-gradient(circle at top right, #e8eaff, transparent 35%), #f4f6fc",
          }}
        >
          <div style={{ maxWidth: "900px", margin: "0 auto" }}>
            <div style={{ marginBottom: "26px" }}>
              <p
                style={{
                  color: "#7557ef",
                  fontSize: "13px",
                  fontWeight: 700,
                  letterSpacing: "1.5px",
                  textTransform: "uppercase",
                  marginBottom: "8px",
                }}
              >
                Your AI Learning Space
              </p>

              <h1
                style={{
                  color: "#172449",
                  fontSize: "clamp(27px, 4vw, 36px)",
                  margin: "0 0 10px",
                }}
              >
                {info.title}
              </h1>

              <p style={{ color: "#6b7692", lineHeight: 1.7, margin: 0 }}>
                {info.description}
              </p>
            </div>

            <form
              onSubmit={handleSubmit}
              style={{
                maxWidth: "760px",
                padding: "clamp(20px, 4vw, 32px)",
                background: "rgba(255,255,255,0.96)",
                border: "1px solid #e5e9f5",
                borderRadius: "20px",
                boxShadow: "0 15px 45px rgba(36,48,100,0.08)",
              }}
            >
              {type === "upload" && (
                <>
                  <label style={labelStyle}>Select learning material</label>

                  <input
                    type="file"
                    required
                    accept=".pdf,.txt,.doc,.docx"
                    onChange={(e) =>
                      setFile(e.target.files?.[0] || null)
                    }
                    style={inputStyle}
                  />

                  <p style={{ color: "#78839c", fontSize: "13px" }}>
                    Upload a supported file. The current upload endpoint
                    saves the file; it does not automatically extract text
                    for Chat or Quiz.
                  </p>
                </>
              )}

              {type === "chat" && (
                <>
                  <label style={labelStyle}>Your question</label>

                  <textarea
                    required
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Example: What is task 3?"
                    rows={3}
                    style={inputStyle}
                  />

                  <label style={labelStyle}>
                    Learning material / context (optional)
                  </label>

                  <textarea
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="Paste the relevant notes, assignment, or textbook content here..."
                    rows={7}
                    style={inputStyle}
                  />

                  <p style={{ color: "#78839c", fontSize: "13px" }}>
                    For document-specific answers, include the relevant
                    material above. Without it, the AI answers as a general
                    assistant.
                  </p>
                </>
              )}

              {type === "summary" && (
                <>
                  <label style={labelStyle}>Text to summarize</label>

                  <textarea
                    required
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Paste your study material here..."
                    rows={9}
                    style={inputStyle}
                  />
                </>
              )}

              {type === "quiz" && (
                <>
                  <label style={labelStyle}>Learning material</label>

                  <textarea
                    required
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Paste your notes, chapter, or assignment here..."
                    rows={9}
                    style={inputStyle}
                  />

                  <p style={{ color: "#78839c", fontSize: "13px" }}>
                    The quiz will be generated from the text you provide.
                  </p>
                </>
              )}

              {type === "studyPlan" && (
                <>
                  <label style={labelStyle}>Study topic</label>

                  <input
                    required
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g. Python programming"
                    style={inputStyle}
                  />

                  <label style={labelStyle}>Number of days</label>

                  <input
                    type="number"
                    min="1"
                    max="365"
                    required
                    value={days}
                    onChange={(e) => setDays(e.target.value)}
                    style={inputStyle}
                  />
                </>
              )}

              {type === "recommendations" && (
                <>
                  <label style={labelStyle}>Quiz scores (JSON)</label>

                  <textarea
                    required
                    value={scores}
                    onChange={(e) => setScores(e.target.value)}
                    rows={3}
                    style={inputStyle}
                  />

                  <label style={labelStyle}>
                    Completed topics (comma-separated)
                  </label>

                  <input
                    value={completedTopics}
                    onChange={(e) => setCompletedTopics(e.target.value)}
                    placeholder="Python, Variables, Functions"
                    style={inputStyle}
                  />
                </>
              )}

              {error && (
                <div
                  role="alert"
                  style={{
                    color: "#b42338",
                    background: "#fff0f1",
                    border: "1px solid #ffd5d8",
                    borderRadius: "10px",
                    padding: "12px 14px",
                    marginBottom: "18px",
                  }}
                >
                  {String(error)}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: "100%",
                  padding: "14px 20px",
                  background: loading
                    ? "#9b91df"
                    : "linear-gradient(100deg, #4387ff, #7932f5)",
                  color: "white",
                  border: "none",
                  borderRadius: "11px",
                  cursor: loading ? "wait" : "pointer",
                  fontSize: "15px",
                  fontWeight: 700,
                  boxShadow: "0 8px 20px rgba(103,66,245,0.2)",
                }}
              >
                {loading
                  ? "Processing..."
                  : type === "chat"
                    ? "Ask AI →"
                    : type === "quiz"
                      ? "Generate Quiz →"
                      : type === "upload"
                        ? "Upload Material →"
                        : "Submit →"}
              </button>
            </form>

            {result !== null && (
              <section
                aria-live="polite"
                style={{
                  marginTop: "24px",
                  padding: "clamp(18px, 4vw, 28px)",
                  background: "#ffffff",
                  border: "1px solid #e5e9f5",
                  borderRadius: "18px",
                  boxShadow: "0 12px 35px rgba(36,48,100,0.07)",
                }}
              >
                <h2 style={{ color: "#172449", marginTop: 0 }}>Result</h2>

                {type === "chat" && result.response ? (
                  <div
                    style={{
                      color: "#35415e",
                      lineHeight: 1.8,
                      whiteSpace: "pre-wrap",
                      overflowWrap: "anywhere",
                    }}
                  >
                    {result.response}
                  </div>
                ) : (
                  <pre
                    style={{
                      margin: 0,
                      color: "#35415e",
                      whiteSpace: "pre-wrap",
                      overflowWrap: "anywhere",
                      fontFamily: "inherit",
                      lineHeight: 1.8,
                    }}
                  >
                    {typeof result === "string"
                      ? result
                      : JSON.stringify(result, null, 2)}
                  </pre>
                )}
              </section>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default FeaturePage;
