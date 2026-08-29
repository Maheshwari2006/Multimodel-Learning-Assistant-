import api from "./api";

export const registerUser = async (userData) => {
    const response = await api.post("/register", userData);
    return response.data;
};

export const loginUser = async (email, password) => {
    const formData = new FormData();

    formData.append("username", email);
    formData.append("password", password);

    const response = await api.post("/login", formData);

    return response.data;
};

export const getCurrentUser = async () => {
    const response = await api.get("/me");
    return response.data;
};