/**
 * pages/trips/TripsList.jsx
 * Screen 6 - User Trip Listing Page.
 * GET /api/trips?group_by=status returns { groups: { ongoing, upcoming,
 * completed } } which maps 1:1 onto the three required sections.
 */
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Map } from "lucide-react";
import toast from "react-hot-toast";
import api from "../../configs/api";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage } from "../../lib/formatters";
import SearchToolbar from "../../components/SearchToolbar";
import TripCard from "../../components/TripCard";
import EmptyState from "../../components/EmptyState";
import Loader from "../../components/Loader";

const SECTIONS = [
  { key: "ongoing", label: "Ongoing" },
  { key: "upcoming", label: "Upcoming" },
  { key: "completed", label: "Completed" },
];

export default function TripsList() {
  useBreadcrumb([{ label: "My Trips" }]);
  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("start_date");
  const [groups, setGroups] = useState({ ongoing: [], upcoming: [], completed: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    api
      .get("/api/trips", {
        params: { search: search || undefined, sort_by: sortBy, order: "desc", group_by: "status" },
        signal: controller.signal,
      })
      .then(({ data }) => setGroups(data.data.groups))
      .catch((err) => {
        if (err.name !== "CanceledError") toast.error(getErrorMessage(err, "Could not load trips."));
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [search, sortBy]);

  const totalTrips = groups.ongoing.length + groups.upcoming.length + groups.completed.length;

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">My Trips</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Every trip you've planned, organized by status.</p>
        </div>
        <button
          onClick={() => navigate("/trips/new")}
          className="inline-flex items-center gap-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white text-sm font-medium px-4 py-2 self-start"
        >
          <Plus size={16} /> Plan a Trip
        </button>
      </div>

      <SearchToolbar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search by trip name, destination, or activity..."
        sortOptions={[
          { value: "start_date", label: "Start Date" },
          { value: "name", label: "Name" },
          { value: "created_at", label: "Recently Created" },
        ]}
        sortBy={sortBy}
        onSortByChange={setSortBy}
      />

      {loading ? (
        <Loader label="Loading your trips..." />
      ) : totalTrips === 0 ? (
        <EmptyState
          icon={Map}
          title="No trips match your search"
          description="Adjust your search or plan a brand new trip."
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
        SECTIONS.map(({ key, label }) => (
          <section key={key} className="space-y-3">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">
              {label} <span className="text-sm font-normal text-slate-400">({groups[key].length})</span>
            </h2>
            {groups[key].length === 0 ? (
              <p className="text-sm text-slate-400 dark:text-slate-500">No {label.toLowerCase()} trips.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {groups[key].map((trip) => (
                  <TripCard key={trip.id} trip={trip} />
                ))}
              </div>
            )}
          </section>
        ))
      )}
    </div>
  );
}
