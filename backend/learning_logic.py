"""Pure learning logic (prompts, validation, scheduling, recommendations).

No FastAPI / SQLAlchemy / Ollama imports here, so this module is unit-testable with a fake LLM.
An "llm" is any object with ``chat(messages, json_mode=False, temperature=0.3) -> str``.
"""
from __future__ import annotations

import json
import math
import random
import re
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple

CONTEXT_CHAR_BUDGET = 14000
LANGUAGES = {"english": "English", "hindi": "Hindi (हिन्दी)", "marathi": "Marathi (मराठी)"}


class GenerationError(Exception):
    """The model answered, but not in a usable form."""


# --------------------------------------------------------------------------
# generic helpers
# --------------------------------------------------------------------------
def language_name(lang: Optional[str]) -> str:
    return LANGUAGES.get((lang or "english").strip().lower(), "English")


def language_rule(lang: Optional[str]) -> str:
    name = language_name(lang)
    if name == "English":
        return "Write in clear English."
    return (
        f"Write all natural-language text in {name}. Keep technical terms, code, numbers and proper nouns "
        "unchanged where translating them would cause confusion."
    )


def parse_json(text: str) -> Any:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for open_c, close_c in (("{", "}"), ("[", "]")):
        start, end = text.find(open_c), text.rfind(close_c)
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                continue
    raise GenerationError("The AI response was not valid JSON.")


def ask_json(llm, messages, temperature=0.3, attempts=2):
    last = None
    for _ in range(attempts):
        raw = llm.chat(messages, json_mode=True, temperature=temperature)
        try:
            return parse_json(raw)
        except GenerationError as exc:
            last = exc
    raise last or GenerationError("The AI response was not valid JSON.")


def chunk_label(c: Dict) -> str:
    parts = [c.get("document_name") or "Document"]
    if c.get("page"):
        parts.append(f"p.{c['page']}")
    if c.get("section"):
        parts.append(str(c["section"])[:80])
    return " · ".join(parts)


def select_context(chunks: Sequence[Dict], budget: int = CONTEXT_CHAR_BUDGET) -> Tuple[str, List[Dict], str]:
    """Pick chunks (evenly spread across the material) that fit the model's context budget."""
    chunks = list(chunks)
    if not chunks:
        return "", [], "full"
    total = sum(len(c["text"]) for c in chunks)
    if total <= budget:
        chosen, coverage = chunks, "full"
    else:
        avg = total / len(chunks)
        keep = max(1, min(len(chunks), int(budget / (avg + 40))))
        if keep == 1:
            indices = [0]
        else:
            indices = sorted({round(i * (len(chunks) - 1) / (keep - 1)) for i in range(keep)})
        chosen, coverage = [chunks[i] for i in indices], "sampled"
    text = "\n\n".join(f"[{chunk_label(c)}]\n{c['text']}" for c in chosen)
    return text, chosen, coverage


# --------------------------------------------------------------------------
# summaries
# --------------------------------------------------------------------------
SUMMARY_WORDS = {"short": "about 80-120 words", "medium": "about 200-300 words", "detailed": "about 450-650 words"}


def _group(chunks: Sequence[Dict], n: int) -> List[List[Dict]]:
    size = math.ceil(len(chunks) / n)
    return [list(chunks[i:i + size]) for i in range(0, len(chunks), size)]


def build_summary(llm, chunks: Sequence[Dict], length: str, language: str) -> Dict:
    length = length if length in SUMMARY_WORDS else "medium"
    sys_msg = (
        "You are an expert study assistant. Use ONLY the supplied material; never add facts that are not in it. "
        + language_rule(language)
    )
    total = sum(len(c["text"]) for c in chunks)
    coverage = "full"
    material, _, coverage = select_context(chunks)
    section_notes = ""

    # Long document + detailed summary: summarise contiguous parts first (chapter-wise), then combine.
    if length == "detailed" and total > CONTEXT_CHAR_BUDGET:
        parts = []
        for group in _group(chunks, min(5, max(2, total // 8000))):
            text, _, _ = select_context(group, 9000)
            raw = llm.chat([
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": "Give this part a short title on the first line, then summarise it "
                                            "in 80-120 words (plain text, no markdown).\n\nMATERIAL:\n" + text},
            ], temperature=0.2)
            parts.append(raw.strip())
        section_notes = "\n\n".join(f"PART {i + 1}:\n{p}" for i, p in enumerate(parts))
        material = section_notes
        coverage = "full"

    schema = (
        '{"summary": "markdown text", "key_points": ["..."], '
        '"definitions": [{"term": "...", "definition": "..."}], '
        '"sections": [{"title": "...", "summary": "..."}]}'
    )
    data = ask_json(llm, [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": (
            f"Summarise the material. The summary must be {SUMMARY_WORDS[length]}. "
            "Include 5-8 key points and up to 8 important definitions (only terms actually defined or explained "
            "in the material). Include 'sections' (chapter/section-wise summaries, 1-2 sentences each) only if the "
            "material has clear sections; otherwise return an empty list.\n"
            f"Return ONLY JSON with this shape: {schema}\n\nMATERIAL:\n{material}")},
    ])
    if not isinstance(data, dict) or not str(data.get("summary", "")).strip():
        raise GenerationError("The AI did not return a summary.")

    def clean_list(v):
        return [str(x).strip() for x in v if str(x).strip()] if isinstance(v, list) else []

    defs = []
    for d in data.get("definitions") or []:
        if isinstance(d, dict) and d.get("term") and d.get("definition"):
            defs.append({"term": str(d["term"]).strip(), "definition": str(d["definition"]).strip()})
    secs = []
    for s in data.get("sections") or []:
        if isinstance(s, dict) and s.get("title") and s.get("summary"):
            secs.append({"title": str(s["title"]).strip(), "summary": str(s["summary"]).strip()})
    return {
        "summary": str(data["summary"]).strip(),
        "key_points": clean_list(data.get("key_points")),
        "definitions": defs[:12],
        "sections": secs[:12],
        "coverage": coverage,
        "length": length,
    }


