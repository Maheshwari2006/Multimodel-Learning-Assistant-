import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { FiCopy, FiDownload, FiFileText } from "react-icons/fi";
import useDocuments from "../hooks/useDocuments";
import { generateSummary, getSummary, summaryHistory } from "../api/learningApi";
import { errorMessage } from "../api/api";
import DocPicker from "../components/ui/DocPicker";
import Markdown from "../components/ui/Markdown";
import { LANGUAGES, PageHeader, copyText, downloadText, timeAgo, SkeletonCard } from "../components/ui/common";
import { useToast } from "../components/ui/Toast";

const LENGTHS = [["short", "Short"], ["medium", "Medium"], ["detailed", "Detailed"]];

function toMarkdown(r) {
    const parts = [`# Summary: ${r.title}`, "", r.summary];
    if (r.key_points?.length) parts.push("", "## Key points", ...r.key_points.map((k) => `- ${k}`));
    if (r.definitions?.length) parts.push("", "## Important definitions", ...r.definitions.map((d) => `- **${d.term}**: ${d.definition}`));
    if (r.sections?.length) parts.push("", "## Section summaries", ...r.sections.map((s) => `### ${s.title}\n${s.summary}`));
    return parts.join("\n");
}

export default function Summary() {
    const toast = useToast();
    const [params] = useSearchParams();
    const { docs, loading: docsLoading } = useDocuments();
    const [source, setSource] = useState("docs");
    const [selected, setSelected] = useState(() => (params.get("doc") ? [Number(params.get("doc"))] : []));
    const [text, setText] = useState("");
    const [length, setLength] = useState("medium");
    const [language, setLanguage] = useState("english");
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [result, setResult] = useState(null);
    const [tab, setTab] = useState("summary");
    const [history, setHistory] = useState([]);

    const loadHistory = () => summaryHistory().then(setHistory).catch(() => {});
    useEffect(() => { loadHistory(); }, []);

    const canRun = source === "docs" ? selected.length > 0 : text.trim().length > 20;

    const run = async () => {
        setBusy(true);
        setError("");
        try {
            const payload = source === "docs" ? { document_ids: selected, length, language } : { text, length, language };
            const r = await generateSummary(payload);
            setResult(r);
            setTab("summary");
            loadHistory();
        } catch (err) {
            setError(errorMessage(err));
        } finally {
            setBusy(false);
        }
    };

    const open = async (id) => {
        try { setResult(await getSummary(id)); setTab("summary"); } catch (err) { toast.error(errorMessage(err)); }
    };

    const tabs = result ? [
        ["summary", "Summary"],
        ...(result.key_points?.length ? [["points", `Key points (${result.key_points.length})`]] : []),
        ...(result.definitions?.length ? [["defs", `Definitions (${result.definitions.length})`]] : []),
        ...(result.sections?.length ? [["sections", `Chapters (${result.sections.length})`]] : []),
    ] : [];

    return (
        <>
            <PageHeader title="Summaries" subtitle="Short, medium or detailed summaries with key points, definitions and chapter-wise notes." />
            <div className="split">
                <div className="card stack">
                    <div className="segmented" role="tablist" aria-label="Source">
                        <button className={source === "docs" ? "on" : ""} onClick={() => setSource("docs")}>Documents</button>
                        <button className={source === "text" ? "on" : ""} onClick={() => setSource("text")}>Paste text</button>
                    </div>

                    {source === "docs" ? (
                        <DocPicker docs={docs} loading={docsLoading} selected={selected} onChange={setSelected} />
                    ) : (
                        <textarea className="textarea" rows={8} value={text} placeholder="Paste the text you want summarised…" aria-label="Text to summarise" onChange={(e) => setText(e.target.value)} />
                    )}

                    <div className="field">
                        <span className="label">Length</span>
                        <div className="segmented">
                            {LENGTHS.map(([v, l]) => <button key={v} className={length === v ? "on" : ""} onClick={() => setLength(v)}>{l}</button>)}
                        </div>
                    </div>
                    <div className="field">
                        <label htmlFor="sum-lang">Language</label>
                        <select id="sum-lang" className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                            {LANGUAGES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
                        </select>
                    </div>
                    <button className="btn primary" disabled={!canRun || busy} onClick={run}>
                        {busy ? <><span className="spinner" /> Summarising…</> : "Generate summary"}
                    </button>
                    {busy && <p className="faint" style={{ margin: 0 }}>Local models can take a minute on long documents.</p>}

                    {history.length > 0 && (
                        <>
                            <div className="label">Previous summaries</div>
                            <div className="stack" style={{ gap: 4 }}>
                                {history.slice(0, 6).map((h) => (
                                    <button key={h.id} className="session" onClick={() => open(h.id)} style={{ background: "none" }}>
                                        <FiFileText style={{ flex: "none" }} />
                                        <span className="truncate" style={{ flex: 1, textAlign: "left" }}>{h.title}</span>
                                        <span className="faint">{timeAgo(h.created_at)}</span>
                                    </button>
                                ))}
                            </div>
                        </>
                    )}
                </div>

                <div>
                    {error && <div className="alert err" role="alert">{error}</div>}
                    {busy && <SkeletonCard lines={6} />}
                    {!busy && !result && !error && (
                        <div className="card empty">
                            <div className="empty-icon"><FiFileText /></div>
                            <h3>Your summary will appear here</h3>
                            <p>Choose one or more documents (or paste text), pick a length and language, then generate.</p>
                        </div>
                    )}
                    {!busy && result && (
                        <div className="card rise">
                            <div className="row between" style={{ marginBottom: 8 }}>
                                <div>
                                    <h2 style={{ margin: 0 }}>{result.title}</h2>
                                    <span className="faint">{result.length} · {result.language}</span>
                                </div>
                                <div className="row">
                                    <button className="btn sm" onClick={async () => (await copyText(toMarkdown(result))) && toast.success("Copied to clipboard")}><FiCopy /> Copy</button>
                                    <button className="btn sm" onClick={() => downloadText(`${result.title.replace(/[^\w-]+/g, "_")}_summary.md`, toMarkdown(result))}><FiDownload /> Download</button>
                                </div>
                            </div>
                            {result.coverage === "sampled" && (
                                <div className="alert warn" style={{ marginBottom: 12 }}>
                                    This material is longer than the model can read at once, so the summary is based on sections sampled evenly
                                    across it. Choose <b>Detailed</b> for a chapter-by-chapter pass over everything.
                                </div>
                            )}
                            <div className="tabs" role="tablist">
                                {tabs.map(([v, l]) => <button key={v} className={tab === v ? "on" : ""} onClick={() => setTab(v)}>{l}</button>)}
                            </div>
                            {tab === "summary" && <Markdown text={result.summary} />}
                            {tab === "points" && <Markdown text={result.key_points.map((k) => `- ${k}`).join("\n")} />}
                            {tab === "defs" && (
                                <div className="stack">
                                    {result.definitions.map((d, i) => (
                                        <div key={i} className="source"><b>{d.term}</b><div style={{ marginTop: 4 }}>{d.definition}</div></div>
                                    ))}
                                </div>
                            )}
                            {tab === "sections" && (
                                <div className="stack">
                                    {result.sections.map((s, i) => (
                                        <div key={i}><h3 style={{ margin: "0 0 4px" }}>{s.title}</h3><p className="muted" style={{ margin: 0 }}>{s.summary}</p></div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
