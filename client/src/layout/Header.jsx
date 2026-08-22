/**
 * layout/Header.jsx
 * App-wide top bar: GlobeTrotter brand on the left, ThemeToggle + profile
 * menu on the right (per the "header with app name left / profile icon
 * right" spec repeated on nearly every screen).
 */
import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { Compass, LogOut, UserCircle, Settings } from "lucide-react";
import toast from "react-hot-toast";
import ThemeToggle from "../components/ThemeToggle";
import { logout } from "../store/slices/authSlice";

export default function Header() {
  const user = useSelector((state) => state.auth.user);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    function onClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const handleLogout = () => {
    dispatch(logout());
    toast.success("Logged out successfully.");
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 backdrop-blur px-4 md:px-6 py-3">
      <Link to="/" className="flex items-center gap-2">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-sky-600 text-white">
          <Compass size={18} />
        </span>
        <span className="text-lg font-bold tracking-tight text-slate-800 dark:text-slate-100">
          GlobeTrotter
        </span>
      </Link>

      <div className="flex items-center gap-3">
        <ThemeToggle />

        <div className="relative" ref={menuRef}>
          <button
            type="button"
            onClick={() => setMenuOpen((v) => !v)}
            className="flex items-center gap-2 rounded-full border border-slate-200 dark:border-slate-700 pl-1 pr-2 py-1 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            {user?.profile_photo_url ? (
              <img
                src={user.profile_photo_url}
                alt={user.full_name}
                className="h-7 w-7 rounded-full object-cover"
              />
            ) : (
              <UserCircle size={26} className="text-slate-400" />
            )}
            <span className="hidden sm:inline text-sm font-medium text-slate-700 dark:text-slate-200 max-w-[120px] truncate">
              {user?.first_name || "Profile"}
            </span>
          </button>

          {menuOpen && (
            <div className="absolute right-0 mt-2 w-48 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg py-1 animate-in fade-in">
              <Link
                to="/profile"
                onClick={() => setMenuOpen(false)}
                className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700"
              >
                <Settings size={16} /> Profile & Settings
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                className="flex w-full items-center gap-2 px-3 py-2 text-sm text-rose-600 dark:text-rose-400 hover:bg-slate-100 dark:hover:bg-slate-700"
              >
                <LogOut size={16} /> Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
