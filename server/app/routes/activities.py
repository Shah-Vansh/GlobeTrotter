"""
Activity search routes (Activity Search screen).
Same Search / Filter / Sort / Group pattern as cities.py, scoped to
activities and additionally filterable by city, category, cost, and rating.
"""
from flask import Blueprint, request

from app.extensions import db
from app.models import Activity, City
from app.utils.responses import success, error
from app.utils.decorators import admin_required

activities_bp = Blueprint("activities", __name__)

SORTABLE_FIELDS = {
    "name": Activity.name,
    "cost": Activity.cost,
    "rating": Activity.rating,
    "duration_minutes": Activity.duration_minutes,
}


@activities_bp.route("", methods=["GET"])
def list_activities():
    """GET /api/activities?search=&city_id=&category=&min_cost=&max_cost=&min_rating=&sort_by=&order=&group_by=category"""
    query = Activity.query

    search = request.args.get("search")
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(Activity.name.ilike(like), Activity.description.ilike(like)))

    city_id = request.args.get("city_id", type=int)
    if city_id:
        query = query.filter(Activity.city_id == city_id)

    category = request.args.get("category")
    if category:
        query = query.filter(Activity.category.ilike(category))

    min_cost = request.args.get("min_cost", type=float)
    max_cost = request.args.get("max_cost", type=float)
    if min_cost is not None:
        query = query.filter(Activity.cost >= min_cost)
    if max_cost is not None:
        query = query.filter(Activity.cost <= max_cost)

    min_rating = request.args.get("min_rating", type=float)
    if min_rating is not None:
        query = query.filter(Activity.rating >= min_rating)

    sort_by = request.args.get("sort_by", "rating")
    order = request.args.get("order", "desc")
    sort_column = SORTABLE_FIELDS.get(sort_by, Activity.rating)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    activities = query.all()

    group_by = request.args.get("group_by")
    if group_by == "category":
        groups = {}
        for a in activities:
            groups.setdefault(a.category or "Other", []).append(a.to_dict())
        return success({"groups": groups})

    return success([a.to_dict() for a in activities])


@activities_bp.route("/<int:activity_id>", methods=["GET"])
def get_activity(activity_id):
    """GET /api/activities/<id>"""
    activity = Activity.query.get(activity_id)
    if not activity:
        return error("Activity not found.", 404)
    return success(activity.to_dict())


@activities_bp.route("", methods=["POST"])
@admin_required
def create_activity():
    """POST /api/activities - admin only."""
    data = request.json or {}
    if not data.get("name") or not data.get("city_id") or not data.get("category"):
        return error("name, city_id and category are required.", 400)
    if not City.query.get(data["city_id"]):
        return error("City not found.", 404)

    activity = Activity(
        city_id=data["city_id"],
        name=data["name"],
        description=data.get("description"),
        category=data["category"],
        cost=data.get("cost", 0.0),
        duration_minutes=data.get("duration_minutes", 60),
        rating=data.get("rating", 0.0),
        image_url=data.get("image_url"),
    )
    db.session.add(activity)
    db.session.commit()
    return success(activity.to_dict(), message="Activity created.", status_code=201)


@activities_bp.route("/<int:activity_id>", methods=["PUT"])
@admin_required
def update_activity(activity_id):
    """PUT /api/activities/<id> - admin only."""
    activity = Activity.query.get(activity_id)
    if not activity:
        return error("Activity not found.", 404)
    data = request.json or {}
    for field in ["name", "description", "category", "cost", "duration_minutes", "rating", "image_url", "city_id"]:
        if field in data:
            setattr(activity, field, data[field])
    db.session.commit()
    return success(activity.to_dict(), message="Activity updated.")


@activities_bp.route("/<int:activity_id>", methods=["DELETE"])
@admin_required
def delete_activity(activity_id):
    """DELETE /api/activities/<id> - admin only."""
    activity = Activity.query.get(activity_id)
    if not activity:
        return error("Activity not found.", 404)
    db.session.delete(activity)
    db.session.commit()
    return success(message="Activity deleted.")
