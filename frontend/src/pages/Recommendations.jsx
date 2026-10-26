import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FiRefreshCw, FiStar } from "react-icons/fi";
import { getRecommendations } from "../api/learningApi";
import { errorMessage } from "../api/api";
import { EmptyState, PageHeader, SkeletonCard } from "../components/ui/common";

const BADGE = { high: ["err", "High priority"], medium: ["warn", "Worth doing"], low: ["ok", "When you can"] };

export default function Recommendations() {
    const [data, setData] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    const load = useCallback(async () => {
        setLoading(true);
        try { setData(await getRecommendations()); setError(""); } catch (err) { setError(errorMessage(err)); } finally { setLoading(false); }
    }, []);
    useEffect(() => { load(); }, [load]);

    const b = data?.basis;

    return (
        <>
            <PageHeader title="Recommendations" subtitle="Based only on your real quiz scores, flashcard reviews, study-plan progress and uploaded documents.">
                <button className="btn" onClick={load} disabled={loading}><FiRefreshCw /> Refresh</button>
            </PageHeader>

            {error && <div className="alert err" role="alert">{error}</div>}
            {loading && !data && <div className="stack"><SkeletonCard /><SkeletonCard /></div>}

            {data && (
                <>
                    {data.recommendations.length === 0 ? (
                        <div className="card">
                            <EmptyState icon={<FiStar />} title="Nothing to recommend yet" action={{ to: b.documents ? "/quiz" : "/upload", label: b.documents ? "Take a quiz" : "Upload a document" }}>
                                Recommendations appear once there is learning history to learn from. Upload a document, take a quiz, review flashcards or
                                follow a study plan and this page will tell you what to do next — and why.
                            </EmptyState>
                        </div>
                    ) : (
                        <div className="stack">
                            {data.recommendations.map((r) => (
                                <div key={r.id} className={`card rec-${r.priority} rise`}>
                                    <div className="row between">
                                        <h3 style={{ margin: 0 }}>{r.title}</h3>
                                        <span className={`badge ${BADGE[r.priority][0]}`}>{BADGE[r.priority][1]}</span>
                                    </div>
                                    <p className="muted" style={{ margin: "8px 0 12px" }}><b style={{ color: "var(--text)" }}>Why: </b>{r.reason}</p>
                                    <Link className="btn sm" to={r.action.path}>{r.action.label}</Link>
                                </div>
                            ))}
                        </div>
                    )}
                    <p className="faint" style={{ marginTop: 16 }}>
                        Built from {b.documents} document{b.documents === 1 ? "" : "s"}, {b.quizzes_taken} completed quiz{b.quizzes_taken === 1 ? "" : "zes"},
                        {" "}{b.flashcard_decks} flashcard deck{b.flashcard_decks === 1 ? "" : "s"} and {b.study_plans} study plan{b.study_plans === 1 ? "" : "s"}.
                    </p>
                </>
            )}
        </>
    );
}
