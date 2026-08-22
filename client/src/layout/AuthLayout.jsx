/**
 * layout/AuthLayout.jsx
 * Shared shell for the Login / Registration screens: centers a card on a
 * gradient backdrop and redirects away if the user is already logged in.
 */
import { useSelector } from "react-redux";
import { Navigate, Outlet } from "react-router-dom";
import { Compass } from "lucide-react";

export default function AuthLayout() {
  const { user } = useSelector((state) => state.auth);
  if (user) return <Navigate to="/" replace />;

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-sky-50 via-white to-emerald-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 px-4 py-10">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-2 mb-6">
          <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-sky-600 text-white">
            <Compass size={22} />
          </span>
          <span className="text-xl font-bold tracking-tight text-slate-800 dark:text-slate-100">
            GlobeTrotter
          </span>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
