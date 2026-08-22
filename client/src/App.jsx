/**
 * App.jsx
 * Route table for the whole app + two small app-level effects:
 *   1. On mount, try to restore the session (GET /api/auth/me) if a
 *      token is already in localStorage, so a hard refresh doesn't log
 *      the user out.
 *   2. Keep the <html> element's "dark" class in sync with themeSlice so
 *      Tailwind's `dark:` variants apply globally.
 *
 * Layout nesting:
 *   AuthLayout   -> /login, /register            (public, redirects if logged in)
 *   MainLayout   -> ProtectedRoute -> everything else (requires a session)
 *                -> AdminRoute -> /admin           (requires is_admin)
 */
import { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";

import AuthLayout from "./layout/AuthLayout";
import MainLayout from "./layout/MainLayout";
import ProtectedRoute from "./layout/ProtectedRoute";
import AdminRoute from "./layout/AdminRoute";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import Dashboard from "./pages/Dashboard";
import TripsList from "./pages/trips/TripsList";
import CreateTrip from "./pages/trips/CreateTrip";
import TripDetail from "./pages/trips/TripDetail";
import CitySearch from "./pages/search/CitySearch";
import ActivitySearch from "./pages/search/ActivitySearch";
import Community from "./pages/community/Community";
import CalendarView from "./pages/calendar/CalendarView";
import Profile from "./pages/profile/Profile";
import AdminPanel from "./pages/admin/AdminPanel";
import PublicTripView from "./pages/public/PublicTripView";
import NotFound from "./pages/NotFound";

import { fetchCurrentUser, bootstrapDone } from "./store/slices/authSlice";
import { tokenStorage } from "./configs/api";

function App() {
  const dispatch = useDispatch();
  const themeMode = useSelector((state) => state.theme.mode);

  // Restore session on first load if we already have a token; otherwise
  // immediately mark the bootstrap check as done so ProtectedRoute can
  // redirect to /login instead of showing a loader forever.
  useEffect(() => {
    if (tokenStorage.getAccessToken()) {
      dispatch(fetchCurrentUser());
    } else {
      dispatch(bootstrapDone());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync the "dark" class on <html> with the theme slice.
  useEffect(() => {
    document.documentElement.classList.toggle("dark", themeMode === "dark");
  }, [themeMode]);

  return (
    <Routes>
      {/* --- Public / auth routes --- */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      {/* --- Public, unauthenticated Shared Itinerary View (screen 11) --- */}
      <Route path="/public/trips/:slug" element={<PublicTripView />} />

      {/* --- Authenticated app shell --- */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trips" element={<TripsList />} />
          <Route path="/trips/new" element={<CreateTrip />} />
          <Route path="/trips/:tripId" element={<TripDetail />} />
          <Route path="/search/cities" element={<CitySearch />} />
          <Route path="/search/activities" element={<ActivitySearch />} />
          <Route path="/community" element={<Community />} />
          <Route path="/calendar" element={<CalendarView />} />
          <Route path="/profile" element={<Profile />} />

          <Route element={<AdminRoute />}>
            <Route path="/admin" element={<AdminPanel />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
