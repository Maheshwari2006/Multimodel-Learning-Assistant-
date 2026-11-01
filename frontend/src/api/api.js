
import axios from "axios";

const API_BASE_URL = (
    import.meta.env.VITE_API_BASE_URL ||
    (import.meta.env.PROD
        ? "https://multimodel-learning-backend.vercel.app"
        : "http://127.0.0.1:8000")
).replace(/\/+$/, "");

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 120000,
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        const url = error.config?.url || "";

        if (
            error.response?.status === 401 &&
            localStorage.getItem("token") &&
            !url.includes("/login") &&
            !url.includes("/register")
        ) {
            localStorage.removeItem("token");
            window.location.assign("/");
        }

        return Promise.reject(error);
    }
);

export function errorMessage(
    err,
    fallback = "Something went wrong. Please try again."
) {
    if (err?.code === "ECONNABORTED") {
        return "The request took too long. Please try again.";
    }

    if (err?.code === "ERR_CANCELED") {
        return "The request was cancelled.";
    }

    if (err?.response) {
        const detail = err.response.data?.detail;

        if (typeof detail === "string") {
            return detail;
        }

        if (Array.isArray(detail) && detail.length) {
            return detail
                .map((item) => item.msg || String(item))
                .join(" ");
        }

        if (err.response.status === 401) {
            return "Your session has expired. Please log in again.";
        }

        if (err.response.status === 403) {
            return "You don't have permission to perform this action.";
        }

        if (err.response.status === 404) {
            return "The requested API endpoint was not found.";
        }

        if (err.response.status === 429) {
            return "Too many requests. Please wait and try again.";
        }

        if (err.response.status >= 500) {
            return "The server encountered an error. Check backend logs.";
        }

        return fallback;
    }

    if (err?.request) {
        return "Cannot reach the backend. Check the API URL and CORS settings.";
    }

    return err?.message || fallback;
}

export default api;
