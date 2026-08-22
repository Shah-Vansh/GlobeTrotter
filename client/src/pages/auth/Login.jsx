/**
 * pages/auth/Login.jsx
 * Screen 1 - Login Page.
 * Centered card: profile/app photo, username + password fields, Login
 * button. Validates empty fields client-side and surfaces the backend's
 * "Invalid username or password" message on bad credentials. On success,
 * redirects to the Main Landing Page (or wherever the user was headed).
 */
import { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { gsap } from "gsap";
import { Eye, EyeOff, LogIn, UserRound } from "lucide-react";
import toast from "react-hot-toast";
import { loginUser } from "../../store/slices/authSlice";

export default function Login() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { status, error } = useSelector((state) => state.auth);

  const [form, setForm] = useState({ username: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const cardRef = useRef(null);

  // Gentle entrance animation for the login card (GSAP).
  useEffect(() => {
    gsap.fromTo(
      cardRef.current,
      { opacity: 0, y: 24 },
      { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }
    );
  }, []);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setFieldErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = () => {
    const errs = {};
    if (!form.username.trim()) errs.username = "Username is required.";
    if (!form.password) errs.password = "Password is required.";
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    const result = await dispatch(loginUser(form));
    if (loginUser.fulfilled.match(result)) {
      toast.success(`Welcome back, ${result.payload.first_name}!`);
      navigate(location.state?.from?.pathname || "/", { replace: true });
    } else {
      toast.error(result.payload || "Invalid username or password.");
    }
  };

  return (
    <div
      ref={cardRef}
      className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl p-8"
    >
      {/* Profile photo / app branding section */}
      <div className="flex flex-col items-center mb-6">
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-sky-50 dark:bg-sky-900/40 text-sky-600 dark:text-sky-400">
          <UserRound size={30} />
        </span>
        <h1 className="mt-3 text-lg font-bold text-slate-800 dark:text-slate-100">Welcome back</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Log in to plan your next trip</p>
      </div>

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Username
          </label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={form.username}
            onChange={handleChange("username")}
            className={`w-full rounded-lg border bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500 ${
              fieldErrors.username ? "border-rose-400" : "border-slate-200 dark:border-slate-700"
            }`}
            placeholder="Enter your username"
          />
          {fieldErrors.username && <p className="mt-1 text-xs text-rose-500">{fieldErrors.username}</p>}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              value={form.password}
              onChange={handleChange("password")}
              className={`w-full rounded-lg border bg-white dark:bg-slate-800 px-3 py-2 pr-10 text-sm outline-none focus:ring-2 focus:ring-sky-500 ${
                fieldErrors.password ? "border-rose-400" : "border-slate-200 dark:border-slate-700"
              }`}
              placeholder="Enter your password"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              tabIndex={-1}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {fieldErrors.password && <p className="mt-1 text-xs text-rose-500">{fieldErrors.password}</p>}
        </div>

        <button
          type="submit"
          disabled={status === "loading"}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-medium py-2.5 transition-colors disabled:opacity-60"
        >
          <LogIn size={16} />
          {status === "loading" ? "Logging in..." : "Login"}
        </button>
      </form>

      <p className="mt-5 text-center text-sm text-slate-500 dark:text-slate-400">
        New to GlobeTrotter?{" "}
        <Link to="/register" className="font-medium text-sky-600 dark:text-sky-400 hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}
