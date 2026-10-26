import { useState } from "react";
import { FiCheck, FiCopy } from "react-icons/fi";
import { copyText } from "./common";

/* Small, dependency-free and XSS-safe Markdown renderer (only builds React elements, never raw HTML).
   Supports headings, bold/italic, inline code, fenced code blocks, lists, quotes, tables, links and [n] citations. */

const INLINE = /(`[^`\n]+`|\*\*[^*\n]+\*\*|__[^_\n]+__|\*[^*\s][^*\n]*\*|\[[^\]\n]+\]\(https?:\/\/[^)\s]+\)|(?:\[\d{1,2}\])+)/g;

function inline(text, keyBase) {
    const out = [];
    let last = 0;
    let n = 0;
    for (const m of text.matchAll(INLINE)) {
        if (m.index > last) out.push(text.slice(last, m.index));
        const tok = m[0];
        const key = `${keyBase}-${n++}`;
        if (tok.startsWith("`")) out.push(<code key={key}>{tok.slice(1, -1)}</code>);
        else if (tok.startsWith("**") || tok.startsWith("__")) out.push(<strong key={key}>{inline(tok.slice(2, -2), key)}</strong>);
        else if (tok.startsWith("*")) out.push(<em key={key}>{inline(tok.slice(1, -1), key)}</em>);
        else if (/^\[\d/.test(tok)) {
            tok.match(/\d+/g).forEach((num, i) => out.push(<sup key={`${key}-${i}`} className="cite">{num}</sup>));
        } else {
            const mm = tok.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/);
            out.push(<a key={key} href={mm[2]} target="_blank" rel="noopener noreferrer">{mm[1]}</a>);
        }
        last = m.index + tok.length;
    }
    if (last < text.length) out.push(text.slice(last));
    return out;
}

function CodeBlock({ lang, code }) {
    const [copied, setCopied] = useState(false);
    return (
        <pre>
            <div className="pre-head">
                <span>{lang || "code"}</span>
                <button
                    className="btn sm"
                    onClick={async () => {
                        if (await copyText(code)) {
                            setCopied(true);
                            setTimeout(() => setCopied(false), 1500);
                        }
                    }}
                >
                    {copied ? <FiCheck /> : <FiCopy />} {copied ? "Copied" : "Copy"}
                </button>
            </div>
            <code>{code}</code>
        </pre>
    );
}

const splitRow = (line) => line.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
const isTableSep = (line) => /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(line);

export default function Markdown({ text = "" }) {
    const lines = String(text).replace(/\r\n/g, "\n").split("\n");
    const blocks = [];
    let i = 0;
    let key = 0;
    while (i < lines.length) {
        const line = lines[i];
        if (!line.trim()) { i++; continue; }

        const fence = line.match(/^\s*```(\w*)/);
        if (fence) {
            const code = [];
            i++;
            while (i < lines.length && !/^\s*```/.test(lines[i])) code.push(lines[i++]);
            i++;
            blocks.push(<CodeBlock key={key++} lang={fence[1]} code={code.join("\n")} />);
            continue;
        }
        const h = line.match(/^(#{1,4})\s+(.*)$/);
        if (h) {
            const Tag = `h${Math.min(h[1].length + 1, 4)}`;
            blocks.push(<Tag key={key++}>{inline(h[2], `h${key}`)}</Tag>);
            i++;
            continue;
        }
        if (line.includes("|") && i + 1 < lines.length && isTableSep(lines[i + 1])) {
            const head = splitRow(line);
            i += 2;
            const rows = [];
            while (i < lines.length && lines[i].includes("|") && lines[i].trim()) rows.push(splitRow(lines[i++]));
            blocks.push(
                <div className="table-wrap" key={key++}>
                    <table>
                        <thead><tr>{head.map((c, j) => <th key={j}>{inline(c, `th${j}`)}</th>)}</tr></thead>
                        <tbody>{rows.map((r, a) => <tr key={a}>{r.map((c, j) => <td key={j}>{inline(c, `td${a}-${j}`)}</td>)}</tr>)}</tbody>
                    </table>
                </div>
            );
            continue;
        }
        if (/^\s*([-*+]|\d+[.)])\s+/.test(line)) {
            const ordered = /^\s*\d+[.)]\s+/.test(line);
            const items = [];
            while (i < lines.length && /^\s*([-*+]|\d+[.)])\s+/.test(lines[i])) {
                items.push(lines[i].replace(/^\s*([-*+]|\d+[.)])\s+/, ""));
                i++;
            }
            const List = ordered ? "ol" : "ul";
            blocks.push(<List key={key++}>{items.map((t, j) => <li key={j}>{inline(t, `li${j}`)}</li>)}</List>);
            continue;
        }
        if (/^\s*>/.test(line)) {
            const q = [];
            while (i < lines.length && /^\s*>/.test(lines[i])) q.push(lines[i++].replace(/^\s*>\s?/, ""));
            blocks.push(<blockquote key={key++}>{inline(q.join(" "), `q${key}`)}</blockquote>);
            continue;
        }
        const para = [];
        while (i < lines.length && lines[i].trim() && !/^\s*(```|#{1,4}\s|>|([-*+]|\d+[.)])\s)/.test(lines[i])) para.push(lines[i++]);
        blocks.push(<p key={key++}>{para.map((p, j) => (<span key={j}>{j > 0 && <br />}{inline(p, `p${key}-${j}`)}</span>))}</p>);
    }
    return <div className="md">{blocks}</div>;
}
