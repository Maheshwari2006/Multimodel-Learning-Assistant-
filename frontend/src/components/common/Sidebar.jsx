import { Link } from "react-router-dom";

function Sidebar() {

    const menu = [
        { name: "Dashboard", path: "/dashboard" },
        { name: "Upload", path: "/upload" },
        { name: "Chat", path: "/chat" },
        { name: "Summary", path: "/summary" },
        { name: "Quiz", path: "/quiz" },
        { name: "Flashcards", path: "/flashcards" },
        { name: "Study Plan", path: "/study-plan" },
        { name: "Recommendations", path: "/recommendations" },
    ];

    return (
        <div
            style={{
                width: "240px",
                background: "#1e293b",
                color: "white",
                minHeight: "100vh",
                padding: "20px",
            }}
        >
            <h2 style={{ marginBottom: "30px" }}>
                Navigation
            </h2>

            {menu.map((item) => (
                <div
                    key={item.path}
                    style={{ marginBottom: "20px" }}
                >
                    <Link
                        to={item.path}
                        style={{
                            color: "white",
                            textDecoration: "none",
                        }}
                    >
                        {item.name}
                    </Link>
                </div>
            ))}
        </div>
    );
}

export default Sidebar;