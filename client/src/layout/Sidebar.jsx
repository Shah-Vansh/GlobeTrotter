/**
 * layout/Sidebar.jsx
 * Left navigation rail. Collapsible (state persisted via uiSlice /
 * localStorage - "saved preferences"). Shows the Admin Panel link only to
 * admin users (User.is_admin, enforced again server-side + AdminRoute).
 */
import { NavLink } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import * as Icons from "lucide-react";
import { ChevronsLeft, ChevronsRight } from "lucide-react";
import { NAV_LINKS, ADMIN_NAV_LINK } from "../lib/constants";
import { toggleSidebar } from "../store/slices/uiSlice";

export default function Sidebar() {
  const dispatch = useDispatch();
  const collapsed = useSelector((state) => state.ui.sidebarCollapsed);
  const isAdmin = useSelector((state) => state.auth.user?.is_admin);

  const links = isAdmin ? [...NAV_LINKS, ADMIN_NAV_LINK] : NAV_LINKS;

  return (
    <aside
      className={`hidden md:flex flex-col shrink-0 h-full overflow-y-auto border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 transition-all duration-200 ${
        collapsed ? "w-16" : "w-60"
      }`}
    >
      <nav className="flex-1 py-4 space-y-1 px-2">
        {links.map((link) => {
          const Icon = Icons[link.icon] || Icons.Circle;
          return (
            <NavLink
              key={link.path}
              to={link.path}
              end={link.path === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-sky-50 text-sky-700 dark:bg-sky-900/30 dark:text-sky-300"
                    : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                }`
              }
              title={collapsed ? link.label : undefined}
            >
              <Icon size={18} className="shrink-0" />
              {!collapsed && <span className="truncate">{link.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      <button
        type="button"
        onClick={() => dispatch(toggleSidebar())}
        className="m-2 flex items-center justify-center gap-2 rounded-lg py-2 text-xs text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
      >
        {collapsed ? <ChevronsRight size={16} /> : (<><ChevronsLeft size={16} /> Collapse</>)}
      </button>
    </aside>
  );
}
