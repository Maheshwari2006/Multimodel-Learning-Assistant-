
import { Routes, Route } from "react-router-dom";

import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";
import Dashboard from "../pages/Dashboard";
import Flashcards from "../pages/flashcards";
import FeaturePage from "../pages/FeaturePages";
import ProtectedRoute from "../components/common/ProtectedRoute";

function AppRoutes() {
    return (
        <Routes>
            {/* Public pages */}
            <Route path="/" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected dashboard */}
            <Route
                path="/dashboard"
                element={
                    <ProtectedRoute>
                        <Dashboard />
                    </ProtectedRoute>
                }
            />

            {/* Existing flashcards page */}
            <Route
                path="/flashcards"
                element={
                    <ProtectedRoute>
                        <Flashcards />
                    </ProtectedRoute>
                }
            />

            {/* Upload */}
            <Route
                path="/upload"
                element={
                    <ProtectedRoute>
                        <FeaturePage type="upload" />
                    </ProtectedRoute>
                }
            />

            {/* AI Chat */}
            <Route
                path="/chat"
                element={
                    <ProtectedRoute>
                        <FeaturePage type="chat" />
                    </ProtectedRoute>
                }
            />

            {/* Summary */}
            <Route
                path="/summary"
                element={
                    <ProtectedRoute>
                        <FeaturePage type="summary" />
                    </ProtectedRoute>
                }
            />

            {/* Quiz */}
            <Route
                path="/quiz"
                element={
                    <ProtectedRoute>
                        <FeaturePage type="quiz" />
                    </ProtectedRoute>
                }
            />

            {/* Study Plan */}
            <Route
                path="/study-plan"
                element={
                    <ProtectedRoute>
                        <FeaturePage type="studyPlan" />
                    </ProtectedRoute>
                }
            />

            {/* Recommendations */}
            <Route
                path="/recommendations"
                element={
                    <ProtectedRoute>
                        <FeaturePage type="recommendations" />
                    </ProtectedRoute>
                }
            />
        </Routes>
    );
}

export default AppRoutes;
