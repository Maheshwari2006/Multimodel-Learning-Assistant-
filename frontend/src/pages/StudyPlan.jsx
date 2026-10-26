import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { FiCalendar, FiTrash2, FiEdit2, FiPlus, FiCheck, FiX, FiClock } from "react-icons/fi";
import useDocuments from "../hooks/useDocuments";
import { addTask, deletePlan, deleteTask, generatePlan, getPlan, listPlans, patchTask } from "../api/learningApi";
import { errorMessage } from "../api/api";
import DocPicker from "../components/ui/DocPicker";
import { EmptyState, LANGUAGES, PageHeader, SkeletonCard } from "../components/ui/common";
import { useToast } from "../components/ui/Toast";

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const today = () => new Date().toISOString().slice(0, 10);

function TaskRow({ task, onToggle, onSave, onDelete, overdue }) {
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState({ title: task.title, description: task.description, minutes: task.minutes });

    if (editing) {
        return (
            <div className="task" style={{ gridTemplateColumns: "1fr" }}>
                <input className="input" value={draft.title} aria-label="Task title" onChange={(e) => setDraft({ ...draft, title: e.target.value })} />
                <textarea className="textarea" rows={2} value={draft.description} aria-label="Task description" onChange={(e) => setDraft({ ...draft, description: e.target.value })} />
                <div className="row">
                    <input className="input" type="number" min={5} max={480} style={{ width: 110 }} value={draft.minutes} aria-label="Minutes" onChange={(e) => setDraft({ ...draft, minutes: Number(e.target.value) })} />
                    <span className="faint">minutes</span>
                    <button className="btn primary sm" disabled={!draft.title.trim()} onClick={async () => { if (await onSave(task.id, { ...draft, title: draft.title.trim() })) setEditing(false); }}><FiCheck /> Save</button>
                    <button className="btn sm" onClick={() => setEditing(false)}><FiX /> Cancel</button>
                </div>
            </div>
        );
    }
    return (
        <div className={`task ${task.done ? "done" : ""}`}>
            <input type="checkbox" checked={task.done} onChange={(e) => onToggle(task.id, e.target.checked)} aria-label={`Mark "${task.title}" ${task.done ? "not done" : "done"}`} />
            <div style={{ minWidth: 0 }}>
                <div className="task-title" style={{ fontWeight: 600 }}>{task.title}</div>
                {task.description && <div className="muted" style={{ fontSize: 14 }}>{task.description}</div>}
                <div className="faint row" style={{ gap: 6, marginTop: 4 }}>
                    <FiClock /> {task.minutes} min
                    {overdue && !task.done && <span className="badge err">Overdue</span>}
                </div>
            </div>
            <div className="row" style={{ gap: 4, flexWrap: "nowrap" }}>
                <button className="btn icon sm" aria-label="Edit task" onClick={() => setEditing(true)}><FiEdit2 /></button>
                <button className="btn icon sm danger" aria-label="Delete task" onClick={() => onDelete(task.id)}><FiTrash2 /></button>
            </div>
        </div>
    );
}

