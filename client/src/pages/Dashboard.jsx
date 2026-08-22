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
import { Plus, Sparkles } from "lucide-react";
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
    gsap.fromTo(bannerRef.current, { opacity: 0, scale: 0.98 }, { opacity: 1, scale: 1, duration: 0.6, ease: "power2.out" });
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
        className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-sky-600 via-sky-500 to-emerald-500 text-white px-6 py-10 md:py-14"
      >
        <Sparkles className="absolute -top-4 -right-4 opacity-20" size={140} />
        <h1 className="text-2xl md:text-3xl font-bold">Where to next?</h1>
        <p className="mt-2 text-sm md:text-base text-sky-50 max-w-xl">
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
            <Building2 size={18} className="text-sky-600 dark:text-sky-400" /> Top Regional Selections
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
                <Globe2 size={14} /> {groupLabel}
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
          <MapIcon size={18} className="text-sky-600 dark:text-sky-400" /> Previous Trips
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
                className="rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-4 py-2"
              >
                Plan a Trip
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
        className="fixed bottom-6 right-6 inline-flex items-center gap-2 rounded-full bg-sky-600 hover:bg-sky-700 text-white font-medium px-5 py-3 shadow-xl hover:shadow-2xl transition-all"
      >
        <Plus size={18} /> Plan a Trip
      </button>
    </div>
  );
}
