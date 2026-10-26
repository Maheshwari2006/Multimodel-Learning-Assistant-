import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
    FiUploadCloud, FiTrash2, FiRefreshCw, FiMessageSquare, FiFileText, FiHelpCircle, FiEye, FiAlertCircle, FiX,
} from "react-icons/fi";
import useDocuments from "../hooks/useDocuments";
import { deleteDocument, getSupported, previewDocument, retryDocument, uploadDocument } from "../api/learningApi";
import { errorMessage } from "../api/api";
import { PageHeader, EmptyState, FileIcon, StatusBadge, formatBytes, timeAgo, Skeleton } from "../components/ui/common";
import { useToast } from "../components/ui/Toast";

const FALLBACK_EXT = [".pdf", ".docx", ".pptx", ".xlsx", ".csv", ".txt", ".md", ".json", ".xml", ".png", ".jpg", ".jpeg", ".py", ".js"];

export default function Upload() {
    const toast = useToast();
    const { docs, loading, error, refresh } = useDocuments();
    const [queue, setQueue] = useState([]);             // files currently uploading or failed to upload
    const [drag, setDrag] = useState(false);
    const [limits, setLimits] = useState({ extensions: FALLBACK_EXT, max_upload_mb: 25 });
    const [preview, setPreview] = useState({});          // docId -> {loading, data}
    const inputRef = useRef(null);

    useEffect(() => { getSupported().then(setLimits).catch(() => {}); }, []);

    const validate = useCallback((file) => {
        const ext = "." + (file.name.split(".").pop() || "").toLowerCase();
        if (!limits.extensions.includes(ext)) return `"${ext}" files are not supported.`;
        if (file.size === 0) return "This file is empty.";
        if (file.size > limits.max_upload_mb * 1024 * 1024) return `Larger than the ${limits.max_upload_mb} MB limit.`;
        return null;
    }, [limits]);

    const patch = (key, changes) => setQueue((q) => q.map((i) => (i.key === key ? { ...i, ...changes } : i)));

    const startUpload = useCallback(async (item) => {
        patch(item.key, { status: "uploading", progress: 0, error: "" });
        try {
            await uploadDocument(item.file, (p) => patch(item.key, { progress: p }));
            setQueue((q) => q.filter((i) => i.key !== item.key));
            refresh();
        } catch (err) {
            patch(item.key, { status: "error", error: errorMessage(err, "Upload failed.") });
        }
    }, [refresh]);

    const addFiles = useCallback((fileList) => {
        const items = Array.from(fileList).map((file) => {
            const problem = validate(file);
            return { key: `${file.name}-${file.size}-${Math.random()}`, file, status: problem ? "error" : "queued", progress: 0, error: problem || "", invalid: !!problem };
        });
        setQueue((q) => [...q, ...items]);
        items.filter((i) => !i.invalid).forEach(startUpload);
    }, [validate, startUpload]);

    const onDrop = (e) => {
        e.preventDefault();
        setDrag(false);
        if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
    };

    const remove = async (doc) => {
        if (!window.confirm(`Delete "${doc.name}"? Its extracted content will be removed too.`)) return;
        try {
            await deleteDocument(doc.id);
            toast.success("Document deleted.");
            refresh();
        } catch (err) { toast.error(errorMessage(err)); }
    };

    const retry = async (doc) => {
        try { await retryDocument(doc.id); refresh(); } catch (err) { toast.error(errorMessage(err)); }
    };

    const togglePreview = async (doc) => {
        if (preview[doc.id]) return setPreview(({ [doc.id]: _, ...rest }) => rest);
        setPreview((p) => ({ ...p, [doc.id]: { loading: true } }));
        try {
            const data = await previewDocument(doc.id);
            setPreview((p) => ({ ...p, [doc.id]: { data } }));
        } catch (err) {
            setPreview(({ [doc.id]: _, ...rest }) => rest);
            toast.error(errorMessage(err));
        }
    };

    return (
        <>
            <PageHeader title="Upload documents" subtitle="Each file is read, split into searchable sections and made available to every learning feature." />

            <div
                className={`dropzone ${drag ? "drag" : ""}`}
                role="button"
                tabIndex={0}
                aria-label="Upload files: drop here or press Enter to choose"
                onClick={() => inputRef.current?.click()}
                onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), inputRef.current?.click())}
                onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
                onDragLeave={() => setDrag(false)}
                onDrop={onDrop}
            >
                <FiUploadCloud className="big" />
                <h2 style={{ margin: "8px 0 4px" }}>Drag & drop files here, or click to browse</h2>
                <p className="muted" style={{ margin: 0 }}>
                    PDF, Word, PowerPoint, Excel/CSV, text/Markdown, JSON/XML, images (OCR) and source code · up to {limits.max_upload_mb} MB each
                </p>
                <input
                    ref={inputRef}
                    type="file"
                    multiple
                    hidden
                    accept={limits.extensions.join(",")}
                    onChange={(e) => { addFiles(e.target.files); e.target.value = ""; }}
                />
            </div>

            {queue.length > 0 && (
                <div className="stack" style={{ marginTop: 18 }}>
                    {queue.map((item) => (
                        <div key={item.key} className="file-row">
                            <div className="file-icon"><FileIcon ext={"." + item.file.name.split(".").pop().toLowerCase()} /></div>
                            <div style={{ minWidth: 0 }}>
                                <div className="truncate">{item.file.name} <span className="faint">· {formatBytes(item.file.size)}</span></div>
                                {item.status === "error" ? (
                                    <div className="field-error row"><FiAlertCircle /> {item.error}</div>
                                ) : (
                                    <div className="progress" style={{ marginTop: 8 }} role="progressbar" aria-valuenow={item.progress} aria-valuemin={0} aria-valuemax={100}>
                                        <span style={{ width: `${item.progress}%` }} />
                                    </div>
                                )}
                            </div>
                            <div className="actions row">
                                {item.status === "uploading" && <span className="faint">{item.progress}%</span>}
                                {item.status === "error" && !item.invalid && (
                                    <button className="btn sm" onClick={() => startUpload(item)}><FiRefreshCw /> Retry</button>
                                )}
                                {item.status === "error" && (
                                    <button className="btn icon sm" aria-label="Dismiss" onClick={() => setQueue((q) => q.filter((i) => i.key !== item.key))}><FiX /></button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <h2 style={{ margin: "28px 0 12px" }}>Your documents</h2>
            {error && <div className="alert err" role="alert">{error}</div>}
            {loading ? (
                <div className="stack"><Skeleton height={70} /><Skeleton height={70} /></div>
            ) : docs.length === 0 ? (
                <div className="card">
                    <EmptyState icon={<FiFileText />} title="Nothing uploaded yet">
                        Your documents will show here with their processing status once uploaded.
                    </EmptyState>
                </div>
            ) : (
                <div className="stack">
                    {docs.map((d) => (
                        <div key={d.id} className="card" style={{ padding: 14 }}>
                            <div className="file-row" style={{ border: 0, background: "none", padding: 0 }}>
                                <div className="file-icon"><FileIcon ext={d.ext} /></div>
                                <div style={{ minWidth: 0 }}>
                                    <div className="row" style={{ gap: 8 }}>
                                        <span className="truncate" title={d.name}>{d.name}</span>
                                        <StatusBadge status={d.status} />
                                        {d.ocr_used && <span className="badge info">OCR</span>}
                                    </div>
                                    <div className="faint">
                                        {formatBytes(d.size_bytes)} · {d.ext.replace(".", "").toUpperCase()}
                                        {d.page_count ? ` · ${d.page_count} page${d.page_count === 1 ? "" : "s"}/slides` : ""}
                                        {d.status === "ready" ? ` · ${d.chunk_count} sections · ${d.char_count.toLocaleString()} characters` : ""}
                                        {" · "}{timeAgo(d.created_at)}
                                    </div>
                                    {d.status === "failed" && <div className="field-error row" style={{ marginTop: 4 }}><FiAlertCircle /> {d.error}</div>}
                                    {d.warnings?.length > 0 && d.status === "ready" && <div className="faint" style={{ color: "var(--amber)" }}>{d.warnings.join(" ")}</div>}
                                </div>
                                <div className="actions row">
                                    {d.status === "ready" && (
                                        <>
                                            <Link className="btn sm" to={`/chat?doc=${d.id}`}><FiMessageSquare /> Chat</Link>
                                            <Link className="btn sm" to={`/summary?doc=${d.id}`}><FiFileText /> Summary</Link>
                                            <Link className="btn sm" to={`/quiz?doc=${d.id}`}><FiHelpCircle /> Quiz</Link>
                                            <button className="btn sm tip" data-tip="Preview extracted text" onClick={() => togglePreview(d)}><FiEye /></button>
                                        </>
                                    )}
                                    {d.status === "failed" && <button className="btn sm" onClick={() => retry(d)}><FiRefreshCw /> Retry</button>}
                                    {d.status === "processing" && <span className="spinner" aria-label="Processing" />}
                                    <button className="btn sm danger" aria-label={`Delete ${d.name}`} onClick={() => remove(d)}><FiTrash2 /></button>
                                </div>
                            </div>
                            {preview[d.id] && (
                                <div className="stack" style={{ marginTop: 12 }}>
                                    {preview[d.id].loading ? <Skeleton height={60} /> : preview[d.id].data.chunks.map((c) => (
                                        <div key={c.idx} className="source">
                                            <b>{[c.page && `Page ${c.page}`, c.section].filter(Boolean).join(" · ") || `Section ${c.idx + 1}`}</b>
                                            <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>{c.text}</div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </>
    );
}
