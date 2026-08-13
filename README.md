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

## Database: SQLite by default, MySQL-ready

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
