"""Run: python -m unittest tests.test_learning_logic -v  (uses a fake LLM; no Ollama needed)"""
import json, unittest
from datetime import date

from backend import learning_logic as L


class FakeLLM:
    def __init__(self, *replies):
        self.replies, self.calls = list(replies), []

    def chat(self, messages, json_mode=False, temperature=0.3):
        self.calls.append(messages)
        r = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        return r if isinstance(r, str) else json.dumps(r)


def chunks(n=3, size=100):
    return [{"document_id": 1, "document_name": "Notes.pdf", "idx": i, "text": "x" * size, "page": i + 1,
             "section": f"S{i}"} for i in range(n)]


class Tests(unittest.TestCase):
    def test_parse_json_variants(self):
        self.assertEqual(L.parse_json('```json\n{"a":1}\n```'), {"a": 1})
        self.assertEqual(L.parse_json('Sure! {"a": [1,2]} done'), {"a": [1, 2]})
        with self.assertRaises(L.GenerationError):
            L.parse_json("no json here")

    def test_ask_json_retries_once(self):
        llm = FakeLLM("garbage", {"ok": True})
        self.assertEqual(L.ask_json(llm, []), {"ok": True})

    def test_select_context_samples_evenly(self):
        text, chosen, cov = L.select_context(chunks(100, 500), budget=5000)
        self.assertEqual(cov, "sampled")
        self.assertLessEqual(len(text), 6500)
        self.assertEqual(chosen[0]["idx"], 0)
        self.assertEqual(chosen[-1]["idx"], 99)
        _, _, cov = L.select_context(chunks(2, 100))
        self.assertEqual(cov, "full")

    def test_quiz_validation_and_shuffle(self):
        raw = {"questions": [
            {"question": "Q1?", "options": ["A) one", "B) two", "C) three", "D) four"], "answer": "B", "explanation": "e"},
            {"question": "Q1?", "options": ["a", "b", "c", "d"], "answer_index": 0},          # duplicate
            {"question": "Bad", "options": ["only"], "answer_index": 0},                         # too few options
            {"question": "Q2?", "options": ["x", "y", "z", "w"], "answer_index": 2},
        ]}
        qs = L.build_quiz(FakeLLM(raw), chunks(), 5, "easy", "english", seed=1)
        self.assertEqual(len(qs), 2)
        q1 = qs[0]
        self.assertEqual(q1["options"][q1["answer_index"]], "two")       # prefix stripped, answer preserved
        q2 = qs[1]
        self.assertEqual(q2["options"][q2["answer_index"]], "z")

    def test_quiz_error_when_nothing_usable(self):
        with self.assertRaises(L.GenerationError):
            L.build_quiz(FakeLLM({"questions": []}), chunks(), 5, "easy", "english")

    def test_flashcards_dedupe(self):
        raw = {"flashcards": [{"question": "A?", "answer": "1"}, {"front": "a?", "back": "2"},
                              {"term": "T", "definition": "D"}, {"question": "no answer"}]}
        cards = L.build_flashcards(FakeLLM(raw), chunks(), 10, "english")
        self.assertEqual([c["question"] for c in cards], ["A?", "T"])

    def test_plan_clamps_days_and_minutes(self):
        raw = {"title": "T", "tasks": [{"day": 99, "title": "late", "minutes": 9999},
                                       {"day": 1, "title": "first", "minutes": "x"}, {"title": ""}]}
        plan = L.build_plan(FakeLLM(raw), chunks(), "ML", 7, 1, "english")
        self.assertEqual([t["day"] for t in plan["tasks"]], [1, 7])
        self.assertEqual(plan["tasks"][1]["minutes"], 240)
        self.assertEqual(plan["tasks"][0]["minutes"], 30)

    def test_schedule_dates_weekdays(self):
        monday = date(2026, 10, 26)
        ds = L.schedule_dates(4, monday, [0, 2])            # Mon & Wed only
        self.assertEqual([d.isoformat() for d in ds], ["2026-10-26", "2026-10-28", "2026-11-02", "2026-11-04"])
        self.assertEqual(len(L.schedule_dates(3, monday)), 3)

    def test_summary_shape_and_detailed_map_reduce(self):
        raw = {"summary": "S", "key_points": ["k"], "definitions": [{"term": "t", "definition": "d"}, {"term": "x"}],
               "sections": []}
        llm = FakeLLM("Part title\nBody", raw)
        out = L.build_summary(llm, chunks(30, 1000), "detailed", "english")   # 30k chars > budget
        self.assertGreaterEqual(len(llm.calls), 3)                              # >=2 part calls + final
        self.assertEqual(out["definitions"], [{"term": "t", "definition": "d"}])
        self.assertEqual(out["coverage"], "full")
        out = L.build_summary(FakeLLM(raw), chunks(30, 1000), "short", "english")
        self.assertEqual(out["coverage"], "sampled")

    def test_rag_messages_cite_and_history(self):
        hist = [{"role": "user", "content": "u" * 3000}, {"role": "assistant", "content": "a"}]
        msgs, sources = L.build_rag_messages("Explain Task 3", hist, chunks(2), "marathi")
        self.assertIn("[1] (Notes.pdf · p.1 · S0)", msgs[0]["content"])
        self.assertIn("Marathi", msgs[0]["content"])
        self.assertEqual(len(msgs[1]["content"]), 1500)
        self.assertEqual(sources[1]["page"], 2)
        self.assertEqual(msgs[-1], {"role": "user", "content": "Explain Task 3"})

    def test_followup_retrieval_query(self):
        hist = [{"role": "user", "content": "What is gradient descent?"}]
        self.assertIn("gradient descent", L.retrieval_query("and its drawbacks?", hist))
        self.assertEqual(L.retrieval_query("Explain in detail how the optimiser works here", hist),
                         "Explain in detail how the optimiser works here")

    def test_recommendations_use_real_data_only(self):
        self.assertEqual(L.compute_recommendations([], [], [], []), [])
        attempts = [{"id": 1, "title": "ML Notes", "document_ids": [4], "score_pct": 40.0, "correct": 2, "total": 5,
                     "when": 1, "missed": ["What is overfitting?"]}]
        decks = [{"id": 2, "title": "ML cards", "total": 10, "known": 3, "review": 4, "new": 3}]
        plans = [{"id": 3, "title": "Week plan", "total": 10, "done": 2, "overdue": 3}]
        docs = [{"id": 9, "name": "Unused.pdf", "status": "ready", "activity": 0},
                {"id": 4, "name": "ML Notes", "status": "ready", "activity": 1}]
        recs = L.compute_recommendations(docs, attempts, decks, plans)
        self.assertEqual({r["id"] for r in recs}, {"quiz-1", "deck-2", "plan-3", "doc-9"})
        self.assertEqual(recs[0]["priority"], "high")
        self.assertIn("40%", next(r for r in recs if r["id"] == "quiz-1")["reason"])
        self.assertIn("overfitting", next(r for r in recs if r["id"] == "quiz-1")["reason"])


if __name__ == "__main__":
    unittest.main()
