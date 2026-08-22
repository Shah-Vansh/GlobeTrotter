/**
 * components/TripCard.jsx
 * Trip summary card used on the Dashboard's "Previous Trips" section and
 * the Trip Listing page's Ongoing/Upcoming/Completed columns.
 */
import { Link } from "react-router-dom";
import { CalendarRange, MapPin, Wallet } from "lucide-react";
import StatusBadge from "./StatusBadge";
import { formatDateRange, formatCurrency } from "../lib/formatters";

export default function TripCard({ trip }) {
  return (
    <Link
      to={`/trips/${trip.id}`}
      className="group block overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200"
    >
      <div className="h-32 w-full bg-gradient-to-br from-sky-400 to-emerald-400 dark:from-sky-700 dark:to-emerald-700 relative">
        {trip.cover_photo_url && (
          <img src={trip.cover_photo_url} alt={trip.name} className="h-full w-full object-cover" />
        )}
        <div className="absolute top-2 right-2">
          <StatusBadge status={trip.status} />
        </div>
      </div>
      <div className="p-4 space-y-2">
        <h3 className="font-semibold text-slate-800 dark:text-slate-100 truncate group-hover:text-sky-600 dark:group-hover:text-sky-400">
          {trip.name}
        </h3>
        <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
          <CalendarRange size={13} />
          {formatDateRange(trip.start_date, trip.end_date)}
        </div>
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1.5">
            <MapPin size={13} /> {trip.destination_count} stop{trip.destination_count === 1 ? "" : "s"}
          </span>
          <span className="flex items-center gap-1.5">
            <Wallet size={13} /> {formatCurrency(trip.total_budget)}
          </span>
        </div>
      </div>
    </Link>
  );
}
