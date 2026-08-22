# GlobeTrotter

Personalized, collaborative travel planning app. Users build multi-city itineraries, assign activities and dates, get automatic budget breakdowns, and share trips publicly.

## Tech Stack

**Frontend**
- React 18 (Vite) + React Router v6
- Redux Toolkit — auth, theme (light/dark), UI state (breadcrumbs, preferences)
- Tailwind CSS v4 (`@tailwindcss/vite`, no config file)
- Axios — JWT access/refresh interceptor
- GSAP — entrance/transition animations
- Recharts — budget & admin analytics charts
- react-hot-toast — notifications
- lucide-react — icons

**Backend**
- Flask + Flask-SQLAlchemy + Flask-Migrate
- Flask-JWT-Extended — access + refresh token auth
- PostgreSQL (SQLite supported for local/dev testing)
- Cloudinary — image uploads (profile photos, trip covers)
- Brevo (Transactional Email API) — password reset / notifications
- openpyxl / reportlab — Excel / PDF export

## Project Structure

```
globetrotter/
├── server/                  # Flask API
│   ├── app/
│   │   ├── models/          # SQLAlchemy models (User, Trip, Stop, City, Activity, ...)
│   │   ├── routes/          # Blueprints: auth, trips, itinerary, cities, activities,
│   │   │                    #   community, calendar, admin, public, export, health
│   │   ├── services/        # Cloudinary, Brevo, export (CSV/Excel/PDF) helpers
│   │   ├── extensions.py    # db, migrate, jwt, cors singletons
│   │   └── config.py
│   ├── seed.py               # dummy data: cities, activities, demo users, trips
│   ├── run.py
│   └── .env.example
│
├── frontend/                # React app
│   └── src/
│       ├── components/      # Reusable UI: cards, modals, toolbars, export menu
│       ├── layout/           # Header, Sidebar, Breadcrumb, ProtectedRoute, AdminRoute
│       ├── pages/            # auth/ trips/ search/ community/ calendar/ profile/ admin/ public/
│       ├── store/            # Redux slices: auth, theme, ui
│       ├── configs/api.js    # Axios instance (baseURL + JWT interceptor)
│       └── lib/               # formatters, constants, breadcrumb hook
│
└── README.md
```

## Getting Started

### 1. Database (PostgreSQL)

Create the database before starting the backend:

```bash
# using psql
psql -U postgres -c "CREATE DATABASE globetrotter;"

# or, from the psql shell
psql -U postgres
postgres=# CREATE DATABASE globetrotter;
```

Use this database name in `DATABASE_URL` below, e.g.:
```
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/globetrotter
```

### 2. Backend

```bash
cd server
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # fill in DATABASE_URL, JWT secrets, Cloudinary, Brevo keys
python seed.py                   # creates tables + seeds demo cities/activities/users
python run.py                    # runs on http://localhost:5000
```

`GET /api/health` should return `{"success": true, "data": {"status": "healthy", ...}}`.

For local testing without PostgreSQL, set `DATABASE_URL=sqlite:///test.db` in `.env`.

**Demo accounts** (from `seed.py`):

| Role  | Username | Password      |
|-------|----------|---------------|
| Admin | `admin`  | `Admin@123`   |
| User  | `alice`  | `Password@123`|
| User  | `bob`    | `Password@123`|

### 3. Frontend

```bash
cd frontend
npm install

cp .env.example .env            # set VITE_BASE_URL to the backend URL above
npm run dev                      # runs on http://localhost:5173
```

> **Important:** Vite only reads `.env` at server start. If you create or edit it while `npm run dev` is already running, restart the dev server.

## Environment Variables

**`server/.env`**

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL (or `sqlite:///file.db` for local dev) connection string |
| `SECRET_KEY` / `JWT_SECRET_KEY` | Flask & JWT signing secrets |
| `CLOUDINARY_URL` | Cloudinary account URL for image uploads |
| `BREVO_API_KEY` | Brevo transactional email API key |
| `FRONTEND_URL` | Used to build public share links |

**`frontend/.env`**

| Variable | Description |
|---|---|
| `VITE_BASE_URL` | Backend API origin, e.g. `http://localhost:5000` |

## Core Features

- JWT auth (login/register/refresh), route guards for authenticated & admin-only pages
- Trip CRUD with cover photo upload (Cloudinary)
- Itinerary Builder: add/edit/remove stops and activities, day-by-day view, up/down reordering, automatic per-day and trip budget recalculation
- City & Activity search with filter/group/sort
- Budget breakdown by category (Recharts)
- Public/shareable read-only trip link + "Copy Trip" into another account
- Calendar view synced to trips/activities
- Community feed
- Admin panel: user management, popular cities/activities, usage analytics
- Light/dark theme (persisted per user)
- Export itinerary as CSV, Excel, or PDF
- Breadcrumb navigation, toast notifications throughout

## Roadmap

- True drag-and-drop reordering (currently up/down controls)
- "Add to Trip" shortcut directly from Activity Search results
- Community post image uploads + comment threads
- Code-splitting the admin/analytics bundle
