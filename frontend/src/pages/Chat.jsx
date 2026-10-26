import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { FiSend, FiPlus, FiTrash2, FiCopy, FiCheck, FiRefreshCw, FiMessageSquare, FiChevronDown, FiChevronUp, FiFileText, FiUser } from "react-icons/fi";
import useDocuments from "../hooks/useDocuments";
import { deleteSession, getSession, listSessions, sendChat } from "../api/learningApi";
import { errorMessage } from "../api/api";
import DocPicker from "../components/ui/DocPicker";
import Markdown from "../components/ui/Markdown";
import { LANGUAGES, copyText, timeAgo } from "../components/ui/common";
import { useToast } from "../components/ui/Toast";

function Sources({ sources }) {
    const [open, setOpen] = useState(false);
    if (!sources?.length) return null;
    return (
        <div style={{ marginTop: 10 }}>
            <button className="btn sm" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
                {open ? <FiChevronUp /> : <FiChevronDown />} {sources.length} source{sources.length === 1 ? "" : "s"}
            </button>
            {open && (
                <div className="sources">
                    {sources.map((s) => (
                        <div key={s.index} className="source">
                            <b>[{s.index}] {s.document_name}</b>
                            {s.page ? ` · page ${s.page}` : ""}{s.section ? ` · ${s.section}` : ""}
                            <div style={{ marginTop: 4 }}>{s.snippet}…</div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

function Message({ m, onRetry }) {
    const [copied, setCopied] = useState(false);
    const isUser = m.role === "user";
    return (
        <div className={`msg ${isUser ? "user" : "assistant"} rise`}>
            <div className="avatar" aria-hidden="true">{isUser ? <FiUser /> : "✦"}</div>
            <div style={{ minWidth: 0 }}>
                <div className="bubble" style={m.error ? { borderColor: "rgba(248,113,113,.5)" } : undefined}>
                    {isUser || m.error ? <span style={{ whiteSpace: "pre-wrap" }}>{m.content}</span> : <Markdown text={m.content} />}
                </div>
                {!isUser && !m.error && (
                    <>
                        <div className="msg-actions">
                            <span className={`badge ${m.mode === "document" ? "ok" : "info"}`}>
                                {m.mode === "document" ? "From your documents" : "General AI knowledge"}
                            </span>
                            <button
                                className="btn sm"
                                onClick={async () => {
                                    if (await copyText(m.content)) { setCopied(true); setTimeout(() => setCopied(false), 1500); }
                                }}
                            >
                                {copied ? <FiCheck /> : <FiCopy />} {copied ? "Copied" : "Copy"}
                            </button>
                        </div>
                        <Sources sources={m.sources} />
                    </>
                )}
                {m.error && <div className="msg-actions"><button className="btn sm" onClick={onRetry}><FiRefreshCw /> Retry</button></div>}
            </div>
        </div>
    );
}

export default function Chat() {
    const toast = useToast();
    const [params, setParams] = useSearchParams();
    const { docs, loading: docsLoading } = useDocuments();
    const [selected, setSelected] = useState(() => (params.get("doc") ? [Number(params.get("doc"))] : []));
    const [language, setLanguage] = useState("english");
    const [sessions, setSessions] = useState([]);
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [sending, setSending] = useState(false);
    const scrollRef = useRef(null);

    const refreshSessions = useCallback(() => listSessions().then(setSessions).catch(() => {}), []);
    useEffect(() => { refreshSessions(); }, [refreshSessions]);

    const openSession = useCallback(async (id) => {
        try {
            const s = await getSession(id);
            setSessionId(s.id);
            setMessages(s.messages);
            setSelected(s.document_ids);
        } catch (err) { toast.error(errorMessage(err)); }
    }, [toast]);

    useEffect(() => {
        const sid = params.get("session");
        if (sid) openSession(Number(sid));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }, [messages, sending]);

    const newChat = () => {
        setSessionId(null);
        setMessages([]);
        setInput("");
        setParams({});
    };

    const ask = useCallback(async (text, { addUser = true } = {}) => {
        setSending(true);
        if (addUser) setMessages((m) => [...m, { role: "user", content: text }]);
        try {
            const res = await sendChat({ message: text, session_id: sessionId, document_ids: selected, language });
            setSessionId(res.session_id);
            setMessages((m) => [...m, { ...res.message }]);
            refreshSessions();
        } catch (err) {
            setMessages((m) => [...m, { role: "assistant", content: errorMessage(err), error: true, retryText: text }]);
        } finally {
            setSending(false);
        }
    }, [sessionId, selected, language, refreshSessions]);

    const submit = () => {
        const text = input.trim();
        if (!text || sending) return;
        setInput("");
        ask(text);
    };

    const retry = (index) => {
        const failed = messages[index];
        setMessages((m) => m.filter((_, i) => i !== index));
        ask(failed.retryText, { addUser: false });
    };

    const removeSession = async (id) => {
        if (!window.confirm("Delete this conversation?")) return;
        try {
            await deleteSession(id);
            if (id === sessionId) newChat();
            refreshSessions();
        } catch (err) { toast.error(errorMessage(err)); }
    };

    const suggestions = selected.length
        ? ["Summarise this document in 5 bullet points", "What are the key definitions?", "Explain the hardest concept simply"]
        : ["Explain overfitting with an example", "What is the difference between supervised and unsupervised learning?"];

    return (
        <div className="chat-layout">
            <aside className="card chat-side">
                <button className="btn primary" onClick={newChat}><FiPlus /> New chat</button>

                <div>
                    <div className="label" style={{ marginBottom: 6 }}>Documents for this chat</div>
                    <DocPicker docs={docs} loading={docsLoading} selected={selected} onChange={setSelected} />
                </div>

                <div className="field">
                    <label htmlFor="chat-lang">Answer language</label>
                    <select id="chat-lang" className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                        {LANGUAGES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
                    </select>
                </div>

                <div className="label">History</div>
                <div className="chat-sessions">
                    {sessions.length === 0 && <span className="faint">No saved chats yet.</span>}
                    {sessions.map((s) => (
                        <div key={s.id} className={`session ${s.id === sessionId ? "on" : ""}`} onClick={() => openSession(s.id)} role="button" tabIndex={0}
                             onKeyDown={(e) => e.key === "Enter" && openSession(s.id)}>
                            <FiMessageSquare style={{ flex: "none" }} />
                            <span className="truncate" style={{ flex: 1 }} title={s.title}>{s.title}</span>
                            <button className="btn icon sm" aria-label={`Delete chat ${s.title}`} onClick={(e) => { e.stopPropagation(); removeSession(s.id); }}><FiTrash2 /></button>
                        </div>
                    ))}
                </div>
            </aside>

            <section className="card chat-main">
                <div className="chat-scroll" ref={scrollRef} aria-live="polite">
                    {messages.length === 0 && (
                        <div className="empty" style={{ margin: "auto" }}>
                            <div className="empty-icon"><FiMessageSquare /></div>
                            <h3>{selected.length ? "Ask anything about your documents" : "Ask me anything"}</h3>
                            <p>
                                {selected.length
                                    ? "Answers are grounded in the selected documents and cite the pages or sections they came from."
                                    : "No document selected, so I'll answer from general knowledge. Select a document to get answers from your own material."}
                            </p>
                            <div className="row" style={{ justifyContent: "center" }}>
                                {suggestions.map((s) => <button key={s} className="chip" onClick={() => ask(s)}>{s}</button>)}
                            </div>
                        </div>
                    )}
                    {messages.map((m, i) => <Message key={m.id || i} m={m} onRetry={() => retry(i)} />)}
                    {sending && (
                        <div className="msg assistant"><div className="avatar">✦</div>
                            <div className="bubble typing" aria-label="Assistant is typing"><span /><span /><span /></div>
                        </div>
                    )}
                </div>

                <div className="composer">
                    {selected.length > 0 && <span className="badge ok tip" data-tip="Documents used for answers"><FiFileText /> {selected.length}</span>}
                    <textarea
                        className="textarea"
                        rows={1}
                        value={input}
                        placeholder={selected.length ? "Ask about your documents…  (Enter to send, Shift+Enter for a new line)" : "Ask a question…  (Enter to send)"}
                        aria-label="Message"
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
                    />
                    <button className="btn primary" onClick={submit} disabled={sending || !input.trim()} aria-label="Send">
                        {sending ? <span className="spinner" /> : <FiSend />}
                    </button>
                </div>
            </section>
        </div>
    );
}
