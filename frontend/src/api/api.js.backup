
import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        const url = error.config?.url || "";
        if (
            error.response?.status === 401 &&
            localStorage.getItem("token") &&
            !url.includes("/login")
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
    if (err?.code === "ECONNABORTED")
        return "The request took too long. Local models can be slow - please try again.";

    if (err?.code === "ERR_CANCELED")
        return "The request was cancelled.";

    if (err?.response) {
        const detail = err.response.data?.detail;

        if (typeof detail === "string") return detail;

        if (Array.isArray(detail) && detail.length) {
            return detail.map((d) => d.msg || String(d)).join(" ");
        }

        if (err.response.status >= 500)
            return "The server hit an error. Check the backend logs.";

        return fallback;
    }

    if (err?.request)
        return "Cannot reach the backend. Please check the backend deployment.";

    return err?.message || fallback;
}

export default api;