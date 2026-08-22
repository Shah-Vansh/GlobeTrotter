/**
 * lib/exportUtils.js
 * Triggers a file download for the backend's CSV / Excel / PDF export
 * routes (GET /api/export/trips/<id>/{csv,excel,pdf}). The backend already
 * returns the file as a binary stream, so we just need to request it with
 * responseType "blob" and hand the blob to file-saver.
 */
import { saveAs } from "file-saver";
import api from "../configs/api";

const FORMAT_CONFIG = {
  csv: { path: "csv", ext: "csv" },
  excel: { path: "excel", ext: "xlsx" },
  pdf: { path: "pdf", ext: "pdf" },
};

/**
 * Download a trip's itinerary/budget export.
 * @param {number} tripId
 * @param {"csv"|"excel"|"pdf"} format
 * @param {string} tripName used to build a friendly filename
 */
export async function exportTrip(tripId, format, tripName = "trip") {
  const config = FORMAT_CONFIG[format];
  if (!config) throw new Error(`Unsupported export format: ${format}`);

  const response = await api.get(`/api/export/trips/${tripId}/${config.path}`, {
    responseType: "blob",
  });

  const safeName = tripName.replace(/[^a-z0-9]+/gi, "_").toLowerCase();
  saveAs(response.data, `${safeName}_itinerary.${config.ext}`);
}
