/**
 * layout/MainLayout.jsx
 * Shell wrapping every authenticated page: Header, Sidebar, breadcrumb,
 * page content, and the floating MCP ChatWidget.
 */
import { Outlet } from "react-router-dom";
import Header from "./Header";
import Sidebar from "./Sidebar";
import Breadcrumb from "./Breadcrumb";
import ChatWidget from "../components/chat/ChatWidget";

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
      <ChatWidget />
    </div>
  );
}
