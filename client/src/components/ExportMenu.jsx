/**
 * components/ExportMenu.jsx
 * "Export data" dropdown (CSV / Excel / PDF) backed by
 * GET /api/export/trips/<id>/{csv,excel,pdf}. Used on the Itinerary /
 * Trip Budget view.
 */
import { useState, useRef, useEffect } from "react";
import { Download, FileSpreadsheet, FileText, FileType } from "lucide-react";
import toast from "react-hot-toast";
import { exportTrip } from "../lib/exportUtils";
import { getErrorMessage } from "../lib/formatters";

const FORMATS = [
  { key: "csv", label: "CSV", icon: FileText },
  { key: "excel", label: "Excel (.xlsx)", icon: FileSpreadsheet },
  { key: "pdf", label: "PDF", icon: FileType },
];

export default function ExportMenu({ tripId, tripName }) {
  const [open, setOpen] = useState(false);
  const [downloading, setDownloading] = useState(null);
  const ref = useRef(null);

  useEffect(() => {
    function onClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const handleExport = async (format) => {
    setDownloading(format);
    try {
      await exportTrip(tripId, format, tripName);
      toast.success(`Exported as ${format.toUpperCase()}.`);
    } catch (err) {
      toast.error(getErrorMessage(err, "Export failed."));
    } finally {
      setDownloading(null);
      setOpen(false);
    }
  };

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800"
      >
        <Download size={16} /> Export
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-48 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg py-1 z-10">
          {FORMATS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              type="button"
              disabled={downloading === key}
              onClick={() => handleExport(key)}
              className="flex w-full items-center gap-2 px-3 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-50"
            >
              <Icon size={15} /> {downloading === key ? "Exporting..." : label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
