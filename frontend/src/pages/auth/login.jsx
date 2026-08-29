import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

import { loginUser } from "../../api/authApi";

function Login() {

    const navigate = useNavigate();

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");

    const [error, setError] = useState("");

    const handleLogin = async (e) => {

        e.preventDefault();

        setError("");

        try {

            const data = await loginUser(
                email,
                password
            );

            localStorage.setItem(
                "token",
                data.access_token
            );

            navigate("/dashboard");

        }

        catch {

            setError("Invalid Email or Password");

        }

    };

    return (

        <div
            style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                height: "100vh",
                background: "#f5f5f5"
            }}
        >

            <form
                onSubmit={handleLogin}
                style={{
                    width: "350px",
                    padding: "30px",
                    background: "white",
                    borderRadius: "10px",
                    boxShadow: "0px 0px 10px gray"
                }}
            >

                <h2
                    style={{
                        textAlign: "center"
                    }}
                >
                    Login
                </h2>

                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e)=>setEmail(e.target.value)}
                    style={{
                        width:"100%",
                        padding:"10px",
                        marginTop:"20px"
                    }}
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e)=>setPassword(e.target.value)}
                    style={{
                        width:"100%",
                        padding:"10px",
                        marginTop:"15px"
                    }}
                />

                {

                    error &&

                    <p style={{color:"red"}}>

                        {error}

                    </p>

                }

                <button
                    style={{
                        width:"100%",
                        marginTop:"20px",
                        padding:"10px"
                    }}
                >

                    Login

                </button>

                <p
                    style={{
                        textAlign:"center",
                        marginTop:"15px"
                    }}
                >

                    Don't have an account?

                    <Link to="/register">

                        Register

                    </Link>

                </p>

            </form>

        </div>

    );

}

export default Login;