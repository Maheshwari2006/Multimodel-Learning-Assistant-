import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { FiChevronLeft, FiChevronRight, FiCheckCircle, FiXCircle, FiRotateCcw, FiPlus, FiHelpCircle } from "react-icons/fi";
import useDocuments from "../hooks/useDocuments";
import { generateQuiz, quizHistory, retakeQuiz, submitQuiz } from "../api/learningApi";
import { errorMessage } from "../api/api";
import DocPicker from "../components/ui/DocPicker";
import { LANGUAGES, PageHeader, SkeletonCard, timeAgo } from "../components/ui/common";
import { useToast } from "../components/ui/Toast";

const LETTERS = ["A", "B", "C", "D"];

function ringColor(pct) {
    return pct >= 80 ? "var(--green)" : pct >= 60 ? "var(--amber)" : "var(--red)";
}

export default function Quiz() {
    const toast = useToast();
    const [params] = useSearchParams();
    const { docs, loading: docsLoading } = useDocuments();
    const [stage, setStage] = useState("setup");              // setup | taking | results
    const [selected, setSelected] = useState(() => (params.get("doc") ? [Number(params.get("doc"))] : []));
    const [count, setCount] = useState(5);
    const [difficulty, setDifficulty] = useState("medium");
    const [language, setLanguage] = useState("english");
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [quiz, setQuiz] = useState(null);                   // {id, title, questions}
    const [answers, setAnswers] = useState([]);
    const [current, setCurrent] = useState(0);
    const [results, setResults] = useState(null);
    const [onlyWrong, setOnlyWrong] = useState(false);
    const [history, setHistory] = useState([]);

    const loadHistory = useCallback(() => quizHistory().then(setHistory).catch(() => {}), []);
    useEffect(() => { loadHistory(); }, [loadHistory]);

    const begin = (q) => {
        setQuiz(q);
        setAnswers(Array(q.questions.length).fill(null));
        setCurrent(0);
        setResults(null);
        setOnlyWrong(false);
        setStage("taking");
    };

    const start = async () => {
        setBusy(true);
        setError("");
        try {
            const q = await generateQuiz({ document_ids: selected, count, difficulty, language });
            if (q.questions.length < count) toast.notify(`The model produced ${q.questions.length} usable question(s) out of ${count} requested.`);
            begin(q);
        } catch (err) {
            setError(errorMessage(err));
        } finally {
            setBusy(false);
        }
    };

    const submit = async () => {
        const unanswered = answers.filter((a) => a === null).length;
        if (unanswered && !window.confirm(`${unanswered} question(s) are unanswered and will count as incorrect. Submit anyway?`)) return;
        setBusy(true);
        try {
            const r = await submitQuiz(quiz.id, answers);
            setResults(r);
            setStage("results");
            loadHistory();
        } catch (err) {
            toast.error(errorMessage(err));
        } finally {
            setBusy(false);
        }
    };

    const retake = async () => {
        setBusy(true);
        try { begin(await retakeQuiz(quiz.id)); } catch (err) { toast.error(errorMessage(err)); } finally { setBusy(false); }
    };

    const choose = useCallback((i) => setAnswers((a) => a.map((v, idx) => (idx === current ? i : v))), [current]);

    // keyboard: 1-4 / A-D choose, arrows move
    useEffect(() => {
        if (stage !== "taking" || !quiz) return undefined;
        const onKey = (e) => {
            if (["INPUT", "TEXTAREA", "SELECT"].includes(e.target.tagName)) return;
            const k = e.key.toLowerCase();
            const idx = "1234".includes(k) && k ? Number(k) - 1 : "abcd".indexOf(k);
            if (k.length === 1 && idx >= 0 && idx < quiz.questions[current].options.length) choose(idx);
            if (e.key === "ArrowRight") setCurrent((c) => Math.min(c + 1, quiz.questions.length - 1));
            if (e.key === "ArrowLeft") setCurrent((c) => Math.max(c - 1, 0));
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [stage, quiz, current, choose]);

    // ------------------------------------------------------------ setup
    if (stage === "setup") {
        return (
            <>
                <PageHeader title="Quizzes" subtitle="Generate a multiple-choice quiz directly from your documents." />
                <div className="split">
                    <div className="card stack">
                        <DocPicker docs={docs} loading={docsLoading} selected={selected} onChange={setSelected} />
                        <div className="grid c2" style={{ gap: 12 }}>
                            <div className="field">
                                <label htmlFor="q-count">Number of questions</label>
                                <select id="q-count" className="select" value={count} onChange={(e) => setCount(Number(e.target.value))}>
                                    {[3, 5, 8, 10, 15, 20].map((n) => <option key={n} value={n}>{n}</option>)}
                                </select>
                            </div>
                            <div className="field">
                                <label htmlFor="q-lang">Language</label>
                                <select id="q-lang" className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                                    {LANGUAGES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
                                </select>
                            </div>
                        </div>
                        <div className="field">
                            <span className="label">Difficulty</span>
                            <div className="segmented">
                                {["easy", "medium", "hard"].map((d) => (
                                    <button key={d} className={difficulty === d ? "on" : ""} onClick={() => setDifficulty(d)}>{d[0].toUpperCase() + d.slice(1)}</button>
                                ))}
                            </div>
                        </div>
                        {error && <div className="alert err" role="alert">{error}</div>}
                        <button className="btn primary" disabled={!selected.length || busy} onClick={start}>
                            {busy ? <><span className="spinner" /> Writing questions…</> : "Generate quiz"}
                        </button>
                    </div>

                    <div className="stack">
                        {busy && <SkeletonCard lines={4} />}
                        <div className="card">
                            <div className="card-title"><h2>Your quiz history</h2></div>
                            {history.length === 0 ? (
                                <p className="muted" style={{ margin: 0 }}>Completed quizzes and scores will show up here.</p>
                            ) : (
                                <div className="stack" style={{ gap: 8 }}>
                                    {history.slice(0, 8).map((h) => (
                                        <div key={h.id} className="row between" style={{ flexWrap: "nowrap" }}>
                                            <div className="truncate"><span>{h.title}</span> <span className="faint">· {h.difficulty} · {timeAgo(h.submitted_at)}</span></div>
                                            <span className="badge" style={{ color: ringColor(h.score_pct) }}>{Math.round(h.score_pct)}% ({h.correct}/{h.total})</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </>
        );
    }

    // ------------------------------------------------------------ taking
    if (stage === "taking" && quiz) {
        const q = quiz.questions[current];
        const answered = answers.filter((a) => a !== null).length;
        return (
            <>
                <PageHeader title={quiz.title} subtitle={`${answered}/${quiz.questions.length} answered · ${quiz.difficulty} difficulty`}>
                    <button className="btn sm" onClick={() => window.confirm("Leave this quiz? Your answers will be lost.") && setStage("setup")}>Exit</button>
                </PageHeader>
                <div className="progress" style={{ marginBottom: 16 }}><span style={{ width: `${(answered / quiz.questions.length) * 100}%` }} /></div>

                <div className="card rise" key={current}>
                    <div className="faint" style={{ marginBottom: 6 }}>Question {current + 1} of {quiz.questions.length}</div>
                    <h2 style={{ marginTop: 0 }}>{q.question}</h2>
                    <div className="stack" role="radiogroup" aria-label="Answer options">
                        {q.options.map((o, i) => (
                            <button key={i} role="radio" aria-checked={answers[current] === i} className={`option ${answers[current] === i ? "sel" : ""}`} onClick={() => choose(i)}>
                                <span className="letter">{LETTERS[i]}</span><span>{o}</span>
                            </button>
                        ))}
                    </div>
                    <div className="row between" style={{ marginTop: 18 }}>
                        <button className="btn" disabled={current === 0} onClick={() => setCurrent(current - 1)}><FiChevronLeft /> Previous</button>
                        {current < quiz.questions.length - 1 ? (
                            <button className="btn primary" onClick={() => setCurrent(current + 1)}>Next <FiChevronRight /></button>
                        ) : (
                            <button className="btn primary" disabled={busy} onClick={submit}>{busy ? <span className="spinner" /> : "Submit quiz"}</button>
                        )}
                    </div>
                </div>

                <div className="row between" style={{ marginTop: 14 }}>
                    <div className="q-dots" aria-label="Question navigator">
                        {quiz.questions.map((_, i) => (
                            <button key={i} className={`q-dot ${answers[i] !== null ? "answered" : ""} ${i === current ? "current" : ""}`} onClick={() => setCurrent(i)} aria-label={`Go to question ${i + 1}`}>{i + 1}</button>
                        ))}
                    </div>
                    {current < quiz.questions.length - 1 && <button className="btn sm" disabled={busy} onClick={submit}>Submit now</button>}
                </div>
                <p className="faint">Tip: press 1–4 (or A–D) to answer and ← → to move between questions.</p>
            </>
        );
    }

    // ------------------------------------------------------------ results
    if (stage === "results" && results) {
        const shown = results.results.map((r, i) => ({ ...r, number: i + 1 })).filter((r) => !onlyWrong || !r.is_correct);
        const wrong = results.results.filter((r) => !r.is_correct).length;
        return (
            <>
                <PageHeader title="Quiz results" subtitle={results.title} />
                <div className="card row" style={{ gap: 28 }}>
                    <div className="score-ring" style={{ "--pct": results.score_pct, "--ring": ringColor(results.score_pct) }}>
                        <b>{Math.round(results.score_pct)}%</b>
                    </div>
                    <div className="stack" style={{ flex: 1, minWidth: 220 }}>
                        <h2 style={{ margin: 0 }}>{results.correct} of {results.total} correct</h2>
                        <p className="muted" style={{ margin: 0 }}>
                            {results.score_pct >= 80 ? "Excellent work — you know this material well." : results.score_pct >= 60 ? "Good effort. Review the questions you missed below." : "Keep going — review the explanations below and try again."}
                        </p>
                        <div className="row">
                            <button className="btn primary" disabled={busy} onClick={retake}><FiRotateCcw /> Retry this quiz</button>
                            <button className="btn" onClick={() => setStage("setup")}><FiPlus /> New quiz</button>
                            {wrong > 0 && <button className="btn" onClick={() => setOnlyWrong((v) => !v)}>{onlyWrong ? "Show all" : `Review ${wrong} incorrect`}</button>}
                        </div>
                    </div>
                </div>

                <div className="stack" style={{ marginTop: 16 }}>
                    {shown.map((r) => (
                        <div key={r.number} className="card">
                            <div className="row between">
                                <b>Question {r.number}</b>
                                {r.is_correct ? <span className="badge ok"><FiCheckCircle /> Correct</span> : <span className="badge err"><FiXCircle /> {r.chosen === null ? "Unanswered" : "Incorrect"}</span>}
                            </div>
                            <p style={{ fontSize: 17 }}>{r.question}</p>
                            <div className="stack" style={{ gap: 8 }}>
                                {r.options.map((o, i) => (
                                    <div key={i} className={`option ${i === r.answer_index ? "right" : i === r.chosen ? "wrong" : ""}`} style={{ cursor: "default" }}>
                                        <span className="letter">{LETTERS[i]}</span>
                                        <span style={{ flex: 1 }}>{o}</span>
                                        {i === r.answer_index && <span className="faint">Correct answer</span>}
                                        {i === r.chosen && i !== r.answer_index && <span className="faint">Your answer</span>}
                                    </div>
                                ))}
                            </div>
                            {r.explanation && <div className="alert info" style={{ marginTop: 12 }}><b>Why: </b>{r.explanation}</div>}
                        </div>
                    ))}
                    {shown.length === 0 && <div className="card empty"><div className="empty-icon"><FiHelpCircle /></div><h3>Perfect score — nothing to review!</h3></div>}
                </div>
            </>
        );
    }
    return null;
}
