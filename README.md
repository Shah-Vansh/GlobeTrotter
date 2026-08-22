# GlobeTrotter

Full-stack travel planning app - Flask + PostgreSQL backend and a React +
Redux Toolkit + Tailwind CSS v4 frontend. All 12 core screens from the spec
are implemented and wired end-to-end against the Flask API (verified by
running the backend + seed data and exercising every route, and by building
the frontend with Vite).

## Stack

- **Frontend:** React 18 (Vite), React Router, Redux Toolkit, Tailwind CSS v4,
  GSAP (entrance animations), react-hot-toast, Recharts (admin + budget
  charts), lucide-react icons, axios (JWT interceptor with auto-refresh).
- **Backend:** Flask, SQLAlchemy, Flask-JWT-Extended, PostgreSQL, Cloudinary
  (images), Brevo (transactional email).

## Getting started

### Backend

```bash
cd server
python -m venv venv
venv\Scripts\activate        # or `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env         # fill in DATABASE_URL, JWT secrets, Cloudinary, Brevo
python seed.py                 # creates tables + seeds demo cities/activities/users
python run.py
```

The API runs on the port configured in `run.py` (Flask default `5000`) with
every route mounted under `/api/*`. `GET /api/health` reports API + DB status.

Demo logins created by `seed.py`:
- Admin: `admin` / `Admin@123`
- Users: `alice` / `Password@123`, `bob` / `Password@123`

For a quick local smoke test without PostgreSQL, `DATABASE_URL` can be
temporarily set to `sqlite:///test.db` (SQLite) - useful for trying the app
before setting up a real Postgres instance.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env          # set VITE_BASE_URL to your backend URL
npm run dev
```

## What's implemented

- `src/configs/api.js` - axios instance with JWT attach + silent refresh.
- `src/store/` - `authSlice`, `themeSlice` (persisted light/dark mode, synced
  to `PUT /api/users/me/theme`), `uiSlice` (breadcrumbs, sidebar preference).
- `src/layout/` - `AuthLayout`, `MainLayout`, `Header`, `Sidebar`,
  `Breadcrumb`, `ProtectedRoute`, `AdminRoute`.
- `src/pages/auth/` - Login (screen 1) and Registration (screen 2), with
  client-side validation, password masking, and GSAP entrance animation.
- `src/pages/Dashboard.jsx` - Main Landing Page (screen 3): banner, search
  toolbar, Top Regional Selections, Previous Trips, floating "+ Plan a Trip".
- `src/pages/trips/` - Trip Listing (screen 6, grouped Ongoing/Upcoming/
  Completed), Create Trip form, and a full Trip Detail page (screens 5 + 9)
  combining the **Itinerary Builder** (add/edit/remove stops and activities,
  up/down reordering, automatic day + trip budget recalculation), a
  Recharts cost-breakdown chart, a Share/Unshare toggle with a copyable
  public link, and CSV/Excel/PDF export.
- `src/pages/public/PublicTripView.jsx` - **Shared/Public Itinerary View**
  (screen 11): unauthenticated read-only page at `/public/trips/:slug`, with
  a "Copy Trip" action that clones the trip (and every stop/activity) into
  the signed-in visitor's own account, or routes signed-out visitors to
  `/login` and back.
- `src/pages/search/` - City Search and Activity Search (screen 8) with
  search/group/filter/sort toolbar.
- `src/pages/community/Community.jsx` - feed, composer, like/comment counts
  (screen 10).
- `src/pages/calendar/CalendarView.jsx` - month grid synced to trips/
  activities.
- `src/pages/profile/Profile.jsx` - editable profile, photo upload, saved
  destinations.
- `src/pages/admin/AdminPanel.jsx` - Manage Users, Popular Cities, Popular
  Activities, and Trends & Analytics tabs with Recharts bar/pie charts
  (screen 12), gated by `is_admin` both client- and server-side.
- `src/components/Modal.jsx` - shared dialog used by the itinerary builder's
  Add/Edit Stop and Add/Edit Activity forms.

## Suggested next steps

- True drag-and-drop for stop/activity reordering (currently up/down
  buttons, which keep the backend's `order_index` as the single source of
  truth without a DnD library dependency).
- "Add to Trip" shortcut directly from the Activity Search results grid
  (currently activities are added from within a trip's itinerary builder,
  which lets you pick the destination day).
- Community post image upload + comment thread UI.
- Code-splitting the Recharts/admin bundle (flagged by the Vite build) via
  `React.lazy`.

## Notes

- Per your existing setup, `tailwind.config.js` and `src/index.css` are left
  untouched (Tailwind v4's `@tailwindcss/vite` plugin needs no config file).
- Every source file has a top-of-file comment describing its responsibility
  and which backend route(s) it talks to, per your request.

