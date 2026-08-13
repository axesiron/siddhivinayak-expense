import os
from datetime import date, timedelta
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, Employee, Expense, ExpenseRate, CompanySettings

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    def sum_since(start=None, end=None):
        q = Expense.query
        if start:
            q = q.filter(Expense.expense_date >= start)
        if end:
            q = q.filter(Expense.expense_date <= end)
        return q.with_entities(func.coalesce(func.sum(Expense.total_amount), 0)).scalar()

    stats = {
        "total_employees": Employee.query.filter_by(role="employee").count(),
        "today": sum_since(today, today),
        "month": sum_since(month_start),
        "year": sum_since(year_start),
        "total": sum_since(),
    }

    recent_expenses = Expense.query.order_by(Expense.expense_date.desc()).limit(10).all()

    return render_template("admin/admin_dashboard.html", stats=stats, recent_expenses=recent_expenses)


@admin_bp.route("/employees")
@login_required
@admin_required
def employees():
    search = request.args.get("q", "").strip()
    query = Employee.query.filter_by(role="employee")
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Employee.name.ilike(like)) |
            (Employee.email.ilike(like)) |
            (Employee.designation.ilike(like))
        )
    all_employees = query.order_by(Employee.name.asc()).all()
    return render_template("admin/employees.html", employees=all_employees, search=search)


