import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";

function Dashboard() {

    return (
        <div>

            <Navbar />

            <div
                style={{
                    display: "flex",
                }}
            >

                <Sidebar />

                <div
                    style={{
                        flex: 1,
                        padding: "30px",
                        background: "#f3f4f6",
                        minHeight: "100vh",
                    }}
                >

                    <h1>Dashboard</h1>

                    <p>

                        Welcome to your AI Learning Assistant.

                    </p>

                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns:
                                "repeat(auto-fit,minmax(220px,1fr))",
                            gap: "20px",
                            marginTop: "30px",
                        }}
                    >

                        <div
                            style={{
                                background: "white",
                                padding: "25px",
                                borderRadius: "10px",
                                boxShadow: "0 2px 8px gray",
                            }}
                        >
                            📁 Upload Files
                        </div>

                        <div
                            style={{
                                background: "white",
                                padding: "25px",
                                borderRadius: "10px",
                                boxShadow: "0 2px 8px gray",
                            }}
                        >
                            💬 AI Chat
                        </div>

                        <div
                            style={{
                                background: "white",
                                padding: "25px",
                                borderRadius: "10px",
                                boxShadow: "0 2px 8px gray",
                            }}
                        >
                            📄 Summary
                        </div>

                        <div
                            style={{
                                background: "white",
                                padding: "25px",
                                borderRadius: "10px",
                                boxShadow: "0 2px 8px gray",
                            }}
                        >
                            ❓ Quiz
                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default Dashboard;