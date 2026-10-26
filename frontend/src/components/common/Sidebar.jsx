import { NavLink } from "react-router-dom";
import {
    FiHome, FiUploadCloud, FiMessageSquare, FiFileText, FiHelpCircle, FiLayers, FiCalendar, FiStar,
    FiChevronsLeft, FiChevronsRight, FiLogOut,
} from "react-icons/fi";

export const MENU = [
    { name: "Dashboard", path: "/dashboard", icon: FiHome },
    { name: "Upload", path: "/upload", icon: FiUploadCloud },
    { name: "AI Chat", path: "/chat", icon: FiMessageSquare },
    { name: "Summary", path: "/summary", icon: FiFileText },
    { name: "Quiz", path: "/quiz", icon: FiHelpCircle },
    { name: "Flashcards", path: "/flashcards", icon: FiLayers },
    { name: "Study Plan", path: "/study-plan", icon: FiCalendar },
    { name: "Recommendations", path: "/recommendations", icon: FiStar },
];

function Sidebar({ collapsed, open, onToggle, onNavigate, onLogout }) {
    return (
        <aside className={`sidebar ${open ? "open" : ""}`} aria-label="Main navigation">
            <div className="brand">
                <span className="brand-mark" aria-hidden="true">✦</span>
                <span className="brand-text">Learning<br />Assistant</span>
            </div>

            <nav className="stack" style={{ gap: 4 }}>
                {MENU.map(({ name, path, icon: Icon }) => (
                    <NavLink
                        key={path}
                        to={path}
                        className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                        onClick={onNavigate}
                        title={collapsed ? name : undefined}
                    >
                        <Icon aria-hidden="true" />
                        <span className="label-text">{name}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="sidebar-foot">
                <button className="nav-link ghost-btn" onClick={onToggle} style={{ background: "none", cursor: "pointer", font: "inherit" }}
                        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}>
                    {collapsed ? <FiChevronsRight aria-hidden="true" /> : <FiChevronsLeft aria-hidden="true" />}
                    <span className="label-text">Collapse</span>
                </button>
                <button className="nav-link" onClick={onLogout} style={{ background: "none", cursor: "pointer", font: "inherit" }}>
                    <FiLogOut aria-hidden="true" />
                    <span className="label-text">Log out</span>
                </button>
            </div>
        </aside>
    );
}

export default Sidebar;
