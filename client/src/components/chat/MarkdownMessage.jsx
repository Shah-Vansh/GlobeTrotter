/**
 * Renders assistant replies as Markdown (GFM): tables, bold, lists, code, links.
 */
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const components = {
  p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  ul: ({ children }) => (
    <ul className="mb-2 list-disc space-y-1 pl-4 last:mb-0">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-2 list-decimal space-y-1 pl-4 last:mb-0">{children}</ol>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  h1: ({ children }) => (
    <h1 className="mb-2 text-base font-bold leading-tight">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="mb-2 text-sm font-bold leading-tight">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="mb-1.5 text-sm font-semibold leading-tight">{children}</h3>
  ),
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="underline underline-offset-2 text-indigo-700 dark:text-indigo-300 hover:opacity-80"
    >
      {children}
    </a>
  ),
  code: ({ inline, className, children, ...props }) => {
    if (inline) {
      return (
        <code
          className="rounded bg-black/10 px-1 py-0.5 font-mono text-[11px] dark:bg-white/10"
          {...props}
        >
          {children}
        </code>
      );
    }
    return (
      <code
        className={`block overflow-x-auto rounded-lg bg-slate-900 p-2 font-mono text-[11px] text-slate-100 dark:bg-black/40 ${className || ""}`}
        {...props}
      >
        {children}
      </code>
    );
  },
  pre: ({ children }) => (
    <pre className="mb-2 overflow-x-auto rounded-lg last:mb-0">{children}</pre>
  ),
  blockquote: ({ children }) => (
    <blockquote className="mb-2 border-l-2 border-indigo-400 pl-2 italic opacity-90 last:mb-0">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="my-2 border-slate-300 dark:border-slate-600" />,
  table: ({ children }) => (
    <div className="mb-2 max-w-full overflow-x-auto last:mb-0">
      <table className="w-full border-collapse text-left text-[11px]">{children}</table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-slate-200/80 dark:bg-slate-700/80">{children}</thead>
  ),
  tbody: ({ children }) => <tbody>{children}</tbody>,
  tr: ({ children }) => (
    <tr className="border-b border-slate-200 dark:border-slate-600">{children}</tr>
  ),
  th: ({ children }) => (
    <th className="whitespace-nowrap px-2 py-1.5 font-semibold">{children}</th>
  ),
  td: ({ children }) => (
    <td className="whitespace-nowrap px-2 py-1.5 align-top">{children}</td>
  ),
};

export default function MarkdownMessage({ content }) {
  if (!content) return null;

  return (
    <div className="chat-md break-words text-sm">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
