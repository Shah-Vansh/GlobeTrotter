/**
 * components/EmptyState.jsx
 * Consistent "nothing here yet" placeholder for empty lists (no trips,
 * no search results, no community posts, etc).
 */
export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-4 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800">
      {Icon && (
        <span className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-full bg-sky-50 dark:bg-sky-900/30 text-sky-600 dark:text-sky-400">
          <Icon size={22} />
        </span>
      )}
      <h3 className="text-base font-semibold text-slate-700 dark:text-slate-200">{title}</h3>
      {description && (
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400 max-w-sm">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
