function Navbar() {
    return (
        <div
            style={{
                height: "70px",
                background: "#2563eb",
                color: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "0 25px",
                fontSize: "22px",
                fontWeight: "bold",
            }}
        >
            <div>📚 Multimodel Learning Assistant</div>

            <div>
                Welcome 👋
            </div>
        </div>
    );
}

export default Navbar;