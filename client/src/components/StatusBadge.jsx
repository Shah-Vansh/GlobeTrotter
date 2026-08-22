/**
 * components/StatusBadge.jsx
 * Small pill used to show a trip's derived status (ongoing/upcoming/completed).
 */
import { TRIP_STATUS_LABELS, TRIP_STATUS_STYLES } from "../lib/constants";

export default function StatusBadge({ status }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
        TRIP_STATUS_STYLES[status] || "bg-slate-100 text-slate-600"
      }`}
    >
      {TRIP_STATUS_LABELS[status] || status}
    </span>
  );
}
