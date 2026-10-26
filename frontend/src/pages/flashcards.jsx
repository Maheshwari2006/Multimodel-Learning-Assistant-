import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
    FiCheck, FiChevronLeft, FiChevronRight, FiEdit2, FiLayers, FiPlus, FiRefreshCw, FiRepeat, FiShuffle, FiTrash2, FiX,
} from "react-icons/fi";
import useDocuments from "../hooks/useDocuments";
import {
    deleteDeck, generateDeck, getDeck, listDecks, markCard, renameDeck, resetDeck,
} from "../api/learningApi";
import { errorMessage } from "../api/api";
import DocPicker from "../components/ui/DocPicker";
import { EmptyState, LANGUAGES, PageHeader, SkeletonCard } from "../components/ui/common";
import { useToast } from "../components/ui/Toast";

const FILTERS = [["all", "All"], ["new", "New"], ["review", "Needs review"], ["known", "Known"]];

function shuffled(n) {
    const a = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

export default function Flashcards() {
    const toast = useToast();
    const [params, setParams] = useSearchParams();
    const { docs, loading: docsLoading } = useDocuments();
    const [decks, setDecks] = useState(null);
    const [deck, setDeck] = useState(null);                   // {id, title, cards:[{id,question,answer,status}]}
    const [creating, setCreating] = useState(false);
    // create form
    const [source, setSource] = useState("docs");
    const [selected, setSelected] = useState([]);
    const [text, setText] = useState("");
    const [count, setCount] = useState(10);
    const [language, setLanguage] = useState("english");
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    // study state
    const [order, setOrder] = useState([]);
    const [pos, setPos] = useState(0);
    const [flipped, setFlipped] = useState(false);
    const [filter, setFilter] = useState("all");
    const [renaming, setRenaming] = useState(null);

    const loadDecks = useCallback(() => listDecks().then(setDecks).catch((e) => { setDecks([]); setError(errorMessage(e)); }), []);
    useEffect(() => { loadDecks(); }, [loadDecks]);

    const openDeck = useCallback(async (id) => {
        try {
            const d = await getDeck(id);
            setDeck(d);
            setOrder(d.cards.map((_, i) => i));
            setPos(0);
            setFlipped(false);
            setFilter("all");
            setCreating(false);
            setParams({ deck: id });
        } catch (err) { toast.error(errorMessage(err)); }
    }, [toast, setParams]);

    useEffect(() => {
        const id = params.get("deck");
        if (id) openDeck(Number(id));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const visible = useMemo(
        () => (deck ? order.filter((i) => filter === "all" || deck.cards[i].status === filter) : []),
        [deck, order, filter]
    );
    const card = deck && visible.length ? deck.cards[visible[Math.min(pos, visible.length - 1)]] : null;

    const go = useCallback((delta) => {
        setFlipped(false);
        setPos((p) => Math.min(Math.max(p + delta, 0), Math.max(visible.length - 1, 0)));
    }, [visible.length]);

    const mark = useCallback(async (status) => {
        if (!card) return;
        const id = card.id;
        const previous = card.status;
        setDeck((d) => ({ ...d, cards: d.cards.map((c) => (c.id === id ? { ...c, status } : c)) }));
        try {
            await markCard(id, status);
            loadDecks();
            if (filter === "all") go(1);
        } catch (err) {
            setDeck((d) => ({ ...d, cards: d.cards.map((c) => (c.id === id ? { ...c, status: previous } : c)) }));
            toast.error(errorMessage(err));
        }
    }, [card, filter, go, loadDecks, toast]);

    useEffect(() => {
        if (!card) return undefined;
        const onKey = (e) => {
            if (["INPUT", "TEXTAREA", "SELECT", "BUTTON"].includes(e.target.tagName)) return;
            if (e.key === " " || e.key === "Enter") { e.preventDefault(); setFlipped((f) => !f); }
            if (e.key === "ArrowRight") go(1);
            if (e.key === "ArrowLeft") go(-1);
            if (e.key.toLowerCase() === "k") mark("known");
            if (e.key.toLowerCase() === "r") mark("review");
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [card, go, mark]);

    const create = async () => {
        setBusy(true);
        setError("");
        try {
            const d = await generateDeck(source === "docs" ? { document_ids: selected, count, language } : { text, count, language });
            toast.success(`Created "${d.title}" with ${d.cards.length} cards.`);
            await loadDecks();
            await openDeck(d.id);
        } catch (err) { setError(errorMessage(err)); } finally { setBusy(false); }
    };

    const remove = async (d) => {
        if (!window.confirm(`Delete deck "${d.title}" and its review progress?`)) return;
        try {
            await deleteDeck(d.id);
            if (deck?.id === d.id) { setDeck(null); setParams({}); }
            loadDecks();
        } catch (err) { toast.error(errorMessage(err)); }
    };

    const reset = async () => {
        if (!window.confirm("Reset all review progress for this deck?")) return;
        try { const d = await resetDeck(deck.id); setDeck(d); setPos(0); loadDecks(); } catch (err) { toast.error(errorMessage(err)); }
    };

    const saveName = async () => {
        const title = renaming.title.trim();
        if (!title) return;
        try {
            await renameDeck(renaming.id, title);
            if (deck?.id === renaming.id) setDeck((d) => ({ ...d, title }));
            setRenaming(null);
            loadDecks();
        } catch (err) { toast.error(errorMessage(err)); }
    };

    const showForm = creating || (!deck && decks !== null && decks.length === 0);
    const canCreate = source === "docs" ? selected.length > 0 : text.trim().length > 20;
    const counts = deck ? {
        known: deck.cards.filter((c) => c.status === "known").length,
        review: deck.cards.filter((c) => c.status === "review").length,
    } : { known: 0, review: 0 };

    return (
        <>
            <PageHeader title="Flashcards" subtitle="Turn documents or notes into decks, flip through them and mark what you know. Progress is saved.">
                {!showForm && <button className="btn primary" onClick={() => { setCreating(true); setDeck(null); setParams({}); }}><FiPlus /> New deck</button>}
            </PageHeader>

            <div className="split">
                <aside className="card stack" style={{ gap: 8 }}>
                    <div className="label">Your decks</div>
                    {decks === null ? <SkeletonCard lines={2} /> : decks.length === 0 ? <span className="faint">No decks yet.</span> : decks.map((d) => (
                        <div key={d.id} className={`session ${deck?.id === d.id ? "on" : ""}`} role="button" tabIndex={0}
                             onClick={() => openDeck(d.id)} onKeyDown={(e) => e.key === "Enter" && openDeck(d.id)}>
                            <FiLayers style={{ flex: "none" }} />
                            {renaming?.id === d.id ? (
                                <input className="input" autoFocus value={renaming.title} aria-label="Deck name" style={{ padding: "4px 8px" }}
                                       onClick={(e) => e.stopPropagation()} onChange={(e) => setRenaming({ ...renaming, title: e.target.value })}
                                       onKeyDown={(e) => { e.stopPropagation(); if (e.key === "Enter") saveName(); if (e.key === "Escape") setRenaming(null); }} />
                            ) : (
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div className="truncate" title={d.title}>{d.title}</div>
                                    <div className="progress" style={{ height: 5, marginTop: 4 }}><span style={{ width: `${d.total ? (d.known / d.total) * 100 : 0}%` }} /></div>
                                    <span className="faint" style={{ fontSize: 12 }}>{d.known}/{d.total} known{d.review ? ` · ${d.review} to review` : ""}</span>
                                </div>
                            )}
                            {renaming?.id === d.id ? (
                                <>
                                    <button className="btn icon sm" aria-label="Save name" onClick={(e) => { e.stopPropagation(); saveName(); }}><FiCheck /></button>
                                    <button className="btn icon sm" aria-label="Cancel" onClick={(e) => { e.stopPropagation(); setRenaming(null); }}><FiX /></button>
                                </>
                            ) : (
                                <>
                                    <button className="btn icon sm" aria-label={`Rename ${d.title}`} onClick={(e) => { e.stopPropagation(); setRenaming({ id: d.id, title: d.title }); }}><FiEdit2 /></button>
                                    <button className="btn icon sm" aria-label={`Delete ${d.title}`} onClick={(e) => { e.stopPropagation(); remove(d); }}><FiTrash2 /></button>
                                </>
                            )}
                        </div>
                    ))}
                </aside>

                <div>
                    {showForm && (
                        <div className="card stack rise">
                            <h2 style={{ margin: 0 }}>Create a deck</h2>
                            <div className="segmented">
                                <button className={source === "docs" ? "on" : ""} onClick={() => setSource("docs")}>From documents</button>
                                <button className={source === "text" ? "on" : ""} onClick={() => setSource("text")}>From pasted notes</button>
                            </div>
                            {source === "docs" ? (
                                <DocPicker docs={docs} loading={docsLoading} selected={selected} onChange={setSelected} />
                            ) : (
                                <textarea className="textarea" rows={7} value={text} aria-label="Notes" placeholder="Paste your notes here…" onChange={(e) => setText(e.target.value)} />
                            )}
                            <div className="grid c2" style={{ gap: 12 }}>
                                <div className="field">
                                    <label htmlFor="fc-count">Number of cards</label>
                                    <select id="fc-count" className="select" value={count} onChange={(e) => setCount(Number(e.target.value))}>
                                        {[5, 10, 15, 20, 30].map((n) => <option key={n} value={n}>{n}</option>)}
                                    </select>
                                </div>
                                <div className="field">
                                    <label htmlFor="fc-lang">Language</label>
                                    <select id="fc-lang" className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                                        {LANGUAGES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
                                    </select>
                                </div>
                            </div>
                            {error && <div className="alert err" role="alert">{error}</div>}
                            <div className="row">
                                <button className="btn primary" disabled={!canCreate || busy} onClick={create}>
                                    {busy ? <><span className="spinner" /> Writing cards…</> : "Generate deck"}
                                </button>
                                {decks?.length > 0 && <button className="btn" onClick={() => setCreating(false)}>Cancel</button>}
                            </div>
                        </div>
                    )}

                    {!showForm && !deck && (
                        <div className="card"><EmptyState icon={<FiLayers />} title="Pick a deck or create one">Select a deck on the left to start studying.</EmptyState></div>
                    )}

                    {!showForm && deck && (
                        <div className="stack rise">
                            <div className="row between">
                                <div>
                                    <h2 style={{ margin: 0 }}>{deck.title}</h2>
                                    <span className="faint">{counts.known} known · {counts.review} need review · {deck.cards.length - counts.known - counts.review} new</span>
                                </div>
                                <div className="row">
                                    <button className="btn sm" onClick={() => { setOrder(shuffled(deck.cards.length)); setPos(0); setFlipped(false); }}><FiShuffle /> Shuffle</button>
                                    <button className="btn sm" onClick={() => { setOrder(deck.cards.map((_, i) => i)); setPos(0); setFlipped(false); }}><FiRepeat /> Original order</button>
                                    <button className="btn sm" onClick={reset}><FiRefreshCw /> Reset progress</button>
                                </div>
                            </div>

                            <div className="progress" aria-label="Known cards"><span style={{ width: `${(counts.known / deck.cards.length) * 100}%` }} /></div>

                            <div className="row">
                                {FILTERS.map(([v, l]) => (
                                    <button key={v} className={`chip ${filter === v ? "on" : ""}`} aria-pressed={filter === v} onClick={() => { setFilter(v); setPos(0); setFlipped(false); }}>{l}</button>
                                ))}
                            </div>

                            {!card ? (
                                <div className="card"><EmptyState icon={<FiCheck />} title="No cards in this filter">Try another filter, or reset the deck's progress.</EmptyState></div>
                            ) : (
                                <>
                                    <div className={`flip ${flipped ? "flipped" : ""}`}>
                                        <div className="flip-inner" role="button" tabIndex={0} aria-label={flipped ? "Showing answer. Press to show question" : "Showing question. Press to show answer"}
                                             onClick={() => setFlipped((f) => !f)} onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), setFlipped((f) => !f))}>
                                            <div className="flip-face front" aria-hidden={flipped}><small>Question · click to flip</small>{card.question}</div>
                                            <div className="flip-face back" aria-hidden={!flipped}><small>Answer</small>{card.answer}</div>
                                        </div>
                                    </div>

                                    <div className="row between">
                                        <button className="btn" onClick={() => go(-1)} disabled={pos === 0}><FiChevronLeft /> Previous</button>
                                        <span className="faint">Card {Math.min(pos, visible.length - 1) + 1} of {visible.length}
                                            {card.status !== "new" && <> · <span className={`badge ${card.status === "known" ? "ok" : "warn"}`}>{card.status === "known" ? "Known" : "Needs review"}</span></>}
                                        </span>
                                        <button className="btn" onClick={() => go(1)} disabled={pos >= visible.length - 1}>Next <FiChevronRight /></button>
                                    </div>

                                    <div className="row" style={{ justifyContent: "center" }}>
                                        <button className="btn danger" onClick={() => mark("review")}><FiX /> Needs review</button>
                                        <button className="btn primary" onClick={() => mark("known")}><FiCheck /> I know this</button>
                                    </div>
                                    <p className="faint" style={{ textAlign: "center", margin: 0 }}>Keyboard: Space flips · ← → move · K known · R needs review</p>
                                </>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
