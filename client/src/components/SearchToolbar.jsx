/**
 * components/SearchToolbar.jsx
 * The recurring "Search Bar + Group By + Filter + Sort By" toolbar that
 * appears on nearly every screen in the spec (Dashboard, Trip Listing,
 * City/Activity Search, Community, Calendar, Admin). Fully controlled -
 * the parent page owns the actual state and passes handlers in, so this
 * component stays a dumb, reusable layout piece.
 *
 * `sortOptions` / `groupOptions` / `filterOptions` are arrays of
 * { value, label }. Pass an empty array to hide that control.
 */
import { Search, SlidersHorizontal, ArrowDownWideNarrow, Layers } from "lucide-react";

export default function SearchToolbar({
  search,
  onSearchChange,
  searchPlaceholder = "Search...",
  groupOptions = [],
  groupBy,
  onGroupByChange,
  filterOptions = [],
  filterValue,
  onFilterChange,
  sortOptions = [],
  sortBy,
  onSortByChange,
}) {
  return (
    <div className="flex flex-col md:flex-row md:items-center gap-3 w-full">
      <div className="relative flex-1 min-w-0">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange?.(e.target.value)}
          placeholder={searchPlaceholder}
          className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 pl-9 pr-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        {groupOptions.length > 0 && (
          <label className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2 text-sm">
            <Layers size={14} className="text-slate-400" />
            <select
              value={groupBy}
              onChange={(e) => onGroupByChange?.(e.target.value)}
              className="bg-transparent outline-none text-slate-700 dark:text-slate-200"
            >
              <option value="">Group By</option>
              {groupOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </label>
        )}

        {filterOptions.length > 0 && (
          <label className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2 text-sm">
            <SlidersHorizontal size={14} className="text-slate-400" />
            <select
              value={filterValue}
              onChange={(e) => onFilterChange?.(e.target.value)}
              className="bg-transparent outline-none text-slate-700 dark:text-slate-200"
            >
              <option value="">Filter</option>
              {filterOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </label>
        )}

        {sortOptions.length > 0 && (
          <label className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2 text-sm">
            <ArrowDownWideNarrow size={14} className="text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => onSortByChange?.(e.target.value)}
              className="bg-transparent outline-none text-slate-700 dark:text-slate-200"
            >
              <option value="">Sort By</option>
              {sortOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </label>
        )}
      </div>
    </div>
  );
}