# --------------------------------------------------------------------------
# quiz
# --------------------------------------------------------------------------
DIFFICULTY = {
    "easy": "Easy: direct recall of facts and definitions.",
    "medium": "Medium: understanding and applying concepts.",
    "hard": "Hard: analysis, comparison and scenario-based questions with plausible distractors.",
}


def _answer_index(q: Dict, options: List[str]) -> Optional[int]:
    raw = q.get("answer_index", q.get("correct_index", q.get("answer", q.get("correct_answer"))))
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw if 0 <= raw < len(options) else (raw - 1 if 1 <= raw <= len(options) else None)
    if isinstance(raw, str):
        r = raw.strip()
        if re.fullmatch(r"[A-Da-d][\).]?", r):
            return "abcd".index(r[0].lower())
        for i, o in enumerate(options):
            if o.strip().lower() == r.lower():
                return i
        if r.isdigit():
            return _answer_index({"answer_index": int(r)}, options)
    return None


def build_quiz(llm, chunks: Sequence[Dict], count: int, difficulty: str, language: str,
               seed: Optional[int] = None) -> List[Dict]:
    count = max(1, min(int(count), 20))
    difficulty = difficulty if difficulty in DIFFICULTY else "medium"
    material, _, _ = select_context(chunks)
    schema = '{"questions": [{"question": "...", "options": ["A","B","C","D"], "answer_index": 0, "explanation": "..."}]}'
    data = ask_json(llm, [
        {"role": "system", "content": "You are an expert exam writer. Use ONLY the supplied material. "
                                      + language_rule(language)},
        {"role": "user", "content": (
            f"Write exactly {count} multiple-choice questions. {DIFFICULTY[difficulty]} Each has exactly 4 options, "
            "one correct answer (answer_index is 0-3), and a one-or-two sentence explanation that cites the "
            "material. Do not repeat questions. Do not ask about anything the material does not state.\n"
            f"Return ONLY JSON: {schema}\n\nMATERIAL:\n{material}")},
    ], temperature=0.4)
    items = data.get("questions") if isinstance(data, dict) else data
    rng = random.Random(seed)
    out, seen = [], set()
    for q in items or []:
        if not isinstance(q, dict) or not q.get("question"):
            continue
        options = [str(o).strip() for o in (q.get("options") or []) if str(o).strip()][:4]
        options = [re.sub(r"^[A-Da-d][\).]\s+", "", o) for o in options]
        idx = _answer_index(q, options)
        key = str(q["question"]).strip().lower()
        if len(options) < 2 or idx is None or key in seen:
            continue
        seen.add(key)
        order = list(range(len(options)))
        rng.shuffle(order)                         # LLMs over-use option A; shuffle
        out.append({
            "question": str(q["question"]).strip(),
            "options": [options[i] for i in order],
            "answer_index": order.index(idx),
            "explanation": str(q.get("explanation") or "").strip(),
        })
    if not out:
        raise GenerationError("The AI did not return any usable quiz questions.")
    return out[:count]


