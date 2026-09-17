/**
 * layout/MainLayout.jsx
 * Shell wrapping every authenticated page: Header, Sidebar, breadcrumb,
 * page content, and the docked MCP ChatWidget (right panel).
 */
import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import Header from "./Header";
import Sidebar from "./Sidebar";
import Breadcrumb from "./Breadcrumb";
import ChatWidget from "../components/chat/ChatWidget";

export default function MainLayout() {
  const [chatOpen, setChatOpen] = useState(
    () => localStorage.getItem("gt_chat_open") === "1"
  );

  useEffect(() => {
    const onChange = (e) => setChatOpen(Boolean(e.detail?.open));
    window.addEventListener("gt-chat-open-change", onChange);
    return () => window.removeEventListener("gt-chat-open-change", onChange);
  }, []);

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <Header />
      <div className="flex min-h-0 flex-1">
        <Sidebar />
        <main
          className="min-w-0 flex-1 overflow-y-auto transition-[margin] duration-200"
          style={{
            // Match ChatWidget dock width so content is not hidden under it
            marginRight: chatOpen ? "min(22rem, 22vw)" : 0,
          }}
        >
          <div className="border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900 md:px-6">
            <Breadcrumb />
          </div>
          <div className="px-4 py-6 md:px-6">
            <Outlet />
          </div>
        </main>
      </div>
      <ChatWidget />
    </div>
  );
}
