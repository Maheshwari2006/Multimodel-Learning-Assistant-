import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// An expired or invalid token sends the user back to the login page (but a wrong password on /login must not).
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const url = error.config?.url || "";
        if (error.response?.status === 401 && localStorage.getItem("token") && !url.includes("/login")) {
            localStorage.removeItem("token");
            window.location.assign("/");
        }
        return Promise.reject(error);
    }
);

/** Turn any axios/FastAPI error into a sentence a person can act on. */
export function errorMessage(err, fallback = "Something went wrong. Please try again.") {
    if (err?.code === "ECONNABORTED") return "The request took too long. Local models can be slow - please try again.";
    if (err?.code === "ERR_CANCELED") return "The request was cancelled.";
    if (err?.response) {
        const detail = err.response.data?.detail;
        if (typeof detail === "string") return detail;
        if (Array.isArray(detail) && detail.length) {
            return detail.map((d) => d.msg || String(d)).join(" ");
        }
        if (err.response.status >= 500) return "The server hit an error. Check the backend terminal for details.";
        return fallback;
    }
    if (err?.request) return "Cannot reach the backend. Make sure FastAPI is running on http://127.0.0.1:8000.";
    return err?.message || fallback;
}

export default api;
