"""
City search routes (City Search screen).
Supports free-text search, filtering by country/region, sorting, and
"group by" so the frontend toolbar (Search / Group By / Filter / Sort By)
maps 1:1 onto query params.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import City
from app.utils.responses import success, error
from app.utils.decorators import admin_required

cities_bp = Blueprint("cities", __name__)

SORTABLE_FIELDS = {
    "name": City.name,
    "popularity": City.popularity,
    "cost_index": City.cost_index,
    "country": City.country,
}


@cities_bp.route("", methods=["GET"])
def list_cities():
    """GET /api/cities?search=&country=&region=&sort_by=&order=&group_by=

    - search: matches city name or country (case-insensitive, partial)
    - country / region: exact-match filters
    - sort_by: one of name|popularity|cost_index|country (default popularity)
    - order: asc|desc (default desc)
    - group_by: region|country -> response becomes { groups: { key: [cities] } }
    """
    query = City.query

    search = request.args.get("search")
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(City.name.ilike(like), City.country.ilike(like)))

    country = request.args.get("country")
    if country:
        query = query.filter(City.country.ilike(country))

    region = request.args.get("region")
    if region:
        query = query.filter(City.region.ilike(region))

    min_cost = request.args.get("min_cost", type=float)
    max_cost = request.args.get("max_cost", type=float)
    if min_cost is not None:
        query = query.filter(City.cost_index >= min_cost)
    if max_cost is not None:
        query = query.filter(City.cost_index <= max_cost)

    sort_by = request.args.get("sort_by", "popularity")
    order = request.args.get("order", "desc")
    sort_column = SORTABLE_FIELDS.get(sort_by, City.popularity)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    cities = query.all()

    group_by = request.args.get("group_by")
    if group_by in ("region", "country"):
        groups = {}
        for c in cities:
            key = getattr(c, group_by) or "Other"
            groups.setdefault(key, []).append(c.to_dict())
        return success({"groups": groups})

    return success([c.to_dict() for c in cities])


@cities_bp.route("/<int:city_id>", methods=["GET"])
def get_city(city_id):
    """GET /api/cities/<id>"""
    city = City.query.get(city_id)
    if not city:
        return error("City not found.", 404)
    return success(city.to_dict())


@cities_bp.route("", methods=["POST"])
@admin_required
def create_city():
    """POST /api/cities - admin only."""
    data = request.json or {}
    if not data.get("name") or not data.get("country"):
        return error("name and country are required.", 400)

    city = City(
        name=data["name"],
        country=data["country"],
        region=data.get("region"),
        description=data.get("description"),
        image_url=data.get("image_url"),
        cost_index=data.get("cost_index", 5.0),
        popularity=data.get("popularity", 0),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
    )
    db.session.add(city)
    db.session.commit()
    return success(city.to_dict(), message="City created.", status_code=201)


@cities_bp.route("/<int:city_id>", methods=["PUT"])
@admin_required
def update_city(city_id):
    """PUT /api/cities/<id> - admin only."""
    city = City.query.get(city_id)
    if not city:
        return error("City not found.", 404)
    data = request.json or {}
    for field in ["name", "country", "region", "description", "image_url",
                  "cost_index", "popularity", "latitude", "longitude"]:
        if field in data:
            setattr(city, field, data[field])
    db.session.commit()
    return success(city.to_dict(), message="City updated.")


@cities_bp.route("/<int:city_id>", methods=["DELETE"])
@admin_required
def delete_city(city_id):
    """DELETE /api/cities/<id> - admin only."""
    city = City.query.get(city_id)
    if not city:
        return error("City not found.", 404)
    db.session.delete(city)
    db.session.commit()
    return success(message="City deleted.")
