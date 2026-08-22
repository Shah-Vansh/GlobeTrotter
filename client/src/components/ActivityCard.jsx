/**
 * components/ActivityCard.jsx
 * Used by the Activity Search results grid.
 */
import { Star, Clock, MapPin } from "lucide-react";
import { formatCurrency, toTitleCase } from "../lib/formatters";

export default function ActivityCard({ activity, onAdd }) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:shadow-lg transition-shadow duration-200">
      <div className="h-28 w-full bg-gradient-to-br from-violet-300 to-sky-400 dark:!from-violet-700 dark:!to-sky-700">
        {activity.image_url && (
          <img src={activity.image_url} alt={activity.name} className="h-full w-full object-cover" />
        )}
      </div>
      <div className="p-3 space-y-1.5">
        <div className="flex items-start justify-between gap-2">
          <h4 className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">{activity.name}</h4>
          <span className="shrink-0 text-xs rounded-full bg-sky-50 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300 px-2 py-0.5">
            {toTitleCase(activity.category)}
          </span>
        </div>
        <p className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
          <MapPin size={12} /> {activity.city_name}
        </p>
        <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1"><Clock size={12} /> {activity.duration_minutes} min</span>
          <span className="flex items-center gap-1"><Star size={12} className="text-amber-400" /> {activity.rating}</span>
        </div>
        <div className="flex items-center justify-between pt-1">
          <span className="font-semibold text-sm text-slate-700 dark:text-slate-200">
            {formatCurrency(activity.cost)}
          </span>
          {onAdd && (
            <button
              type="button"
              onClick={() => onAdd(activity)}
              className="text-xs font-medium rounded-lg bg-sky-600 hover:bg-sky-700 text-white px-2.5 py-1.5 transition-colors"
            >
              Add to Trip
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
