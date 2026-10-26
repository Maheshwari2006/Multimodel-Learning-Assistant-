import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
    FiUploadCloud, FiMessageSquare, FiFileText, FiHelpCircle, FiLayers, FiCalendar, FiStar, FiActivity, FiAlertCircle,
} from "react-icons/fi";
import { getDashboard } from "../api/learningApi";
import { errorMessage } from "../api/api";
import { EmptyState, FileIcon, SkeletonCard, StatusBadge, timeAgo } from "../components/ui/common";
import { useAuth } from "../context/AuthContext";

const SHORTCUTS = [
    { to: "/summary", icon: <FiFileText />, title: "Summaries", text: "Short to detailed, with key points" },
    { to: "/quiz", icon: <FiHelpCircle />, title: "Quizzes", text: "Test yourself on a document" },
    { to: "/flashcards", icon: <FiLayers />, title: "Flashcards", text: "Flip, shuffle and track review" },
    { to: "/study-plan", icon: <FiCalendar />, title: "Study plan", text: "A day-by-day schedule" },
    { to: "/recommendations", icon: <FiStar />, title: "Recommendations", text: "What to study next, and why" },
];
const ACTIVITY_ICON = { upload: FiUploadCloud, chat: FiMessageSquare, quiz: FiHelpCircle, flashcards: FiLayers, plan: FiCalendar, summary: FiFileText, task: FiActivity };

function Stat({ value, label, to }) {
    const body = (<div className="stat"><b>{value}</b><span>{label}</span></div>);
    return to ? <Link to={to} className="card hover" style={{ padding: 16 }}>{body}</Link> : <div className="card" style={{ padding: 16 }}>{body}</div>;
}

