/**
 * layout/MainLayout.jsx
 * Shell wrapping every authenticated page: Header on top, collapsible
 * Sidebar on the left, breadcrumb strip + routed page content on the
 * right. All of screens 3/6/8/9/10/11/12 share this shell.
 *
 * Layout is pinned to the viewport height (`h-screen overflow-hidden`)
 * with only `<main>` scrolling internally. This keeps the Header and
 * Sidebar fixed in place as the page content scrolls - without a fixed
 * viewport height here, the whole document would scroll instead and
 * drag the sidebar along with it.
 */
import { Outlet } from "react-router-dom";
import Header from "./Header";
import Sidebar from "./Sidebar";
import Breadcrumb from "./Breadcrumb";

export default function MainLayout() {
  return (
    <div className="h-screen flex flex-col overflow-hidden bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <Header />
      <div className="flex flex-1 min-h-0">
        <Sidebar />
        <main className="flex-1 min-w-0 overflow-y-auto">
          <div className="px-4 md:px-6 py-3 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
            <Breadcrumb />
          </div>
          <div className="px-4 md:px-6 py-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
