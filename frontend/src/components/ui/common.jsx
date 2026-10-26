import { Link } from "react-router-dom";
import { FiFile, FiFileText, FiImage, FiCode, FiGrid, FiLayers } from "react-icons/fi";

export function Skeleton({ width = "100%", height = 16, style }) {
    return <div className="skeleton" style={{ width, height, ...style }} aria-hidden="true" />;
}

export function SkeletonCard({ lines = 3 }) {
    return (
        <div className="card stack" aria-busy="true" aria-label="Loading">
            <Skeleton width="40%" height={18} />
            {Array.from({ length: lines }).map((_, i) => (
                <Skeleton key={i} width={`${90 - i * 12}%`} />
            ))}
        </div>
    );
}

export function EmptyState({ icon, title, children, action }) {
    return (
        <div className="empty">
            <div className="empty-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{children}</p>
            {action &&
                (action.to ? (
                    <Link to={action.to} className="btn primary">{action.label}</Link>
                ) : (
                    <button className="btn primary" onClick={action.onClick}>{action.label}</button>
                ))}
        </div>
    );
}

export function PageHeader({ title, subtitle, children }) {
    return (
        <div className="page-header row between">
            <div>
                <h1>{title}</h1>
                {subtitle && <p>{subtitle}</p>}
            </div>
            {children}
        </div>
    );
}

export function StatusBadge({ status }) {
    const map = {
        ready: ["ok", "Ready"],
        processing: ["info", "Processing…"],
        uploaded: ["info", "Queued"],
        failed: ["err", "Failed"],
    };
    const [cls, label] = map[status] || ["", status];
    return <span className={`badge ${cls}`}>{label}</span>;
}

export function FileIcon({ ext }) {
    if ([".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"].includes(ext)) return <FiImage />;
    if ([".xlsx", ".xlsm", ".csv", ".tsv"].includes(ext)) return <FiGrid />;
    if ([".pptx"].includes(ext)) return <FiLayers />;
    if ([".pdf", ".docx", ".txt", ".md", ".markdown"].includes(ext)) return <FiFileText />;
    if ([".json", ".xml", ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".cs", ".go", ".rs", ".sql", ".html", ".css"].includes(ext)) return <FiCode />;
    return <FiFile />;
}

export function formatBytes(n) {
    if (!n && n !== 0) return "";
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
    return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

export function timeAgo(iso) {
    if (!iso) return "";
    const diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} h ago`;
    if (diff < 86400 * 7) return `${Math.floor(diff / 86400)} d ago`;
    return new Date(iso).toLocaleDateString();
}

export async function copyText(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch {
        const ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        const ok = document.execCommand("copy");
        document.body.removeChild(ta);
        return ok;
    }
}

export function downloadText(filename, text, type = "text/markdown") {
    const url = URL.createObjectURL(new Blob([text], { type: `${type};charset=utf-8` }));
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

export const LANGUAGES = [
    { value: "english", label: "English" },
    { value: "hindi", label: "हिन्दी (Hindi)" },
    { value: "marathi", label: "मराठी (Marathi)" },
];
