# GlobeTrotter Capability Matrix (Phase 0 Audit)

Source of truth: actual routes under `server/app/routes/` on the `dev` branch.

## Cities / Destinations

| Feature                    | Method | Endpoint                     | Auth      | MCP Tool (planned)          | Notes                          |
|----------------------------|--------|------------------------------|-----------|-----------------------------|--------------------------------|
| List / Search cities       | GET    | `/api/cities`                | Public    | `search_destinations`       | Supports search, country, region, cost, sort, group_by |
| Get city details           | GET    | `/api/cities/{id}`           | Public    | `get_destination_details`   |                                |
| Create city                | POST   | `/api/cities`                | Admin     | *(not exposed to users)*    | Admin only                     |
| Update city                | PUT    | `/api/cities/{id}`           | Admin     | *(not exposed to users)*    | Admin only                     |
| Delete city                | DELETE | `/api/cities/{id}`           | Admin     | *(not exposed to users)*    | Admin only                     |

## Activities

| Feature                    | Method | Endpoint                     | Auth      | MCP Tool (planned)          | Notes                          |
|----------------------------|--------|------------------------------|-----------|-----------------------------|--------------------------------|
| List / Search activities   | GET    | `/api/activities`            | Public    | `search_activities`         | city_id, category, cost, rating, sort, group_by |
| Get activity details       | GET    | `/api/activities/{id}`       | Public    | `get_activity_details`      |                                |
| Create activity            | POST   | `/api/activities`            | Admin     | *(not exposed)*             | Admin only                     |
| Update / Delete activity   | PUT/DELETE | `/api/activities/{id}`   | Admin     | *(not exposed)*             | Admin only                     |

## Trips

| Feature                    | Method | Endpoint                     | Auth      | MCP Tool (planned)          | Notes                          |
|----------------------------|--------|------------------------------|-----------|-----------------------------|--------------------------------|
| List my trips              | GET    | `/api/trips`                 | JWT       | `list_trips`                | search, status, sort, group_by |
| Create trip                | POST   | `/api/trips`                 | JWT       | `create_trip`               | name, start_date, end_date required |
| Get trip (full)            | GET    | `/api/trips/{id}`            | JWT       | `get_trip`                  | includes stops + itinerary     |
| Update trip                | PUT    | `/api/trips/{id}`            | JWT       | `update_trip`               |                                |
| Delete trip                | DELETE | `/api/trips/{id}`            | JWT       | `delete_trip`               |                                |
| Get budget breakdown       | GET    | `/api/trips/{id}/budget`     | JWT       | `get_trip_budget`           | by_category, by_day, overbudget |
| Share trip                 | POST   | `/api/trips/{id}/share`      | JWT       | `share_trip`                | generates share_slug           |
| Unshare trip               | POST   | `/api/trips/{id}/unshare`    | JWT       | `unshare_trip`              |                                |

## Stops (City legs inside a trip)

| Feature                    | Method | Endpoint                              | Auth | MCP Tool (planned)     |
|----------------------------|--------|---------------------------------------|------|------------------------|
| Add stop                   | POST   | `/api/trips/{id}/stops`               | JWT  | `add_stop_to_trip`     |
| Update stop                | PUT    | `/api/trips/{id}/stops/{stop_id}`     | JWT  | `update_stop`          |
| Delete stop                | DELETE | `/api/trips/{id}/stops/{stop_id}`     | JWT  | `remove_stop`          |
| Reorder stops              | PUT    | `/api/trips/{id}/stops/reorder`       | JWT  | `reorder_stops`        |

## Itinerary Activities

| Feature                         | Method | Endpoint                                              | Auth | MCP Tool (planned)              |
|---------------------------------|--------|-------------------------------------------------------|------|---------------------------------|
| List itinerary for a stop       | GET    | `/api/trips/{tid}/stops/{sid}/itinerary`              | JWT  | `list_itinerary`                |
| Add activity to itinerary       | POST   | `/api/trips/{tid}/stops/{sid}/itinerary`              | JWT  | `add_activity_to_itinerary`     |
| Update itinerary entry          | PUT    | `/api/trips/{tid}/stops/{sid}/itinerary/{entry_id}`   | JWT  | `update_itinerary_activity`     |
| Remove from itinerary           | DELETE | `/api/trips/{tid}/stops/{sid}/itinerary/{entry_id}`   | JWT  | `remove_activity_from_itinerary`|

## Auth (supporting)

| Feature          | Method | Endpoint              | Notes                                      |
|------------------|--------|-----------------------|--------------------------------------------|
| Login            | POST   | `/api/auth/login`     | Returns access_token + refresh_token       |
| Refresh          | POST   | `/api/auth/refresh`   |                                            |
| Current user     | GET    | `/api/auth/me`        | Used to verify identity                    |

The chatbot will receive the user's JWT (or obtain one) and forward it on every authenticated tool call so that authorization rules remain identical to the frontend.

## Explicitly Out of Scope (until backend supports them)

- Booking flights / hotels / payments
- Arbitrary database mutation
- Admin-only city/activity CRUD for normal users
- Any capability that does not already exist as a working API
