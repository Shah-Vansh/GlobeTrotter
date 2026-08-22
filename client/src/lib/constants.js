/**
 * lib/constants.js
 * Shared constant values used across pages/components.
 */
export const TRIP_STATUS = {
  ONGOING: "ongoing",
  UPCOMING: "upcoming",
  COMPLETED: "completed",
};

export const TRIP_STATUS_LABELS = {
  ongoing: "Ongoing",
  upcoming: "Upcoming",
  completed: "Completed",
};

export const TRIP_STATUS_STYLES = {
  ongoing: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  upcoming: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  completed: "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
};

// Sidebar / breadcrumb navigation source-of-truth.
export const NAV_LINKS = [
  { label: "Dashboard", path: "/", icon: "LayoutDashboard" },
  { label: "My Trips", path: "/trips", icon: "Map" },
  { label: "Explore Cities", path: "/search/cities", icon: "Building2" },
  { label: "Explore Activities", path: "/search/activities", icon: "Ticket" },
  { label: "Community", path: "/community", icon: "Users" },
  { label: "Calendar", path: "/calendar", icon: "CalendarDays" },
  { label: "Profile", path: "/profile", icon: "UserCircle" },
];

export const ADMIN_NAV_LINK = { label: "Admin Panel", path: "/admin", icon: "ShieldCheck" };
