# Generic Hotel Management Platform

A configurable Django + React hotel foundation. Hotel identity, contacts, services, rooms and rates are database-driven so another property can reuse this code without customer-facing source edits.

## Included

- Professional public site with 14 homepage sections, responsive navigation, rooms, services, events, contact and booking pages.
- Email-based users, operational roles, JWT authentication, backend permission enforcement and role-aware dashboards.
- Hotel settings, services, amenities, room types, date-specific availability and traceable booking requests.
- Reception workflow: booking confirmation, room allocation, guest registration, check-in, stay history, checkout and dirty-room handoff.
- Guest folios, accommodation/outlet/event charges, receipts, payments, invoices, installment schedules, quotations, controlled reversals, refunds and approved expenses.
- Configurable outlets and point of sale with cash, credit, electronic and room-charge settlement.
- Product master data, suppliers, purchase receipts, stock locations, immutable stock movements, physical counts, low-stock notifications and stock protection.
- Venues, event types, event requests, conflict-safe confirmation, event services and operational tasks.
- Housekeeping, maintenance, notifications, communications, marketing campaigns, cash control and management reports.
- Database-grounded assistant responses that respect the signed-in user’s scope and do not invent hotel records.
- PostgreSQL-ready Django, Redis caching, Celery/Beat, REST and GraphQL.
- PWA service worker, IndexedDB cache/operation queue and visible connection state.
- Docker Compose, Render Blueprint and Vercel configuration.

## Local Docker setup

Run `docker compose up --build`, then open `http://localhost:5173`. The API runs at `http://localhost:8000/api`. PostgreSQL is available to host tools on `postgresql://hotel:hotel@127.0.0.1:5433/hotel_platform`; the backend container uses `postgresql://hotel:hotel@db:5432/hotel_platform`.

Set `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD`, then run `python manage.py seed_hotel` in the backend container to create the first owner. The seed is idempotent.

SQLite is not used. For a production installation, set `DATABASE_URL` to the PostgreSQL connection string issued by Render or another PostgreSQL provider. That environment value replaces the local Docker default without a source-code change.

## Vercel frontend

Create a Vercel project with Root Directory `frontend`, then add:

- `VITE_API_BASE_URL=https://YOUR-RENDER-SERVICE.onrender.com/api`
- `VITE_GRAPHQL_URL=https://YOUR-RENDER-SERVICE.onrender.com/graphql/`

The included `frontend/vercel.json` preserves React routes after refresh.

## Render backend

Use `render.yaml`, or create a Docker web service with `backend/Dockerfile`. Configure `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `FRONTEND_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `CLOUDINARY_URL`, the property name/timezone, and the bootstrap owner credentials. The pre-deploy step applies migrations and runs the idempotent seed.

Edit the active hotel in Dashboard → Settings or Django Admin after first login. Public branding updates automatically from the database.

## Production verification

Before opening a new installation, verify the seeded owner can sign in; configure rooms, outlets and stock locations; submit and confirm a test booking; check in the guest; post and pay a folio; complete checkout; record and void a POS sale; receive stock and approve a count; and submit an event request. Financial and stock records are preserved through reversals, returns and audit entries rather than destructive deletion.

Browser-offline support caches hotel settings and provides an IndexedDB operation queue with visible sync/conflict state. PostgreSQL remains authoritative. High-risk financial and inventory decisions are validated again by the API when synchronization occurs.