@admin_bp.route("/employees/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_employee():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if Employee.query.filter_by(email=email).first():
            flash("An employee with this email already exists.", "danger")
            return redirect(url_for("admin.add_employee"))

        last = Employee.query.order_by(Employee.id.desc()).first()
        next_id = (last.id + 1) if last else 1

        emp = Employee(
            employee_code=f"SVEC-{next_id:03d}",
            name=request.form.get("name", "").strip(),
            email=email,
            mobile=request.form.get("mobile", "").strip(),
            designation=request.form.get("designation", "").strip(),
            department=request.form.get("department", "").strip(),
            role=request.form.get("role", "employee"),
        )
        emp.set_password(request.form.get("password") or "changeme123")
        db.session.add(emp)
        db.session.commit()
        flash("Employee added successfully.", "success")
        return redirect(url_for("admin.employees"))

    return render_template("admin/employee_form.html", employee=None)


@admin_bp.route("/employees/edit/<int:emp_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    if request.method == "POST":
        emp.name = request.form.get("name", "").strip()
        emp.mobile = request.form.get("mobile", "").strip()
        emp.designation = request.form.get("designation", "").strip()
        emp.department = request.form.get("department", "").strip()
        emp.role = request.form.get("role", emp.role)
        new_password = request.form.get("password")
        if new_password:
            emp.set_password(new_password)
        db.session.commit()
        flash("Employee updated.", "success")
        return redirect(url_for("admin.employees"))

    return render_template("admin/employee_form.html", employee=emp)


@admin_bp.route("/employees/delete/<int:emp_id>", methods=["POST"])
@login_required
@admin_required
def delete_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash("Employee deleted.", "info")
    return redirect(url_for("admin.employees"))


@admin_bp.route("/employees/toggle-block/<int:emp_id>", methods=["POST"])
@login_required
@admin_required
def toggle_block(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    emp.is_blocked = not emp.is_blocked
    db.session.commit()
    flash(f"{emp.name} has been {'blocked' if emp.is_blocked else 'unblocked'}.", "info")
    return redirect(url_for("admin.employees"))


@admin_bp.route("/expenses")
@login_required
@admin_required
def all_expenses():
    query = Expense.query.join(Employee)

    emp_id = request.args.get("employee_id", type=int)
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    designation = request.args.get("designation", "").strip()

    if emp_id:
        query = query.filter(Expense.employee_id == emp_id)
    if from_date:
        query = query.filter(Expense.expense_date >= from_date)
    if to_date:
        query = query.filter(Expense.expense_date <= to_date)
    if designation:
        query = query.filter(Employee.designation == designation)

    items = query.order_by(Expense.expense_date.desc()).all()
    all_employees = Employee.query.filter_by(role="employee").order_by(Employee.name).all()
    designations = sorted({e.designation for e in all_employees if e.designation})

    grand_total = sum(e.total_amount or 0 for e in items)

    return render_template("admin/all_expenses.html", expenses=items, employees=all_employees,
                            designations=designations, grand_total=grand_total,
                            filters=request.args)


@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    return render_template("admin/reports.html")


@admin_bp.route("/reports/employee", methods=["GET"])
@login_required
@admin_required
def employee_report():
    all_employees = Employee.query.filter_by(role="employee").order_by(Employee.name).all()
    emp_id = request.args.get("employee_id", type=int)
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    employee = None
    items = []
    summary = None

    if emp_id:
        employee = Employee.query.get_or_404(emp_id)
        query = Expense.query.filter_by(employee_id=employee.id)
        if from_date:
            query = query.filter(Expense.expense_date >= from_date)
        if to_date:
            query = query.filter(Expense.expense_date <= to_date)
        items = query.order_by(Expense.expense_date.asc()).all()

        summary = {
            "count": len(items),
            "km": sum(e.km or 0 for e in items),
            "food": sum(e.food_amount or 0 for e in items),
            "transport": sum((e.courier_transport_amount or 0) + (e.cng_bus_amount or 0) for e in items),
            "grand_total": sum(e.total_amount or 0 for e in items),
        }

    return render_template("admin/employee_report.html", employees=all_employees,
                            employee=employee, items=items, summary=summary,
                            from_date=from_date, to_date=to_date)


ALLOWED_LOGO_EXT = {"png", "jpg", "jpeg"}


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def settings():
    settings_row = CompanySettings.query.first()
    if not settings_row:
        settings_row = CompanySettings()
        db.session.add(settings_row)
        db.session.commit()

    if request.method == "POST":
        settings_row.company_name = request.form.get("company_name", "").strip()
        settings_row.address_line1 = request.form.get("address_line1", "").strip()
        settings_row.address_line2 = request.form.get("address_line2", "").strip()
        settings_row.mobile = request.form.get("mobile", "").strip()

        logo_file = request.files.get("logo")
        if logo_file and logo_file.filename:
            ext = logo_file.filename.rsplit(".", 1)[-1].lower()
            if ext in ALLOWED_LOGO_EXT:
                filename = f"company_logo.{ext}"
                save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                logo_file.save(save_path)
                settings_row.logo_path = save_path
            else:
                flash("Logo must be a PNG or JPG file.", "danger")
                return redirect(url_for("admin.settings"))

        db.session.commit()
        flash("Company settings updated.", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", settings=settings_row)


@admin_bp.route("/settings/remove-logo", methods=["POST"])
@login_required
@admin_required
def remove_logo():
    settings_row = CompanySettings.query.first()
    if settings_row and settings_row.logo_path:
        try:
            if os.path.exists(settings_row.logo_path):
                os.remove(settings_row.logo_path)
        except OSError:
            pass
        settings_row.logo_path = None
        db.session.commit()
        flash("Logo removed.", "info")
    return redirect(url_for("admin.settings"))


@admin_bp.route("/rates", methods=["GET", "POST"])
@login_required
@admin_required
def rates():
    rates_row = ExpenseRate.query.first()
    if not rates_row:
        rates_row = ExpenseRate()
        db.session.add(rates_row)
        db.session.commit()

    if request.method == "POST":
        rates_row.bike_rate = float(request.form.get("bike_rate") or 0)
        rates_row.car_rate = float(request.form.get("car_rate") or 0)
        rates_row.other_rate = float(request.form.get("other_rate") or 0)
        rates_row.rounding = request.form.get("rounding", "nearest")
        db.session.commit()
        flash("KM rates updated.", "success")
        return redirect(url_for("admin.rates"))

    return render_template("admin/rates.html", rates=rates_row)
