/**
 * layout/ProtectedRoute.jsx
 * Route guard: redirects to /login if there's no authenticated user once
 * the initial session-restore check (fetchCurrentUser) has finished.
 * While that check is in flight, show a loader instead of bouncing the
 * user to /login on every hard refresh.
 */
import { useSelector } from "react-redux";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import Loader from "../components/Loader";

export default function ProtectedRoute() {
  const { user, bootstrapped } = useSelector((state) => state.auth);
  const location = useLocation();

  if (!bootstrapped) {
    return <Loader fullScreen label="Restoring your session..." />;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