# --------------------------------------------------------------------------
# flashcards
# --------------------------------------------------------------------------
def build_flashcards(llm, chunks: Sequence[Dict], count: int, language: str) -> List[Dict]:
    count = max(1, min(int(count), 40))
    material, _, _ = select_context(chunks)
    data = ask_json(llm, [
        {"role": "system", "content": "You are an expert educator. Use ONLY the supplied material. "
                                      + language_rule(language)},
        {"role": "user", "content": (
            f"Create up to {count} flashcards, prioritising important definitions, key concepts, formulas and "
            "facts. Fewer is better than inventing anything. Questions must be self-contained and answers short.\n"
            'Return ONLY JSON: {"flashcards": [{"question": "...", "answer": "..."}]}\n\n'
            f"MATERIAL:\n{material}")},
    ])
    items = data.get("flashcards", data.get("cards")) if isinstance(data, dict) else data
    out, seen = [], set()
    for c in items or []:
        if not isinstance(c, dict):
            continue
        q = c.get("question") or c.get("front") or c.get("term")
        a = c.get("answer") or c.get("back") or c.get("definition")
        if q and a and str(q).strip().lower() not in seen:
            seen.add(str(q).strip().lower())
            out.append({"question": str(q).strip(), "answer": str(a).strip()})
    if not out:
        raise GenerationError("The AI did not return any flashcards.")
    return out[:count]


# --------------------------------------------------------------------------
# study plan
# --------------------------------------------------------------------------
def schedule_dates(days: int, start: date, weekdays: Optional[Sequence[int]] = None) -> List[date]:
    """Calendar date for study day 1..days. ``weekdays`` uses Monday=0 ... Sunday=6."""
    allowed = {int(w) for w in weekdays} if weekdays else None
    out, cur, guard = [], start, 0
    while len(out) < days and guard < 800:
        if allowed is None or cur.weekday() in allowed:
            out.append(cur)
        cur += timedelta(days=1)
        guard += 1
    return out


def build_plan(llm, chunks: Sequence[Dict], topic: str, days: int, hours_per_day: float, language: str) -> Dict:
    days = max(1, min(int(days), 60))
    minutes = max(15, min(int(hours_per_day * 60), 480))
    material, _, _ = select_context(chunks, 9000) if chunks else ("", [], "full")
    subject = topic.strip() if topic and topic.strip() else "the supplied material"
    source = f"\n\nMATERIAL (base the plan on this content):\n{material}" if material else ""
    data = ask_json(llm, [
        {"role": "system", "content": "You are an expert study coach. " + language_rule(language)},
        {"role": "user", "content": (
            f"Create a {days}-study-day plan for: {subject}. About {minutes} minutes of study per day. "
            "Order topics from fundamentals to advanced, put practice tasks and a revision day near the end, and "
            "finish with a self-test. Each task needs a short title and a concrete 1-2 sentence description. "
            f"Use 1-4 tasks per day; 'day' is 1..{days}.\n"
            'Return ONLY JSON: {"title": "...", "tasks": [{"day": 1, "title": "...", "description": "...", '
            '"minutes": 30}]}' + source)},
    ], temperature=0.4)
    if not isinstance(data, dict):
        raise GenerationError("The AI did not return a study plan.")
    tasks = []
    for t in data.get("tasks") or []:
        if not isinstance(t, dict) or not t.get("title"):
            continue
        try:
            day = int(t.get("day", 1))
        except (TypeError, ValueError):
            day = 1
        try:
            mins = int(t.get("minutes", 30))
        except (TypeError, ValueError):
            mins = 30
        tasks.append({
            "day": min(max(day, 1), days),
            "title": str(t["title"]).strip()[:300],
            "description": str(t.get("description") or "").strip(),
            "minutes": min(max(mins, 10), 240),
        })
    if not tasks:
        raise GenerationError("The AI did not return any study tasks.")
    tasks.sort(key=lambda t: t["day"])
    return {"title": str(data.get("title") or f"Study plan: {subject}")[:200], "tasks": tasks}


# --------------------------------------------------------------------------
# document-grounded chat
# --------------------------------------------------------------------------
def build_rag_messages(question: str, history: Sequence[Dict], chunks: Sequence[Dict], language: str):
    """Return (messages, sources). ``chunks`` are the retrieved excerpts, best first."""
    excerpts, sources = [], []
    for i, c in enumerate(chunks, start=1):
        excerpts.append(f"[{i}] ({chunk_label(c)})\n{c['text']}")
        sources.append({
            "index": i,
            "document_id": c.get("document_id"),
            "document_name": c.get("document_name"),
            "page": c.get("page"),
            "section": c.get("section"),
            "snippet": c["text"][:240].strip(),
        })
    system = (
        "You are a study assistant answering questions about the user's uploaded documents.\n"
        "Rules:\n"
        "1. Answer ONLY from the numbered excerpts below. Never invent document-specific facts.\n"
        "2. Cite the excerpts you used like [1] or [2][3] right after the relevant statement.\n"
        "3. If the excerpts do not contain enough information, say so plainly and state what is missing; "
        "you may then add clearly-labelled general knowledge starting with 'General knowledge:'.\n"
        "4. Use Markdown. Preserve table structure when asked about tables.\n"
        f"5. {language_rule(language)}\n\nEXCERPTS:\n" + "\n\n".join(excerpts)
    )
    messages = [{"role": "system", "content": system}]
    for m in list(history)[-6:]:
        messages.append({"role": m["role"], "content": m["content"][:1500]})
    messages.append({"role": "user", "content": question})
    return messages, sources


