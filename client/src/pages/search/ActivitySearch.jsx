/**
 * pages/search/ActivitySearch.jsx
 * Screen 8 - Activity Search (activity mode).
 * GET /api/activities?search=&category=&sort_by=&order=&group_by=
 */
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Ticket } from "lucide-react";
import api from "../../configs/api";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage } from "../../lib/formatters";
import SearchToolbar from "../../components/SearchToolbar";
import ActivityCard from "../../components/ActivityCard";
import EmptyState from "../../components/EmptyState";
import Loader from "../../components/Loader";

const CATEGORIES = ["sightseeing", "food", "adventure", "culture", "relaxation", "nightlife"];

export default function ActivitySearch() {
  useBreadcrumb([{ label: "Explore Activities" }]);

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("rating");
  const [category, setCategory] = useState("");
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    api
      .get("/api/activities", {
        params: { search: search || undefined, sort_by: sortBy, order: "desc", category: category || undefined },
        signal: controller.signal,
      })
      .then(({ data }) => setActivities(data.data))
      .catch((err) => {
        if (err.name !== "CanceledError") toast.error(getErrorMessage(err, "Could not load activities."));
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [search, sortBy, category]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">Explore Activities</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Find things to do and add them to your itinerary.</p>
      </div>

      <SearchToolbar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search activities..."
        filterOptions={CATEGORIES.map((c) => ({ value: c, label: c[0].toUpperCase() + c.slice(1) }))}
        filterValue={category}
        onFilterChange={setCategory}
        sortOptions={[
          { value: "rating", label: "Rating" },
          { value: "cost", label: "Cost" },
          { value: "duration_minutes", label: "Duration" },
          { value: "name", label: "Name" },
        ]}
        sortBy={sortBy}
        onSortByChange={setSortBy}
      />

      {loading ? (
        <Loader label="Searching activities..." />
      ) : activities.length === 0 ? (
        <EmptyState icon={Ticket} title="No activities found" description="Try a different search term or category." />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {activities.map((activity) => (
            <ActivityCard
              key={activity.id}
              activity={activity}
              onAdd={() => toast("Open a trip's itinerary to add this activity.", { icon: "info" })}
            />
          ))}
        </div>
      )}
    </div>
  );
}
