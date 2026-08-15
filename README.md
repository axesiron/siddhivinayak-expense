# SIDDHIVINAYAK EXPENSE MANAGER

A real, working expense-management web app for **Siddhivinayak Engineering &
Trading Corporation** — employees log daily travel/expenses through a
modern UI, everything is stored in a database, and a professional,
print-ready Excel expense sheet is generated on demand (matching the
company's original expense-sheet format: SR.NO / DATE / REASON / MODE /
FROM / TO / OTHER / CNG-BUS / KM / COURIER-TRANSPORT / FOOD / TOTAL).

## Quick start

```bash
cd siddhivinayak_expense_manager
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000**. The database and two demo accounts are
created automatically on first run:

| Role     | Email                         | Password      |
|----------|--------------------------------|---------------|
| Admin    | admin@siddhivinayak.com        | Admin@123     |
| Employee | rajkumar@siddhivinayak.com     | Employee@123  |

Change both passwords before any real use.

## Deploying live (Render — free tier)

The repo is already set up for this: `Procfile`, `gunicorn` in
`requirements.txt`, `render.yaml`, and `config.py` handles Render's
Postgres connection string automatically.

**Note on SQLite:** Render's free web service disk is wiped on every
deploy/restart, so SQLite (the local default) won't persist. Use Render's
free PostgreSQL database instead — the steps below set that up for you.

### 1. Push this code to GitHub
```bash
cd siddhivinayak_expense_manager
git init
git add .
git commit -m "Initial commit"
```
Create a new empty repo on GitHub (github.com/new), then:
```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render
**Option A — one-click Blueprint (recommended):**
1. Go to [dashboard.render.com/blueprints](https://dashboard.render.com/blueprints) → **New Blueprint Instance**.
2. Connect the GitHub repo you just pushed. Render reads `render.yaml`
   and automatically provisions both the web service *and* a free
   PostgreSQL database, wired together via `DATABASE_URL`.
3. Click **Apply** — first deploy takes a few minutes.

**Option B — manual setup:**
1. **New +** → **PostgreSQL** → name it, free plan → **Create Database**.
   Copy the "Internal Database URL" once it's ready.
2. **New +** → **Web Service** → connect your repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - Add environment variables: `DATABASE_URL` (paste the URL from step 1)
     and `SECRET_KEY` (any long random string).
3. **Create Web Service** — Render builds and deploys automatically.

### 3. First login
Render runs `db.create_all()` and seeds the demo admin/employee accounts
automatically on first boot, same as local — visit your new
`https://<your-app>.onrender.com` and log in with the demo credentials
from the Quick Start section above, **then change both passwords**
immediately since the app is now public.

### Notes
- Free-tier Render web services spin down after inactivity and take ~30s
  to wake back up on the next request — normal for the free plan, not a bug.
- The demo seed data (admin + one employee account) is created automatically
  the first time the app starts against a fresh, empty database.
- For a custom domain, Render's dashboard has a straightforward "Custom
  Domains" tab under the web service settings.

## Installing as a mobile app (PWA → optional real .apk)

This app ships as a **Progressive Web App**: a manifest
(`static/manifest.json`), app icons, and a service worker (`/sw.js`,
scoped to the whole app) are already wired in. Once it's deployed live
with HTTPS (Render gives you this automatically, see above):

**Just install it (no APK needed):**
1. Open the live URL in Chrome on Android.
2. Chrome shows an **"Install app"** prompt (or: menu ⋮ → **Add to Home
   screen**).
3. It installs with a real icon, opens full-screen with no browser bar,
   and behaves like a native app — fastest path, nothing else required.

**If you specifically need a downloadable `.apk` file** (e.g. to
side-load or publish to the Play Store), use
[PWABuilder](https://www.pwabuilder.com) — a free Microsoft-run tool that
packages any PWA into a signed Android package, no dev machine or Android
Studio required:
1. Deploy the app live (Render, above).
2. Go to pwabuilder.com, paste your `https://<your-app>.onrender.com` URL.
3. It reads `manifest.json` automatically (already configured here) →
   choose **Android** → **Download Package** → you get a real `.apk`/`.aab`.

## Database: SQLite locally, Postgres/MySQL in production

The app runs on **SQLite out of the box** (a single `siddhivinayak.db`
file, zero setup) so it works immediately. The brief specifies MySQL —
switching is a one-line change, no code changes needed, because the app
uses SQLAlchemy:

```bash
pip install pymysql   # already in requirements.txt
mysql -u root -p -e "CREATE DATABASE siddhivinayak_expense_manager"
export DATABASE_URL="mysql+pymysql://user:password@localhost/siddhivinayak_expense_manager"
python app.py
```

`database/schema.sql` and `database/sample_data.sql` are provided for
reference/manual provisioning, but `app.py` also auto-creates every table
via `db.create_all()` on first run against whichever database you point it at.

## What's implemented

- **Auth**: registration, login, logout, forgot-password UI, password
  hashing (Werkzeug), session auth (Flask-Login), CSRF protection on every
  form (Flask-WTF), role-based access (employee vs admin), employee data
  isolation (an employee only ever sees their own records).
- **Employee dashboard**: today / week / month / year / total cards,
  recent expenses, current expense period.
- **Add/Edit expense**: exact fields from the brief (Date, Reason, Mode,
  From, To, Other, CNG/Bus, KM, Courier/Transport, Food, Total, Notes).
  Total is always server-calculated — the UI shows a **live preview** as
  you type (via `/api/calculate-total`), but the authoritative total is
  computed and stored server-side on save, so it can never be tampered
  with from the browser.
- **KM-rate engine**: Bike/Car use a configurable ₹/km rate (Admin →
  KM Rates) with a configurable rounding rule (nearest / up / down / none
  — "13 km × ₹4.50 = ₹58.50 → ₹59" is the exact worked example from the
  brief). Bus/Train/Auto/Cab/Other are **not** auto-costed by KM — those
  use the CNG/Bus field, per the brief.
- **Expense table**: search + date range + mode filters, latest-first,
  view/edit/delete actions, confirmation before delete.
- **Excel export (the core feature)**: `openpyxl`-generated workbook with
  company name/address/mobile header, employee name/designation/period,
  bordered + styled data table, currency + date formatting, totals block
  (Other/CNG-Bus/KM/Courier-Transport/Food + Grand Total), frozen header
  row, autofilter, landscape orientation, fit-to-width, print area,
  header/footer. Four export endpoints: all records, custom date range,
  monthly, and (admin) per-employee — plus an admin "all employees" export
  that produces one sheet per employee in a single workbook.
- **Admin panel**: dashboard cards (employees / today / month / year /
  total), employee CRUD, block/unblock, search, all-expenses view with
  employee/designation/date filters, company settings, KM-rate settings.
- **Reports & analytics**: daily report with a trend chart, monthly report
  with category totals, and a full analytics page covering all the chart
  types from the brief: monthly trend, category breakdown, plus 30-day
  Food, Transport/Courier, CNG/Bus, and KM-travel charts (Chart.js).
- **Employee-wise admin report** — a dedicated page (Admin → Reports →
  Employee-wise Report) to pick an employee + date range and view/export
  their sheet.
- **Company logo** — upload a PNG/JPG in Admin → Settings; it's embedded
  in the top-left corner of every generated Excel export via `openpyxl`.
- **Responsive UI**: sidebar + topbar corporate layout on desktop, bottom
  navigation + floating add-button on mobile, premium theme (no default
  Bootstrap look) in `static/css/style.css`.

## Scope notes (be aware of these before treating it as finished)

This is a genuinely working app, not a static prototype — every button
above is wired to a real route and a real database write. A brief this
large (30 sections) also asks for things a first pass reasonably leaves
as follow-ups rather than guessing at:

- **Password reset email delivery** isn't wired up (no SMTP configured) —
  the form exists and flashes a message but doesn't send mail. Wiring an
  SMTP provider (or a service like SendGrid) into `routes/auth.py` is the
  remaining step.
- Flask's built-in dev server is fine for trying this out; put it behind
  gunicorn/nginx (or similar) for real deployment, and set a strong
  `SECRET_KEY` via environment variable rather than the default.

## Project structure

```
siddhivinayak_expense_manager/
├── app.py                  # app factory, blueprint registration, seed data
├── config.py                # config incl. company info & default KM rates
├── models.py                 # Employee, Expense, ExpenseRate, CompanySettings
├── requirements.txt
├── database/
│   ├── schema.sql            # MySQL reference schema
│   └── sample_data.sql
├── routes/
│   ├── auth.py                # /login /register /logout /forgot-password
│   ├── employee.py            # dashboard, expense CRUD, reports, analytics
│   ├── admin.py                # admin dashboard, employees, settings, rates
│   └── excel.py                 # all /export/excel/* endpoints
├── utils/
│   ├── calculations.py        # KM-rate + total calculation logic
│   └── excel_generator.py     # the openpyxl report builder
├── templates/                # Jinja2 templates (base + employee + admin/)
└── static/
    ├── css/style.css
    └── js/{app.js, expense.js}
```

## Sample data matching the brief's worked example

Log in as the demo employee and add these rows (or import
`database/sample_data.sql`) to reproduce the exact example from the spec:

| Date       | Reason              | Mode | From   | To      | KM | Courier/Transport | Food | Total |
|------------|---------------------|------|--------|---------|----|--------------------|------|-------|
| 18-07-2026 | Shiroli Parcel      | Bike | Office | Shiroli | 13 | —                  | —    | ₹59   |
| 20-07-2026 | Shiroli Parcel      | Bike | Office | Shiroli | 13 | —                  | —    | ₹59   |
| 21-07-2026 | Shiroli Parcel      | Bike | Office | Shiroli | 13 | —                  | —    | ₹59   |
| 23-07-2026 | Travel to Mysore    | Bus  | Office | Mysore  | —  | ₹1,500             | —    | ₹1,500|

Then click **Download Excel** — the generated sheet matches this table
row-for-row, with the company header and totals block on top/bottom.
