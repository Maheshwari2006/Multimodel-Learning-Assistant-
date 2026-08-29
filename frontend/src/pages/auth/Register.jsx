import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../../api/authApi";

function Register() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setLoading(true);
        setError("");
        setSuccess("");

        try {
            console.log("Sending:", formData);

            const data = await registerUser(formData);

            console.log("Response:", data);

            setSuccess("Registration Successful!");

            setTimeout(() => {
                navigate("/");
            }, 1500);

        } catch (err) {
            console.error("Register Error:", err);

            if (err.response) {
                console.log("Status:", err.response.status);
                console.log("Data:", err.response.data);

                setError(
                    err.response.data.detail ||
                    JSON.stringify(err.response.data)
                );
            } else if (err.request) {
                console.log("Request:", err.request);
                setError("Cannot connect to FastAPI server.");
            } else {
                console.log("Message:", err.message);
                setError(err.message);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                minHeight: "100vh",
                background: "#f3f4f6",
            }}
        >
            <form
                onSubmit={handleSubmit}
                style={{
                    width: "420px",
                    background: "#fff",
                    padding: "30px",
                    borderRadius: "10px",
                    boxShadow: "0 0 10px rgba(0,0,0,0.2)",
                }}
            >
                <h2 style={{ textAlign: "center" }}>Register</h2>

                <input
                    type="text"
                    name="username"
                    placeholder="Username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                    style={inputStyle}
                />

                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    style={inputStyle}
                />

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    style={inputStyle}
                />

                {error && (
                    <p style={{ color: "red", textAlign: "center" }}>
                        {error}
                    </p>
                )}

                {success && (
                    <p style={{ color: "green", textAlign: "center" }}>
                        {success}
                    </p>
                )}

                <button
                    type="submit"
                    disabled={loading}
                    style={{
                        width: "100%",
                        padding: "12px",
                        background: "#2563eb",
                        color: "white",
                        border: "none",
                        borderRadius: "5px",
                        cursor: "pointer",
                    }}
                >
                    {loading ? "Registering..." : "Register"}
                </button>

                <p style={{ textAlign: "center", marginTop: "20px" }}>
                    Already have an account?{" "}
                    <Link to="/">Login</Link>
                </p>
            </form>
        </div>
    );
}

const inputStyle = {
    width: "100%",
    padding: "12px",
    marginBottom: "15px",
    border: "1px solid #ccc",
    borderRadius: "5px",
    boxSizing: "border-box",
};

export default Register;