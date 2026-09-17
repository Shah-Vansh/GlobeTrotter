/**
 * components/chat/ChatWidget.jsx
 *
 * Full-height right sidebar chat (not a floating popup).
 * Messages + conversation_id persist in localStorage until the user
 * clicks Clear — they are never wiped on navigation/reload alone.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MessageCircle, X, Send, Loader2, Trash2, Bot } from "lucide-react";
import { sendChatMessage } from "../../lib/chatApi";
import MarkdownMessage from "./MarkdownMessage";

const STORAGE_CONV_ID = "gt_chat_conversation_id";
const STORAGE_MESSAGES = "gt_chat_messages";
const STORAGE_OPEN = "gt_chat_open";

const DEFAULT_WELCOME = {
  role: "assistant",
  content:
    "Hi! I'm the **GlobeTrotter** assistant. I can search destinations & activities, and manage your trips using the same APIs as the app. Tell me your name or ask anything about travel planning.",
};

const SUGGESTIONS = [
  "Search destinations related to Goa",
  "Find highly rated activities",
  "List my trips",
  "Help me plan a 5-day beach trip",
];

function loadMessages() {
  try {
    const raw = localStorage.getItem(STORAGE_MESSAGES);
    if (!raw) return [DEFAULT_WELCOME];
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed) && parsed.length > 0) return parsed;
  } catch {
    /* ignore corrupt storage */
  }
  return [DEFAULT_WELCOME];
}

function saveMessages(msgs) {
  try {
    localStorage.setItem(STORAGE_MESSAGES, JSON.stringify(msgs));
  } catch {
    /* quota / private mode */
  }
}

export default function ChatWidget() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(() => localStorage.getItem(STORAGE_OPEN) === "1");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState(loadMessages);
  const [conversationId, setConversationId] = useState(() =>
    localStorage.getItem(STORAGE_CONV_ID)
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Persist open state so sidebar stays open across route changes
  useEffect(() => {
    localStorage.setItem(STORAGE_OPEN, open ? "1" : "0");
    // Notify layout to reserve space for the dock
    window.dispatchEvent(
      new CustomEvent("gt-chat-open-change", { detail: { open } })
    );
  }, [open]);

  // Persist messages whenever they change (never auto-clear)
  useEffect(() => {
    saveMessages(messages);
  }, [messages]);

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      inputRef.current?.focus();
    }
  }, [open, messages, loading]);

  const persistConversationId = useCallback((id) => {
    setConversationId(id);
    if (id) localStorage.setItem(STORAGE_CONV_ID, id);
    else localStorage.removeItem(STORAGE_CONV_ID);
  }, []);

  /** Only path that clears history — trash button */
  const handleClear = () => {
    if (
      !window.confirm(
        "Clear this conversation? The assistant will forget this chat history."
      )
    ) {
      return;
    }
    persistConversationId(null);
    const cleared = [
      {
        role: "assistant",
        content:
          "Conversation cleared. Ask me anything about destinations, activities, or your trips.",
      },
    ];
    setMessages(cleared);
    saveMessages(cleared);
    setError(null);
  };

  const handleSend = async (text) => {
    const content = (text ?? input).trim();
    if (!content || loading) return;

    setInput("");
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content }]);
    setLoading(true);

    try {
      const data = await sendChatMessage(content, conversationId);
      if (data.conversation_id) {
        persistConversationId(data.conversation_id);
      }

      const nav = data.navigation;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply || "(No reply)",
          meta: {
            workflow_steps: data.workflow_steps,
            latency: data.latency_seconds,
            navigation: nav || null,
          },
        },
      ]);

      if (nav?.path && typeof nav.path === "string") {
        setTimeout(() => navigate(nav.path), 400);
      }
    } catch (err) {
      const msg = err.message || "Something went wrong talking to the assistant.";
      setError(msg);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Sorry — ${msg}`,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Toggle when closed — sits on the right edge */}
      {!open && (
        <button
          type="button"
          aria-label="Open chat"
          onClick={() => setOpen(true)}
          className="fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600 text-white shadow-lg hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 dark:focus:ring-offset-slate-900 transition"
        >
          <MessageCircle className="h-6 w-6" />
        </button>
      )}

      {/* Full-height right dock — ~18–22rem (~12–18% on large screens) */}
      <aside
        className={`fixed top-0 right-0 z-40 flex h-screen flex-col border-l border-slate-200 bg-white shadow-xl transition-transform duration-200 dark:border-slate-700 dark:bg-slate-900 ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
        style={{
          width: "min(22rem, 22vw)",
          minWidth: open ? "18rem" : undefined,
        }}
        aria-hidden={!open}
      >
        {/* Header */}
        <div className="flex shrink-0 items-center justify-between gap-2 border-b border-indigo-500/30 bg-indigo-600 px-3 py-3 text-white">
          <div className="flex min-w-0 items-center gap-2">
            <Bot className="h-5 w-5 shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-semibold leading-tight">GlobeTrotter AI</p>
              <p className="truncate text-[11px] text-indigo-100">
                Destinations · Activities · Your trips
              </p>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-1">
            <button
              type="button"
              onClick={handleClear}
              title="Clear conversation"
              className="rounded-lg p-1.5 hover:bg-indigo-500/80 transition"
            >
              <Trash2 className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => setOpen(false)}
              title="Close panel"
              className="rounded-lg p-1.5 hover:bg-indigo-500/80 transition"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 space-y-3 overflow-y-auto px-3 py-3 text-sm">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[95%] rounded-2xl px-3 py-2 ${
                  m.role === "user"
                    ? "rounded-br-md bg-indigo-600 text-white whitespace-pre-wrap"
                    : m.isError
                      ? "rounded-bl-md bg-red-50 text-red-800 dark:bg-red-950/40 dark:text-red-200"
                      : "rounded-bl-md bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-100"
                }`}
              >
                {m.role === "assistant" && !m.isError ? (
                  <MarkdownMessage content={m.content} />
                ) : (
                  m.content
                )}
                {m.meta?.navigation?.path && (
                  <button
                    type="button"
                    onClick={() => navigate(m.meta.navigation.path)}
                    className="mt-2 block w-full rounded-lg bg-indigo-600 px-2 py-1.5 text-center text-[11px] font-medium text-white hover:bg-indigo-500"
                  >
                    {m.meta.navigation.label || "Open page"} →
                  </button>
                )}
                {m.meta?.workflow_steps?.length > 0 && (
                  <p className="mt-1.5 border-t border-black/10 pt-1 text-[10px] opacity-70 dark:border-white/10">
                    {m.meta.workflow_steps.join(" → ")}
                    {m.meta.latency != null && ` · ${m.meta.latency}s`}
                  </p>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 rounded-2xl rounded-bl-md bg-slate-100 px-3 py-2 text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                Thinking…
              </div>
            </div>
          )}

          {messages.length <= 1 && !loading && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => handleSend(s)}
                  className="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-[11px] text-slate-600 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-indigo-500"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="shrink-0 border-t border-slate-200 p-2 dark:border-slate-700">
          {error && (
            <p className="mb-1 px-1 text-[11px] text-red-600 dark:text-red-400">
              {error}
            </p>
          )}
          <div className="flex items-end gap-2">
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Ask about trips, cities, activities…"
              disabled={loading}
              className="max-h-28 min-h-[2.5rem] flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
            <button
              type="button"
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-white transition hover:bg-indigo-500 disabled:opacity-40"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
