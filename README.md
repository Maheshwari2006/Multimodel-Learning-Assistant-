# Multimodel Learning Assistant

# 🧠 Multimodal Learning Assistant

**Upload once. Learn in multiple ways.**

An AI-powered learning platform that transforms educational documents into interactive and personalized learning experiences using Generative AI and document intelligence.

🚀 **Live Demo:** [Multimodal Learning Assistant](https://multimodel-learning-assistant.vercel.app/)

📂 **GitHub Repository:** [View Source Code](https://github.com/Maheshwari2006/Multimodal-Learning-Assistant-)

---

## 📌 About the Project

The **Multimodal Learning Assistant** is designed to make learning more accessible, interactive, and efficient.

Instead of manually reading lengthy documents and preparing study materials, users can upload their learning resources and use AI to generate summaries, quizzes, flashcards, study plans, and contextual answers.

The platform integrates document processing, information retrieval, cloud storage, and Generative AI into a unified learning environment.

## ✨ Key Features

- **Document Upload:** Upload educational documents for AI-powered processing.
- **AI-Powered Chat:** Ask questions about uploaded documents and receive context-aware answers.
- **Smart Summarization:** Generate concise summaries from lengthy learning materials.
- **Quiz Generation:** Automatically create quizzes based on document content.
- **Flashcard Generation:** Generate revision flashcards for effective learning.
- **Personalized Study Plans:** Create structured study plans from learning materials.
- **Learning Recommendations:** Get AI-generated suggestions to support learning.
- **User Authentication:** Secure registration and login using JWT authentication.
- **Cloud Document Storage:** Store and manage uploaded documents using Supabase Storage.

## 🔄 How It Works

The application follows a simple learning workflow:

**Upload → Extract → Chat → Summarize → Quiz → Flashcards → Study Plan → Recommendations**

1. Upload an educational document.
2. Extract and process its content.
3. Retrieve relevant information using BM25.
4. Ask questions and interact with the document.
5. Generate AI-powered learning resources.
6. Use the generated materials for revision and preparation.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Production AI | Google Gemini API |
| Local AI Development | Ollama, Llama 3 |
| Database | Neon PostgreSQL |
| Cloud Storage | Supabase Storage |
| Information Retrieval | BM25 |
| Authentication | JWT |
| Deployment | Vercel |
| API Documentation | FastAPI Swagger UI |

## 🏗️ System Architecture

```text
                 USER
                   |
                   v
           React + Vite
              Frontend
                   |
                   v
             FastAPI
              Backend
                   |
          +--------+--------+
          |        |        |
          v        v        v
        Gemini   Neon DB  Supabase
         API   PostgreSQL Storage
          |
          v
    AI Learning Services
          |
     +----+-----+-------+
     |    |     |       |
    Chat Summary Quiz Flashcards
                       |
                  Study Plans
                       |
                Recommendations
```

### Document Processing Pipeline

- **Upload:** Documents are uploaded through the application.
- **Storage:** Supabase Storage manages document files.
- **Extraction:** Document content is extracted using the document processing pipeline.
- **Chunking:** Extracted content is divided into manageable chunks.
- **Retrieval:** BM25 identifies relevant document content.
- **Generation:** Gemini generates context-aware responses and learning materials.

## 🌐 Live Application

| Service | URL |
|---|---|
| Frontend Demo | [Open Application](https://multimodel-learning-assistant.vercel.app/) |
| Backend API | [Backend Deployment](https://multimodel-learning-backend.vercel.app/) |
| API Documentation | [Swagger UI](https://multimodel-learning-backend.vercel.app/docs) |

## 💻 Installation and Setup

Follow these steps to run the project locally.

### Prerequisites

Make sure you have installed:

- Python 3.10 or later
- Node.js and npm
- Git
- Ollama (for local AI development)

### 1. Clone the Repository

```bash
git clone https://github.com/Maheshwari2006/Multimodal-Learning-Assistant-.git
cd Multimodal-Learning-Assistant-
```

### 2. Backend Setup

Create a virtual environment:

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

Start the FastAPI server:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend URL:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

`http://localhost:5173`

### 4. Local AI Setup with Ollama

Install Ollama and download the Llama 3 model:

```bash
ollama pull llama3
```

Start the Ollama service:

```bash
ollama serve
```

Configure the backend to use Ollama for local AI development.

## ⚙️ Environment Variables

Configure the required environment variables in your local environment or deployment dashboard.

| Variable | Description |
|---|---|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase backend authentication key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GEMINI_MODEL` | Gemini model configuration |
| `SECRET_KEY` | JWT signing secret |
| `VITE_API_URL` | Backend API URL for the frontend |
| `OLLAMA_MODEL` | Local Ollama model |
| `MAX_UPLOAD_MB` | Maximum document upload size |

**Security Note:** Never upload API keys, database credentials, JWT secrets, or other sensitive configuration values to GitHub.

## 🧪 Running Tests

Run learning logic and document pipeline tests:

```bash
python -m unittest tests.test_learning_logic tests.test_document_pipeline -v
```

Run API smoke tests:

```bash
python -m unittest tests.test_api_smoke -v
```

## 📁 Project Structure

```text
Multimodal-Learning-Assistant/
│
├── backend/
│   ├── main.py
│   ├── database/
│   ├── document_intelligence/
│   ├── storage.py
│   ├── documents_api.py
│   ├── services.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── tests/
│
├── .gitignore
└── README.md
```

*Note: This is a simplified representation of the project structure.*

## 🔮 Future Enhancements

- Advanced semantic search and vector-based retrieval.
- Support for additional document formats.
- Multilingual learning capabilities.
- Learning progress tracking and analytics.
- More personalized AI-driven recommendations.
- Enhanced interactive learning experiences.

## 👩‍💻 Author

**Maheshwari Rewatkar**

B.Tech – Artificial Intelligence Engineering

- GitHub: [Maheshwari2006](https://github.com/Maheshwari2006)
- 
