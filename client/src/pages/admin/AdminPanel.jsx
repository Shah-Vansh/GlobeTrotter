/**
 * pages/admin/AdminPanel.jsx
 * Screen 12 - Admin Panel.
 * Four tabs backed by the admin_required-gated routes:
 *   Manage Users        -> GET/PUT /api/admin/users[/<id>/status]
 *   Popular Cities       -> GET /api/admin/analytics/popular-cities
 *   Popular Activities   -> GET /api/admin/analytics/popular-activities
 *   Trends & Analytics    -> GET /api/admin/analytics/trends
 * Route access is also gated client-side by layout/AdminRoute.jsx.
 */
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import { ShieldCheck, Users, Building2, Ticket, TrendingUp, Check, Ban } from "lucide-react";
import api from "../../configs/api";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage } from "../../lib/formatters";
import SearchToolbar from "../../components/SearchToolbar";
import Loader from "../../components/Loader";
import EmptyState from "../../components/EmptyState";

const TABS = [
  { key: "users", label: "Manage Users", icon: Users },
  { key: "cities", label: "Popular Cities", icon: Building2 },
  { key: "activities", label: "Popular Activities", icon: Ticket },
  { key: "trends", label: "User Trends & Analytics", icon: TrendingUp },
];

const PIE_COLORS = ["#0ea5e9", "#f59e0b", "#10b981", "#f43f5e"];

function StatCard({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
      <p className="text-2xl font-bold text-slate-800 dark:text-slate-100 mt-1">{value}</p>
    </div>
  );
}

export default function AdminPanel() {
  useBreadcrumb([{ label: "Admin Panel" }]);
  const [tab, setTab] = useState("users");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <ShieldCheck size={20} className="text-sky-600 dark:text-sky-400" /> Admin Panel
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Manage users and monitor platform-wide travel trends.</p>
      </div>

      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800 overflow-x-auto">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
              tab === key
                ? "border-sky-600 text-sky-600 dark:text-sky-400"
                : "border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
            }`}
          >
            <Icon size={15} /> {label}
          </button>
        ))}
      </div>

      {tab === "users" && <ManageUsersTab />}
      {tab === "cities" && <PopularCitiesTab />}
      {tab === "activities" && <PopularActivitiesTab />}
      {tab === "trends" && <TrendsTab />}
    </div>
  );
}

function ManageUsersTab() {
  const [search, setSearch] = useState("");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadUsers = () => {
    setLoading(true);
    api
      .get("/api/admin/users", { params: { search: search || undefined } })
      .then(({ data }) => setUsers(data.data))
      .catch((err) => toast.error(getErrorMessage(err, "Could not load users.")))
      .finally(() => setLoading(false));
  };

  useEffect(loadUsers, [search]);

  const toggleStatus = async (user) => {
    try {
      await api.put(`/api/admin/users/${user.id}/status`, { is_active: !user.is_active });
      toast.success(`${user.full_name} ${user.is_active ? "deactivated" : "activated"}.`);
      loadUsers();
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not update user status."));
    }
  };

  return (
    <div className="space-y-4">
      <SearchToolbar search={search} onSearchChange={setSearch} searchPlaceholder="Search users by name, username, or email..." />
      {loading ? (
        <Loader label="Loading users..." />
      ) : users.length === 0 ? (
        <EmptyState icon={Users} title="No users found" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800 text-left text-xs text-slate-500 dark:text-slate-400">
              <tr>
                <th className="px-4 py-2.5">User</th>
                <th className="px-4 py-2.5">Email</th>
                <th className="px-4 py-2.5">Trips</th>
                <th className="px-4 py-2.5">Status</th>
                <th className="px-4 py-2.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="px-4 py-2.5 font-medium text-slate-800 dark:text-slate-100">{u.full_name}</td>
                  <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">{u.email}</td>
                  <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">{u.trip_count}</td>
                  <td className="px-4 py-2.5">
                    <span className={`rounded-full px-2 py-0.5 text-xs ${u.is_active ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300" : "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300"}`}>
                      {u.is_active ? "Active" : "Deactivated"}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <button
                      onClick={() => toggleStatus(u)}
                      className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium ${
                        u.is_active
                          ? "bg-rose-50 text-rose-600 hover:bg-rose-100 dark:bg-rose-900/30 dark:text-rose-300"
                          : "bg-emerald-50 text-emerald-600 hover:bg-emerald-100 dark:bg-emerald-900/30 dark:text-emerald-300"
                      }`}
                    >
                      {u.is_active ? <><Ban size={13} /> Deactivate</> : <><Check size={13} /> Activate</>}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function PopularCitiesTab() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/api/admin/analytics/popular-cities")
      .then(({ data }) => setData(data.data))
      .catch((err) => toast.error(getErrorMessage(err, "Could not load popular cities.")))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader label="Loading popular cities..." />;
  if (data.length === 0) return <EmptyState icon={Building2} title="No city data yet" />;

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <ResponsiveContainer width="100%" height={340}>
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis dataKey="city" angle={-30} textAnchor="end" interval={0} height={60} tick={{ fontSize: 11 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="count" name="Times visited" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function PopularActivitiesTab() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/api/admin/analytics/popular-activities")
      .then(({ data }) => setData(data.data))
      .catch((err) => toast.error(getErrorMessage(err, "Could not load popular activities.")))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader label="Loading popular activities..." />;
  if (data.length === 0) return <EmptyState icon={Ticket} title="No activity data yet" />;

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <ResponsiveContainer width="100%" height={340}>
        <BarChart data={data} layout="vertical" margin={{ top: 10, right: 20, left: 40, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
          <YAxis type="category" dataKey="activity" width={140} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="count" name="Times added" fill="#10b981" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function TrendsTab() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/api/admin/analytics/trends")
      .then(({ data }) => setStats(data.data))
      .catch((err) => toast.error(getErrorMessage(err, "Could not load trends.")))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader label="Crunching platform stats..." />;
  if (!stats) return <EmptyState icon={TrendingUp} title="No analytics available" />;

  const statusData = Object.entries(stats.trips_by_status || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Users" value={stats.total_users} />
        <StatCard label="Active Users" value={stats.active_users} />
        <StatCard label="Total Trips" value={stats.total_trips} />
        <StatCard label="Cities / Activities" value={`${stats.total_cities} / ${stats.total_activities}`} />
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-2">Trips by Status</h3>
        {statusData.length === 0 ? (
          <p className="text-sm text-slate-400">No trip data yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                {statusData.map((entry, idx) => (
                  <Cell key={entry.name} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
