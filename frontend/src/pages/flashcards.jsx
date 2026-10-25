
import { useState } from "react";
import api from "../api/api";

export default function Flashcards() {
  const [text, setText] = useState("");
  const [pdfFile, setPdfFile] = useState(null);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [revealed, setRevealed] = useState({});

  // Generate flashcards from manually entered notes
  const generateFlashcards = async (event) => {
    event.preventDefault();

    if (!text.trim()) {
      setError("Please enter your study material first.");
      setSuccess("");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");
    setCards([]);
    setRevealed({});

    try {
      const response = await api.post("/flashcards", null, {
        params: { text: text.trim() },
      });

      const data = response.data;
      const generated = Array.isArray(data)
        ? data
        : data.flashcards ?? data.cards ?? [];

      if (!Array.isArray(generated) || generated.length === 0) {
        setError("No flashcards were returned. Please try different notes.");
        return;
      }

      setCards(generated);
      setSuccess("Flashcards generated successfully!");
    } catch (err) {
      console.error("Flashcard generation failed:", err);
      setError(
        err.response?.data?.detail ||
          "Unable to generate flashcards. Check that FastAPI and Ollama are running."
      );
    } finally {
      setLoading(false);
    }
  };

  // Generate flashcards directly from an uploaded PDF
  const generateFromPDF = async (event) => {
    event.preventDefault();

    if (!pdfFile) {
      setError("Please select a PDF file first.");
      setSuccess("");
      return;
    }

    if (
      !pdfFile.name.toLowerCase().endsWith(".pdf") ||
      (pdfFile.type && pdfFile.type !== "application/pdf")
    ) {
      setError("Please select a valid PDF file.");
      setSuccess("");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");
    setCards([]);
    setRevealed({});

    try {
      const formData = new FormData();
      formData.append("file", pdfFile);

      const response = await api.post("/upload/flashcards", formData);

      const generated = response.data?.flashcards;

      if (!Array.isArray(generated) || generated.length === 0) {
        setError("The PDF was processed, but no flashcards were returned.");
        return;
      }

      setCards(generated);
      setSuccess(
        `Generated ${generated.length} flashcards from ${pdfFile.name}.`
      );
    } catch (err) {
      console.error("PDF flashcard generation failed:", err);
      setError(
        err.response?.data?.detail ||
          "Unable to generate flashcards from this PDF. Check the backend terminal."
      );
    } finally {
      setLoading(false);
    }
  };

  const getQuestion = (card) =>
    card.question ?? card.front ?? card.term ?? "Question";

  const getAnswer = (card) =>
    card.answer ?? card.back ?? card.definition ?? "No answer provided.";

  // Toggle the answer for a particular card
  const toggleCard = (index) => {
    setRevealed((previous) => ({
      ...previous,
      [index]: !previous[index],
    }));
  };

  const buttonStyle = {
    marginTop: 14,
    padding: "12px 22px",
    background: loading ? "#9ca3af" : "#2563eb",
    color: "white",
    border: "none",
    borderRadius: 8,
    cursor: loading ? "wait" : "pointer",
    fontSize: 16,
    fontWeight: 600,
  };

  return (
    <div
      style={{
        maxWidth: 1000,
        margin: "0 auto",
        padding: 24,
        color: "#1f2937",
      }}
    >
      <h1>📚 Flashcards</h1>
      <p>
        Generate question-and-answer flashcards from your notes or PDF study
        materials.
      </p>

      {/* PDF upload section */}
      <section
        style={{
          marginTop: 24,
          padding: 20,
          border: "1px solid #d1d5db",
          borderRadius: 12,
          background: "#f9fafb",
        }}
      >
        <h2>📄 Generate from PDF</h2>
        <p>Select a PDF containing your study material.</p>

        <form onSubmit={generateFromPDF}>
          <label
            htmlFor="pdf-file"
            style={{
              display: "block",
              fontWeight: 600,
              marginBottom: 10,
            }}
          >
            Choose PDF file
          </label>

          <input
            id="pdf-file"
            type="file"
            accept=".pdf,application/pdf"
            disabled={loading}
            onChange={(event) => {
              setPdfFile(event.target.files?.[0] || null);
              setError("");
              setSuccess("");
            }}
            style={{
              display: "block",
              maxWidth: "100%",
              marginBottom: 8,
            }}
          />

          {pdfFile && (
            <p style={{ fontSize: 14, color: "#4b5563" }}>
              Selected: {pdfFile.name}
            </p>
          )}

          <button type="submit" disabled={loading} style={buttonStyle}>
            {loading ? "Generating..." : "Upload PDF & Generate"}
          </button>
        </form>
      </section>

      {/* Manual notes section */}
      <section style={{ marginTop: 32 }}>
        <h2>📝 Generate from Notes</h2>

        <form onSubmit={generateFlashcards}>
          <label
            htmlFor="study-material"
            style={{
              display: "block",
              fontWeight: 600,
              marginBottom: 8,
            }}
          >
            Enter your notes or study material
          </label>

          <textarea
            id="study-material"
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Paste your notes here..."
            rows={8}
            disabled={loading}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: 14,
              border: "1px solid #d1d5db",
              borderRadius: 8,
              fontSize: 16,
              resize: "vertical",
            }}
          />

          <button type="submit" disabled={loading} style={buttonStyle}>
            {loading ? "Generating..." : "Generate from Notes"}
          </button>
        </form>
      </section>

      {/* Status messages */}
      {error && (
        <p
          role="alert"
          style={{
            color: "#dc2626",
            marginTop: 20,
            padding: 12,
            background: "#fef2f2",
            borderRadius: 8,
          }}
        >
          {error}
        </p>
      )}

      {success && (
        <p
          role="status"
          style={{
            color: "#166534",
            marginTop: 20,
            padding: 12,
            background: "#f0fdf4",
            borderRadius: 8,
          }}
        >
          {success}
        </p>
      )}

      {/* Generated flashcards */}
      {cards.length > 0 && (
        <section style={{ marginTop: 32 }}>
          <h2>Generated Flashcards ({cards.length})</h2>
          <p>Click any card to reveal or hide its answer.</p>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(min(100%, 240px), 1fr))",
              gap: 16,
            }}
          >
            {cards.map((card, index) => (
              <button
                type="button"
                key={card.id ?? index}
                onClick={() => toggleCard(index)}
                aria-expanded={Boolean(revealed[index])}
                style={{
                  minHeight: 170,
                  padding: 20,
                  textAlign: "left",
                  border: revealed[index]
                    ? "2px solid #2563eb"
                    : "1px solid #d1d5db",
                  borderRadius: 12,
                  background: revealed[index] ? "#eff6ff" : "white",
                  color: "#1f2937",
                  cursor: "pointer",
                  overflowWrap: "anywhere",
                }}
              >
                <small>
                  CARD {index + 1} ·{" "}
                  {revealed[index] ? "ANSWER" : "QUESTION"}
                </small>

                <h3>
                  {revealed[index]
                    ? getAnswer(card)
                    : getQuestion(card)}
                </h3>

                <small>
                  {revealed[index]
                    ? "Click to hide answer"
                    : "Click to reveal answer"}
                </small>
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
