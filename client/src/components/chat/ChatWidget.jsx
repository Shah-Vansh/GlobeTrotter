/**
 * components/chat/ChatWidget.jsx
 * Floating chat panel for the GlobeTrotter MCP AI assistant.
 * Assistant replies are rendered as Markdown (GFM tables, bold, lists, etc.).
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { MessageCircle, X, Send, Loader2, Trash2, Bot } from "lucide-react";
import { sendChatMessage } from "../../lib/chatApi";
import MarkdownMessage from "./MarkdownMessage";

const STORAGE_KEY = "gt_chat_conversation_id";

const SUGGESTIONS = [
  "Search destinations related to Goa",
  "Find highly rated activities",
  "List my trips",
  "Help me plan a 5-day beach trip",
];

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I'm the **GlobeTrotter** assistant. I can search destinations & activities, and manage your trips using the same APIs as the app. How can I help?",
    },
  ]);
  const [conversationId, setConversationId] = useState(() =>
    localStorage.getItem(STORAGE_KEY)
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      inputRef.current?.focus();
    }
  }, [open, messages, loading]);

  const persistConversationId = useCallback((id) => {
    setConversationId(id);
    if (id) localStorage.setItem(STORAGE_KEY, id);
    else localStorage.removeItem(STORAGE_KEY);
  }, []);

  const handleClear = () => {
    persistConversationId(null);
    setMessages([
      {
        role: "assistant",
        content:
          "Conversation cleared. Ask me anything about destinations, activities, or your trips.",
      },
    ]);
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
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply || "(No reply)",
          meta: {
            workflow_steps: data.workflow_steps,
            latency: data.latency_seconds,
          },
        },
      ]);
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
      <button
        type="button"
        aria-label={open ? "Close chat" : "Open chat"}
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600 text-white shadow-lg hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 dark:focus:ring-offset-slate-900 transition"
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>

      {open && (
        <div
          className="fixed right-5 z-50 flex w-[min(100vw-1.5rem,26rem)] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900"
          style={{ bottom: "5.5rem", maxHeight: "min(75vh, 36rem)" }}
        >
          <div className="flex items-center justify-between gap-2 border-b border-slate-200 bg-indigo-600 px-4 py-3 text-white dark:border-slate-700">
            <div className="flex items-center gap-2 min-w-0">
              <Bot className="h-5 w-5 shrink-0" />
              <div className="min-w-0">
                <p className="text-sm font-semibold leading-tight">GlobeTrotter AI</p>
                <p className="text-[11px] text-indigo-100 truncate">
                  Destinations · Activities · Your trips
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleClear}
              title="Clear conversation"
              className="rounded-lg p-1.5 hover:bg-indigo-500/80 transition"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto px-3 py-3 text-sm">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex ${
                  m.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[92%] rounded-2xl px-3 py-2 ${
                    m.role === "user"
                      ? "bg-indigo-600 text-white rounded-br-md whitespace-pre-wrap"
                      : m.isError
                        ? "bg-red-50 text-red-800 dark:bg-red-950/40 dark:text-red-200 rounded-bl-md"
                        : "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-100 rounded-bl-md"
                  }`}
                >
                  {m.role === "assistant" && !m.isError ? (
                    <MarkdownMessage content={m.content} />
                  ) : (
                    m.content
                  )}
                  {m.meta?.workflow_steps?.length > 0 && (
                    <p className="mt-1.5 text-[10px] opacity-70 border-t border-black/10 dark:border-white/10 pt-1">
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

          <div className="border-t border-slate-200 p-2 dark:border-slate-700">
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
                className="max-h-24 min-h-[2.5rem] flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
              />
              <button
                type="button"
                onClick={() => handleSend()}
                disabled={loading || !input.trim()}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-40 transition"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
