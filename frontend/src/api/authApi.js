
import api from "./api";

// Register a new user
export const registerUser = async (userData) => {
    const response = await api.post("/register", userData);
    return response.data;
};

// Login user using form-urlencoded data
export const loginUser = async (email, password) => {
    const formData = new URLSearchParams();

    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(
        `${api.defaults.baseURL}/login`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            body: formData.toString(),
        }
    );

    const data = await response.json();

    if (!response.ok) {
        const error = new Error(
            typeof data.detail === "string"
                ? data.detail
                : "Login failed. Please check your credentials."
        );

        error.status = response.status;
        error.detail = data.detail;

        throw error;
    }

    return data;
};

// Get currently logged-in user
export const getCurrentUser = async () => {
    const response = await api.get("/me");
    return response.data;
};
