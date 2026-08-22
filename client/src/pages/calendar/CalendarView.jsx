/**
 * pages/calendar/CalendarView.jsx
 * Screen 11 - Calendar View Page.
 * GET /api/calendar?month=YYYY-MM returns { month, events: [...] } where
 * each event is either a "trip" (spans start_date..end_date) or an
 * "activity" (single date). We build a classic month grid and mark each
 * day that falls inside an event's range.
 */
import { useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { ChevronLeft, ChevronRight, CalendarDays } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../../configs/api";
import { useBreadcrumb } from "../../lib/useBreadcrumb";
import { getErrorMessage } from "../../lib/formatters";
import Loader from "../../components/Loader";

function toMonthKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function buildMonthGrid(year, month) {
  // month is 0-indexed here (JS Date convention).
  const firstDay = new Date(year, month, 1);
  const startOffset = firstDay.getDay(); // 0 = Sunday
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const cells = [];
  for (let i = 0; i < startOffset; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(new Date(year, month, d));
  return cells;
}

const EVENT_COLORS = {
  trip: "bg-sky-500",
  activity: "bg-emerald-500",
};

export default function CalendarView() {
  useBreadcrumb([{ label: "Calendar" }]);
  const navigate = useNavigate();
  const [cursor, setCursor] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const monthKey = toMonthKey(cursor);
  const cells = useMemo(() => buildMonthGrid(cursor.getFullYear(), cursor.getMonth()), [cursor]);

  useEffect(() => {
    setLoading(true);
    api
      .get("/api/calendar", { params: { month: monthKey } })
      .then(({ data }) => setEvents(data.data.events))
      .catch((err) => toast.error(getErrorMessage(err, "Could not load the calendar.")))
      .finally(() => setLoading(false));
  }, [monthKey]);

  const eventsForDay = (day) => {
    if (!day) return [];
    const iso = day.toISOString().slice(0, 10);
    return events.filter((ev) => {
      if (ev.type === "trip") return iso >= ev.start_date && iso <= ev.end_date;
      return ev.date === iso;
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <CalendarDays size={20} className="text-sky-600 dark:text-sky-400" /> Calendar
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Your trips and activities at a glance.</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1))} className="rounded-lg border border-slate-200 dark:border-slate-700 p-2 hover:bg-slate-100 dark:hover:bg-slate-800">
            <ChevronLeft size={16} />
          </button>
          <span className="text-sm font-semibold w-32 text-center text-slate-700 dark:text-slate-200">
            {cursor.toLocaleDateString(undefined, { month: "long", year: "numeric" })}
          </span>
          <button onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1))} className="rounded-lg border border-slate-200 dark:border-slate-700 p-2 hover:bg-slate-100 dark:hover:bg-slate-800">
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {loading ? (
        <Loader label="Loading calendar..." />
      ) : (
        <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
          <div className="grid grid-cols-7 border-b border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-500 dark:text-slate-400">
            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
              <div key={d} className="px-2 py-2 text-center">{d}</div>
            ))}
          </div>
          <div className="grid grid-cols-7">
            {cells.map((day, idx) => {
              const dayEvents = eventsForDay(day);
              return (
                <div
                  key={idx}
                  className={`min-h-24 border-b border-r border-slate-100 dark:border-slate-800 p-1.5 text-xs ${
                    day ? "" : "bg-slate-50 dark:bg-slate-950/40"
                  }`}
                >
                  {day && (
                    <>
                      <span className="text-slate-500 dark:text-slate-400">{day.getDate()}</span>
                      <div className="mt-1 space-y-1">
                        {dayEvents.slice(0, 2).map((ev) => (
                          <button
                            key={`${ev.type}-${ev.id}`}
                            onClick={() => ev.type === "trip" && navigate(`/trips/${ev.id}`)}
                            title={ev.title}
                            className={`w-full truncate rounded px-1 py-0.5 text-[10px] text-left text-white ${EVENT_COLORS[ev.type]}`}
                          >
                            {ev.title}
                          </button>
                        ))}
                        {dayEvents.length > 2 && (
                          <span className="text-[10px] text-slate-400">+{dayEvents.length - 2} more</span>
                        )}
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
