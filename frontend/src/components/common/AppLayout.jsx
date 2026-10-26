import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import Sidebar, { MENU } from "./Sidebar";
import Navbar from "./Navbar";
import { useAuth } from "../../context/AuthContext";

function AppLayout() {
    const { user, logout, refreshUser } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [collapsed, setCollapsed] = useState(() => localStorage.getItem("sidebar_collapsed") === "1");
    const [open, setOpen] = useState(false);

    useEffect(() => setOpen(false), [location.pathname]);

    // The login page only stores the token, so load the user once the layout mounts.
    useEffect(() => {
        if (!user) refreshUser();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const toggle = () =>
        setCollapsed((c) => {
            localStorage.setItem("sidebar_collapsed", c ? "0" : "1");
            return !c;
        });

    const title = MENU.find((m) => location.pathname.startsWith(m.path))?.name || "";

    return (
        <div className={`app-shell ${collapsed ? "collapsed" : ""}`}>
            <Sidebar
                collapsed={collapsed}
                open={open}
                onToggle={toggle}
                onNavigate={() => setOpen(false)}
                onLogout={() => {
                    logout();
                    navigate("/");
                }}
            />
            <div className={`scrim ${open ? "open" : ""}`} onClick={() => setOpen(false)} aria-hidden="true" />
            <div className="main">
                <Navbar title={title} user={user} onMenu={() => setOpen(true)} />
                <main className="page rise" key={location.pathname}>
                    <Outlet />
                </main>
            </div>
        </div>
    );
}

export default AppLayout;
