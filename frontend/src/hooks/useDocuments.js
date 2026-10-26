import { useCallback, useEffect, useRef, useState } from "react";
import { listDocuments } from "../api/learningApi";
import { errorMessage } from "../api/api";

const BUSY = ["uploaded", "processing"];

/** Loads the user's documents and keeps polling while any are still being processed. */
export default function useDocuments() {
    const [docs, setDocs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const timer = useRef(null);

    const refresh = useCallback(async () => {
        try {
            const data = await listDocuments();
            setDocs(data);
            setError("");
            return data;
        } catch (err) {
            setError(errorMessage(err, "Could not load your documents."));
            return [];
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        refresh();
        return () => clearTimeout(timer.current);
    }, [refresh]);

    const busy = docs.some((d) => BUSY.includes(d.status));
    useEffect(() => {
        if (!busy) return undefined;
        timer.current = setTimeout(refresh, 1500);
        return () => clearTimeout(timer.current);
    }, [busy, docs, refresh]);

    return { docs, loading, error, refresh, setDocs };
}
