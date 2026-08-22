/**
 * pages/trips/TripDetail.jsx
 * Screens 5 + 6 + 9 combined - Itinerary Builder, Itinerary View, and
 * Trip Budget & Cost Breakdown, all scoped to one trip.
 *
 * Data flow:
 *   GET  /api/trips/:id                       -> trip + stops + itinerary_activities
 *   GET  /api/trips/:id/budget                 -> cost breakdown for the chart
 *   POST /api/trips/:id/stops                  -> "Add Stop" (city + dates)
 *   PUT/DELETE .../stops/:stopId                -> edit / remove a stop
 *   POST/PUT/DELETE .../stops/:stopId/itinerary[/:entryId]
 *                                                -> add/edit/remove/reorder
 *                                                   an activity within a day
 *   POST /api/trips/:id/share | /unshare        -> public link toggle
 *
 * Reordering: activities within a day and stops within a trip are
 * reordered with simple up/down controls (order_index), which keeps the
 * daily/overall budget recompute logic on the backend the single source
 * of truth - no separate drag-and-drop library needed.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { gsap } from "gsap";
import {
  CalendarRange,
  MapPin,
  Wallet,
  ArrowLeft,
  Plus,
  Pencil,
  Trash2,
  ChevronUp,
  ChevronDown,
  Share2,
  Copy,
  Check,
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

import api from "../../configs/api";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage, formatDateRange, formatCurrency, toTitleCase } from "../../lib/formatters";
import StatusBadge from "../../components/StatusBadge";
import ExportMenu from "../../components/ExportMenu";
import Loader from "../../components/Loader";
import EmptyState from "../../components/EmptyState";
import Modal from "../../components/Modal";

export default function TripDetail() {
  const { tripId } = useParams();
  const navigate = useNavigate();
  const heroRef = useRef(null);

  const [trip, setTrip] = useState(null);
  const [budget, setBudget] = useState(null);
  const [loading, setLoading] = useState(true);

  // Modal state: which form is open, and which stop/entry it targets.
  const [stopModal, setStopModal] = useState(null); // { mode: 'add'|'edit', stop? }
  const [activityModal, setActivityModal] = useState(null); // { stop, dayNumber, entry? }
  const [deleteTarget, setDeleteTarget] = useState(null); // { type: 'stop'|'trip', id }
  const [shareBusy, setShareBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  useBreadcrumb([{ label: "My Trips", path: "/trips" }, { label: trip?.name || "Trip" }]);

  const loadTrip = useCallback(() => {
    return api
      .get(`/api/trips/${tripId}`)
      .then(({ data }) => setTrip(data.data))
      .catch((err) => toast.error(getErrorMessage(err, "Could not load this trip.")));
  }, [tripId]);

  const loadBudget = useCallback(() => {
    return api
      .get(`/api/trips/${tripId}/budget`)
      .then(({ data }) => setBudget(data.data))
      .catch(() => {}); // Non-critical - the header total already covers the essentials.
  }, [tripId]);

  useEffect(() => {
    setLoading(true);
    Promise.all([loadTrip(), loadBudget()]).finally(() => setLoading(false));
  }, [loadTrip, loadBudget]);

  useEffect(() => {
    if (!loading && heroRef.current) {
      gsap.fromTo(heroRef.current, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" });
    }
  }, [loading]);

  const refreshAll = () => Promise.all([loadTrip(), loadBudget()]);

  // --- Share / unshare ---
  const handleShareToggle = async () => {
    setShareBusy(true);
    try {
      if (trip.is_public) {
        await api.post(`/api/trips/${tripId}/unshare`);
        toast.success("Trip is no longer public.");
      } else {
        await api.post(`/api/trips/${tripId}/share`);
        toast.success("Trip is now shareable!");
      }
      await loadTrip();
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not update sharing."));
    } finally {
      setShareBusy(false);
    }
  };

  const shareUrl = trip?.share_slug
    ? `${window.location.origin}/public/trips/${trip.share_slug}`
    : null;

  const handleCopyLink = () => {
    if (!shareUrl) return;
    navigator.clipboard.writeText(shareUrl).then(() => {
      setCopied(true);
      toast.success("Link copied to clipboard.");
      setTimeout(() => setCopied(false), 2000);
    });
  };

  // --- Stop delete ---
  const handleDeleteStop = async (stopId) => {
    try {
      await api.delete(`/api/trips/${tripId}/stops/${stopId}`);
      toast.success("Stop removed.");
      setDeleteTarget(null);
      refreshAll();
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not remove stop."));
    }
  };

  // --- Stop reorder (swap order_index with neighbor, persist via /reorder) ---
  const handleMoveStop = async (index, direction) => {
    const stops = [...trip.stops];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= stops.length) return;
    [stops[index], stops[targetIndex]] = [stops[targetIndex], stops[index]];
    setTrip((prev) => ({ ...prev, stops })); // optimistic
    try {
      await api.put(`/api/trips/${tripId}/stops/reorder`, { order: stops.map((s) => s.id) });
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not reorder stops."));
      refreshAll();
    }
  };

  // --- Itinerary activity delete ---
  const handleDeleteActivity = async (stopId, entryId) => {
    try {
      await api.delete(`/api/trips/${tripId}/stops/${stopId}/itinerary/${entryId}`);
      toast.success("Activity removed.");
      refreshAll();
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not remove activity."));
    }
  };

  // --- Itinerary activity reorder within a day ---
  const handleMoveActivity = async (stop, dayEntries, index, direction) => {
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= dayEntries.length) return;
    const reordered = [...dayEntries];
    [reordered[index], reordered[targetIndex]] = [reordered[targetIndex], reordered[index]];
    try {
      await Promise.all(
        reordered.map((entry, i) =>
          api.put(`/api/trips/${tripId}/stops/${stop.id}/itinerary/${entry.id}`, { order_index: i })
        )
      );
      refreshAll();
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not reorder activities."));
    }
  };

  if (loading) return <Loader fullScreen label="Loading itinerary..." />;
  if (!trip) return <EmptyState title="Trip not found" description="It may have been deleted or you don't have access." />;

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate("/trips")}
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-sky-600 dark:hover:text-sky-400"
      >
        <ArrowLeft size={15} /> Back to My Trips
      </button>

      {/* --- Hero / summary card --- */}
      <div ref={heroRef} className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
        <div className="h-40 bg-gradient-to-br from-sky-400 to-emerald-400 dark:!from-sky-700 dark:!to-emerald-700">
          {trip.cover_photo_url && <img src={trip.cover_photo_url} alt={trip.name} className="h-full w-full object-cover" />}
        </div>
        <div className="p-5 space-y-3">
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">{trip.name}</h1>
                <StatusBadge status={trip.status} />
              </div>
              {trip.description && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400 max-w-2xl">{trip.description}</p>}
            </div>
            <div className="flex items-center gap-2">
              <ExportMenu tripId={trip.id} tripName={trip.name} />
              <button
                type="button"
                onClick={() => setDeleteTarget({ type: "trip", id: trip.id })}
                className="inline-flex items-center gap-2 rounded-lg border border-rose-200 dark:border-rose-900 bg-white dark:bg-slate-900 px-3 py-2 text-sm font-medium text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950"
              >
                <Trash2 size={15} /> Delete Trip
              </button>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-5 text-sm text-slate-600 dark:text-slate-300 pt-2">
            <span className="flex items-center gap-1.5"><CalendarRange size={15} /> {formatDateRange(trip.start_date, trip.end_date)}</span>
            <span className="flex items-center gap-1.5"><MapPin size={15} /> {trip.destination_count} stop{trip.destination_count === 1 ? "" : "s"}</span>
            <span className="flex items-center gap-1.5 font-semibold text-slate-800 dark:text-slate-100"><Wallet size={15} /> {formatCurrency(trip.total_budget)} total budget</span>
          </div>

          {/* --- Share section --- */}
          <div className="flex flex-wrap items-center gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
            <button
              type="button"
              onClick={handleShareToggle}
              disabled={shareBusy}
              className={`inline-flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors disabled:opacity-60 ${
                trip.is_public
                  ? "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
              }`}
            >
              <Share2 size={14} /> {trip.is_public ? "Public" : "Make Public"}
            </button>
            {trip.is_public && shareUrl && (
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <input
                  readOnly
                  value={shareUrl}
                  className="flex-1 min-w-0 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1.5 text-xs text-slate-500 dark:text-slate-400 truncate"
                />
                <button
                  type="button"
                  onClick={handleCopyLink}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-700 px-2.5 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 shrink-0"
                >
                  {copied ? <Check size={13} /> : <Copy size={13} />} {copied ? "Copied" : "Copy Link"}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* --- Budget breakdown chart --- */}
      {budget && Object.keys(budget.by_category || {}).length > 0 && (
        <section className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Cost Breakdown</h2>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              Avg {formatCurrency(budget.average_cost_per_day)}/day
            </span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={Object.entries(budget.by_category).map(([category, cost]) => ({ category: toTitleCase(category), cost }))}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-slate-100 dark:stroke-slate-800" />
              <XAxis dataKey="category" tick={{ fontSize: 12 }} stroke="currentColor" className="text-slate-500" />
              <YAxis tick={{ fontSize: 12 }} stroke="currentColor" className="text-slate-500" />
              <Tooltip formatter={(value) => formatCurrency(value)} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              <Bar dataKey="cost" fill="#0284c7" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>
      )}

      {/* --- Stops / itinerary builder --- */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Itinerary by Stop</h2>
          <button
            type="button"
            onClick={() => setStopModal({ mode: "add" })}
            className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-3 py-1.5"
          >
            <Plus size={15} /> Add Stop
          </button>
        </div>

        {(!trip.stops || trip.stops.length === 0) ? (
          <EmptyState
            icon={MapPin}
            title="No stops added yet"
            description="Add a city stop to start building your day-by-day itinerary and budget."
            action={
              <button
                onClick={() => setStopModal({ mode: "add" })}
                className="rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-4 py-2"
              >
                Add Your First Stop
              </button>
            }
          />
        ) : (
          <div className="space-y-4">
            {trip.stops.map((stop, stopIndex) => (
              <StopCard
                key={stop.id}
                stop={stop}
                stopIndex={stopIndex}
                stopCount={trip.stops.length}
                onMoveStop={handleMoveStop}
                onEditStop={() => setStopModal({ mode: "edit", stop })}
                onDeleteStop={() => setDeleteTarget({ type: "stop", id: stop.id, label: stop.city?.name })}
                onAddActivity={(dayNumber) => setActivityModal({ stop, dayNumber })}
                onEditActivity={(entry) => setActivityModal({ stop, dayNumber: entry.day_number, entry })}
                onDeleteActivity={(entryId) => handleDeleteActivity(stop.id, entryId)}
                onMoveActivity={handleMoveActivity}
              />
            ))}
          </div>
        )}
      </section>

      {/* --- Modals --- */}
      {stopModal && (
        <StopFormModal
          tripId={tripId}
          mode={stopModal.mode}
          stop={stopModal.stop}
          tripDates={{ start: trip.start_date, end: trip.end_date }}
          onClose={() => setStopModal(null)}
          onSaved={() => {
            setStopModal(null);
            refreshAll();
          }}
        />
      )}

      {activityModal && (
        <ActivityFormModal
          tripId={tripId}
          stop={activityModal.stop}
          dayNumber={activityModal.dayNumber}
          entry={activityModal.entry}
          onClose={() => setActivityModal(null)}
          onSaved={() => {
            setActivityModal(null);
            refreshAll();
          }}
        />
      )}

      {deleteTarget && (
        <Modal open onClose={() => setDeleteTarget(null)} title={deleteTarget.type === "trip" ? "Delete this trip?" : "Remove this stop?"} maxWidth="max-w-sm">
          <p className="text-sm text-slate-600 dark:text-slate-300 mb-5">
            {deleteTarget.type === "trip"
              ? "This permanently deletes the trip and its entire itinerary. This cannot be undone."
              : `This removes ${deleteTarget.label || "this city"} and every activity planned for it. This cannot be undone.`}
          </p>
          <div className="flex items-center justify-end gap-3">
            <button onClick={() => setDeleteTarget(null)} className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">
              Cancel
            </button>
            <button
              onClick={async () => {
                if (deleteTarget.type === "trip") {
                  try {
                    await api.delete(`/api/trips/${tripId}`);
                    toast.success("Trip deleted.");
                    navigate("/trips");
                  } catch (err) {
                    toast.error(getErrorMessage(err, "Could not delete trip."));
                  }
                } else {
                  handleDeleteStop(deleteTarget.id);
                }
              }}
              className="rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-4 py-2"
            >
              Delete
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* StopCard - one city leg, its day-by-day activities, and controls   */
/* ------------------------------------------------------------------ */
function StopCard({
  stop,
  stopIndex,
  stopCount,
  onMoveStop,
  onEditStop,
  onDeleteStop,
  onAddActivity,
  onEditActivity,
  onDeleteActivity,
  onMoveActivity,
}) {
  // Group this stop's activities by day_number, in order_index order.
  const days = {};
  for (let d = 1; d <= (stop.day_count || 1); d++) days[d] = [];
  (stop.itinerary_activities || [])
    .slice()
    .sort((a, b) => a.order_index - b.order_index)
    .forEach((entry) => {
      if (!days[entry.day_number]) days[entry.day_number] = [];
      days[entry.day_number].push(entry);
    });

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <h3 className="font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
          <MapPin size={15} className="text-sky-600 dark:text-sky-400" /> {stop.city?.name || "Unnamed stop"}
          <span className="text-xs font-normal text-slate-400">{stop.city?.country}</span>
        </h3>
        <div className="flex items-center gap-1">
          <span className="text-xs text-slate-500 dark:text-slate-400 mr-2">{formatDateRange(stop.start_date, stop.end_date)}</span>
          <IconBtn onClick={() => onMoveStop(stopIndex, -1)} disabled={stopIndex === 0} title="Move stop earlier"><ChevronUp size={14} /></IconBtn>
          <IconBtn onClick={() => onMoveStop(stopIndex, 1)} disabled={stopIndex === stopCount - 1} title="Move stop later"><ChevronDown size={14} /></IconBtn>
          <IconBtn onClick={onEditStop} title="Edit dates"><Pencil size={14} /></IconBtn>
          <IconBtn onClick={onDeleteStop} title="Remove stop" danger><Trash2 size={14} /></IconBtn>
        </div>
      </div>

      <div className="space-y-3">
        {Object.entries(days).map(([dayNumber, entries]) => {
          const dayTotal = entries.reduce((sum, e) => sum + (e.cost ?? e.activity?.cost ?? 0), 0);
          return (
            <div key={dayNumber} className="rounded-lg bg-slate-50 dark:bg-slate-800/60 p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                  Day {dayNumber}
                  {dayTotal > 0 && <span className="ml-2 font-normal normal-case text-slate-400">{formatCurrency(dayTotal)}</span>}
                </span>
                <button
                  type="button"
                  onClick={() => onAddActivity(Number(dayNumber))}
                  className="inline-flex items-center gap-1 text-xs font-medium text-sky-600 dark:text-sky-400 hover:underline"
                >
                  <Plus size={12} /> Add Activity
                </button>
              </div>
              {entries.length === 0 ? (
                <p className="text-sm text-slate-400 dark:text-slate-500">No activities planned for this day yet.</p>
              ) : (
                <ul className="space-y-1.5">
                  {entries.map((entry, idx) => (
                    <li key={entry.id} className="flex items-center justify-between gap-2 text-sm rounded-lg bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 px-3 py-2">
                      <div className="min-w-0">
                        <p className="text-slate-700 dark:text-slate-200 truncate">
                          {entry.start_time ? `${entry.start_time.slice(0, 5)} - ` : ""}{entry.activity?.name || "Activity"}
                        </p>
                        {entry.notes && <p className="text-xs text-slate-400 truncate">{entry.notes}</p>}
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        <span className="font-medium text-slate-600 dark:text-slate-300 mr-1">{formatCurrency(entry.cost ?? entry.activity?.cost)}</span>
                        <IconBtn onClick={() => onMoveActivity(stop, entries, idx, -1)} disabled={idx === 0} title="Move up"><ChevronUp size={13} /></IconBtn>
                        <IconBtn onClick={() => onMoveActivity(stop, entries, idx, 1)} disabled={idx === entries.length - 1} title="Move down"><ChevronDown size={13} /></IconBtn>
                        <IconBtn onClick={() => onEditActivity(entry)} title="Edit"><Pencil size={13} /></IconBtn>
                        <IconBtn onClick={() => onDeleteActivity(entry.id)} title="Remove" danger><Trash2 size={13} /></IconBtn>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function IconBtn({ children, onClick, disabled, title, danger }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`rounded-md p-1 disabled:opacity-30 disabled:cursor-not-allowed transition-colors ${
        danger
          ? "text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950"
          : "text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-600 dark:hover:text-slate-200"
      }`}
    >
      {children}
    </button>
  );
}

/* ------------------------------------------------------------------ */
/* StopFormModal - "Add Stop" / "Edit Stop dates"                     */
/* ------------------------------------------------------------------ */
function StopFormModal({ tripId, mode, stop, tripDates, onClose, onSaved }) {
  const [cities, setCities] = useState([]);
  const [citySearch, setCitySearch] = useState("");
  const [form, setForm] = useState({
    city_id: stop?.city_id || "",
    start_date: stop?.start_date || tripDates.start,
    end_date: stop?.end_date || tripDates.end,
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    api
      .get("/api/cities", { params: { search: citySearch || undefined, sort_by: "popularity", order: "desc" }, signal: controller.signal })
      .then(({ data }) => setCities(data.data))
      .catch(() => {});
    return () => controller.abort();
  }, [citySearch]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.city_id) return toast.error("Choose a city for this stop.");
    if (!form.start_date || !form.end_date) return toast.error("Start and end dates are required.");
    if (form.end_date < form.start_date) return toast.error("End date cannot be before the start date.");

    setSubmitting(true);
    try {
      if (mode === "edit") {
        await api.put(`/api/trips/${tripId}/stops/${stop.id}`, form);
        toast.success("Stop updated.");
      } else {
        await api.post(`/api/trips/${tripId}/stops`, form);
        toast.success("Stop added.");
      }
      onSaved();
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not save this stop."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open onClose={onClose} title={mode === "edit" ? "Edit Stop" : "Add a Stop"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {mode !== "edit" && (
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">City</label>
            <input
              type="text"
              value={citySearch}
              onChange={(e) => setCitySearch(e.target.value)}
              placeholder="Search cities..."
              className="w-full mb-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500"
            />
            <select
              value={form.city_id}
              onChange={(e) => setForm((p) => ({ ...p, city_id: e.target.value }))}
              className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500"
              size={Math.min(6, Math.max(3, cities.length))}
            >
              {cities.map((c) => (
                <option key={c.id} value={c.id}>{c.name}, {c.country}</option>
              ))}
            </select>
          </div>
        )}

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Start Date</label>
            <input type="date" value={form.start_date} onChange={(e) => setForm((p) => ({ ...p, start_date: e.target.value }))} className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">End Date</label>
            <input type="date" value={form.end_date} onChange={(e) => setForm((p) => ({ ...p, end_date: e.target.value }))} className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500" />
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button type="button" onClick={onClose} className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">
            Cancel
          </button>
          <button type="submit" disabled={submitting} className="rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-5 py-2 disabled:opacity-60">
            {submitting ? "Saving..." : mode === "edit" ? "Save Changes" : "Add Stop"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

/* ------------------------------------------------------------------ */
/* ActivityFormModal - "Add Activity" / "Edit Activity" for a day     */
/* ------------------------------------------------------------------ */
function ActivityFormModal({ tripId, stop, dayNumber, entry, onClose, onSaved }) {
  const isEdit = Boolean(entry);
  const [activities, setActivities] = useState([]);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState({
    activity_id: entry?.activity_id || "",
    start_time: entry?.start_time ? entry.start_time.slice(0, 5) : "",
    cost: entry?.cost ?? "",
    notes: entry?.notes || "",
  });
  const [submitting, setSubmitting] = useState(false);

  // Browse activities available in this stop's city.
  useEffect(() => {
    if (isEdit) return;
    const controller = new AbortController();
    api
      .get("/api/activities", { params: { city_id: stop.city_id, search: search || undefined, sort_by: "rating", order: "desc" }, signal: controller.signal })
      .then(({ data }) => setActivities(data.data))
      .catch(() => {});
    return () => controller.abort();
  }, [stop.city_id, search, isEdit]);

  // Pre-fill cost from the selected activity's base cost when adding new.
  const handleSelectActivity = (activityId) => {
    const picked = activities.find((a) => String(a.id) === String(activityId));
    setForm((p) => ({ ...p, activity_id: activityId, cost: picked ? picked.cost : p.cost }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isEdit && !form.activity_id) return toast.error("Choose an activity to add.");

    setSubmitting(true);
    try {
      const payload = {
        day_number: dayNumber,
        date: stop.start_date, // simple default; the day badge is what matters for grouping
        start_time: form.start_time || undefined,
        cost: form.cost === "" ? undefined : Number(form.cost),
        notes: form.notes || undefined,
      };
      if (isEdit) {
        await api.put(`/api/trips/${tripId}/stops/${stop.id}/itinerary/${entry.id}`, payload);
        toast.success("Activity updated.");
      } else {
        await api.post(`/api/trips/${tripId}/stops/${stop.id}/itinerary`, { ...payload, activity_id: form.activity_id });
        toast.success("Activity added to Day " + dayNumber + ".");
      }
      onSaved();
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not save this activity."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open onClose={onClose} title={isEdit ? "Edit Activity" : `Add Activity - Day ${dayNumber}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {!isEdit && (
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">
              Activity in {stop.city?.name}
            </label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search activities..."
              className="w-full mb-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500"
            />
            {activities.length === 0 ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 py-2">No activities found for this city yet.</p>
            ) : (
              <select
                value={form.activity_id}
                onChange={(e) => handleSelectActivity(e.target.value)}
                className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500"
                size={Math.min(6, Math.max(3, activities.length))}
              >
                <option value="" disabled>Select an activity...</option>
                {activities.map((a) => (
                  <option key={a.id} value={a.id}>{a.name} - {toTitleCase(a.category)} - {formatCurrency(a.cost)}</option>
                ))}
              </select>
            )}
          </div>
        )}

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Start Time</label>
            <input type="time" value={form.start_time} onChange={(e) => setForm((p) => ({ ...p, start_time: e.target.value }))} className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Cost ($)</label>
            <input type="number" min="0" step="0.01" value={form.cost} onChange={(e) => setForm((p) => ({ ...p, cost: e.target.value }))} className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">Notes (optional)</label>
          <textarea rows={2} value={form.notes} onChange={(e) => setForm((p) => ({ ...p, notes: e.target.value }))} className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500" placeholder="Booking reference, reminders, etc." />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button type="button" onClick={onClose} className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">
            Cancel
          </button>
          <button type="submit" disabled={submitting} className="rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-5 py-2 disabled:opacity-60">
            {submitting ? "Saving..." : isEdit ? "Save Changes" : "Add Activity"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
