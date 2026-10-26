# Multimodel Learning Assistant

React + Vite frontend, FastAPI + SQLite backend, Ollama (`llama3`) for the AI.
One uploaded document powers: **Upload → Extract → Chat → Summary → Quiz → Flashcards → Study Plan → Recommendations**.

## Run it

```bash
# 1. Ollama
ollama pull llama3            # and keep `ollama serve` running

# 2. Backend (from the project root)
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload                       # http://127.0.0.1:8000/docs

# 3. Frontend
cd frontend && npm install && npm run dev               # http://localhost:5173
```

Optional environment variables: `OLLAMA_MODEL` (default `llama3`), `OLLAMA_NUM_CTX` (8192), `MAX_UPLOAD_MB` (25),
`SECRET_KEY` (JWT signing key - set this outside local development), `VITE_API_URL` (frontend -> backend URL).
OCR for scanned PDFs/images needs the Tesseract program installed in addition to `pytesseract`.

## Tests

```bash
python -m unittest tests.test_learning_logic tests.test_document_pipeline -v   # no server needed
python -m unittest tests.test_api_smoke -v                                      # needs backend requirements installed
```

## How documents flow through the app

`backend/documents_api.py` stores each upload under a generated name, then `document_intelligence/` extracts text with
page / sheet / section metadata, splits it into chunks and saves them in SQLite. Chat retrieves the best chunks with BM25
(`document_intelligence/retriever.py`, no vector database) and cites them; summaries, quizzes, flashcards and study plans
read the same stored chunks. To support a new file type, register one extractor in `document_intelligence/extractors.py`.
