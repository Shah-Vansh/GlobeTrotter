/**
 * components/ThemeToggle.jsx
 * Light/dark switch used in the header. Toggles themeSlice, applies the
 * "dark" class to <html> (see App.jsx effect), and best-effort syncs the
 * preference to the backend for logged-in users.
 */
import { useDispatch, useSelector } from "react-redux";
import { Moon, Sun } from "lucide-react";
import { toggleTheme, syncThemeToServer } from "../store/slices/themeSlice";

export default function ThemeToggle() {
  const dispatch = useDispatch();
  const mode = useSelector((state) => state.theme.mode);
  const user = useSelector((state) => state.auth.user);

  const handleToggle = () => {
    const next = mode === "dark" ? "light" : "dark";
    dispatch(toggleTheme());
    if (user) dispatch(syncThemeToServer(next));
  };

  return (
    <button
      type="button"
      onClick={handleToggle}
      aria-label="Toggle color theme"
      title="Toggle light / dark mode"
      className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
    >
      {mode === "dark" ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}
