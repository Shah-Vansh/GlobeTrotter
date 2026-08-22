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
import { Camera, PlaneTakeoff } from "lucide-react";
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
    gsap.fromTo(cardRef.current, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
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
    if (!validate()) return;

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
    `w-full rounded-lg border bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500 ${
      errors[field] ? "border-rose-400" : "border-slate-200 dark:border-slate-700"
    }`;

  return (
    <div className="max-w-xl mx-auto">
      <div ref={cardRef} className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-6 md:p-8">
        <div className="flex items-center gap-2 mb-6">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-50 dark:bg-sky-900/40 text-sky-600 dark:text-sky-400">
            <PlaneTakeoff size={18} />
          </span>
          <div>
            <h1 className="text-lg font-bold text-slate-800 dark:text-slate-100">Plan a New Trip</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Give your trip a name and set your travel dates.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <label className="flex items-center gap-3 rounded-lg border border-dashed border-slate-300 dark:border-slate-700 px-3 py-3 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800">
            <span className="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-400">
              {coverPreview ? <img src={coverPreview} alt="Cover preview" className="h-full w-full object-cover" /> : <Camera size={20} />}
            </span>
            <span className="text-sm text-slate-500 dark:text-slate-400">
              {coverFile ? coverFile.name : "Upload a cover photo (optional)"}
            </span>
            <input type="file" accept="image/*" onChange={handleCoverChange} className="hidden" />
          </label>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Trip Name</label>
            <input value={form.name} onChange={handleChange("name")} className={inputClass("name")} placeholder="e.g. Summer in Southeast Asia" />
            {errors.name && <p className="mt-1 text-xs text-rose-500">{errors.name}</p>}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Start Date</label>
              <input type="date" value={form.start_date} onChange={handleChange("start_date")} className={inputClass("start_date")} />
              {errors.start_date && <p className="mt-1 text-xs text-rose-500">{errors.start_date}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">End Date</label>
              <input type="date" value={form.end_date} onChange={handleChange("end_date")} className={inputClass("end_date")} />
              {errors.end_date && <p className="mt-1 text-xs text-rose-500">{errors.end_date}</p>}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Description</label>
            <textarea rows={3} value={form.description} onChange={handleChange("description")} className={inputClass("description")} placeholder="What's this trip about?" />
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button type="button" onClick={() => navigate(-1)} className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">
              Cancel
            </button>
            <button type="submit" disabled={submitting} className="rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-5 py-2 disabled:opacity-60">
              {submitting ? "Creating..." : "Create Trip"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
