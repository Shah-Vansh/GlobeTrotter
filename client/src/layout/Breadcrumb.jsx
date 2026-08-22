/**
 * layout/Breadcrumb.jsx
 * Renders the current navigation trail (state.ui.breadcrumbs). Pages set
 * their own trail via the useBreadcrumb hook (see lib/useBreadcrumb.js)
 * so the header stays a "dumb" renderer.
 */
import { Link } from "react-router-dom";
import { ChevronRight, Home } from "lucide-react";
import { useSelector } from "react-redux";

export default function Breadcrumb() {
  const crumbs = useSelector((state) => state.ui.breadcrumbs);

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm text-slate-500 dark:text-slate-400 overflow-x-auto">
      <Link to="/" className="flex items-center gap-1 hover:text-sky-600 dark:hover:text-sky-400 shrink-0">
        <Home size={14} />
      </Link>
      {crumbs.map((crumb, idx) => {
        const isLast = idx === crumbs.length - 1;
        return (
          <span key={crumb.path || crumb.label} className="flex items-center gap-1 shrink-0">
            <ChevronRight size={14} className="opacity-50" />
            {isLast || !crumb.path ? (
              <span className="font-medium text-slate-700 dark:text-slate-200">{crumb.label}</span>
            ) : (
              <Link to={crumb.path} className="hover:text-sky-600 dark:hover:text-sky-400">
                {crumb.label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