export default function Dashboard() {
    const { user } = useAuth();
    const [data, setData] = useState(null);
    const [error, setError] = useState("");

    const load = useCallback(async () => {
        try { setData(await getDashboard()); setError(""); } catch (err) { setError(errorMessage(err)); }
    }, []);
    useEffect(() => { load(); }, [load]);

    // keep the processing status fresh while a document is being read
    const processing = data?.stats.documents_processing || 0;
    useEffect(() => {
        if (!processing) return undefined;
        const t = setTimeout(load, 2500);
        return () => clearTimeout(t);
    }, [processing, data, load]);

    const name = data?.user?.username || user?.username || "there";
    const s = data?.stats;
    const isNew = s && s.documents === 0 && s.conversations === 0 && s.quizzes_taken === 0;

    return (
        <>
            <section className="hero rise">
                <h1>Welcome back, {name}</h1>
                <p>
                    {isNew
                        ? "Upload your first document and everything else - chat, summaries, quizzes, flashcards and plans - is built from it."
                        : "Pick up where you left off, or start something new from your documents."}
                </p>
                <div className="row">
                    <Link to="/upload" className="btn primary"><FiUploadCloud /> Upload a document</Link>
                    <Link to="/chat" className="btn"><FiMessageSquare /> Start AI chat</Link>
                </div>
            </section>

            {error && <div className="alert err" role="alert" style={{ marginTop: 16 }}>{error}</div>}
            {!data && !error && <div className="grid c2" style={{ marginTop: 16 }}><SkeletonCard /><SkeletonCard /></div>}

            {data && (
                <>
                    {/* Real counts only: nothing here is a placeholder */}
                    <div className="grid c4 keep2" style={{ marginTop: 16 }}>
                        <Stat value={s.documents} label={`document${s.documents === 1 ? "" : "s"}${s.documents_processing ? ` (${s.documents_processing} processing)` : ""}`} to="/upload" />
                        <Stat value={s.quizzes_taken ? `${s.average_quiz_score}%` : "-"} label={s.quizzes_taken ? `average over ${s.quizzes_taken} quiz${s.quizzes_taken === 1 ? "" : "zes"}` : "no quizzes taken yet"} to="/quiz" />
                        <Stat value={s.flashcards_total ? `${s.flashcards_known}/${s.flashcards_total}` : "-"} label="flashcards known" to="/flashcards" />
                        <Stat value={s.tasks_total ? `${s.tasks_done}/${s.tasks_total}` : "-"} label={s.tasks_overdue ? `plan tasks done · ${s.tasks_overdue} overdue` : "plan tasks done"} to="/study-plan" />
                    </div>

                    {s.documents_failed > 0 && (
                        <div className="alert warn row" style={{ marginTop: 16 }}>
                            <FiAlertCircle /> {s.documents_failed} document{s.documents_failed === 1 ? "" : "s"} could not be read.
                            <Link to="/upload">See why and retry</Link>
                        </div>
                    )}

                    <div className="split" style={{ marginTop: 16, gridTemplateColumns: "minmax(0, 1.2fr) minmax(0, 1fr)" }}>
                        <div className="card">
                            <div className="card-title"><h2>Recent documents</h2><Link to="/upload" className="faint">Manage</Link></div>
                            {data.recent_documents.length === 0 ? (
                                <EmptyState icon={<FiUploadCloud />} title="No documents yet" action={{ to: "/upload", label: "Upload your first document" }}>
                                    PDFs, Word, slides, spreadsheets, notes, images and code are all supported.
                                </EmptyState>
                            ) : (
                                <div className="stack" style={{ gap: 10 }}>
                                    {data.recent_documents.map((d) => (
                                        <div key={d.id} className="row" style={{ flexWrap: "nowrap" }}>
                                            <span className="file-icon"><FileIcon ext={d.ext} /></span>
                                            <div style={{ flex: 1, minWidth: 0 }}>
                                                <div className="truncate" title={d.name}>{d.name}</div>
                                                <div className="faint">{timeAgo(d.created_at)}{d.status === "ready" ? ` · ${d.chunk_count} sections` : ""}</div>
                                            </div>
                                            {d.status === "ready"
                                                ? <Link className="btn sm" to={`/chat?doc=${d.id}`}><FiMessageSquare /> Chat</Link>
                                                : <StatusBadge status={d.status} />}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="stack">
                            <div className="card">
                                <div className="card-title"><h2>Recent conversations</h2><Link to="/chat" className="faint">Open chat</Link></div>
                                {data.recent_conversations.length === 0 ? (
                                    <p className="muted" style={{ margin: 0 }}>Your chats will appear here. Ask a question about any document, or about any topic.</p>
                                ) : (
                                    <div className="stack" style={{ gap: 4 }}>
                                        {data.recent_conversations.map((c) => (
                                            <Link key={c.id} className="session" to={`/chat?session=${c.id}`}>
                                                <FiMessageSquare style={{ flex: "none" }} />
                                                <span className="truncate" style={{ flex: 1 }}>{c.title}</span>
                                                <span className="faint">{timeAgo(c.updated_at)}</span>
                                            </Link>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="card">
                                <div className="card-title"><h2>Recent activity</h2></div>
                                {data.activity.length === 0 ? (
                                    <p className="muted" style={{ margin: 0 }}>Nothing yet. Uploads, quizzes, decks and completed tasks are listed here as you use the app.</p>
                                ) : data.activity.map((a, i) => {
                                    const Icon = ACTIVITY_ICON[a.type] || FiActivity;
                                    return (
                                        <Link key={i} to={a.path} className="activity">
                                            <Icon style={{ flex: "none", color: "#a78bfa" }} />
                                            <span className="truncate" style={{ flex: 1 }}>{a.text}</span>
                                            <span className="faint">{timeAgo(a.at)}</span>
                                        </Link>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    <h2 style={{ margin: "24px 0 12px" }}>Learning tools</h2>
                    <div className="grid c3">
                        {SHORTCUTS.map((x) => (
                            <Link key={x.to} to={x.to} className="shortcut">
                                <span className="file-icon">{x.icon}</span>
                                <span><b>{x.title}</b><br /><span className="faint">{x.text}</span></span>
                            </Link>
                        ))}
                    </div>
                </>
            )}
        </>
    );
}
