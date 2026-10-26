"""End-to-end API smoke test with a temporary database and a fake LLM (no Ollama needed).

Run from the project root after `pip install -r backend/requirements.txt`:
    python -m unittest tests.test_api_smoke -v
"""
import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import documents_api, services
from backend.database import database
from backend.database.database import Base, get_db
from backend.llm import llm
from backend.main import app

NOTES = ("Photosynthesis converts light energy into chemical energy. Chlorophyll absorbs light in the chloroplast. "
         "Task 3: explain the Calvin cycle and list its three phases. The Calvin cycle fixes carbon dioxide into sugar. ") * 8


def fake_chat(messages, json_mode=False, temperature=0.3):
    prompt = " ".join(m["content"] for m in messages)
    if "multiple-choice" in prompt:
        return json.dumps({"questions": [
            {"question": f"Question {i}?", "options": ["A1", "B1", "C1", "D1"], "answer_index": 1, "explanation": "Because."}
            for i in range(3)]})
    if "flashcards" in prompt:
        return json.dumps({"flashcards": [{"question": "What absorbs light?", "answer": "Chlorophyll"}]})
    if "study-day plan" in prompt:
        return json.dumps({"title": "Plan", "tasks": [{"day": 1, "title": "Read", "description": "Read notes", "minutes": 30},
                                                      {"day": 2, "title": "Practise", "description": "Do tasks", "minutes": 30}]})
    if "Summarise the material" in prompt:
        return json.dumps({"summary": "A short summary.", "key_points": ["One"], "definitions": [], "sections": []})
    return "The Calvin cycle has three phases [1]."


class ApiSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.engine = engine = create_engine(f"sqlite:///{cls.tmp.name}/test.db", connect_args={"check_same_thread": False})
        Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        Base.metadata.create_all(engine)

        def override():
            db = Session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override
        cls._saved = (services.SessionLocal, services.UPLOAD_DIR, documents_api.UPLOAD_DIR, llm.chat)
        services.SessionLocal = Session
        services.UPLOAD_DIR = documents_api.UPLOAD_DIR = Path(cls.tmp.name)
        llm.chat = fake_chat
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        cls.engine.dispose()                      # release test.db so Windows can delete it
        services.SessionLocal, services.UPLOAD_DIR, documents_api.UPLOAD_DIR, llm.chat = cls._saved
        cls.tmp.cleanup()

    def test_full_learning_flow(self):
        c = self.client
        c.post("/register", json={"username": "sam", "email": "sam@example.com", "password": "secret123"})
        token = c.post("/login", data={"username": "sam@example.com", "password": "secret123"}).json()["access_token"]
        c.headers["Authorization"] = f"Bearer {token}"

        r = c.post("/documents/upload", files={"file": ("notes.txt", NOTES.encode(), "text/plain")})
        self.assertEqual(r.status_code, 201, r.text)
        doc_id = r.json()["id"]
        doc = c.get(f"/documents/{doc_id}").json()          # background task has already run in TestClient
        self.assertEqual(doc["status"], "ready", doc)
        self.assertEqual(c.post("/documents/upload", files={"file": ("a.exe", b"MZ")}).status_code, 415)

        chat = c.post("/chat/query", json={"message": "Explain Task 3", "document_ids": [doc_id]}).json()
        self.assertEqual(chat["message"]["mode"], "document")
        self.assertTrue(chat["message"]["sources"])
        general = c.post("/chat/query", json={"message": "What is gravity?"}).json()
        self.assertEqual(general["message"]["mode"], "general")
        self.assertEqual(len(c.get(f"/chat/sessions/{chat['session_id']}").json()["messages"]), 2)

        self.assertIn("summary", c.post("/summary/", json={"document_ids": [doc_id], "length": "short"}).json())

        quiz = c.post("/quiz/generate", json={"document_ids": [doc_id], "count": 3}).json()
        self.assertNotIn("answer_index", quiz["questions"][0])           # answers stay server-side
        done = c.post(f"/quiz/attempts/{quiz['id']}/submit", json={"answers": [None, None, None]}).json()
        self.assertEqual(done["correct"], 0)
        self.assertEqual(c.post(f"/quiz/attempts/{quiz['id']}/submit", json={"answers": [0, 0, 0]}).status_code, 409)

        deck = c.post("/flashcards/generate", json={"document_ids": [doc_id]}).json()
        card_id = deck["cards"][0]["id"]
        self.assertEqual(c.patch(f"/flashcards/items/{card_id}", json={"status": "review"}).status_code, 200)

        plan = c.post("/study-plan/generate", json={"document_ids": [doc_id], "days": 2}).json()
        task_id = plan["tasks"][0]["id"]
        self.assertEqual(c.patch(f"/study-plan/tasks/{task_id}", json={"done": True}).json()["done"], True)

        recs = c.get("/recommendation/").json()
        self.assertEqual(recs["basis"]["quizzes_taken"], 1)
        self.assertTrue(any(x["type"] == "revise" for x in recs["recommendations"]))   # 0% quiz -> revise
        dash = c.get("/dashboard").json()
        self.assertEqual(dash["stats"]["documents_ready"], 1)

        # another user cannot see this document
        c2 = TestClient(app)
        c2.post("/register", json={"username": "kim", "email": "kim@example.com", "password": "secret123"})
        t2 = c2.post("/login", data={"username": "kim@example.com", "password": "secret123"}).json()["access_token"]
        c2.headers["Authorization"] = f"Bearer {t2}"
        self.assertEqual(c2.get(f"/documents/{doc_id}").status_code, 404)

        self.assertEqual(c.delete(f"/documents/{doc_id}").status_code, 200)


if __name__ == "__main__":
    unittest.main()
