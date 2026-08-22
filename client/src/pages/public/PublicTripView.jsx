/**
 * pages/public/PublicTripView.jsx
 * Screen 11 - Shared/Public Itinerary View.
 * Unauthenticated, read-only page at /public/trips/:slug backed by
 * GET /api/public/trips/:slug. Anyone with the link can view it, and a
 * signed-in visitor can "Copy Trip" to clone it into their own account
 * (signed-out visitors are sent to /login and returned here after).
 *
 * "Copy Trip" implementation note: the backend's
 * POST /api/public/trips/:slug/copy intentionally only validates the
 * slug and returns the trip payload (copying requires an authenticated
 * owner). So the actual clone is built here: create a new trip shell via
 * POST /api/trips, then re-create each stop and itinerary activity under
 * the new trip via the normal authenticated trip endpoints.
 */
import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useSelector } from "react-redux";
import toast from "react-hot-toast";
import { Compass, CalendarRange, MapPin, Wallet, Copy, ArrowLeft, User } from "lucide-react";

import api from "../../configs/api";
import ThemeToggle from "../../components/ThemeToggle";
import Loader from "../../components/Loader";
import EmptyState from "../../components/EmptyState";
import { formatDateRange, formatCurrency, getErrorMessage } from "../../lib/formatters";

export default function PublicTripView() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);

  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [copying, setCopying] = useState(false);

  useEffect(() => {
    setLoading(true);
    setNotFound(false);
    api
      .get(`/api/public/trips/${slug}`)
      .then(({ data }) => setTrip(data.data))
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [slug]);

  const handleCopyTrip = async () => {
    if (!user) {
      toast("Log in to copy this trip to your account.", { icon: "info" });
      navigate("/login", { state: { from: { pathname: `/public/trips/${slug}` } } });
      return;
    }

    setCopying(true);
    try {
      // 1. Re-validate the slug and grab the full payload to clone from.
      const { data: copyRes } = await api.post(`/api/public/trips/${slug}/copy`);
      const source = copyRes.data;

      // 2. Create the new trip shell in the visitor's own account.
      const tripPayload = new FormData();
      tripPayload.append("name", `${source.name} (Copy)`);
      tripPayload.append("start_date", source.start_date);
      tripPayload.append("end_date", source.end_date);
      if (source.description) tripPayload.append("description", source.description);
      const { data: newTripRes } = await api.post("/api/trips", tripPayload);
      const newTrip = newTripRes.data;

      // 3. Re-create each stop, then each of its itinerary activities.
      for (const stop of source.stops || []) {
        const { data: stopRes } = await api.post(`/api/trips/${newTrip.id}/stops`, {
          city_id: stop.city_id,
          start_date: stop.start_date,
          end_date: stop.end_date,
        });
        const newStop = stopRes.data;

        for (const entry of stop.itinerary_activities || []) {
          await api.post(`/api/trips/${newTrip.id}/stops/${newStop.id}/itinerary`, {
            activity_id: entry.activity_id,
            day_number: entry.day_number,
            date: entry.date,
            start_time: entry.start_time ? entry.start_time.slice(0, 5) : undefined,
            cost: entry.cost,
            notes: entry.notes,
          });
        }
      }

      toast.success("Trip copied to your account!");
      navigate(`/trips/${newTrip.id}`);
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not copy this trip."));
    } finally {
      setCopying(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* --- Minimal public header (no sidebar/auth chrome) --- */}
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-600 text-white">
              <Compass size={16} />
            </span>
            <span className="font-bold text-slate-800 dark:text-slate-100">GlobeTrotter</span>
          </Link>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            {user ? (
              <Link to="/" className="text-sm font-medium text-sky-600 dark:text-sky-400 hover:underline">
                Go to Dashboard
              </Link>
            ) : (
              <Link to="/login" className="text-sm font-medium text-sky-600 dark:text-sky-400 hover:underline">
                Log In
              </Link>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {loading ? (
          <Loader fullScreen label="Loading shared itinerary..." />
        ) : notFound || !trip ? (
          <EmptyState
            icon={MapPin}
            title="This shared trip isn't available"
            description="The link may be incorrect, or the owner has made this trip private again."
            action={
              <button onClick={() => navigate("/")} className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-4 py-2">
                <ArrowLeft size={15} /> Go Home
              </button>
            }
          />
        ) : (
          <div className="space-y-6">
            {/* --- Trip summary --- */}
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
              <div className="h-40 bg-gradient-to-br from-sky-400 to-emerald-400 dark:!from-sky-700 dark:!to-emerald-700">
                {trip.cover_photo_url && <img src={trip.cover_photo_url} alt={trip.name} className="h-full w-full object-cover" />}
              </div>
              <div className="p-5 space-y-3">
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div>
                    <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">{trip.name}</h1>
                    {trip.owner && (
                      <p className="mt-0.5 flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
                        <User size={12} /> Shared by {trip.owner.full_name || trip.owner.username}
                      </p>
                    )}
                    {trip.description && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400 max-w-2xl">{trip.description}</p>}
                  </div>
                  <button
                    type="button"
                    onClick={handleCopyTrip}
                    disabled={copying}
                    className="inline-flex items-center gap-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-4 py-2 disabled:opacity-60"
                  >
                    <Copy size={15} /> {copying ? "Copying..." : "Copy Trip"}
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-5 text-sm text-slate-600 dark:text-slate-300 pt-2">
                  <span className="flex items-center gap-1.5"><CalendarRange size={15} /> {formatDateRange(trip.start_date, trip.end_date)}</span>
                  <span className="flex items-center gap-1.5"><MapPin size={15} /> {trip.destination_count} stop{trip.destination_count === 1 ? "" : "s"}</span>
                  <span className="flex items-center gap-1.5 font-semibold text-slate-800 dark:text-slate-100"><Wallet size={15} /> {formatCurrency(trip.total_budget)} total budget</span>
                </div>
              </div>
            </div>

            {/* --- Read-only itinerary by stop --- */}
            <section className="space-y-4">
              <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Itinerary</h2>
              {(!trip.stops || trip.stops.length === 0) ? (
                <EmptyState icon={MapPin} title="No stops in this itinerary yet" />
              ) : (
                trip.stops.map((stop) => (
                  <div key={stop.id} className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
                        <MapPin size={15} className="text-sky-600 dark:text-sky-400" /> {stop.city?.name || "Unnamed stop"}
                      </h3>
                      <span className="text-xs text-slate-500 dark:text-slate-400">{formatDateRange(stop.start_date, stop.end_date)}</span>
                    </div>
                    {(!stop.itinerary_activities || stop.itinerary_activities.length === 0) ? (
                      <p className="text-sm text-slate-400 dark:text-slate-500">No activities added for this stop yet.</p>
                    ) : (
                      <ul className="space-y-2">
                        {stop.itinerary_activities.map((entry) => (
                          <li key={entry.id} className="flex items-center justify-between text-sm rounded-lg bg-slate-50 dark:bg-slate-800 px-3 py-2">
                            <span className="text-slate-700 dark:text-slate-200">
                              Day {entry.day_number} - {entry.activity?.name || "Activity"}
                            </span>
                            <span className="font-medium text-slate-600 dark:text-slate-300">{formatCurrency(entry.cost ?? entry.activity?.cost)}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))
              )}
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
