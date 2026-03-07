import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import Layout from "./components/layout/Layout";
import LoginPage from "./pages/auth/LoginPage";
import OAuthCallback from "./pages/auth/OAuthCallback";
import DashboardPage from "./pages/dashboard/DashboardPage";
import OverallStatsPage from "./pages/analytics/OverallStatsPage";
import TacticsPage from "./pages/analytics/TacticsPage";
import TimeAnalysisPage from "./pages/analytics/TimeAnalysisPage";
import LoadingSpinner from "./components/common/LoadingSpinner";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return <LoadingSpinner fullScreen />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<OAuthCallback />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="analytics/overview" element={<OverallStatsPage />} />
        <Route path="analytics/tactics" element={<TacticsPage />} />
        <Route path="analytics/time" element={<TimeAnalysisPage />} />
      </Route>
    </Routes>
  );
}
