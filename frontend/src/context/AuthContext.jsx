import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { getCurrentUser } from "../api/authApi";

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);

    const login = useCallback((token) => {
        localStorage.setItem("token", token);
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem("token");
        setUser(null);
    }, []);

    // The Login page only stores the token, so the layout loads the profile afterwards.
    const refreshUser = useCallback(async () => {
        try {
            const me = await getCurrentUser();
            setUser(me);
            return me;
        } catch {
            return null;
        }
    }, []);

    const value = useMemo(() => ({ user, setUser, login, logout, refreshUser }), [user, login, logout, refreshUser]);
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
    return ctx;
};
