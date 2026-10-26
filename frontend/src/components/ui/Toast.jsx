import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { FiAlertCircle, FiCheckCircle, FiInfo, FiX } from "react-icons/fi";

const ToastContext = createContext({ notify: () => {} });
export const useToast = () => useContext(ToastContext);

export function ToastProvider({ children }) {
    const [toasts, setToasts] = useState([]);

    const dismiss = useCallback((id) => setToasts((t) => t.filter((x) => x.id !== id)), []);

    const notify = useCallback((message, type = "info") => {
        const id = Date.now() + Math.random();
        setToasts((t) => [...t.slice(-3), { id, message, type }]);
        setTimeout(() => dismiss(id), type === "error" ? 7000 : 3500);
    }, [dismiss]);

    const value = useMemo(() => ({
        notify,
        success: (m) => notify(m, "success"),
        error: (m) => notify(m, "error"),
    }), [notify]);

    const Icon = { success: FiCheckCircle, error: FiAlertCircle, info: FiInfo };

    return (
        <ToastContext.Provider value={value}>
            {children}
            <div className="toast-wrap" role="status" aria-live="polite">
                {toasts.map((t) => {
                    const I = Icon[t.type] || FiInfo;
                    return (
                        <div key={t.id} className={`toast ${t.type}`}>
                            <I style={{ marginTop: 2, flex: "none" }} />
                            <div style={{ flex: 1 }}>{t.message}</div>
                            <button className="btn icon sm" aria-label="Dismiss" onClick={() => dismiss(t.id)}>
                                <FiX />
                            </button>
                        </div>
                    );
                })}
            </div>
        </ToastContext.Provider>
    );
}