def build_general_messages(question: str, history: Sequence[Dict], language: str):
    system = (
        "You are a friendly learning assistant. Explain concepts clearly with examples and use Markdown. "
        "No documents are selected, so do not pretend to know the user's specific files, course or assignment; "
        "if the question depends on one, ask them to select a document. " + language_rule(language)
    )
    messages = [{"role": "system", "content": system}]
    for m in list(history)[-8:]:
        messages.append({"role": m["role"], "content": m["content"][:1500]})
    messages.append({"role": "user", "content": question})
    return messages


def retrieval_query(question: str, history: Sequence[Dict]) -> str:
    """Short follow-ups ('and the second one?') borrow the previous user turn for retrieval."""
    if len(question.split()) < 6:
        prev = [m["content"] for m in history if m["role"] == "user"]
        if prev:
            return f"{prev[-1][:300]} {question}"
    return question


# --------------------------------------------------------------------------
# recommendations (rule-based, from real learning history only)
# --------------------------------------------------------------------------
def compute_recommendations(documents: Sequence[Dict], attempts: Sequence[Dict], decks: Sequence[Dict],
                            plans: Sequence[Dict]) -> List[Dict]:
    recs: List[Dict] = []
    latest: Dict[str, Dict] = {}
    for a in sorted(attempts, key=lambda x: x["when"]):
        latest[a["title"]] = a
    for title, a in latest.items():
        score = round(a["score_pct"])
        doc_q = f"?doc={a['document_ids'][0]}" if a.get("document_ids") else ""
        if score < 60:
            wrong = a.get("missed", [])[:3]
            recs.append({
                "id": f"quiz-{a['id']}", "type": "revise", "priority": "high",
                "title": f"Revise: {title}",
                "reason": f"Your latest quiz on this scored {score}% ({a['correct']}/{a['total']}), below the 60% mark."
                          + (" Concepts you missed: " + "; ".join(wrong) if wrong else ""),
                "action": {"label": "Summarise this material", "path": f"/summary{doc_q}"},
            })
        elif score < 80:
            recs.append({
                "id": f"quiz-{a['id']}", "type": "practice", "priority": "medium",
                "title": f"Practise more: {title}",
                "reason": f"You scored {score}% ({a['correct']}/{a['total']}). A harder quiz or flashcards should push you past 80%.",
                "action": {"label": "Take another quiz", "path": f"/quiz{doc_q}"},
            })
        else:
            recs.append({
                "id": f"quiz-{a['id']}", "type": "strength", "priority": "low",
                "title": f"Strong result: {title}",
                "reason": f"You scored {score}% on your latest quiz. Try a hard-difficulty quiz to stretch yourself.",
                "action": {"label": "Try a harder quiz", "path": f"/quiz{doc_q}"},
            })
    for d in decks:
        if d["review"] > 0:
            recs.append({
                "id": f"deck-{d['id']}", "type": "review", "priority": "medium",
                "title": f"Review {d['review']} flashcard{'s' if d['review'] != 1 else ''}: {d['title']}",
                "reason": f"You marked {d['review']} of {d['total']} cards as needing review.",
                "action": {"label": "Open deck", "path": f"/flashcards?deck={d['id']}"},
            })
        elif d["total"] and d["new"] == d["total"]:
            recs.append({
                "id": f"deck-{d['id']}", "type": "start", "priority": "low",
                "title": f"Start studying: {d['title']}",
                "reason": f"This deck has {d['total']} cards and you haven't reviewed any yet.",
                "action": {"label": "Open deck", "path": f"/flashcards?deck={d['id']}"},
            })
    for p in plans:
        if p["overdue"] > 0:
            recs.append({
                "id": f"plan-{p['id']}", "type": "catch-up", "priority": "high",
                "title": f"Catch up: {p['title']}",
                "reason": f"{p['overdue']} scheduled task{'s are' if p['overdue'] != 1 else ' is'} overdue "
                          f"({p['done']}/{p['total']} done overall).",
                "action": {"label": "Open plan", "path": f"/study-plan?plan={p['id']}"},
            })
    for doc in documents:
        if doc["status"] == "ready" and doc["activity"] == 0:
            recs.append({
                "id": f"doc-{doc['id']}", "type": "start", "priority": "low",
                "title": f"Put \"{doc['name']}\" to work",
                "reason": "You uploaded this document but haven't generated a summary, quiz, flashcards or plan from it yet.",
                "action": {"label": "Generate a quiz", "path": f"/quiz?doc={doc['id']}"},
            })
    order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: order[r["priority"]])
    return recs
