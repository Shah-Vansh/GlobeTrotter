/**
 * pages/NotFound.jsx
 * Catch-all 404 route.
 */
import { Link } from "react-router-dom";
import { Compass } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-3 text-center px-4 bg-slate-50 dark:bg-slate-950">
      <Compass size={40} className="text-sky-500" />
      <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Lost your way?</h1>
      <p className="text-sm text-slate-500 dark:text-slate-400">We couldn't find the page you're looking for.</p>
      <Link to="/" className="mt-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-4 py-2">
        Back to Dashboard
      </Link>
    </div>
  );
}
