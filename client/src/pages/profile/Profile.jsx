/**
 * pages/profile/Profile.jsx
 * User Profile / Settings screen. Edits the fields exposed by
 * PUT /api/users/me, uploads a new photo via POST /api/users/me/photo,
 * and lists saved destinations (GET/DELETE /api/users/me/saved-destinations).
 */
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import toast from "react-hot-toast";
import { Camera, Save, Trash2, MapPin, Heart } from "lucide-react";
import api from "../../configs/api";
import { setUser } from "../../store/slices/authSlice";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage } from "../../lib/formatters";
import Loader from "../../components/Loader";
import EmptyState from "../../components/EmptyState";

export default function Profile() {
  useBreadcrumb([{ label: "Profile" }]);
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);

  const [form, setForm] = useState({
    first_name: "", last_name: "", phone_number: "", city: "", country: "", additional_info: "",
  });
  const [saving, setSaving] = useState(false);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [saved, setSaved] = useState([]);
  const [loadingSaved, setLoadingSaved] = useState(true);

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        phone_number: user.phone_number || "",
        city: user.city || "",
        country: user.country || "",
        additional_info: user.additional_info || "",
      });
    }
  }, [user]);

  useEffect(() => {
    api
      .get("/api/users/me/saved-destinations")
      .then(({ data }) => setSaved(data.data))
      .catch(() => {})
      .finally(() => setLoadingSaved(false));
  }, []);

  const handleChange = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const { data } = await api.put("/api/users/me", form);
      dispatch(setUser(data.data));
      toast.success("Profile updated.");
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not update profile."));
    } finally {
      setSaving(false);
    }
  };

  const handlePhotoChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingPhoto(true);
    try {
      const payload = new FormData();
      payload.append("profile_photo", file);
      const { data } = await api.post("/api/users/me/photo", payload);
      dispatch(setUser({ ...user, profile_photo_url: data.data.profile_photo_url }));
      toast.success("Profile photo updated.");
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not upload photo."));
    } finally {
      setUploadingPhoto(false);
    }
  };

  const removeSaved = async (id) => {
    try {
      await api.delete(`/api/users/me/saved-destinations/${id}`);
      setSaved((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not remove destination."));
    }
  };

  if (!user) return <Loader fullScreen />;

  const inputClass =
    "w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 px-3.5 py-2.5 text-sm outline-none transition-all duration-200 placeholder:text-slate-400 focus:ring-2 focus:ring-sky-500/30 focus:border-sky-500 focus:shadow-[0_0_0_4px_rgba(14,165,233,0.1)] hover:border-slate-300 dark:hover:border-slate-600";

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">Profile & Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Manage your personal information and preferences.</p>
      </div>

      <div className="relative overflow-hidden rounded-3xl border border-slate-200/60 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl shadow-xl p-6 space-y-6">
        <div className="absolute -top-24 -right-24 w-56 h-56 bg-sky-100/40 dark:bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex items-center gap-4">
          <label className="relative cursor-pointer group shrink-0">
            <span className="flex h-16 w-16 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 text-white shadow-lg shadow-sky-500/25">
              {user.profile_photo_url ? (
                <img src={user.profile_photo_url} alt="" className="h-full w-full object-cover" />
              ) : (
                <Camera size={22} />
              )}
            </span>
            <input type="file" accept="image/*" onChange={handlePhotoChange} className="hidden" disabled={uploadingPhoto} />
            <span className="absolute -bottom-1 -right-1 rounded-full bg-sky-600 text-white text-[10px] px-1.5 py-0.5 group-hover:bg-sky-700 transition-colors">
              {uploadingPhoto ? "..." : "Edit"}
            </span>
          </label>
          <div>
            <p className="font-semibold text-slate-800 dark:text-slate-100">{user.full_name}</p>
            <p className="text-sm text-slate-500 dark:text-slate-400">@{user.username} &middot; {user.email}</p>
          </div>
        </div>

        <form onSubmit={handleSave} className="relative space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5">First Name</label>
              <input value={form.first_name} onChange={handleChange("first_name")} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5">Last Name</label>
              <input value={form.last_name} onChange={handleChange("last_name")} className={inputClass} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5">Phone Number</label>
              <input value={form.phone_number} onChange={handleChange("phone_number")} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5">City</label>
              <input value={form.city} onChange={handleChange("city")} className={inputClass} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5">Country</label>
            <input value={form.country} onChange={handleChange("country")} className={inputClass} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1.5">Additional Information</label>
            <textarea rows={3} value={form.additional_info} onChange={handleChange("additional_info")} className={inputClass} />
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 text-white text-sm font-semibold px-5 py-2.5 shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <Save size={15} /> {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-rose-400 to-rose-600 text-white shadow-md shadow-rose-500/25">
            <Heart size={16} fill="currentColor" />
          </span>
          Saved Destinations
        </h2>
        {loadingSaved ? (
          <Loader label="Loading saved destinations..." />
        ) : saved.length === 0 ? (
          <EmptyState icon={MapPin} title="No saved destinations" description="Cities you save will show up here." />
        ) : (
          <ul className="space-y-2">
            {saved.map((s) => (
              <li
                key={s.id}
                className="flex items-center justify-between rounded-xl border border-slate-200/60 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl px-4 py-2.5 text-sm shadow-sm hover:shadow-md transition-shadow duration-300"
              >
                <span className="flex items-center gap-2 text-slate-700 dark:text-slate-200">
                  <MapPin size={14} className="text-sky-500" /> {s.city?.name}, {s.city?.country}
                </span>
                <button
                  onClick={() => removeSaved(s.id)}
                  className="text-slate-400 hover:text-rose-500 transition-colors p-1 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-900/20"
                >
                  <Trash2 size={15} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}