/**
 * lib/formatters.js
 * Small, dependency-free formatting helpers reused across pages.
 */

/** Format an ISO date string ("2026-08-22") into a readable label. */
export function formatDate(isoDate, options = { month: "short", day: "numeric", year: "numeric" }) {
  if (!isoDate) return "";
  const d = new Date(isoDate);
  if (Number.isNaN(d.getTime())) return isoDate;
  return d.toLocaleDateString(undefined, options);
}

/** Format a start/end date pair as "Aug 22 - Aug 28, 2026". */
export function formatDateRange(start, end) {
  if (!start || !end) return "";
  return `${formatDate(start, { month: "short", day: "numeric" })} - ${formatDate(end)}`;
}

/** Format a number as currency (defaults to USD, no cents when whole). */
export function formatCurrency(amount, currency = "USD") {
  const value = Number(amount) || 0;
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: value % 1 === 0 ? 0 : 2,
  }).format(value);
}

/** Turn "san_francisco" / "san-francisco" into "San Francisco". */
export function toTitleCase(value) {
  if (!value) return "";
  return String(value)
    .replace(/[_-]/g, " ")
    .replace(/\w\S*/g, (w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase());
}

/** Build a readable "N days" label from two ISO dates. */
export function tripDurationLabel(start, end) {
  if (!start || !end) return "";
  const ms = new Date(end) - new Date(start);
  const days = Math.max(1, Math.round(ms / 86400000) + 1);
  return `${days} day${days === 1 ? "" : "s"}`;
}

/** Extract a friendly error message from a failed axios call. */
export function getErrorMessage(err, fallback = "Something went wrong. Please try again.") {
  return err?.response?.data?.message || err?.message || fallback;
}