export default function StudyPlan() {
    const toast = useToast();
    const [params, setParams] = useSearchParams();
    const { docs, loading: docsLoading } = useDocuments();
    const [plans, setPlans] = useState(null);
    const [plan, setPlan] = useState(null);                     // selected plan with tasks
    const [creating, setCreating] = useState(false);
    // form
    const [source, setSource] = useState(params.get("doc") ? "docs" : "topic");
    const [selected, setSelected] = useState(() => (params.get("doc") ? [Number(params.get("doc"))] : []));
    const [topic, setTopic] = useState("");
    const [days, setDays] = useState(7);
    const [hours, setHours] = useState(1);
    const [weekdays, setWeekdays] = useState([0, 1, 2, 3, 4, 5, 6]);
    const [start, setStart] = useState(today());
    const [language, setLanguage] = useState("english");
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [newTask, setNewTask] = useState({ day: 1, title: "" });

    const loadPlans = useCallback(() => listPlans().then(setPlans).catch((e) => { setPlans([]); setError(errorMessage(e)); }), []);
    const openPlan = useCallback(async (id) => {
        try { setPlan(await getPlan(id)); setCreating(false); setParams({ plan: id }); } catch (err) { toast.error(errorMessage(err)); }
    }, [toast, setParams]);

    useEffect(() => { loadPlans(); }, [loadPlans]);
    useEffect(() => {
        const id = params.get("plan");
        if (id) openPlan(Number(id));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const canRun = (source === "docs" ? selected.length > 0 : topic.trim().length > 1) && weekdays.length > 0;

    const create = async () => {
        setBusy(true);
        setError("");
        try {
            const created = await generatePlan({
                topic: source === "topic" ? topic.trim() : undefined,
                document_ids: source === "docs" ? selected : undefined,
                days, hours_per_day: hours, language, start_date: start,
                weekdays: weekdays.length === 7 ? undefined : weekdays,
            });
            setPlan(created);
            setCreating(false);
            setParams({ plan: created.id });
            loadPlans();
        } catch (err) {
            setError(errorMessage(err));
        } finally {
            setBusy(false);
        }
    };

    const refreshPlan = async () => { if (plan) { setPlan(await getPlan(plan.id)); loadPlans(); } };

    const toggle = async (id, done) => {
        setPlan((p) => ({ ...p, tasks: p.tasks.map((t) => (t.id === id ? { ...t, done } : t)) }));   // optimistic
        try { await patchTask(id, { done }); await refreshPlan(); } catch (err) { toast.error(errorMessage(err)); refreshPlan(); }
    };
    const save = async (id, body) => {
        try { await patchTask(id, body); await refreshPlan(); return true; } catch (err) { toast.error(errorMessage(err)); return false; }
    };
    const removeTask = async (id) => {
        try { await deleteTask(id); await refreshPlan(); } catch (err) { toast.error(errorMessage(err)); }
    };
    const add = async () => {
        if (!newTask.title.trim()) return;
        try { await addTask(plan.id, { day: newTask.day, title: newTask.title.trim(), minutes: 30 }); setNewTask({ ...newTask, title: "" }); await refreshPlan(); } catch (err) { toast.error(errorMessage(err)); }
    };
    const removePlan = async (p) => {
        if (!window.confirm(`Delete plan "${p.title}"?`)) return;
        try { await deletePlan(p.id); if (plan?.id === p.id) { setPlan(null); setParams({}); } loadPlans(); } catch (err) { toast.error(errorMessage(err)); }
    };

    const byDay = useMemo(() => {
        const map = new Map();
        (plan?.tasks || []).forEach((t) => { if (!map.has(t.day)) map.set(t.day, []); map.get(t.day).push(t); });
        return [...map.entries()].sort((a, b) => a[0] - b[0]);
    }, [plan]);

    const showForm = creating || (!plan && plans !== null && plans.length === 0);

    return (
        <>
            <PageHeader title="Study plan" subtitle="Turn a document or topic into a day-by-day schedule, then tick tasks off as you go.">
                {!showForm && <button className="btn primary" onClick={() => { setCreating(true); setPlan(null); setParams({}); }}><FiPlus /> New plan</button>}
            </PageHeader>

            <div className="split">
                <aside className="card stack" style={{ gap: 8 }}>
                    <div className="label">Your plans</div>
                    {plans === null ? <SkeletonCard lines={2} /> : plans.length === 0 ? <span className="faint">No plans yet.</span> : plans.map((p) => (
                        <div key={p.id} className={`session ${plan?.id === p.id ? "on" : ""}`} role="button" tabIndex={0} onClick={() => openPlan(p.id)} onKeyDown={(e) => e.key === "Enter" && openPlan(p.id)}>
                            <FiCalendar style={{ flex: "none" }} />
                            <div style={{ flex: 1, minWidth: 0 }}>
                                <div className="truncate">{p.title}</div>
                                <div className="progress" style={{ height: 5, marginTop: 4 }}><span style={{ width: `${p.progress}%` }} /></div>
                            </div>
                            <span className="faint">{p.progress}%</span>
                            <button className="btn icon sm" aria-label={`Delete plan ${p.title}`} onClick={(e) => { e.stopPropagation(); removePlan(p); }}><FiTrash2 /></button>
                        </div>
                    ))}
                </aside>

                <div>
                    {showForm && (
                        <div className="card stack">
                            <h2 style={{ margin: 0 }}>Create a study plan</h2>
                            <div className="segmented">
                                <button className={source === "topic" ? "on" : ""} onClick={() => setSource("topic")}>A topic</button>
                                <button className={source === "docs" ? "on" : ""} onClick={() => setSource("docs")}>My documents</button>
                            </div>
                            {source === "topic" ? (
                                <div className="field">
                                    <label htmlFor="sp-topic">What do you want to learn?</label>
                                    <input id="sp-topic" className="input" value={topic} placeholder="e.g. Neural networks basics" onChange={(e) => setTopic(e.target.value)} />
                                </div>
                            ) : (
                                <DocPicker docs={docs} loading={docsLoading} selected={selected} onChange={setSelected} />
                            )}
                            <div className="grid c3" style={{ gap: 12 }}>
                                <div className="field">
                                    <label htmlFor="sp-days">Study days</label>
                                    <input id="sp-days" className="input" type="number" min={1} max={60} value={days} onChange={(e) => setDays(Math.min(60, Math.max(1, Number(e.target.value) || 1)))} />
                                </div>
                                <div className="field">
                                    <label htmlFor="sp-hours">Hours per day</label>
                                    <input id="sp-hours" className="input" type="number" min={0.5} max={8} step={0.5} value={hours} onChange={(e) => setHours(Math.min(8, Math.max(0.5, Number(e.target.value) || 1)))} />
                                </div>
                                <div className="field">
                                    <label htmlFor="sp-start">Start date</label>
                                    <input id="sp-start" className="input" type="date" min={today()} value={start} onChange={(e) => setStart(e.target.value)} />
                                </div>
                            </div>
                            <div className="field">
                                <span className="label">Days of the week you can study</span>
                                <div className="row" style={{ gap: 6 }}>
                                    {WEEKDAYS.map((d, i) => (
                                        <button key={d} className={`chip ${weekdays.includes(i) ? "on" : ""}`} aria-pressed={weekdays.includes(i)}
                                                onClick={() => setWeekdays((w) => (w.includes(i) ? w.filter((x) => x !== i) : [...w, i].sort()))}>{d}</button>
                                    ))}
                                </div>
                                {weekdays.length === 0 && <span className="field-error">Choose at least one day.</span>}
                            </div>
                            <div className="field">
                                <label htmlFor="sp-lang">Language</label>
                                <select id="sp-lang" className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                                    {LANGUAGES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
                                </select>
                            </div>
                            {error && <div className="alert err" role="alert">{error}</div>}
                            <div className="row">
                                <button className="btn primary" disabled={!canRun || busy} onClick={create}>{busy ? <><span className="spinner" /> Planning…</> : "Generate plan"}</button>
                                {plans?.length > 0 && <button className="btn" onClick={() => setCreating(false)}>Cancel</button>}
                            </div>
                        </div>
                    )}

                    {!showForm && !plan && (
                        <div className="card"><EmptyState icon={<FiCalendar />} title="Pick a plan or create a new one">Select a plan on the left to see its tasks and progress.</EmptyState></div>
                    )}

                    {!showForm && plan && (
                        <div className="card rise">
                            <div className="row between">
                                <div>
                                    <h2 style={{ margin: 0 }}>{plan.title}</h2>
                                    <span className="faint">{plan.done}/{plan.total} tasks done{plan.overdue ? ` · ${plan.overdue} overdue` : ""}</span>
                                </div>
                                <b style={{ fontSize: 24 }}>{plan.progress}%</b>
                            </div>
                            <div className="progress" style={{ margin: "10px 0 4px" }}><span style={{ width: `${plan.progress}%` }} /></div>

                            {byDay.map(([day, tasks]) => (
                                <div key={day}>
                                    <div className="day-head">
                                        Day {day}
                                        {tasks[0].scheduled_date && <span className="faint">{new Date(tasks[0].scheduled_date + "T00:00:00").toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" })}</span>}
                                    </div>
                                    <div className="stack" style={{ gap: 8 }}>
                                        {tasks.map((t) => (
                                            <TaskRow key={t.id} task={t} onToggle={toggle} onSave={save} onDelete={removeTask} overdue={!!t.scheduled_date && t.scheduled_date < today()} />
                                        ))}
                                    </div>
                                </div>
                            ))}

                            <div className="day-head">Add a task</div>
                            <div className="row">
                                <select className="select" style={{ width: 110 }} aria-label="Day" value={newTask.day} onChange={(e) => setNewTask({ ...newTask, day: Number(e.target.value) })}>
                                    {Array.from({ length: plan.days }, (_, i) => <option key={i} value={i + 1}>Day {i + 1}</option>)}
                                </select>
                                <input className="input" style={{ flex: 1, minWidth: 180 }} placeholder="e.g. Re-read chapter 2" aria-label="New task title" value={newTask.title}
                                       onChange={(e) => setNewTask({ ...newTask, title: e.target.value })} onKeyDown={(e) => e.key === "Enter" && add()} />
                                <button className="btn" onClick={add} disabled={!newTask.title.trim()}><FiPlus /> Add</button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
