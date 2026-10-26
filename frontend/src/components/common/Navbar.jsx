import { FiMenu } from "react-icons/fi";

function Navbar({ title, user, onMenu }) {
    const name = user?.username || "";
    return (
        <header className="navbar">
            <button className="btn icon menu-btn" onClick={onMenu} aria-label="Open navigation menu">
                <FiMenu />
            </button>
            <div className="grow"><h2>{title}</h2></div>
            {user && (
                <div className="user-chip" title={user.email}>
                    <span className="av" aria-hidden="true">{name.charAt(0).toUpperCase() || "?"}</span>
                    <span className="who">{name}</span>
                </div>
            )}
        </header>
    );
}

export default Navbar;
