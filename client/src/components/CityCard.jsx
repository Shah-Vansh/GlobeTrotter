/**
 * components/CityCard.jsx
 * Used by the Dashboard's "Top Regional Selections" and the City Search
 * results grid.
 */
import { MapPin, Star, TrendingUp } from "lucide-react";

export default function CityCard({ city, onSelect }) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(city)}
      className="text-left group overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200"
    >
      <div className="h-28 w-full bg-gradient-to-br from-amber-300 to-rose-400 dark:!from-amber-700 dark:!to-rose-700">
        {city.image_url && (
          <img src={city.image_url} alt={city.name} className="h-full w-full object-cover" />
        )}
      </div>
      <div className="p-3 space-y-1">
        <h4 className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate group-hover:text-sky-600 dark:group-hover:text-sky-400">
          {city.name}
        </h4>
        <p className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400 truncate">
          <MapPin size={12} /> {city.country}
        </p>
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 pt-1">
          <span className="flex items-center gap-1">
            <TrendingUp size={12} /> Popularity {city.popularity}
          </span>
          <span>Cost {city.cost_index}/10</span>
        </div>
      </div>
    </button>
  );
}
