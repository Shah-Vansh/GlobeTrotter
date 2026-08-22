"""
Export routes.
Lets a user download a trip's itinerary/budget as CSV, Excel (.xlsx),
or PDF - the "Export data" feature.
"""
import io

import pandas as pd
from flask import Blueprint, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.models import Trip
from app.utils.responses import error

export_bp = Blueprint("export", __name__)


def _build_rows(trip: Trip):
    """Flatten a trip's stops/itinerary into row dicts shared by every export format."""
    rows = []
    for stop in trip.stops:
        city_name = stop.city.name if stop.city else "Unknown"
        for entry in stop.itinerary_activities:
            rows.append(
                {
                    "City": city_name,
                    "Day": entry.day_number,
                    "Date": entry.date.isoformat() if entry.date else "",
                    "Activity": entry.activity.name if entry.activity else "",
                    "Category": entry.activity.category if entry.activity else "",
                    "Cost": entry.cost if entry.cost is not None else (entry.activity.cost if entry.activity else 0),
                }
            )
    return rows


def _get_owned_trip(trip_id, user_id):
    return Trip.query.filter_by(id=trip_id, user_id=user_id).first()


@export_bp.route("/trips/<int:trip_id>/csv", methods=["GET"])
@jwt_required()
def export_csv(trip_id):
    """GET /api/export/trips/<id>/csv"""
    trip = _get_owned_trip(trip_id, get_jwt_identity())
    if not trip:
        return error("Trip not found.", 404)

    df = pd.DataFrame(_build_rows(trip))
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(
        buffer, mimetype="text/csv", as_attachment=True, download_name=f"{trip.name}_itinerary.csv"
    )


@export_bp.route("/trips/<int:trip_id>/excel", methods=["GET"])
@jwt_required()
def export_excel(trip_id):
    """GET /api/export/trips/<id>/excel"""
    trip = _get_owned_trip(trip_id, get_jwt_identity())
    if not trip:
        return error("Trip not found.", 404)

    df = pd.DataFrame(_build_rows(trip))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Itinerary")
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"{trip.name}_itinerary.xlsx",
    )


@export_bp.route("/trips/<int:trip_id>/pdf", methods=["GET"])
@jwt_required()
def export_pdf(trip_id):
    """GET /api/export/trips/<id>/pdf"""
    trip = _get_owned_trip(trip_id, get_jwt_identity())
    if not trip:
        return error("Trip not found.", 404)

    rows = _build_rows(trip)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph(f"{trip.name}", styles["Title"]),
        Paragraph(f"{trip.start_date} to {trip.end_date}", styles["Normal"]),
        Spacer(1, 12),
    ]

    table_data = [["City", "Day", "Date", "Activity", "Category", "Cost"]]
    for r in rows:
        table_data.append([r["City"], r["Day"], r["Date"], r["Activity"], r["Category"], r["Cost"]])

    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Total Budget: {trip.total_budget}", styles["Heading2"]))

    doc.build(elements)
    buffer.seek(0)
    return send_file(
        buffer, mimetype="application/pdf", as_attachment=True, download_name=f"{trip.name}_itinerary.pdf"
    )
