/**
 * layout/AdminRoute.jsx
 * Extra guard layered on top of ProtectedRoute for /admin/* - only users
 * with is_admin=true (see User model) may pass; everyone else is bounced
 * back to the dashboard.
 */
import { useSelector } from "react-redux";
import { Navigate, Outlet } from "react-router-dom";

export default function AdminRoute() {
  const { user } = useSelector((state) => state.auth);
  if (!user?.is_admin) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}
