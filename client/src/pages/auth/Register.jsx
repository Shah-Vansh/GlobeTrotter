/**
 * pages/auth/Register.jsx
 * Screen 2 - Registration Page.
 * Profile photo picker + First/Last Name, Email, Phone, City, Country,
 * Additional Information. Submits multipart/form-data so the optional
 * photo reaches Cloudinary via the backend. On success the user is
 * auto-authenticated (backend returns tokens) and redirected in.
 */
import { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link, useNavigate } from "react-router-dom";
import { gsap } from "gsap";
import { Camera, UserPlus } from "lucide-react";
import toast from "react-hot-toast";
import { registerUser } from "../../store/slices/authSlice";
import { getErrorMessage } from "../../lib/formatters";

const EMPTY_FORM = {
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  phone_number: "",
  city: "",
  country: "",
  additional_info: "",
};

export default function Register() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { status } = useSelector((state) => state.auth);

  const [form, setForm] = useState(EMPTY_FORM);
  const [photoFile, setPhotoFile] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const cardRef = useRef(null);

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

  const handlePhotoChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPhotoFile(file);
    setPhotoPreview(URL.createObjectURL(file));
  };

  const validate = () => {
    const errs = {};
    if (!form.username.trim()) errs.username = "Username is required.";
    if (!form.first_name.trim()) errs.first_name = "First name is required.";
    if (!form.last_name.trim()) errs.last_name = "Last name is required.";
    if (!form.email.trim()) errs.email = "Email is required.";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = "Enter a valid email address.";
    if (!form.password || form.password.length < 6) errs.password = "Password must be at least 6 characters.";
    if (form.phone_number && !/^[0-9+\-\s()]{7,20}$/.test(form.phone_number)) {
      errs.phone_number = "Enter a valid phone number.";
    }
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    const payload = new FormData();
    Object.entries(form).forEach(([key, value]) => payload.append(key, value));
    if (photoFile) payload.append("profile_photo", photoFile);

    const result = await dispatch(registerUser(payload));
    if (registerUser.fulfilled.match(result)) {
      toast.success("Account created! Welcome to GlobeTrotter.");
      navigate("/", { replace: true });
    } else {
      toast.error(result.payload || getErrorMessage(result.error, "Registration failed."));
    }
  };

  const inputClass = (field) =>
    `w-full rounded-lg border bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500 ${
      fieldErrors[field] ? "border-rose-400" : "border-slate-200 dark:border-slate-700"
    }`;

  return (
    <div
      ref={cardRef}
      className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl p-8"
    >
      <div className="flex flex-col items-center mb-6">
        <label className="relative cursor-pointer group">
          <span className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full bg-sky-50 dark:bg-sky-900/40 text-sky-600 dark:text-sky-400 border-2 border-dashed border-sky-300 dark:border-sky-700">
            {photoPreview ? (
              <img src={photoPreview} alt="Profile preview" className="h-full w-full object-cover" />
            ) : (
              <Camera size={26} />
            )}
          </span>
          <input type="file" accept="image/*" onChange={handlePhotoChange} className="hidden" />
          <span className="absolute -bottom-1 -right-1 rounded-full bg-sky-600 text-white text-[10px] px-1.5 py-0.5 group-hover:bg-sky-700">
            Edit
          </span>
        </label>
        <h1 className="mt-3 text-lg font-bold text-slate-800 dark:text-slate-100">Create your account</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Start planning your next adventure</p>
      </div>

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">First Name</label>
            <input value={form.first_name} onChange={handleChange("first_name")} className={inputClass("first_name")} />
            {fieldErrors.first_name && <p className="mt-1 text-xs text-rose-500">{fieldErrors.first_name}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Last Name</label>
            <input value={form.last_name} onChange={handleChange("last_name")} className={inputClass("last_name")} />
            {fieldErrors.last_name && <p className="mt-1 text-xs text-rose-500">{fieldErrors.last_name}</p>}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Username</label>
          <input value={form.username} onChange={handleChange("username")} className={inputClass("username")} />
          {fieldErrors.username && <p className="mt-1 text-xs text-rose-500">{fieldErrors.username}</p>}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Email Address</label>
            <input type="email" value={form.email} onChange={handleChange("email")} className={inputClass("email")} />
            {fieldErrors.email && <p className="mt-1 text-xs text-rose-500">{fieldErrors.email}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Phone Number</label>
            <input value={form.phone_number} onChange={handleChange("phone_number")} className={inputClass("phone_number")} />
            {fieldErrors.phone_number && <p className="mt-1 text-xs text-rose-500">{fieldErrors.phone_number}</p>}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Password</label>
          <input type="password" value={form.password} onChange={handleChange("password")} className={inputClass("password")} />
          {fieldErrors.password && <p className="mt-1 text-xs text-rose-500">{fieldErrors.password}</p>}
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">City</label>
            <input value={form.city} onChange={handleChange("city")} className={inputClass("city")} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Country</label>
            <input value={form.country} onChange={handleChange("country")} className={inputClass("country")} />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Additional Information</label>
          <textarea
            rows={3}
            value={form.additional_info}
            onChange={handleChange("additional_info")}
            className={inputClass("additional_info")}
            placeholder="Travel preferences, interests, anything you'd like us to know..."
          />
        </div>

        <button
          type="submit"
          disabled={status === "loading"}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-medium py-2.5 transition-colors disabled:opacity-60"
        >
          <UserPlus size={16} />
          {status === "loading" ? "Creating account..." : "Register User"}
        </button>
      </form>

      <p className="mt-5 text-center text-sm text-slate-500 dark:text-slate-400">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-sky-600 dark:text-sky-400 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
