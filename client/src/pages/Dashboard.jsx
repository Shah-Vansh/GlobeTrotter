/**
 * pages/Dashboard.jsx
 * Screen 3 - Main Landing Page.
 * Banner -> search/group/filter/sort toolbar -> Top Regional Selections
 * (GET /api/cities, sorted by popularity) -> Previous Trips (GET /api/trips)
 * -> floating "+ Plan a Trip" button.
 */
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { gsap } from "gsap";
import { Plus, Sparkles, ArrowRight } from "lucide-react";
import toast from "react-hot-toast";
import api from "../configs/api";
import { useBreadcrumb } from "../lib/useBreadcrumb";
import { getErrorMessage } from "../lib/formatters";
import SearchToolbar from "../components/SearchToolbar";
import CityCard from "../components/CityCard";
import TripCard from "../components/TripCard";
import EmptyState from "../components/EmptyState";
import Loader from "../components/Loader";
import { Map as MapIcon, Building2, Globe2 } from "lucide-react";

export default function Dashboard() {
  useBreadcrumb([{ label: "Dashboard" }]);
  const navigate = useNavigate();
  const bannerRef = useRef(null);

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("popularity");
  const [groupBy, setGroupBy] = useState("");
  const [filterValue, setFilterValue] = useState("");

  const [cities, setCities] = useState([]);
  const [trips, setTrips] = useState([]);
  const [loadingCities, setLoadingCities] = useState(true);
  const [loadingTrips, setLoadingTrips] = useState(true);

  useEffect(() => {
    gsap.fromTo(
      bannerRef.current,
      { opacity: 0, scale: 0.98 },
      { opacity: 1, scale: 1, duration: 0.6, ease: "power2.out" }
    );
  }, []);

  // Fetch Top Regional Selections whenever search/sort/filter changes.
  useEffect(() => {
    const controller = new AbortController();
    setLoadingCities(true);
    api
      .get("/api/cities", {
        params: { search: search || undefined, sort_by: sortBy, order: "desc", region: filterValue || undefined },
        signal: controller.signal,
      })
      .then(({ data }) => setCities(data.data.slice(0, 8)))
      .catch((err) => {
        if (err.name !== "CanceledError") toast.error(getErrorMessage(err, "Could not load destinations."));
      })
      .finally(() => setLoadingCities(false));
    return () => controller.abort();
  }, [search, sortBy, filterValue]);

  // Previous trips.
  useEffect(() => {
    setLoadingTrips(true);
    api
      .get("/api/trips", { params: { sort_by: "start_date", order: "desc" } })
      .then(({ data }) => setTrips(data.data.slice(0, 6)))
      .catch((err) => toast.error(getErrorMessage(err, "Could not load your trips.")))
      .finally(() => setLoadingTrips(false));
  }, []);

  return (
    <div className="space-y-8 relative pb-16">
      {/* Banner */}
      <div
        ref={bannerRef}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-sky-600 via-sky-600 to-indigo-700 text-white px-6 py-10 md:py-14 shadow-xl shadow-sky-500/20"
      >
        <Sparkles className="absolute -top-4 -right-4 opacity-20" size={140} />
        <div className="absolute -bottom-24 -left-24 w-72 h-72 bg-white/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/2 right-1/4 -translate-y-1/2 w-64 h-64 bg-indigo-400/20 rounded-full blur-3xl pointer-events-none" />
        <h1 className="relative text-2xl md:text-3xl font-bold">Where to next?</h1>
        <p className="relative mt-2 text-sm md:text-base text-sky-50/90 max-w-xl">
          Discover destinations, build day-by-day itineraries, and keep every trip on budget - all in one place.
        </p>
      </div>

      {/* Toolbar */}
      <SearchToolbar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search destinations, cities, or activities..."
        groupOptions={[{ value: "region", label: "Region" }, { value: "country", label: "Country" }]}
        groupBy={groupBy}
        onGroupByChange={setGroupBy}
        filterOptions={[
          { value: "Europe", label: "Europe" },
          { value: "Asia", label: "Asia" },
          { value: "South Asia", label: "South Asia" },
          { value: "North America", label: "North America" },
        ]}
        filterValue={filterValue}
        onFilterChange={setFilterValue}
        sortOptions={[
          { value: "popularity", label: "Popularity" },
          { value: "cost_index", label: "Cost" },
          { value: "name", label: "Name" },
        ]}
        sortBy={sortBy}
        onSortByChange={setSortBy}
      />

      {/* Top Regional Selections */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white shadow-md shadow-sky-500/25">
              <Building2 size={16} />
            </span>
            Top Regional Selections
          </h2>
        </div>
        {loadingCities ? (
          <Loader label="Finding great destinations..." />
        ) : cities.length === 0 ? (
          <EmptyState icon={Building2} title="No destinations found" description="Try a different search or filter." />
        ) : groupBy ? (
          // Grouped view: bucket cities by the selected field (region/country)
          // and render each group under its own heading.
          Object.entries(
            cities.reduce((groups, city) => {
              const key = city[groupBy] || "Other";
              (groups[key] = groups[key] || []).push(city);
              return groups;
            }, {})
          ).map(([groupLabel, groupCities]) => (
            <div key={groupLabel} className="space-y-2">
              <h3 className="flex items-center gap-1.5 text-sm font-semibold text-slate-500 dark:text-slate-400">
                <Globe2 size={14} className="text-sky-500" /> {groupLabel}
                <span className="font-normal text-slate-400">({groupCities.length})</span>
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {groupCities.map((city) => (
                  <CityCard key={city.id} city={city} onSelect={() => navigate("/search/cities")} />
                ))}
              </div>
            </div>
          ))
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {cities.map((city) => (
              <CityCard key={city.id} city={city} onSelect={() => navigate("/search/cities")} />
            ))}
          </div>
        )}
      </section>

      {/* Previous Trips */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white shadow-md shadow-sky-500/25">
            <MapIcon size={16} />
          </span>
          Previous Trips
        </h2>
        {loadingTrips ? (
          <Loader label="Loading your trips..." />
        ) : trips.length === 0 ? (
          <EmptyState
            icon={MapIcon}
            title="No trips yet"
            description="Plan your first trip to see it show up here."
            action={
              <button
                onClick={() => navigate("/trips/new")}
                className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 text-white text-sm font-semibold px-5 py-2.5 shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40 transition-all duration-300"
              >
                Plan a Trip
                <ArrowRight size={15} className="transition-transform group-hover:translate-x-1" />
              </button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {trips.map((trip) => (
              <TripCard key={trip.id} trip={trip} />
            ))}
          </div>
        )}
      </section>

      {/* Floating Plan a Trip button */}
      <button
        onClick={() => navigate("/trips/new")}
        className="group fixed bottom-6 right-6 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-700 hover:to-indigo-700 text-white font-medium px-5 py-3 shadow-xl shadow-sky-500/30 hover:shadow-2xl hover:shadow-sky-500/40 transition-all duration-300"
      >
        <Plus size={18} className="transition-transform group-hover:rotate-90 duration-300" /> Plan a Trip
      </button>
    </div>
  );
}