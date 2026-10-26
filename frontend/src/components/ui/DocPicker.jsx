import { Link } from "react-router-dom";
import { FiFileText } from "react-icons/fi";
import { FileIcon, StatusBadge, EmptyState, Skeleton } from "./common";

/** Pick one or several uploaded documents. Only "ready" documents can be selected. */
export default function DocPicker({ docs, loading, selected, onChange, multiple = true }) {
    if (loading) {
        return (
            <div className="stack" aria-busy="true">
                <Skeleton height={42} />
                <Skeleton height={42} />
            </div>
        );
    }
    if (!docs.length) {
        return (
            <EmptyState icon={<FiFileText />} title="No documents yet" action={{ to: "/upload", label: "Upload a document" }}>
                Upload notes, slides, PDFs or spreadsheets and they will be available here.
            </EmptyState>
        );
    }
    const toggle = (id) => {
        if (!multiple) return onChange([id]);
        onChange(selected.includes(id) ? selected.filter((x) => x !== id) : [...selected, id]);
    };
    return (
        <div className="doc-list" role="group" aria-label="Documents">
            {docs.map((d) => {
                const ready = d.status === "ready";
                const on = selected.includes(d.id);
                return (
                    <label key={d.id} className={`doc-option ${on ? "on" : ""} ${ready ? "" : "disabled"}`}>
                        <input
                            type={multiple ? "checkbox" : "radio"}
                            name="doc-picker"
                            checked={on}
                            disabled={!ready}
                            onChange={() => toggle(d.id)}
                        />
                        <span className="file-icon" style={{ width: 30, height: 30, fontSize: 15 }}><FileIcon ext={d.ext} /></span>
                        <span className="truncate" style={{ flex: 1 }} title={d.name}>{d.name}</span>
                        {!ready && <StatusBadge status={d.status} />}
                    </label>
                );
            })}
            <Link to="/upload" className="faint" style={{ padding: "4px 2px" }}>+ Upload another document</Link>
        </div>
    );
}
