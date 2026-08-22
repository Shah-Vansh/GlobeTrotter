/**
 * pages/search/CitySearch.jsx
 * Screen 8 - City Search (Activity Search / City Search page, city mode).
 * GET /api/cities?search=&region=&sort_by=&order=&group_by=
 */
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Building2 } from "lucide-react";
import api from "../../configs/api";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage } from "../../lib/formatters";
import SearchToolbar from "../../components/SearchToolbar";
import CityCard from "../../components/CityCard";
import EmptyState from "../../components/EmptyState";
import Loader from "../../components/Loader";

export default function CitySearch() {
  useBreadcrumb([{ label: "Explore Cities" }]);

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("popularity");
  const [region, setRegion] = useState("");
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    api
      .get("/api/cities", {
        params: { search: search || undefined, sort_by: sortBy, order: "desc", region: region || undefined },
        signal: controller.signal,
      })
      .then(({ data }) => setCities(data.data))
      .catch((err) => {
        if (err.name !== "CanceledError") toast.error(getErrorMessage(err, "Could not load cities."));
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [search, sortBy, region]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">Explore Cities</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Discover destinations to add to your next trip.</p>
      </div>

      <SearchToolbar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search cities or countries..."
        filterOptions={[
          { value: "Europe", label: "Europe" },
          { value: "Asia", label: "Asia" },
          { value: "South Asia", label: "South Asia" },
          { value: "North America", label: "North America" },
          { value: "South America", label: "South America" },
        ]}
        filterValue={region}
        onFilterChange={setRegion}
        sortOptions={[
          { value: "popularity", label: "Popularity" },
          { value: "cost_index", label: "Cost Index" },
          { value: "name", label: "Name" },
          { value: "country", label: "Country" },
        ]}
        sortBy={sortBy}
        onSortByChange={setSortBy}
      />

      {loading ? (
        <Loader label="Searching cities..." />
      ) : cities.length === 0 ? (
        <EmptyState icon={Building2} title="No cities found" description="Try a different search term or filter." />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {cities.map((city) => (
            <CityCard key={city.id} city={city} />
          ))}
        </div>
      )}
    </div>
  );
}
