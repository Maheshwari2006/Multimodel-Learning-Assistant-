import { Navigate, Route, Routes } from "react-router-dom";

import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";
import Dashboard from "../pages/Dashboard";
import Upload from "../pages/Upload";
import Chat from "../pages/Chat";
import Summary from "../pages/Summary";
import Quiz from "../pages/Quiz";
import Flashcards from "../pages/flashcards";
import StudyPlan from "../pages/StudyPlan";
import Recommendations from "../pages/Recommendations";
import AppLayout from "../components/common/AppLayout";
import ProtectedRoute from "../components/common/ProtectedRoute";

function AppRoutes() {
    return (
        <Routes>
            {/* Public pages */}
            <Route path="/" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Everything else shares one layout: sidebar + top bar */}
            <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/upload" element={<Upload />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/summary" element={<Summary />} />
                <Route path="/quiz" element={<Quiz />} />
                <Route path="/flashcards" element={<Flashcards />} />
                <Route path="/study-plan" element={<StudyPlan />} />
                <Route path="/recommendations" element={<Recommendations />} />
            </Route>

            <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
    );
}

export default AppRoutes;
