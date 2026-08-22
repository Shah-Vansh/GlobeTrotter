/**
 * pages/trips/CreateTrip.jsx
 * "+ Plan a Trip" destination. Minimal Create Trip form (name, dates,
 * description, optional cover photo) posting to POST /api/trips. Full
 * itinerary building (adding stops/activities day-by-day) lands on the
 * Trip Detail page next - this screen only creates the trip shell.
 */
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { gsap } from "gsap";
import { Camera, PlaneTakeoff, ArrowRight, CalendarDays } from "lucide-react";
import toast from "react-hot-toast";
import api from "../../configs/api";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage } from "../../lib/formatters";

export default function CreateTrip() {
  useBreadcrumb([{ label: "My Trips", path: "/trips" }, { label: "Plan a Trip" }]);
  const navigate = useNavigate();
  const cardRef = useRef(null);

  const [form, setForm] = useState({ name: "", start_date: "", end_date: "", description: "" });
  const [coverFile, setCoverFile] = useState(null);
  const [coverPreview, setCoverPreview] = useState(null);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    gsap.fromTo(
      cardRef.current,
      { opacity: 0, y: 20, scale: 0.98 },
      { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "power3.out" }
    );
  }, []);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleCoverChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setCoverFile(file);
    setCoverPreview(URL.createObjectURL(file));
  };

  const validate = () => {
    const errs = {};
    if (!form.name.trim()) errs.name = "Trip name is required.";
    if (!form.start_date) errs.start_date = "Start date is required.";
    if (!form.end_date) errs.end_date = "End date is required.";
    if (form.start_date && form.end_date && form.end_date < form.start_date) {
      errs.end_date = "End date cannot be before the start date.";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) {
      gsap.to(cardRef.current, {
        x: -10,
        duration: 0.1,
        repeat: 3,
        yoyo: true,
        ease: "power2.out",
        clearProps: "x",
      });
      return;
    }

    setSubmitting(true);
    try {
      const payload = new FormData();
      Object.entries(form).forEach(([key, value]) => payload.append(key, value));
      if (coverFile) payload.append("cover_photo", coverFile);

      const { data } = await api.post("/api/trips", payload);
      toast.success("Trip created! Now build out your itinerary.");
      navigate(`/trips/${data.data.id}`);
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not create trip."));
    } finally {
      setSubmitting(false);
    }
  };

  const inputClass = (field) =>
    `w-full rounded-xl border bg-white dark:bg-slate-800/50 px-3.5 py-2.5 text-sm outline-none transition-all duration-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:ring-2 focus:ring-sky-500/30 focus:border-sky-500 focus:shadow-[0_0_0_4px_rgba(14,165,233,0.1)] hover:border-slate-300 dark:hover:border-slate-600 ${
      errors[field]
        ? "border-rose-400 dark:border-rose-500 bg-rose-50/50 dark:bg-rose-900/20"
        : "border-slate-200 dark:border-slate-700"
    }`;

  return (
    <div className="max-w-xl mx-auto">
      <div
        ref={cardRef}
        className="relative overflow-hidden rounded-3xl border border-slate-200/60 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl shadow-2xl p-6 md:p-8"
      >
        <div className="absolute -top-24 -right-24 w-56 h-56 bg-sky-100/40 dark:bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex items-center gap-3 mb-6">
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white shadow-lg shadow-sky-500/25">
            <PlaneTakeoff size={20} />
          </span>
          <div>
            <h1 className="text-lg font-bold text-slate-800 dark:text-slate-100">Plan a New Trip</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Give your trip a name and set your travel dates.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} noValidate className="relative space-y-4">
          <label className="flex items-center gap-3 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 px-3.5 py-3 cursor-pointer transition-colors hover:border-sky-400 hover:bg-sky-50/50 dark:hover:bg-sky-900/10">
            <span className="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-400">
              {coverPreview ? (
                <img src={coverPreview} alt="Cover preview" className="h-full w-full object-cover" />
              ) : (
                <Camera size={20} />
              )}
            </span>
            <span className="text-sm text-slate-500 dark:text-slate-400">
              {coverFile ? coverFile.name : "Upload a cover photo (optional)"}
            </span>
            <input type="file" accept="image/*" onChange={handleCoverChange} className="hidden" />
          </label>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5">Trip Name</label>
            <input
              value={form.name}
              onChange={handleChange("name")}
              className={inputClass("name")}
              placeholder="e.g. Summer in Southeast Asia"
            />
            {errors.name && (
              <p className="mt-1.5 text-xs text-rose-500 flex items-center gap-1">
                <span className="inline-block w-1 h-1 rounded-full bg-rose-500" />
                {errors.name}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5 flex items-center gap-1">
                <CalendarDays size={13} className="text-slate-400" />
                Start Date
              </label>
              <input
                type="date"
                value={form.start_date}
                onChange={handleChange("start_date")}
                className={inputClass("start_date")}
              />
              {errors.start_date && (
                <p className="mt-1.5 text-xs text-rose-500 flex items-center gap-1">
                  <span className="inline-block w-1 h-1 rounded-full bg-rose-500" />
                  {errors.start_date}
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5 flex items-center gap-1">
                <CalendarDays size={13} className="text-slate-400" />
                End Date
              </label>
              <input
                type="date"
                value={form.end_date}
                onChange={handleChange("end_date")}
                className={inputClass("end_date")}
              />
              {errors.end_date && (
                <p className="mt-1.5 text-xs text-rose-500 flex items-center gap-1">
                  <span className="inline-block w-1 h-1 rounded-full bg-rose-500" />
                  {errors.end_date}
                </p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5">Description</label>
            <textarea
              rows={3}
              value={form.description}
              onChange={handleChange("description")}
              className={inputClass("description")}
              placeholder="What's this trip about?"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="relative group flex items-center gap-2 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 text-white text-sm font-semibold px-5 py-2.5 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40"
            >
              {submitting ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Creating...
                </span>
              ) : (
                <>
                  Create Trip
                  <ArrowRight size={15} className="transition-transform group-hover:translate-x-1" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}