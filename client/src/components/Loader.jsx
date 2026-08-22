/**
 * components/Loader.jsx
 * Small reusable spinner. Pass fullScreen for page-level loading states
 * (e.g. session restore, initial data fetch) or use inline for buttons.
 */
import { Loader2 } from "lucide-react";

export default function Loader({ label = "Loading...", fullScreen = false, size = 22 }) {
  const spinner = (
    <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
      <Loader2 size={size} className="animate-spin text-sky-600 dark:text-sky-400" />
      {label && <span className="text-sm">{label}</span>}
    </div>
  );

  if (!fullScreen) return spinner;

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-white dark:bg-slate-950">
      {spinner}
    </div>
  );
}
